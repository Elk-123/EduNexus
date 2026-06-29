/**
 * Hacker Agent - 极客智能体
 * 负责生成代码示例和编程练习
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult, ExecutionStatus } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class HackerAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个经验丰富的程序员和教育专家，专门负责生成编程相关的教学内容。
请根据以下信息生成一套编程教学材料：

主题: {topic}
参考上下文（上游Agent输出的教学内容）: {context}

请严格以JSON格式返回（不要包含任何其他文字）：
\`\`\`json
{
  "title": "代码示例标题",
  "description": "代码功能描述",
  "code": "完整的可运行代码（包含注释）",
  "expected_output": "预期输出结果",
  "exercises": [
    {
      "title": "练习标题",
      "description": "练习描述",
      "requirement": "练习要求",
      "hint": "提示"
    }
  ]
}
\`\`\`

要求：代码清晰简洁，包含必要注释，提供至少2个练习题。
`;

  constructor(config: AgentConfig = {
    id: 'hacker',
    name: '极客智能体',
    role: '编程教育专家',
    capabilities: ['代码生成', '编程教学', '实践练习'],
    timeout: 30000
  }) {
    super(config);
  }

  async execute(context: AgentContext): Promise<AgentExecutionResult> {
    const startTime = Date.now();
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(HackerAgent.PROMPT_TEMPLATE);
      const llmResponse = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic,
        context: JSON.stringify(context.context || {}, null, 2),
      });

      const parsed = LangChainUtils.tryParseJson(llmResponse);
      let content: any;
      if (parsed) {
        content = {
          title: parsed.title || `${context.topic} 编程示例`,
          description: parsed.description || "",
          code: parsed.code || "",
          expected_output: parsed.expected_output || "",
          exercises: parsed.exercises || [],
        };
      } else {
        content = {
          title: `${context.topic} 编程示例`,
          description: "LLM 生成的代码内容",
          code: llmResponse.trim(),
          expected_output: "",
          exercises: [],
        };
      }

      this._recordSuccess(context.topic);
      return {
        agentId: this.config.id,
        status: ExecutionStatus.SUCCESS,
        result: {
          content,
          type: 'code',
          timestamp: new Date(),
          log: [`成功生成代码内容: ${context.topic}`]
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
