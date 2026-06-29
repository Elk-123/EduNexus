"""
Examiner Agent - 考官智能体
负责生成测验题目和评估材料
"""
import json
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils


class ExaminerAgent(BaseAgent):
    """考官智能体 — 生成测验与评估材料"""

    PROMPT_TEMPLATE = """
你是一个经验丰富的教育评估专家，专门负责设计高质量的测验题目。
请根据以下信息生成一套评估材料：

主题: {topic}
参考上下文（上游Agent输出的教学内容）: {context}

请严格以JSON格式返回（不要包含任何其他文字）：
```json
{
  "questions": [
    {
      "question": "题目内容",
      "options": ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"],
      "answer": "B",
      "explanation": "解析说明"
    }
  ],
  "essayQuestions": [
    {
      "question": "简答题内容",
      "maxPoints": 10
    }
  ]
}
```

要求：至少3道选择题和2道简答题，难度适中，涵盖核心知识点。
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
                content = {
                    "questions": parsed.get("questions", []),
                    "essayQuestions": parsed.get("essayQuestions", []),
                }
            else:
                content = {
                    "questions": [],
                    "essayQuestions": [{"question": llm_response.strip(), "maxPoints": 10}],
                }

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
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.ERROR,
                error=str(error),
                duration=duration
            )
