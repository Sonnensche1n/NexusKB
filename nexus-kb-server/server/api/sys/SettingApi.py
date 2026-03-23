from fastapi import FastAPI, Request
from server.db.DbManager import session_scope
from server.api.BaseApi import BaseApi
from sqlalchemy import select, delete, or_
from server.model.orm_sys import ModelPrvdInfo, ModelPrvdParam, ModelPrvdModl, ModelSetting, ModelParam, SettingParam, SettingEmrt
from server.model.entity_sys import ModelPrvdInfo as ModelPrvdInfoEntity, ModelPrvdParam as ModelPrvdParamEntity, ModelPrvdModl as ModelPrvdModlEntity, ModelParam as ModelParamEntity, SettingParam as SettingParamEntity, SettingEmrt as SettingEmrtEntity
from server.exception.exception import BaseBusiException
from server.utils.secretutils import aes_encrypt, aes_decrypt
from config.common import DEFAULT_SYSTEM_USER_ID

def replace_with_asterisks(s):
  # 获取原始字符串的长度
  length = len(s)
  # 检查字符串是否足够长以进行替换
  if length < 8:  # 至少需要8个字符才能替换
    return s
  # 使用分段获取需要保留的部分，并使用 '*' 替换中间部分
  new_s = s[:6] + '*' * (length - 8) + s[-2:]
  return new_s

class SettingApi(BaseApi):
  def __init__(self, app: FastAPI):
    BaseApi.__init__(self)
    
    # 查询模型供应商列表
    @app.post('/sys/model/prvd/list')
    def modelProviderList(prvd: ModelPrvdInfoEntity=None):
      list = []
      with session_scope(True) as session:
        stmt = select(ModelPrvdInfo)
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 查询用户设置过的供应商列表
    @app.post('/sys/model/prvd/my/list')
    def myModelProviderList(request: Request):
      userId = self.getUserId(request)
      with session_scope(True) as session:
        settings = session.query(ModelSetting).where(or_(ModelSetting.userId == userId, ModelSetting.userId == DEFAULT_SYSTEM_USER_ID)).all()
        if (len(settings) == 0):
          return self.success([])
        prvdIds = [setting.prvdId for setting in settings]
        return self.success(session.query(ModelPrvdInfo).where(ModelPrvdInfo.prvdId.in_(prvdIds)).all())
    
    # 查询模型供应商的模型列表
    @app.get('/sys/model/prvd/modl/my/list/{prvdId}')
    def modelProviderModelList(prvdId:str, request: Request):
      userId = self.getUserId(request)
      with session_scope(True) as session:
        orms = session.query(ModelPrvdModl).filter(ModelPrvdModl.prvdId == prvdId).all()
        orms = [ModelPrvdModlEntity().copy_from_dict(orm.to_dict()) for orm in orms if orm.userId is None or orm.userId == userId]
        return self.success(orms)

    # 查询模型供应商参数列表
    @app.get('/sys/model/prvd/param/list/{prvdId}')
    def modelProviderParamList(prvdId:str):
      list = []
      with session_scope(True) as session:
        stmt = select(ModelPrvdParam).where(ModelPrvdParam.prvdId == prvdId).order_by(ModelPrvdParam.prmOdr.asc())
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 查询用户配置的模型参数列表
    @app.post('/sys/model/param/my/list')
    def myModelParamList(request: Request, param: ModelParamEntity):
      userId = self.getUserId(request)
      prvdId = param.prvdId
      modlId = param.modlId
      with session_scope(True) as session:
        query = session.query(ModelParam).where(ModelParam.userId == userId, ModelParam.prvdId == prvdId)
        if (modlId is not None):
          query = query.where(ModelParam.modlId == modlId)
        else:
          query = query.where(ModelParam.modlId.is_(None))
        orms = query.all()
        for orm in orms:
          if (orm.valEcrp == 'Y' and orm.prmVal is not None):
            prmVal = aes_decrypt(orm.prmVal)
            orm.prmVal = replace_with_asterisks(prmVal)
        return self.success(orms)

    # 保存供应商配置
    @app.post('/sys/model/param/prvd/{prvdId}')
    def savePrvdModelParamList(prvdId: str, params: list[ModelParamEntity], request: Request):
      userId = self.getUserId(request)
      modelSetting = ModelSetting(userId=userId, prvdId=prvdId)
      with session_scope() as session:
        oldOrms = session.query(ModelParam).where(ModelParam.userId == userId, ModelParam.prvdId == prvdId, ModelParam.modlId.is_(None)).all()
        oldIdVals = { oldOrm.prmId: oldOrm.prmVal for oldOrm in oldOrms }
        for param in params:
          if (param.prmId is None):
            param.prmId = self.getPk()
          param.userId = userId
          param.prvdId = prvdId
          if (param.reqEcrp == 'Y'):
            if (param.valEcrp == 'N'):
              param.prmVal = aes_encrypt(param.prmVal)
              param.valEcrp = 'Y'
            elif (param.valEcrp == 'Y'): # 需要将数据库的值替换出来
              param.prmVal = oldIdVals.get(param.prmId, None)
        
        session.merge(modelSetting)
        # 先删除数据，再保存数据
        stmt = delete(ModelParam).where(ModelParam.userId == userId, ModelParam.prvdId == prvdId, ModelParam.modlId.is_(None))
        session.execute(stmt)
        orms = [ModelParam().copy_from_dict(param.to_dict()) for param in params]
        session.add_all(orms)
      return self.success()
    
    # 删除供应商配置
    @app.delete('/sys/model/setting/{prvdId}')
    def removeModelSetting(prvdId:str, request:Request):
      userId = self.getUserId(request)
      with session_scope() as session:
        stmt = delete(ModelSetting).where(ModelSetting.userId == userId, ModelSetting.prvdId == prvdId)
        session.execute(stmt)
        stmt = delete(ModelParam).where(ModelParam.userId == userId, ModelParam.prvdId == prvdId)
        session.execute(stmt)
      return self.success()
    
    # 查询模型供应商模型配置
    @app.get('/sys/model/prvd/modl/{modlId}')
    def getPrvdModelModl(modlId:str, request: Request):
      userId = self.getUserId(request)
      with session_scope(True) as session:
        model = session.get(ModelPrvdModl, modlId)
        if (model is None):
          raise BaseBusiException('模型不存在或已被删除')
        if (model.userId != userId):
          raise BaseBusiException('您没有权限查看该模型')
        model = ModelPrvdModlEntity().copy_from_dict(model.to_dict())
        stmt = select(ModelParam).where(ModelParam.modlId == modlId, ModelParam.userId == userId)
        params = session.scalars(stmt).all()
        params = [ModelParamEntity().copy_from_dict(param.to_dict()) for param in params]
      return self.success({'model': model, 'params': params})
    
    # 保存模型供应商模型
    @app.post('/sys/model/prvd/modl/{prvdId}')
    def savePrvdModelModl(prvdId: str, model: ModelPrvdModlEntity, params: list[ModelParamEntity], request: Request):
      userId = self.getUserId(request)
      modelSetting = ModelSetting(userId=userId, prvdId=prvdId)
      modlId = model.modlId
      model.prvdId = prvdId
      model.userId = userId
      model.builtIn = 'N'
      with session_scope() as session:
        oldOrms = session.query(ModelParam).where(ModelParam.userId == userId, ModelParam.prvdId == prvdId, ModelParam.modlId == modlId).all()
        oldIdVals = { oldOrm.prmId: oldOrm.prmVal for oldOrm in oldOrms }
        if (modlId is None): # 新增
          modlId = self.getPk()
          model.modlId = modlId
        for param in params:
          # if (param.prmId is None):
          param.prmId = self.getPk()
          if (param.modlId is None):
            param.modlId = modlId
          param.userId = userId
          param.prvdId = prvdId
          if (param.reqEcrp == 'Y'):
            if (param.valEcrp == 'N'):
              param.prmVal = aes_encrypt(param.prmVal)
              param.valEcrp = 'Y'
            elif (param.valEcrp == 'Y'): # 需要将数据库的值替换出来
              param.prmVal = oldIdVals.get(param.prmId, None)
        session.merge(modelSetting)
        session.merge(ModelPrvdModl().copy_from_dict(model.to_dict()))
        # 先删除数据，再保存数据
        stmt = delete(ModelParam).where(ModelParam.userId == userId, ModelParam.prvdId == prvdId, ModelParam.modlId == modlId)
        session.execute(stmt)
        orms = [ModelParam().copy_from_dict(param.to_dict()) for param in params]
        session.add_all(orms)
      return self.success()

    # 移除用户创建的模型
    @app.delete('/sys/model/prvd/modl/{modlId}')
    def removePrvdModelModl(modlId: str):
      with session_scope() as session:
        stmt = delete(ModelPrvdModl).where(ModelPrvdModl.modlId == modlId)
        session.execute(stmt)
        stmt = delete(ModelParam).where(ModelParam.modlId == modlId)
        session.execute(stmt)
      return self.success()
    
    # 查询用户能使用的模型列表
    @app.get('/sys/model/my/list')
    def getMyModelList(request: Request):
      userId = self.getUserId(request)
      with session_scope(True) as session:
        settings = session.query(ModelSetting).where(ModelSetting.userId.in_([userId, DEFAULT_SYSTEM_USER_ID])).add_columns(ModelSetting.prvdId).all()
        prvdIds = [setting.prvdId for setting in settings] # 能够使用的供应商id
        prvds = session.query(ModelPrvdInfo).where(ModelPrvdInfo.prvdId.in_(prvdIds)).all()
        models = session.query(ModelPrvdModl).where(ModelPrvdModl.prvdId.in_(prvdIds), or_(ModelPrvdModl.userId == userId, ModelPrvdModl.userId.is_(None))).all()
        items = [{
          'value': prvd.prvdId, 'label': prvd.prvdNm, 'icon': prvd.prvdIcon, 'disabled': False,
          'children': [{
            'value': model.modlId, 'label': model.modlNm, 'icon': model.modlIcon, 'type': model.modlTyp, 'disabled': False
          } for model in [m for m in models if m.prvdId == prvd.prvdId]] } for prvd in prvds]
      return self.success(items)
    
    # 获取用户系统参数信息
    @app.get('/sys/setting/user/{prmCd}')
    def settingParam(prmCd: str, request: Request):
      userId = self.getUserId(request)
      with session_scope(True) as session:
        orm = session.query(SettingParam).where(SettingParam.userId == userId, SettingParam.prmCd == prmCd).first() # 理论上来讲只会有一条或者没有
        if orm is None:
          raise BaseBusiException(f'用户配置参数{prmCd}不存在')
        settingParam = SettingParamEntity().copy_from_dict(orm.to_dict())
        prmId = settingParam.prmId
        if (settingParam.whthEmrt == 'Y'):
          stmt = select(SettingEmrt).where(SettingEmrt.prmId == prmId).order_by(SettingEmrt.valOdr.asc())
          emrts = []
          for row in session.scalars(stmt):
            emrts.append(SettingEmrtEntity().copy_from_dict(row.to_dict()))
          settingParam.prmEmrts = emrts
      return self.success(settingParam)
    
    # 修改用户系统配置参数的值
    @app.post('/sys/setting/user')
    def settingSave(settingParam: SettingParamEntity, request: Request):
      prmId = settingParam.prmId
      isNew = (prmId is None)
      settingParam.userId = self.getUserId(request)
      with session_scope() as session:
        orm = None
        if (not isNew):
          orm = session.get(SettingParam, prmId)
        if (orm is None):
          settingParam.prmId = self.getPk()
          prmId = settingParam.prmId
          orm = SettingParam().copy_from_dict(vars(settingParam))
        else:
          orm.prmVal = settingParam.prmVal
        session.merge(orm)
        # 处理参数值
        if (orm.whthEmrt == 'Y'):
          stmt = delete(SettingEmrt).where(SettingEmrt.prmId == prmId)
          session.execute(stmt)
          if (settingParam.prmEmrts is None):
            return self.success()
          for emrt in settingParam.prmEmrts:
            emrt['prmId'] = prmId
            emrt['userId'] = settingParam.userId
            orm = SettingEmrt().copy_from_dict(emrt)
            session.add(orm)
      return self.success(settingParam)