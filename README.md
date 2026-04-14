# NexusKB - 智能个人知识库桌面应用

NexusKB 是一款基于大语言模型（LLM）的下一代知识管理工具，融合AI能力重新定义知识组织方式。支持多源知识整合、智能问答、自动化知识加工和可视化知识网络，助力构建您的第二大脑。

## ✨ 核心功能

### 智能知识库管理
* **多格式导入**：支持文档（PDF/Word/Markdown）、网页链接、纯文本等多源数据接入
* **AI自动化处理**：自动分段、生成摘要、创建Q&A对、提取知识图谱三元组
* **动态维护**：支持文档版本管理、知识关联标注、批量处理操作
* **双模式编辑器**：Markdown + 富文本混合编辑

### 强大的搜索与问答
* **混合检索架构**：采用 向量粗排 (ChromaDB MMR) + Reranker 模型二阶精排 的检索增强生成 (RAG) 架构，显著提升上下文相关性。
* **对话式交互**：支持追问、溯源引用、多轮知识推理

### 🌐 多模型支持
兼容 OpenAI GPT、DeepSeek、Moonshot AI等主流大模型，支持连接Ollama本地模型部署。

## 🚀 快速开始

本项目分为前端（Vue3 + Tauri）和后端（Python）两部分。

### 0. 源码克隆 (关于 m3e 模型与 Git LFS)
本项目使用 Git LFS 来管理大文件（如 `m3e` 向量模型）。如果你在 `git clone` 时遇到下载失败或卡顿，通常是因为网络环境限制。

**🚀 最快/最推荐的解决方案：跳过 LFS + 手动下载模型**
1. **跳过大文件克隆**：先仅克隆代码主体，跳过模型下载，保证代码库秒级拉取成功。
   ```bash
   GIT_LFS_SKIP_SMUDGE=1 git clone <你的项目仓库地址>
   cd NexusKB
   ```
2. **手动下载模型**：前往国内镜像站（如 [魔搭社区 ModelScope](https://modelscope.cn/models/moka-ai/m3e-base/files) 或 HF-Mirror）下载 `m3e` 模型文件，然后将下载的模型内容直接放入项目对应的模型存放目录：`nexus-kb-server/resources/model/m3e/`（如果使用的是 m3e-small，则放到 `m3e-small` 子目录下）。

**备选方案：配置代理后拉取**
如果你有稳定的代理，也可以在克隆后配置 Git 代理并使用 LFS 拉取：
   ```bash
   git config --global http.proxy http://127.0.0.1:你的代理端口
   git lfs pull
   ```

### 1. 前端启动 (NexusKB Client)

确保你已经安装了 [Node.js](https://nodejs.org/)。
如果想以桌面原生应用形式启动，你需要安装 [Rust](https://www.rust-lang.org/tools/install)。

```bash
cd nexus-kb-client
npm install

# 选项 A：在浏览器中预览（速度快，适合调试 UI）
npm run dev

# 选项 B：作为独立桌面应用启动（需要 Rust 环境）
npm run tauri dev
```
> **如何结束桌面端进程？**
> 在启动了 `npm run tauri dev` 的终端中，按 `Ctrl + C` 即可强制停止进程并关闭窗口。

### 2. 后端启动 (NexusKB Server)

确保你已经安装了 [uv](https://docs.astral.sh/uv/)，并使用 Python 3.11+。

> **💡 关于 Reranker API Key 配置（可选但推荐）**
> 项目开启了基于硅基流动 API 的 Reranker 精排功能以提升检索精度。你需要去 [硅基流动官网](https://cloud.siliconflow.cn/) 免费申请一个 API Key。
> **配置方法：**
> 在 `nexus-kb-server` 目录下创建一个 `.env` 文件，写入：
> ```env
> RERANKER_API_KEY=sk-你的APIKey
> ```
> *(注：`.env` 文件已被 Git 忽略，不会上传到仓库中。如果你不配置此项，系统将自动跳过精排阶段，不影响基础功能。)*

```bash
cd nexus-kb-server
uv sync --python 3.11
uv run app.py
```

### 3. 使用 Docker 部署后端 (可选)

如果你不想在本地安装 Python 环境，你可以使用 Docker 一键启动后端。

```bash
cd nexus-kb-server

# 构建 Docker 镜像
docker build -t nexus-kb-server .

# 运行容器，将本地 16088 端口映射到容器内
docker run -d -p 16088:16088 --name nexus-kb nexus-kb-server
```

## 🛠️ 技术栈
* 前端：Vue 3 + Tauri + Naive UI + Vite
* 后端：Python + FastAPI/Flask (根据实际架构) + LangChain + 向量数据库
* AI 能力：支持 OpenAI、DeepSeek、Ollama 等多模态 LLM

## 📄 License
MIT License
