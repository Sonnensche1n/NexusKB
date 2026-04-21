import json
import asyncio
from logger import logger
from config.llm import TOP_K, RERANKER_ENABLED, RERANKER_RECALL_MULTIPLIER, HYDE_ENABLED, HYBRID_SEARCH_ENABLED, FC_MAX_ROUNDS, AGENT_MODE
from config.prompt import REPOSCHAT_PROMPT_TEMPLATE, REPOSHISTORY_PROMPT_TEMPLATE
from server.core.tools.repos_vector_db import get_or_build_vector_db
from server.core.tools.reranker import rerank
from server.core.tools.hyde import generate_hypothetical_document
from server.core.tools.bm25_retriever import BM25Retriever
from server.core.tools.hybrid_search import rrf_fusion
from server.core.tools.post_processor import post_process_results
from server.core.tools.tool_registry import tool_registry
from server.utils.websocketutils import WebsocketManager
from server.model.entity_knb import ChatMesg as ChatMesgEntity, ChatMesgQuote as ChatMesgQuoteEntity, ReposSetting as ReposSettingEntity
from server.model.orm_knb import ChatMesg
from server.db.DbManager import session_scope
from datetime import datetime
from server.core.tools.llm_client_tools import get_user_llm_client
from server.core.tools.message_tools import message_chunk_to_json, message_quote_to_json, message_error_to_json, message_tool_call_to_json
def prob_related_documents_and_score(related_docs_with_score):
  sources = []
  for doc, score in related_docs_with_score:
    metadata = doc.metadata
    sources.append({
      'dtsetId': metadata['dtsetId'],
      'dtsetNm': metadata['dtsetNm'],
      'fileNm': metadata['fileNm'],
      'fileTyp': metadata['fileTyp'],
      'score': score,
      'content': doc.page_content
    })
    # print('%s [%s]: %s' % (doc.metadata['source'], score, doc.page_content))
  return sources

def compress_chat_history(
  history: list,
  max_pairs: int = 6,
  max_total_chars: int = 4000,
) -> list:
  """滑动窗口 + 字符数限制压缩聊天历史。"""
  if not history:
    return []

  recent = history[-(max_pairs * 2):]
  total_chars = 0
  result = []
  for msg in reversed(recent):
    content_len = len(getattr(msg, "mesgCntnt", "") or "")
    if total_chars + content_len > max_total_chars:
      break
    result.insert(0, msg)
    total_chars += content_len
  return result

def get_related_docs_by_repos_id(reposId:str, question:str, setting: ReposSettingEntity = ReposSettingEntity()):
  vector_store = get_or_build_vector_db(reposId)
  if (vector_store is None):
    return None
  
  # 如果启用了 Reranker，扩大召回量以提供更大的候选池
  recall_k = setting.topK * RERANKER_RECALL_MULTIPLIER if RERANKER_ENABLED else setting.topK
  
  # 优先尝试获取带有分数的普通检索结果
  related_docs_with_score_ = get_related_docs_with_score(vector_store=vector_store, question=question, k=recall_k)
  
  # 格式化向量检索结果
  vector_results = []
  for doc, score in related_docs_with_score_:
      vector_results.append({
          "content": doc.page_content,
          "metadata": doc.metadata,
          "score": score,
          "retrieval_type": "vector",
      })

  # 【新增】BM25 检索与 RRF 融合
  if HYBRID_SEARCH_ENABLED:
      try:
          # 注意：由于缺少独立缓存，这里每次动态获取全量文本进行 BM25 索引构建（存在性能瓶颈，应作为二期优化）
          all_docs_dict = vector_store.get()
          bm25_retriever = BM25Retriever()
          bm25_docs = []
          
          # ChromaDB get() 返回字典结构：{'documents': [...], 'metadatas': [...]}
          if all_docs_dict and "documents" in all_docs_dict and all_docs_dict["documents"]:
              for idx, content in enumerate(all_docs_dict["documents"]):
                  metadata = all_docs_dict["metadatas"][idx] if "metadatas" in all_docs_dict and all_docs_dict["metadatas"] else {}
                  bm25_docs.append({"content": content, "metadata": metadata})

          if bm25_docs:
              bm25_retriever.build_index(bm25_docs)
              bm25_results = bm25_retriever.search(question, top_k=recall_k)
          else:
              bm25_results = []

          # RRF 融合
          fused_results = rrf_fusion(
              result_lists=[vector_results, bm25_results],
              top_k=recall_k,
          )
          
          # 兼容原有的返回结构
          class DummyDoc:
              def __init__(self, content, metadata):
                  self.page_content = content
                  self.metadata = metadata
          
          related_docs_with_score_ = []
          for item in fused_results:
              # 对于 RRF，分数越高越好，但原有代码中 score 是距离（越小越好）。
              # 因此如果使用了混合检索，我们需要暂时跳过原有逻辑中根据 smlrTrval 的粗暴过滤
              related_docs_with_score_.append((DummyDoc(item["content"], item["metadata"]), -item["rrf_score"]))
              
      except Exception as e:
          logger.error(f"[HybridSearch] 混合检索失败，降级为向量检索: {e}")
  else:
      # 如果未启用，则保持之前的向量搜索逻辑（不修改 related_docs_with_score_）
      pass

  return related_docs_with_score_

def get_related_docs_with_score(vector_store, question:str, k:int = TOP_K):
  return vector_store.similarity_search_with_score(question, k)

def generate_llm_prompts(question: str, related_docs_with_score) -> str:
  context = '\n'.join([doc.page_content for doc, score in related_docs_with_score])
  return REPOSCHAT_PROMPT_TEMPLATE.replace('{question}', question).replace('{context}', context)

def get_question_prompts_and_sources(reposId: str, question: str, setting: ReposSettingEntity, llm_client=None):
  if (question is None or question == ''):
    return None, None
    
  # ==========================================
  # 1. HyDE 查询扩展
  # ==========================================
  search_query = question
  if HYDE_ENABLED and llm_client:
      try:
          import concurrent.futures
          def run_async_hyde(q, client):
              return asyncio.run(generate_hypothetical_document(q, client, enabled=True))
              
          with concurrent.futures.ThreadPoolExecutor() as pool:
              search_query = pool.submit(run_async_hyde, question, llm_client).result()
      except Exception as e:
          logger.error(f"[HyDE] 扩展查询失败: {e}")
          search_query = question
          
  # 使用扩展后的 query 进行检索
  related_docs_with_score_ = get_related_docs_by_repos_id(reposId, search_query, setting)
  if (related_docs_with_score_ is None):
    return None, None
    
  # 第一阶段过滤：保留符合相似度阈值的文档
  filtered_results = []
  for doc, score in related_docs_with_score_:
    if score < setting.smlrTrval: # 越小越相似
      filtered_results.append({
          "content": doc.page_content,
          "metadata": doc.metadata,
          "score": score,
      })

  # 第二阶段精排：如果启用了 Reranker，则进行重排序
  if RERANKER_ENABLED and filtered_results:
    # 由于当前外层可能非 async 函数（比如被 stream 包含调用），通过 asyncio.run 运行
    # 注意：如果这已经是在 asyncio event loop 中运行的，需要适当处理，
    # 比如在 FastAPI 中应直接使用 async/await
    try:
      loop = asyncio.get_event_loop()
      if loop.is_running():
        # 如果事件循环已运行（如 FastAPI），需要将 rerank 包装为同步任务，或者把 ask_to_llm_stream 整个改为异步
        # 为了兼容当前的同步 generator (ask_to_llm_stream)，我们可以使用一个新线程，或者使用 await
        # 此处假设我们不破坏原有的 generator 机制，先采取粗暴的 run_until_complete (但可能会报错 RuntimeError: This event loop is already running)
        # 更安全的做法是把这一层交给外部处理，或者使用同步的 httpx 客户端进行 rerank。
        # 考虑到项目框架，我们先尝试在协程外执行：
        pass
    except RuntimeError:
      pass

    try:
      # 为了避免修改顶层路由为 async 生成器导致的大量重构，这里我们创建一个新的事件循环来运行（在子线程中）
      import concurrent.futures
      def run_async_rerank(q, docs, n):
          return asyncio.run(rerank(q, docs, n))
          
      with concurrent.futures.ThreadPoolExecutor() as pool:
          filtered_results = pool.submit(run_async_rerank, question, filtered_results, setting.maxCtx).result()
    except Exception as e:
      logger.error(f"Reranker 异步调用失败，降级: {e}")

  # 取 Top-N (无论是否 Reranker 都有此步骤)
  filtered_results = filtered_results[:setting.maxCtx]
  
  # 新增：后处理（去重 + 按文档位置重排）
  filtered_results = post_process_results(
      chunks=filtered_results,
      deduplicate=True,
      reorder=True,
      similarity_threshold=0.85,
  )
  
  # 将字典格式还原为旧版格式，以兼容现有的 prob_related_documents_and_score
  # 为了适配原有的代码逻辑
  class DummyDoc:
      def __init__(self, content, metadata):
          self.page_content = content
          self.metadata = metadata
          
  final_docs_with_score = [[DummyDoc(item["content"], item["metadata"]), item["score"]] for item in filtered_results]

  sources = prob_related_documents_and_score(final_docs_with_score)
  prompts = generate_llm_prompts(question, final_docs_with_score)
  return prompts, sources

# 发送引用数据
async def send_ws_quote_message(chatMesg:ChatMesgEntity, sources:list, manager: WebsocketManager, token: str = None):
  mesgId = chatMesg.mesgId
  reposId = chatMesg.reposId
  chatId = chatMesg.chatId
  quotes = []
  for source in sources:
    quote = ChatMesgQuoteEntity(mesgId=mesgId).copy_from_dict(source, convert=lambda key,value: value if key != 'score' else float(value))
    quotes.append(vars(quote))
  message = {
    'type': 'chat_message_quote', 'data': {
      'mesgId': mesgId, 'chatId': chatId, 'reposId': reposId, 'quotes': quotes
    }
  }
  message = json.dumps(message, ensure_ascii=False)
  if (token is None):
    await manager.broadcast(message=message)
  else:
    await manager.send_message_to_client_id(message=message, client_id=token)
  return message
# 发送分段消息
async def send_ws_chunk_message(chatMesg: ChatMesgEntity, chunk: str, manager: WebsocketManager, token: str = None):
  chatMesg.mesgCntnt = chunk
  message = {
    'type': 'chat_message_chunk', 'data': vars(chatMesg)
  }
  message = json.dumps(message, ensure_ascii=False)
  if (token is None):
    await manager.broadcast(message=message)
  else:
    await manager.send_message_to_client_id(message=message, client_id=token)
  return message

def ask_to_llm_stream(setting: ReposSettingEntity, chatMesg: ChatMesgEntity, question: str, userId: str, chatHistory: list[ChatMesgEntity] = []):
  client = None
  try:
    client = get_user_llm_client(userId=userId, temperature=setting.llmTptur)
  except Exception as e:
    logger.error(e)
    yield message_error_to_json(str(e))
    message = '很抱歉，似乎发生了错误'
    yield message_chunk_to_json(message)
    return message
  if (len(chatHistory) > 0):
    chatHistory = compress_chat_history(chatHistory, max_pairs=setting.maxHist)
    history = []
    for hist in chatHistory:
      # if (hist.crtRole == 'sys'):
      #   continue
      role = 'Q' if hist.crtRole == 'usr' else 'A' # usr 用户, sys 系统
      history.append(f'{role}: {hist.mesgCntnt}')
    if (len(history) == 0):
      history = ''
    else:
      history = '\n'.join(history) # 历史记录拼接
    prompts = REPOSHISTORY_PROMPT_TEMPLATE.replace('{question}', question).replace('{history}', history)
    question = ''
    try:
      question = client.invoke(prompts) # 返回的数据可能需要处理一下
      if (type(question) != str): # langchain_core.messages.ai.AIMessage
        question = question.content
    except Exception as e:
      logger.error(e)
      yield message_error_to_json(str(e))
      message = '很抱歉，似乎发生了错误'
      yield message_chunk_to_json(message)
      return message
  prompts, sources = None, None
  try:
    prompts, sources = get_question_prompts_and_sources(chatMesg.reposId, question, setting, llm_client=client)
  except Exception as e:
    logger.error(e)
    yield message_error_to_json(str(e))
    message = '很抱歉，似乎发生了错误'
    yield message_chunk_to_json(message)
    return message
  message = ''
  if (prompts is None):
    message = '很抱歉，无法回答该问题'
    yield message_chunk_to_json(message)
  else:
    try:
      for chunk in client.stream(prompts):
        if (type(chunk) != str):
          chunk = chunk.content
        yield message_chunk_to_json(chunk)
        message = message + chunk
    except Exception as e:
      logger.error(e)
      yield message_error_to_json(str(e))
  yield message_quote_to_json(mesgId=chatMesg.mesgId, chatId=chatMesg.chatId, reposId=chatMesg.reposId, quotes=sources)
  mesgId = chatMesg.mesgId
  with session_scope() as session:
    orm = session.get(ChatMesg, mesgId)
    if (orm is None):
      orm = ChatMesg().copy_from_dict(vars(chatMesg))
      orm.crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    orm.mesgCntnt = message
    session.merge(orm)
  return message


def build_system_message(repos_id: str) -> str:
  """构建 FC 模式下的 system prompt。"""
  return (
    "你是 NexusKB 知识库助手。你可以使用工具辅助回答用户问题。\n"
    "优先使用 search_knowledge_base 检索知识库内容；如果信息不足，可继续使用摘要、问答对或三元组工具补充。\n"
    "如果所有工具都无法找到相关信息，请明确告知用户。\n"
    f"当前知识库ID: {repos_id}\n"
    "请始终使用中文回答。"
  )


def build_messages_from_history(
  question: str,
  repos_id: str,
  chat_history: list = None,
  max_history: int = 6,
) -> list:
  """将聊天历史构造成 OpenAI messages。"""
  messages = [{"role": "system", "content": build_system_message(repos_id)}]
  if chat_history:
    for hist in chat_history[-max_history * 2:]:
      role = "user" if hist.crtRole == "usr" else "assistant"
      if hist.mesgCntnt:
        messages.append({"role": role, "content": hist.mesgCntnt})
  messages.append({"role": "user", "content": question})
  return messages


def ask_to_llm_stream_with_fc(
  setting: ReposSettingEntity,
  chatMesg: ChatMesgEntity,
  question: str,
  userId: str,
  chatHistory: list[ChatMesgEntity] = None,
):
  """Function Calling 模式问答流程。"""
  try:
    client = get_user_llm_client(userId=userId, temperature=setting.llmTptur)
  except Exception as e:
    logger.error(e)
    yield message_error_to_json(str(e))
    yield message_chunk_to_json("很抱歉，模型连接失败")
    return

  messages = build_messages_from_history(
    question=question,
    repos_id=chatMesg.reposId,
    chat_history=compress_chat_history(chatHistory or [], max_pairs=setting.maxHist if hasattr(setting, "maxHist") else 6),
    max_history=setting.maxHist if hasattr(setting, "maxHist") else 6,
  )
  tools = tool_registry.get_schemas()
  all_sources = []

  if AGENT_MODE:
    from server.core.tools.agent_executor import AgentExecutor
    agent = AgentExecutor(client, chatMesg.reposId, setting)
    plan = agent.plan(question)
    if plan.get("mode") == "complex":
      logger.info(f"[Agent] 进入多步骤模式: {plan.get('reason')}")
      message = ""
      for chunk in agent.execute_steps(question, plan, chatMesg):
        yield chunk
        try:
          chunk_data = json.loads(chunk)
          if chunk_data.get("type") == "chat_message_chunk":
            message += str(chunk_data.get("data", ""))
        except Exception:
          pass

      mesgId = chatMesg.mesgId
      with session_scope() as session:
        orm = session.get(ChatMesg, mesgId)
        if (orm is None):
          orm = ChatMesg().copy_from_dict(vars(chatMesg))
          orm.crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        orm.mesgCntnt = message
        session.merge(orm)
      return
    logger.info(f"[Agent] 简单模式，走 FC 流程: {plan.get('reason')}")

  for round_num in range(FC_MAX_ROUNDS):
    try:
      response = client.chat_with_tools(
        messages=messages,
        tools=tools,
        tool_choice="auto" if round_num < FC_MAX_ROUNDS - 1 else "none",
      )
    except Exception as e:
      logger.error(f"[FC] 第{round_num + 1}轮调用失败，降级到无工具模式: {e}")
      try:
        response = client.chat_with_tools(messages=messages, tools=None)
      except Exception as inner_e:
        logger.error(inner_e)
        yield message_error_to_json(str(inner_e))
        yield message_chunk_to_json("很抱歉，似乎发生了错误")
        return

    choice = response.choices[0]
    tool_calls = getattr(choice.message, "tool_calls", None) or []
    if choice.finish_reason == "tool_calls" or tool_calls:
      messages.append({
        "role": "assistant",
        "content": choice.message.content or "",
        "tool_calls": [
          {
            "id": tool_call.id,
            "type": "function",
            "function": {
              "name": tool_call.function.name,
              "arguments": tool_call.function.arguments,
            },
          }
          for tool_call in tool_calls
        ],
      })

      for tool_call in tool_calls:
        tool_name = tool_call.function.name
        try:
          tool_args = json.loads(tool_call.function.arguments or "{}")
        except Exception:
          tool_args = {}

        if "repos_id" not in tool_args:
          tool_args["repos_id"] = chatMesg.reposId

        logger.info(f"[FC] 第{round_num + 1}轮调用工具: {tool_name}({tool_args})")
        yield message_tool_call_to_json(tool_name, "running")
        result = tool_registry.execute(tool_name, tool_args)
        yield message_tool_call_to_json(tool_name, "done")

        try:
          result_data = json.loads(result)
          for item in result_data.get("results", []):
            all_sources.append({
              "dtsetId": item.get("dtsetId", ""),
              "dtsetNm": item.get("dtsetNm", ""),
              "fileNm": item.get("fileNm", item.get("source", "")),
              "fileTyp": item.get("fileTyp", ""),
              "score": item.get("score", 0),
              "content": item.get("content", ""),
            })
        except Exception:
          pass

        messages.append({
          "role": "tool",
          "tool_call_id": tool_call.id,
          "content": result,
        })
      continue

    break

  message = ""
  try:
    stream = client.chat_stream(messages=messages)
    for chunk in stream:
      if chunk.choices and chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        yield message_chunk_to_json(content)
        message += content
  except Exception as e:
    logger.error(f"[FC] 流式输出失败: {e}")
    yield message_error_to_json(str(e))

  yield message_quote_to_json(
    mesgId=chatMesg.mesgId,
    chatId=chatMesg.chatId,
    reposId=chatMesg.reposId,
    quotes=all_sources[:10],
  )

  mesgId = chatMesg.mesgId
  with session_scope() as session:
    orm = session.get(ChatMesg, mesgId)
    if (orm is None):
      orm = ChatMesg().copy_from_dict(vars(chatMesg))
      orm.crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    orm.mesgCntnt = message
    session.merge(orm)
