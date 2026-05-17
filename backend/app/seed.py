# backend/app/seed.py
import asyncio
import uuid
from datetime import datetime
from app.core.database import engine, Base
from app.models.student import Student
from app.models.factory import GenerationTask, GeneratedResource
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def init_db():
    async with engine.begin() as conn:
        # 强制创建所有表（开发环境测试用）
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # 检查并创建一个测试用户
        from sqlalchemy import select
        result = await session.execute(select(Student).where(Student.email == "test@edunexus.com"))
        test_user = result.scalar_one_or_none()

        if test_user is None:
            test_user = Student(
                email="test@edunexus.com",
                username="TestUser",
                hashed_password=get_password_hash("123456"), # 密码为 123456
                onboarding_completed=False
            )
            session.add(test_user)
            await session.commit()
            print("✅ 创建了测试用户: test@edunexus.com / 密码: 123456")
        else:
            print("✅ 测试用户已存在: test@edunexus.com / 密码: 123456")

        # 创建一个关于 Transformer 注意机制的 Mock 生成任务
        task_id = uuid.uuid4()
        transformer_task = GenerationTask(
            id=task_id,
            student_id=test_user.id,
            topic="Transformer 架构中的注意机制",
            status="completed",
            agents_status={
                "manager": "success",
                "professor": "success",
                "architect": "success",
                "examiner": "success",
                "director": "success",
                "hacker": "success",
                "reviewer": "success"
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(transformer_task)
        await session.commit()

        # 添加各种类型的 Mock 资源
        resources = [
            # 教授文档
            {
                "task_id": task_id,
                "student_id": test_user.id,
                "agent_type": "professor",
                "resource_type": "document",
                "content": {
                    "title": "深入理解：Transformer 架构中的注意机制",
                    "sections": [
                        {
                            "heading": "注意机制的起源与动机",
                            "body": "在2017年提出的Transformer架构中，注意机制（Attention）是革命性的创新。它解决了RNN序列建模的局限性，允许模型直接关注序列中任意位置的信息。这种机制模拟了人类认知中的注意力分配方式，使得模型能够学习到序列中不同部分之间的依赖关系。"
                        },
                        {
                            "heading": "Scaled Dot-Product 注意力",
                            "body": "Transformer使用Scaled Dot-Product注意力，它通过计算查询（Query）、键（Key）和值（Value）之间的点积来获得注意力权重。具体来说，将Query与所有Key进行点积，通过softmax归一化得到权重，再与Value加权求和。缩放因子（1/√d_k）用于防止点积过大导致梯度消失。"
                        },
                        {
                            "heading": "多头注意力的优势",
                            "body": "多头注意力（Multi-Head Attention）允许模型同时关注不同位置的不同表示子空间。每个头学习不同的注意力模式，有的关注语法结构，有的关注语义关系。这种并行处理增强了模型的表达能力，使得Transformer能够捕捉更复杂的序列关系。"
                        },
                        {
                            "heading": "自注意力与掩码",
                            "body": "自注意力（Self-Attention）允许序列中的每个位置都关注序列中的所有位置。在解码器中，掩码注意力防止当前位置关注未来信息，保持自回归特性。这种设计使Transformer在机器翻译、文本生成等任务中表现出色。"
                        }
                    ]
                },
                "status": "completed"
            },
            # 思维导图
            {
                "task_id": task_id,
                "student_id": test_user.id,
                "agent_type": "architect",
                "resource_type": "mindmap",
                "content": {
                    "mindmap": {
                        "root": "Transformer 注意机制",
                        "children": [
                            {
                                "name": "理论基础",
                                "children": [
                                    {"name": "注意力分数", "children": [{"name": "点积运算"}, {"name": "缩放因子"}, {"name": "Softmax"}]},
                                    {"name": "Query-Key-Value", "children": [{"name": "矩阵表示"}, {"name": "维度匹配"}]},
                                    {"name": "注意力权重", "children": [{"name": "概率分布"}, {"name": "权重解释"}]}
                                ]
                            },
                            {
                                "name": "多头注意力",
                                "children": [
                                    {"name": "并行头设计", "children": [{"name": "参数共享"}, {"name": "特征分割"}]},
                                    {"name": "输出合并", "children": [{"name": "拼接操作"}, {"name": "线性变换"}]},
                                    {"name": "头的重要性", "children": [{"name": "不同视角"}, {"name": "互补信息"}]}
                                ]
                            },
                            {
                                "name": "应用实现",
                                "children": [
                                    {"name": "位置编码", "children": [{"name": "正弦编码"}, {"name": "绝对位置"}]},
                                    {"name": "残差连接", "children": [{"name": "梯度流动"}, {"name": "信息保持"}]},
                                    {"name": "层归一化", "children": [{"name": "稳定训练"}, {"name": "收敛加速"}]}
                                ]
                            },
                            {
                                "name": "实际应用",
                                "children": [
                                    {"name": "机器翻译", "children": [{"name": "跨语言对齐"}, {"name": "长距离依赖"}]},
                                    {"name": "文本生成", "children": [{"name": "上下文理解"}, {"name": "连贯性保证"}]},
                                    {"name": "图像处理", "children": [{"name": "ViT架构"}, {"name": "特征聚合"}]}
                                ]
                            }
                        ]
                    }
                },
                "status": "completed"
            },
            # 选择题
            {
                "task_id": task_id,
                "student_id": test_user.id,
                "agent_type": "examiner",
                "resource_type": "quiz",
                "content": {
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
                            "explanation": "缩放因子用于防止点积值过大导致softmax函数进入梯度饱和区域，从而避免梯度消失问题。"
                        },
                        {
                            "question": "多头注意力机制相比单头注意力的主要优势是什么？",
                            "options": [
                                "计算效率更高",
                                "能够关注不同表示子空间",
                                "减少参数数量",
                                "简化实现难度"
                            ],
                            "answer": 1,
                            "explanation": "多头注意力允许模型同时学习不同的注意力模式，每个头关注不同的表示子空间，从而获得更全面的理解。"
                        },
                        {
                            "question": "在Transformer解码器中，为什么需要掩码注意力机制？",
                            "options": [
                                "提高推理速度",
                                "防止信息泄露",
                                "减少计算复杂度",
                                "增强正则化效果"
                            ],
                            "answer": 1,
                            "explanation": "掩码注意力防止当前位置关注到未来位置的信息，保持自回归特性，确保预测时的因果约束。"
                        }
                    ]
                },
                "status": "completed"
            },
            # 视频脚本（包含高质量视频链接）
            {
                "task_id": task_id,
                "student_id": test_user.id,
                "agent_type": "director",
                "resource_type": "video_script",
                "content": {
                    "scenes": [
                        {
                            "scene_number": 1,
                            "title": "注意力机制的诞生",
                            "visual": "动画展示从CNN到RNN再到Transformer的演进过程，突出注意力机制的革命性",
                            "voiceover": "在2017年，Google的研究团队提出了Transformer架构，彻底改变了NLP领域。其核心创新就是注意力机制...",
                            "duration_seconds": 45,
                            "resources": [
                                {
                                    "type": "video",
                                    "title": "The Illustrated Transformer: Attention Mechanism Explained",
                                    "url": "https://www.youtube.com/watch/wjZQCy8mrxA",
                                    "thumbnail": "https://img.youtube.com/vi/wjZQCy8mrxA/maxresdefault.jpg",
                                    "duration": "15:32",
                                    "platform": "YouTube",
                                    "description": "深入浅出地解释Transformer中的注意力机制，包含动画演示"
                                },
                                {
                                    "type": "video",
                                    "title": "Transformer Architecture: Attention Mechanism",
                                    "url": "https://www.youtube.com/watch/9sY3TCs4N-8",
                                    "thumbnail": "https://img.youtube.com/vi/9sY3TCs4N-8/maxresdefault.jpg",
                                    "duration": "22:45",
                                    "platform": "YouTube",
                                    "description": "详细讲解Transformer的注意力机制实现原理"
                                }
                            ]
                        },
                        {
                            "scene_number": 2,
                            "title": "注意力分数的计算",
                            "visual": "动态演示Query、Key、Value三个矩阵的乘法过程，以及softmax的归一化效果",
                            "voiceover": "注意力分数通过Query和Key的点积计算，经过缩放和softmax处理，最后与Value加权求和...",
                            "duration_seconds": 60,
                            "resources": [
                                {
                                    "type": "video",
                                    "title": "Visualizing Attention in Neural Networks",
                                    "url": "https://www.youtube.com/watch/7EsRwe4JRTo",
                                    "thumbnail": "https://img.youtube.com/vi/7EsRwe4JRTo/maxresdefault.jpg",
                                    "duration": "18:20",
                                    "platform": "YouTube",
                                    "description": "通过可视化帮助理解注意力机制的工作原理"
                                }
                            ]
                        },
                        {
                            "scene_number": 3,
                            "title": "多头注意力的威力",
                            "visual": "同时展示8个注意力头的不同关注模式，每个头突出不同的文本特征",
                            "voiceover": "多头注意力让模型能够同时关注不同方面的信息。看，每个头都在学习不同的注意力模式...",
                            "duration_seconds": 75,
                            "resources": [
                                {
                                    "type": "video",
                                    "title": "Multi-Head Attention Explained",
                                    "url": "https://www.youtube.com/watch/GABz3zV3it0",
                                    "thumbnail": "https://img.youtube.com/vi/GABz3zV3it0/maxresdefault.jpg",
                                    "duration": "12:45",
                                    "platform": "YouTube",
                                    "description": "详解多头注意力的设计和实现"
                                }
                            ]
                        },
                        {
                            "scene_number": 4,
                            "title": "实际应用展示",
                            "visual": "展示BERT、GPT等模型如何利用注意力机制，以及在实际任务中的表现",
                            "voiceover": "基于注意力的模型已经在机器翻译、文本生成、问答系统等任务上取得了突破性成果...",
                            "duration_seconds": 40,
                            "resources": [
                                {
                                    "type": "video",
                                    "title": "Transformer Models in Practice",
                                    "url": "https://www.bilibili.com/video/BV1Jt411d7hu",
                                    "thumbnail": "https://pic.bilibili.com/cover/d7hu.jpg",
                                    "duration": "45:30",
                                    "platform": "Bilibili",
                                    "description": "实践案例：Transformer模型在实际应用中的表现"
                                }
                            ]
                        }
                    ]
                },
                "status": "completed"
            },
            # 代码实验
            {
                "task_id": task_id,
                "student_id": test_user.id,
                "agent_type": "hacker",
                "resource_type": "code_lab",
                "content": {
                    "title": "Transformer 注意机制 - 代码实验",
                    "description": "通过PyTorch实现和可视化注意力机制，深入理解其工作原理",
                    "code": '''"""
Transformer 注意机制详解实验
通过PyTorch实现和可视化，深入理解Self-Attention和Multi-Head Attention
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional

def scaled_dot_product_attention(query, key, value, mask: Optional[torch.Tensor] = None):
    """实现Scaled Dot-Product注意力机制"""
    d_k = query.size(-1)
    # 计算注意力分数
    scores = torch.matmul(query, key.transpose(-2, -1)) / np.sqrt(d_k)

    # 应用掩码（如果需要）
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)

    # 计算注意力权重
    attention_weights = F.softmax(scores, dim=-1)

    # 加权求和
    output = torch.matmul(attention_weights, value)

    return output, attention_weights

class SelfAttention(nn.Module):
    """自注意力层"""
    def __init__(self, embed_dim: int, dropout: float = 0.1):
        super().__init__()
        self.embed_dim = embed_dim

        # 线性变换层
        self.query = nn.Linear(embed_dim, embed_dim)
        self.key = nn.Linear(embed_dim, embed_dim)
        self.value = nn.Linear(embed_dim, embed_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask: Optional[torch.Tensor] = None):
        batch_size, seq_len, embed_dim = x.size()

        # 获取Q, K, V
        Q = self.query(x)  # [batch, seq_len, embed_dim]
        K = self.key(x)    # [batch, seq_len, embed_dim]
        V = self.value(x)  # [batch, seq_len, embed_dim]

        # 计算注意力
        attention_output, attention_weights = scaled_dot_product_attention(Q, K, V, mask)

        return attention_output, attention_weights

class MultiHeadAttention(nn.Module):
    """多头注意力层"""
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert embed_dim % num_heads == 0

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        self.heads = nn.ModuleList([
            SelfAttention(embed_dim, dropout) for _ in range(num_heads)
        ])

        self.output_projection = nn.Linear(embed_dim, embed_dim)

    def forward(self, x, mask: Optional[torch.Tensor] = None):
        # 并行计算多个头的注意力
        head_outputs = []
        attention_weights = []

        for head in self.heads:
            output, weights = head(x, mask)
            head_outputs.append(output)
            attention_weights.append(weights)

        # 拼接头的输出
        concat_output = torch.cat(head_outputs, dim=-1)
        # 线性变换
        output = self.output_projection(concat_output)

        # 平均化注意力权重
        avg_attention = torch.stack(attention_weights).mean(dim=0)

        return output, avg_attention

def demonstrate_attention_mechanism():
    """演示注意力机制的工作原理"""
    print("=== Transformer 注意力机制实验 ===\\n")

    # 创建示例文本
    text = "The cat sat on the mat because it was tired"
    tokens = text.split()
    vocab_size = len(tokens)
    embed_dim = 64
    seq_len = len(tokens)

    print(f"示例文本: {text}")
    print(f"词汇表大小: {vocab_size}")
    print(f"嵌入维度: {embed_dim}")
    print(f"序列长度: {seq_len}\\n")

    # 1. 创建词嵌入
    embedding = nn.Embedding(vocab_size, embed_dim)
    x = embedding(torch.arange(seq_len))  # [seq_len, embed_dim]
    x = x.unsqueeze(0)  # [1, seq_len, embed_dim]

    print("步骤1: 创建词嵌入")
    print(f"输入形状: {x.shape}\\n")

    # 2. 测试自注意力
    print("步骤2: 测试自注意力机制")
    self_attention = SelfAttention(embed_dim)
    self_attn_output, self_attn_weights = self_attention(x)

    print(f"自注意力输出形状: {self_attn_output.shape}")
    print(f"注意力权重形状: {self_attn_weights.shape}")
    print(f"权重行和（应该为1）: {self_attn_weights.sum(dim=-1)}\\n")

    # 3. 测试多头注意力
    print("步骤3: 测试多头注意力机制")
    num_heads = 8
    multi_head_attn = MultiHeadAttention(embed_dim, num_heads)
    multi_head_output, multi_head_weights = multi_head_attn(x)

    print(f"多头注意力输出形状: {multi_head_output.shape}")
    print(f"多头注意力权重形状: {multi_head_weights.shape}")
    print(f"每个头的维度: {embed_dim // num_heads}\\n")

    # 4. 展示注意力模式
    print("步骤4: 分析注意力模式")
    print("自注意力权重第一行（关注第一个词'The'）:")
    for i, weight in enumerate(self_attn_weights[0, 0]):
        print(f"  {tokens[i]}: {weight.item():.3f}")

    print("\\n多头注意力平均权重（第一行）:")
    for i, weight in enumerate(multi_head_weights[0, 0]):
        print(f"  {tokens[i]}: {weight.item():.3f}")

    # 5. 测试掩码注意力
    print("\\n步骤5: 测试掩码注意力（模拟解码器场景）")
    mask = torch.ones(seq_len, seq_len)
    for i in range(seq_len):
        mask[i, i+1:] = 0  # 掩码未来位置

    masked_output, masked_weights = self_attention(x, mask)
    print("掩码后第一个词的注意力权重（不应该关注后面的词）:")
    for i, weight in enumerate(masked_weights[0, 0]):
        print(f"  {tokens[i]}: {weight.item():.3f}")

    # 6. 权重可视化（可选）
    print("\\n步骤6: 注意力权重可视化")
    print("注意权重矩阵显示了每个词关注其他词的程度。")
    print("对角线上的高值表示词更关注自身，而横线上的高值可能表示关注关系。")

    # 7. 总结
    print("\\n=== 实验总结 ===")
    print("1. 自注意力允许序列中的每个位置关注所有位置")
    print("2. 注意力权重表示词之间的关联强度")
    print("3. 多头注意力捕捉不同类型的依赖关系")
    print("4. 掩码注意力确保自回归约束")

    return {
        "input_tokens": tokens,
        "self_attention_weights": self_attn_weights,
        "multi_head_attention_weights": multi_head_weights,
        "masked_attention_weights": masked_weights
    }

if __name__ == "__main__":
    results = demonstrate_attention_mechanism()
    print(f"\\n实验完成！返回了 {len(results)} 个结果。")
''',
                    "expected_output": '''=== Transformer 注意力机制实验 ===

示例文本: The cat sat on the mat because it was tired
词汇表大小: 8
嵌入维度: 64
序列长度: 10

步骤1: 创建词嵌入
输入形状: torch.Size([1, 10, 64])

步骤2: 测试自注意力机制
自注意力输出形状: torch.Size([1, 10, 64])
注意力权重形状: torch.Size([1, 10, 10])
权重行和（应该为1）: tensor([[1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000,
         1.0000]])

步骤3: 测试多头注意力机制
多头注意力输出形状: torch.Size([1, 10, 64])
多头注意力权重形状: torch.Size([1, 10, 10])
每个头的维度: 8

步骤4: 分析注意力模式
自注意力权重第一行（关注第一个词'The'）:
  The: 0.112
  cat: 0.098
  sat: 0.105
  on: 0.102
  the: 0.099
  mat: 0.104
  because: 0.100
  it: 0.110
  was: 0.106
  tired: 0.064

多头注意力平均权重（第一行）:
  The: 0.112
  cat: 0.098
  sat: 0.105
  on: 0.102
  the: 0.099
  mat: 0.104
  because: 0.100
  it: 0.110
  was: 0.106
  tired: 0.064

步骤5: 测试掩码注意力（模拟解码器场景）
掩码后第一个词的注意力权重（不应该关注后面的词）:
  The: 1.000
  cat: 0.000
  sat: 0.000
  on: 0.000
  the: 0.000
  mat: 0.000
  because: 0.000
  it: 0.000
  was: 0.000
  tired: 0.000

步骤6: 注意力权重可视化
注意权重矩阵显示了每个词关注其他词的程度。
对角线上的高值表示词更关注自身，而横线上的高值可能表示关注关系。

=== 实验总结 ===
1. 自注意力允许序列中的每个位置关注所有位置
2. 注意力权重表示词之间的关联强度
3. 多头注意力捕捉不同类型的依赖关系
4. 掩码注意力确保自回归约束

实验完成！返回了 4 个结果。''',
                    "exercises": [
                        "修改嵌入维度，观察对注意力模式的影响",
                        "实现相对位置编码并添加到注意力机制中",
                        "比较不同数量的头的注意力效果的差异",
                        "尝试不同的注意力变体，如Additive Attention"
                    ]
                },
                "status": "completed"
            },
            # 质量评估报告
            {
                "task_id": task_id,
                "student_id": test_user.id,
                "agent_type": "reviewer",
                "resource_type": "review_report",
                "content": {
                    "hallucination_risk": "low",
                    "quality_score": 95,
                    "suggestions": [
                        "可以增加注意力可视化的实际案例，如展示BERT中不同层的注意力模式差异",
                        "建议添加更多数学推导的细节，特别是缩放因子的理论依据",
                        "可以扩展实验部分，增加与LSTM等传统模型的性能对比"
                    ],
                    "difficulty_assessment": "内容适合有一定深度学习基础的学习者，需要线性代数和PyTorch基础"
                },
                "status": "completed"
            }
        ]

        # 批量添加资源
        for resource_data in resources:
            resource = GeneratedResource(**resource_data)
            session.add(resource)

        await session.commit()
        print("✅ 已添加 Transformer 注意机制 Mock 数据")
        print("📹 包含 5 个高质量视频资源:")
        print("   1. The Illustrated Transformer - 15:32")
        print("   2. Transformer Architecture - 22:45")
        print("   3. Visualizing Attention - 18:20")
        print("   4. Multi-Head Attention Explained - 12:45")
        print("   5. Transformer Models in Practice - 45:30 (Bilibili)")

    print("✅ 数据库表已创建，测试账号: test@edunexus.com / 密码: 123456")

if __name__ == "__main__":
    asyncio.run(init_db())