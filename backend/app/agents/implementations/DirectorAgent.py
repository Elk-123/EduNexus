"""
Director Agent - 导演智能体
负责生成视频脚本和多媒体内容
"""
import json
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils


class DirectorAgent(BaseAgent):
    """导演智能体 — 生成教育视频脚本"""

    PROMPT_TEMPLATE = """
你是一个专业的教育视频制作人，擅长将复杂概念转化为易于理解的视频内容。
请根据以下信息生成一个视频脚本：

主题: {topic}
参考上下文（上游Agent输出的教学内容）: {context}

请严格以JSON格式返回（不要包含任何其他文字）：
```json
{
  "scenes": [
    {
      "scene_number": 1,
      "title": "场景标题",
      "visual": "视觉描述（具体生动的画面描述）",
      "voiceover": "旁白内容（通俗易懂的讲解）",
      "duration_seconds": 30
    }
  ],
  "total_duration": 150
}
```

要求：至少3个场景，场景之间逻辑连贯，适合教育类视频制作。
"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                id="director",
                name="导演智能体",
                role="教育视频制作人",
                capabilities=["视频脚本创作", "多媒体内容设计", "故事板构建"],
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
                    "scenes": parsed.get("scenes", []),
                    "total_duration": parsed.get("total_duration", 0),
                }
            else:
                content = {
                    "scenes": [{
                        "scene_number": 1,
                        "title": f"关于{context.topic}",
                        "visual": "教育动画展示",
                        "voiceover": llm_response.strip(),
                        "duration_seconds": 60
                    }],
                    "total_duration": 60,
                }

            self._record_success(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=content,
                    type="video_script",
                    timestamp=datetime.now(),
                    log=[f"成功生成视频脚本: {context.topic}"]
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
