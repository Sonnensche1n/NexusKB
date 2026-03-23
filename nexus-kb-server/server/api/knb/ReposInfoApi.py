from fastapi import FastAPI, Request, Body
from server.db.DbManager import session_scope
from server.api.BaseApi import BaseApi
from sqlalchemy import select, delete
from datetime import datetime
from server.model.orm_knb import ReposInfo, ChatInfo, ChatMesg, ReposQuest, ReposSetting
from server.model.entity_base import PageBase
from server.model.entity_knb import ReposInfo as ReposInfoEntity, ReposQuest as ReposQuestEntity, ReposSetting as ReposSettingEntity
from server.utils.websocketutils import WebsocketManager
from server.core.knb.ReposService import ReposService

class ReposInfoApi(BaseApi):
  reposService = ReposService()
  def __init__(self, app: FastAPI, manager: WebsocketManager):
    BaseApi.__init__(self)

    # 获取单个知识库
    @app.get('/knb/repository/{id}')
    def getRepository(id: str, request: Request):
      userId = self.getUserId(request)
      return self.success(self.reposService.select_by_repos_id_and_user_id(reposId=id, userId=userId))
    
    # 修改名称
    @app.put('/knb/repository/name')
    def editRepositoryName(reposInfo: ReposInfoEntity):
      reposId = reposInfo.reposId
      with session_scope() as session:
        orm = session.get(ReposInfo, reposId)
        orm.reposNm = reposInfo.reposNm
        session.merge(orm)
      return self.success()
    
    # 修改介绍
    @app.put('/knb/repository/desc')
    def editRepositoryDesc(reposInfo: ReposInfoEntity):
      reposId = reposInfo.reposId
      with session_scope() as session:
        orm = session.get(ReposInfo, reposId)
        orm.reposDesc = reposInfo.reposDesc
        session.merge(orm)
      return self.success()
    
    # 修改权限
    @app.put('/knb/repository/auth/range')
    def editRepositoryAuthRange(reposInfo: ReposInfoEntity):
      reposId = reposInfo.reposId
      authRang = reposInfo.authRang
      with session_scope() as session:
        orm = session.get(ReposInfo, reposId)
        if (orm.authRang == authRang):
          return self.success()
        orm.authRang = authRang
        session.merge(orm)
        # if (authRang == 'prvt' or authRang == 'pblc'): # 需要删除团队信息
        #   session.query(ReposTeam).filter(ReposTeam.reposId == reposId).delete()
      return self.success()

    # 查询知识库列表
    @app.post('/knb/repository/list')
    def repositoryList():
      stmt = select(ReposInfo).where().order_by(ReposInfo.crtTm.desc())
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 查询知识库列表
    @app.post('/knb/repository/my/list')
    def repositoryList(request:Request):
      stmt = select(ReposInfo).where().order_by(ReposInfo.crtTm.desc())
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          entity = ReposInfoEntity().copy_from_dict(row.to_dict())
          entity.optAuth = 'alter'
          list.append(entity)
      return self.success(list)
    
    # 新增知识库
    @app.post('/knb/repository')
    def addRepository(reposInfo: ReposInfoEntity, request: Request):
      # reposId='' reposNm='123456' reposDesc='' reposIcon=None crtUser=None authRang=None
      reposInfo.reposId = self.getPk()
      reposInfo.crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      reposInfo.crtUser = self.getUserId(request=request)
      if (reposInfo.reposTyp is None):
        reposInfo.reposTyp = 'nml' # 知识库类型：nml 通用知识库，tbl 表格知识库
      if (reposInfo.authRang is None):
        reposInfo.authRang = 'prvt'
      orm = ReposInfo().copy_from_dict(reposInfo.to_dict())
      with session_scope() as session:
        session.add(orm)
      return self.success(reposInfo)
    
    # 修改知识库 todo 需要同时删除索引库
    @app.put('/knb/repository')
    def editRepository(reposInfo:ReposInfoEntity):
      # reposId='' reposNm='123456' reposDesc='' reposIcon=None crtUser=None authRang=None
      reposId = reposInfo.reposId
      with session_scope() as session:
        orm = session.get(ReposInfo, reposId)
        orm.reposNm = reposInfo.reposNm
        orm.reposDesc = reposInfo.reposDesc
        orm.reposIcon = reposInfo.reposIcon
        orm.authRang = reposInfo.authRang
        orm.vecModlId = reposInfo.vecModlId # 嵌入模型
        session.merge(orm)
      return self.success()

    # 删除知识库
    @app.delete('/knb/repository/{id}')
    def removeRepository(id:str):
      # reposId='' reposNm='123456' reposDesc='' reposIcon=None crtUser=None authRang=None
      with session_scope() as session:
        orm = session.get(ReposInfo, id)
        session.delete(orm)
      return self.success()
    
    # 删除对话
    @app.delete('/knb/repository/chat/clear/{id}')
    def clearRepositoryChat(id):
      with session_scope() as session:
        stmt = delete(ChatInfo).where(ChatInfo.reposId == id)
        session.execute(stmt)
        stmt = delete(ChatMesg).where(ChatMesg.reposId == id)
        session.execute(stmt)
      return self.success()
  
    # 查询知识库QA列表
    @app.post('/knb/repository/quest/list')
    def repositoryQuestList(reposQuest: ReposQuestEntity):
      reposId = reposQuest.reposId
      stmt = select(ReposQuest).where(ReposQuest.reposId == reposId)
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 新增QA
    @app.post('/knb/repository/quest')
    def addRepositoryQuest(reposQuest: ReposQuestEntity):
      return self.success(self.reposService.add_repos_quest(reposQuest))

    # 修改QA
    @app.put('/knb/repository/quest')
    def editRepositoryQuest(reposQuest: ReposQuestEntity):
      self.reposService.edit_repos_quest(reposQuest)
      return self.success()

    # 移除QA
    @app.delete('/knb/repository/quest/{qstId}')
    def repositoryRemoveQuest(qstId: str):
      self.reposService.remove_repos_quest(qstId)
      return self.success()
    
    @app.post('/knb/repository/guess/list')
    def repositoryGuessQuestList(reposQuest: ReposQuestEntity):
      reposId = reposQuest.reposId
      qstQuest = reposQuest.qstQuest
      if (qstQuest is None):
        qstQuest = ''
      stmt = select(ReposQuest).where(ReposQuest.reposId == reposId, ReposQuest.qstQuest.ilike(f'%{qstQuest}%')).limit(5)
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    @app.post('/knb/repository/quest/page')
    def repositoryGuessQuestPage(reposQuest: ReposQuestEntity, pageBase: PageBase):
      reposId = reposQuest.reposId
      dtsetId = reposQuest.dtsetId
      qstQuest = reposQuest.qstQuest
      if (qstQuest is None):
        qstQuest = ''
      list = []
      with session_scope(True) as session:
        query = session.query(ReposQuest).where(ReposQuest.reposId == reposId, ReposQuest.qstQuest.ilike(f'%{qstQuest}%'))
        stmt = select(ReposQuest).where(ReposQuest.reposId == reposId, ReposQuest.qstQuest.ilike(f'%{qstQuest}%'))
        if (dtsetId is not None and len(dtsetId) > 0):
          query = query.filter(ReposQuest.dtsetId == dtsetId)
          stmt = stmt.filter(ReposQuest.dtsetId == dtsetId)
        total = query.count()
        stmt = stmt.offset(pageBase.get_offset()).limit(pageBase.pageSize)
        for row in session.scalars(stmt):
          list.append(row)
      return self.sucess_page(data=list, total=total, size=pageBase.pageSize, page=pageBase.pageNum)
    

    # 查询知识库设置
    @app.get('/knb/repository/setting/{reposId}')
    def getReposSetting(reposId:str):
      return self.success(self.reposService.get_repos_setting(reposId))
    
    # 新增或修改知识库设置
    @app.post('/knb/repository/setting')
    def addOrEditRepositorySetting(setting:ReposSettingEntity):
      with session_scope() as session:
        orm = ReposSetting().copy_from_dict(setting.to_dict())
        session.merge(orm)
      return self.success()