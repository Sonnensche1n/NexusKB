import os
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
# 默认 LLM 参数兜底：当用户未在“设置/模型设置”中选择首选项时使用。
# 这样可以保证黑盒链路（上传文档 -> 检索 -> 对话）在全新环境下也能直接跑通。
DEFAULT_LLM_ARGUMENTS = {
  'provider': 'ollama',
  'model': OLLAMA_MODEL,
  'base_url': OLLAMA_BASE_URL,
  'api_key': None,
}

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

# ============================================================
# Reranker 重排序配置
# ============================================================

# 是否启用 Reranker（设为 False 则完全不影响现有逻辑）
RERANKER_ENABLED = True

# Reranker 服务提供商："api" (如硅基流动) 或 "local" (如 Xinference)
RERANKER_PROVIDER = "api"

# Reranker API 基础地址
RERANKER_BASE_URL = "https://api.siliconflow.cn/v1"

# 本地 Reranker 服务地址 (当 RERANKER_PROVIDER="local" 时使用)
RERANKER_LOCAL_URL = "http://localhost:9997/v1"

# Reranker 模型名称
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

# Reranker API Key（优先从环境变量获取，也可以在 .env 文件中配置）
RERANKER_API_KEY = os.environ.get("RERANKER_API_KEY", "")

# 精排后返回的 Top N 数量（建议与 TOP_K 保持一致）
RERANKER_TOP_N = 20

# 向量粗召回的扩大系数
# 启用 Reranker 时，实际召回量 = TOP_K × RERANKER_RECALL_MULTIPLIER
# 召回池太小精排没意义，太大浪费延迟，3 倍是业界经验值
RERANKER_RECALL_MULTIPLIER = 3

# ============================================================ 
# HyDE 查询扩展配置 
# ============================================================ 
HYDE_ENABLED = True  # 是否启用 HyDE 查询扩展

# ============================================================ 
# 混合检索配置 
# ============================================================ 
HYBRID_SEARCH_ENABLED = True  # 是否启用 BM25 + 向量混合检索

# ============================================================
# Function Calling / Agent 模式配置
# ============================================================
FC_ENABLED = True
FC_MAX_ROUNDS = 5
AGENT_MODE = False
