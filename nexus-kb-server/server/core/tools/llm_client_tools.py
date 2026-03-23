from logger import logger
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings, OllamaEmbeddings, OpenAIEmbeddings
from cachetools import cached, TTLCache
from sqlalchemy import select
from server.db.DbManager import session_scope
from server.model.orm_sys import ModelParam, ModelPrvdInfo, ModelPrvdModl, SettingParam, SettingEmrt
from server.model.orm_knb import ReposInfo
from config.common import DEFAULT_SYSTEM_USER_ID, SYSTEM_MODEL_PREFERENCE_PARAM_CODE
from config.llm import DEFAULT_LLM_ARGUMENTS, DEFAULT_EMBEDDING_ARGUMENTS, LLM_BASE_URLS, MODEL_DIR
from server.utils.secretutils import aes_decrypt

DEFAULT_EMBEDDING_FUNCTION = None
DEFAULT_EMBEDDING_DEVICE = 'cpu'

DEFAULT_EMBEDDING_FUNCTION_MAP = {} # { modelName: function }

# 创建一个缓存对象，缓存最大大小为100，每个键缓存60秒
# 缓存清空的问题需要处理，暂时不管
MODEL_ARGS_CACHE = TTLCache(maxsize=100, ttl=60)
LLM_CLIENT_CACHE = TTLCache(maxsize=100, ttl=60)
EMBEDDING_FUNCTION_CACHE = TTLCache(maxsize=100, ttl=60)

class LLMClient:
  def __init__(self, userId: str = None, modlId: str = None, temperature: float = 0.1):
    self.temperature = temperature
    self.args = get_model_arguments(userId, modlId, 'llm')
    self.model = self.args['model']
    self.provider = self.args['provider']
    self.client = self.get_llm_client()
  def get_llm_client(self):
    if self.provider == 'ollama':
      return Ollama(model=self.model, base_url=self.args.get('base_url', None), temperature=self.temperature)
    else:
      return ChatOpenAI(model=self.model, base_url=self.args.get('base_url', None), api_key=self.args.get('api_key', None), temperature=self.temperature)
  def invoke(self, prompts: str):
    return self.client.invoke(prompts)
  def stream(self, prompts: str):
    return self.client.stream(input=prompts)

class EmbeddingFunction:
  def __init__(self, userId: str = None, modlId: str = None):
    self.args = get_model_arguments(userId, modlId, 'text-embedding')
    self.model = self.args['model']
    self.provider = self.args['provider']
    self.function = self.get_embedding_function()
  def get_embedding_function(self):
    if self.provider =='ollama':
      return OllamaEmbeddings(model=self.model, base_url=self.args.get('base_url', None))
    elif self.provider == 'default':
      model = self.model
      if (model in DEFAULT_EMBEDDING_FUNCTION_MAP):
        return DEFAULT_EMBEDDING_FUNCTION_MAP[model]
      model_dir = self.args.get('model_dir', MODEL_DIR)
      if (not model_dir.endswith('/')):
        model_dir = model_dir + '/'
      model_name = model
      if (not model_name.startswith(model_dir)): # 需要添加上默认的路径
        model_name = model_dir + model_name
      # 将系统默认的嵌入向量缓存到内存中
      DEFAULT_EMBEDDING_FUNCTION_MAP[model] = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': DEFAULT_EMBEDDING_DEVICE},
        encode_kwargs={'normalize_embeddings': True} # 归一化处理
      )
      return DEFAULT_EMBEDDING_FUNCTION_MAP[model]
    else:
      return OpenAIEmbeddings(model=self.model, openai_api_base=self.args.get('base_url', None), openai_api_key=self.args.get('api_key', None))

# 获取知识库的嵌入模型
@cached(EMBEDDING_FUNCTION_CACHE)
def get_repos_embedding_function(reposId:str):
  with session_scope(True) as session:
    repos = session.get(ReposInfo, reposId)
    if (repos is None):
      logger.warn(f'llm_client_tools.get_repos_embedding_function: reposId={reposId} not found')
      return EmbeddingFunction(userId=None, modlId=None).function
    vecModlId = repos.vecModlId
    userId = repos.crtUser # 知识库创建用户设置的模型信息
    if (vecModlId is None or vecModlId == ''):
      logger.warn(f'llm_client_tools.get_repos_embedding_function: reposId={reposId} has no vector model')
    return EmbeddingFunction(userId=userId, modlId=vecModlId).function

def get_user_llm_client(userId: str, modlId: str = None, temperature: float = 0.1):
  return LLMClient(userId, modlId, temperature)

# 获取用户的模型首选项 返回 { llm: modlId, text-embedding: modlId }
def get_user_model_preference(userId: str):
  with session_scope(True) as session:
    stmt = select(SettingEmrt).where(SettingEmrt.prmCd == SYSTEM_MODEL_PREFERENCE_PARAM_CODE, SettingEmrt.userId == userId)
    emrts = {}
    for row in session.scalars(stmt):
      emrts[row.valCd] = row.prmVal
    return emrts

def get_default_model_arguments(modlTyp: str = 'llm'):
  if modlTyp == 'llm':
    if (DEFAULT_LLM_ARGUMENTS is None):
      raise Exception('请在[设置/模型设置]中配置模型首选项')
    return DEFAULT_LLM_ARGUMENTS
  elif modlTyp == 'text-embedding':
    return DEFAULT_EMBEDDING_ARGUMENTS
  logger.warn(f'llm_client_tools.get_default_model_arguments: unknown modlTyp={modlTyp}')
  return {}

# 根据用户id和模型id获取模型参数
@cached(MODEL_ARGS_CACHE)  # 使用缓存装饰器
def get_model_arguments(userId: str = None, modlId: str = None, modlTyp: str = 'llm'):
  if (userId is None or userId == ''):
    logger.warn(f'llm_client_tools.get_model_arguments: userId is None, use default {modlTyp} model arguments')
    return get_default_model_arguments(modlTyp)
  if (modlId is None or modlId == ''):
    modlId = get_user_model_preference(userId).get(modlTyp, None)
    if modlId is None or modlId == '':
      logger.warn(f'llm_client_tools.get_model_arguments: userId={userId} has no preference for {modlTyp} model')
      return get_default_model_arguments(modlTyp) # text-emebedding 模型需要再处理，暂时不管
  with session_scope(True) as session:
    model = session.get(ModelPrvdModl, modlId) # 查询模型信息
    if model is None: # 模型不存在，暂时不管
      logger.warn(f'llm_client_tools.get_model_arguments: model not found, modlId={modlId}')
      return get_default_model_arguments(modlTyp)
    prvdId = model.prvdId
    provider = session.get(ModelPrvdInfo, prvdId)
    if provider is None: # 模型提供方不存在，暂时不管
      logger.warn(f'llm_client_tools.get_model_arguments: provider not found, prvdId={prvdId}')
      return get_default_model_arguments(modlTyp)
    # 先查询用户自己配置的供应商级别的参数以及系统默认级别的参数
    params = session.query(ModelParam).where(ModelParam.prvdId == prvdId, ModelParam.modlId.is_(None), ModelParam.userId.in_([userId, DEFAULT_SYSTEM_USER_ID])).all()
    args = {}
    args['provider'] = prvdId
    args['model'] = model.modlNm
    # 再查询模型级别的参数
    params.extend(session.query(ModelParam).where(ModelParam.prvdId == prvdId, ModelParam.modlId == modlId, ModelParam.userId.in_([userId, DEFAULT_SYSTEM_USER_ID])).all())
    for param in params: # 覆盖用户配置的参数
      prmVal = param.prmVal
      if(param.valEcrp == 'Y'):
        if (prmVal is not None and prmVal != ''):
          args[param.prmCd] = aes_decrypt(prmVal)
      else:
        args[param.prmCd] = prmVal
    base_url = args.get('base_url', None)
    if (base_url is None):
      base_url = LLM_BASE_URLS.get(prvdId, None)
    if (base_url is not None):
      args['base_url'] = base_url
  return args