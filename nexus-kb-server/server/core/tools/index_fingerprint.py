""" 
文件指纹管理器 
用于实现增量索引：通过 MD5 指纹判断文件是否变更，跳过未变更文件。 
指纹信息存储在 SQLite 中，与现有数据库架构一致。 
""" 

import hashlib 
import logging 
from typing import Optional 
from datetime import datetime 

logger = logging.getLogger(__name__) 


def compute_content_fingerprint(content: str) -> str: 
    """计算文本内容的 MD5 指纹""" 
    return hashlib.md5(content.encode("utf-8")).hexdigest() 


def compute_file_fingerprint(file_path: str) -> Optional[str]: 
    """计算文件的 MD5 指纹""" 
    try: 
        with open(file_path, "rb") as f: 
            return hashlib.md5(f.read()).hexdigest() 
    except Exception as e: 
        logger.error(f"[Fingerprint] 计算文件指纹失败 {file_path}: {e}") 
        return None 


class IndexFingerprintManager: 
    """ 
    增量索引指纹管理器 

    工作流程： 
    1. 文档首次入库时，计算内容 MD5 并存入 fingerprint 表 
    2. 后续索引时，对比当前内容 MD5 与存储的 MD5 
    3. MD5 相同 → 跳过；MD5 不同 → 删除旧 chunks + 重新索引 
    """ 

    def __init__(self, db_session): 
        """ 
        :param db_session: SQLAlchemy session 对象 
        """ 
        self.db = db_session 

    def needs_reindex(self, source_path: str, current_content: str) -> bool: 
        """ 
        判断文档是否需要重新索引。 

        :param source_path: 文档路径/标识 
        :param current_content: 当前文档内容 
        :return: True 需要重新索引，False 可跳过 
        """ 
        current_fingerprint = compute_content_fingerprint(current_content) 

        try: 
            # 查询数据库中的旧指纹 
            from server.model.orm_model.orm_knb import DatasetFingerprint 
            record = self.db.query(DatasetFingerprint).filter( 
                DatasetFingerprint.source_path == source_path 
            ).first() 

            if record is None: 
                # 新文档，需要索引 
                logger.info(f"[Fingerprint] 新文档: {source_path}") 
                return True 

            if record.fingerprint != current_fingerprint: 
                # 内容变更，需要重新索引 
                logger.info(f"[Fingerprint] 内容变更: {source_path}") 
                return True 

            # 指纹一致，跳过 
            logger.debug(f"[Fingerprint] 未变更，跳过: {source_path}") 
            return False 

        except Exception as e: 
            logger.error(f"[Fingerprint] 查询失败，默认重新索引: {e}") 
            return True 

    def update_fingerprint(self, source_path: str, content: str): 
        """ 
        更新文档指纹记录。 

        :param source_path: 文档路径/标识 
        :param content: 文档内容 
        """ 
        fingerprint = compute_content_fingerprint(content) 

        try: 
            from server.model.orm_model.orm_knb import DatasetFingerprint 
            record = self.db.query(DatasetFingerprint).filter( 
                DatasetFingerprint.source_path == source_path 
            ).first() 

            if record: 
                record.fingerprint = fingerprint 
                record.updated_at = datetime.now() 
            else: 
                record = DatasetFingerprint( 
                    source_path=source_path, 
                    fingerprint=fingerprint, 
                    created_at=datetime.now(), 
                    updated_at=datetime.now(), 
                ) 
                self.db.add(record) 

            self.db.commit() 
            logger.info(f"[Fingerprint] 指纹已更新: {source_path}") 

        except Exception as e: 
            self.db.rollback() 
            logger.error(f"[Fingerprint] 更新失败: {e}") 

    def delete_fingerprint(self, source_path: str): 
        """删除文档指纹记录""" 
        try: 
            from server.model.orm_model.orm_knb import DatasetFingerprint 
            self.db.query(DatasetFingerprint).filter( 
                DatasetFingerprint.source_path == source_path 
            ).delete() 
            self.db.commit() 
        except Exception as e: 
            self.db.rollback() 
            logger.error(f"[Fingerprint] 删除失败: {e}")