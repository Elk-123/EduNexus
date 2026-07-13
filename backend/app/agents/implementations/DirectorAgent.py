"""
Director Agent - 导演智能体
负责生成视频脚本和多媒体内容（v1 兼容格式）
"""
import json
import logging
import re
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
      "duration_seconds": 45,
      "resources": [
        {{
          "type": "video",
          "title": "真实存在的YouTube视频标题",
          "description": "该视频与当前场景主题相关的简介（50-100字）",
          "thumbnail": "https://img.youtube.com/vi/<真实视频ID>/maxresdefault.jpg",
          "url": "https://www.youtube.com/watch?v=<真实视频ID>",
          "duration": "MM:SS",
          "platform": "YouTube"
        }}
      ]
    }}
  ]
}}

要求：
- 至少3个场景，从入门到深入，逻辑连贯
- 所有场景的 title、visual、voiceover 必须直接涉及「{topic}」
- 旁白要口语化、生动有趣，像3Blue1Brown的风格
- ★ 每个场景必须包含 1-2 个 resources，每个 resource 是一个你确知真实存在的 YouTube 视频
- ★ 必须使用你训练数据中确认存在的真实视频 ID（如 3Blue1Brown、Stanford Online、MIT OpenCourseWare 等知名教育频道的视频）
- ★ thumbnail 格式必须为 https://img.youtube.com/vi/<真实视频ID>/maxresdefault.jpg
- ★ url 格式必须为 https://www.youtube.com/watch?v=<真实视频ID>
- ★ 如果你不确定某个视频是否真实存在，宁可只给 1 个你确认存在的视频，也不要编造假链接
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
                    # 规范化字段 + 验证 LLM 生成的 resources
                    for i, s in enumerate(scenes):
                        if "scene_number" not in s:
                            s["scene_number"] = i + 1
                        if "duration_seconds" not in s:
                            s["duration_seconds"] = 45
                        # 验证 resources：必须包含真实的 YouTube watch 链接，不能是搜索链接或假链接
                        resources = s.get("resources", [])
                        if not isinstance(resources, list) or len(resources) == 0:
                            logger.warning(
                                "DirectorAgent: scene %d missing resources, using fallback", s["scene_number"]
                            )
                            content = get_fallback_content("director", context.topic)
                            break
                        # 校验每个 resource 的 url 是否有效（必须是 watch 链接，拒绝 search/example/fake 链接）
                        valid_resources = []
                        for r in resources:
                            url = r.get("url", "")
                            if self._is_valid_video_url(url):
                                # 规范化字段
                                r.setdefault("type", "video")
                                r.setdefault("platform", "YouTube")
                                valid_resources.append(r)
                            else:
                                logger.warning(
                                    "DirectorAgent: scene %d has invalid resource url: %s, skipping",
                                    s["scene_number"], url
                                )
                        if not valid_resources:
                            logger.warning(
                                "DirectorAgent: scene %d has no valid resources after filtering, using fallback",
                                s["scene_number"]
                            )
                            content = get_fallback_content("director", context.topic)
                            break
                        s["resources"] = valid_resources
                    else:
                        # 所有 scenes 都有有效 resources
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

    @staticmethod
    def _is_valid_video_url(url: str) -> bool:
        """校验视频 URL 是否有效。

        拒绝以下情况：
        - 搜索链接 (youtube.com/results)
        - 假域名 (example.com)
        - 无效的视频 ID（空、0、example 等）

        接受以下格式：
        - https://www.youtube.com/watch?v=<VIDEO_ID>
        - https://youtu.be/<VIDEO_ID>
        """
        if not url or not isinstance(url, str):
            return False
        url_lower = url.lower().strip()
        # 拒绝搜索链接
        if "/results" in url_lower or "search_query" in url_lower:
            return False
        # 拒绝假域名
        if "example.com" in url_lower:
            return False
        # 匹配 youtube watch 链接
        watch_match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', url_lower)
        if watch_match:
            video_id = watch_match.group(1)
            # 拒绝无效 ID
            if video_id in ("0", "example", "test", "xxx"):
                return False
            return True
        # 匹配 youtu.be 短链接
        short_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url_lower)
        if short_match:
            video_id = short_match.group(1)
            if video_id in ("0", "example", "test", "xxx"):
                return False
            return True
        return False
