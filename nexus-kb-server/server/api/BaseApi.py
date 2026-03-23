from fastapi import Request
import uuid

class BaseApi():
  def __init__(self):
    pass
  
  # 获取主键
  def getPk(self):
    return str(uuid.uuid4()).replace('-', '')
  
  def getToken(self, request:Request):
    return request.headers.get('token')

  def getUserId(self, request:Request):
    if (request.state.user is None):
      return None
    else:
      return request.state.user['id']
  def success(self, data=None, msg='操作成功'):
    return {
      'code': '0000',
      'success': True,
      'data': data,
      'msg': msg
    }

  def fail(self, code='9999', data=None, msg='操作失败'):
    return {
      'code': code,
      'success': False,
      'data': data,
      'msg': msg
    }
  
  def sucess_page(self, data=None, total=0, size=10, page=1, pages=0, msg='操作成功'):
    if (pages == 0 and total > 0 and size > 0):
      pages = (total + size - 1) // size
    return {
      'total': total,
      'size': size, # 每页大小
      'page': page, # 页码
      'pages': pages, # 总页数
      'data': data,
      'code': '0000',
      'success': True,
      'msg': msg
    }