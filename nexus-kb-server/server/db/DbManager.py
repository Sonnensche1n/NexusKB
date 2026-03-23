from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from contextlib import contextmanager
from config.datasource import DB_URI
# 初始化数据库连接
ENGINE = create_engine(DB_URI, echo=True) # echo=True 参数表示连接发出的 SQL 将被记录到标准输出。
SESSION = sessionmaker(ENGINE)  # 构建session对象
class Base:
  __allow_unmapped__ = True
  def copy_from_dict(self, dict_:dict, convert = None, excludes:list = []):
    for key, value in dict_.items():
      if (key in excludes):
        continue
      if convert is not None:
        value = convert(key, value)
      setattr(self, key, value)
    return self
  def to_dict(self, convert = None, excludes:list = []):
    if ('_sa_instance_state' not in excludes):
      excludes.append('_sa_instance_state')
    dict_ = vars(self)
    new_dict = {}
    for key, value in dict_.items():
      if (key in excludes):
        continue
      if convert is not None:
        value = convert(key, value)
      if (value is not None and isinstance(value, datetime)):
        value = value.isoformat() # 不处理,不能序列化为 json
      new_dict[key] = value
    return new_dict
  
Base = declarative_base(cls=Base)  # SQLORM基类

@contextmanager
def session_scope(query:bool = False):
  """Provide a transactional scope around a series of operations."""
  session = SESSION()
  try:
    yield session
    if not query:
      session.commit()
  except:
    if not query:
      session.rollback()
    raise
  finally:
    session.close()