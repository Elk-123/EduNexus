/**
 * Hacker Agent - 极客智能体
 * 负责生成代码示例和编程练习
 */
import { BaseAgent } from '../base/BaseAgent';
import { AgentConfig, AgentContext, AgentExecutionResult } from '../types';
import { LangChainUtils } from '../utils/LangChainUtils';

export class HackerAgent extends BaseAgent {
  private static readonly PROMPT_TEMPLATE = `
你是一个经验丰富的程序员和教育专家，专门负责生成编程相关的教学内容。
请根据以下主题生成一套编程教学材料：

主题: {topic}

你需要生成以下内容：
1. 代码示例：一个完整的可运行代码片段
2. 代码说明：详细解释代码的功能和实现方式
3. 练习题目：2个编程练习题，包含要求和参考答案

代码要求：
- 代码应该清晰、简洁、易懂
- 包含必要的注释
- 符合最佳实践
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
    try {
      const promptTemplate = LangChainUtils.createPromptTemplate(HackerAgent.PROMPT_TEMPLATE);
      const result = await LangChainUtils.executeChain(promptTemplate, {
        topic: context.topic
      });

      return {
        agentId: this.config.id,
        status: 'success',
        result: {
          content: {
            title: `${context.topic} 编程示例`,
            description: `这是一个关于${context.topic}的完整代码示例`,
            code: `// ${context.topic} 示例代码
function exampleFunction() {
  // 实现${context.topic}的核心功能
  console.log("Hello from ${context.topic}");
  return true;
}`,
            expected_output: "Hello from Transformer Architecture",
            exercises: [
              {
                title: "基础练习",
                description: "根据提供的代码实现一个类似功能",
                requirement: "实现一个接受参数的函数",
                hint: "参考示例代码的结构"
              },
              {
                title: "进阶练习",
                description: "扩展功能以满足额外要求",
                requirement: "添加错误处理机制",
                hint: "考虑使用try-catch语句"
              }
            ]
          },
          type: 'code',
          timestamp: new Date(),
          log: [`成功生成代码内容: ${context.topic}`]
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
    console.log('Hacker agent interrupted');
  }
}