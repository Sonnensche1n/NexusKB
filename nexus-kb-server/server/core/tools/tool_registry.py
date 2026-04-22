"""
工具注册表
统一管理可被 LLM 通过 Function Calling 调用的工具。
"""

import json
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class ToolRegistry:
  """工具注册中心。"""

  def __init__(self):
    self._tools = {}

  def register(self, name: str, description: str, parameters: dict, handler: Callable):
    self._tools[name] = {
      "schema": {
        "type": "function",
        "function": {
          "name": name,
          "description": description,
          "parameters": parameters,
        },
      },
      "handler": handler,
    }
    logger.info(f"[ToolRegistry] 注册工具: {name}")

  def get_schemas(self) -> list:
    return [tool["schema"] for tool in self._tools.values()]

  def execute(self, name: str, arguments: dict) -> str:
    if name not in self._tools:
      return json.dumps({"error": f"工具 {name} 不存在"}, ensure_ascii=False)
    try:
      result = self._tools[name]["handler"](**arguments)
      if isinstance(result, str):
        return result
      return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
      logger.error(f"[ToolRegistry] 执行工具 {name} 失败: {e}")
      return json.dumps({"error": str(e)}, ensure_ascii=False)

  def has_tool(self, name: str) -> bool:
    return name in self._tools

  def list_tools(self) -> list:
    return list(self._tools.keys())


tool_registry = ToolRegistry()


def register_default_tools():
  """注册 NexusKB 内置工具。重复调用时直接返回。"""
  if tool_registry.list_tools():
    return

  def search_knowledge_base(query: str, repos_id: str, top_k: int = 5) -> dict:
    from server.core.tools.ask_to_llm import get_related_docs_by_repos_id
    from server.model.entity_knb import ReposSetting as ReposSettingEntity

    setting = ReposSettingEntity()
    setting.topK = top_k
    setting.smlrTrval = 1.0
    setting.maxCtx = top_k

    docs = get_related_docs_by_repos_id(repos_id, query, setting)
    if docs is None:
      return {"results": [], "message": "知识库为空或不存在"}

    results = []
    for doc, score in docs[:top_k]:
      metadata = getattr(doc, "metadata", {}) or {}
      results.append({
        "content": getattr(doc, "page_content", ""),
        "dtsetId": metadata.get("dtsetId", ""),
        "dtsetNm": metadata.get("dtsetNm", ""),
        "fileNm": metadata.get("fileNm", ""),
        "fileTyp": metadata.get("fileTyp", ""),
        "source": metadata.get("fileNm") or metadata.get("dtsetNm") or "未知",
        "score": float(score),
      })
    return {"results": results, "count": len(results)}

  tool_registry.register(
    name="search_knowledge_base",
    description="搜索指定知识库中的相关文档片段，用于回答基于知识库的问题。",
    parameters={
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "搜索查询文本，通常是用户问题中的核心检索词。",
        },
        "repos_id": {
          "type": "string",
          "description": "知识库ID。",
        },
        "top_k": {
          "type": "integer",
          "description": "返回的文档片段数量，默认 5。",
          "default": 5,
        },
      },
      "required": ["query", "repos_id"],
    },
    handler=search_knowledge_base,
  )

  def get_document_summary(repos_id: str, dataset_id: str = None) -> dict:
    from sqlalchemy import select
    from server.db.DbManager import session_scope
    from server.model.orm_knb import Dataset, DatasetPrecis

    with session_scope(True) as session:
      if dataset_id:
        stmt = (
          select(DatasetPrecis, Dataset.dtsetNm)
          .join(Dataset, Dataset.dtsetId == DatasetPrecis.dtsetId)
          .where(DatasetPrecis.reposId == repos_id, DatasetPrecis.dtsetId == dataset_id)
          .order_by(DatasetPrecis.prcsSeq.asc())
        )
        summaries = []
        title = ""
        for precis, dtset_nm in session.execute(stmt):
          title = dtset_nm or title
          if precis.prcsCntnt:
            summaries.append(precis.prcsCntnt)
        if summaries:
          return {"summary": "\n".join(summaries), "source": title}
        return {"summary": "该文档暂无摘要", "source": ""}

      stmt = (
        select(DatasetPrecis, Dataset.dtsetNm)
        .join(Dataset, Dataset.dtsetId == DatasetPrecis.dtsetId)
        .where(DatasetPrecis.reposId == repos_id)
        .order_by(DatasetPrecis.prcsSeq.asc())
        .limit(5)
      )
      results = []
      for precis, dtset_nm in session.execute(stmt):
        results.append({
          "title": dtset_nm,
          "summary": precis.prcsCntnt,
        })
      return {"summaries": results, "count": len(results)}

  tool_registry.register(
    name="get_document_summary",
    description="获取知识库中文档的自动生成摘要，可以获取单个文档摘要或知识库中的摘要列表。",
    parameters={
      "type": "object",
      "properties": {
        "repos_id": {
          "type": "string",
          "description": "知识库ID。",
        },
        "dataset_id": {
          "type": "string",
          "description": "文档集ID，可选。",
        },
      },
      "required": ["repos_id"],
    },
    handler=get_document_summary,
  )

  def search_qa_pairs(query: str, repos_id: str, limit: int = 5) -> dict:
    from sqlalchemy import select
    from server.db.DbManager import session_scope
    from server.model.orm_knb import ReposQuest

    keywords = [kw for kw in query.split() if kw][:3]
    with session_scope(True) as session:
      stmt = select(ReposQuest).where(ReposQuest.reposId == repos_id).limit(limit * 5)
      results = []
      for row in session.scalars(stmt):
        question = row.qstQuest or ""
        answer = row.qstAswr or ""
        if not keywords or any(kw in question or kw in answer for kw in keywords):
          results.append({
            "question": question,
            "answer": answer,
          })
        if len(results) >= limit:
          break
      return {"qa_pairs": results, "count": len(results)}

  tool_registry.register(
    name="search_qa_pairs",
    description="搜索知识库中预先生成的问答对，适合 FAQ 或八股问答场景。",
    parameters={
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "搜索关键词。",
        },
        "repos_id": {
          "type": "string",
          "description": "知识库ID。",
        },
        "limit": {
          "type": "integer",
          "description": "返回数量上限，默认 5。",
          "default": 5,
        },
      },
      "required": ["query", "repos_id"],
    },
    handler=search_qa_pairs,
  )

  def search_knowledge_triplets(query: str, repos_id: str, limit: int = 10) -> dict:
    from sqlalchemy import or_, select
    from server.db.DbManager import session_scope
    from server.model.orm_knb import DatasetTriplet

    keywords = [kw for kw in query.split() if kw][:5]
    with session_scope(True) as session:
      stmt = select(DatasetTriplet).where(DatasetTriplet.reposId == repos_id)
      if keywords:
        conditions = []
        for kw in keywords:
          conditions.append(DatasetTriplet.tpltSbjct.contains(kw))
          conditions.append(DatasetTriplet.tpltObjct.contains(kw))
          conditions.append(DatasetTriplet.tpltPrdct.contains(kw))
        stmt = stmt.where(or_(*conditions))
      stmt = stmt.limit(limit)

      triplets = []
      for row in session.scalars(stmt):
        triplets.append({
          "subject": row.tpltSbjct,
          "predicate": row.tpltPrdct,
          "object": row.tpltObjct,
        })
      return {"triplets": triplets, "count": len(triplets)}

  tool_registry.register(
    name="search_knowledge_triplets",
    description="搜索知识库中的知识三元组，适合实体关系查询。",
    parameters={
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "搜索关键词，用于匹配三元组中的主体、谓词或客体。",
        },
        "repos_id": {
          "type": "string",
          "description": "知识库ID。",
        },
        "limit": {
          "type": "integer",
          "description": "返回数量上限，默认 10。",
          "default": 10,
        },
      },
      "required": ["query", "repos_id"],
    },
    handler=search_knowledge_triplets,
  )

  logger.info(
    f"[ToolRegistry] 已注册 {len(tool_registry.list_tools())} 个内置工具: {tool_registry.list_tools()}"
  )
