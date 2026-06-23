import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getTodayResources, getTrending, updateProgress as updateProgressApi } from '@/api/resources'
import type { TodayResource, TrendingItem, ResourceProgress } from '@/types/resources'

export const useDeliveryStore = defineStore('delivery', () => {
  const todayResources = ref<TodayResource[]>([])
  const trendingItems = ref<TrendingItem[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ── Demo Fallback：AI 学科资源 ──
  const fallbackTodayResources: TodayResource[] = [
    {
      id: 'fb-1',
      resource_type: 'document',
      title: 'Transformer 自注意力机制深度解析',
      description: '从 Scaled Dot-Product Attention 到 Multi-Head Attention，理解 Q/K/V 的直观含义与数学推导',
      status: 'completed',
      ai_reason: '你已完成基础储备阶段，这篇文档帮你打通注意力机制的核心概念',
      duration: '25 min',
    },
    {
      id: 'fb-2',
      resource_type: 'video',
      title: '反向传播算法可视化讲解',
      description: '3Blue1Brown 风格的可视化视频，直观理解计算图、链式法则与梯度反向流动',
      status: 'completed',
      duration: '18 min',
    },
    {
      id: 'fb-3',
      resource_type: 'document',
      title: '卷积神经网络 (CNN) 入门与实践',
      description: '从卷积核、池化层到经典架构 LeNet/AlexNet/ResNet，附 PyTorch 实现',
      status: 'current',
      ai_reason: '核心模型阶段首选知识点，CNN 是理解后续 Transformer 的重要前置概念',
      duration: '35 min',
    },
    {
      id: 'fb-4',
      resource_type: 'code',
      title: 'NumPy 手写 MLP 多层感知机',
      description: '不依赖框架，用 NumPy 从零实现前向传播、反向传播与 SGD 优化器',
      status: 'locked',
      duration: '45 min',
    },
    {
      id: 'fb-5',
      resource_type: 'quiz',
      title: '深度学习基础概念自测',
      description: '15 道选择题 + 3 道简答题，覆盖激活函数、损失函数、正则化与优化器',
      status: 'locked',
      duration: '20 min',
    },
    {
      id: 'fb-6',
      resource_type: 'document',
      title: 'RNN / LSTM / GRU 序列模型对比',
      description: '从循环结构到门控机制，理解三种序列建模架构的设计哲学与适用场景',
      status: 'locked',
      duration: '30 min',
      ai_reason: '配合教授智能体 RNN 答疑内容，巩固序列建模知识体系',
    },
    {
      id: 'fb-7',
      resource_type: 'video',
      title: '生成对抗网络 (GAN) 原理与实战',
      description: '从博弈论视角理解生成器与判别器的对抗训练，实现 DCGAN 生成 MNIST 手写数字',
      status: 'locked',
      duration: '40 min',
    },
  ]

  // ── Demo Fallback：科技行业 6 条趋势 ──
  const fallbackTrendingItems: TrendingItem[] = [
    {
      source: 'GitHub',
      title: 'Meta 开源 Llama 4 多模态模型，支持图像/视频/语音理解',
      meta: '24.5k stars',
      tag: 'LLM',
      url: 'https://github.com/meta-llama/llama',
    },
    {
      source: 'Arxiv',
      title: 'Mamba-2: 状态空间模型在长序列建模上超越 Transformer',
      meta: '引用 380+',
      tag: 'SSM',
      url: 'https://arxiv.org/abs/2405.12345',
    },
    {
      source: 'GitHub',
      title: 'Claude Code 开源实现 OpenCode 一周斩获 15k Star',
      meta: '15.2k stars',
      tag: 'Agent',
      url: 'https://github.com/opencode-ai/opencode',
    },
    {
      source: 'HackerNews',
      title: 'WebAssembly 在浏览器端运行 LLM 推理达到实用水平',
      meta: '2.1k points',
      tag: 'WASM',
      url: 'https://news.ycombinator.com/item?id=41000000',
    },
    {
      source: 'Arxiv',
      title: 'MoE (Mixture of Experts) 架构在移动端部署取得突破',
      meta: '引用 210+',
      tag: 'MoE',
      url: 'https://arxiv.org/abs/2406.07890',
    },
    {
      source: 'GitHub',
      title: 'Rust 重写的 ESLint 替代品 Biome 发布 v2.0 正式版',
      meta: '18.7k stars',
      tag: 'Tooling',
      url: 'https://github.com/biomejs/biome',
    },
  ]

  const currentResource = computed(() =>
    todayResources.value.find((r) => r.status === 'current') || todayResources.value[0]
  )

  async function fetchToday() {
    try {
      const data = await getTodayResources()
      todayResources.value = data.length > 0 ? data : fallbackTodayResources
    } catch {
      todayResources.value = fallbackTodayResources
    }
  }

  async function fetchTrending() {
    try {
      const data = await getTrending()
      // 后端固定返回 3 条，演示用 fallback 6 条替换
      trendingItems.value = data.length >= 6 ? data : fallbackTrendingItems
    } catch {
      trendingItems.value = fallbackTrendingItems
    }
  }

  async function fetchAll() {
    isLoading.value = true
    error.value = null
    try {
      await Promise.all([fetchToday(), fetchTrending()])
    } finally {
      isLoading.value = false
    }
  }

  async function updateResourceProgress(resourceId: string, progress: ResourceProgress) {
    await updateProgressApi(resourceId, progress)
    const idx = todayResources.value.findIndex((r) => r.id === resourceId)
    if (idx !== -1) {
      todayResources.value[idx].status = progress.status as TodayResource['status']
    }
  }

  return { todayResources, trendingItems, isLoading, error,
           currentResource, fetchToday, fetchTrending, fetchAll, updateResourceProgress }
})
