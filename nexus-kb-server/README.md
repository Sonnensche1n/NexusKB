# 环境准备
- python 3.11.5
- uv (用于包管理)

# 依赖安装
- uv sync --python 3.11

# 打包方式
- PyInstaller

# 启动方式
- uv run uvicorn app:app --host 0.0.0.0 --port 16088 --reload
- nohup uv run uvicorn app:app --host 0.0.0.0 --port 16088 --reload > nexus-kb.log 2>&1 &
- uv run app.py