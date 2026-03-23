from sqlalchemy import Column, String, Text, Integer, Float
from server.db.DbManager import Base

# 知识库
class ReposInfo(Base):
  __tablename__ = 't_knb_repos_info'
	# 表的结构
  reposId = Column(String(32), name='repos_id', primary_key=True)
  reposNm = Column(String(200), name='repos_nm')
  reposDesc = Column(String(2000), name='repos_desc')
  reposIcon = Column(String(100), name='repos_icon')
  reposTyp = Column(String(10), name='repos_typ')
  vecModlId = Column(String(32), name='vec_modl_id')
  crtUser = Column(String(32), name='crt_user')
  authRang = Column(String(10), name= 'auth_rang')
  crtTm = Column(String, name='crt_tm') 

# 知识库问答对
class ReposQuest(Base):
  __tablename__ = 't_knb_repos_quest'
	# 表的结构
  qstId = Column(String(32), name='qst_id', primary_key=True)
  reposId = Column(String(32), name='repos_id')
  dtsetId = Column(String(32), name= 'dtset_id')
  qstQuest = Column(String(2000), name= 'qst_quest')
  qstAswr = Column(Text, name= 'qst_aswr')
  qstSrc = Column(String(10), name= 'qst_src')

# 知识库数据集
class Dataset(Base):
  __tablename__ = 't_knb_dataset'
	# 表的结构
  dtsetId = Column(String(32), name='dtset_id', primary_key=True)
  reposId = Column(String(32), name='repos_id')
  dtsetNm = Column(String(200), name='dtset_nm')
  dtsetTyp = Column(String(10), name='dtset_typ')
  ctlgId = Column(String(32), name='ctlg_id')
  idxSts = Column(String(10), name='idx_sts')
  prcsSts = Column(String(10), name='prcs_sts')
  qaSts = Column(String(10), name='qa_sts')
  tpltSts = Column(String(10), name='tplt_sts')
  enbSts = Column(String(10), name='enb_sts')
  fileNm = Column(String(200), name='file_nm')
  fileTyp = Column(String(10), name= 'file_typ')
  filePath = Column(String(500), name= 'file_path')
  docId = Column(String(32), name='doc_id')
  docVerId = Column(String(32), name='doc_ver_id')
  crtUser = Column(String(32), name= 'crt_user')
  crtTm = Column(String, name='crt_tm')

# 知识库数据集目录
class DatasetCtlg(Base):
  __tablename__ = 't_knb_dataset_ctlg'
	# 表的结构
  ctlgId = Column(String(32), name='ctlg_id', primary_key=True)
  ctlgPid = Column(String(32), name='ctlg_pid')
  ctlgPath = Column(String(32), name='ctlg_path')
  reposId = Column(Integer, name='repos_id')
  ctlgNm = Column(Text, name='ctlg_nm')
  ctlgDesc = Column(Text, name='ctlg_desc')
  ctlgOdr = Column(Integer, name='ctlg_odr')

# 知识库数据集分片
class DatasetChunk(Base):
  __tablename__ = 't_knb_dataset_chunk'
	# 表的结构
  chkId = Column(String(32), name='chk_id', primary_key=True)
  dtsetId = Column(String(32), name='dtset_id')
  reposId = Column(String(32), name='repos_id')
  chkSeq = Column(Integer, name='chk_seq')
  chkCntnt = Column(Text, name='chk_cntnt')
  chkAsst = Column(Text, name='chk_asst')

# 知识库数据集摘要
class DatasetPrecis(Base):
  __tablename__ = 't_knb_dataset_precis'
	# 表的结构
  prcsId = Column(String(32), name='prcs_id', primary_key=True)
  dtsetId = Column(String(32), name='dtset_id')
  reposId = Column(String(32), name='repos_id')
  prcsSeq = Column(Integer, name='prcs_seq')
  prcsCntnt = Column(Text, name='prcs_cntnt')
  prcsSrc = Column(String(10), name= 'prcs_src')

# 知识库会话
class ChatInfo(Base):
  __tablename__ = 't_knb_chat_info'
	# 表的结构
  chatId = Column(String(32), name='chat_id', primary_key=True)
  reposId = Column(String(32), name='repos_id')
  chatTtl = Column(String(200), name='chat_ttl')
  crtUser = Column(String(32), name='crt_user')
  crtTm = Column(String, name='crt_tm')
  lastTm = Column(String, name= 'last_tm')

# 知识库会话消息
class ChatMesg(Base):
  __tablename__ = 't_knb_chat_mesg'
	# 表的结构
  mesgId = Column(String(32), name='mesg_id', primary_key=True)
  mesgPid = Column(String(32), name='mesg_pid')
  reposId = Column(String(32), name='repos_id')
  chatId = Column(String(200), name='chat_id')
  mesgCntnt = Column(Text, name='mesg_cntnt')
  mesgTyp = Column(String(10), name='mesg_typ')
  crtRole = Column(String(10), name= 'crt_role')
  crtUser = Column(String(32), name= 'crt_user')
  crtTm = Column(String, name= 'crt_tm')

# 知识库搜索历史
class SrchHist(Base):
  __tablename__ = 't_knb_srch_hist'
  # 表的结构
  srchId = Column(String(32), name='srch_id', primary_key=True)
  reposId = Column(String(32), name='repos_id')
  srchText = Column(String(2000), name='srch_text')
  srchTyp = Column(String(10), name='srch_typ')
  srchTm = Column(String, name= 'srch_tm')
  crtUser = Column(String(32), name= 'crt_user')

# 知识库数据集三元组
class DatasetTriplet(Base):
  __tablename__ = 't_knb_dataset_triplet'
	# 表的结构
  tpltId = Column(String(32), name='tplt_id', primary_key=True)
  reposId = Column(String(32), name='repos_id')
  dtsetId = Column(String(32), name= 'dtset_id')
  tpltSeq = Column(Integer, name= 'tplt_seq')
  tpltSbjct = Column(String(1000), name= 'tplt_sbjct')
  tpltPrdct = Column(String(1000), name= 'tplt_prdct')
  tpltObjct = Column(String(1000), name= 'tplt_objct')
  tpltSrc = Column(String(10), name= 'tplt_src')

# 知识库数据集索引错误信息
class DatasetIndexError(Base):
  __tablename__ = 't_knb_dataset_index_error'
	# 表的结构
  dtsetId = Column(String(32), name='dtset_id', primary_key=True)
  idxTyp = Column(String(10), name='idx_typ', primary_key=True)
  errInf = Column(Text, name= 'err_inf')

# 知识库配置
class ReposSetting(Base):
  __tablename__ = 't_knb_repos_setting'
	# 表的结构
  reposId = Column(String(32), name='repos_id', primary_key=True)
  maxCtx = Column(Integer, name= 'max_ctx')
  maxHist = Column(Integer, name= 'max_hist')
  llmTptur = Column(Float, name= 'llm_tptur')
  smlrTrval = Column(Float, name= 'smlr_trval')
  topK = Column(Integer, name= 'top_k')