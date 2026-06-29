/**
 * Architect Agent - 架构师智能体
 * 负责生成思维导图和知识结构图
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult, ExecutionStatus } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class ArchitectAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个专业的知识架构师，专门负责将复杂主题转化为清晰的思维导图结构。
请根据以下信息生成一个思维导图结构：

主题: {topic}
参考上下文（上游Agent输出）: {context}

请严格以JSON格式返回（不要包含任何其他文字）：
\`\`\`json
{
  "root": "主题根节点",
  "children": [
    {
      "name": "一级分支1",
      "children": [
        {"name": "二级分支1.1", "children": []},
        {"name": "二级分支1.2", "children": []}
      ]
    },
    {
      "name": "一级分支2",
      "children": []
    }
  ]
}
\`\`\`

请确保结构清晰，层次分明（至少2层深度），便于理解和记忆。
`;

  constructor(config: AgentConfig = {
    id: 'architect',
    name: '架构师智能体',
    role: '知识结构设计师',
    capabilities: ['思维导图生成', '知识架构', '可视化表达'],
    timeout: 30000
  }) {
    super(config);
  }

  async execute(context: AgentContext): Promise<AgentExecutionResult> {
    const startTime = Date.now();
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(ArchitectAgent.PROMPT_TEMPLATE);
      const llmResponse = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic,
        context: JSON.stringify(context.context || {}, null, 2),
      });

      const parsed = LangChainUtils.tryParseJson(llmResponse);
      let content: any;
      if (parsed) {
        content = {
          root: parsed.root || context.topic,
          children: parsed.children || [],
        };
      } else {
        content = {
          root: context.topic,
          children: [{
            name: "LLM 生成内容",
            children: [{ name: llmResponse.trim().substring(0, 100), children: [] }]
          }],
        };
      }

      this._recordSuccess(context.topic);
      return {
        agentId: this.config.id,
        status: ExecutionStatus.SUCCESS,
        result: {
          content,
          type: 'mindmap',
          timestamp: new Date(),
          log: [`成功生成架构图: ${context.topic}`]
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
