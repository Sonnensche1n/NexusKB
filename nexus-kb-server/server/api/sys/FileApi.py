from fastapi import FastAPI, Request, File, UploadFile
from server.db.DbManager import session_scope
from server.api.BaseApi import BaseApi
from datetime import datetime
from config.common import DEFAULT_UPLOAD_FILE_DIR, DEFAULT_STATIC_DIR_NAME, DEFAULT_UPLOAD_DIR_NAME
from server.model.orm_sys import FileInfo
from server.model.entity_sys import FileInfo as FileInfoEntity
from server.core.tools.file_tools import create_dir_if_not_exist

class FileApi(BaseApi):
  def __init__(self, app: FastAPI):
    BaseApi.__init__(self)
  
    # 导入文件
    @app.post('/sys/file/upload')
    async def upload(request: Request, file: UploadFile = File(...)):
      # 将文件保存到本地再存储到数据集表中
      fileId = self.getPk()
      filename = file.filename
      # 获取文件扩展名（类型）
      fileExtension = filename.split('.')[-1]
      fileBaseName = filename[:filename.rfind('.')] if '.' in filename else filename
      filePath = DEFAULT_UPLOAD_FILE_DIR + '/' + fileId + '.' + fileExtension
      create_dir_if_not_exist(DEFAULT_UPLOAD_FILE_DIR)
      fileSize = file.size # 单位为字节

      # 保存到数据库
      fileInfo = FileInfoEntity(
        fileId = fileId,
        fileNm = fileBaseName,
        filePath = filePath,
        fileTyp = fileExtension,
        crtUser = self.getUserId(request),
        crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        fileSize = fileSize,
        fileUrl = f'/{DEFAULT_STATIC_DIR_NAME}/{DEFAULT_UPLOAD_DIR_NAME}/{fileId}.{fileExtension}'
      )
      with session_scope() as session:
        session.add(FileInfo().copy_from_dict(vars(fileInfo)))
      # 将文件内容保存到本地
      with open(filePath, 'wb') as buffer:
        contents = await file.read()
        buffer.write(contents)
      return self.success(fileInfo)