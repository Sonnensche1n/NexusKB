""" 
BM25 稀疏关键词检索器 
与向量检索互补：向量检索擅长语义匹配，BM25 擅长精确关键词匹配。 
使用 rank_bm25 库实现，无需外部服务。 
""" 

import logging 
import jieba 
from typing import Optional 
from rank_bm25 import BM25Okapi 

logger = logging.getLogger(__name__) 


class BM25Retriever: 
    """ 
    BM25 稀疏检索器 

    工作流程： 
    1. 离线：对所有文档 chunk 进行分词，构建 BM25 索引 
    2. 在线：对 query 分词后，用 BM25 算法计算与每个 chunk 的匹配分数 
    """ 

    def __init__(self): 
        self.bm25: Optional[BM25Okapi] = None 
        self.documents: list[dict] = []  # 保存原始文档信息 
        self.tokenized_corpus: list[list[str]] = [] 

    def build_index(self, documents: list[dict]): 
        """ 
        构建 BM25 索引。 

        :param documents: 文档列表，每项需包含 'content' 字段 
                          格式: [{"content": "...", "metadata": {...}}, ...] 
        """ 
        self.documents = documents 
        self.tokenized_corpus = [] 

        for doc in documents: 
            # 使用 jieba 分词 
            tokens = list(jieba.cut(doc["content"])) 
            # 过滤停用词和单字符 
            tokens = [t for t in tokens if len(t) > 1] 
            self.tokenized_corpus.append(tokens) 

        self.bm25 = BM25Okapi(self.tokenized_corpus) 
        logger.info(f"[BM25] 索引构建完成，共 {len(documents)} 个文档") 

    def search(self, query: str, top_k: int = 60) -> list[dict]: 
        """ 
        BM25 检索。 

        :param query: 查询文本 
        :param top_k: 返回 Top K 结果 
        :return: 检索结果列表，每项包含 content, metadata, score 
        """ 
        if self.bm25 is None or not self.documents: 
            logger.warning("[BM25] 索引未构建，返回空结果") 
            return [] 

        # 对 query 分词 
        query_tokens = list(jieba.cut(query)) 
        query_tokens = [t for t in query_tokens if len(t) > 1] 

        # 计算 BM25 分数 
        scores = self.bm25.get_scores(query_tokens) 

        # 按分数降序排序，取 Top K 
        scored_docs = list(zip(range(len(scores)), scores)) 
        scored_docs.sort(key=lambda x: x[1], reverse=True) 
        top_docs = scored_docs[:top_k] 

        results = [] 
        for idx, score in top_docs: 
            if score > 0:  # 只返回有匹配的结果 
                results.append({ 
                    "content": self.documents[idx]["content"], 
                    "metadata": self.documents[idx].get("metadata", {}), 
                    "score": float(score), 
                    "retrieval_type": "bm25", 
                }) 

        logger.info(f"[BM25] 检索完成，返回 {len(results)} 条结果") 
        return results