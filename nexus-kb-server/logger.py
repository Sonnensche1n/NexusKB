#!/usr/bin/env python
# coding=utf-8
"""
# @Time    : 2024/4/8
# @Author  : Summer
# @File    : logger.py
# @describe:
"""
import colorlog
import logging
from logging.handlers import TimedRotatingFileHandler

# 创建logger对象
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 创建handler
stream_handler = logging.StreamHandler()
# 创建TimedRotatingFileHandler对象,每天生成一个文件，共备份10个文件
file_handler = TimedRotatingFileHandler(filename='resources/logs/app.log', when='D', interval=1, backupCount=10, encoding='utf-8')

# 创建带颜色的formatter
formatter = colorlog.ColoredFormatter(
  "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
  datefmt=None,
  reset=True,
  log_colors={
    'DEBUG':    'cyan',
    'INFO':     'green',
    'WARNING':  'yellow',
    'ERROR':    'red',
    'CRITICAL': 'red,bg_white',
  },
  secondary_log_colors={},
  style='%'
)

# 设置handler的formatter
stream_handler.setFormatter(formatter)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# logging.basicConfig(handlers=[stream_handler, file_handler], level=logging.DEBUG)
# 将handler添加到logger中
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

# 记录示例日志
# logger.debug('Debug message')
# logger.info('Info message')
# logger.warning('Warning message')
# logger.error('Error message')
# logger.critical('Critical message')