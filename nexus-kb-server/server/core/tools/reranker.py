"""
Reranker 重排序服务
支持硅基流动（SiliconFlow）等 OpenAI 兼容的 Rerank API
参考 Lumina-Note 实现，增加异步支持和优雅降级
"""

import httpx
import logging
from typing import Optional
from config.llm import (
    RERANKER_ENABLED,
    RERANKER_BASE_URL,
    RERANKER_MODEL,
    RERANKER_API_KEY,
    RERANKER_TOP_N,
    RERANKER_PROVIDER,
    RERANKER_LOCAL_URL,
)
from cachetools import TTLCache
import asyncio

logger = logging.getLogger(__name__)

# Reranker 结果短时缓存，避免短时间内对相同查询和文档的重复调用（5分钟缓存）
_rerank_cache = TTLCache(maxsize=50, ttl=300)

async def rerank(
    query: str,
    documents: list[dict],
    top_n: Optional[int] = None,
) -> list[dict]:
    """
    对检索结果进行 Reranker 重排序。

    设计原则：
    1. 未启用或配置不完整时，直接返回原始结果（零影响）
    2. API 调用失败时，降级返回原始结果（不中断主流程）
    3. 用 Reranker 的 relevanceScore 替换原始向量相似度分数

    :param query: 用户的查询文本
    :param documents: 检索结果列表，每项需包含 'content' 字段
                      格式: [{"content": "...", "metadata": {...}, "score": 0.85}, ...]
    :param top_n: 精排后返回的 Top N 数量，默认使用配置值
    :return: 重排序后的结果列表（与输入格式一致）
    """
    # 守卫条件：未启用 / 无候选文档 → 直接返回
    if not RERANKER_ENABLED:
        return documents
    if RERANKER_PROVIDER == "api" and not RERANKER_API_KEY:
        logger.warning("[Reranker] API Key 未配置，跳过重排序")
        return documents
    if not documents:
        return documents

    top_n = top_n or RERANKER_TOP_N

    # 生成缓存键：查询文本 + 所有的内容哈希（简单拼接前 100 字符）
    doc_contents = [doc["content"] for doc in documents]
    cache_key = hash(query + "".join([c[:100] for c in doc_contents]))
    
    if cache_key in _rerank_cache:
        logger.info(f"[Reranker] 命中缓存，返回重排序结果")
        return _rerank_cache[cache_key][:top_n]

    try:
        url = f"{RERANKER_BASE_URL}/rerank" if RERANKER_PROVIDER == "api" else f"{RERANKER_LOCAL_URL}/rerank"
        headers = {"Content-Type": "application/json"}
        if RERANKER_PROVIDER == "api":
            headers["Authorization"] = f"Bearer {RERANKER_API_KEY}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json={
                    "model": RERANKER_MODEL,
                    "query": query,
                    "documents": doc_contents,
                    "top_n": min(top_n, len(doc_contents)),
                    "return_documents": False,  # 只返回 index + score，节省带宽
                },
            )
            response.raise_for_status()
            data = response.json()

        # 按 relevanceScore 降序排列，映射回原始文档
        ranked_results = sorted(
            data["results"],
            key=lambda x: x["relevanceScore"],
            reverse=True,
        )

        reranked_documents = []
        for r in ranked_results:
            idx = r["index"]
            if 0 <= idx < len(documents):
                reranked_doc = {**documents[idx]}
                reranked_doc["score"] = r["relevanceScore"]  # 用精排分数替换粗排分数
                reranked_documents.append(reranked_doc)

        logger.info(
            f"[Reranker] 精排完成: {len(documents)} 条候选 → {len(reranked_documents)} 条结果"
        )
        
        # 存入缓存
        _rerank_cache[cache_key] = reranked_documents
        return reranked_documents

    except httpx.TimeoutException:
        logger.error("[Reranker] 请求超时，降级返回原始结果")
        return documents
    except httpx.HTTPStatusError as e:
        logger.error(f"[Reranker] API 返回错误 {e.response.status_code}: {e.response.text}")
        return documents
    except Exception as e:
        logger.error(f"[Reranker] 调用异常，降级返回原始结果: {e}")
        return documents


def is_reranker_available() -> bool:
    """检查 Reranker 是否可用（用于前端状态显示）"""
    if not RERANKER_ENABLED:
        return False
    if RERANKER_PROVIDER == "api":
        return bool(RERANKER_API_KEY)
    return bool(RERANKER_LOCAL_URL)
