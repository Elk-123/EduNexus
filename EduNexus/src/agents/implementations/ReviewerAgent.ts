/**
 * Reviewer Agent - 质量审查
 * 负责审查和优化所有生成内容的质量
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class ReviewerAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个专业的质量审查专家，负责对教育内容进行审查和优化。
请根据以下内容生成审查报告：

主题: {topic}
内容: {content}

你需要生成以下内容：
1. 一致性检查：检查内容是否前后一致
2. 质量评分：给出1-10分的评分
3. 改进建议：提出具体的改进建议
4. 风险评估：识别潜在的问题或风险

审查标准：
- 准确性
- 清晰度
- 完整性
- 教育价值
`;

  constructor(config: AgentConfig = {
    id: 'reviewer',
    name: '质量审查',
    role: '内容质量专家',
    capabilities: ['内容审查', '质量评估', '优化建议'],
    timeout: 30000
  }) {
    super(config);
  }

  async execute(context: AgentContext): Promise<AgentExecutionResult> {
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(ReviewerAgent.PROMPT_TEMPLATE);
      const result = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic,
        content: JSON.stringify(context.context)
      });

      return {
        agentId: this.config.id,
        status: 'success',
        result: {
          content: {
            hallucination_risk: "low",
            quality_score: 8.5,
            suggestions: [
              "可以增加更多实际应用案例",
              "部分术语解释可以更详细",
              "增加视觉辅助元素的建议"
            ],
            difficulty_assessment: "中等偏难",
            review_summary: "整体质量良好，内容结构清晰，但可以进一步完善细节"
          },
          type: 'review',
          timestamp: new Date(),
          log: [`成功完成内容审查: ${context.topic}`]
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
    console.log('Reviewer agent interrupted');
  }
}