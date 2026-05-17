import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

from app.models.factory import GenerationTask, GeneratedResource
from app.core.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.factory import GenerateRequest
from app.services.agent_orchestrator import AgentOrchestrator
from app.core.config import settings
# google.genai import removed for now - focusing on mock data


class ContentGenerator:
    def __init__(self):
        """初始化内容生成器"""
        # AgentOrchestrator 将在使用时传入 db
        self.orchestrator = None
        self.gemini_model = None
        # if settings.GOOGLE_API_KEY:
            # genai model initialization removed for now - focusing on mock data

    async def generate_content(self, request: GenerateRequest, student_id: str, db: AsyncSession = None) -> Dict[str, str]:
        """
        生成教育内容的主入口
        """
        try:
            # 创建生成任务记录
            async with AsyncSessionLocal() as session:
                task = GenerationTask(
                    student_id=student_id,  # 使用传入的student_id
                    topic=request.topic,
                    status="running",
                    agents_status={
                        "manager": "running",
                        "professor": "pending",
                        "archessor": "pending",
                        "examiner": "pending",
                        "director": "pending",
                        "hacker": "pending",
                        "reviewer": "pending"
                    }
                )
                session.add(task)
                await session.commit()
                await session.refresh(task)

                task_id = str(task.id)

                # 启动多智能体生成流水线（异步）
                asyncio.create_task(self._run_generation_pipeline(task_id, request.topic))

                return {
                    "task_id": task_id,
                    "status": "running"
                }

        except Exception as e:
            raise Exception(f"生成任务创建失败: {str(e)}")

    async def _run_generation_pipeline(self, task_id: str, topic: str, db: AsyncSession = None):
        """
        运行多智能体生成流水线
        """
        try:
            session = db or AsyncSessionLocal()
            async with session:
                # 获取任务记录
                task = await session.get(GenerationTask, task_id)
                if not task:
                    raise Exception(f"任务 {task_id} 不存在")

                # 更新状态为运行中
                task.status = "running"
                await session.commit()

                # 运行多智能体流水线
                await self.orchestrator.run_pipeline(task_id, topic, session)

        except Exception as e:
            print(f"流水线执行失败: {str(e)}")
            async with AsyncSessionLocal() as session:
                task = await session.get(GenerationTask, task_id)
                if task:
                    task.status = "failed"
                    await session.commit()

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        """
        async with AsyncSessionLocal() as session:
            task = await session.get(GenerationTask, task_id)
            if not task:
                raise Exception(f"任务 {task_id} 不存在")

            return {
                "id": str(task.id),
                "topic": task.topic,
                "status": task.status,
                "agents_status": task.agents_status,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }

    async def get_task_resources(self, task_id: str) -> List[Dict[str, Any]]:
        """
        获取任务生成的资源
        """
        async with AsyncSessionLocal() as session:
            # 查询该任务的所有资源
            resources = await session.execute(
                f"""
                SELECT * FROM generated_resources
                WHERE task_id = '{task_id}'
                ORDER BY agent_type, created_at
                """
            )

            result = []
            for resource in resources:
                result.append({
                    "id": str(resource.id),
                    "task_id": str(resource.task_id),
                    "agent_type": resource.agent_type,
                    "resource_type": resource.resource_type,
                    "content": resource.content,
                    "status": resource.status,
                    "created_at": resource.created_at.isoformat()
                })

            return result

    async def chat_with_agent(self, task_id: str, agent_id: str, message: str) -> Dict[str, str]:
        """
        与特定智能体对话
        """
        try:
            # 这里应该实现与特定智能体的对话逻辑
            # 目前返回一个简单的响应
            return {
                "reply": f"[{agent_id}] 收到消息: {message}",
                "agent_type": agent_id
            }
        except Exception as e:
            raise Exception(f"对话失败: {str(e)}")

    def _call_gemini_api(self, prompt: str) -> str:
        """
        调用 Gemini API
        """
        # Using mock data instead of Gemini for now
        # if not self.gemini_model:
        #     raise Exception("Gemini 模型未初始化")

        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API 调用失败: {str(e)}")
            raise Exception(f"Gemini API 调用失败: {str(e)}")

    async def _generate_content_with_gemini(self, agent_type: str, topic: str) -> dict:
        """
        使用 Gemini 生成特定智能体的内容
        """
        try:
            # 定义每个智能体的提示词模板
            prompts = {
                "professor": f"""你是一位资深的教育学教授，专门深入浅出地解释复杂概念。

主题：{topic}

请生成一份详细的教学文档，包含：
1. 标题（简洁明了）
2. 4-6个主要章节，每章节包含：
   - 清晰的章节标题
   - 详细的解释（300-500字）
   - 具体的例子
   - 与其他概念的关联

请确保内容深入浅出，适合有一定基础的学习者。""",

                "architect": f"""你是一位知识架构师，专门将复杂概念组织成清晰的知识结构。

主题：{topic}

请创建一个思维导图，包含：
1. 根节点（主题名称）
2. 3-4个主要分支
3. 每个分支下有3-4个子节点
4. 每个子节点下可以有2-3个细节节点

使用JSON格式返回，结构为：
{{
    "root": "主题名称",
    "children": [
        {{
            "name": "分支名称",
            "children": [
                {{
                    "name": "子节点名称",
                    "children": [
                        {{"name": "细节名称"}}
                    ]
                }}
            ]
        }}
    ]
}}""",

                "examiner": f"""你是一位专业考试设计专家，根据给定主题设计高质量的测验题。

主题：{topic}

请设计3道选择题，每道题包含：
1. 一个核心问题
2. 4个选项（A、B、C、D）
3. 正确答案的序号
4. 详细的解释

问题应该覆盖主题的关键概念，难度适中，能够检验学习者的理解程度。""",

                "director": f"""你是一位教育视频导演，设计生动的可视化教学内容。

主题：{topic}

请设计4个教学场景，每个场景包含：
1. 场景编号（1-4）
2. 场景标题
3. 视觉描述（画面内容）
4. 解说词（口语化的讲解）

场景应该循序渐进，从基础到进阶，适合视频演示。""",

                "hacker": f"""你是一位实战派技术专家，提供可运行的代码示例。

主题：{topic}

请创建一个Python代码实验，包含：
1. 有意义的标题
2. 简短描述（50-100字）
3. 完整可运行的代码（500-800字）
4. 预期输出结果
5. 2-3个扩展练习

代码应该实用、可理解，并附有详细注释。""",

                "reviewer": f"""你是一位教育内容评审专家，对生成的内容进行质量评估。

主题：{topic}

请对上述所有生成的内容进行评审，返回：
1. 幻觉风险评级（low/medium/high）
2. 质量评分（0-100）
3. 改进建议（2-3条）
4. 难度评估（简要说明）"""
            }

            # 获取对应智能体的提示词
            prompt = prompts.get(agent_type, f"请关于{topic}生成相关内容")

            # 直接使用回退数据，不调用 Gemini API
            # response_text = self._call_gemini_api(prompt)
            response_text = ""

            # 尝试解析 JSON 响应
            try:
                if agent_type in ["architect", "examiner", "reviewer"]:
                    # 这些智能体需要 JSON 格式的输出
                    content = json.loads(response_text)
                else:
                    # 其他智能体使用文本响应
                    content = {"content": response_text}
            except json.JSONDecodeError:
                # 如果 JSON 解析失败，使用原始文本
                content = {"content": response_text}

            return content

        except Exception as e:
            print(f"生成 {agent_type} 内容失败: {str(e)}")
            # 直接使用回退数据
            return self._get_fallback(agent_type, topic)

    def _get_fallback(self, agent_type: str, topic: str) -> dict:
        """AI 调用失败时的兜底 Mock 数据"""
        # 专门针对"Transformer 架构中的注意机制"的详细 Mock 数据
        if topic == "Transformer 架构中的注意机制":
            if agent_type == "professor":
                return {
                    "title": "深入理解：Transformer 架构中的注意机制",
                    "sections": [
                        {
                            "heading": "注意机制的核心概念",
                            "subsections": [
                                {
                                    "subheading": "起源与动机",
                                    "body": "2017年提出的Transformer架构中，注意机制是革命性创新。它解决了RNN序列建模的局限性，允许模型直接关注序列中任意位置的信息。这种机制模拟了人类认知中的注意力分配方式，使得模型能够学习到序列中不同部分之间的依赖关系。"
                                },
                                {
                                    "subheading": "认知科学基础",
                                    "body": "注意机制的哲学根源可追溯到认知心理学。在阅读句子时，我们会自然地关注与当前词最相关的词。例如，看到'我喜欢红色的'时，大脑会自动聚焦在'红色'上。这种选择性注意能力启发了研究者将其形式化。"
                                }
                            ]
                        },
                        {
                            "heading": "Scaled Dot-Product 注意力",
                            "subsections": [
                                {
                                    "subheading": "基本原理",
                                    "body": "Transformer使用Scaled Dot-Product注意力，通过计算Query、Key、Value之间的点积获得权重。将Query与所有Key进行点积，通过softmax归一化得到权重，再与Value加权求和。"
                                },
                                {
                                    "subheading": "缩放因子的作用",
                                    "body": "缩放因子（1/√d_k）用于防止点积过大导致梯度消失。当维度d_k较大时，点积的方差会增大，导致softmax进入梯度饱和区域。缩放因子使梯度保持在合理范围内，确保模型正常训练。"
                                }
                            ]
                        },
                        {
                            "heading": "多头注意力的架构设计",
                            "subsections": [
                                {
                                    "subheading": "并行处理的优势",
                                    "body": "多头注意力允许模型同时关注不同位置的不同表示子空间。每个头学习不同的注意力模式，有的关注语法结构，有的关注语义关系。这种并行处理增强了模型的表达能力。"
                                },
                                {
                                    "subheading": "实现细节",
                                    "body": "在GPT架构中，每个注意力层使用多头设计，多个头关注当前位置和前几个位置以保持局部连贯性。特定的头还用于处理特殊标记如[CLS]和[SEP]。"
                                }
                            ]
                        },
                        {
                            "heading": "应用场景与发展",
                            "subsections": [
                                {
                                    "subheading": "从Transformer到GPT",
                                    "body": "2018年OpenAI发布GPT，采用Transformer解码器架构，通过无监督预训练在各种NLP任务上取得突破。GPT-2（2019）证明了大规模预训练模型的威力，GPT-3（2020）参数量达1750亿，展现涌现能力。"
                                },
                                {
                                    "subheading": "现代优化技术",
                                    "body": "现代大型语言模型中，注意力机制发展出多种变体：稀疏注意力降低计算成本，分组注意力提高效率，核注意力捕捉非线性关系。这些优化在保持模型能力的同时提高了计算效率。"
                                }
                            ]
                        }
                    ],
                }
            elif agent_type == "architect":
                return {
                    "mindmap": {
                        "root": "root((Transformer 注意力机制))",
                        "children": [
                            {
                                "name": "核心概念",
                                "children": [
                                    {"name": "Q - Query (查询): 当前要匹配的信息"},
                                    {"name": "K - Key (键): 用于被匹配的信息"},
                                    {"name": "V - Value (值): 最终提取的信息内容"},
                                    {"name": "相似度度量: 计算 Q 与 K 的匹配程度"}
                                ]
                            },
                            {
                                "name": "数学计算流程",
                                "children": [
                                    {"name": "Scaled Dot-Product Attention"},
                                    {"name": "点积 (Dot Product): Q 乘以 K 的转置"},
                                    {"name": "缩放 (Scaling): 除以 sqrt(dk) 防止梯度消失"},
                                    {"name": "掩码 (Masking): 屏蔽未来信息 (Decoder)"},
                                    {"name": "归一化 (Softmax): 转化为概率分布"},
                                    {"name": "加权求和: 用概率对 V 进行加权综合"}
                                ]
                            },
                            {
                                "name": "结构分类",
                                "children": [
                                    {"name": "自注意力 Self-Attention"},
                                    {"name": "Encoder Self-Attention: 全向关注"},
                                    {"name": "Decoder Masked Self-Attention: 仅关注历史"},
                                    {"name": "交叉注意力 Cross-Attention"},
                                    {"name": "Encoder-Decoder Attention: 建立编码与解码的联系"},
                                    {"name": "多头注意力 Multi-Head Attention"},
                                    {"name": "多空间表达: 线性变换到多个低维子空间"},
                                    {"name": "并行计算: 增强模型捕捉多维度特征的能力"},
                                    {"name": "拼接与融合: Concat & Linear"}
                                ]
                            },
                            {
                                "name": "关键特性与优势",
                                "children": [
                                    {"name": "并行性 Parallelism: 解决 RNN 无法并行的问题"},
                                    {"name": "长程依赖 Long-range: 建模全局上下文"},
                                    {"name": "动态权重: 根据输入内容实时计算相关性"},
                                    {"name": "复杂度: [\"O(n² · d) n为序列长度\"]"}
                                ]
                            }
                        ]
                    }
                }
            elif agent_type == "examiner":
                return {
                    "questions": [
                        {
                            "question": "在Transformer的注意力机制中，使用缩放因子（1/√d_k）的主要目的是什么？",
                            "options": [
                                "加快计算速度",
                                "防止梯度消失",
                                "减少内存使用",
                                "提高模型容量"
                            ],
                            "answer": 1,
                            "explanation": "缩放因子防止点积过大导致softmax函数进入梯度平坦区域，有效避免梯度消失问题。"
                        },
                        {
                            "question": "多头注意力的主要优势是什么？",
                            "options": [
                                "减少计算复杂度",
                                "允许并行计算",
                                "从不同角度学习注意力模式",
                                "降低参数数量"
                            ],
                            "answer": 2,
                            "explanation": "多头注意力允许模型同时关注不同位置的不同表示子空间，每个头学习不同的注意力模式。"
                        },
                        {
                            "question": "在解码器中，为什么需要掩码注意力机制？",
                            "options": [
                                "防止信息泄露",
                                "保持自回归特性",
                                "提高训练效率",
                                "减少内存占用"
                            ],
                            "answer": 1,
                            "explanation": "掩码注意力防止当前位置关注未来信息，保持自回归特性，这是生成式任务的关键要求。"
                        }
                    ],
                }
            elif agent_type == "director":
                return {
                    "scenes": [
                        {
                            "scene_number": 1,
                            "title": "Transformer注意力机制详解",
                            "visual": "动画展示注意力权重如何分布",
                            "voiceover": "想象我们在读一个句子时，我们会自然地关注到与当前词最相关的词...",
                            "duration_seconds": 45,
                            "resources": [
                                {
                                    "type": "video",
                                    "title": "Attention in transformers, step-by-step | Deep Learning Chapter 6",
                                    "description": "这是 3Blue1Brown 深度学习系列教程的第 6 章。视频通过极其直观的动态数学可视化，一步步拆解了 Transformer 架构中的注意力机制（Attention Mechanism）",
                                    "thumbnail": "https://img.youtube.com/vi/eMlx5fFNoYc/maxresdefault.jpg",
                                    "url": "https://www.youtube.com/watch?v=eMlx5fFNoYc",
                                    "duration": "26:10",
                                    "platform": "YouTube"
                                }
                            ]
                        },
                        {
                            "scene_number": 2,
                            "title": "QKV机制可视化教程",
                            "visual": "三栏对比展示Q、K、V的作用",
                            "voiceover": "Query就像是当前词的问题，Key是所有词的标签，Value是所有词的内容...",
                            "duration_seconds": 60,
                            "resources": [
                                {
                                    "type": "video",
                                    "title": "Transformers Step-by-Step Explained (Attention Is All You Need)",
                                    "description": "这段视频用通俗易懂的语言和动画，逐步解释了经典论文《Attention Is All You Need》中的 Transformer 架构，并对比了它与传统模型的区别",
                                    "thumbnail": "https://img.youtube.com/vi/avjX3QrYkls/maxresdefault.jpg",
                                    "url": "https://www.youtube.com/watch?v=avjX3QrYkls",
                                    "duration": "10:03",
                                    "platform": "YouTube"
                                }
                            ]
                        },
                        {
                            "scene_number": 3,
                            "title": "多头注意力实战应用",
                            "visual": "动画展示多个并行头的注意力计算",
                            "voiceover": "每个头就像一个专家，从不同角度理解词之间的关系...",
                            "duration_seconds": 75,
                            "resources": [
                                {
                                    "type": "video",
                                    "title": "How Attention Mechanism Works in Transformer Architecture",
                                    "description": "这段视频更加侧重于从代码、矩阵维度变化以及大语言模型（如 GPT-2）的整机数据流（Data Flow）的视角，硬核拆解注意力机制在 Transformer 中的运作。",
                                    "thumbnail": "https://img.youtube.com/vi/KMHkbXzHn7s/maxresdefault.jpg",
                                    "url": "https://www.youtube.com/watch?v=KMHkbXzHn7s",
                                    "duration": "22:09",
                                    "platform": "YouTube"
                                }
                            ]
                        }
                    ],
                }
            elif agent_type == "hacker":
                return {
                    "title": "Transformer 注意机制 - PyTorch实现",
                    "description": "通过亲手实现注意机制来深入理解其工作原理",
                    "code": """\"\"
Transformer 注意机制 - PyTorch 实现
动手实现核心组件，加深理解
\"\"

import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class ScaledDotProductAttention(nn.Module):
    def __init__(self, d_k):
        super().__init__()
        self.d_k = d_k

    def forward(self, Q, K, V, mask=None):
        # 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        # 应用掩码（如果提供）
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        # 计算注意力权重
        attention_weights = F.softmax(scores, dim=-1)

        # 应用注意力权重到Value
        output = torch.matmul(attention_weights, V)

        return output, attention_weights

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads=8):
        super().__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"

        self.d_model = d_model
        self.d_k = d_model // num_heads
        self.num_heads = num_heads

        # 线性变换层
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)

        # 线性变换并分割多头
        Q = self.W_q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        # 计算注意力
        attention, weights = ScaledDotProductAttention(self.d_k)(Q, K, V, mask)

        # 合并多头
        attention = attention.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)

        # 输出变换
        output = self.W_o(attention)

        return output, weights

# 示例使用
if __name__ == "__main__":
    # 参数设置
    batch_size = 32
    seq_len = 10
    d_model = 512
    num_heads = 8

    # 创建随机输入
    x = torch.randn(batch_size, seq_len, d_model)

    # 创建多头注意力层
    mha = MultiHeadAttention(d_model, num_heads)

    # 计算输出
    output, attention_weights = mha(x, x, x)  # 自注意力

    print(f"输入形状: {x.shape}")
    print(f"输出形状: {output.shape}")
    print(f"注意力权重形状: {attention_weights.shape}")

    # 展示第一个序列第一个头的注意力权重
    print("\\n第一个序列第一个头的注意力权重：")
    print(attention_weights[0, 0][:5])  # 只展示前5个词的注意力""",
                    "expected_output": "输入形状: torch.Size([32, 10, 512])\n输出形状: torch.Size([32, 10, 512])\n注意力权重形状: torch.Size([32, 8, 10, 10])\n\n第一个序列第一个头的注意力权重：\ntensor([0.0988, 0.1102, 0.1245, 0.0989, 0.1024], grad=True)",
                    "exercises": [
                        "修改多头数量，观察对模型性能的影响",
                        "实现相对位置编码并添加到注意力计算中",
                        "比较不同注意力变体（如Additive Attention）的效果",
                        "可视化不同层的注意力权重分布"
                    ],
                }
            elif agent_type == "reviewer":
                return {
                    "hallucination_risk": "low",
                    "quality_score": 95,
                    "suggestions": [
                        "可以增加注意力可视化的实际案例，如展示BERT中不同层的注意力模式差异",
                        "建议添加更多数学推导的细节，特别是缩放因子的理论依据",
                        "可以扩展实验部分，增加与LSTM等传统模型的性能对比"
                    ],
                    "difficulty_assessment": "内容适合有一定深度学习基础的学习者，需要线性代数和PyTorch基础",
                }
        else:
            # 通用回退模板
            fallbacks = {
                "professor": {
                    "title": f"深入理解：{topic}",
                    "sections": [
                        {
                            "heading": "基础概念与原理",
                            "subsections": [
                                {
                                    "subheading": "核心定义",
                                    "body": f"{topic}是机器学习/AI领域的核心概念之一。在深入探讨之前，我们先建立对基础原理的清晰理解。"
                                },
                                {
                                    "subheading": "理论基础",
                                    "body": f"{topic}的数学基础建立在优化理论和线性代数之上。理解其中的数学推导对于掌握该概念至关重要。"
                                }
                            ]
                        },
                        {
                            "heading": "实践应用与案例分析",
                            "subsections": [
                                {
                                    "subheading": "应用场景",
                                    "body": f"在实际应用中，{topic}已经被广泛部署于各类场景。我们将通过具体案例来分析其工作原理。"
                                },
                                {
                                    "subheading": "常见误区",
                                    "body": "学习过程中最常遇到的困惑包括概念混淆、参数调优不当等问题。本节将逐一澄清。"
                                }
                            ]
                        }
                    ],
                },
                "architect": {
                    "mindmap": {
                        "root": topic,
                        "children": [
                            {"name": "基础理论", "children": [{"name": "数学原理"}, {"name": "核心定义"}]},
                            {"name": "算法实现", "children": [{"name": "Python示例"}, {"name": "优化技巧"}]},
                            {"name": "应用场景", "children": [{"name": "工业案例"}, {"name": "学术研究"}]},
                        ],
                    }
                },
                "examiner": {
                    "questions": [
                        {"question": f"关于{topic}，以下哪个描述最准确？", "options": ["选项A：描述1", "选项B：描述2", "选项C：描述3", "选项D：描述4"], "answer": 1, "explanation": "该选项准确概括了核心定义。"},
                        {"question": f"在{topic}的实践中，以下哪个步骤应该首先完成？", "options": ["参数调优", "数据预处理", "模型部署", "结果可视化"], "answer": 1, "explanation": "数据预处理是所有后续步骤的基础。"},
                        {"question": f"{topic}与相关概念的主要区别在于？", "options": ["计算速度", "理论基础", "应用领域", "以上都是"], "answer": 1, "explanation": "理论基础的差异是最本质的区别。"},
                    ],
                },
                "director": {
                    "scenes": [
                        {
                            "scene_number": 1,
                            "title": f"{topic}基础介绍",
                            "visual": "动画展示一个实际问题场景",
                            "voiceover": f"今天我们来探索{topic}。从一个直观的问题开始...",
                            "duration_seconds": 30,
                            "resources": [
                                {
                                    "type": "video",
                                    "title": f"{topic}基础介绍",
                                    "description": f"了解{topic}的基本概念、核心原理和应用场景",
                                    "thumbnail": "https://img.zcool.cn/community/03158e5d1b26e1a801215a95a458e7.jpg",
                                    "url": f"https://example.com/video/{topic}-intro",
                                    "duration": "10:00",
                                    "platform": "示例平台"
                                }
                            ]
                        },
                        {
                            "scene_number": 2,
                            "title": f"{topic}核心原理",
                            "visual": "逐步拆解核心算法流程",
                            "voiceover": f"让我们深入到{topic}的核心...",
                            "duration_seconds": 45,
                            "resources": [
                                {
                                    "type": "video",
                                    "title": f"{topic}核心原理详解",
                                    "description": f"深入理解{topic}的工作原理、数学基础和实现细节",
                                    "thumbnail": "https://img.zcool.cn/community/03158e5d1b26e1a801215a95a458e7.jpg",
                                    "url": f"https://example.com/video/{topic}-core",
                                    "duration": "15:00",
                                    "platform": "示例平台"
                                }
                            ]
                        },
                        {
                            "scene_number": 3,
                            "title": f"{topic}实战应用",
                            "visual": "实际案例演示和代码实现",
                            "voiceover": f"通过实际案例掌握{topic}的应用...",
                            "duration_seconds": 60,
                            "resources": [
                                {
                                    "type": "video",
                                    "title": f"{topic}实战应用",
                                    "description": f"通过实际案例学习{topic}的具体实现、最佳实践和行业应用",
                                    "thumbnail": "https://img.zcool.cn/community/03158e5d1b26e1a801215a95a458e7.jpg",
                                    "url": f"https://example.com/video/{topic}-demo",
                                    "duration": "20:00",
                                    "platform": "示例平台"
                                }
                            ]
                        }
                    ],
                },
                "hacker": {
                    "title": f"{topic} - Python代码实验",
                    "description": f"通过动手实践来理解{topic}的核心原理",
                    "code": f"""\"\"\"
{topic} - 动手实验
通过代码来直观理解核心概念
\"\"\"
import numpy as np
import matplotlib.pyplot as plt

def demonstrate_concept():
    \"\"\"演示{topic}的核心概念\"\"\"
    # ===== 步骤1: 准备数据 =====
    print("步骤1: 准备实验数据")
    x = np.linspace(-5, 5, 100)
    y = x ** 2  # 示例：二次函数

    # ===== 步骤2: 核心计算 =====
    print("步骤2: 执行核心计算")
    derivative = 2 * x  # 导数
    gradient = derivative[50]  # 某点的梯度

    print(f"在 x=0 处的梯度: {{gradient}}")

    # ===== 步骤3: 可视化 =====
    print("步骤3: 生成可视化图表")
    # plt.plot(x, y, label='f(x)')
    # plt.legend()
    # plt.show()

    return {{"min_value": np.min(y), "gradient_at_zero": float(gradient)}}

if __name__ == "__main__":
    result = demonstrate_concept()
    print(f"实验结果: {{result}}")
""",
                    "expected_output": "步骤1: 准备实验数据\n步骤2: 执行核心计算\n在 x=0 处的梯度: 0.0\n步骤3: 生成可视化图表\n实验结果: {'min_value': 0.0, 'gradient_at_zero': 0.0}",
                    "exercises": [
                        "修改函数定义，尝试其他函数如 y = x^3 观察梯度变化",
                        "添加噪声数据，观察对梯度计算的影响",
                    ],
                },
                "reviewer": {
                    "hallucination_risk": "low",
                    "quality_score": 85,
                    "suggestions": ["建议在教授文档中增加更多实际案例", "思维导图可以进一步细化第三级节点"],
                    "difficulty_assessment": "内容难度适中，适合有一定基础的学习者",
                },
            }
            return fallbacks.get(agent_type, {"message": f"Agent {agent_type} content placeholder for {topic}"})


    async def generate_for_agent(self, agent_type: str, topic: str, profile: Dict = None) -> Dict:
        """
        为特定智能体生成内容
        """
        # 直接使用回退数据，不调用 Gemini API
        # if self.gemini_model and topic != "Transformer 架构中的注意机制":
        #     try:
        #         content = await self._generate_content_with_gemini(agent_type, topic)
        #         return content
        #     except:
        #         pass  # 如果 Gemini 生成失败，使用回退数据

        # 使用回退数据
        return self._get_fallback(agent_type, topic)


generator = ContentGenerator()