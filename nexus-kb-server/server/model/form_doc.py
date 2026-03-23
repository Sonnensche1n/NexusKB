from pydantic import BaseModel, Field
from typing import Optional

# 文档转数据集
class DocmtToDatasetForm(BaseModel):
  docId: str
  reposId: str