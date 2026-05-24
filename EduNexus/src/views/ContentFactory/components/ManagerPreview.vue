<!-- src/views/ContentFactory/components/ManagerPreview.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import {
  BarChart, Clock, FileText, GitFork, ClipboardCheck, Video, Code2, ShieldCheck,
  AlertCircle, CheckCircle2, XCircle, Zap, Cpu, BrainCircuit
} from 'lucide-vue-next'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'

interface Props {
  topic: string
  isGenerating: boolean
  agentsStatus: Record<string, string>
  resources: any[]
  logs: any[]
  taskStatus?: string
}

const props = defineProps<Props>()

// 计算生成进度 - 根据智能体状态计算
const generationProgress = computed(() => {
  const agentTypes = ['manager', 'professor', 'architect', 'examiner', 'director', 'hacker', 'reviewer']
  const completedCount = agentTypes.filter(agent =>
    props.agentsStatus[agent] === 'success'
  ).length

  return Math.round((completedCount / agentTypes.length) * 100)
})

// 各智能体状态统计
const agentStats = computed(() => {
  const stats = {
    running: 0,
    success: 0,
    error: 0,
    idle: 0
  }

  Object.values(props.agentsStatus).forEach(status => {
    if (stats.hasOwnProperty(status)) {
      stats[status as keyof typeof stats]++
    }
  })

  return stats
})

// 资源类型统计 - 使用后端实际的 resource_type
const resourceStats = computed(() => {
  const stats: Record<string, number> = {
    document: 0,
    mindmap: 0,
    quiz: 0,
    video_script: 0,
    code_lab: 0,
    review_report: 0
  }

  props.resources.forEach(resource => {
    if (stats.hasOwnProperty(resource.resource_type)) {
      stats[resource.resource_type]++
    }
  })

  return stats
})

// 最近的日志事件 - 过滤出重要的日志
const recentLogs = computed(() => {
  // 只显示 info 和 success 类型的日志，排除 warn 和错误
  const importantLogs = props.logs.filter(log =>
    log.type === 'info' || log.type === 'success'
  )

  return [...importantLogs].reverse().slice(0, 8)
})

// 获取日志类型的图标和颜色
const getLogIconAndColor = (type: string) => {
  switch (type) {
    case 'info':
      return { icon: Cpu, color: 'text-blue-400' }
    case 'success':
      return { icon: CheckCircle2, color: 'text-green-400' }
    case 'warn':
      return { icon: AlertCircle, color: 'text-yellow-400' }
    default:
      return { icon: BrainCircuit, color: 'text-purple-400' }
  }
}

// 获取资源类型的图标和显示名称
const getResourceTypeInfo = (type: string) => {
  const types: Record<string, { icon: any; name: string; color: string }> = {
    document: { icon: FileText, name: '教授文档', color: 'text-blue-400' },
    mindmap: { icon: GitFork, name: '思维导图', color: 'text-orange-400' },
    quiz: { icon: ClipboardCheck, name: '测验题目', color: 'text-pink-400' },
    video_script: { icon: Video, name: '视频脚本', color: 'text-cyan-400' },
    code_lab: { icon: Code2, name: '代码实验', color: 'text-green-400' },
    review_report: { icon: ShieldCheck, name: '审查报告', color: 'text-red-400' }
  }
  return types[type] || { icon: FileText, name: type, color: 'text-slate-400' }
}

// 任务总体状态
const taskOverallStatus = computed(() => {
  if (props.isGenerating) return 'generating'
  if (props.taskStatus === 'completed') return 'completed'
  if (props.taskStatus === 'failed') return 'failed'
  return 'idle'
})

// 质量评分（从审查报告中获取）
const qualityScore = computed(() => {
  const reviewResource = props.resources.find(r => r.agent_type === 'reviewer')
  return reviewResource?.content?.quality_score || 0
})

// 幻觉风险
const hallucinationRisk = computed(() => {
  const reviewResource = props.resources.find(r => r.agent_type === 'reviewer')
  return reviewResource?.content?.hallucination_risk || 'low'
})
</script>

<template>
  <div class="h-full flex flex-col p-4">
    <!-- 顶部状态栏 -->
    <div class="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
      <div class="flex items-center gap-3">
        <div class="p-2 rounded-lg bg-purple-500/20 text-purple-400">
          <BrainCircuit class="h-5 w-5" />
        </div>
        <div>
          <h2 class="text-xl font-bold text-white">主控中枢</h2>
          <p class="text-sm text-slate-400">生成流水线监控面板</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Badge
          :class="[
            taskOverallStatus === 'generating' ? 'bg-blue-500/20 text-blue-400' :
            taskOverallStatus === 'completed' ? 'bg-green-500/20 text-green-400' :
            taskOverallStatus === 'failed' ? 'bg-red-500/20 text-red-400' :
            'bg-slate-500/20 text-slate-400'
          ]"
          class="text-sm font-medium px-3 py-1"
        >
          {{
            taskOverallStatus === 'generating' ? '生成中' :
            taskOverallStatus === 'completed' ? '已完成' :
            taskOverallStatus === 'failed' ? '失败' :
            '空闲'
          }}
        </Badge>
        <div class="text-xs text-slate-500">
          {{ topic || '等待输入主题...' }}
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="flex-1 space-y-6">
      <!-- 进度和质量 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- 生成进度 -->
        <div class="bg-gradient-to-br from-blue-900/30 to-blue-800/20 rounded-2xl border border-blue-500/20 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-blue-300 flex items-center gap-2">
              <Zap class="h-4 w-4" />
              生成进度
            </h3>
            <Badge class="bg-blue-500/20 text-blue-300 text-[11px] font-medium">
              {{ generationProgress }}%
            </Badge>
          </div>
          <Progress :model-value="generationProgress" class="h-2 bg-blue-500/10" />
          <div class="mt-4 grid grid-cols-4 gap-2 text-center">
            <div class="text-xs">
              <div class="font-medium text-white">{{ agentStats.success }}</div>
              <div class="text-slate-400">完成</div>
            </div>
            <div class="text-xs">
              <div class="font-medium text-white">{{ agentStats.running }}</div>
              <div class="text-slate-400">运行中</div>
            </div>
            <div class="text-xs">
              <div class="font-medium text-white">{{ agentStats.error }}</div>
              <div class="text-slate-400">错误</div>
            </div>
            <div class="text-xs">
              <div class="font-medium text-white">{{ agentStats.idle }}</div>
              <div class="text-slate-400">待处理</div>
            </div>
          </div>
        </div>

        <!-- 质量评估 -->
        <div class="bg-gradient-to-br from-purple-900/30 to-purple-800/20 rounded-2xl border border-purple-500/20 p-6">
          <h3 class="text-lg font-semibold text-purple-300 flex items-center gap-2 mb-4">
            <ShieldCheck class="h-4 w-4" />
            质量评估
          </h3>
          <div class="flex items-center justify-between mb-4">
            <div class="text-3xl font-bold text-white">
              {{ qualityScore || '--' }}
            </div>
            <Badge
              :class="[
                hallucinationRisk === 'low' ? 'bg-green-500/20 text-green-400' :
                hallucinationRisk === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-red-500/20 text-red-400'
              ]"
              class="text-sm px-3 py-1 font-medium"
            >
              {{
                hallucinationRisk === 'low' ? '低幻觉风险' :
                hallucinationRisk === 'medium' ? '中幻觉风险' :
                '高幻觉风险'
              }}
            </Badge>
          </div>
          <div class="text-xs text-slate-300">
            基于内容审查报告的综合质量评分
          </div>
        </div>
      </div>

      <!-- 资源概览 -->
      <div class="bg-[#1a1a1a] rounded-2xl border border-white/5 p-6">
        <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <FileText class="h-4 w-4 text-blue-400" />
          资源概览
        </h3>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div
            v-for="(count, type) in resourceStats"
            :key="type"
            class="bg-white/5 rounded-xl p-4 border border-white/10 hover:border-blue-500/30 transition-all"
          >
            <div class="flex items-center justify-between mb-2">
              <component
                :is="getResourceTypeInfo(type).icon"
                :class="['h-4 w-4', getResourceTypeInfo(type).color]"
              />
              <Badge class="text-[10px] bg-white/10 border-none">
                {{ count }}
              </Badge>
            </div>
            <div class="text-xs font-medium text-white">
              {{ getResourceTypeInfo(type).name }}
            </div>
            <div class="text-[10px] text-slate-500 mt-1">
              已生成
            </div>
          </div>
        </div>
      </div>

      <!-- 实时活动日志 -->
      <div class="bg-[#1a1a1a] rounded-2xl border border-white/5 p-6 flex-1">
        <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Clock class="h-4 w-4 text-purple-400" />
          实时活动
        </h3>
        <div class="h-[280px] overflow-y-auto custom-scrollbar">
          <div
            v-for="(log, index) in recentLogs"
            :key="index"
            class="flex items-start gap-3 p-3 hover:bg-white/5 rounded-lg transition-colors"
          >
            <div class="mt-1">
              <div class="w-1.5 h-1.5 rounded-full" :class="getLogIconAndColor(log.type).color"></div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-[11px] font-medium text-white">{{ log.agent }}</span>
                <span class="text-[9px] text-slate-500">•</span>
                <span class="text-[9px] text-slate-400">
                  {{ new Date(log.timestamp).toLocaleTimeString() }}
                </span>
              </div>
              <div class="text-sm text-slate-300 break-words">
                {{ log.message }}
              </div>
            </div>
          </div>
          <div v-if="recentLogs.length === 0" class="text-center py-8 text-slate-500">
            <Clock class="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p class="text-sm">暂无活动记录</p>
            <p class="text-xs text-slate-400 mt-1">开始生成内容后将显示实时日志</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部提示 -->
    <div class="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
      <p class="text-xs text-blue-300 leading-relaxed">
        💡 <span class="font-medium">提示：</span>主控中枢协调 6 位专家智能体并行工作，完成生成后会进行质量审查。点击左侧智能体卡片可进入深度研讨室进行 1-on-1 优化对话。
      </p>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #222;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #333;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>