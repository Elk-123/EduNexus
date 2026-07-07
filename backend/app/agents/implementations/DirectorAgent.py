"""
Director Agent - 导演智能体
负责生成视频脚本和多媒体内容（v1 兼容格式）
"""
import json
import logging
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils
from ..fallback_data import get_fallback_content

logger = logging.getLogger("edunexus.agents")


class DirectorAgent(BaseAgent):
    """导演智能体 — 生成教育视频脚本（v1 兼容格式）"""

    PROMPT_TEMPLATE = """
你是一个专业的教育视频制作人，擅长将复杂概念转化为易于理解的视频内容。

⚠️ 核心约束：你必须且只能围绕下面这个主题制作视频脚本！

生成主题：{topic}

上游已生成的教学内容：{context}

请严格以JSON格式返回（不要包含任何其他文字）：
```json
{{
  "scenes": [
    {{
      "scene_number": 1,
      "title": "场景标题（与上述主题相关）",
      "visual": "视觉描述",
      "voiceover": "旁白内容（100-200字，口语化）",
      "duration_seconds": 45,
      "resources": [
        {{
          "type": "video",
          "title": "相关视频标题",
          "description": "视频简介",
          "thumbnail": "https://img.youtube.com/vi/xxxxx/maxresdefault.jpg",
          "url": "https://www.youtube.com/results?search_query=关键词",
          "duration": "10:00",
          "platform": "YouTube"
        }}
      ]
    }}
  ]
}}
```

要求：
- 所有场景必须围绕上述生成主题，不可偏离
- 至少3个场景，从入门到深入，逻辑连贯
- 每个场景必须包含至少1个 resources 条目
- 旁白要口语化、生动有趣
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
                scenes = parsed.get("scenes", [])
                # 确保每个场景有 scene_number
                for i, s in enumerate(scenes):
                    if "scene_number" not in s:
                        s["scene_number"] = i + 1
                    if "duration_seconds" not in s:
                        s["duration_seconds"] = 45
                    if "resources" not in s:
                        s["resources"] = []
                content = {"scenes": scenes}
            else:
                logger.warning("DirectorAgent: LLM returned non-JSON, using fallback")
                content = get_fallback_content("director", context.topic)

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
            logger.warning("DirectorAgent LLM call failed: %s — using fallback", error)
            self._record_failure(context.topic)
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            fallback_content = get_fallback_content("director", context.topic)
            return AgentExecutionResult(
                agent_id=self.config.id,
                status=AgentStatus.SUCCESS,
                result=AgentResult(
                    content=fallback_content,
                    type="video_script",
                    timestamp=datetime.now(),
                    log=[f"使用 fallback 数据生成视频脚本: {context.topic}"]
                ),
                duration=duration
            )
