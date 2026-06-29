/**
 * Examiner Agent - 考官智能体
 * 负责生成测验题目和评估材料
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult, ExecutionStatus } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class ExaminerAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个经验丰富的教育评估专家，专门负责设计高质量的测验题目。
请根据以下信息生成一套评估材料：

主题: {topic}
参考上下文（上游Agent输出的教学内容）: {context}

请严格以JSON格式返回（不要包含任何其他文字）：
\`\`\`json
{
  "questions": [
    {
      "question": "题目内容",
      "options": ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"],
      "answer": "B",
      "explanation": "解析说明"
    }
  ],
  "essayQuestions": [
    {
      "question": "简答题内容",
      "maxPoints": 10
    }
  ]
}
\`\`\`

要求：至少3道选择题和2道简答题，难度适中，涵盖核心知识点。
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
    const startTime = Date.now();
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(ExaminerAgent.PROMPT_TEMPLATE);
      const llmResponse = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic,
        context: JSON.stringify(context.context || {}, null, 2),
      });

      const parsed = LangChainUtils.tryParseJson(llmResponse);
      let content: any;
      if (parsed) {
        content = {
          questions: parsed.questions || [],
          essayQuestions: parsed.essayQuestions || [],
        };
      } else {
        content = {
          questions: [],
          essayQuestions: [{ question: llmResponse.trim(), maxPoints: 10 }],
        };
      }

      this._recordSuccess(context.topic);
      return {
        agentId: this.config.id,
        status: ExecutionStatus.SUCCESS,
        result: {
          content,
          type: 'quiz',
          timestamp: new Date(),
          log: [`成功生成测验材料: ${context.topic}`]
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
