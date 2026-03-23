import jwt
import datetime

SECRET_KEY = 'xxxxxxxxxxxxxxx'
ALGORITHM = 'HS256'

# 创建token
def generate_token(inf:dict):
  payload = {
    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7), # 有效期七天
    'iat': datetime.datetime.utcnow(),
    'inf': inf
  }
  return jwt.encode(
    payload,
    SECRET_KEY,
    algorithm=ALGORITHM
  )
  
# 解析token
def decode_token(token):
  """ 解码Token并处理异常 """
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    return payload['inf']  # 返回成功标志和内容
  except jwt.ExpiredSignatureError as e:
    return False
  except jwt.InvalidTokenError as e:
    return False