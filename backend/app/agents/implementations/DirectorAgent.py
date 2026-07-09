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

🔴【主题锁定】生成主题：「{topic}」
🔴 你接下来的所有视频脚本必须且只能围绕「{topic}」制作。
🔴 每个场景的标题、视觉描述、旁白都必须直接涉及「{topic}」。
🔴 绝对禁止制作与「{topic}」无关的视频脚本。

上游已生成的教学内容：{context}

请严格以JSON格式返回（不要包含任何其他文字，不要markdown代码块标记）：
{{
  "scenes": [
    {{
      "scene_number": 1,
      "title": "与「{topic}」相关的场景标题",
      "visual": "画面描述（与{topic}直接相关）",
      "voiceover": "旁白内容（100-200字，口语化，涉及{topic}）",
      "duration_seconds": 45,
      "resources": [
        {{
          "type": "video",
          "title": "与{topic}相关的教学视频标题",
          "description": "视频简介（与{topic}相关）",
          "thumbnail": "https://img.youtube.com/vi/xxxxx/maxresdefault.jpg",
          "url": "https://www.youtube.com/results?search_query={topic}",
          "duration": "10:00",
          "platform": "YouTube"
        }}
      ]
    }}
  ]
}}

要求：
- 至少3个场景，从入门到深入，逻辑连贯
- 所有场景标题和旁白必须涉及「{topic}」
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
            if parsed and isinstance(parsed.get("scenes"), list) and len(parsed["scenes"]) > 0:
                scenes = parsed["scenes"]
                for i, s in enumerate(scenes):
                    if "scene_number" not in s:
                        s["scene_number"] = i + 1
                    if "duration_seconds" not in s:
                        s["duration_seconds"] = 45
                    if "resources" not in s:
                        s["resources"] = []
                content = {"scenes": scenes}
            else:
                logger.warning("DirectorAgent: output validation failed (missing scenes array), using fallback")
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
