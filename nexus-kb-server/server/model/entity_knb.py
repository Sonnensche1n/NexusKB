from pydantic import Field
from typing import Optional
from .entity_base import BaseEntity
from config.llm import TOP_K, MAX_CONTEXT, MAX_HISTORY, TEMPERATURE, SIMILARITY_TRVAL

# 知识库
class ReposInfo(BaseEntity):
  reposId: Optional[str] = Field(None)
  reposNm: Optional[str] = Field(None)
  reposDesc: Optional[str] = Field(None)
  reposIcon: Optional[str] = Field(None)
  reposTyp: Optional[str] = Field(None)
  vecModlId: Optional[str] = Field(None)
  crtUser: Optional[str] = Field(None)
  authRang: Optional[str] = Field(None)
  crtTm: Optional[str] = Field(None)
  optAuth: Optional[str] = Field(None) # 没在数据库中定义，操作权限[visit 访问, alter 修改]

# 知识库问答对
class ReposQuest(BaseEntity):
  qstId: Optional[str] = Field(None)
  reposId: Optional[str] = Field(None)
  dtsetId: Optional[str] = Field(None)
  qstQuest: Optional[str] = Field(None)
  qstAswr: Optional[str] = Field(None)
  qstSrc: Optional[str] = Field(None)

# 数据集
class Dataset(BaseEntity):
  dtsetId: Optional[str] = Field(None)
  reposId: Optional[str] = Field(None)
  dtsetNm: Optional[str] = Field(None)
  dtsetTyp: Optional[str] = Field(None)
  ctlgId: Optional[str] = Field(None)
  idxSts: Optional[str] = Field(None)
  prcsSts: Optional[str] = Field(None)
  qaSts: Optional[str] = Field(None)
  tpltSts: Optional[str] = Field(None)
  enbSts: Optional[str] = Field(None)
  fileNm: Optional[str] = Field(None)
  fileTyp: Optional[str] = Field(None)
  filePath: Optional[str] = Field(None)
  docId: Optional[str] = Field(None)
  docVerId: Optional[str] = Field(None)
  crtUser: Optional[str] = Field(None)
  crtTm: Optional[str] = Field(None)

# 知识库数据集目录
class DatasetCtlg(BaseEntity):
  __tablename__ = 't_knb_dataset_ctlg'
	# 表的结构
  ctlgId: Optional[str] = Field(None)
  ctlgPid: Optional[str] = Field(None)
  ctlgPath: Optional[str] = Field(None)
  reposId: Optional[str] = Field(None)
  ctlgNm: Optional[str] = Field(None)
  ctlgDesc: Optional[str] = Field(None)
  ctlgOdr: Optional[int] = Field(None)

# 数据集分片
class DatasetChunk(BaseEntity):
  chkId: Optional[str] = Field(None)
  dtsetId: Optional[str] = Field(None)
  reposId: Optional[str] = Field(None)
  chkSeq: Optional[int] = Field(None)
  chkCntnt: Optional[str] = Field(None)
  chkAsst: Optional[str] = Field(None)

# 知识库数据集摘要
class DatasetPrecis(BaseEntity):
  prcsId: Optional[str] = Field(None)
  dtsetId: Optional[str] = Field(None)
  reposId: Optional[str] = Field(None)
  prcsSeq: Optional[int] = Field(None)
  prcsCntnt: Optional[str] = Field(None)
  prcsSrc: Optional[str] = Field(None)

# 对话信息
class ChatInfo(BaseEntity):
  chatId: Optional[str] = Field(None)
  reposId: Optional[str] = Field(None)
  chatTtl: Optional[str] = Field(None)
  crtUser: Optional[str] = Field(None)
  crtTm: Optional[str] = Field(None)
  lastTm: Optional[str] = Field(None)

# 对话消息
class ChatMesg(BaseEntity):
  mesgId: Optional[str] = Field(None)
  mesgPid: Optional[str] = Field(None)
  reposId: Optional[str] = Field(None)
  chatId: Optional[str] = Field(None)
  mesgCntnt: Optional[str] = Field(None)
  mesgTyp: Optional[str] = Field(None)
  crtRole: Optional[str] = Field(None)
  crtUser: Optional[str] = Field(None)
  crtTm: Optional[str] = Field(None)

# 对话消息引用的内容
class ChatMesgQuote(BaseEntity):
  mesgId: Optional[str] = Field(None)
  dtsetId: Optional[str] = Field(None)
  dtsetNm: Optional[str] = Field(None)
  fileNm: Optional[str] = Field(None)
  fileTyp: Optional[str] = Field(None)
  score: Optional[float] = Field(None) # 引用内容的相似度
  content: Optional[str] = Field(None) # 引用的内容

# 搜索信息
class SrchInfo(BaseEntity):
  reposId: Optional[str] = Field(None)
  searchTxt: Optional[str] = Field(None)
  noHist: Optional[bool] = Field(True) # 是否记录历史

# 搜索历史
class SrchHist(BaseEntity):
  srchId: Optional[str] = Field(None)
  reposId: Optional[str] = Field(None)
  srchText: Optional[str] = Field(None)
  srchTyp: Optional[str] = Field(None)
  srchTm: Optional[str] = Field(None)
  crtUser: Optional[str] = Field(None)

# 知识库数据集三元组
class DatasetTriplet(BaseEntity):
  tpltId: Optional[str] = Field(None)
  reposId: Optional[str] = Field(None)
  dtsetId: Optional[str] = Field(None)
  tpltSeq: Optional[int] = Field(None)
  tpltSbjct: Optional[str] = Field(None)
  tpltPrdct: Optional[str] = Field(None)
  tpltObjct: Optional[str] = Field(None)
  tpltSrc: Optional[str] = Field(None)

# 知识库数据集索引错误信息
class DatasetIndexError(BaseEntity):
  dtsetId: Optional[str] = Field(None)
  idxTyp: Optional[str] = Field(None)
  errInf: Optional[str] = Field(None)

# 知识库配置
class ReposSetting(BaseEntity):
  reposId: Optional[str] = Field(None)
  maxCtx: Optional[int] = Field(MAX_CONTEXT)
  maxHist: Optional[int] = Field(MAX_HISTORY)
  llmTptur: Optional[float] = Field(TEMPERATURE)
  smlrTrval: Optional[float] = Field(SIMILARITY_TRVAL)
  topK: Optional[int] = Field(TOP_K)