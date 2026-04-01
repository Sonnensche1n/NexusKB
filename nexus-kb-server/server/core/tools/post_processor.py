""" 
检索结果后处理器 
在 Reranker 精排之后、Prompt 组装之前执行： 
1. 内容去重：消除 overlap 切分造成的重复内容 
2. 文档顺序重排：按文档原始位置排序，让 LLM 读到连贯的上下文 
""" 

import logging 
from difflib import SequenceMatcher 

logger = logging.getLogger(__name__) 


def deduplicate_chunks( 
    chunks: list[dict], 
    similarity_threshold: float = 0.85, 
    content_key: str = "content", 
) -> list[dict]: 
    """ 
    基于文本相似度去重。 

    当两个 chunk 的文本相似度超过阈值时，保留分数更高的那个。 
    使用 SequenceMatcher 而非 Embedding，避免额外 API 调用。 

    :param chunks: Reranker 精排后的结果列表 
    :param similarity_threshold: 相似度阈值，超过则视为重复 
    :param content_key: 内容字段名 
    :return: 去重后的结果列表 
    """ 
    if len(chunks) <= 1: 
        return chunks 

    deduplicated = [] 
    removed_indices = set() 

    for i in range(len(chunks)): 
        if i in removed_indices: 
            continue 

        is_duplicate = False 
        for j in range(len(deduplicated)): 
            similarity = SequenceMatcher( 
                None, 
                chunks[i][content_key], 
                deduplicated[j][content_key], 
            ).ratio() 

            if similarity > similarity_threshold: 
                is_duplicate = True 
                # 保留分数更高的 
                if chunks[i].get("score", 0) > deduplicated[j].get("score", 0): 
                    deduplicated[j] = chunks[i] 
                break 

        if not is_duplicate: 
            deduplicated.append(chunks[i]) 

    removed_count = len(chunks) - len(deduplicated) 
    if removed_count > 0: 
        logger.info(f"[PostProcessor] 去重: {len(chunks)} → {len(deduplicated)}（移除 {removed_count} 条重复）") 

    return deduplicated 


def reorder_by_document_position( 
    chunks: list[dict], 
) -> list[dict]: 
    """ 
    按文档原始位置重新排序。 

    Reranker 按相关度排序，但 LLM 更擅长处理连续、有逻辑的文本。 
    将同一文档的 chunks 按原始顺序排列，不同文档按首个 chunk 的相关度排列。 

    :param chunks: 去重后的结果列表 
    :return: 按文档位置排序的结果列表 
    """ 
    if len(chunks) <= 1: 
        return chunks 

    # 按 (source 文件名, chunk_index) 排序 
    def sort_key(chunk): 
        metadata = chunk.get("metadata", {}) 
        source = metadata.get("source", "") 
        chunk_index = metadata.get("chunk_index", 0) 
        return (source, chunk_index) 

    reordered = sorted(chunks, key=sort_key) 
    return reordered 


def post_process_results( 
    chunks: list[dict], 
    deduplicate: bool = True, 
    reorder: bool = True, 
    similarity_threshold: float = 0.85, 
) -> list[dict]: 
    """ 
    完整的后处理流水线。 

    :param chunks: Reranker 精排后的结果 
    :param deduplicate: 是否去重 
    :param reorder: 是否按文档位置重排 
    :param similarity_threshold: 去重相似度阈值 
    :return: 后处理后的结果 
    """ 
    result = chunks 

    if deduplicate: 
        result = deduplicate_chunks(result, similarity_threshold) 

    if reorder: 
        result = reorder_by_document_position(result) 

    return result