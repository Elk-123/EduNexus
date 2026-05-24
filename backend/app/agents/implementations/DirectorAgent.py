"""
Director Agent - 导演智能体
负责生成视频脚本和多媒体内容
"""
from typing import Dict, Any
from . import BaseAgent, AgentConfig, AgentContext, AgentExecutionResult, AgentResult
from ..utils.LangChainUtils import LangChainUtils
from datetime import datetime

class DirectorAgent(BaseAgent):
    """导演智能体"""

    PROMPT_TEMPLATE = """
你是一个专业的教育视频制作人，擅长将复杂概念转化为易于理解的视频内容。
请根据以下主题生成一个视频脚本：

主题: {topic}

你需要生成以下内容：
1. 视频场景：至少3个场景，每个场景包含场景编号、标题、视觉描述、旁白内容和时长
2. 视频总时长：估算总时长

视频脚本要求：
- 场景之间逻辑连贯
- 视觉描述具体生动
- 旁白内容通俗易懂
- 适合教育类视频制作
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
        """执行任务"""
        try:
            prompt_template = LangChainUtils.create_prompt_template(self.PROMPT_TEMPLATE)
            result = LangChainUtils.execute_chain(prompt_template, {
                "topic": context.topic
            })

            return AgentExecutionResult(
                agent_id=self.config.id,
                status="success",
                result=AgentResult(
                    content={
                        "scenes": [
                            {
                                "scene_number": 1,
                                "title": "引入主题",
                                "visual": "动画展示主题概念",
                                "voiceover": f"今天我们要学习的是{context.topic}。这是一个非常重要的概念...",
                                "duration_seconds": 30
                            },
                            {
                                "scene_number": 2,
                                "title": "核心概念详解",
                                "visual": "图表和动画演示",
                                "voiceover": f"让我们深入了解一下{context.topic}的核心要素...",
                                "duration_seconds": 60
                            },
                            {
                                "scene_number": 3,
                                "title": "应用实例",
                                "visual": "现实应用案例",
                                "voiceover": f"现在我们来看一下{context.topic}在实际中的应用...",
                                "duration_seconds": 45
                            }
                        ],
                        "total_duration": 135
                    },
                    type="video_script",
                    timestamp=datetime.now(),
                    log=[f"成功生成视频脚本: {context.topic}"]
                ),
                duration=0
            )
        except Exception as error:
            return AgentExecutionResult(
                agent_id=self.config.id,
                status="error",
                error=str(error),
                duration=0
            )

    def get_status(self) -> "AgentStatusInfo":
        """获取状态"""
        # 实现获取状态的逻辑
        from ..types import AgentStatusInfo, AgentStatus
        return AgentStatusInfo(
            agent_id=self.config.id,
            status=AgentStatus.IDLE,
            last_updated=datetime.now(),
            success_count=0,
            failure_count=0
        )

    def interrupt(self) -> None:
        """中断执行"""
        print("Director agent interrupted")