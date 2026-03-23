import os
# 获取当前脚本所在的目录
BUILD_PY_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BUILD_PY_DIR) if '_internal' in BUILD_PY_DIR else BUILD_PY_DIR # 处理 pyinstaller 打包后，在 pyinstaller 打包后的目录的上一级目录下执行脚本
os.chdir(ROOT_DIR) # 设置当前工作目录为脚本所在目录
import uvicorn
from multiprocessing import freeze_support
from fastapi.middleware.cors import CORSMiddleware
from app import app

# 添加CORS中间件
app.add_middleware(
  CORSMiddleware,
  # 允许跨域的源列表，例如 ["http://www.example.org"] 等等，["*"] 表示允许任何源
  allow_origins=["*"],
  # 跨域请求是否支持 cookie，默认是 False，如果为 True，allow_origins 必须为具体的源，不可以是 ["*"]
  allow_credentials=False,
  # 允许跨域请求的 HTTP 方法列表，默认是 ["GET"]
  allow_methods=["*"],
  # 允许跨域请求的 HTTP 请求头列表，默认是 []，可以使用 ["*"] 表示允许所有的请求头
  # 当然 Accept、Accept-Language、Content-Language 以及 Content-Type 总之被允许的
  allow_headers=["*"],
  # 可以被浏览器访问的响应头, 默认是 []，一般很少指定
  # expose_headers=["*"]
  # 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600，一般也很少指定
  # max_age=1000
)

if __name__ == '__main__':
  freeze_support() # freeze_support() 方法是用于在使用 PyInstaller、Py2exe、cx_Freeze 等工具进行打包时的多进程代码中的线程中使用的。在 Windows 平台上，由于操作系统的限制，当使用这些工具将 Python 脚本打包成可执行文件时，会出现一些问题。其中一个常见的问题是该脚本无法正确地启动多进程。这是由于在 Windows 上，多进程的启动需要一些特殊的处理。而 freeze_support() 方法就是用于解决这个问题的
  # PyInstaller --noconsole 打包不配置日志的话会报错,这样配置日志
  log_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
      "file_handler": {
        "class": "logging.FileHandler",
        "filename": "./resources/logs/logfile.log",
      },
    },
    "root": {
      "handlers": ["file_handler"],
      "level": "ERROR",
    },
  }
  uvicorn.run(app, host='0.0.0.0', port=16088, log_level='error', log_config=log_config)