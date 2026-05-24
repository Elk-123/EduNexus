/**
 * Examiner Agent - 考官智能体
 * 负责生成测验题目和评估材料
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class ExaminerAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个经验丰富的教育评估专家，专门负责设计高质量的测验题目。
请根据以下主题生成一套评估材料：

主题: {topic}

你需要生成以下内容：
1. 选择题：3道题目，每道题包含4个选项和正确答案
2. 简答题：2道开放性问题

题目要求：
- 选择题难度适中，涵盖核心知识点
- 简答题需要考察学生的理解深度
- 题目表述清晰，无歧义
`;

  constructor(config: AgentConfig = {
    id: 'examiner',
    name: '考官智能体',
    role: '试题设计专家',
    capabilities: ['题库生成', '评估设计', '测试策划'],
    timeout: 30000
  }) {
    super(config);
  }

  async execute(context: AgentContext): Promise<AgentExecutionResult> {
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(ExaminerAgent.PROMPT_TEMPLATE);
      const result = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic
      });

      return {
        agentId: this.config.id,
        status: 'success',
        result: {
          content: {
            questions: [
              {
                question: `关于${context.topic}的基础问题`,
                options: ["选项A", "选项B", "选项C", "选项D"],
                answer: "选项B",
                explanation: "这是关于基础概念的题目"
              },
              {
                question: `关于${context.topic}的进阶问题`,
                options: ["选项A", "选项B", "选项C", "选项D"],
                answer: "选项C",
                explanation: "这是需要综合理解的问题"
              },
              {
                question: `关于${context.topic}的高级问题`,
                options: ["选项A", "选项B", "选项C", "选项D"],
                answer: "选项A",
                explanation: "这是考验应用能力的问题"
              }
            ],
            essayQuestions: [
              {
                question: `请阐述${context.topic}的核心思想`,
                maxPoints: 10
              },
              {
                question: `结合实例说明${context.topic}的应用`,
                maxPoints: 15
              }
            ]
          },
          type: 'quiz',
          timestamp: new Date(),
          log: [`成功生成测验材料: ${context.topic}`]
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
    console.log('Examiner agent interrupted');
  }
}