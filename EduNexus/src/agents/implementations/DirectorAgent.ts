/**
 * Director Agent - 导演智能体
 * 负责生成视频脚本和多媒体内容
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class DirectorAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
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
`;

  constructor(config: AgentConfig = {
    id: 'director',
    name: '导演智能体',
    role: '教育视频制作人',
    capabilities: ['视频脚本创作', '多媒体内容设计', '故事板构建'],
    timeout: 30000
  }) {
    super(config);
  }

  async execute(context: AgentContext): Promise<AgentExecutionResult> {
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(DirectorAgent.PROMPT_TEMPLATE);
      const result = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic
      });

      return {
        agentId: this.config.id,
        status: 'success',
        result: {
          content: {
            scenes: [
              {
                scene_number: 1,
                title: "引入主题",
                visual: "动画展示主题概念",
                voiceover: `今天我们要学习的是${context.topic}。这是一个非常重要的概念...`,
                duration_seconds: 30
              },
              {
                scene_number: 2,
                title: "核心概念详解",
                visual: "图表和动画演示",
                voiceover: "让我们深入了解一下${context.topic}的核心要素...",
                duration_seconds: 60
              },
              {
                scene_number: 3,
                title: "应用实例",
                visual: "现实应用案例",
                voiceover: "现在我们来看一下${context.topic}在实际中的应用...",
                duration_seconds: 45
              }
            ],
            total_duration: 135
          },
          type: 'video_script',
          timestamp: new Date(),
          log: [`成功生成视频脚本: ${context.topic}`]
        },
        duration: 0
      };
    } catch (error) {
      return {
        agentId: this.config.id,
        status: 'failed',
        error: error instanceof Error ? error.message : String(error),
        duration: 0
      };
    }
  }

  async getStatus(): Promise<AgentStatus> {
    // 实现获取状态的逻辑
    return {
      agentId: this.config.id,
      status: 'idle',
      lastUpdated: new Date(),
      successCount: 0,
      failureCount: 0
    };
  }

  interrupt(): void {
    // 实现中断逻辑
    console.log('Director agent interrupted');
  }
}