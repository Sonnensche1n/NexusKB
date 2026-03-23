import json
import uuid
from langchain_core.documents import Document
from server.db.DbManager import session_scope
from sqlalchemy import delete
from server.model.orm_knb import Dataset, DatasetChunk, ReposQuest, DatasetPrecis, DatasetTriplet
from server.model.entity_knb import DatasetChunk as DatasetChunkEntity, DatasetPrecis as DatasetPrecisEntity, DatasetTriplet as DatasetTripletEntity
from server.core.tools.repos_vector_db import vector_get, vector_update_document, vector_delete, vector_add_texts
from server.core.tools.dataset_to_metadata import precis_to_metadata, triplet_to_metadata

class DatasetService():
  # 删除数据集相关内容：分段，摘要，QA，索引等
  def removeDatasetExtendsByIdAndTypes(self, reposId: str, dtsetId: str, session, types: list = ['index', 'precis', 'qanswer', 'triplet']):
    ids = []
    if ('index' in types):
      chunks = session.query(DatasetChunk).filter(DatasetChunk.dtsetId == dtsetId).values(DatasetChunk.chkId)
      ids.extend([chunk.chkId for chunk in chunks])
      # 删除数据集分片
      session.execute(delete(DatasetChunk).where(DatasetChunk.dtsetId == dtsetId))
    if ('precis' in types):
      precies = session.query(DatasetPrecis).filter(DatasetPrecis.dtsetId == dtsetId, DatasetPrecis.prcsSrc == 'ai').values(DatasetPrecis.prcsId)
      ids.extend([precis.prcsId for precis in precies])
      # 删除摘要
      session.execute(delete(DatasetPrecis).where(DatasetPrecis.dtsetId == dtsetId, DatasetPrecis.prcsSrc == 'ai'))
    if ('qanswer' in types):
      quests = session.query(ReposQuest).filter(ReposQuest.dtsetId == dtsetId, ReposQuest.qstSrc == 'ai').values(ReposQuest.qstId)
      ids.extend([quest.qstId for quest in quests])
      # 删除Q&A
      session.execute(delete(ReposQuest).where(ReposQuest.dtsetId == dtsetId, ReposQuest.qstSrc == 'ai'))
    if ('triplet' in types):
      triplets = session.query(DatasetTriplet).filter(DatasetTriplet.dtsetId == dtsetId, DatasetTriplet.tpltSrc == 'ai').values(DatasetTriplet.tpltId)
      ids.extend([triplet.tpltId for triplet in triplets])
      # 删除三元组
      session.execute(delete(DatasetTriplet).where(DatasetTriplet.dtsetId == dtsetId, DatasetTriplet.tpltSrc == 'ai'))
    
    # 删除向量库的内容
    if (len(ids) > 0):
      vector_delete(reposId=reposId, ids=ids)

  def removeDatasetById(self, dtsetId: str):
    with session_scope() as session:
      orm = session.get(Dataset, dtsetId)
      if (orm is None):
        return
      reposId = orm.reposId
      # 删除数据集
      session.delete(orm)
      if (orm.idxSts == 'new'):
        return
      self.removeDatasetExtendsByIdAndTypes(reposId=reposId, dtsetId=dtsetId, session=session)
      # todo 还需要删除文件，待定

  # types: [ 'index', 'precis', 'qanswer', 'triplet' ]
  def reindexDatasetByIdAndTypes(self, dtsetId: str, types: list):
    with session_scope() as session:
      orm = session.get(Dataset, dtsetId)
      if (orm is None):
        return
      reposId = orm.reposId
      if ('index' in types):
        orm.idxSts = 'new'
      if ('precis' in types):
        orm.prcsSts = 'new'
      if ('qanswer' in types):
        orm.qaSts = 'new'
      if ('triplet' in types):
        orm.tpltSts = 'new'

      session.merge(orm) # 重置状态
      self.removeDatasetExtendsByIdAndTypes(reposId=reposId, dtsetId=dtsetId, types=types, session=session)

  def get_chunk_vector_text(self, content:str, assist: str = None):
    if (assist is None or len(assist) == 0):
      return content
    d = {
      'content': content,
      'assist': assist
    }
    return json.dumps(d, ensure_ascii=False)
  # 修改数据集分片内容 ，return部分暂时都不处理
  def modifyChunkContent(self, datasetChunk: DatasetChunkEntity):
    chkId = datasetChunk.chkId
    chkCntnt = datasetChunk.chkCntnt
    chkAsst = datasetChunk.chkAsst
    with session_scope() as session:
      orm = session.get(DatasetChunk, chkId)
      if (orm is None):
        return
      if (orm.chkCntnt == chkCntnt and orm.chkAsst == chkAsst):
        return
      reposId = orm.reposId
      result = vector_get(reposId=reposId, ids=chkId, limit=1) # { ids: [], metadatas: [], documents: [] }
      isNew = len(result) == 0
      if (isNew):
        return
      else:
        text = self.get_chunk_vector_text(content=chkCntnt, assist=chkAsst)
        vector_update_document(reposId=reposId, document_id=chkId, document=Document(page_content=text, metadata=result['metadatas'][0])) # 更新到向量库
        # 更新到数据库
        orm.chkCntnt = chkCntnt
        orm.chkAsst = chkAsst
        session.merge(orm)

  def removeChunkById(self, chkId: str):
    with session_scope() as session:
      orm = session.get(DatasetChunk, chkId)
      if (orm is None):
        return
      vector_delete(reposId=orm.reposId, ids=[chkId])
      # 删除数据库
      session.delete(orm)
  
  def addPrecis(self, datasetPrecis: DatasetPrecisEntity):
    datasetPrecis.prcsId = str(uuid.uuid4()).replace('-', '')
    with session_scope() as session:
      session.add(DatasetPrecis().copy_from_dict(vars(datasetPrecis)))
      dtsetId = datasetPrecis.dtsetId
      if (dtsetId is not None):
        dataset = session.get(Dataset, dtsetId)
      # 添加到向量数据库
      text = datasetPrecis.prcsCntnt
      metadata = precis_to_metadata(precis=datasetPrecis, dataset=dataset)
      vector_add_texts(reposId=datasetPrecis.reposId, texts=[text], metadatas=[metadata], ids=[datasetPrecis.prcsId])
    return datasetPrecis
  # 修改数据集摘要内容 ，return部分暂时都不处理
  def modifyPrecisContent(self, datasetPrecis: DatasetPrecisEntity):
    prcsId = datasetPrecis.prcsId
    prcsCntnt = datasetPrecis.prcsCntnt

    with session_scope() as session:
      orm = session.get(DatasetPrecis, prcsId)
      if (orm is None):
        return
      if (orm.prcsCntnt == prcsCntnt):
        return
      reposId = orm.reposId
      result = vector_get(reposId=reposId, ids=prcsId, limit=1) # { ids: [], metadatas: [], documents: [] }
      isNew = len(result) == 0
      if (isNew):
        return
      else:
        text = prcsCntnt
        vector_update_document(reposId=reposId, document_id=prcsId, document=Document(page_content=text, metadata=result['metadatas'][0])) # 更新到向量库
        # 更新到数据库
        orm.prcsCntnt = prcsCntnt
        session.merge(orm)

  def removePrecisById(self, prcsId: str):
    with session_scope() as session:
      orm = session.get(DatasetPrecis, prcsId)
      if (orm is None):
        return
      vector_delete(reposId=orm.reposId, ids=[prcsId])
      # 删除数据库
      session.delete(orm)


  def get_triplet_vector_text(self, subject:str, predicate:str, object:str):
    return f'({subject},{predicate},{object})'

  def addTriplet(self, datasetTriplet: DatasetTripletEntity):
    datasetTriplet.tpltId = str(uuid.uuid4()).replace('-', '')
    with session_scope() as session:
      session.add(DatasetTriplet().copy_from_dict(vars(datasetTriplet)))
      dtsetId = datasetTriplet.dtsetId
      if (dtsetId is not None):
        dataset = session.get(Dataset, dtsetId)
      # 添加到向量数据库
      text = self.get_triplet_vector_text(subject=datasetTriplet.tpltSbjct, predicate=datasetTriplet.tpltPrdct, object=datasetTriplet.tpltObjct)
      metadata = triplet_to_metadata(triplet=datasetTriplet, dataset=dataset)
      vector_add_texts(reposId=datasetTriplet.reposId, texts=[text], metadatas=[metadata], ids=[datasetTriplet.tpltId])
    return datasetTriplet
  
  # 修改数据集三元组 ，return部分暂时都不处理
  def modifyTriplet(self, datasetTriplet: DatasetTripletEntity):
    tpltId = datasetTriplet.tpltId
    with session_scope() as session:
      orm = session.get(DatasetTriplet, tpltId)
      if (orm is None):
        return
      reposId = orm.reposId
      result = vector_get(reposId=reposId, ids=tpltId, limit=1) # { ids: [], metadatas: [], documents: [] }
      isNew = len(result) == 0
      if (isNew):
        return
      else:
        text = self.get_triplet_vector_text(subject=datasetTriplet.tpltSbjct, predicate=datasetTriplet.tpltPrdct, object=datasetTriplet.tpltObjct)
        vector_update_document(reposId=reposId, document_id=tpltId, document=Document(page_content=text, metadata=result['metadatas'][0])) # 更新到向量库
        # 更新到数据库
        orm.copy_from_dict(datasetTriplet.to_dict())
        session.merge(orm)

  def removeTripletById(self, tpltId: str):
    with session_scope() as session:
      orm = session.get(DatasetTriplet, tpltId)
      if (orm is None):
        return
      vector_delete(reposId=orm.reposId, ids=[tpltId])
      # 删除数据库
      session.delete(orm)