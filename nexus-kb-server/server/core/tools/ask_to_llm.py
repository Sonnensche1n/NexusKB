import json
import asyncio
from logger import logger
from config.llm import TOP_K, RERANKER_ENABLED, RERANKER_RECALL_MULTIPLIER
from config.prompt import REPOSCHAT_PROMPT_TEMPLATE, REPOSHISTORY_PROMPT_TEMPLATE
from server.core.tools.repos_vector_db import get_or_build_vector_db
from server.core.tools.reranker import rerank
from server.utils.websocketutils import WebsocketManager
from server.model.entity_knb import ChatMesg as ChatMesgEntity, ChatMesgQuote as ChatMesgQuoteEntity, ReposSetting as ReposSettingEntity
from server.model.orm_knb import ChatMesg
from server.db.DbManager import session_scope
from datetime import datetime
from server.core.tools.llm_client_tools import get_user_llm_client
from server.core.tools.message_tools import message_chunk_to_json, message_quote_to_json, message_error_to_json
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

def get_related_docs_by_repos_id(reposId:str, question:str, setting: ReposSettingEntity = ReposSettingEntity()):
  vector_store = get_or_build_vector_db(reposId)
  if (vector_store is None):
    return None
  
  # 如果启用了 Reranker，扩大召回量以提供更大的候选池
  recall_k = setting.topK * RERANKER_RECALL_MULTIPLIER if RERANKER_ENABLED else setting.topK
  
  # 优先尝试获取带有分数的普通检索结果
  related_docs_with_score_ = get_related_docs_with_score(vector_store=vector_store, question=question, k=recall_k)
  
  # 增加 MMR 检索补充（如果配置支持或者为了混合结果）
  try:
    mmr_docs = vector_store.max_marginal_relevance_search(question, k=recall_k, fetch_k=recall_k * 3)
    # 将 MMR 结果合并，如果没有 score 则默认给一个合理的通过阈值的分数（或者通过原本的检索匹配分数）
    existing_docs_contents = [doc.page_content for doc, _ in related_docs_with_score_]
    for doc in mmr_docs:
      if doc.page_content not in existing_docs_contents:
        # MMR 补充的文档，为了能够通过阈值过滤，赋予一个略低于阈值的基础分 (这里越小越相似，因此给个相对安全的距离)
        related_docs_with_score_.append((doc, setting.smlrTrval - 0.01 if setting.smlrTrval else 0.5))
  except Exception as e:
    logger.error(f"MMR 检索失败: {e}")

  return related_docs_with_score_

def get_related_docs_with_score(vector_store, question:str, k:int = TOP_K):
  return vector_store.similarity_search_with_score(question, k)

def generate_llm_prompts(question: str, related_docs_with_score) -> str:
  context = '\n'.join([doc.page_content for doc, score in related_docs_with_score])
  return REPOSCHAT_PROMPT_TEMPLATE.replace('{question}', question).replace('{context}', context)

def get_question_prompts_and_sources(reposId: str, question: str, setting: ReposSettingEntity):
  if (question is None or question == ''):
    return None, None
  related_docs_with_score_ = get_related_docs_by_repos_id(reposId, question, setting)
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
    chatHistory = chatHistory[:setting.maxHist]
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
    prompts, sources = get_question_prompts_and_sources(chatMesg.reposId, question, setting)
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