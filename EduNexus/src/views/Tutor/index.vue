<script setup lang="ts">
import { ref } from 'vue'
import {
  ArrowRight, Loader2, CheckCircle2, Lightbulb,
  Key, GitBranch, ListTree, Database, Search, Calculator,
  FileText, Beaker, FlaskConical, ScanEye,
  Upload, ImageIcon, X, AlertCircle,
} from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { solveProblem } from '@/api/tutor'
import type { SolveStep } from '@/types/tutor'

// ── 状态 ──
const uploadedImage = ref<string | null>(null)
const isSolving = ref(false)
const solution = ref<{ steps: UiStep[]; summary: string } | null>(null)
const solverLog = ref<string[]>([])
const errorMessage = ref<string | null>(null)

// ── UI 增强后的步骤类型 ──
interface UiStep {
  title: string
  content: string[]
  icon: any
  color: string
  bg: string
}

// ── 图标/颜色分配策略 ──
const stepPresets = [
  { icons: [Search, ListTree, FileText], color: 'text-blue-400', bg: 'bg-blue-500/5 border-blue-500/15' },
  { icons: [Key, Calculator, GitBranch], color: 'text-amber-400', bg: 'bg-amber-500/5 border-amber-500/15' },
  { icons: [GitBranch, Lightbulb, Beaker], color: 'text-purple-400', bg: 'bg-purple-500/5 border-purple-500/15' },
  { icons: [Database, FlaskConical, ListTree], color: 'text-emerald-400', bg: 'bg-emerald-500/5 border-emerald-500/15' },
  { icons: [CheckCircle2, Lightbulb, Search], color: 'text-rose-400', bg: 'bg-rose-500/5 border-rose-500/15' },
]

function enhanceSteps(steps: SolveStep[]): UiStep[] {
  return steps.map((step, i) => {
    const preset = stepPresets[i % stepPresets.length]
    const iconIndex = i % preset.icons.length
    return {
      title: step.title,
      content: step.content,
      icon: preset.icons[iconIndex],
      color: preset.color,
      bg: preset.bg,
    }
  })
}

// ── 模拟推理日志（纯 UI 动画，提升体验）──
const baseMockLogs = [
  '收到图片，启动 Qwen3-VL-Flash 视觉识别...',
  '视觉模型分析图片内容，提取题目信息...',
  '识别题目类型与知识点归属...',
  '构建解题策略，规划推理步骤...',
  '执行逐步推理与计算...',
  '验证计算结果与逻辑一致性...',
  '整理输出结构化解答...',
]

// ── 图片上传处理 ──
function handleFileInput(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) processFile(file)
  input.value = ''
}

function processFile(file: File) {
  if (!file.type.startsWith('image/')) return
  const reader = new FileReader()
  reader.onload = () => {
    uploadedImage.value = reader.result as string
    solution.value = null
    solverLog.value = []
    errorMessage.value = null
  }
  reader.readAsDataURL(file)
}

function handlePaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      e.preventDefault()
      processFile(item.getAsFile()!)
      return
    }
  }
}

function handleDrop(e: DragEvent) {
  e.preventDefault()
  const file = e.dataTransfer?.files?.[0]
  if (file) processFile(file)
}

function clearImage() {
  uploadedImage.value = null
  solution.value = null
  solverLog.value = []
  errorMessage.value = null
}

// ── 解题 ──
async function solve() {
  if (!uploadedImage.value || isSolving.value) return

  isSolving.value = true
  solution.value = null
  solverLog.value = []
  errorMessage.value = null

  // 播放模拟推理日志（纯 UI 动画）
  const logTimer = playMockLogs()

  try {
    // 提取纯 base64（去掉 data:...;base64, 前缀 — 后端会处理，这里保持兼容）
    const imageBase64 = uploadedImage.value

    const res = await solveProblem({
      image_base64: imageBase64,
      message: '请帮我详细解答这道题目',
    })

    // 停止模拟日志
    clearInterval(logTimer)

    // 补全日志最后几条
    solverLog.value = [
      ...baseMockLogs,
      `解答完成：共 ${res.steps.length} 个步骤`,
    ]

    // 短暂延迟让用户看到日志完成
    await new Promise(r => setTimeout(r, 400))

    solution.value = {
      steps: enhanceSteps(res.steps),
      summary: res.summary,
    }
  } catch (err: any) {
    clearInterval(logTimer)
    const msg = err?.response?.data?.detail
      || err?.message
      || '网络请求失败，请检查后端服务是否启动'
    errorMessage.value = msg
    solverLog.value = []
  } finally {
    isSolving.value = false
  }
}

function playMockLogs(): ReturnType<typeof setInterval> {
  let i = 0
  solverLog.value = [baseMockLogs[0]]

  return setInterval(() => {
    i++
    if (i < baseMockLogs.length) {
      solverLog.value = [...solverLog.value, baseMockLogs[i]]
    }
  }, 250 + Math.random() * 350)
}
</script>

<template>
  <div class="min-h-screen bg-[#0b0b0b]">
    <!-- 背景 -->
    <div class="absolute inset-0 z-0 bg-[linear-gradient(to_right,#ffffff06_1px,transparent_1px),linear-gradient(to_bottom,#ffffff06_1px,transparent_1px)] bg-[size:48px_48px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,#000_60%,transparent_100%)]"></div>
    <div class="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-600/8 rounded-full blur-[120px] pointer-events-none"></div>

    <div class="relative z-10 max-w-4xl mx-auto px-6 py-8 pb-20">
      <!-- 头部 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-white mb-2">智能辅导 · 题目解答</h1>
        <p class="text-zinc-500 text-sm">
          上传题目图片，AI 导师识别并逐步分析解答
          <span class="ml-2 text-xs text-zinc-600">Powered by Qwen3-VL-Flash</span>
        </p>
      </div>

      <!-- 上传 / 粘贴区域 -->
      <div class="bg-[#131314] border border-[#303134] rounded-[2rem] p-6 mb-8">
        <!-- 未上传：拖拽区 -->
        <div
          v-if="!uploadedImage"
          class="relative border-2 border-dashed border-zinc-700 rounded-2xl p-12 text-center hover:border-blue-500/40 hover:bg-blue-500/[0.02] transition-all cursor-pointer"
          @click="($refs.fileInput as HTMLInputElement)?.click()"
          @paste="handlePaste"
          @dragover.prevent
          @drop="handleDrop"
        >
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="handleFileInput"
          />
          <Upload class="w-10 h-10 text-zinc-600 mx-auto mb-4" />
          <p class="text-sm text-zinc-400 mb-2">
            点击上传、拖拽图片到此处，或 <span class="text-blue-400">Ctrl+V</span> 粘贴
          </p>
          <p class="text-xs text-zinc-600">支持 JPG / PNG / WebP — Qwen3-VL-Flash 理解图片内容</p>
        </div>

        <!-- 已上传：预览 + 操作 -->
        <div v-else>
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
              <ImageIcon class="w-4 h-4 text-blue-400" />
              <span class="text-sm text-zinc-300">题目图片</span>
            </div>
            <button
              @click="clearImage"
              :disabled="isSolving"
              class="flex items-center gap-1 text-xs text-zinc-500 hover:text-zinc-300 transition-colors disabled:opacity-30"
            >
              <X class="w-3.5 h-3.5" />
              移除
            </button>
          </div>

          <!-- 图片预览 -->
          <div class="relative rounded-2xl overflow-hidden border border-[#252525] bg-[#0b0b0b] mb-5">
            <img
              :src="uploadedImage"
              alt="题目图片"
              class="w-full max-h-[400px] object-contain"
            />
            <!-- 识别中遮罩 -->
            <div
              v-if="isSolving && solverLog.length <= 1"
              class="absolute inset-0 bg-black/60 flex items-center justify-center backdrop-blur-sm"
            >
              <div class="text-center">
                <ScanEye class="w-8 h-8 text-blue-400 mx-auto mb-2 animate-pulse" />
                <p class="text-xs text-blue-300">视觉识别中...</p>
              </div>
            </div>
          </div>

          <!-- 错误提示 -->
          <div
            v-if="errorMessage"
            class="flex items-start gap-3 p-4 rounded-xl bg-red-500/5 border border-red-500/20 mb-5"
          >
            <AlertCircle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <p class="text-sm text-red-300">{{ errorMessage }}</p>
          </div>

          <Button
            @click="solve"
            :disabled="isSolving"
            class="w-full rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800/50 text-white text-sm h-11 gap-2"
          >
            <Loader2 v-if="isSolving" class="w-4 h-4 animate-spin" />
            <ArrowRight v-else class="w-4 h-4" />
            {{ isSolving ? 'Qwen3-VL-Flash 正在解答...' : '开始解答' }}
          </Button>
        </div>
      </div>

      <!-- 求解日志 (流式) -->
      <div
        v-if="solverLog.length > 0 && !solution"
        class="bg-[#131314] border border-[#202022] rounded-[2rem] p-6 mb-8 font-mono"
      >
        <p class="text-[10px] text-zinc-500 uppercase tracking-wider mb-4">推理过程</p>
        <div class="space-y-2">
          <div
            v-for="(log, i) in solverLog"
            :key="i"
            class="flex items-start gap-3 text-xs animate-in fade-in slide-in-from-top-1 duration-200"
          >
            <span class="text-emerald-500 shrink-0 mt-0.5">▸</span>
            <span class="text-zinc-400">{{ log }}</span>
          </div>
        </div>
        <div v-if="isSolving" class="flex items-center gap-2 mt-3 text-xs text-zinc-500">
          <Loader2 class="w-3 h-3 animate-spin" />
          正在等待 Qwen3-VL-Flash 响应...
        </div>
      </div>

      <!-- 解答结果 -->
      <div v-if="solution" class="space-y-5">
        <div
          v-for="(step, i) in solution.steps"
          :key="i"
          :class="['rounded-[2rem] border p-6', step.bg]"
        >
          <div class="flex items-center gap-3 mb-4">
            <div :class="['w-9 h-9 rounded-xl flex items-center justify-center', step.bg]">
              <component :is="step.icon" :class="['w-5 h-5', step.color]" />
            </div>
            <h3 :class="['text-base font-bold', step.color]">{{ step.title }}</h3>
            <CheckCircle2
              v-if="i < solution.steps.length"
              class="w-4 h-4 text-emerald-500 ml-auto"
            />
          </div>
          <div class="ml-12 space-y-1">
            <p
              v-for="(line, j) in step.content"
              :key="j"
              :class="[
                'text-sm whitespace-pre-wrap',
                line.startsWith('┌') || line.startsWith('│') || line.startsWith('├') || line.startsWith('└') || line.startsWith('  ')
                  ? 'font-mono text-zinc-400 leading-snug'
                  : line === ''
                    ? 'h-2'
                    : 'text-zinc-300 leading-relaxed',
              ]"
            >{{ line }}</p>
          </div>
        </div>

        <!-- 总结 -->
        <div class="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-[2rem] p-6">
          <div class="flex items-start gap-3">
            <Lightbulb class="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <p class="text-xs text-amber-400/80 uppercase tracking-wider mb-1">结论总结</p>
              <p class="text-sm text-zinc-200 leading-relaxed">{{ solution.summary }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
