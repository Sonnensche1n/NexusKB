import os
import traceback
from config.common import DB_SCHEMA_VERSION
from sqlalchemy import Column, Integer
from sqlalchemy import text
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from .DbManager import ENGINE, session_scope, Base
from logger import logger
from server.utils.stringutils import is_int_str

DDL_DIR = os.path.join(os.path.dirname(__file__), 'upgrade', 'ddl')
DML_DIR = os.path.join(os.path.dirname(__file__), 'upgrade', 'dml')

inspector = inspect(ENGINE)

class SchemaVersion(Base):
  __tablename__ = 't_sys_schema_version'
  version = Column(Integer, name='version', primary_key=True)

def get_current_version():
  if (SchemaVersion.__tablename__ not in inspector.get_table_names()):
    return 0
  with session_scope(True) as session:
    versions = session.query(SchemaVersion).all()
    return versions[0].version if len(versions) > 0 else 0

def upgrade_db():
  current_version = get_current_version()
  if (current_version == DB_SCHEMA_VERSION): # 版本一致不需要升级
    logger.info('数据库版本一致，不需要升级。')
    return
  logger.error('数据库版本不一致，当前版本为:%d，需要升级到:%d。' % (current_version, DB_SCHEMA_VERSION))
  try:
    execute_ddl(current_version, DB_SCHEMA_VERSION)
    execute_dml(current_version, DB_SCHEMA_VERSION)
  except Exception as e: # 失败还需要进一步处理回滚等操作，暂时不处理
    traceback.print_exc()
    logger.error(e)
    logger.error('升级数据库失败，请检查日志。')
  else:
    logger.info('升级数据库成功')
    with session_scope() as session:
      if (current_version == 0):
        session.add(SchemaVersion(version=DB_SCHEMA_VERSION))
      else:
        session.query(SchemaVersion).filter(SchemaVersion.version == current_version).update({'version': DB_SCHEMA_VERSION})
# 遍历文件夹下的sql文件，并获取文件内容
def get_sql_scripts(dir_path:str, current_version:int, target_version:int):
  paths = []
  for file in os.listdir(dir_path): # 还需要按文件名排序，暂时没做
    if (not file.endswith('.sql')):
      continue
    name = file.split('.')[0]
    if (not is_int_str(name)):
      continue
    name = int(name)
    if (current_version == 0):
      if (name == current_version): # 版本不符合要求，如果没有安装过则直接执行全量脚本，即0.sql
        paths.append(os.path.join(dir_path, file))
    else:
      if (name > current_version and name <= target_version): # 版本不符合要求
        paths.append(os.path.join(dir_path, file))
  # 获取文件的内容
  contents = [open(path, 'r', encoding='utf-8').read() for path in paths]
  scripts = [] # 需要执行的脚本
  for content in contents:
    for line in content.split(';'): # 按分号分割，暂时不支持多行sql以及其他情况
      line = line.strip()
      if (len(line) > 0):
        scripts.append(line)
  return scripts

def execute_ddl(current_version:int, target_version:int):
  logger.info(f'开始升级数据库DDL版本，从 {current_version} 到 {target_version}')
  scripts = get_sql_scripts(DDL_DIR, current_version, target_version)
  with session_scope() as session:
    for script in scripts:
      session.execute(text(script))
  logger.info('升级数据库DDL版本成功')

def execute_dml(current_version:int, target_version:int):
  logger.info(f'开始升级数据库DML版本，从 {current_version} 到 {target_version}')
  scripts = get_sql_scripts(DML_DIR, current_version, target_version)
  with session_scope() as session:
    for script in scripts:
      try:
        session.execute(text(script))
      except IntegrityError as e:
        if ('UNIQUE constraint failed' not in str(e)): # 主键冲突不处理
          raise e
  logger.info('升级数据库DML版本成功')