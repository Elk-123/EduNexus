"""
Examiner Agent - 考官智能体
负责生成测验题目和评估材料（v1 兼容格式）
"""
import json
import logging
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils
from ..fallback_data import get_fallback_content

logger = logging.getLogger("edunexus.agents")


class ExaminerAgent(BaseAgent):
    """考官智能体 — 生成测验与评估材料（v1 兼容格式）"""

    PROMPT_TEMPLATE = """
你是一个经验丰富的教育评估专家，专门负责设计高质量的测验题目。

⚠️ 核心约束：你必须且只能围绕下面这个主题和上游教学内容来出题！

生成主题：{topic}

上游教授和架构师生成的教学内容：{context}

请严格以JSON格式返回（不要包含任何其他文字）：
```json
{{
  "questions": [
    {{
      "question": "基于上述主题的测验题目",
      "options": ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"],
      "answer": 0,
      "explanation": "详细解析"
    }}
  ]
}}
```

要求：
- 所有题目必须与上述生成主题直接相关
- 至少3道选择题，覆盖教学内容中的核心知识点
- answer 必须是 0-3 的整数（0=A, 1=B, 2=C, 3=D），不是字母！
- 每个选项以 "A. "、"B. "、"C. "、"D. " 开头
"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                id="examiner",
                name="考官智能体",
                role="试题设计专家",
                capabilities=["题库生成", "评估设计", "测试策划"],
                timeout=30000
            )
        super().__init__(config)

    def execute(self, context: AgentContext) -> AgentExecutionResult:
        start_time = datetime.now()
        try:
            prompt_template = LangChainUtils.create_prompt_template(self.PROMPT_TEMPLATE)
            llm_response = LangChainUtils.execute_chain(prompt_template, {
                "topic": context.topic,
                "context": json.dumps(context.context or {}, ensure_ascii=False, indent=2),
            })

            parsed = LangChainUtils.try_parse_json(llm_response)
            if parsed:
                questions = parsed.get("questions", [])
                # 规范化：确保 answer 是整数
                for q in questions:
                    ans = q.get("answer", 0)
                    if isinstance(ans, str):
                        # 字母 → 数字映射
                        ans_map = {"a": 0, "A": 0, "b": 1, "B": 1, "c": 2, "C": 2, "d": 3, "D": 3}
                        q["answer"] = ans_map.get(ans.strip(), 0)
                    elif isinstance(ans, int):
                        q["answer"] = ans
                    else:
                        q["answer"] = 0
                    # 确保 explanation 存在
                    if "explanation" not in q:
                        q["explanation"] = "该选项是正确答案。"
                content = {"questions": questions}
            else:
                logger.warning("ExaminerAgent: LLM returned non-JSON, using fallback")
                content = get_fallback_content("examiner", context.topic)

            self._record_success(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=content,
                    type="quiz",
                    timestamp=datetime.now(),
                    log=[f"成功生成测验材料: {context.topic}"]
                ),
                duration=duration
            )
        except Exception as error:
            logger.warning("ExaminerAgent LLM call failed: %s — using fallback", error)
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            fallback_content = get_fallback_content("examiner", context.topic)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=fallback_content,
                    type="quiz",
                    timestamp=datetime.now(),
                    log=[f"使用 fallback 数据生成测验: {context.topic}"]
                ),
                duration=duration
            )
