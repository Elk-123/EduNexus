<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  BrainCircuit, Sparkles,
  ChevronRight, FileText,
  CheckCircle2, AlertCircle,
  Video, Code, GitFork,
  Calendar, ShieldCheck, ClipboardCheck,
  Zap, Clock, ArrowRight
} from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/authStore'
import { useDeliveryStore } from '@/stores/deliveryStore'

const router = useRouter()
const authStore = useAuthStore()
const deliveryStore = useDeliveryStore()

const userName = computed(() => authStore.user?.username || '同学')

const fallbackResources = [
  { title: 'Transformer 注意力机制', resource_type: 'document', description: '深入理解注意力机制的核心概念' },
  { title: '知识图谱导论', resource_type: 'mindmap', description: '可视化知识结构导图' },
  { title: '机器学习基础测试', resource_type: 'quiz', description: '3道选择题检验学习成果' },
  { title: 'Python 神经网络实战', resource_type: 'code', description: '动手实现简单的神经网络' },
]

// ── 内容制造车间：智能体流水线 + 演示内容 ──
const pipelineAgents = [
  { id: 'manager', shortName: '主控', name: '主控中枢', icon: BrainCircuit, color: 'text-purple-400', bgClass: 'bg-purple-500/10 border border-purple-500/20' },
  { id: 'professor', shortName: '教授', name: '教授智能体', icon: FileText, color: 'text-blue-400', bgClass: 'bg-blue-500/10 border border-blue-500/20' },
  { id: 'architect', shortName: '架构', name: '架构师智能体', icon: GitFork, color: 'text-orange-400', bgClass: 'bg-orange-500/10 border border-orange-500/20' },
  { id: 'examiner', shortName: '考官', name: '考官智能体', icon: ClipboardCheck, color: 'text-pink-400', bgClass: 'bg-pink-500/10 border border-pink-500/20' },
  { id: 'director', shortName: '导演', name: '导演智能体', icon: Video, color: 'text-cyan-400', bgClass: 'bg-cyan-500/10 border border-cyan-500/20' },
  { id: 'hacker', shortName: '极客', name: '极客智能体', icon: Code, color: 'text-emerald-400', bgClass: 'bg-emerald-500/10 border border-emerald-500/20' },
  { id: 'reviewer', shortName: '审查', name: '质量审查', icon: ShieldCheck, color: 'text-rose-400', bgClass: 'bg-rose-500/10 border border-rose-500/20' },
]

const demoContents = [
  {
    id: 1,
    title: 'Transformer 架构深度解析',
    desc: '自注意力机制 · 多头注意力 · 位置编码',
    agentName: 'Professor Agent',
    icon: FileText,
    iconColor: 'text-blue-400',
    tag: '文档',
    tagClass: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  },
  {
    id: 2,
    title: '注意力机制知识结构',
    desc: 'Scaled Dot-Product → Multi-Head → Cross-Attention',
    agentName: 'Architect Agent',
    icon: GitFork,
    iconColor: 'text-orange-400',
    tag: '导图',
    tagClass: 'bg-orange-500/10 text-orange-400 border border-orange-500/20',
  },
  {
    id: 3,
    title: '机器学习基础能力评估',
    desc: '3 道选择题 + 1 道简答题 · 难度中等',
    agentName: 'Examiner Agent',
    icon: ClipboardCheck,
    iconColor: 'text-pink-400',
    tag: '测验',
    tagClass: 'bg-pink-500/10 text-pink-400 border border-pink-500/20',
  },
]

onMounted(() => {
  deliveryStore.fetchAll()
})
</script>

<template>
  <div class="space-y-8 pb-10">
    <!-- 1. 顶部：欢迎标题 -->
    <section>
      <h1 class="text-4xl font-bold text-white tracking-tight">
        你好, {{ userName }} <span class="text-zinc-500 text-2xl font-normal">/ 准备好开始今天的学习了吗？</span>
      </h1>
    </section>

    <!-- 2. 中间主要内容：Bento 布局 -->
    <div class="grid grid-cols-12 gap-6">
      
      <!-- 左侧：知识图谱动态路由 (三阶段展示) -->
      <div class="col-span-12 lg:col-span-8 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8 flex flex-col">
        <!-- 标题行 -->
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <BrainCircuit class="w-5 h-5 text-blue-500" />
              动态规划路径：人工智能导论
            </h3>
            <p class="text-zinc-500 text-sm mt-0.5">基础储备 → 核心模型 → 前沿进阶</p>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-xs font-mono text-zinc-400 bg-zinc-800/60 px-2.5 py-1 rounded-lg border border-zinc-700/50">总进度 28%</span>
            <Button variant="outline" class="rounded-xl border-[#303134] bg-transparent text-xs" @click="router.push('/path')">查看全量图谱</Button>
          </div>
        </div>

        <!-- 进度条 -->
        <div class="h-1.5 bg-zinc-800 rounded-full mb-6 overflow-hidden">
          <div class="h-full bg-gradient-to-r from-emerald-500 via-blue-500 to-zinc-600 rounded-full shadow-[0_0_8px_rgba(37,99,235,0.3)]" style="width: 28%"></div>
        </div>

        <!-- 三阶段详情卡片 -->
        <div class="grid grid-cols-3 gap-4 mb-5">
          <!-- 阶段一：基础储备 (已完成) -->
          <div class="bg-emerald-500/5 border border-emerald-500/15 rounded-2xl p-4 relative overflow-hidden">
            <div class="absolute top-0 right-0 w-12 h-12 bg-emerald-500/5 rounded-bl-2xl -mr-3 -mt-3"></div>
            <div class="flex items-center gap-2 mb-3">
              <CheckCircle2 class="w-4 h-4 text-emerald-500" />
              <span class="text-sm font-bold text-emerald-400">基础储备</span>
              <span class="ml-auto text-[10px] font-mono text-emerald-500/70">100%</span>
            </div>
            <div class="space-y-1.5">
              <div class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-emerald-500/40 shrink-0"></span><span class="text-[11px] text-zinc-400">线性代数基础</span></div>
              <div class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-emerald-500/40 shrink-0"></span><span class="text-[11px] text-zinc-400">Python 编程入门</span></div>
              <div class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-emerald-500/40 shrink-0"></span><span class="text-[11px] text-zinc-400">概率与统计</span></div>
              <div class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-emerald-500/40 shrink-0"></span><span class="text-[11px] text-zinc-400">微积分复习</span></div>
            </div>
            <div class="mt-3 pt-3 border-t border-emerald-500/10 flex items-center justify-between">
              <span class="text-[10px] text-zinc-500">4 节点</span>
              <span class="text-[10px] text-zinc-500">约 2.5h</span>
            </div>
          </div>

          <!-- 阶段二：核心模型 (进行中) -->
          <div class="bg-blue-500/5 border border-blue-500/20 rounded-2xl p-4 relative overflow-hidden ring-1 ring-blue-500/10">
            <div class="absolute top-0 right-0 w-12 h-12 bg-blue-500/5 rounded-bl-2xl -mr-3 -mt-3"></div>
            <div class="flex items-center gap-2 mb-3">
              <span class="relative flex h-4 w-4">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-30"></span>
                <span class="relative inline-flex rounded-full h-4 w-4 bg-blue-500"></span>
              </span>
              <span class="text-sm font-bold text-blue-400">核心模型</span>
              <span class="ml-auto text-[10px] font-mono text-blue-400/70">35%</span>
            </div>
            <div class="space-y-1.5">
              <div class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-blue-500/60 shrink-0"></span><span class="text-[11px] text-zinc-300">机器学习概论</span></div>
              <div class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-blue-500/60 shrink-0"></span><span class="text-[11px] text-zinc-300">深度学习基础</span></div>
              <div class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span><span class="text-[11px] text-zinc-500">卷积神经网络</span></div>
              <div class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span><span class="text-[11px] text-zinc-500">RNN / LSTM</span></div>
            </div>
            <div class="mt-3 pt-3 border-t border-blue-500/10 flex items-center justify-between">
              <span class="text-[10px] text-zinc-500">6 节点</span>
              <span class="text-[10px] text-zinc-500">约 8h 预估</span>
            </div>
          </div>

          <!-- 阶段三：前沿进阶 (待解锁) -->
          <div class="bg-[#0b0b0b] border border-zinc-700/50 rounded-2xl p-4 relative overflow-hidden opacity-70">
            <div class="absolute top-0 right-0 w-12 h-12 bg-zinc-500/5 rounded-bl-2xl -mr-3 -mt-3"></div>
            <div class="flex items-center gap-2 mb-3">
              <div class="w-4 h-4 rounded-full border border-zinc-600 flex items-center justify-center">
                <div class="w-1.5 h-1.5 rounded-full bg-zinc-600"></div>
              </div>
              <span class="text-sm font-bold text-zinc-500">前沿进阶</span>
              <span class="ml-auto text-[10px] font-mono text-zinc-600">0%</span>
            </div>
            <div class="space-y-1.5">
              <div class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span><span class="text-[11px] text-zinc-500">Transformer 架构</span></div>
              <div class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span><span class="text-[11px] text-zinc-500">LLM 预训练</span></div>
              <div class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-zinc-600 shrink-0"></span><span class="text-[11px] text-zinc-500">RAG 与 Agent</span></div>
            </div>
            <div class="mt-3 pt-3 border-t border-zinc-700/30 flex items-center justify-between">
              <span class="text-[10px] text-zinc-600">3 节点</span>
              <span class="text-[10px] text-zinc-600">约 6h 预估</span>
            </div>
          </div>
        </div>

        <!-- 当前聚焦节点 + AI 洞察 -->
        <div class="grid grid-cols-5 gap-4 mt-auto">
          <!-- 当前聚焦 -->
          <div class="col-span-3 bg-[#0b0b0b] border border-[#202022] rounded-2xl p-4">
            <p class="text-[10px] text-blue-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
              当前聚焦
            </p>
            <div class="space-y-2">
              <div class="flex items-center gap-3 p-2.5 rounded-xl bg-[#131314] border border-[#202022] hover:border-blue-500/30 cursor-pointer transition-all group" @click="router.push('/path')">
                <div class="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0 group-hover:bg-blue-500/20 transition-colors">
                  <BrainCircuit class="w-4 h-4 text-blue-400" />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-zinc-200 truncate">卷积神经网络 (CNN)</p>
                  <p class="text-[9px] text-zinc-500">核心模型 · 待开始</p>
                </div>
                <ArrowRight class="w-3.5 h-3.5 text-zinc-600 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all shrink-0" />
              </div>
              <div class="flex items-center gap-3 p-2.5 rounded-xl bg-[#131314] border border-[#202022] hover:border-blue-500/30 cursor-pointer transition-all group" @click="router.push('/path')">
                <div class="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center shrink-0 group-hover:bg-amber-500/20 transition-colors">
                  <Zap class="w-4 h-4 text-amber-400" />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-zinc-200 truncate">反向传播算法</p>
                  <p class="text-[9px] text-zinc-500">核心模型 · 进行中 60%</p>
                </div>
                <ArrowRight class="w-3.5 h-3.5 text-zinc-600 group-hover:text-amber-400 group-hover:translate-x-0.5 transition-all shrink-0" />
              </div>
            </div>
          </div>

          <!-- AI 诊断洞察 -->
          <div class="col-span-2 bg-blue-500/5 border border-blue-500/10 rounded-2xl p-4 flex flex-col">
            <p class="text-[10px] text-blue-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <AlertCircle class="w-3 h-3" />
              AI 洞察
            </p>
            <p class="text-[11px] text-blue-200/70 leading-relaxed flex-1">
              基础阶段已全部完成，数学和编程基础扎实。核心模型阶段建议优先攻克 <span class="text-blue-300 font-medium">CNN</span>，预计 3-4 个学习单元可完成。
            </p>
            <div class="mt-3 pt-3 border-t border-blue-500/10">
              <span class="text-[10px] text-blue-400/60">📊 学习效率评分：<span class="text-blue-300 font-bold">87/100</span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：内容制造车间 (Multi-Agent Workspace) -->
      <div class="col-span-12 lg:col-span-4 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8 flex flex-col">
        <!-- 标题行 + 状态徽章 -->
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-xl font-bold text-white flex items-center gap-2">
            <Sparkles class="w-5 h-5 text-purple-500" />
            内容制造车间
          </h3>
          <span class="text-[10px] text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20 flex items-center gap-1.5 shrink-0">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_6px_rgba(52,211,153,0.6)]"></span>
            7 Agents Online
          </span>
        </div>

        <!-- 智能体流水线可视化 -->
        <div class="mb-5">
          <p class="text-[10px] text-zinc-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Zap class="w-3 h-3 text-amber-500" />
            Agent 流水线
          </p>
          <div class="flex items-center">
            <template v-for="(agent, i) in pipelineAgents" :key="agent.id">
              <div
                class="flex flex-col items-center gap-1.5 group cursor-default"
                :title="agent.name"
              >
                <div
                  :class="[
                    'w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-300',
                    'hover:scale-110 hover:shadow-lg',
                    agent.bgClass,
                  ]"
                >
                  <component :is="agent.icon" :class="['w-4 h-4', agent.color]" />
                </div>
              </div>
              <!-- 连接线 -->
              <div
                v-if="i < pipelineAgents.length - 1"
                class="flex-1 h-px mx-0.5 bg-gradient-to-r from-zinc-600 via-zinc-500 to-zinc-600"
              ></div>
            </template>
          </div>
          <!-- 标签行 -->
          <div class="flex items-center mt-1.5">
            <template v-for="(agent, i) in pipelineAgents" :key="'lbl-' + agent.id">
              <span class="text-[8px] text-zinc-500 text-center truncate" style="width: 2.25rem">{{ agent.shortName }}</span>
              <div v-if="i < pipelineAgents.length - 1" class="flex-1 mx-0.5"></div>
            </template>
          </div>
        </div>

        <!-- 分割线 -->
        <div class="border-t border-[#202022] mb-4"></div>

        <!-- 最近生成内容预览 -->
        <p class="text-[10px] text-zinc-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
          <Clock class="w-3 h-3 text-zinc-500" />
          最近生成
        </p>
        <div class="space-y-2.5 flex-1">
          <div
            v-for="item in demoContents"
            :key="item.id"
            @click="router.push('/factory')"
            class="p-3 rounded-xl bg-[#0b0b0b] border border-[#202022] hover:border-zinc-600 hover:bg-[#0f0f0f] transition-all cursor-pointer group"
          >
            <div class="flex items-center gap-2 mb-1.5">
              <component :is="item.icon" class="w-3.5 h-3.5 shrink-0" :class="item.iconColor" />
              <span class="text-[10px] text-zinc-500">{{ item.agentName }}</span>
              <span
                :class="['ml-auto text-[9px] px-1.5 py-0.5 rounded-md font-medium shrink-0', item.tagClass]"
              >{{ item.tag }}</span>
            </div>
            <p class="text-xs font-medium text-zinc-200 group-hover:text-white transition-colors truncate">
              {{ item.title }}
            </p>
            <p class="text-[10px] text-zinc-500 mt-0.5 truncate">{{ item.desc }}</p>
          </div>
        </div>

        <!-- CTA 按钮 -->
        <Button
          class="w-full mt-4 rounded-xl border-[#303134] bg-gradient-to-r from-blue-600/20 to-purple-600/20 hover:from-blue-600/30 hover:to-purple-600/30 text-white text-xs h-10 group"
          @click="router.push('/factory')"
        >
          <Sparkles class="w-4 h-4 mr-2 text-purple-400 group-hover:text-purple-300 transition-colors" />
          进入制造车间
          <ArrowRight class="w-3.5 h-3.5 ml-2 text-zinc-500 group-hover:translate-x-0.5 transition-transform" />
        </Button>
      </div>

      <!-- 下方左侧：资源推送预览 -->
      <div class="col-span-12 lg:col-span-4 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8 flex flex-col">
        <h3 class="text-lg font-bold text-white mb-6 flex items-center gap-2">
          <Calendar class="w-5 h-5 text-orange-500" />
          今日资源推荐
        </h3>

        <!-- 真实数据或 fallback 预览 -->
        <div class="space-y-3 flex-1">
          <template v-if="deliveryStore.todayResources.length > 0">
            <div
              v-for="(item, idx) in deliveryStore.todayResources.slice(0, 4)"
              :key="idx"
              @click="router.push('/delivery')"
              class="flex items-center gap-3 p-3 rounded-xl bg-[#0b0b0b] border border-[#202022] hover:border-zinc-700 transition-all cursor-pointer group"
            >
              <span class="text-sm font-mono text-zinc-600 w-5 text-right shrink-0 group-hover:text-zinc-400 transition-colors">{{ idx + 1 }}</span>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-zinc-200 truncate">{{ item.title }}</p>
                <p class="text-[10px] text-zinc-500">{{ item.resource_type }}</p>
              </div>
              <ChevronRight class="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
            </div>
          </template>
          <template v-else>
            <div
              v-for="(item, idx) in fallbackResources"
              :key="idx"
              @click="router.push('/delivery')"
              class="flex items-center gap-3 p-3 rounded-xl bg-[#0b0b0b] border border-[#202022] hover:border-zinc-700 transition-all cursor-pointer group"
            >
              <span class="text-sm font-mono text-zinc-600 w-5 text-right shrink-0 group-hover:text-zinc-400 transition-colors">{{ idx + 1 }}</span>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-zinc-200 truncate">{{ item.title }}</p>
                <p class="text-[10px] text-zinc-500">{{ item.description }}</p>
              </div>
              <ChevronRight class="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
            </div>
          </template>
        </div>

        <Button variant="outline" class="w-full mt-4 rounded-xl border-[#303134] bg-transparent text-xs" @click="router.push('/delivery')">
          查看全部资源
        </Button>
      </div>

      <!-- 下方右侧：学情诊断报告摘要 -->
      <div class="col-span-12 lg:col-span-8 bg-[#131314] border border-[#303134] rounded-[2.5rem] p-8 flex flex-col md:flex-row items-center gap-8">
        <div class="flex-1">
          <h3 class="text-xl font-bold text-white mb-2 underline decoration-blue-500 decoration-4 underline-offset-4">Assessor Agent 诊断</h3>
          <p class="text-zinc-400 text-sm leading-relaxed mb-6">
            本周你对线性代数的掌握程度提升了 <span class="text-emerald-500 font-bold">15%</span>，但在代码实操部分的"梯度爆炸"问题上停留超过 45 分钟。建议开启 <span class="text-blue-400">Tutor Agent</span> 专项答疑。
          </p>
          <div class="flex gap-4">
            <Button size="sm" class="rounded-lg bg-blue-600">生成周报 PDF</Button>
            <Button size="sm" variant="ghost" class="text-zinc-400">查看历史曲线</Button>
          </div>
        </div>
        <!-- 装饰性元素：雷达图占位 -->
        <div class="w-48 h-48 bg-blue-500/5 rounded-full border border-blue-500/10 flex items-center justify-center">
           <BrainCircuit class="w-20 h-20 text-blue-500/20" />
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* 虚线背景动画 */
.bg-dashed {
  background-image: linear-gradient(to right, #303134 50%, transparent 50%);
  background-size: 10px 1px;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(37,99,235,0.4); }
  70% { box-shadow: 0 0 0 20px rgba(37,99,235,0); }
  100% { box-shadow: 0 0 0 0 rgba(37,99,235,0); }
}

.animate-pulse {
  animation: pulse 2s infinite;
}
</style>  