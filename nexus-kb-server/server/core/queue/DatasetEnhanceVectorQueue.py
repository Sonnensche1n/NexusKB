import queue
import threading
import time
import traceback
from logger import logger
from server.core.tools.dataset_to_enhance import start_dataset_to_enhance
from server.db.DbManager import session_scope
from server.model.orm_knb import Dataset, DatasetIndexError

# 数据集文档内容构建 摘要，Q&A，三元组等内容的索引
# 数据集文档内容自动生成Q&A内容存储
DATASET_ENHANCE_TASK_QUEUE = queue.Queue(maxsize=30)

class EnhanceItem:
  def __init__(self, dtsetId:str, type:str) -> None:
    self.dtsetId = dtsetId
    self.type = type
def produce(item:EnhanceItem):
  try:
    DATASET_ENHANCE_TASK_QUEUE.put_nowait(item)
    logger.info(f"Producing {item.dtsetId}-{item.type}")
    return True
  except queue.Full:
    return False

# 修改数据集状态
def update_status(dtsetId:str, type: str, status:str, error: DatasetIndexError = None):
  with session_scope() as session:
    dt = session.get(Dataset, dtsetId)
    if (dt is None):
      return
    if (type == 'precis'):
      dt.prcsSts = status # 构建索引中
    elif (type == 'qanswer'):
      dt.qaSts = status
    elif (type == 'triplet'):
      dt.tpltSts = status
    session.merge(dt)
    if (error is not None):
      session.merge(error)

# type: index, precis, qanswer, triplet
def index_error(dtsetId:str, type: str, error: str):
  with session_scope() as session:
    orm = DatasetIndexError(dtsetId=dtsetId, idxTyp=type, errInf=error)
    session.merge(orm)

def consumer():
  while True:
    time.sleep(5)
    item = DATASET_ENHANCE_TASK_QUEUE.get()
    dtsetId = item.dtsetId
    type = item.type
    update_status(dtsetId, type, 'index')
    logger.info(f"Consuming {dtsetId}-{type}")
    try:
      start_dataset_to_enhance(dtsetId=dtsetId, type=item.type)
    except Exception as e:
      logger.info(f"Consume Failed {dtsetId}-{type}")
      traceback.print_exc()
      update_status(dtsetId, type, 'error', DatasetIndexError(dtsetId=dtsetId, idxTyp=type, errInf=str(e))) # type: index, precis, qanswer, triplet
    else:
      logger.info(f"Consumed {dtsetId}-{type}")
      # 修改状态
      update_status(dtsetId, type, 'ready')

thread = threading.Thread(target=consumer)
thread.start()