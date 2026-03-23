import uuid
from datetime import datetime
from server.db.DbManager import session_scope
from server.model.orm_doc import DocsetInfo, DocmtVersion, DocmtInfo
from server.model.orm_knb import Dataset
from server.model.entity_doc import DocsetInfo as DocsetInfoEntity
from server.exception.exception import BaseBusiException
from server.core.knb.DatasetService import DatasetService

class DocsetService():
  datasetService = DatasetService()
  # 根据文档集id与用户id查询文档集信息，带权限的信息
  def select_by_set_id_and_user_id(self, setId:str, userId:str):
    with session_scope() as session:
      orm = session.get(DocsetInfo, setId)
      if orm is None: return None
      docsetInfo = DocsetInfoEntity().copy_from_dict(orm.to_dict())
      docsetInfo.optAuth = 'alter'
      return docsetInfo
  # 查询用户的文档集列表
  def select_list_by_user_id(self, userId:str):
    return []
  
  # 将文档发布到数据集中
  def add_to_dataset(self, reposId:str, docId:str, userId:str):
    with session_scope() as session:
      info = session.get(DocmtInfo, docId)
      if (info is None):
        raise BaseBusiException('文档不存在或被删除')
      # 创建版本
      verId = str(uuid.uuid4()).replace('-', '')
      version = DocmtVersion().copy_from_dict(info.to_dict()) # 复制数据
      version.verId = verId
      version.crtUser = userId
      version.crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      session.add(version)

      # 查询是否已经添加到该知识库
      dataset = session.query(Dataset).where(Dataset.reposId==reposId, Dataset.docId==docId).first()
      dtsetId = str(uuid.uuid4()).replace('-', '')
      enbSts = 'une'
      if (dataset is not None):
        dtsetId = dataset.dtsetId
        enbSts = dataset.enbSts
        self.datasetService.removeDatasetExtendsByIdAndTypes(reposId=reposId, dtsetId=dtsetId, session=session)
      # 创建数据集与版本关联起来
      
      dataset = Dataset(
        dtsetId = dtsetId,
        reposId = reposId,
        dtsetTyp = 'dcmt', # 暂时默认只支持文本
        dtsetNm = version.docTtl,
        docId = docId,
        docVerId = verId,
        fileTyp = 'html' if version.docTyp == 'rt' else 'md',
        idxSts = 'new',
        prcsSts = 'nobd',
        qaSts = 'nobd',
        tpltSts = 'nobd',
        enbSts = enbSts, # enb 已启用，une 未启用
        crtUser = userId,
        crtTm = version.crtTm
      )
      session.merge(dataset)