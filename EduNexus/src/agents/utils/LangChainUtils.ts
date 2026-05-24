/**
 * LangChain集成工具类
 */
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { RunnableSequence } from "@langchain/core/runnables";
import { HumanMessage, SystemMessage } from "@langchain/core/messages";

export class LangChainUtils {
  private static model: ChatGoogleGenerativeAI;

  /**
   * 初始化LangChain模型
   */
  static initializeModel(apiKey: string, modelName: string = "gemini-2.5-flash") {
    this.model = new ChatGoogleGenerativeAI({
      model: modelName,
      apiKey: apiKey,
      temperature: 0.7,
    });
  }

  /**
   * 创建提示模板
   */
  static createPromptTemplate(template: string): ChatPromptTemplate {
    return ChatPromptTemplate.fromMessages([
      new SystemMessage("You are an expert assistant designed to help with educational content creation."),
      new HumanMessage(template)
    ]);
  }

  /**
   * 创建可运行序列
   */
  static createRunnableSequence(promptTemplate: ChatPromptTemplate) {
    if (!this.model) {
      throw new Error("LangChain model not initialized. Call LangChainUtils.initializeModel first.");
    }

    return RunnableSequence.from([
      promptTemplate,
      this.model
    ]);
  }

  /**
   * 执行链式调用
   */
  static async executeChain(
    promptTemplate: ChatPromptTemplate,
    inputs: Record<string, any>
  ): Promise<string> {
    const runnable = this.createRunnableSequence(promptTemplate);
    const result = await runnable.invoke(inputs);
    return result.content as string;
  }
}