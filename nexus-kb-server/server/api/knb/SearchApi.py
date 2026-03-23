from fastapi import FastAPI, Request
from server.db.DbManager import session_scope
from server.api.BaseApi import BaseApi
from sqlalchemy import select, delete
from server.model.orm_knb import SrchHist
from server.model.entity_knb import SrchInfo as SrchInfoEntity, SrchHist as SrchHistEntity
from datetime import datetime
from server.core.tools.ask_to_llm import get_related_docs_by_repos_id
from server.utils.websocketutils import WebsocketManager

class SearchApi(BaseApi):
  def __init__(self, app: FastAPI, manager: WebsocketManager):
    BaseApi.__init__(self)
  
    # 搜索
    @app.post('/knb/search')
    def search(srchInfo: SrchInfoEntity, request: Request):
      reposId = srchInfo.reposId
      if (not srchInfo.noHist):
        srchHist = SrchHistEntity(
          srchId = self.getPk(),
          reposId = reposId,
          srchText = srchInfo.searchTxt,
          srchTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
          crtUser = self.getUserId(request)
        )
        orm = SrchHist().copy_from_dict(vars(srchHist))
        with session_scope() as session:
          session.add(orm)
      
      related_docs_with_score = get_related_docs_by_repos_id(reposId=reposId, question=srchInfo.searchTxt)
      data = []
      if (related_docs_with_score is None):
        return self.success(data)
      # dtsetIds = set()
      for doc, score in related_docs_with_score:
        metadata = doc.metadata
        if ('dtsetId' in metadata):
          dtsetId = metadata['dtsetId']
        elif ('source' in metadata):
          source = metadata['source']
          dtsetId = (source.split('/')[-1]).split('.')[0]
        if (dtsetId is None):
          continue
        # dtsetIds.add(dtsetId)
        data.append({
          'srcId': dtsetId, # 来源文件ID
          'score': float(score),
          'content': doc.page_content,
          'srcNm': metadata['dtsetNm'],
          'srcTyp': metadata['fileTyp']
        })
      return self.success(data)
    
    # 搜索历史查询
    @app.post('/knb/search/hist/list')
    def searchHistList(srchHist: SrchHistEntity):
      reposId = srchHist.reposId
      stmt = select(SrchHist).where(SrchHist.reposId == reposId).order_by(SrchHist.srchTm.desc()).limit(10)
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 搜索我的历史查询
    @app.post('/knb/search/hist/my/list')
    def searchHistList(srchHist: SrchHistEntity, request: Request):
      reposId = srchHist.reposId
      stmt = select(SrchHist).where(SrchHist.reposId == reposId, SrchHist.crtUser == self.getUserId(request)).order_by(SrchHist.srchTm.desc()).limit(10)
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 移除搜索历史
    @app.delete('/knb/search/hist/{srchId}')
    def searchHistRemove(srchId: str):
      with session_scope() as session:
        stmt = delete(SrchHist).where(SrchHist.srchId == srchId)
        session.execute(stmt)
      return self.success()