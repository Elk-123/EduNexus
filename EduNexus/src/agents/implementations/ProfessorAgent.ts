/**
 * Professor Agent - 教授智能体
 * 负责生成学术性的、结构化的教学内容
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult, ExecutionStatus } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class ProfessorAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个资深的教育专家，专门负责生成高质量的教学内容。
请根据以下信息生成一份结构化的学术性内容：

主题: {topic}
参考上下文（上游Agent输出）: {context}

请严格以JSON格式返回（不要包含任何其他文字）：
\`\`\`json
{
  "title": "主题标题",
  "sections": [
    {"heading": "章节标题", "body": "详细内容（至少100字）"}
  ],
  "keyConcepts": [
    {"name": "概念名称", "explanation": "概念解释"}
  ]
}
\`\`\`

请确保内容具有教育价值，逻辑清晰，包含至少3个章节和3个关键概念。
`;

  constructor(config: AgentConfig = {
    id: 'professor',
    name: '教授智能体',
    role: '学术内容生成专家',
    capabilities: ['结构化内容生成', '学术写作', '知识梳理'],
    timeout: 30000
  }) {
    super(config);
  }

  async execute(context: AgentContext): Promise<AgentExecutionResult> {
    const startTime = Date.now();
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(ProfessorAgent.PROMPT_TEMPLATE);
      const llmResponse = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic,
        context: JSON.stringify(context.context || {}, null, 2),
      });

      const parsed = LangChainUtils.tryParseJson(llmResponse);
      let content: any;
      if (parsed) {
        content = {
          title: parsed.title || `关于${context.topic}的学术解析`,
          sections: parsed.sections || [],
          keyConcepts: parsed.keyConcepts || [],
        };
      } else {
        content = {
          title: `关于${context.topic}的学术解析`,
          sections: [{ heading: "LLM 生成内容", body: llmResponse.trim() }],
          keyConcepts: [],
        };
      }

      this._recordSuccess(context.topic);
      return {
        agentId: this.config.id,
        status: ExecutionStatus.SUCCESS,
        result: {
          content,
          type: 'academic_content',
          timestamp: new Date(),
          log: [`成功生成教授内容: ${context.topic}`]
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
