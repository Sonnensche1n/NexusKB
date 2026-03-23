from openai import OpenAI
from langchain_community.llms import Ollama

# 后面调整为可以配置的内容
OPENAI_MODEL = 'gpt-3.5-turbo'
OPENAI_BASE_URL = 'https://api.openai.com/v1'

NVIDIA_MODEL = 'meta/llama3-70b-instruct'
NVIDIA_BASE_URL = 'https://integrate.api.nvidia.com/v1'

OLLAMA_MODEL = 'qwen2'  # 'gemma2' # 'qwen2' # 'llama3.1'
OLLAMA_BASE_URL = 'http://127.0.0.1:11434'

MOONSHOT_BASE_URL = 'https://api.moonshot.cn/v1'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'
TONGYI_BASE_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
ZHIPUAI_BASE_URL = 'https://open.bigmodel.cn/api/paas/v4'

OLLAMA_CLIENT = Ollama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL, temperature=0.1)

MODEL_DIR = './resources/model'
# 查询向量数据库返回结果的最大数量
TOP_K = 20
MAX_CONTEXT = 20
MAX_HISTORY = 10
TEMPERATURE = 0.1
SIMILARITY_TRVAL = 1

# 默认的模型提供者
LLM_PROVIDER = 'ollama'  # 'ollama' # 'openai' # 'nvidia'
EMBEDDING_PROVIDER = 'default' # 'default' # wenkb表示自己

# DEFAULT_LLM_ARGUMENTS = {
#   'provider': LLM_PROVIDER,
#   'model': OLLAMA_MODEL,
#   'base_url': OLLAMA_BASE_URL
# }
DEFAULT_LLM_ARGUMENTS = None # 客户端不设置默认的大模型参数

# The embedding model name could be one of the following:
#   ghuyong/ernie-3.0-nano-zh
#   nghuyong/ernie-3.0-base-zh
#   shibing624/text2vec-base-chinese
#   GanymedeNil/text2vec-large-chinese
DEFAULT_EMBEDDING_ARGUMENTS = { # 部署后不能再修改默认模型不然，已经构建索引的知识库不能用了
  'provider': EMBEDDING_PROVIDER,
  'model': 'm3e/m3e-small',
  'base_url': None,
  'api_key': None,
  'model_dir': MODEL_DIR
}

LLM_BASE_URLS = {
  'moonshot': MOONSHOT_BASE_URL,
  'nvidia': NVIDIA_BASE_URL,
  'openai': OPENAI_BASE_URL,
  'ollama': OLLAMA_BASE_URL,
  'deepseek': DEEPSEEK_BASE_URL,
  'tongyi': TONGYI_BASE_URL,
  'zhipuai': ZHIPUAI_BASE_URL
}
