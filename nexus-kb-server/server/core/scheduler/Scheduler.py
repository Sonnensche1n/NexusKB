import asyncio
from sqlalchemy import select, or_
from logger import logger
from server.db.DbManager import session_scope
from server.model.orm_knb import Dataset
from server.core.queue.DatasetToVectorQueue import produce as vectorProduce
from server.core.queue.DatasetEnhanceVectorQueue import produce as enhanceProduce, EnhanceItem
from datetime import datetime

# 定义定时任务函数
async def datasetToVectorQueueJob():
  while True:
    logger.info(f"数据集向量索引定时任务执行于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # 查询索引状态为新建且已启用的数据集
    stmt = select(Dataset).where(Dataset.idxSts == 'new', Dataset.enbSts == 'enb').order_by(Dataset.crtTm.asc())
    with session_scope() as session:
      for row in session.scalars(stmt):
        dataset = row.to_dict(convert=lambda key, value: '' if value is None else value, excludes=['crtUser', 'crtTm', 'idxSts', 'enbSts'])
        if (vectorProduce(dataset)):
          row.idxSts = 'order'
          session.merge(row)
    await asyncio.sleep(30) # 每隔30秒执行一次

async def datasetEnhanceQueueJob():
  while True:
    logger.info(f"数据集增强索引定时任务执行于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # 查询摘要,Q&A,三元组状态为新建且已启用的数据集：三种任务共用一个队列
    stmt = select(Dataset).where(Dataset.enbSts == 'enb', Dataset.idxSts == 'ready', or_(Dataset.prcsSts == 'new', Dataset.qaSts == 'new', Dataset.tpltSts == 'new')).order_by(Dataset.crtTm.asc())
    with session_scope() as session:
      for row in session.scalars(stmt):
        dataset = row.to_dict(convert=lambda key, value: '' if value is None else value, excludes=['crtUser', 'crtTm', 'idxSts', 'enbSts'])
        if (row.prcsSts == 'new'):
          item = EnhanceItem(dataset['dtsetId'], 'precis')
          if (enhanceProduce(item)):
            row.prcsSts = 'order'
        if (row.qaSts == 'new'):
          item = EnhanceItem(dataset['dtsetId'], 'qanswer')
          if (enhanceProduce(item)):
            row.qaSts = 'order'
        if (row.tpltSts == 'new'):
          item = EnhanceItem(dataset['dtsetId'], 'triplet')
          if (enhanceProduce(item)):
            row.tpltSts = 'order'
          session.merge(row)
    await asyncio.sleep(30) # 每隔30秒执行一次