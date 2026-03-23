import os
import nltk
import uuid
from logger import logger
from sqlalchemy import insert
from server.db.DbManager import session_scope
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredPowerPointLoader
from langchain_text_splitters.html import HTMLHeaderTextSplitter
from langchain_text_splitters.markdown import MarkdownTextSplitter
from text_splitter.chinese_recursive_text_splitter import ChineseRecursiveTextSplitter
from .file_tools import is_pdf, is_ppt, is_word, is_markdown
from server.model.orm_knb import DatasetChunk
from server.model.orm_doc import DocmtVersion
from .repos_vector_db import docs_save_to_vector_db
from server.utils.httputils import get_webpage_text

# nltk 模型存储路径 RapidOCRPDFLoader 需要用到
NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'resources/nltk_data')
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

#
# 配合此文阅读代码，效果更佳：https://zhuanlan.zhihu.com/p/635661366
#
os.environ['CUDA_LAUNCH_BLOCKING'] = '1' # 打印详细的cuda错误日志

CHUNK_SIZE = 1024
CHUNK_OVERLAP = 200

# 开始构建数据集索引
def start_to_build_dataset_index(dataset):
  reposId = dataset['reposId'] # 知识库ID
  dtsetTyp = dataset['dtsetTyp']
  docs = []
  if (dtsetTyp == 'dcmt'):
    docVerId = dataset['docVerId']
    if (docVerId is None):
      raise Exception('没有找到数据集对应文档版本' + docVerId)
    docs = dcmt_to_documents(docVerId)
  elif (dtsetTyp == 'text' or dtsetTyp == 'audio' or dtsetTyp == 'video'):
    # 将文本向量化
    filePath = dataset['filePath'] # 待构建索引的文件路径
    logger.info('正在将文档解析并拆分为文本集合:' + dataset['fileNm'])
    fileTyp = dataset['fileTyp']
    if (fileTyp == 'link'):
      docs = link_to_documents(filePath)
    else:
      docs = file_to_documents(filePath) # 将文件转换为文本集合
  if (docs is None or len(docs) == 0):
    raise Exception('没有解析出文本内容，索引失败' + dataset['fileNm'])
  
  # 将文档分段保存到数据库中
  datasetChunks = [] # 保存到数据库中
  texts = [] # 需要保存的文档，保存到向量库中
  ids = [] # 文档对应的id，保存到向量库中
  metadatas = [] # 文档对应的元数据，保存到向量库中

  for i, doc in enumerate(docs):
    chkId = str(uuid.uuid4()).replace('-', '') # 分段ID
    datasetChunks.append(DatasetChunk(
      chkId=chkId, dtsetId=dataset['dtsetId'], reposId=reposId, chkCntnt=doc.page_content, chkSeq=i
    ))
    texts.append(doc.page_content)
    ids.append(chkId)
    doc.metadata['chkId'] = chkId
    doc.metadata.update(dataset) # 将数据集的内容也放进去 元数据的属性不能为空
    metadatas.append(doc.metadata)
  with session_scope() as session:
    session.bulk_save_objects(datasetChunks)
  
  logger.info('完成将文档解析并拆分为文本集合:' + dataset['fileNm'])
  logger.info('将文本集合保存到索引文件:' + dataset['fileNm'])
  docs_save_to_vector_db(reposId=reposId, texts=texts, ids=ids, metadatas=metadatas)
  logger.info('完成将文本集合保存到索引文件:' + dataset['fileNm'])

def dcmt_to_documents(docVerId:str) -> list:
  with session_scope(True) as session:
    docmtVersion = session.get(DocmtVersion, docVerId)
    if (docmtVersion is None):
      raise Exception('数据集对应文档版本数据不存在或被删除' + docVerId)
    content = docmtVersion.docCntnt
    docTyp = docmtVersion.docTyp
    if (docTyp == 'rt'): # 富文本
      textsplitter = HTMLHeaderTextSplitter([('h1', '一级标题'), ('h2', '二级标题'), ('h3', '三级标题')])
    elif (docTyp == 'md'):
      textsplitter = MarkdownTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    else:
      textsplitter = ChineseRecursiveTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    docs = textsplitter.split_text(content)
  return docs

# 将文档分割为文本集合
def file_to_documents(doc_path: str) -> list:
  docs = []
  pdf = is_pdf(doc_path)
  if (pdf): # pdf文件
    loader = PyPDFLoader(file_path=doc_path)
  elif (is_ppt(doc_path)): # ppt文件
    loader = UnstructuredPowerPointLoader(file_path=doc_path)
  elif (is_word(doc_path)):
    loader = UnstructuredWordDocumentLoader(file_path=doc_path)
  else:
    loader = TextLoader(doc_path, autodetect_encoding=True)
  documents = loader.load()
  # textsplitter = ChineseTextSplitter(pdf=pdf, sentence_size=CHUNK_SIZE)
  if (is_markdown(doc_path)):
    textsplitter = MarkdownTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
  else:
    textsplitter = ChineseRecursiveTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
  docs.extend(textsplitter.split_documents(documents))
  return docs

def link_to_documents(url_path: str) -> list:
  text = get_webpage_text(url_path)
  if (text is None):
    return []
  textsplitter = HTMLHeaderTextSplitter([('h1', '一级标题'), ('h2', '二级标题'), ('h3', '三级标题')])
  docs = textsplitter.split_text(text)
  return docs
def prob_related_documents_and_score(related_docs_with_score):
  for doc, score in related_docs_with_score:
    logger.info('%s [%s]: %s' % (doc.metadata['source'], score, doc.page_content))
