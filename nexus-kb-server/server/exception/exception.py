# 官方推荐注册异常处理器时，应该注册到来自 Starlette 的 HTTPException
import traceback
from fastapi import Request
from starlette.exceptions import HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.responses import JSONResponse
from logger import logger

class BaseBusiException(HTTPException):
  status_code = HTTP_500_INTERNAL_SERVER_ERROR # 系统错误码
  error_code: str = '9999' # 业务错误码
  error_msg = 'An internal program error has occurred!'
  def __init__(self, error_msg: str = None, error_code: str = '9999', status_code: int = HTTP_500_INTERNAL_SERVER_ERROR):
    self.error_msg = error_msg or self.error_msg
    self.detail = self.error_msg
    self.status_code = status_code or self.status_code
    self.error_code = error_code or self.error_code

# 全局异常
async def global_busi_exception_handler(request: Request, exc:BaseBusiException):
  return JSONResponse(
		status_code=exc.status_code or HTTP_500_INTERNAL_SERVER_ERROR,
		content={
      'code': exc.error_code or '9998', # 业务错误码
      'success': False,
      'data': None,
      'msg': exc.error_msg,
    })

# 处理可捕获的异常
golbal_exception_handlers = {
	BaseBusiException: global_busi_exception_handler,
}

# 处理未捕获的异常
async def global_exceptions_middleware(request: Request, call_next):
  try:
    return await call_next(request)
  except Exception as e:
    logger.error(f'内部错误：{e}')
    traceback.print_exc()
    return JSONResponse(
      status_code=HTTP_500_INTERNAL_SERVER_ERROR,
      content={
        'code': '9999', # 系统错误码
        'success': False,
        'data': None,
        'msg': '发生内部错误'
      })


