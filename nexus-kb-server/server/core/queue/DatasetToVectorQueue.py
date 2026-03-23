import queue
import threading
import time
import traceback
from logger import logger
from server.core.tools.dataset_to_vector import start_to_build_dataset_index
from server.db.DbManager import session_scope
from server.model.orm_knb import Dataset, DatasetIndexError

# 数据集文档转为向量索引存储
DATASET_TO_VECTOR_TASK_QUEUE = queue.Queue(maxsize=10)
def produce(dataset):
  try:
    DATASET_TO_VECTOR_TASK_QUEUE.put_nowait(dataset)
    logger.info(f"Producing {dataset['dtsetNm']}")
    return True
  except queue.Full:
    return False

# 修改数据集状态
def update_status(dtsetId:str, status:str, error: DatasetIndexError = None):
  with session_scope() as session:
    dt = session.get(Dataset, dtsetId)
    if (dt is None):
      return
    dt.idxSts = status # 构建索引中
    session.merge(dt)
    if (error is not None):
      session.merge(error)

def consumer():
  while True:
    time.sleep(5)
    dataset = DATASET_TO_VECTOR_TASK_QUEUE.get()
    dtsetId = dataset['dtsetId']
    update_status(dtsetId, 'index')
    logger.info(f"Consuming {dataset['dtsetNm']}")
    try:
      start_to_build_dataset_index(dataset)
    except Exception as e:
      logger.info(f"Consume Failed {dataset['dtsetNm']}")
      traceback.print_exc()
      update_status(dtsetId, 'error', DatasetIndexError(dtsetId=dtsetId, idxTyp='index', errInf=str(e))) # type: index, precis, qanswer, triplet
    else:
      logger.info(f"Consumed {dataset['dtsetNm']}")
      # 修改状态
      update_status(dtsetId, 'ready')

thread = threading.Thread(target=consumer)
thread.start()