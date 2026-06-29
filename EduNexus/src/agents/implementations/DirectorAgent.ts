/**
 * Director Agent - 导演智能体
 * 负责生成视频脚本和多媒体内容
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult, ExecutionStatus } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class DirectorAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个专业的教育视频制作人，擅长将复杂概念转化为易于理解的视频内容。
请根据以下信息生成一个视频脚本：

主题: {topic}
参考上下文（上游Agent输出的教学内容）: {context}

请严格以JSON格式返回（不要包含任何其他文字）：
\`\`\`json
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
\`\`\`

要求：至少3个场景，场景之间逻辑连贯，适合教育类视频制作。
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
    const startTime = Date.now();
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(DirectorAgent.PROMPT_TEMPLATE);
      const llmResponse = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic,
        context: JSON.stringify(context.context || {}, null, 2),
      });

      const parsed = LangChainUtils.tryParseJson(llmResponse);
      let content: any;
      if (parsed) {
        content = {
          scenes: parsed.scenes || [],
          total_duration: parsed.total_duration || 0,
        };
      } else {
        content = {
          scenes: [{
            scene_number: 1,
            title: `关于${context.topic}`,
            visual: "教育动画展示",
            voiceover: llmResponse.trim(),
            duration_seconds: 60
          }],
          total_duration: 60,
        };
      }

      this._recordSuccess(context.topic);
      return {
        agentId: this.config.id,
        status: ExecutionStatus.SUCCESS,
        result: {
          content,
          type: 'video_script',
          timestamp: new Date(),
          log: [`成功生成视频脚本: ${context.topic}`]
        },
        duration: Date.now() - startTime
      };
    } catch (error) {
      this._recordFailure(context.topic);
      return {
        agentId: this.config.id,
        status: ExecutionStatus.ERROR,
        error: error instanceof Error ? error.message : String(error),
        duration: Date.now() - startTime
      };
    }
  }
}
