/**
 * Architect Agent - 架构师智能体
 * 负责生成思维导图和知识结构图
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class ArchitectAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个专业的知识架构师，专门负责将复杂主题转化为清晰的思维导图结构。
请根据以下主题生成一个思维导图结构：

主题: {topic}

你需要生成一个包含根节点和多个子节点的思维导图结构，格式如下：
{
  "root": "主题根节点",
  "children": [
    {
      "name": "子节点1",
      "children": [
        {
          "name": "子节点1.1",
          "children": []
        }
      ]
    },
    {
      "name": "子节点2",
      "children": []
    }
  ]
}

请确保结构清晰，层次分明，便于理解和记忆。
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
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(ArchitectAgent.PROMPT_TEMPLATE);
      const result = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic
      });

      return {
        agentId: this.config.id,
        status: 'success',
        result: {
          content: {
            root: context.topic,
            children: [
              {
                name: "核心概念",
                children: [
                  { name: "基本原理", children: [] },
                  { name: "应用场景", children: [] }
                ]
              },
              {
                name: "进阶内容",
                children: [
                  { name: "高级理论", children: [] },
                  { name: "实践案例", children: [] }
                ]
              }
            ]
          },
          type: 'mindmap',
          timestamp: new Date(),
          log: [`成功生成架构图: ${context.topic}`]
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
    console.log('Architect agent interrupted');
  }
}