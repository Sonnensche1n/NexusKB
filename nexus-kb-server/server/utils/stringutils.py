import json
# 下划线命名转大驼峰命名
def snake_to_pascal(snake_str):
  components = snake_str.split('_')
  # 我们把 split 得到的每一个单词的首字母都大写，然后连接起来
  return ''.join(x.title() for x in components)

def to_json_str_or_not(obj):
  if isinstance(obj, str):
    # 如果已经是字符串，则直接返回
    return obj
  else:
    # 如果不是字符串，则尝试转换为 JSON 字符串
    try:
      return json.dumps(obj, ensure_ascii=False)
    except TypeError as e:
      # 如果对象不能被序列化为 JSON，则抛出异常
      raise ValueError(f"Object of type {type(obj).__name__} is not JSON serializable") from e
    
def is_int_str(s):
  try:
    int(s)
    return True
  except ValueError:
    return False
