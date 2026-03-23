from fastapi import FastAPI, Request
from server.db.DbManager import session_scope
from server.api.BaseApi import BaseApi
from sqlalchemy import select, update
from sqlalchemy.orm import defer
from datetime import datetime
from server.model.form_doc import DocmtToDatasetForm
from server.model.orm_doc import DocsetInfo, DocmtInfo
from server.model.orm_knb import Dataset
from server.model.entity_doc import DocsetInfo as DocsetInfoEntity, DocmtInfo as DocmtInfoEntity
from server.utils.websocketutils import WebsocketManager
from server.core.doc.DocsetService import DocsetService
from server.exception.exception import BaseBusiException

class DocsetInfoApi(BaseApi):
  docsetService = DocsetService()
  def __init__(self, app: FastAPI, manager: WebsocketManager = None):
    BaseApi.__init__(self)

    # 获取单个文档集
    @app.get('/doc/docset/{id}')
    def getDocumentSet(id: str, request: Request):
      userId = self.getUserId(request)
      return self.success(self.docsetService.select_by_set_id_and_user_id(setId=id, userId=userId))
    
    # 修改名称
    @app.put('/doc/docset/name')
    def editDocumentSetName(docsetInfo: DocsetInfoEntity):
      setId = docsetInfo.setId
      with session_scope() as session:
        orm = session.get(DocsetInfo, setId)
        orm.setNm = docsetInfo.setNm
        session.merge(orm)
      return self.success()
    
    # 修改介绍
    @app.put('/doc/docset/desc')
    def editDocumentSetDesc(docsetInfo: DocsetInfoEntity):
      setId = docsetInfo.setId
      with session_scope() as session:
        orm = session.get(DocsetInfo, setId)
        orm.setDesc = docsetInfo.setDesc
        session.merge(orm)
      return self.success()
    
    # 修改权限
    @app.put('/doc/docset/auth/range')
    def editDocumentSetAuthRange(docsetInfo: DocsetInfoEntity):
      setId = docsetInfo.setId
      authRang = docsetInfo.authRang
      with session_scope() as session:
        orm = session.get(DocsetInfo, setId)
        if (orm.authRang == authRang):
          return self.success()
        orm.authRang = authRang
        session.merge(orm)
        # if (authRang == 'prvt' or authRang == 'pblc'): # 需要删除团队信息
        #   session.query(DocsetTeam).filter(DocsetTeam.setId == setId).delete()
      return self.success()

    # 查询文档集列表
    @app.post('/doc/docset/list')
    def documentSetList():
      stmt = select(DocsetInfo).where().order_by(DocsetInfo.crtTm.desc())
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 查询文档集列表
    @app.post('/doc/docset/my/list')
    def documentSetList(request:Request):
      list = []
      with session_scope(True) as session:
        stmt = select(DocsetInfo).where().order_by(DocsetInfo.crtTm.desc())
        for row in session.scalars(stmt):
          entity = DocsetInfoEntity().copy_from_dict(row.to_dict())
          entity.optAuth = 'alter'
          list.append(entity)
      return self.success(list)
    
    # 新增文档集
    @app.post('/doc/docset')
    def addDocumentSet(docsetInfo: DocsetInfoEntity, request: Request):
      # setId='' setNm='123456' setDesc='' setIcon=None crtUser=None authRang=None
      docsetInfo.setId = self.getPk()
      docsetInfo.crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      docsetInfo.crtUser = self.getUserId(request=request)
      if (docsetInfo.authRang is None):
        docsetInfo.authRang = 'prvt'
      orm = DocsetInfo().copy_from_dict(vars(docsetInfo))
      with session_scope() as session:
        session.add(orm)
      return self.success(docsetInfo)
    
    # 修改文档集
    @app.put('/doc/docset')
    def editDocumentSet(docsetInfo:DocsetInfoEntity):
      # setId='' setNm='123456' setDesc='' setIcon=None crtUser=None authRang=None
      setId = docsetInfo.setId
      with session_scope() as session:
        orm = session.get(DocsetInfo, setId)
        orm.setNm = docsetInfo.setNm
        orm.setDesc = docsetInfo.setDesc
        orm.setIcon = docsetInfo.setIcon
        orm.authRang = docsetInfo.authRang
        session.merge(orm)
      return self.success()

    # 删除文档集
    @app.delete('/doc/docset/{id}')
    def removeDocumentSet(id:str):
      # setId='' setNm='123456' setDesc='' setIcon=None crtUser=None authRang=None
      with session_scope() as session:
        orm = session.get(DocsetInfo, id)
        session.delete(orm)
      return self.success()
    
    # 查询文档集中的文档列表
    @app.post('/doc/document/list/{id}')
    def documentList(id: str):
      stmt = select(DocmtInfo).where(DocmtInfo.setId==id).options(defer(DocmtInfo.docCntnt)).order_by(DocmtInfo.crtTm.asc())
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 新增文档
    @app.post('/doc/document')
    def addDocument(docmtInfo: DocmtInfoEntity, request: Request):
      docmtInfo.docId = self.getPk()
      docmtInfo.crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      docmtInfo.updTm = docmtInfo.crtTm
      docmtInfo.crtUser = self.getUserId(request=request)
      docPid = docmtInfo.docPid
      docPath = '/' + docmtInfo.docId
      with session_scope() as session:
        if (docPid is not None):
          porm = session.get(DocmtInfo, docPid)
          if (porm is None):
            raise BaseBusiException('上级文档不存在或被删除')
          docPath = porm.docPath + docPath
        docmtInfo.docPath = docPath
        orm = DocmtInfo().copy_from_dict(vars(docmtInfo))
        session.add(orm)
      return self.success(docmtInfo)
    
    # 修改文档
    @app.put('/doc/document')
    def editDocument(docmtInfo: DocmtInfoEntity):
      docId = docmtInfo.docId
      with session_scope() as session:
        orm = session.get(DocmtInfo, docId)
        orm.docTtl = docmtInfo.docTtl
        session.merge(orm)
      return self.success()

    # 删除文档
    @app.delete('/doc/document/{id}')
    def removeDocument(id:str):
      with session_scope() as session:
        orm = session.get(DocmtInfo, id)
        session.delete(orm)
      return self.success()
    
    # 获取单个文档
    @app.get('/doc/document/{id}')
    def getDocument(id: str, request: Request):
      with session_scope(True) as session:
        orm = session.get(DocmtInfo, id)
      return self.success(orm)
    
    # 修改内容
    @app.put('/doc/document/content')
    def editDocumentContent(docmtInfo: DocmtInfoEntity):
      docId = docmtInfo.docId
      docCntnt = docmtInfo.docCntnt
      with session_scope() as session:
        stmt = update(DocmtInfo).where(DocmtInfo.docId == docId).values(docCntnt=docCntnt, updTm=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        session.execute(stmt)
      return self.success()
    
    # 将文档添加到数据集
    @app.post('/doc/document/to/dataset')
    def documentAddToDataset(form: DocmtToDatasetForm, request: Request):
      self.docsetService.add_to_dataset(reposId=form.reposId, docId=form.docId, userId=self.getUserId(request))
      return self.success()
    
    @app.get('/doc/document/reposid/list/{docId}')
    def documentDatasetList(docId: str):
      with session_scope(True) as session:
        orms = session.query(Dataset).where(Dataset.docId == docId).all()
        idsset = set()
        for orm in orms:
          idsset.add(orm.reposId)
        return self.success(list(idsset))