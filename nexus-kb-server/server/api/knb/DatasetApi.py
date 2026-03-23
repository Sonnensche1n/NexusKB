from typing import List
from fastapi import FastAPI, File, UploadFile, Form, Request, Body
from server.db.DbManager import session_scope
from server.api.BaseApi import BaseApi
from sqlalchemy import select, delete, update
from server.model.orm_knb import Dataset, DatasetChunk, DatasetPrecis, DatasetCtlg, DatasetTriplet, DatasetIndexError
from server.model.entity_base import PageBase
from server.model.entity_knb import Dataset as DatasetEntity, DatasetChunk as DatasetChunkEntity, DatasetPrecis as DatasetPrecisEntity, DatasetCtlg as DatasetCtlgEntity, DatasetTriplet as DatasetTripletEntity
from config.common import DATASET_UPLOAD_FILE_DIR
from datetime import datetime
from server.utils.websocketutils import WebsocketManager
from server.core.knb.DatasetService import DatasetService
from server.exception.exception import BaseBusiException
from server.utils.httputils import get_webpage_title

class DatasetApi(BaseApi):
  datasetService = DatasetService()
  def __init__(self, app: FastAPI, manager: WebsocketManager):
    BaseApi.__init__(self)
    
    # 查询数据集列表
    @app.post('/knb/dataset/list')
    def datasetList(dataset: DatasetEntity):
      reposId = dataset.reposId
      stmt = select(Dataset).where(Dataset.reposId == reposId).order_by(Dataset.crtTm.desc())
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    @app.post('/knb/dataset/page')
    def datasetPage(dataset: DatasetEntity, pageBase: PageBase):
      reposId = dataset.reposId
      dtsetNm = dataset.dtsetNm
      ctlgId = dataset.ctlgId
      hasCtlgId = ctlgId is not None and ctlgId != ''
      if (dtsetNm is None):
        dtsetNm = ''
      list = []
      with session_scope(True) as session:
        query = session.query(Dataset).where(Dataset.reposId == reposId, Dataset.dtsetNm.ilike(f'%{dtsetNm}%'))
        if (hasCtlgId):
          query = query.where(Dataset.ctlgId == ctlgId)
        total = query.count()
        stmt = select(Dataset).where(Dataset.reposId == reposId, Dataset.dtsetNm.ilike(f'%{dtsetNm}%'))
        if (hasCtlgId):
          stmt = stmt.where(Dataset.ctlgId == ctlgId)
        orderName = Dataset.crtTm if pageBase.orderName == '' else getattr(Dataset, pageBase.orderName)
        orderValue = orderName.asc() if pageBase.orderValue.startswith('asc') else orderName.desc()
        stmt = stmt.offset(pageBase.get_offset()).limit(pageBase.pageSize).order_by(orderValue)

        for row in session.scalars(stmt):
          list.append(row)
      return self.sucess_page(data=list, total=total, size=pageBase.pageSize, page=pageBase.pageNum)
    
    # 导入文档数据集
    @app.post('/knb/dataset/upload/document')
    async def uploadDocument(request: Request, file: UploadFile = File(...), reposId: str = Form(...), ctlgId: str = Form(None)):
      userId = self.getUserId(request)
      # 将文件保存到本地再存储到数据集表中
      dtsetId = self.getPk()
      filename = file.filename
      fileSize = file.size # 单位为字节
      # 获取文件扩展名（类型）
      fileExtension = filename.split('.')[-1]
      if (fileExtension != ''):
        fileExtension = fileExtension.lower()
      fileBaseName = filename[:filename.rfind('.')] if '.' in filename else filename
      filePath = DATASET_UPLOAD_FILE_DIR + '/' + dtsetId + '.' + fileExtension

      # 保存到数据库
      dataset = Dataset(
        dtsetId = dtsetId,
        reposId = reposId,
        ctlgId = ctlgId,
        dtsetTyp = 'text', # 暂时默认只支持文本
        dtsetNm = fileBaseName,
        idxSts = 'new', # 索引状态：new 新建, order 排队中, index 索引中, ready 已就绪, error 索引失败
        prcsSts = 'nobd', # 摘要状态：nobd 不构建，new 新建, order 排队中, index 索引中, ready 已就绪, error 索引失败
        qaSts = 'nobd', # QA状态：nobd 不构建，new 新建, order 排队中, index 索引中, ready 已就绪, error 索引失败
        tpltSts = 'nobd', # 三元组状态：nobd 不构建，new 新建, order 排队中, index 索引中, ready 已就绪, error 索引失败
        enbSts = 'une', # enb 已启用，une 未启用
        fileNm = filename,
        fileTyp = fileExtension,
        filePath = filePath,
        crtTm = datetime.now(),
        crtUser = userId
      )
      with session_scope() as session:
        session.add(dataset)
      # 将文件内容保存到本地
      with open(filePath, 'wb') as buffer:
        contents = await file.read()
        buffer.write(contents)
      return self.success(dataset)
    
    # 导入网页链接数据集
    @app.post('/knb/dataset/upload/link')
    def uploadLink(request: Request, links: list[dict] = Body(...), reposId: str = Body(...), ctlgId: str = Body(None)):
      userId = self.getUserId(request)
      if (links is None or len(links) == 0):
        raise BaseBusiException('链接列表不能为空')
      datasets = []
      for link in links:
        dtsetId = self.getPk()
        url = link.get('url', None)
        if (url is None):
          continue
        title = link.get('title', url)
        dataset = Dataset(
          dtsetId = dtsetId,
          reposId = reposId,
          ctlgId = ctlgId,
          dtsetTyp = 'text', # 暂时默认只支持文本
          dtsetNm = title,
          idxSts = 'new',
          prcsSts = 'nobd',
          qaSts = 'nobd',
          tpltSts = 'nobd',
          enbSts = 'enb', # enb 已启用，une 未启用
          fileNm = title,
          fileTyp = 'link',
          filePath = url, # 如果文件类型是 link 则 filePath 存储的是 url 地址
          crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
          crtUser = userId
        )
        datasets.append(dataset)
      if (len(datasets) > 0):
        with session_scope() as session:
          session.bulk_save_objects(datasets)
      return self.success()
    
    # 获取连接标题
    @app.post('/knb/dataset/links/title')
    def getLinksTitle(links: list[str]):
      titles = {}
      for link in links:
        title = get_webpage_title(link)
        if (title is not None):
          titles[link] = title
        else:
          titles[link] = link
      return self.success(titles)

    # 修改数据集启用状态
    @app.put('/knb/dataset/enable/status')
    def editDatasetEnableStatus(dataset:DatasetEntity):
      dtsetId = dataset.dtsetId
      with session_scope() as session:
        orm = session.get(Dataset, dtsetId)
        orm.enbSts = dataset.enbSts
        session.merge(orm)
      return self.success()
    
     # 修改数据集其他索引构建状态
    @app.put('/knb/dataset/build/status')
    def editDatasetEnableStatus(form: dict):
      dtsetId = form.get('dtsetId', None)
      if (dtsetId is None or dtsetId == ''):
        raise BaseBusiException('数据集ID不能为空')
      with session_scope() as session:
        orm = session.get(Dataset, dtsetId)
        orm_dic = orm.to_dict()
        orm_dic[form.get('buildKey')] = form.get('buildValue')
        orm.copy_from_dict(orm_dic)
        session.merge(orm)
      return self.success()
    
    # 分页查询数据集分段的内容
    @app.post('/knb/dataset/chunk/page')
    def datasetChunkPage(datasetChunk: DatasetChunkEntity, pageBase: PageBase):
      dtsetId = datasetChunk.dtsetId
      chkCntnt = datasetChunk.chkCntnt
      list = []
      with session_scope(True) as session:
        query = session.query(DatasetChunk).where(DatasetChunk.dtsetId == dtsetId)
        stmt = select(DatasetChunk).where(DatasetChunk.dtsetId == dtsetId)
        if (chkCntnt is not None and len(chkCntnt) != 0):
          query = query.where(DatasetChunk.chkCntnt.ilike(f'%{chkCntnt}%'))
          stmt = stmt.where(DatasetChunk.chkCntnt.ilike(f'%{chkCntnt}%'))
        total = query.count()
        stmt = stmt.offset(pageBase.get_offset()).limit(pageBase.pageSize).order_by(DatasetChunk.chkSeq.asc())
        for row in session.scalars(stmt):
          list.append(row)
      return self.sucess_page(data=list, total=total, size=pageBase.pageSize, page=pageBase.pageNum)
    
    # 修改分段内容
    @app.put('/knb/dataset/chunk/content')
    def editDatasetChunkContent(datasetChunk: DatasetChunkEntity):
      self.datasetService.modifyChunkContent(datasetChunk=datasetChunk)
      # 除了修改数据库还需要修改向量库
      return self.success()
    
    # 删除分段
    @app.delete('/knb/dataset/chunk/{chkId}')
    def repositoryRemoveChunk(chkId: str):
      self.datasetService.removeChunkById(chkId)
      return self.success()
    
    # 修改数据集基本信息 仅修改中文名称与所在目录
    @app.put('/knb/dataset')
    def editDataset(dataset:DatasetEntity):
      dtsetId = dataset.dtsetId
      with session_scope() as session:
        orm = session.get(Dataset, dtsetId)
        orm.dtsetNm = dataset.dtsetNm
        orm.ctlgId = dataset.ctlgId
        session.merge(orm)
      return self.success()

    # 删除知识库 需要删除对应的索引库
    @app.delete('/knb/dataset/{id}')
    def removeDataset(id:str):
      self.datasetService.removeDatasetById(id)
      return self.success()

    # 重建数据集索引库
    @app.post('/knb/dataset/reindex/{id}')
    def reindexDataset(id:str, types:list[str] = Body(...)):
      self.datasetService.reindexDatasetByIdAndTypes(id, types)
      return self.success()
    
    # 分页查询数据集摘要的内容
    @app.post('/knb/dataset/precis/page')
    def datasetPrecisPage(datasetPrecis: DatasetPrecisEntity, pageBase: PageBase):
      dtsetId = datasetPrecis.dtsetId
      prcsCntnt = datasetPrecis.prcsCntnt
      list = []
      with session_scope(True) as session:
        query = session.query(DatasetPrecis).where(DatasetPrecis.dtsetId == dtsetId)
        stmt = select(DatasetPrecis).where(DatasetPrecis.dtsetId == dtsetId)
        if (prcsCntnt is not None and len(prcsCntnt) != 0):
          query = query.where(DatasetPrecis.prcsCntnt.ilike(f'%{prcsCntnt}%'))
          stmt = stmt.where(DatasetPrecis.prcsCntnt.ilike(f'%{prcsCntnt}%'))
        total = query.count()
        stmt = stmt.offset(pageBase.get_offset()).limit(pageBase.pageSize).order_by(DatasetPrecis.prcsSeq.asc())
        for row in session.scalars(stmt):
          list.append(row)
      return self.sucess_page(data=list, total=total, size=pageBase.pageSize, page=pageBase.pageNum)
    
    # 新增摘要
    @app.post('/knb/dataset/precis')
    def addDatasetPrecis(datasetPrecis: DatasetPrecisEntity):
      return self.success(self.datasetService.addPrecis(datasetPrecis=datasetPrecis))

    # 修改摘要
    @app.put('/knb/dataset/precis/content')
    def editDatasetPrecisContent(datasetPrecis: DatasetPrecisEntity):
      self.datasetService.modifyPrecisContent(datasetPrecis=datasetPrecis)
      # 除了修改数据库还需要修改向量库
      return self.success()
    
    # 删除摘要
    @app.delete('/knb/dataset/precis/{prcsId}')
    def repositoryRemovePrecis(prcsId: str):
      self.datasetService.removePrecisById(prcsId)
      return self.success()
    
    # 查询目录列表
    @app.post('/knb/dataset/catalog/list')
    def catalogList(catasetCtlg: DatasetCtlgEntity):
      reposId = catasetCtlg.reposId
      stmt = select(DatasetCtlg).where(DatasetCtlg.reposId == reposId).order_by(DatasetCtlg.ctlgOdr.asc())
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)

    # 新增目录
    @app.post('/knb/dataset/catalog')
    def addCatalog(catasetCtlg: DatasetCtlgEntity, request: Request):
      catasetCtlg.ctlgId = self.getPk()
      with session_scope() as session:
        ctlgPid = catasetCtlg.ctlgPid
        ctlgPath = '/' + catasetCtlg.ctlgId
        if (ctlgPid is not None):
          porm = session.get(DatasetCtlg, ctlgPid)
          if (porm is None):
            raise BaseBusiException('上级目录不存在或被删除')
          count = session.query(DatasetCtlg).filter(DatasetCtlg.ctlgPid == ctlgPid).count() # 设置默认排序
          ctlgPath = porm.ctlgPath + ctlgPath
          catasetCtlg.ctlgOdr = count
        catasetCtlg.ctlgPath = ctlgPath
        orm = DatasetCtlg().copy_from_dict(vars(catasetCtlg))
        session.add(orm)
      return self.success(catasetCtlg)
    
    # 修改目录
    @app.put('/knb/dataset/catalog')
    def editCatalog(catasetCtlg: DatasetCtlgEntity):
      ctlgId = catasetCtlg.ctlgId
      with session_scope() as session:
        orm = session.get(DatasetCtlg, ctlgId)
        if (orm is None):
          raise BaseBusiException('目录不存在或被删除')
        orm.copy_from_dict(vars(catasetCtlg))
        session.merge(orm)
      return self.success()

    # 修改数据集目录顺序
    @app.put('/knb/dataset/catalog/sort')
    def editCatalogOrder(list: List[DatasetCtlgEntity]):
      with session_scope() as session:
        for entity in list:
          ctlgId = entity.ctlgId
          ctlgOdr = entity.ctlgOdr
          stmt = update(DatasetCtlg).where(DatasetCtlg.ctlgId == ctlgId).values(ctlgOdr=ctlgOdr)
          session.execute(stmt)
      return self.success()

    # 删除目录
    @app.delete('/knb/dataset/catalog/{id}')
    def removeCatalog(id):
      with session_scope() as session:
        orm = session.get(DatasetCtlg, id)
        if (orm is None):
          return self.success()
        ctlgPath = orm.ctlgPath
        ctlgList = session.query(DatasetCtlg).filter(DatasetCtlg.ctlgPath.like(f'{ctlgPath}%')).add_columns(DatasetCtlg.ctlgId).all()
        ctlgIdList = [ctlg.ctlgId for ctlg in ctlgList]
        # 修改目录下的数据集对应的目录为空
        session.query(Dataset).filter(Dataset.ctlgId.in_(ctlgIdList)).update({Dataset.ctlgId: None}, synchronize_session=False)
        # 删除目录
        stmt = delete(DatasetCtlg).where(DatasetCtlg.ctlgId.in_(ctlgIdList))
        session.execute(stmt)
      return self.success()
    
    # 分页查询数据集三元组的内容
    @app.post('/knb/dataset/triplet/page')
    def datasetTripletPage(datasetTriplet: DatasetTripletEntity, pageBase: PageBase):
      dtsetId = datasetTriplet.dtsetId
      subject = datasetTriplet.tpltSbjct
      predicate = datasetTriplet.tpltPrdct
      object = datasetTriplet.tpltObjct
      list = []
      with session_scope(True) as session:
        query = session.query(DatasetTriplet).where(DatasetTriplet.dtsetId == dtsetId)
        stmt = select(DatasetTriplet).where(DatasetTriplet.dtsetId == dtsetId)
        if (subject is not None and subject != ''):
          query = query.where(DatasetTriplet.tpltSbjct.ilike(f'%{subject}%'))
          stmt = stmt.where(DatasetTriplet.tpltSbjct.ilike(f'%{subject}%'))
        if (predicate is not None and predicate != ''):
          query = query.where(DatasetTriplet.tpltPrdct.ilike(f'%{predicate}%'))
          stmt = stmt.where(DatasetTriplet.tpltPrdct.ilike(f'%{predicate}%'))
        if (object is not None and object != ''):
          query = query.where(DatasetTriplet.tpltObjct.ilike(f'%{object}%'))
          stmt = stmt.where(DatasetTriplet.tpltObjct.ilike(f'%{object}%'))
        total = query.count()
        stmt = stmt.offset(pageBase.get_offset()).limit(pageBase.pageSize).order_by(DatasetTriplet.tpltSeq.asc())
        for row in session.scalars(stmt):
          list.append(row)
      return self.sucess_page(data=list, total=total, size=pageBase.pageSize, page=pageBase.pageNum)

    @app.get('/knb/dataset/triplet/{dtsetId}')    
    def datasetTripletAll(dtsetId: str):
      with session_scope(True) as session:
        list = session.query(DatasetTriplet).filter(DatasetTriplet.dtsetId == dtsetId).all()
        return self.success(list)

    # 新增三元组
    @app.post('/knb/dataset/triplet')
    def addDatasetTriplet(datasetTriplet: DatasetTripletEntity):
      return self.success(self.datasetService.addTriplet(datasetTriplet=datasetTriplet))
    
    # 修改摘要
    @app.put('/knb/dataset/triplet')
    def editDatasetTriplet(datasetTriplet: DatasetTripletEntity):
      self.datasetService.modifyTriplet(datasetTriplet=datasetTriplet)
      # 除了修改数据库还需要修改向量库
      return self.success()

    # 删除三元组
    @app.delete('/knb/dataset/triplet/{tpltId}')
    def removeDatasetTriplet(tpltId: str):
      self.datasetService.removeTripletById(tpltId)
      return self.success()
    
    # 获取错误信息
    @app.get('/knb/dataset/index/error/{dtsetId}/{idxTyp}')
    def datasetIndexError(dtsetId: str, idxTyp: str):
      with session_scope(True) as session:
        orm = session.query(DatasetIndexError).filter(DatasetIndexError.dtsetId == dtsetId, DatasetIndexError.idxTyp == idxTyp).one_or_none()
        return self.success(orm)