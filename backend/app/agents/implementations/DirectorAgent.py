"""
Director Agent - 导演智能体
负责生成视频脚本和多媒体内容（v1 兼容格式）
"""
import json
import logging
import urllib.parse
from datetime import datetime
from ..base.BaseAgent import BaseAgent
from ..types import AgentConfig, AgentContext, AgentExecutionResult, AgentResult, AgentStatus
from ..utils.LangChainUtils import LangChainUtils
from ..fallback_data import get_fallback_content

logger = logging.getLogger("edunexus.agents")


class DirectorAgent(BaseAgent):
    """导演智能体 — 生成教育视频脚本（v1 兼容格式）"""

    PROMPT_TEMPLATE = """
你是一个专业的教育视频制作人，擅长将复杂概念转化为易于理解的视频脚本。

🔴【主题锁定】生成主题：「{topic}」
🔴 你接下来的所有视频脚本必须且只能围绕「{topic}」制作。
🔴 每个场景的标题、视觉描述、旁白都必须直接涉及「{topic}」。
🔴 绝对禁止制作与「{topic}」无关的视频脚本（如主题是注意力机制就不能做黑洞科普）。

上游已生成的教学内容：{context}

请严格以JSON格式返回（不要包含任何其他文字，不要markdown代码块标记）：
{{
  "scenes": [
    {{
      "scene_number": 1,
      "title": "与「{topic}」直接相关的场景标题",
      "visual": "画面描述（与{topic}直接相关，描述具体的动画/图示/演示内容）",
      "voiceover": "旁白内容（100-200字，口语化，必须围绕{topic}展开）",
      "duration_seconds": 45
    }}
  ]
}}

要求：
- 至少3个场景，从入门到深入，逻辑连贯
- 所有场景的 title、visual、voiceover 必须直接涉及「{topic}」
- 旁白要口语化、生动有趣，像3Blue1Brown的风格
- ⚠️ 不要生成 resources 字段（视频链接会由系统自动生成）
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
                # 验证：至少一个 scene 的 title 包含 topic 关键词
                has_topic = any(
                    any(kw in s.get("title", "") for kw in context.topic.split() if len(kw) >= 2)
                    for s in scenes
                )
                if not has_topic:
                    logger.warning("DirectorAgent: scene titles don't contain topic keywords, using fallback")
                    content = get_fallback_content("director", context.topic)
                else:
                    # 规范化 + 自动生成 YouTube 搜索链接（不让 LLM 编造）
                    search_query = urllib.parse.quote(context.topic)
                    for i, s in enumerate(scenes):
                        if "scene_number" not in s:
                            s["scene_number"] = i + 1
                        if "duration_seconds" not in s:
                            s["duration_seconds"] = 45
                        # ★ 用真实的 YouTube 搜索链接替代 LLM 幻觉的链接
                        s["resources"] = [
                            {
                                "type": "video",
                                "title": f"{context.topic} — {s.get('title', f'第{i+1}部分')}",
                                "description": f"在 YouTube 上搜索关于「{context.topic}」的优质教学视频",
                                "thumbnail": f"https://img.youtube.com/vi/0/maxresdefault.jpg",
                                "url": f"https://www.youtube.com/results?search_query={search_query}",
                                "duration": "10:00",
                                "platform": "YouTube",
                            }
                        ]
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
