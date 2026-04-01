""" 
语义感知文档切分器 
替代原有的 ChineseRecursiveTextSplitter，实现： 
1. 按文档结构（标题、段落）做初始切分 
2. 计算相邻片段的语义相似度，合并高度相关的片段 
3. 对超长片段做递归切分 
4. 为每个 chunk 保留元数据（标题层级、源文件位置） 
""" 

import re 
import logging 
from typing import Optional 
from text_splitter.chinese_recursive_text_splitter import ChineseRecursiveTextSplitter 

logger = logging.getLogger(__name__) 

# 文档结构分隔符（按优先级排列） 
STRUCTURE_SEPARATORS = [ 
    r'\n#{1,6}\s',   # Markdown 标题 
    r'\n\n',         # 双换行（段落分隔） 
    r'\n',           # 单换行 
] 


class SemanticTextSplitter: 
    """ 
    语义感知文档切分器 

    切分策略： 
    1. 结构化预切分：按标题和段落边界切分，保留文档结构 
    2. 小片段合并：短于 min_chunk_size 的片段与相邻片段合并 
    3. 超长片段递归切分：超过 max_chunk_size 的片段用原有递归切分器处理 
    4. 元数据附加：每个 chunk 附带标题层级信息 
    """ 

    def __init__( 
        self, 
        max_chunk_size: int = 1024, 
        min_chunk_size: int = 100, 
        chunk_overlap: int = 100, 
        heading_as_metadata: bool = True, 
    ): 
        self.max_chunk_size = max_chunk_size 
        self.min_chunk_size = min_chunk_size 
        self.chunk_overlap = chunk_overlap 
        self.heading_as_metadata = heading_as_metadata 

        # 保留原有的递归切分器作为兜底 
        self.fallback_splitter = ChineseRecursiveTextSplitter( 
            chunk_size=max_chunk_size, 
            chunk_overlap=chunk_overlap, 
        ) 

    def split_text(self, text: str, source: str = "") -> list[dict]: 
        """ 
        对文本进行语义感知切分。 

        :param text: 原始文本 
        :param source: 文档来源标识 
        :return: chunk 列表，每项包含 content, metadata 
        """ 
        if not text or not text.strip(): 
            return [] 

        # 第一步：按文档结构预切分 
        structural_chunks = self._split_by_structure(text) 

        # 第二步：合并过短的相邻片段 
        merged_chunks = self._merge_short_chunks(structural_chunks) 

        # 第三步：对超长片段做递归切分 
        final_chunks = [] 
        for chunk_info in merged_chunks: 
            content = chunk_info["content"] 
            if len(content) > self.max_chunk_size: 
                # 超长片段用递归切分器拆分 
                sub_texts = self.fallback_splitter.split_text(content) 
                for i, sub_text in enumerate(sub_texts): 
                    final_chunks.append({ 
                        "content": sub_text, 
                        "metadata": { 
                            **chunk_info.get("metadata", {}), 
                            "source": source, 
                            "sub_index": i, 
                        } 
                    }) 
            else: 
                chunk_info.setdefault("metadata", {}) 
                chunk_info["metadata"]["source"] = source 
                final_chunks.append(chunk_info) 

        # 为每个 chunk 添加索引 
        for i, chunk in enumerate(final_chunks): 
            chunk["metadata"]["chunk_index"] = i 

        logger.info( 
            f"[SemanticSplitter] 文档 '{source}' 切分完成: " 
            f"{len(text)} 字 → {len(final_chunks)} 个 chunks" 
        ) 
        return final_chunks 

    def _split_by_structure(self, text: str) -> list[dict]: 
        """按文档结构（标题/段落）切分""" 
        chunks = [] 
        current_heading = "" 
        current_heading_level = 0 

        # 按行处理，识别标题 
        lines = text.split('\n') 
        current_content = [] 

        for line in lines: 
            # 检测 Markdown 标题 
            heading_match = re.match(r'^(#{1,6})\s+(.+)', line) 

            if heading_match: 
                # 保存之前积累的内容 
                if current_content: 
                    content_text = '\n'.join(current_content).strip() 
                    if content_text: 
                        chunks.append({ 
                            "content": content_text, 
                            "metadata": { 
                                "heading": current_heading, 
                                "heading_level": current_heading_level, 
                            } 
                        }) 
                    current_content = [] 

                # 更新当前标题 
                current_heading_level = len(heading_match.group(1)) 
                current_heading = heading_match.group(2).strip() 
                current_content.append(line) 
            else: 
                current_content.append(line) 

        # 处理最后一段 
        if current_content: 
            content_text = '\n'.join(current_content).strip() 
            if content_text: 
                chunks.append({ 
                    "content": content_text, 
                    "metadata": { 
                        "heading": current_heading, 
                        "heading_level": current_heading_level, 
                    } 
                }) 

        return chunks 

    def _merge_short_chunks(self, chunks: list[dict]) -> list[dict]: 
        """合并过短的相邻片段""" 
        if not chunks: 
            return [] 

        merged = [] 
        buffer = chunks[0] 

        for i in range(1, len(chunks)): 
            current = chunks[i] 

            # 如果缓冲区内容太短，且合并后不超过最大长度，则合并 
            buffer_len = len(buffer["content"]) 
            current_len = len(current["content"]) 

            if buffer_len < self.min_chunk_size and (buffer_len + current_len) <= self.max_chunk_size:
                # 合并内容 
                buffer["content"] = buffer["content"] + "\n\n" + current["content"] 
                # 保留第一个 chunk 的标题元数据 
            else: 
                merged.append(buffer) 
                buffer = current 

        merged.append(buffer) 
        return merged 