""" 
混合检索 + RRF 融合排序 
将稠密向量检索和 BM25 稀疏检索的结果通过 RRF 算法融合。 

RRF (Reciprocal Rank Fusion) 原理： 
  对于每条文档，计算 RRF_score = Σ 1/(k + rank_i) 
  其中 k 是常数（通常为 60），rank_i 是该文档在第 i 路检索中的排名。 
  最终按 RRF_score 降序排列。 

优势： 
- 不依赖各路检索分数的绝对值（向量距离和 BM25 分数量纲不同） 
- 只看排名，天然归一化 
""" 

import logging 
from typing import Optional 

logger = logging.getLogger(__name__) 

# RRF 常数，控制排名靠后的文档衰减速度，60 是经典值 
RRF_K = 60 


def rrf_fusion( 
    result_lists: list[list[dict]], 
    top_k: int = 60, 
    rrf_k: int = RRF_K, 
    content_key: str = "content", 
) -> list[dict]: 
    """ 
    RRF 融合多路检索结果。 

    :param result_lists: 多路检索结果，每路是 list[dict]，每个 dict 需包含 content_key 字段 
    :param top_k: 融合后返回 Top K 
    :param rrf_k: RRF 常数 
    :param content_key: 用于去重的内容字段名 
    :return: 融合排序后的结果列表 
    """ 
    # 用 content 作为文档唯一标识（去重用） 
    doc_scores = {}   # content -> rrf_score 
    doc_info = {}     # content -> 完整文档信息 

    for result_list in result_lists: 
        for rank, doc in enumerate(result_list): 
            content = doc.get(content_key, "") 
            if not content: 
                continue 

            # RRF 分数累加 
            rrf_score = 1.0 / (rrf_k + rank + 1) 

            if content not in doc_scores: 
                doc_scores[content] = 0.0 
                doc_info[content] = doc 

            doc_scores[content] += rrf_score 

    # 按 RRF 总分降序排列 
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True) 

    results = [] 
    for content, rrf_score in sorted_docs[:top_k]: 
        doc = {**doc_info[content]} 
        doc["rrf_score"] = rrf_score 
        doc["retrieval_type"] = "hybrid" 
        results.append(doc) 

    logger.info( 
        f"[HybridSearch] RRF 融合完成: " 
        f"{sum(len(rl) for rl in result_lists)} 条候选 → {len(results)} 条结果" 
    ) 
    return results