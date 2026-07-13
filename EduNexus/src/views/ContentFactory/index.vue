<!-- src/views/ContentFactory/index.vue -->
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  BrainCircuit, FileText, GitFork, ClipboardCheck, Video, Code2, ShieldCheck
} from 'lucide-vue-next'
import TopicInput from './components/TopicInput.vue'
import AgentTerminal from './components/AgentTerminal.vue'
import ResourceDisplay from './components/ResourceDisplay.vue'
import AgentStatusCard from './components/AgentStatusCard.vue'
import AgentDetailView from './components/AgentDetailView.vue'
import { useFactoryStore } from '@/stores/factoryStore'
import type { GeneratedResource } from '@/types/factory'

const route = useRoute()
const factoryStore = useFactoryStore()

// 从URL参数获取默认标签
const defaultTab = computed(() => {
  const tab = route.query.tab as string
  const tabMapping: Record<string, string> = {
    'professor': 'professor',
    'architect': 'mindmap',
    'examiner': 'quiz',
    'director': 'video',
    'hacker': 'code'
  }
  return tabMapping[tab] || 'professor'
})

// 智能体定义
const agentDefs = [
  { id: 'manager', name: '主控中枢', role: 'Manager', icon: BrainCircuit, color: 'text-purple-400' },
  { id: 'professor', name: '教授智能体', role: 'Professor', icon: FileText, color: 'text-blue-400' },
  { id: 'architect', name: '架构师智能体', role: 'Architect', icon: GitFork, color: 'text-orange-400' },
  { id: 'examiner', name: '考官智能体', role: 'Examiner', icon: ClipboardCheck, color: 'text-pink-400' },
  { id: 'director', name: '导演智能体', role: 'Director', icon: Video, color: 'text-cyan-400' },
  { id: 'hacker', name: '极客智能体', role: 'Hacker', icon: Code2, color: 'text-green-400' },
  { id: 'reviewer', name: '质量审查', role: 'Reviewer', icon: ShieldCheck, color: 'text-red-400' },
]

const selectedAgent = ref<any>(null)

// 从 store 状态推导智能体状态列表
const agents = computed(() =>
  agentDefs.map((def) => {
    const statusFromStore = factoryStore.agentsStatus[def.id]
    const status = (statusFromStore || 'idle') as 'idle' | 'running' | 'success' | 'error'
    return {
      ...def,
      status,
    }
  })
)

const isGenerating = computed(() => factoryStore.isGenerating)
const currentTopic = computed(() => factoryStore.currentTopic)
const logs = computed(() => factoryStore.logs)

// ═══════════════════════════════════════════════════════════
//  [已注释] v1.0 getMockResources — 保留兼容，改用 v2.0 API 返回真实数据
// ═══════════════════════════════════════════════════════════
/*
function _v1_getMockResources(topic: string): GeneratedResource[] {
  const taskId = 'mock-task-' + Date.now()
  // 针对 "Transformer 架构中的注意机制" 使用后端完全一致的数据
  if (topic === 'Transformer 架构中的注意机制') {
    return [
      {
        id: 'mock-prof-' + Date.now(),
        task_id: taskId,
        agent_type: 'professor',
        resource_type: 'document',
        content: {
          title: '深入理解：Transformer 架构中的注意机制',
          sections: [
            {
              heading: '注意机制的核心概念',
              subsections: [
                { subheading: '起源与动机', body: '2017年提出的Transformer架构中，注意机制是革命性创新。它解决了RNN序列建模的局限性，允许模型直接关注序列中任意位置的信息。这种机制模拟了人类认知中的注意力分配方式，使得模型能够学习到序列中不同部分之间的依赖关系。' },
                { subheading: '认知科学基础', body: '注意机制的哲学根源可追溯到认知心理学。在阅读句子时，我们会自然地关注与当前词最相关的词。例如，看到\'我喜欢红色的\'时，大脑会自动聚焦在\'红色\'上。这种选择性注意能力启发了研究者将其形式化。' },
              ]
            },
            {
              heading: 'Scaled Dot-Product 注意力',
              subsections: [
                { subheading: '基本原理', body: 'Transformer使用Scaled Dot-Product注意力，通过计算Query、Key、Value之间的点积获得权重。将Query与所有Key进行点积，通过softmax归一化得到权重，再与Value加权求和。' },
                { subheading: '缩放因子的作用', body: '缩放因子（1/√d_k）用于防止点积过大导致梯度消失。当维度d_k较大时，点积的方差会增大，导致softmax进入梯度饱和区域。缩放因子使梯度保持在合理范围内，确保模型正常训练。' },
              ]
            },
            {
              heading: '多头注意力的架构设计',
              subsections: [
                { subheading: '并行处理的优势', body: '多头注意力允许模型同时关注不同位置的不同表示子空间。每个头学习不同的注意力模式，有的关注语法结构，有的关注语义关系。这种并行处理增强了模型的表达能力。' },
                { subheading: '实现细节', body: '在GPT架构中，每个注意力层使用多头设计，多个头关注当前位置和前几个位置以保持局部连贯性。特定的头还用于处理特殊标记如[CLS]和[SEP]。' },
              ]
            },
            {
              heading: '应用场景与发展',
              subsections: [
                { subheading: '从Transformer到GPT', body: '2018年OpenAI发布GPT，采用Transformer解码器架构，通过无监督预训练在各种NLP任务上取得突破。GPT-2（2019）证明了大规模预训练模型的威力，GPT-3（2020）参数量达1750亿，展现涌现能力。' },
                { subheading: '现代优化技术', body: '现代大型语言模型中，注意力机制发展出多种变体：稀疏注意力降低计算成本，分组注意力提高效率，核注意力捕捉非线性关系。这些优化在保持模型能力的同时提高了计算效率。' },
              ]
            },
          ],
        },
        status: 'completed'
      },
      {
        id: 'mock-arch-' + Date.now(),
        task_id: taskId,
        agent_type: 'architect',
        resource_type: 'mindmap',
        content: {
          mindmap: {
            root: 'root((Transformer 注意力机制))',
            children: [
              {
                name: '核心概念',
                children: [
                  { name: 'Q - Query (查询): 当前要匹配的信息' },
                  { name: 'K - Key (键): 用于被匹配的信息' },
                  { name: 'V - Value (值): 最终提取的信息内容' },
                  { name: '相似度度量: 计算 Q 与 K 的匹配程度' },
                ]
              },
              {
                name: '数学计算流程',
                children: [
                  { name: 'Scaled Dot-Product Attention' },
                  { name: '点积 (Dot Product): Q 乘以 K 的转置' },
                  { name: '缩放 (Scaling): 除以 sqrt(dk) 防止梯度消失' },
                  { name: '掩码 (Masking): 屏蔽未来信息 (Decoder)' },
                  { name: '归一化 (Softmax): 转化为概率分布' },
                  { name: '加权求和: 用概率对 V 进行加权综合' },
                ]
              },
              {
                name: '结构分类',
                children: [
                  { name: '自注意力 Self-Attention' },
                  { name: 'Encoder Self-Attention: 全向关注' },
                  { name: 'Decoder Masked Self-Attention: 仅关注历史' },
                  { name: '交叉注意力 Cross-Attention' },
                  { name: 'Encoder-Decoder Attention: 建立编码与解码的联系' },
                  { name: '多头注意力 Multi-Head Attention' },
                  { name: '多空间表达: 线性变换到多个低维子空间' },
                  { name: '并行计算: 增强模型捕捉多维度特征的能力' },
                  { name: '拼接与融合: Concat & Linear' },
                ]
              },
              {
                name: '关键特性与优势',
                children: [
                  { name: '并行性 Parallelism: 解决 RNN 无法并行的问题' },
                  { name: '长程依赖 Long-range: 建模全局上下文' },
                  { name: '动态权重: 根据输入内容实时计算相关性' },
                  { name: '复杂度: O(n² · d) n为序列长度' },
                ]
              },
            ]
          }
        },
        status: 'completed'
      },
      {
        id: 'mock-exam-' + Date.now(),
        task_id: taskId,
        agent_type: 'examiner',
        resource_type: 'quiz',
        content: {
          questions: [
            {
              question: '在Transformer的注意力机制中，使用缩放因子（1/√d_k）的主要目的是什么？',
              options: ['加快计算速度', '防止梯度消失', '减少内存使用', '提高模型容量'],
              answer: 1,
              explanation: '缩放因子防止点积过大导致softmax函数进入梯度平坦区域，有效避免梯度消失问题。'
            },
            {
              question: '多头注意力的主要优势是什么？',
              options: ['减少计算复杂度', '允许并行计算', '从不同角度学习注意力模式', '降低参数数量'],
              answer: 2,
              explanation: '多头注意力允许模型同时关注不同位置的不同表示子空间，每个头学习不同的注意力模式。'
            },
            {
              question: '在解码器中，为什么需要掩码注意力机制？',
              options: ['防止信息泄露', '保持自回归特性', '提高训练效率', '减少内存占用'],
              answer: 1,
              explanation: '掩码注意力防止当前位置关注未来信息，保持自回归特性，这是生成式任务的关键要求。'
            },
          ],
        },
        status: 'completed'
      },
      {
        id: 'mock-dir-' + Date.now(),
        task_id: taskId,
        agent_type: 'director',
        resource_type: 'video_script',
        content: {
          scenes: [
            {
              scene_number: 1,
              title: 'Transformer注意力机制详解',
              visual: '动画展示注意力权重如何分布',
              voiceover: '想象我们在读一个句子时，我们会自然地关注到与当前词最相关的词...',
              duration_seconds: 45,
              resources: [
                { type: 'video', title: 'Attention in transformers, step-by-step | Deep Learning Chapter 6', description: '这是 3Blue1Brown 深度学习系列教程的第 6 章。视频通过极其直观的动态数学可视化，一步步拆解了 Transformer 架构中的注意力机制（Attention Mechanism）', thumbnail: 'https://img.youtube.com/vi/eMlx5fFNoYc/maxresdefault.jpg', url: 'https://www.youtube.com/watch?v=eMlx5fFNoYc', duration: '26:10', platform: 'YouTube' },
              ]
            },
            {
              scene_number: 2,
              title: 'QKV机制可视化教程',
              visual: '三栏对比展示Q、K、V的作用',
              voiceover: 'Query就像是当前词的问题，Key是所有词的标签，Value是所有词的内容...',
              duration_seconds: 60,
              resources: [
                { type: 'video', title: 'Transformers Step-by-Step Explained (Attention Is All You Need)', description: '这段视频用通俗易懂的语言和动画，逐步解释了经典论文《Attention Is All You Need》中的 Transformer 架构，并对比了它与传统模型的区别', thumbnail: 'https://img.youtube.com/vi/avjX3QrYkls/maxresdefault.jpg', url: 'https://www.youtube.com/watch?v=avjX3QrYkls', duration: '10:03', platform: 'YouTube' },
              ]
            },
            {
              scene_number: 3,
              title: '多头注意力实战应用',
              visual: '动画展示多个并行头的注意力计算',
              voiceover: '每个头就像一个专家，从不同角度理解词之间的关系...',
              duration_seconds: 75,
              resources: [
                { type: 'video', title: 'How Attention Mechanism Works in Transformer Architecture', description: '这段视频更加侧重于从代码、矩阵维度变化以及大语言模型（如 GPT-2）的整机数据流（Data Flow）的视角，硬核拆解注意力机制在 Transformer 中的运作。', thumbnail: 'https://img.youtube.com/vi/KMHkbXzHn7s/maxresdefault.jpg', url: 'https://www.youtube.com/watch?v=KMHkbXzHn7s', duration: '22:09', platform: 'YouTube' },
              ]
            },
          ],
        },
        status: 'completed'
      },
      {
        id: 'mock-hack-' + Date.now(),
        task_id: taskId,
        agent_type: 'hacker',
        resource_type: 'code_lab',
        content: {
          title: 'Transformer 注意机制 - PyTorch实现',
          description: '通过亲手实现注意机制来深入理解其工作原理',
          code: `"""
Transformer 注意机制 - PyTorch 实现
动手实现核心组件，加深理解
"""

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
    print(attention_weights[0, 0][:5])  # 只展示前5个词的注意力`,
          expected_output: '输入形状: torch.Size([32, 10, 512])\n输出形状: torch.Size([32, 10, 512])\n注意力权重形状: torch.Size([32, 8, 10, 10])\n\n第一个序列第一个头的注意力权重：\ntensor([0.0988, 0.1102, 0.1245, 0.0989, 0.1024], grad=True)',
          exercises: [
            '修改多头数量，观察对模型性能的影响',
            '实现相对位置编码并添加到注意力计算中',
            '比较不同注意力变体（如Additive Attention）的效果',
            '可视化不同层的注意力权重分布',
          ],
        },
        status: 'completed'
      },
      {
        id: 'mock-rev-' + Date.now(),
        task_id: taskId,
        agent_type: 'reviewer',
        resource_type: 'review_report',
        content: {
          hallucination_risk: 'low',
          quality_score: 95,
          suggestions: [
            '可以增加注意力可视化的实际案例，如展示BERT中不同层的注意力模式差异',
            '建议添加更多数学推导的细节，特别是缩放因子的理论依据',
            '可以扩展实验部分，增加与LSTM等传统模型的性能对比',
          ],
          difficulty_assessment: '内容适合有一定深度学习基础的学习者，需要线性代数和PyTorch基础',
        },
        status: 'completed'
      },
    ]
  }
  // 通用回退模板（其他主题）
  const fallbackContent: Record<string, any> = {
    professor: {
      title: `深入理解：${topic}`,
      sections: [
        { heading: '基础概念与原理', subsections: [
          { subheading: '核心定义', body: `${topic}是机器学习/AI领域的核心概念之一。在深入探讨之前，我们先建立对基础原理的清晰理解。` },
          { subheading: '理论基础', body: `${topic}的数学基础建立在优化理论和线性代数之上。理解其中的数学推导对于掌握该概念至关重要。` },
        ]},
        { heading: '实践应用与案例分析', subsections: [
          { subheading: '应用场景', body: `在实际应用中，${topic}已经被广泛部署于各类场景。我们将通过具体案例来分析其工作原理。` },
          { subheading: '常见误区', body: '学习过程中最常遇到的困惑包括概念混淆、参数调优不当等问题。本节将逐一澄清。' },
        ]},
      ],
    },
    architect: {
      mindmap: {
        root: topic,
        children: [
          { name: '基础理论', children: [{ name: '数学原理' }, { name: '核心定义' }] },
          { name: '算法实现', children: [{ name: 'Python示例' }, { name: '优化技巧' }] },
          { name: '应用场景', children: [{ name: '工业案例' }, { name: '学术研究' }] },
        ],
      }
    },
    examiner: {
      questions: [
        { question: `关于${topic}，以下哪个描述最准确？`, options: ['选项A：描述1', '选项B：描述2', '选项C：描述3', '选项D：描述4'], answer: 1, explanation: '该选项准确概括了核心定义。' },
        { question: `在${topic}的实践中，以下哪个步骤应该首先完成？`, options: ['参数调优', '数据预处理', '模型部署', '结果可视化'], answer: 1, explanation: '数据预处理是所有后续步骤的基础。' },
        { question: `${topic}与相关概念的主要区别在于？`, options: ['计算速度', '理论基础', '应用领域', '以上都是'], answer: 1, explanation: '理论基础的差异是最本质的区别。' },
      ],
    },
    director: {
      scenes: [
        { scene_number: 1, title: `${topic}基础介绍`, visual: '动画展示一个实际问题场景', voiceover: `今天我们来探索${topic}。从一个直观的问题开始...`, duration_seconds: 30, resources: [
          { type: 'video', title: `${topic}基础介绍`, description: `了解${topic}的基本概念、核心原理和应用场景`, thumbnail: 'https://img.zcool.cn/community/03158e5d1b26e1a801215a95a458e7.jpg', url: `https://example.com/video/${topic}-intro`, duration: '10:00', platform: '示例平台' },
        ]},
        { scene_number: 2, title: `${topic}核心原理`, visual: '逐步拆解核心算法流程', voiceover: `让我们深入到${topic}的核心...`, duration_seconds: 45, resources: [
          { type: 'video', title: `${topic}核心原理详解`, description: `深入理解${topic}的工作原理、数学基础和实现细节`, thumbnail: 'https://img.zcool.cn/community/03158e5d1b26e1a801215a95a458e7.jpg', url: `https://example.com/video/${topic}-core`, duration: '15:00', platform: '示例平台' },
        ]},
        { scene_number: 3, title: `${topic}实战应用`, visual: '实际案例演示和代码实现', voiceover: `通过实际案例掌握${topic}的应用...`, duration_seconds: 60, resources: [
          { type: 'video', title: `${topic}实战应用`, description: `通过实际案例学习${topic}的具体实现、最佳实践和行业应用`, thumbnail: 'https://img.zcool.cn/community/03158e5d1b26e1a801215a95a458e7.jpg', url: `https://example.com/video/${topic}-demo`, duration: '20:00', platform: '示例平台' },
        ]},
      ],
    },
    hacker: {
      title: `${topic} - Python代码实验`,
      description: `通过动手实践来理解${topic}的核心原理`,
      code: `"""
${topic} - 动手实验
通过代码来直观理解核心概念
"""
import numpy as np
import matplotlib.pyplot as plt

def demonstrate_concept():
    """演示${topic}的核心概念"""
    # ===== 步骤1: 准备数据 =====
    print("步骤1: 准备实验数据")
    x = np.linspace(-5, 5, 100)
    y = x ** 2  # 示例：二次函数

    # ===== 步骤2: 核心计算 =====
    print("步骤2: 执行核心计算")
    derivative = 2 * x  # 导数
    gradient = derivative[50]  # 某点的梯度

    print(f"在 x=0 处的梯度: {gradient}")

    # ===== 步骤3: 可视化 =====
    print("步骤3: 生成可视化图表")
    # plt.plot(x, y, label='f(x)')
    # plt.legend()
    # plt.show()

    return {"min_value": np.min(y), "gradient_at_zero": float(gradient)}

if __name__ == "__main__":
    result = demonstrate_concept()
    print(f"实验结果: {result}")
`,
      expected_output: "步骤1: 准备实验数据\n步骤2: 执行核心计算\n在 x=0 处的梯度: 0.0\n步骤3: 生成可视化图表\n实验结果: {'min_value': 0.0, 'gradient_at_zero': 0.0}",
      exercises: [
        '修改函数定义，尝试其他函数如 y = x^3 观察梯度变化',
        '添加噪声数据，观察对梯度计算的影响',
      ],
    },
    reviewer: {
      hallucination_risk: 'low',
      quality_score: 85,
      suggestions: ['建议在教授文档中增加更多实际案例', '思维导图可以进一步细化第三级节点'],
      difficulty_assessment: '内容难度适中，适合有一定基础的学习者',
    },
  }

  const agentTypes = [
    { agent_type: 'professor', resource_type: 'document' as const },
    { agent_type: 'architect', resource_type: 'mindmap' as const },
    { agent_type: 'examiner', resource_type: 'quiz' as const },
    { agent_type: 'director', resource_type: 'video_script' as const },
    { agent_type: 'hacker', resource_type: 'code_lab' as const },
    { agent_type: 'reviewer', resource_type: 'review_report' as const },
  ]

  return agentTypes.map((at) => ({
    id: 'mock-' + at.agent_type + '-' + Date.now(),
    task_id: taskId,
    agent_type: at.agent_type,
    resource_type: at.resource_type,
    content: fallbackContent[at.agent_type] || {},
    status: 'completed',
  }))
}
*/
// ═══════════════════════════════════════════════════════════
//  [已注释] v1.0 getMockResources END
// ═══════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════
//  [已注释] v1.0 runWorkflow 模拟 — 保留兼容
// ═══════════════════════════════════════════════════════════
// const runWorkflow = async (topic: string) => {
//   ... (前端 setTimeout 模拟 15 秒管道，不再使用)
// }

// ═══════════════════════════════════════════════════════════
//  v2.0 runV2Pipeline — 调用后端真实 Agent 管道
// ═══════════════════════════════════════════════════════════
const runV2Pipeline = async (topic: string) => {
  selectedAgent.value = null
  console.log('[V2] Starting pipeline for topic:', topic)

  // 调用 store 的 v2 方法（连接 WebSocket + 后端 API）
  await factoryStore.startV2Generation(topic)
}

// 调试：监听store状态
watch(() => factoryStore.resources, (newResources) => {
  console.log('ContentFactory: Store resources updated', {
    count: newResources?.length,
    types: newResources?.map(r => r.agent_type),
    isGenerating: factoryStore.isGenerating
  })
}, { deep: true })

// 点击智能体卡片进入详情
const handleAgentClick = (agent: any) => {
  if (agent.status === 'success') {
    selectedAgent.value = agent
  }
}
</script>

<template>
  <div class="flex flex-col h-full bg-[#0b0b0b] text-slate-200 overflow-hidden relative">
    <!-- 顶部输入 -->
    <header class="border-b border-white/5 py-10 px-6 bg-gradient-to-b from-blue-900/5 to-transparent">
      <TopicInput :isGenerating="isGenerating" @start="runV2Pipeline" />
    </header>

    <main class="flex-1 flex overflow-hidden p-6 gap-6">
      <!-- 左侧：工作台控制面板 -->
      <aside class="w-80 flex flex-col gap-6">
        <div class="bg-[#141414] border border-white/5 rounded-3xl p-5 flex-1 flex flex-col shadow-2xl relative overflow-hidden">
          <h3 class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-5 flex items-center gap-2 px-1">
            <span class="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse"></span>
            专家集群状态
          </h3>
          
          <!-- 智能体列表 -->
          <div class="space-y-3 overflow-y-auto pr-1 custom-scrollbar">
            <AgentStatusCard 
              v-for="agent in agents" 
              :key="agent.id" 
              :agent="agent" 
              @click="handleAgentClick(agent)"
              :class="[
                agent.status === 'success' ? 'cursor-pointer hover:translate-x-1 active:scale-95 transition-all' : ''
              ]"
            />
          </div>

          <!-- 底部提示 -->
          <div v-if="!isGenerating && currentTopic" class="mt-4 p-3 bg-blue-500/5 rounded-xl border border-blue-500/10">
            <p class="text-[10px] text-blue-400/80 leading-relaxed">
              💡 点击带有 <span class="font-bold">READY/DONE</span> 标记的专家，可进入深度研讨室进行 1-on-1 对话。
            </p>
          </div>
        </div>

        <!-- 终端日志 -->
        <div class="h-60">
           <AgentTerminal :logs="logs" />
        </div>
      </aside>

      <!-- 右侧：主展示区 -->
      <section class="flex-1 min-w-0">
        <ResourceDisplay
          :resources="factoryStore.resources"
          :isGenerating="factoryStore.isGenerating"
          :topic="factoryStore.currentTopic"
          :defaultTab="defaultTab"
        />
      </section>
    </main>

    <!-- 深度对话研讨室 (Overlay) -->
    <Transition
      enter-active-class="transition duration-500 ease-out"
      enter-from-class="opacity-0 translate-y-10 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition duration-300 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-10 scale-95"
    >
      <AgentDetailView
        v-if="selectedAgent"
        :agent="selectedAgent"
        :topic="currentTopic"
        :taskId="factoryStore.currentTaskId"
        :resources="factoryStore.resources"
        @close="selectedAgent = null"
      />
    </Transition>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #222; border-radius: 10px; }
</style>