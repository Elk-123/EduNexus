"""
Hacker Agent - 极客智能体
负责生成代码示例和编程练习（v1 兼容格式）
"""
import json
import logging
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils
from ..fallback_data import get_fallback_content

logger = logging.getLogger("edunexus.agents")


class HackerAgent(BaseAgent):
    """极客智能体 — 生成代码示例与编程练习（v1 兼容格式）"""

    PROMPT_TEMPLATE = """
你是一个经验丰富的程序员和教育专家。你的唯一任务是：为「{topic}」编写Python代码示例。

🔴🔴🔴 致命规则：你的代码必须100%围绕「{topic}」。不允许写任何与「{topic}」无关的代码。 🔴🔴🔴

举例说明（严格遵守）：
- 如果主题是「Transformer注意力机制」→ 代码必须实现注意力计算、QKV、softmax等
- 如果主题是「二分查找」→ 代码必须实现二分查找算法
- 如果主题是「线性回归」→ 代码必须实现梯度下降拟合线性模型
- 如果主题是「排序算法」→ 代码必须实现排序算法（冒泡、快排等）
- 不论主题是什么，都必须围绕它写代码。禁止写print('hello world')这种无关代码。

以下是对「{topic}」的教学内容摘要，供你参考（只关注与{topic}直接相关的内容）：
{context}

请严格以JSON格式返回（不要包含任何其他文字，不要markdown代码块标记）：
{{
  "title": "【必须包含{topic}完整关键词】的代码实验标题",
  "description": "说明这段代码如何演示{topic}的核心概念（50-100字）",
  "code": "完整的可运行Python代码（含import、中文注释、主逻辑，至少20行，必须与{topic}直接相关）",
  "expected_output": "运行这段代码后的预期输出结果",
  "exercises": [
    "练习1：修改代码中的参数，观察{topic}的行为变化",
    "练习2：用另一种方法实现{topic}的核心功能",
    "练习3：给{topic}的代码添加新功能"
  ]
}}

再次强调：
- title、description、code、exercises 每一项都必须直接提及或演示「{topic}」
- 禁止写通用示例代码（如 print('hello')、简单的加减乘除等与{topic}无关的代码）
- 代码注释必须用中文，详细解释每步与{topic}的关系
"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                id="hacker",
                name="极客智能体",
                role="编程教育专家",
                capabilities=["代码生成", "编程教学", "实践练习"],
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

            # 验证：parsed 非空 + code 存在且足够长 + title 包含 topic 关键词
            if parsed is not None:
                code = parsed.get("code", "")
                title = parsed.get("title", "")
                code_ok = isinstance(code, str) and len(code) > 50
                title_ok = isinstance(title, str) and any(
                    kw in title for kw in context.topic.split() if len(kw) >= 2
                )
            else:
                code_ok = False
                title_ok = False

            if parsed is not None and code_ok and title_ok:
                exercises = parsed.get("exercises", [])
                normalized_exercises = []
                for ex in exercises:
                    if isinstance(ex, str):
                        normalized_exercises.append(ex)
                    elif isinstance(ex, dict):
                        parts = []
                        if ex.get("title"):
                            parts.append(ex["title"])
                        if ex.get("description"):
                            parts.append(ex["description"])
                        if ex.get("requirement"):
                            parts.append(f"要求: {ex['requirement']}")
                        normalized_exercises.append(" — ".join(parts) if parts else str(ex))
                    else:
                        normalized_exercises.append(str(ex))

                content = {
                    "title": parsed["title"],
                    "description": parsed.get("description", ""),
                    "code": parsed["code"],
                    "expected_output": parsed.get("expected_output", ""),
                    "exercises": normalized_exercises if normalized_exercises else [
                        f"修改代码中的参数，观察{context.topic}的行为变化",
                        f"尝试用另一种方法实现{context.topic}的相同功能",
                    ],
                }
            else:
                logger.warning("HackerAgent: output validation failed (missing code or wrong topic), using fallback")
                content = get_fallback_content("hacker", context.topic)

            self._record_success(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=content,
                    type="code",
                    timestamp=datetime.now(),
                    log=[f"成功生成代码内容: {context.topic}"]
                ),
                duration=duration
            )
        except Exception as error:
            logger.warning("HackerAgent LLM call failed: %s — using fallback", error)
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            fallback_content = get_fallback_content("hacker", context.topic)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=fallback_content,
                    type="code",
                    timestamp=datetime.now(),
                    log=[f"使用 fallback 数据生成代码: {context.topic}"]
                ),
                duration=duration
            )
