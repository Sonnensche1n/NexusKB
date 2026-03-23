from pydantic import BaseModel, Field
from typing import Optional
from .entity_base import BaseEntity, PageBase
# 模型提供方信息
class ModelPrvdInfo(BaseEntity):
  prvdId: Optional[str] = Field(None)
  prvdNm: Optional[str] = Field(None)
  prvdDesc: Optional[str] = Field(None)
  prvdIcon: Optional[str] = Field(None)
  modlTyp: Optional[str] = Field(None)

# 模型提供方参数
class ModelPrvdParam(BaseEntity):
  prvdId: Optional[str] = Field(None)
  prmCd: Optional[str] = Field(None)
  prmNm: Optional[str] = Field(None)
  prmDesc: Optional[str] = Field(None)
  dftVal: Optional[str] = Field(None)
  prmLvl: Optional[str] = Field(None)
  modlTyp: Optional[str] = Field(None)
  prmOdr: Optional[int] = Field(None)
  notNull: Optional[str] = Field(None)
  optVals: Optional[str] = Field(None)
  reqEcrp: Optional[str] = Field(None)

# 模型提供方模型
class ModelPrvdModl(BaseEntity):
  modlId: Optional[str] = Field(None)
  prvdId: Optional[str] = Field(None)
  modlNm: Optional[str] = Field(None)
  modlTyp: Optional[str] = Field(None)
  userId: Optional[str] = Field(None)
  modlIcon: Optional[str] = Field(None)
  builtIn: Optional[str] = Field(None)

# 模型配置信息
class ModelSetting(BaseEntity):
  userId: Optional[str] = Field(None)
  prvdId: Optional[str] = Field(None)

# 模型配置参数
class ModelParam(BaseEntity):
  prmId: Optional[str] = Field(None)
  prvdId: Optional[str] = Field(None)
  modlId: Optional[str] = Field(None)
  userId: Optional[str] = Field(None)
  prmCd: Optional[str] = Field(None)
  prmVal: Optional[str] = Field(None)
  valEcrp: Optional[str] = Field(None) # 已经加密存储
  reqEcrp: Optional[str] = Field(None) # 保存的时候需要加密存储 数据库中没有此字段

# 系统参数设置
class SettingParam(BaseEntity):
  prmId: Optional[str] = Field(None)
  prmCd: Optional[str] = Field(None)
  prmNm: Optional[str] = Field(None)
  prmVal: Optional[str] = Field(None)
  whthEmrt: Optional[str] = Field(None)
  userId: Optional[str] = Field(None)
  prmDesc: Optional[str] = Field(None)
  prmEmrts: Optional[list] = Field(None) # 数据库中没有此字段

# 系统参数枚举值
class SettingEmrt(BaseEntity):
  prmId: Optional[str] = Field(None)
  valCd: Optional[str] = Field(None)
  prmCd: Optional[str] = Field(None)
  userId: Optional[str] = Field(None)
  prmVal: Optional[str] = Field(None)
  valOdr: Optional[int] = Field(None)

# 文件信息
class FileInfo(BaseEntity):
	# 表的结构
  fileId: Optional[str] = Field(None)
  fileNm: Optional[str] = Field(None)
  filePath: Optional[str] = Field(None)
  fileTyp: Optional[str] = Field(None)
  crtUser: Optional[str] = Field(None)
  crtTm: Optional[str] = Field(None)
  fileSize: Optional[int] = Field(None)
  md5Hex: Optional[str] = Field(None)
  sha1Hex: Optional[str] = Field(None)
  fileUrl: Optional[str] = Field(None)