/**
 * LangChain集成工具类 - DeepSeek版本
 */
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage, SystemMessage } from "@langchain/core/messages";

export class LangChainUtils {
  private static model: ChatOpenAI | null = null;

  /**
   * 初始化DeepSeek LangChain模型
   *
   * @param apiKey - DeepSeek API Key
   * @param modelName - 模型名称，默认 deepseek-chat
   *                    可选: deepseek-chat, deepseek-reasoner
   */
  static initializeModel(apiKey: string, modelName: string = "deepseek-chat") {
    this.model = new ChatOpenAI({
      model: modelName,
      apiKey: apiKey,
      temperature: 0.7,
      configuration: {
        baseURL: "https://api.deepseek.com",
      },
    });
    console.log(`[LangChainUtils] Model initialized: ${modelName} via DeepSeek API`);
  }

  /**
   * 获取模型实例
   */
  private static _getModel(): ChatOpenAI {
    if (!this.model) {
      throw new Error(
        "LangChain model not initialized. Call LangChainUtils.initializeModel(apiKey) first."
      );
    }
    return this.model;
  }

  /**
   * 创建提示模板
   */
  static createPromptTemplate(template: string): ChatPromptTemplate {
    return ChatPromptTemplate.fromMessages([
      new SystemMessage(
        "You are an expert assistant designed to help with educational content creation. " +
        "Always respond with valid JSON matching the requested schema exactly. " +
        "Do not include explanations outside the JSON structure."
      ),
      new HumanMessage(template)
    ]);
  }

  /**
   * 执行链式调用 (异步) — 使用管道语法
   *
   * @param promptTemplate - ChatPromptTemplate 提示模板
   * @param inputs - 模板变量输入对象
   * @returns LLM 响应的文本内容
   */
  static async executeChain(
    promptTemplate: ChatPromptTemplate,
    inputs: Record<string, any>
  ): Promise<string> {
    const model = this._getModel();
    const runnable = promptTemplate.pipe(model);
    const result = await runnable.invoke(inputs);
    return typeof result.content === 'string' ? result.content : JSON.stringify(result.content);
  }

  /**
   * 尝试从 LLM 响应中解析 JSON
   *
   * 支持从 markdown 代码块或纯文本中提取 JSON。
   *
   * @param text - LLM 响应的原始文本
   * @returns 解析成功的对象，失败返回 null
   */
  static tryParseJson(text: string): Record<string, any> | null {
    if (!text) return null;

    // 尝试直接解析
    try {
      return JSON.parse(text);
    } catch {
      // 继续尝试其他方式
    }

    // 尝试从 markdown ```json ... ``` 代码块中提取
    const jsonMatch = text.match(/```(?:json)?\s*\n?(.*?)\n?```/s);
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[1]);
      } catch {
        // 继续尝试
      }
    }

    // 尝试找到第一个 { 和最后一个 }
    const start = text.indexOf('{');
    const end = text.lastIndexOf('}');
    if (start !== -1 && end !== -1 && end > start) {
      try {
        return JSON.parse(text.substring(start, end + 1));
      } catch {
        // 最终失败
      }
    }

    return null;
  }
}
