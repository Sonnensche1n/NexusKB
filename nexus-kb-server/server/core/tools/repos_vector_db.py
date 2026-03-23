from typing import (
    Iterable,
    List,
    Optional
)
import chromadb
from chromadb.api.types import ID, OneOrMany, Where, WhereDocument
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from config.common import VECTOR_STORE_FILE_DIR # 向量存储的位置
from .file_tools import create_dir_if_not_exist
from .llm_client_tools import get_repos_embedding_function
from server.exception.exception import BaseBusiException

# 知识库向量文件存储库
VECTOR_STORE_DICT = {}

def get_repos_index_dir(reposId:str):
  dir = VECTOR_STORE_FILE_DIR + '/' + reposId
  create_dir_if_not_exist(dir)
  return dir
# 将解析出来的文档存储到索引文件
def docs_save_to_vector_db(reposId: str, texts: list, ids: list, metadatas: list):
  # 可能是空，暂时不管
  '''
  chromadb
    Cannot submit more than 41,666 embeddings at once.
    Please submit your embeddings in batches of size
    41,666 or less.
  -- 使用 chromadb.PersistentClient 解决
  '''
  vector_add_texts(reposId=reposId, texts=texts, metadatas=metadatas, ids=ids)

# 获取索引文件
def get_or_build_vector_db(reposId: str) -> Chroma:
  if reposId in VECTOR_STORE_DICT:
    return VECTOR_STORE_DICT[reposId]
  vectorStore = load_vector_store(reposId)
  if vectorStore is None: # 如果索引文件不存在则重新构建索引文件
    raise BaseBusiException('知识库向量集合创建失败:' + reposId)
  VECTOR_STORE_DICT[reposId] = vectorStore
  return vectorStore

def get_or_build_vector_retriever(reposId: str):
  vector_db = get_or_build_vector_db(reposId=reposId)
  return vector_db.as_retriever(search_kwargs={'k': TOP_K}, search_type='mmr')

def load_vector_store(reposId:str):
  try:
    embedding = get_repos_embedding_function(reposId)
    client = chromadb.PersistentClient(path=get_repos_index_dir(reposId=reposId))
    chroma = Chroma(collection_name=reposId, embedding_function=embedding, client=client)
    return chroma
  except Exception as e:
    import traceback
    traceback.print_exc()
    return None
  finally:
    pass

# 添加文档到向量库
def vector_add_texts(
  reposId: str,
  texts: Iterable[str],
  metadatas: Optional[List[dict]] = None,
  ids: Optional[List[str]] = None,
):
  vector = get_or_build_vector_db(reposId=reposId)
  if hasattr(
    vector._client, 'max_batch_size'
  ):  # for Chroma 0.4.10 and above
    from chromadb.utils.batch_utils import create_batches
    for batch in create_batches(
      api=vector._client,
      ids=ids,
      metadatas=metadatas,
      documents=texts,
    ):
      vector.add_texts(
        texts=batch[3] if batch[3] else [],
        metadatas=batch[2] if batch[2] else None,
        ids=batch[0],
      )
  else:
    vector.add_texts(texts=texts, metadatas=metadatas, ids=ids)

# 从向量库获取文档
def vector_get(
  reposId: str,
  ids: Optional[OneOrMany[ID]] = None,
  where: Optional[Where] = None,
  limit: Optional[int] = None,
  offset: Optional[int] = None,
  where_document: Optional[WhereDocument] = None,
  include: Optional[List[str]] = None,
):
  vector = get_or_build_vector_db(reposId=reposId)
  kwargs = {
    "ids": ids,
    "where": where,
    "limit": limit,
    "offset": offset,
    "where_document": where_document,
  }
  if include is not None:
    kwargs["include"] = include
  return vector.get(**kwargs)

# 更新向量库文档
def vector_update_document(reposId: str, document_id: str, document: Document):
  vector = get_or_build_vector_db(reposId=reposId)
  vector.update_document(document_id=document_id, document=document)

# 删除向量库索引
def vector_delete(reposId: str, ids: Optional[List[str]] = None):
  if (len(ids) == 0):
    return
  vector = get_or_build_vector_db(reposId=reposId)
  if hasattr(
    vector._client, 'max_batch_size'
  ):  # for Chroma 0.4.10 and above
    from chromadb.utils.batch_utils import create_batches
    for batch in create_batches(
      api=vector._client,
      ids=ids
    ):
      vector.delete(
        ids=batch[0]
      )
  else:
    vector.delete(ids=ids)
# 删除向量库数据集
def vector_delete_collection(reposId: str):
  vector = get_or_build_vector_db(reposId=reposId)
  vector.delete_collection()
  del VECTOR_STORE_DICT[reposId]