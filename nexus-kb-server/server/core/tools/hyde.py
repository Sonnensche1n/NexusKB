""" 
HyDE (Hypothetical Document Embeddings) 查询扩展 
原理：让 LLM 先生成一段假设性回答，将其与原始 query 拼接后做 Embedding， 
     使查询向量更接近真实文档的向量分布，提升召回率。 
适用场景：短 query、模糊 query、专业术语 query 
""" 

import logging 
from typing import Optional 

logger = logging.getLogger(__name__) 

# HyDE Prompt 模板 
HYDE_PROMPT_TEMPLATE = """请根据以下问题，写一段可能的回答（100-200字）。 
不需要保证准确性，只需要包含相关的关键词和概念，用中文回答。 

问题：{query} 

假设性回答：""" 


async def generate_hypothetical_document( 
    query: str, 
    llm_client, 
    enabled: bool = True, 
    min_query_length: int = 2, 
    max_query_length: int = 200, 
) -> str: 
    """ 
    生成假设性文档并与原始 query 拼接。 

    :param query: 用户原始查询 
    :param llm_client: LLM 客户端实例（需有 apredict/predict 方法） 
    :param enabled: 是否启用 HyDE 
    :param min_query_length: query 太短才启用（低于此长度必然启用） 
    :param max_query_length: query 超过此长度跳过（已足够丰富） 
    :return: 增强后的 query（原始 query + 假设回答） 
    """ 
    if not enabled: 
        return query 

    # query 已经很长（比如用户粘贴了一大段），跳过 HyDE 
    if len(query) > max_query_length: 
        logger.info(f"[HyDE] Query 长度 {len(query)} 超过阈值，跳过扩展") 
        return query 

    try: 
        prompt = HYDE_PROMPT_TEMPLATE.format(query=query) 

        # 兼容同步/异步 LLM 客户端 
        if hasattr(llm_client, 'apredict'): 
            hypothetical_doc = await llm_client.apredict(prompt) 
        elif hasattr(llm_client, 'predict'): 
            hypothetical_doc = llm_client.predict(prompt) 
        elif hasattr(llm_client, 'invoke'): 
            result = llm_client.invoke(prompt) 
            hypothetical_doc = result.content if hasattr(result, 'content') else str(result) 
        else: 
            logger.warning("[HyDE] LLM 客户端不支持 predict/invoke 方法，跳过") 
            return query 

        # 拼接：原始 query + 假设回答 
        enhanced_query = f"{query}\n{hypothetical_doc.strip()}" 
        logger.info(f"[HyDE] 查询扩展完成，原始长度 {len(query)} → 扩展后 {len(enhanced_query)}") 
        return enhanced_query 

    except Exception as e: 
        logger.error(f"[HyDE] 生成失败，降级使用原始 query: {e}") 
        return query