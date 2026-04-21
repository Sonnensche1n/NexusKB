# NexusKB - 智能个人知识库桌面应用

NexusKB 是一个面向个人知识沉淀的本地知识库与问答系统，支持文档导入、RAG 检索问答、知识摘要/Q&A/三元组增强，以及基于 Function Calling 和 Agent 的工具化问答流程。

> 截图位置：可在此补充主界面、聊天界面、知识库管理界面截图。

## ✨ 核心功能

### 知识库管理
- 支持 PDF、Word、Markdown、网页链接、纯文本等多源内容导入
- 支持文档分块、摘要生成、Q&A 提取、知识三元组提取
- 支持知识库配置、数据集管理、文档查看与编辑

### 智能问答
- 基于 RAG 的知识库问答，支持引用来源展示
- 支持混合检索：向量检索 + BM25 + Reranker 精排
- 支持 Function Calling 工具调用
- 支持 Agent 模式下的多步检索与综合回答

### 本地化模型支持
- 支持 Ollama 本地模型
- 兼容 OpenAI、DeepSeek、Moonshot、通义、智谱等 OpenAI 兼容接口
- 支持本地 Embedding 模型与可选 Reranker 配置

## 🛠️ 技术栈

### 前端
- Vue 3
- Vite
- Tauri 2
- Naive UI
- md-editor-v3

### 后端
- Python 3.11
- FastAPI
- SQLAlchemy
- LangChain
- ChromaDB

### AI / RAG
- Ollama
- OpenAI Compatible API
- M3E Embedding
- BGE Reranker
- BM25 / RRF / HyDE
- Function Calling / Agent

## 🚀 快速开始

### 方式一：本地开发启动

#### 1. 启动前端
确保你已经安装 [Node.js](https://nodejs.org/)。
如果需要桌面端能力，请安装 [Rust](https://www.rust-lang.org/tools/install)。

```bash
cd nexus-kb-client
npm install

# 浏览器调试
npm run dev

# 桌面应用调试
npm run tauri dev
```

#### 2. 启动后端
确保你已经安装 [uv](https://docs.astral.sh/uv/) 且本地 Python 为 3.11+。

```bash
cd nexus-kb-server
uv sync --python 3.11
uv run app.py
```

默认访问地址：
- 前端开发服务：`http://localhost:5173`
- 后端服务：`http://127.0.0.1:16088`

### 方式二：Docker 一键部署

项目已提供 `docker-compose.yml`、前端容器构建文件和 `Makefile`。

```bash
# 校验编排文件
make config

# 一键启动
make start

# 查看日志
make logs

# 停止服务
make stop
```

启动后默认访问：
- 前端：`http://localhost:11420`
- 后端：`http://localhost:16088`

## ⚙️ 配置说明

### LLM / Embedding
- 后端模型配置位于 `nexus-kb-server/config/llm.py`
- 用户维度的模型选择可在前端设置页配置
- 默认支持本地 Ollama 与 OpenAI 兼容接口

### Reranker
- Reranker 配置位于 `nexus-kb-server/config/llm.py`
- 可配置是否启用、服务提供方、模型名、API Key

### Function Calling / Agent
- `FC_ENABLED`：是否启用 Function Calling
- `FC_MAX_ROUNDS`：最大工具调用轮次
- `AGENT_MODE`：是否启用多步 Agent 模式

### 本地资源目录
- 数据库：`nexus-kb-server/resources/database`
- 向量索引：`nexus-kb-server/resources/vector_store`
- 文档资源：`nexus-kb-server/resources/documents`
- 模型文件：`nexus-kb-server/resources/model`

## 📁 目录结构

```text
NexusKB/
├── nexus-kb-client/          # Vue3 + Tauri 前端
├── nexus-kb-server/          # Python 后端
│   ├── server/api/           # 接口层
│   ├── server/core/          # 核心业务 / 工具 / 队列 / 调度
│   ├── server/model/         # ORM / Entity
│   ├── config/               # 配置项
│   ├── resources/            # 数据库、向量索引、模型与静态资源
│   └── text_splitter/        # 文本切分相关逻辑
├── docker-compose.yml        # 容器编排
└── Makefile                  # 一键启动命令
```

## 🔌 主要接口

### 知识库与数据集
- `POST /knb/repository/my/list`
- `POST /knb/dataset/list`
- `POST /knb/repository/guess/list`

### 对话
- `POST /knb/chat`
- `POST /knb/chat/message`
- `POST /knb/chat/remessage`
- `POST /knb/chat/message/list`

### WebSocket / SSE
- `WS /ws/knb/{client_id}`
- 对话流式输出通过 SSE 返回消息块、引用信息、错误信息与工具状态

## 🧪 开发说明

### 推荐开发方式
- 前端使用 `npm run dev`
- 后端使用 `uv run app.py`
- 桌面端调试使用 `npm run tauri dev`

### 当前问答链路
- 基础模式：RAG 检索 + 流式回答
- FC 模式：模型自动调用工具检索知识库
- Agent 模式：复杂问题先规划，再多步执行检索，最后综合回答

### 当前内置工具
- `search_knowledge_base`
- `get_document_summary`
- `search_qa_pairs`
- `search_knowledge_triplets`

## 📝 Changelog

### 当前版本新增
- 新增 Function Calling 能力
- 新增 Tool Registry 工具注册机制
- 新增 Agent 多步问答模式
- 新增聊天历史滑动窗口压缩
- 新增 Docker Compose 与 Makefile 一键部署

## 📄 License

MIT License
