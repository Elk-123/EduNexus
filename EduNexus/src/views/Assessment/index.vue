<script setup lang="ts">
import { ref } from 'vue'
import { BookOpen, Code, FileText, Video, CheckCircle2, TrendingUp, Clock, Target, Brain, Zap, Layers, ChevronRight, GitBranch } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'

// ── Mock：学习历史记录 ──
interface HistoryItem {
  id: number
  title: string
  type: 'document' | 'video' | 'code' | 'quiz' | 'mindmap'
  completedAt: string
  score: number | null
  duration: string
  topic: string
}

const history = ref<HistoryItem[]>([
  { id: 1, title: 'Transformer 自注意力机制深度解析', type: 'document', completedAt: '2026-06-18 14:30', score: 95, duration: '25 min', topic: '深度学习' },
  { id: 2, title: '反向传播算法数学推导', type: 'video', completedAt: '2026-06-18 10:15', score: 92, duration: '18 min', topic: '深度学习' },
  { id: 3, title: 'CNN 卷积核可视化实验', type: 'code', completedAt: '2026-06-17 16:45', score: 88, duration: '35 min', topic: '计算机视觉' },
  { id: 4, title: '数据库范式与规范化设计', type: 'quiz', completedAt: '2026-06-17 09:20', score: 85, duration: '15 min', topic: '数据库' },
  { id: 5, title: 'RNN / LSTM / GRU 序列模型对比', type: 'document', completedAt: '2026-06-16 19:00', score: 90, duration: '30 min', topic: '深度学习' },
  { id: 6, title: '知识图谱构建方法论', type: 'mindmap', completedAt: '2026-06-16 11:30', score: null, duration: '12 min', topic: '知识工程' },
  { id: 7, title: 'NumPy 手写 MLP 多层感知机', type: 'code', completedAt: '2026-06-15 20:15', score: 87, duration: '45 min', topic: '深度学习' },
  { id: 8, title: '梯度下降优化器对比实验', type: 'code', completedAt: '2026-06-15 14:00', score: 93, duration: '40 min', topic: '机器学习' },
  { id: 9, title: '线性代数矩阵运算复习', type: 'quiz', completedAt: '2026-06-14 16:30', score: 78, duration: '20 min', topic: '数学基础' },
  { id: 10, title: '概率论与信息熵基础', type: 'document', completedAt: '2026-06-14 09:00', score: 82, duration: '22 min', topic: '数学基础' },
])

const typeIcon = (type: string) => {
  switch (type) {
    case 'document': return FileText
    case 'video': return Video
    case 'code': return Code
    case 'quiz': return CheckCircle2
    case 'mindmap': return Layers
    default: return BookOpen
  }
}

const typeColor = (type: string) => {
  switch (type) {
    case 'document': return 'bg-blue-500/10 text-blue-400'
    case 'video': return 'bg-rose-500/10 text-rose-400'
    case 'code': return 'bg-emerald-500/10 text-emerald-400'
    case 'quiz': return 'bg-amber-500/10 text-amber-400'
    case 'mindmap': return 'bg-purple-500/10 text-purple-400'
    default: return 'bg-zinc-500/10 text-zinc-400'
  }
}

const typeLabel = (type: string) => {
  switch (type) {
    case 'document': return '文档'
    case 'video': return '视频'
    case 'code': return '代码'
    case 'quiz': return '测验'
    case 'mindmap': return '导图'
    default: return '其他'
  }
}

// ── Mock：学习总结 ──
const summary = {
  weeklyStats: {
    totalHours: 12.5,
    completedItems: 10,
    avgScore: 88,
    topicsCovered: 6,
  },
  techPreferences: [
    { name: '深度学习 / NLP', level: 92, description: 'Transformer、注意力机制、RNN/LSTM 序列建模为主要研究方向' },
    { name: '计算机视觉', level: 75, description: 'CNN 架构理解扎实，目标检测与图像分割有待深入' },
    { name: '机器学习基础', level: 80, description: '优化器、损失函数、正则化等核心概念掌握良好' },
    { name: '知识工程 / 图论', level: 65, description: '知识图谱构建有初步实践，图神经网络 (GNN) 尚未涉猎' },
    { name: '数学基础', level: 72, description: '线性代数和概率论为薄弱环节，建议针对性强化' },
    { name: '数据库系统', level: 58, description: '范式理论与 SQL 优化接触较少，范式分解刚完成入门' },
  ],
  researchDepth: {
    score: 73,
    label: '中级研究者',
    dimensions: [
      { label: '理论深度', value: 70, detail: '能理解论文核心方法，独立推导关键公式' },
      { label: '工程实践', value: 85, detail: '熟练使用 PyTorch/TensorFlow，可复现论文代码' },
      { label: '知识广度', value: 65, detail: '覆盖 CV/NLP/基础 ML，知识工程领域较弱' },
      { label: '创新思维', value: 60, detail: '善于综合现有方法，独立提出改进方案的能力待提升' },
    ],
  },
}

// ── 跨模块上下文 ──
const crossModuleContext = {
  pathPlanning: {
    summary: '学生已具备深度学习核心知识（Transformer/RNN/CNN），数学基础（线性代数 72/概率论 78）为相对薄弱环节。建议路径规划时在核心模型阶段插入 2 个数学补丁节点，前沿进阶阶段优先安排 LLM 与 Agent 相关节点。',
    injectedNodes: ['线性代数强化：特征值与SVD', '概率图模型入门'],
    priority: 'LLM 架构 → RAG 系统 → Agent 编排',
  },
  resourceDelivery: {
    summary: '学生偏好代码实践类资源（代码类均分 89）和结构化文档（文档类均分 89），视频类接受度中等（85）。建议推送以 Colab 代码实验 + 技术深度文章为主，辅以少量论文精读视频。知识工程与数据库领域应增加基础入门内容。',
    recommendedTypes: ['code（优先）', 'document', 'video（辅助）'],
    avoidTopics: ['过于基础的 Python 语法', '已掌握的 CNN 基础'],
  },
}
</script>

<template>
  <div class="min-h-screen bg-[#0b0b0b]">
    <!-- 背景 -->
    <div class="absolute inset-0 z-0 bg-[linear-gradient(to_right,#ffffff06_1px,transparent_1px),linear-gradient(to_bottom,#ffffff06_1px,transparent_1px)] bg-[size:48px_48px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,#000_60%,transparent_100%)]"></div>

    <div class="relative z-10 max-w-6xl mx-auto px-6 py-8 pb-20">
      <!-- 头部 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-white mb-2">学习效果评估</h1>
        <p class="text-zinc-500 text-sm">学习历程回顾与能力画像分析</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- ═══════════ 左侧：学习历程 (8 cols) ═══════════ -->
        <div class="lg:col-span-8 space-y-5">
          <!-- 本周统计条 -->
          <div class="grid grid-cols-4 gap-3">
            <div class="bg-[#131314] border border-[#252525] rounded-2xl p-4 text-center">
              <p class="text-2xl font-bold text-white">{{ summary.weeklyStats.totalHours }}h</p>
              <p class="text-[11px] text-zinc-500 mt-0.5">本周学习</p>
            </div>
            <div class="bg-[#131314] border border-[#252525] rounded-2xl p-4 text-center">
              <p class="text-2xl font-bold text-white">{{ summary.weeklyStats.completedItems }}</p>
              <p class="text-[11px] text-zinc-500 mt-0.5">完成项目</p>
            </div>
            <div class="bg-[#131314] border border-[#252525] rounded-2xl p-4 text-center">
              <p class="text-2xl font-bold text-emerald-400">{{ summary.weeklyStats.avgScore }}</p>
              <p class="text-[11px] text-zinc-500 mt-0.5">均分</p>
            </div>
            <div class="bg-[#131314] border border-[#252525] rounded-2xl p-4 text-center">
              <p class="text-2xl font-bold text-blue-400">{{ summary.weeklyStats.topicsCovered }}</p>
              <p class="text-[11px] text-zinc-500 mt-0.5">覆盖领域</p>
            </div>
          </div>

          <!-- 历史记录 -->
          <div class="bg-[#131314] border border-[#252525] rounded-[2rem] p-6">
            <h3 class="text-sm font-bold text-white mb-5 flex items-center gap-2">
              <Clock class="w-4 h-4 text-zinc-500" />
              学习历程
              <span class="text-[11px] text-zinc-600 font-normal">最近 10 条</span>
            </h3>

            <div class="space-y-1">
              <div
                v-for="item in history"
                :key="item.id"
                class="flex items-center gap-4 px-4 py-3 rounded-xl hover:bg-white/[0.02] transition-colors group"
              >
                <!-- 类型图标 -->
                <div :class="['w-9 h-9 rounded-lg flex items-center justify-center shrink-0', typeColor(item.type)]">
                  <component :is="typeIcon(item.type)" class="w-4 h-4" />
                </div>

                <!-- 标题 + 时间 -->
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-zinc-200 font-medium truncate">{{ item.title }}</p>
                  <div class="flex items-center gap-3 mt-0.5">
                    <span class="text-[11px] text-zinc-500">{{ item.completedAt }}</span>
                    <Badge variant="outline" class="text-[9px] py-0 h-4 bg-transparent border-zinc-700 text-zinc-500">
                      {{ item.topic }}
                    </Badge>
                  </div>
                </div>

                <!-- 类型标签 -->
                <span :class="['text-[10px] px-2 py-0.5 rounded-md font-medium shrink-0', typeColor(item.type)]">
                  {{ typeLabel(item.type) }}
                </span>

                <!-- 分数 -->
                <div class="w-12 text-right shrink-0">
                  <span v-if="item.score" :class="['text-sm font-mono font-bold', item.score >= 90 ? 'text-emerald-400' : item.score >= 80 ? 'text-blue-400' : 'text-amber-400']">
                    {{ item.score }}
                  </span>
                  <span v-else class="text-xs text-zinc-600">—</span>
                </div>

                <ChevronRight class="w-4 h-4 text-zinc-700 group-hover:text-zinc-500 shrink-0" />
              </div>
            </div>
          </div>
        </div>

        <!-- ═══════════ 右侧：学习总结 (4 cols) ═══════════ -->
        <div class="lg:col-span-4 space-y-5">
          <!-- 技术偏好 -->
          <div class="bg-[#131314] border border-[#252525] rounded-[2rem] p-6">
            <h3 class="text-sm font-bold text-white mb-5 flex items-center gap-2">
              <Target class="w-4 h-4 text-blue-400" />
              技术偏好
            </h3>
            <div class="space-y-4">
              <div v-for="tech in summary.techPreferences" :key="tech.name" class="group">
                <div class="flex items-center justify-between mb-1.5">
                  <span class="text-xs text-zinc-300 truncate flex-1 mr-2">{{ tech.name }}</span>
                  <span
                    :class="[
                      'text-[11px] font-mono font-bold',
                      tech.level >= 85 ? 'text-emerald-400' :
                      tech.level >= 70 ? 'text-blue-400' :
                      'text-amber-400'
                    ]"
                  >{{ tech.level }}</span>
                </div>
                <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div
                    :class="[
                      'h-full rounded-full transition-all',
                      tech.level >= 85 ? 'bg-emerald-500' :
                      tech.level >= 70 ? 'bg-blue-500' :
                      'bg-amber-500'
                    ]"
                    :style="{ width: tech.level + '%' }"
                  ></div>
                </div>
                <p class="text-[10px] text-zinc-500 mt-1 leading-relaxed">{{ tech.description }}</p>
              </div>
            </div>
          </div>

          <!-- 研究深度 -->
          <div class="bg-[#131314] border border-[#252525] rounded-[2rem] p-6">
            <h3 class="text-sm font-bold text-white mb-5 flex items-center gap-2">
              <Layers class="w-4 h-4 text-purple-400" />
              研究深度
            </h3>

            <div class="flex items-center gap-4 mb-5">
              <div class="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                <span class="text-2xl font-bold text-purple-400">{{ summary.researchDepth.score }}</span>
              </div>
              <div>
                <p class="text-sm font-bold text-white">{{ summary.researchDepth.label }}</p>
                <p class="text-[11px] text-zinc-500">综合评估得分</p>
              </div>
            </div>

            <div class="space-y-3">
              <div v-for="dim in summary.researchDepth.dimensions" :key="dim.label">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-xs text-zinc-400">{{ dim.label }}</span>
                  <span class="text-[11px] font-mono text-zinc-500">{{ dim.value }}</span>
                </div>
                <div class="h-1 bg-zinc-800 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-purple-500/60 rounded-full"
                    :style="{ width: dim.value + '%' }"
                  ></div>
                </div>
                <p class="text-[10px] text-zinc-500 mt-0.5 leading-relaxed">{{ dim.detail }}</p>
              </div>
            </div>
          </div>

          <!-- AI 洞察 -->
          <div class="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/15 rounded-[2rem] p-5">
            <div class="flex items-start gap-2.5">
              <Zap class="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <p class="text-[10px] text-amber-400/80 uppercase tracking-wider mb-1">AI 学习建议</p>
                <p class="text-xs text-zinc-300 leading-relaxed">
                  你在深度学习方向已形成明显优势。建议下一步补齐数学基础（概率论、线性代数），并尝试阅读顶会论文复现代码，向高级研究者进阶。
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════════ 跨模块上下文 ═══════════ -->
      <div class="mt-8 space-y-4">
        <h3 class="text-sm font-bold text-white flex items-center gap-2">
          <Brain class="w-4 h-4 text-purple-400" />
          评估上下文 — 联动下游模块
          <span class="text-[11px] text-zinc-600 font-normal">以下总结将作为输入传递给路径规划与资源推送模块</span>
        </h3>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <!-- 路径规划上下文 -->
          <div class="bg-[#131314] border border-blue-500/15 rounded-2xl p-5">
            <div class="flex items-center gap-2 mb-3">
              <GitBranch class="w-4 h-4 text-blue-400" />
              <span class="text-xs font-bold text-blue-400 uppercase tracking-wide">→ 学习路径规划上下文</span>
            </div>
            <p class="text-sm text-zinc-300 leading-relaxed mb-4">{{ crossModuleContext.pathPlanning.summary }}</p>
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-blue-500/5 border border-blue-500/10 rounded-xl p-3">
                <p class="text-[10px] text-blue-400/70 uppercase tracking-wider mb-1.5">建议注入补丁节点</p>
                <p class="text-xs text-zinc-400" v-for="node in crossModuleContext.pathPlanning.injectedNodes" :key="node">• {{ node }}</p>
              </div>
              <div class="bg-emerald-500/5 border border-emerald-500/10 rounded-xl p-3">
                <p class="text-[10px] text-emerald-400/70 uppercase tracking-wider mb-1.5">前沿优先路径</p>
                <p class="text-xs text-zinc-400">{{ crossModuleContext.pathPlanning.priority }}</p>
              </div>
            </div>
          </div>

          <!-- 资源推送上下文 -->
          <div class="bg-[#131314] border border-emerald-500/15 rounded-2xl p-5">
            <div class="flex items-center gap-2 mb-3">
              <TrendingUp class="w-4 h-4 text-emerald-400" />
              <span class="text-xs font-bold text-emerald-400 uppercase tracking-wide">→ 资源推送上下文</span>
            </div>
            <p class="text-sm text-zinc-300 leading-relaxed mb-4">{{ crossModuleContext.resourceDelivery.summary }}</p>
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-emerald-500/5 border border-emerald-500/10 rounded-xl p-3">
                <p class="text-[10px] text-emerald-400/70 uppercase tracking-wider mb-1.5">推荐资源类型</p>
                <p class="text-xs text-zinc-400" v-for="type in crossModuleContext.resourceDelivery.recommendedTypes" :key="type">• {{ type }}</p>
              </div>
              <div class="bg-amber-500/5 border border-amber-500/10 rounded-xl p-3">
                <p class="text-[10px] text-amber-400/70 uppercase tracking-wider mb-1.5">可跳过内容</p>
                <p class="text-xs text-zinc-400" v-for="t in crossModuleContext.resourceDelivery.avoidTopics" :key="t">• {{ t }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
