# 环境准备
- python 3.11.5
# 打包方式
- PyInstaller
# 启动方式
- uvicorn app:app --host 0.0.0.0 --port 6088 --reload
- nohup uvicorn app:app --host 0.0.0.0 --port 6088 --reload > nexus-kb.log 2>&1 &
- python ./app.py