import os
# 判断文件夹是否存在
def is_dir_exist(path: str) -> bool:
  return os.path.exists(path) and os.path.isdir(path)
# 判断文件是否存在
def is_file_exist(path: str) -> bool:
  return os.path.exists(path) and os.path.isfile(path)

# 如果文件夹不存在则创建该文件夹
def create_dir_if_not_exist(path: str) -> bool:
  if not is_dir_exist(path):
    os.makedirs(path)
    return True
  return False

# 如果文件不存在则创建该文件
def create_file_if_not_exist(path: str) -> bool:
  if not is_file_exist(path):
    with open(path, 'w') as f:
      pass
    return True
  return False

DB_DIR = './resources/database'
DB_NAME = 'wenkb.db'
DB_PATH = os.path.join(DB_DIR, DB_NAME)

create_dir_if_not_exist(DB_DIR)
create_file_if_not_exist(DB_PATH)

DB_URI = f"sqlite:///{DB_PATH.replace('./', '')}"