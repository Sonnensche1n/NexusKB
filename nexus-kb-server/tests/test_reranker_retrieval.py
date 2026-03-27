import os
import sys

# 将上一级目录加入到 path 中，以便能正确引用 server 和 config 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.core.tools.ask_to_llm import get_question_prompts_and_sources
from server.model.entity_knb import ReposSetting
import config.llm as llm_config
import time

def test_retrieval(query: str, repos_id: str):
    # 模拟默认配置
    setting = ReposSetting()
    setting.topK = 20
    setting.maxCtx = 5
    setting.smlrTrval = 1.0

    print(f"\n{'='*50}")
    print(f"测试查询: {query}")
    print(f"当前 RERANKER_ENABLED 状态: {llm_config.RERANKER_ENABLED}")
    print(f"{'='*50}")

    start_time = time.time()
    
    try:
        prompts, sources = get_question_prompts_and_sources(repos_id, query, setting)
        elapsed = time.time() - start_time
        
        print(f"检索耗时: {elapsed:.2f} 秒")
        if sources:
            print(f"共召回并保留了 {len(sources)} 个最终文档片段")
            for i, source in enumerate(sources):
                print(f"\n--- 片段 {i+1} [score: {source['score']:.4f}] ---")
                # 只打印前150个字符避免刷屏
                content_preview = source['content'][:150].replace('\n', ' ')
                print(f"{content_preview}...")
        else:
            print("未召回到相关文档片段。请检查该 repos_id 是否有建立向量索引。")
            
    except Exception as e:
        print(f"检索过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 请替换为你的实际知识库 reposId，可以在数据库或者管理界面中获取
    TEST_REPOS_ID = "test_repos_id" 
    
    query = "帮我总结一下文档中的核心观点"
    
    # 1. 开启 Reranker 测试
    print("\n[阶段 1] 开启 Reranker 进行测试...")
    llm_config.RERANKER_ENABLED = True
    test_retrieval(query, TEST_REPOS_ID)
    
    # 2. 关闭 Reranker 测试
    print("\n[阶段 2] 关闭 Reranker 进行对比测试...")
    llm_config.RERANKER_ENABLED = False
    test_retrieval(query, TEST_REPOS_ID)
    
    print("\n说明: 要运行此测试，请将 TEST_REPOS_ID 替换为你真实的知识库ID。")