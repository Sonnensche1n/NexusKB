from pydantic import Field
from typing import Optional
from .entity_base import BaseEntity

# 文档集
class DocsetInfo(BaseEntity):
  setId: Optional[str] = Field(None)
  setNm: Optional[str] = Field(None)
  setDesc: Optional[str] = Field(None)
  setIcon: Optional[str] = Field(None)
  authRang: Optional[str] = Field(None)
  crtUser: Optional[str] = Field(None)
  crtTm: Optional[str] = Field(None)
  optAuth: Optional[str] = Field(None) # 没在数据库中定义，操作权限[visit 访问, alter 修改]

# 文档信息
class DocmtInfo(BaseEntity):
  docId: Optional[str] = Field(None)
  setId: Optional[str] = Field(None)
  docTtl: Optional[str] = Field(None)
  docTyp: Optional[str] = Field(None)
  docSts: Optional[str] = Field(None)
  docCntnt: Optional[str] = Field(None)
  docPid: Optional[str] = Field(None)
  docPath: Optional[str] = Field(None)
  crtUser: Optional[str] = Field(None)
  crtTm: Optional[str] = Field(None)
  updTm: Optional[str] = Field(None)

# 文档版本
class DocmtVersion(BaseEntity):
  verId: Optional[str] = Field(None)
  docId: Optional[str] = Field(None)
  setId: Optional[str] = Field(None)
  docTtl: Optional[str] = Field(None)
  docTyp: Optional[str] = Field(None)
  docCntnt: Optional[str] = Field(None)
  crtUser: Optional[str] = Field(None)
  crtTm: Optional[str] = Field(None)