"""
Agent 执行器
实现简化版的 Planner-Executor 模式：
1. Planner：分析用户问题，拆解为执行步骤
2. Executor：逐步执行每个步骤（调用工具）
3. Synthesizer：综合所有结果生成最终回答
"""

import json
import logging
from typing import Generator

logger = logging.getLogger(__name__)

PLANNER_PROMPT = """你是一个问题分析器。分析用户的问题，判断是否需要多步骤处理。

如果问题简单（只需要一次检索即可回答），返回：
{"mode": "simple", "reason": "问题简单，直接检索即可"}

如果问题复杂（需要多次检索、对比、综合），返回包含具体步骤的计划：
{"mode": "complex", "steps": [
    {"action": "search", "query": "检索查询1", "purpose": "目的说明"},
    {"action": "search", "query": "检索查询2", "purpose": "目的说明"},
    {"action": "summarize", "purpose": "综合以上结果回答"}
], "reason": "需要多步骤处理的原因"}

只返回JSON，不要其他内容。

用户问题：{question}
"""

SYNTHESIZER_PROMPT = """基于以下检索结果，综合回答用户的问题。

用户问题：{question}

检索结果：
{evidence}

请给出全面、有条理的回答。引用具体的来源信息。如果某些方面没有找到相关信息，请说明。
"""


class AgentExecutor:
  """简化版多步 Agent 执行器。"""

  def __init__(self, llm_client, repos_id: str, setting):
    self.client = llm_client
    self.repos_id = repos_id
    self.setting = setting

  def plan(self, question: str) -> dict:
    """分析问题并生成执行计划。"""
    prompt = PLANNER_PROMPT.format(question=question)
    try:
      response = self.client.chat_with_tools(
        messages=[{"role": "user", "content": prompt}],
        tools=None,
      )
      content = (response.choices[0].message.content or "").strip()
      if "```json" in content:
        content = content.split("```json", 1)[1].split("```", 1)[0].strip()
      elif "```" in content:
        content = content.split("```", 1)[1].split("```", 1)[0].strip()
      return json.loads(content)
    except Exception as e:
      logger.error(f"[Agent] 规划失败: {e}")
      return {"mode": "simple", "reason": "规划失败，降级为简单模式"}

  def execute_steps(self, question: str, plan: dict, chat_message=None) -> Generator:
    """执行多步骤计划并流式返回过程与结论。"""
    from server.core.tools.message_tools import message_chunk_to_json, message_quote_to_json
    from server.core.tools.tool_registry import tool_registry

    if plan.get("mode") != "complex":
      return

    steps = plan.get("steps", [])
    evidence = []
    collected_quotes = []

    yield message_chunk_to_json(f"📋 正在执行多步骤分析（共 {len(steps)} 步）...\n\n")

    for i, step in enumerate(steps):
      action = step.get("action", "search")
      query = step.get("query", question)
      purpose = step.get("purpose", "")

      yield message_chunk_to_json(f"**步骤 {i + 1}/{len(steps)}**：{purpose}\n")

      if action == "search":
        result = tool_registry.execute("search_knowledge_base", {
          "query": query,
          "repos_id": self.repos_id,
          "top_k": self.setting.topK if hasattr(self.setting, "topK") else 5,
        })
        try:
          result_data = json.loads(result)
          docs = result_data.get("results", [])
          evidence.append({
            "step": i + 1,
            "purpose": purpose,
            "query": query,
            "docs": docs,
          })
          for doc in docs:
            collected_quotes.append({
              "dtsetId": doc.get("dtsetId", ""),
              "dtsetNm": doc.get("dtsetNm", ""),
              "fileNm": doc.get("fileNm", doc.get("source", "")),
              "fileTyp": doc.get("fileTyp", ""),
              "score": doc.get("score", 0),
              "content": doc.get("content", ""),
            })
          yield message_chunk_to_json(f"  -> 找到 {len(docs)} 个相关片段\n\n")
        except Exception:
          evidence.append({"step": i + 1, "purpose": purpose, "docs": []})
          yield message_chunk_to_json("  -> 未找到相关信息\n\n")

      elif action == "summarize":
        # 汇总步骤在最后统一处理
        yield message_chunk_to_json("  -> 正在准备综合分析\n\n")

    yield message_chunk_to_json("---\n\n**综合分析结果：**\n\n")

    evidence_text = ""
    for ev in evidence:
      evidence_text += f"\n--- 步骤{ev['step']}: {ev.get('purpose', '')} ---\n"
      for doc in ev.get("docs", []):
        evidence_text += f"[来源: {doc.get('source', '未知')}] {doc.get('content', '')}\n"

    prompt = SYNTHESIZER_PROMPT.format(question=question, evidence=evidence_text)
    try:
      stream = self.client.chat_stream(messages=[{"role": "user", "content": prompt}])
      for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
          yield message_chunk_to_json(chunk.choices[0].delta.content)
    except Exception as e:
      logger.error(f"[Agent] 综合生成失败: {e}")
      yield message_chunk_to_json(f"\n\n综合分析失败: {str(e)}")

    yield message_quote_to_json(
      mesgId=getattr(chat_message, "mesgId", ""),
      chatId=getattr(chat_message, "chatId", ""),
      reposId=self.repos_id,
      quotes=collected_quotes[:10],
    )
