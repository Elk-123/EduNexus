/**
 * Manager Agent - 主控中枢
 * 负责协调整个Agent流程和任务调度
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult, ExecutionStatus } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class ManagerAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个智能任务协调员，专门负责规划和管理复杂的多智能体任务。
请根据以下主题生成任务规划和协调指令：

主题: {topic}

请严格以JSON格式返回（不要包含任何其他文字）：
\`\`\`json
{
  "tasks": ["子任务1", "子任务2", ...],
  "priority": ["professor", "architect", "examiner", "director", "hacker", "reviewer"],
  "coordination_notes": ["协调说明1", "协调说明2", ...]
}
\`\`\`

任务规划要求：
- 将"生成关于 {topic} 的完整教学内容"分解为7个子任务
- 确保逻辑连贯性，明确任务边界
- 合理分配给不同的智能体
`;

  constructor(config: AgentConfig = {
    id: 'manager',
    name: '主控中枢',
    role: '任务协调专家',
    capabilities: ['任务规划', '流程协调', '资源调度'],
    timeout: 30000
  }) {
    super(config);
  }

  async execute(context: AgentContext): Promise<AgentExecutionResult> {
    const startTime = Date.now();
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(ManagerAgent.PROMPT_TEMPLATE);
      const llmResponse = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic
      });

      const parsed = LangChainUtils.tryParseJson(llmResponse);
      let content: any;
      if (parsed) {
        content = {
          tasks: parsed.tasks || [context.topic],
          priority: parsed.priority || [],
          coordination_notes: parsed.coordination_notes || [],
          raw_response: llmResponse,
        };
      } else {
        content = {
          tasks: [context.topic],
          priority: [],
          coordination_notes: [llmResponse.trim()],
          raw_response: llmResponse,
        };
      }

      this._recordSuccess(context.topic);
      return {
        agentId: this.config.id,
        status: ExecutionStatus.SUCCESS,
        result: {
          content,
          type: 'task_plan',
          timestamp: new Date(),
          log: [`成功生成任务计划: ${context.topic}`]
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
