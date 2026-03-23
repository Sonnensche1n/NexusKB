from sqlalchemy import Column, String, Text, Integer
from server.db.DbManager import Base

# 文档集
class DocsetInfo(Base):
  __tablename__ = 't_doc_docset_info'
  # 表的结构
  setId = Column(String(32), name='set_id', primary_key=True)
  setNm = Column(String(32), name='set_nm')
  setDesc = Column(String(2000), name='set_desc')
  setIcon = Column(String(100), name='set_icon')
  authRang = Column(String(10), name='auth_rang')
  crtUser = Column(String(32), name='crt_user')
  crtTm = Column(String, name= 'crt_tm')

# 文档信息
class DocmtInfo(Base):
  __tablename__ = 't_doc_docmt_info'
  # 表的结构
  docId = Column(String(32), name='doc_id', primary_key=True)
  setId = Column(String(32), name='set_id')
  docTtl = Column(String(200), name='doc_ttl')
  docTyp = Column(String(10), name='doc_typ')
  docSts = Column(String(10), name='doc_sts')
  docCntnt = Column(Text, name='doc_cntnt')
  docPid = Column(String(32), name='doc_pid')
  docPath = Column(String(320), name='doc_path')
  crtUser = Column(String(32), name='crt_user')
  crtTm = Column(String, name= 'crt_tm')
  updTm = Column(String, name= 'upd_tm')

# 文档版本
class DocmtVersion(Base):
  __tablename__ = 't_doc_docmt_version'
  # 表的结构
  verId = Column(String(32), name='ver_id', primary_key=True)
  docId = Column(String(32), name='doc_id')
  setId = Column(String(32), name='set_id')
  docTtl = Column(String(200), name='doc_ttl')
  docTyp = Column(String(10), name='doc_typ')
  docCntnt = Column(Text, name='doc_cntnt')
  crtUser = Column(String(32), name= 'crt_user')
  crtTm = Column(String, name= 'crt_tm')