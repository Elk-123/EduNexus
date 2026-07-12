"""
共享 Fallback 数据 — v2 Agent LLM 调用失败时的兜底 Mock 数据
格式与 v1.0.0 ContentGenerator._get_fallback() 完全对齐，保证前端正常渲染
"""
from typing import Dict, Any


def get_fallback_content(agent_type: str, topic: str) -> Dict[str, Any]:
    """返回 v1 兼容格式的 mock 内容"""

    if agent_type == "manager":
        return {
            "tasks": [
                f"确定「{topic}」的教学目标和核心知识点",
                f"设计「{topic}」的课程大纲与知识结构",
                f"编写「{topic}」的详细教学内容与示例",
                f"创建「{topic}」的评估题目和答案",
                f"制作「{topic}」的教学视频脚本",
                f"开发「{topic}」的互动练习与代码案例",
                f"审核并优化「{topic}」的全部教学材料",
            ],
            "priority": ["professor", "architect", "examiner", "director", "hacker", "reviewer"],
            "coordination_notes": [
                "教授智能体应在架构师之前生成基础内容",
                "考官智能体应基于教授的内容设计题目",
                "导演智能体需要基于架构师的结构制作脚本",
            ],
        }

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

    if agent_type == "architect":
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

    if agent_type == "examiner":
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

    if agent_type == "director":
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

    if agent_type == "hacker":
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

    if agent_type == "reviewer":
        return {
            "hallucination_risk": "low",
            "quality_score": 85,
            "suggestions": [
                "建议在教授文档中增加更多实际案例，帮助学习者建立直观理解",
                "思维导图可以进一步细化第三级节点，增强知识结构的完整性",
                "代码实验部分可以增加更多交互式练习，提升动手实践的效果",
            ],
            "difficulty_assessment": "内容难度适中，适合有一定基础的学习者。建议初学者先补充相关前置知识。",
        }

    # 未知 agent_type
    return {"message": f"Agent '{agent_type}' fallback content for topic: {topic}"}
