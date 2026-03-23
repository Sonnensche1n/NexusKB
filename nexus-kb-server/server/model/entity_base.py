from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BaseEntity(BaseModel):
  def copy_from_dict(self, dict_:dict, convert = None, excludes:list = []):
    for key, value in dict_.items():
      if (key in excludes):
        continue
      if convert is not None:
        value = convert(key, value)
      setattr(self, key, value)
    return self
  def to_dict(self, convert = None, excludes:list = []):
    dict_ = vars(self)
    new_dict = {}
    for key, value in dict_.items():
      if (key in excludes):
        continue
      if convert is not None:
        value = convert(key, value)
      if (value is not None and isinstance(value, datetime)):
        value = value.isoformat() # 不处理,不能序列化为 json
      new_dict[key] = value
    return new_dict
  
class PageBase(BaseEntity):
  pageSize: Optional[int] = Field(10)
  pageNum: Optional[int] = Field(1)
  orderName: Optional[str] = Field(None)
  orderValue: Optional[str] = Field(None)
  def get_offset(self) -> int:
    return (self.pageNum - 1) * self.pageSize
