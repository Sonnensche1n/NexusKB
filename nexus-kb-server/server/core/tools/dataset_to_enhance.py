import json
import uuid
import random
import re
from logger import logger
from sqlalchemy import select
from config.prompt import QANSWER_PROMPT_TEMPLATE, PRECIS_PROMPT_TEMPLATE, TRIPLET_PROMPT_TEMPLATE
from server.model.orm_knb import ReposQuest, DatasetChunk, Dataset, DatasetPrecis, DatasetTriplet
from server.model.entity_knb import Dataset as DatasetEntity, ReposQuest as ReposQuestEntity, DatasetPrecis as DatasetPrecisEntity, DatasetTriplet as DatasetTripletEntity
from server.db.DbManager import session_scope
from .repos_vector_db import docs_save_to_vector_db
from server.core.tools.llm_client_tools import get_user_llm_client

default_dataset_excludes=['crtUser', 'crtTm', 'idxSts', 'prcsSts', 'qaSts', 'tpltSts', 'enbSts', '_sa_instance_state']

def ask_to_llm(userId: str, prompts: str):
  client = get_user_llm_client(userId)
  reponse = client.invoke(prompts)
  if (type(reponse) != str):
    return reponse.content
  return reponse

def generate_llm_qanswer_prompts(source: str, context: str) -> str:
  return QANSWER_PROMPT_TEMPLATE.replace('{source}', source).replace('{context}', context)

def generate_llm_precis_prompts(source: str, context: str) -> str:
  return PRECIS_PROMPT_TEMPLATE.replace('{source}', source).replace('{context}', context)

def generate_llm_triplet_prompts(source: str, context: str) -> str:
  return TRIPLET_PROMPT_TEMPLATE.replace('{source}', source).replace('{context}', context)

def extract_response_code(type: str, content: str):
  try:
    code = content.split(f"```{type}")[1].split("```")[0]
  except Exception:
    code = ''
  return code

def sample_from_list(data_list, num_samples):
  if len(data_list) <= num_samples:
    return data_list
  else:
    return random.sample(data_list, num_samples)

def start_to_build_precis_index(dataset:DatasetEntity, pages:int, size:int):
  dtsetId = dataset.dtsetId
  dtsetNm = dataset.dtsetNm
  reposId = dataset.reposId
  userId = dataset.crtUser
  precisList = [] # entity
  finalPrecisContent = ''
  precis = []
  with session_scope() as session:
    for page in range(pages): # 分页处理
      offset = page * size
      stmt = select(DatasetChunk).where(DatasetChunk.dtsetId == dtsetId).order_by(DatasetChunk.chkSeq.asc()).offset(offset).limit(size)
      chunks = session.scalars(stmt)
      contents = [chunk.chkCntnt for chunk in chunks]
      context = finalPrecisContent + '\n' + '\n'.join(contents) # 将前一次的摘要与这一次的分片一起拼接，再生成新的摘要
      # 生成摘要
      precis_prompts = generate_llm_precis_prompts(source=dtsetNm, context=context)
      finalPrecisContent = ask_to_llm(userId, precis_prompts) # 这是生成的摘要
      precis_orm = DatasetPrecis(
        prcsId=str(uuid.uuid4()).replace('-', ''), prcsSrc='ai', dtsetId=dtsetId, reposId=reposId, prcsSeq=page, prcsCntnt=f'#{dtsetNm}\n{finalPrecisContent}'
      )
      precis.append(precis_orm)
      precisList.append(DatasetPrecisEntity().copy_from_dict(precis_orm.to_dict(), excludes=['prcsSrc', 'prcsSeq']))

    if (len(precis) > 0):
      session.bulk_save_objects(precis) # 保存到数据库

  # 保存到向量库
  if (len(precisList) > 0):
    logger.info('开始构建数据集摘要索引:' + dtsetId)
    precis_save_to_vector_db(precisList=precisList, dataset=dataset)
    logger.info('构建数据集摘要索引:' + dtsetId + '完毕,摘要总数:' + str(len(precisList)))

def start_to_build_qanswer_index(dataset:DatasetEntity, pages:int, size:int):
  dtsetId = dataset.dtsetId
  dtsetNm = dataset.dtsetNm
  reposId = dataset.reposId
  userId = dataset.crtUser
  qanswerList = [] # entity
  with session_scope() as session:
    for page in range(pages): # 分页处理
      offset = page * size
      stmt = select(DatasetChunk).where(DatasetChunk.dtsetId == dtsetId).order_by(DatasetChunk.chkSeq.asc()).offset(offset).limit(size)
      chunks = session.scalars(stmt)
      contents = [chunk.chkCntnt for chunk in chunks]
      context = ''.join(contents)
      # 生成问答对
      qanswer_prompts = generate_llm_qanswer_prompts(source=dtsetNm, context=context)
      response = ask_to_llm(userId, qanswer_prompts) # 这是生成的问答对
      response = extract_response_code('json', response)
      qanswers = []
      try:
        qas = json.loads(response)
        for qa in qas:
          qstId = str(uuid.uuid4()).replace('-', '')
          quest_orm = ReposQuest(qstId=qstId, qstQuest=qa['question'], qstAswr=qa['answer'], qstSrc='ai', reposId=reposId, dtsetId=dtsetId)
          qanswers.append(quest_orm)
          qanswerList.append(ReposQuestEntity().copy_from_dict(vars(quest_orm), excludes=['qstSrc']))
      except json.JSONDecodeError:
        pass
      if (len(qanswers) > 0):
        session.bulk_save_objects(qanswers) # 保存到数据库
  # 保存到向量库
  if (len(qanswerList) > 0):
    logger.info('开始构建数据集QA索引:' + dtsetId)
    qanswer_save_to_vector_db(qanswerList=qanswerList, dataset=dataset)
    logger.info('构建数据集QA索引:' + dtsetId + '完毕,摘要总数:' + str(len(qanswerList)))

extract_triplet_pattern = r'\(.*?\)'
# 提取内容
def extract_triplet_content(text: str) -> str:
  matchs = re.findall(extract_triplet_pattern, text)
  # 如果找到了匹配项
  result = []
  for match in matchs:
    # 提取括号内的内容并去除括号
    content = match[1:-1]
    items = []
    if (',' in content):
      items = content.split(',')
    # 按逗号分割内容
    items = content.split('，') # 输出: 提取的内容: ['可视化大屏项目', '归属于', '梦洪公司']
    if (len(items) != 3):
      continue
    result.append(items)
  return result

def start_to_build_triplet_index(dataset:DatasetEntity, pages:int, size:int):
  dtsetId = dataset.dtsetId
  dtsetNm = dataset.dtsetNm
  reposId = dataset.reposId
  userId = dataset.crtUser
  tripletList = [] # entity
  tripletKeys = []
  with session_scope() as session:
    for page in range(pages): # 分页处理
      offset = page * size
      stmt = select(DatasetChunk).where(DatasetChunk.dtsetId == dtsetId).order_by(DatasetChunk.chkSeq.asc()).offset(offset).limit(size)
      chunks = session.scalars(stmt)
      contents = [chunk.chkCntnt for chunk in chunks]
      context = ''.join(contents)
      # 生成三元组【如果一次性内容太多本地模型完全没有效果】
      triplet_prompts = generate_llm_triplet_prompts(source=dtsetNm, context=context)
      response = ask_to_llm(userId, triplet_prompts)
      extract_triplets = extract_triplet_content(response)
      if (len(extract_triplets) == 0):
        continue
      triplets = []
      for i, tp in enumerate(extract_triplets):
        subject = tp[0]
        predicate = tp[1]
        object = tp[2]
        if (subject == object):
          continue
        key = subject + '-' + object
        if (key in tripletKeys):
          continue
        tripletKeys.append(key)
        key = object + '-' + subject
        if (key in tripletKeys):
          continue
        tripletKeys.append(key)

        tpltId = str(uuid.uuid4()).replace('-', '')
        tplt_orm = DatasetTriplet(tpltId=tpltId, tpltSeq=i, tpltSbjct=subject, tpltPrdct=predicate, tpltObjct=object, tpltSrc='ai', dtsetId=dtsetId, reposId=reposId)
        triplets.append(tplt_orm)
        tripletList.append(DatasetTripletEntity().copy_from_dict(vars(tplt_orm), excludes=['tpltSrc', 'tpltSeq']))
      
      if (len(triplets) > 0):
        session.bulk_save_objects(triplets) # 保存到数据库

  if (len(tripletList) > 0):
    logger.info('开始构建数据集三元组索引:' + dtsetId)
    triplet_save_to_vector_db(tripletList=tripletList, dataset=dataset)
    logger.info('构建数据集三元组索引:' + dtsetId + '完毕,三元组总数:' + str(len(tripletList)))

# 根据拆分的内容生成问答对
# type: precis, qanswer, triplet
def start_dataset_to_enhance(dtsetId:str, type:str):
  logger.info('开始处理数据集摘要、问答对:' + dtsetId)
  with session_scope() as session:
    dataset = session.get(Dataset, dtsetId)
    if (dataset is None):
      logger.error('数据集不存在或者被删除:' + dtsetId)
      return
    dataset = DatasetEntity().copy_from_dict(vars(dataset))
    total = session.query(DatasetChunk).where(DatasetChunk.dtsetId == dtsetId).count()
    if (total == 0):
      logger.info('数据集分片数量为0:' + dtsetId)
      return
    size = 10
    pages = (total + size - 1) // size # 总页数
    if (type == 'precis'):
      start_to_build_precis_index(dataset, pages, size)
    elif (type == 'qanswer'):
      start_to_build_qanswer_index(dataset, pages, size)
    elif (type == 'triplet'):
      start_to_build_triplet_index(dataset, pages, size)

def precis_save_to_vector_db(precisList: list[DatasetPrecisEntity], dataset: DatasetEntity):
  reposId = dataset.reposId
  dataset = dataset.to_dict(convert=lambda key, value: '' if value is None else value, excludes=default_dataset_excludes)
  texts = []
  ids = []
  metadatas = []
  for precis in precisList:
    prcsId = precis.prcsId
    texts.append(precis.prcsCntnt)
    ids.append(prcsId)
    metadata = {
      'prcsId': prcsId
    }
    metadata.update(dataset)
    metadatas.append(metadata)
  docs_save_to_vector_db(reposId=reposId, texts=texts, ids=ids, metadatas=metadatas)

def triplet_save_to_vector_db(tripletList: list[DatasetTripletEntity], dataset: DatasetEntity):
  reposId = dataset.reposId
  dataset = dataset.to_dict(convert=lambda key, value: '' if value is None else value, excludes=default_dataset_excludes)
  texts = []
  ids = []
  metadatas = []
  for triplet in tripletList:
    tpltId = triplet.tpltId
    texts.append(f'({triplet.tpltSbjct}, {triplet.tpltPrdct}, {triplet.tpltObjct})')
    ids.append(tpltId)
    metadata = {
      'tpltId': tpltId
    }
    metadata.update(dataset)
    metadatas.append(metadata)
  docs_save_to_vector_db(reposId=reposId, texts=texts, ids=ids, metadatas=metadatas)

def qanswer_save_to_vector_db(qanswerList: list[ReposQuestEntity], dataset: DatasetEntity):
  reposId = dataset.reposId
  dataset = dataset.to_dict(convert=lambda key,value: '' if value is None else value, excludes=default_dataset_excludes)
  texts = []
  ids = []
  metadatas = []
  for qa in qanswerList:
    text = {
      'question': qa.qstQuest, 'answer': qa.qstAswr
    }
    qstId = qa.qstId
    texts.append(json.dumps(text, ensure_ascii=False))
    ids.append(qstId)
    metadata = {
      'qstId': qstId
    }
    metadata.update(dataset)
    metadatas.append(metadata)
  docs_save_to_vector_db(reposId=reposId, texts=texts, ids=ids, metadatas=metadatas)
