from sqlalchemy import Column, String, Integer
from server.db.DbManager import Base

# 模型提供方信息
class ModelPrvdInfo(Base):
  __tablename__ = 't_sys_model_prvd_info'
	# 表的结构
  prvdId = Column(String(100), name='prvd_id', primary_key=True)
  prvdNm = Column(String(200), name='prvd_nm')
  prvdDesc = Column(String(2000), name='prvd_desc')
  prvdIcon = Column(String(1000), name='prvd_icon')
  modlTyp = Column(String(100), name='modl_typ')

# 模型提供方参数
class ModelPrvdParam(Base):
  __tablename__ = 't_sys_model_prvd_param'
	# 表的结构
  prvdId = Column(String(100), name='prvd_id', primary_key=True)
  prmCd = Column(String(100), name='prm_cd', primary_key=True)
  prmNm = Column(String(200), name='prm_nm')
  prmDesc = Column(String(2000), name='prm_desc')
  dftVal = Column(String(2000), name='dft_val')
  prmLvl = Column(String(10), name='prm_lvl')
  modlTyp = Column(String(100), name='modl_typ')
  prmOdr = Column(Integer, name='prm_odr')
  notNull = Column(String(1), name='not_null')
  optVals = Column(String(1000), name='opt_vals')
  reqEcrp = Column(String(1), name='req_ecrp')

# 模型提供方模型
class ModelPrvdModl(Base):
  __tablename__ = 't_sys_model_prvd_modl'
	# 表的结构
  modlId = Column(String(32), name='modl_id', primary_key=True)
  prvdId = Column(String(100), name='prvd_id')
  modlNm = Column(String(200), name='modl_nm')
  modlTyp = Column(String(100), name='modl_typ')
  userId = Column(String(32), name='user_id')
  modlIcon = Column(String(1000), name='modl_icon')
  builtIn = Column(String(1), name='built_in')


# 模型配置信息
class ModelSetting(Base):
  __tablename__ = 't_sys_model_setting'
	# 表的结构
  userId = Column(String(32), name='user_id', primary_key=True)
  prvdId = Column(String(100), name='prvd_id', primary_key=True)

# 模型配置参数
class ModelParam(Base):
  __tablename__ = 't_sys_model_param'
	# 表的结构
  prmId = Column(String(32), name='prm_id', primary_key=True)
  prvdId = Column(String(100), name='prvd_id')
  modlId = Column(String(32), name='modl_id')
  userId = Column(String(32), name='user_id')
  prmCd = Column(String(100), name='prm_cd')
  prmVal = Column(String(2000), name='prm_val')
  valEcrp = Column(String(1), name='val_ecrp')

# 系统参数设置
class SettingParam(Base):
  __tablename__ = 't_sys_setting_param'
	# 表的结构
  prmId = Column(String(32), name='prm_id', primary_key=True)
  prmCd = Column(String(100), name='prm_cd')
  prmNm = Column(String(200), name='prm_nm')
  prmVal = Column(String(2000), name='prm_val')
  whthEmrt = Column(String(1), name='whth_emrt')
  userId = Column(String(32), name='user_id')
  prmDesc = Column(String(2000), name='prm_desc')

# 系统参数枚举值
class SettingEmrt(Base):
  __tablename__ = 't_sys_setting_emrt'
	# 表的结构
  prmId = Column(String(32), name='prm_id', primary_key=True)
  valCd = Column(String(200), name='val_cd', primary_key=True)
  prmCd = Column(String(100), name='prm_cd')
  userId = Column(String(32), name='user_id')
  prmVal = Column(String(2000), name='prm_val')
  valOdr = Column(Integer, name='val_odr')

# 文件信息
class FileInfo(Base):
  __tablename__ = 't_sys_file_info'
	# 表的结构
  fileId = Column(String(32), name='file_id', primary_key=True)
  fileNm = Column(String(200), name='file_nm')
  filePath = Column(String(500), name='file_path')
  fileTyp = Column(String(10), name='file_typ')
  crtUser = Column(String(32), name='crt_user')
  crtTm = Column(String, name='crt_tm')
  fileSize = Column(Integer, name='file_size')
  md5Hex = Column(String(32), name='md5_hex')
  sha1Hex = Column(String(40), name='sha1_hex')
  fileUrl = Column(String(100), name='file_url')