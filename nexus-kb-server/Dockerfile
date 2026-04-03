FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装 uv 和必要的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# 复制项目文件
COPY . /app

# 使用 uv 同步依赖 (系统级安装)
RUN uv sync --system

# 暴露后端端口
EXPOSE 16088

# 启动命令
CMD ["uv", "run", "app.py"]
