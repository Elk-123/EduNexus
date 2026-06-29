/**
 * Reviewer Agent - 质量审查
 * 负责审查和优化所有生成内容的质量
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult, ExecutionStatus } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class ReviewerAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个专业的质量审查专家，负责对教育内容进行审查和优化。
请根据以下所有生成的内容进行质量审查：

主题: {topic}

以下是所有上游Agent生成的完整内容：
{content}

请严格以JSON格式返回审查报告（不要包含任何其他文字）：
\`\`\`json
{
  "hallucination_risk": "low/medium/high",
  "quality_score": 8.5,
  "suggestions": ["具体改进建议1", "具体改进建议2", "具体改进建议3"],
  "difficulty_assessment": "难度评估（如：适合初学者/中等偏难/高级）",
  "review_summary": "总体评价（100字以内）"
}
\`\`\`

审查标准：
- 准确性：内容是否准确无误
- 清晰度：表达是否清晰易懂
- 完整性：是否涵盖主题的各个方面
- 教育价值：是否适合目标学习者
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
    const startTime = Date.now();
    try {
      // 将累积的所有上游Agent输出格式化传入 prompt
      const contentJson = context.context
        ? JSON.stringify(context.context, null, 2)
        : context.topic;

      const promptTemplate = LangChainUtils.createPromptTemplate(ReviewerAgent.PROMPT_TEMPLATE);
      const llmResponse = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic,
        content: contentJson,
      });

      const parsed = LangChainUtils.tryParseJson(llmResponse);
      let content: any;
      if (parsed) {
        content = {
          hallucination_risk: parsed.hallucination_risk || "low",
          quality_score: typeof parsed.quality_score === 'number' ? parsed.quality_score : 7.0,
          suggestions: parsed.suggestions || [],
          difficulty_assessment: parsed.difficulty_assessment || "中等",
          review_summary: parsed.review_summary || "",
        };
      } else {
        content = {
          hallucination_risk: "low",
          quality_score: 7.0,
          suggestions: [],
          difficulty_assessment: "中等",
          review_summary: llmResponse.trim().substring(0, 500),
        };
      }

      this._recordSuccess(context.topic);
      return {
        agentId: this.config.id,
        status: ExecutionStatus.SUCCESS,
        result: {
          content,
          type: 'review',
          timestamp: new Date(),
          log: [`成功完成内容审查: ${context.topic}`]
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
