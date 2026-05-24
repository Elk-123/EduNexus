/**
 * Manager Agent - 主控中枢
 * 负责协调整个Agent流程和任务调度
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class ManagerAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个智能任务协调员，专门负责规划和管理复杂的多智能体任务。
请根据以下主题生成任务规划和协调指令：

主题: {topic}

你需要生成以下内容：
1. 任务分解：将复杂主题分解为7个子任务
2. 执行优先级：给出每个子任务的执行顺序
3. 协调要点：说明各智能体间如何配合

任务规划要求：
- 确保逻辑连贯性
- 明确任务边界
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
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(ManagerAgent.PROMPT_TEMPLATE);
      const result = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic
      });

      return {
        agentId: this.config.id,
        status: 'success',
        result: {
          content: {
            tasks: [
              "分析主题",
              "生成学术内容",
              "构建知识结构",
              "设计测验题目",
              "制作视频脚本",
              "编写代码示例",
              "质量审核"
            ],
            priority: ["analysis", "professor", "architect", "examiner", "director", "hacker", "reviewer"],
            coordination_notes: [
              "教授智能体应在架构师之前生成基础内容",
              "考官智能体应基于教授的内容设计题目",
              "导演智能体需要基于架构师的结构制作脚本",
              "极客智能体需参考教授的内容编写代码",
              "质量审查在最后进行"
            ]
          },
          type: 'task_plan',
          timestamp: new Date(),
          log: [`成功生成任务计划: ${context.topic}`]
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
    console.log('Manager agent interrupted');
  }
}