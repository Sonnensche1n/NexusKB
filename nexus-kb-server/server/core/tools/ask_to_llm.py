import json
from logger import logger
from config.llm import TOP_K
from config.prompt import REPOSCHAT_PROMPT_TEMPLATE, REPOSHISTORY_PROMPT_TEMPLATE
from server.core.tools.repos_vector_db import get_or_build_vector_db
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
  return get_related_docs_with_score(vector_store=vector_store, question=question, k=setting.topK)

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
  related_docs_with_score = [[doc, score] for doc, score in related_docs_with_score_ if score < setting.smlrTrval ] # 越小越相似
  # 将related_docs_with_score截取setting.maxCtx条
  related_docs_with_score = related_docs_with_score[:setting.maxCtx]
  sources = prob_related_documents_and_score(related_docs_with_score)
  prompts = generate_llm_prompts(question, related_docs_with_score)
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