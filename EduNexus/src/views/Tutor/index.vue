<script setup lang="ts">
import { ref } from 'vue'
import { ArrowRight, Loader2, CheckCircle2, Lightbulb, Key, GitBranch, ListTree, Database, Upload, ImageIcon, X, ScanEye } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

const uploadedImage = ref<string | null>(null)
const isSolving = ref(false)
const solution = ref<any>(null)
const solverLog = ref<string[]>([])

// ── Mock 解答：数据库范式分解 ──
const mockSolution = {
  steps: [
    {
      title: 'Step 1：分析函数依赖',
      icon: ListTree,
      color: 'text-blue-400',
      bg: 'bg-blue-500/5 border-blue-500/15',
      content: [
        '从关系 R(A,B,C,D,E,F) 和数据实例出发，确定属性间的函数依赖关系：',
        '',
        '• A → B   (职工号 → 职工名)     每个职工号唯一确定一个姓名',
        '• A → C   (职工号 → 年龄)       每个职工号唯一确定年龄',
        '• A → D   (职工号 → 性别)       每个职工号唯一确定性别',
        '• A → E   (职工号 → 单位号)     每个职工号唯一确定所属单位',
        '• E → F   (单位号 → 单位名)     每个单位号唯一确定单位名称',
        '',
        '综上，函数依赖集 F = { A→B, A→C, A→D, A→E, E→F }',
      ],
    },
    {
      title: 'Step 2：确定候选码 (Candidate Key)',
      icon: Key,
      color: 'text-amber-400',
      bg: 'bg-amber-500/5 border-amber-500/15',
      content: [
        '属性 A 的闭包 A⁺：',
        '',
        '  A⁺ = {A}',
        '  → 由 A→B 得 A⁺ = {A, B}',
        '  → 由 A→C 得 A⁺ = {A, B, C}',
        '  → 由 A→D 得 A⁺ = {A, B, C, D}',
        '  → 由 A→E 得 A⁺ = {A, B, C, D, E}',
        '  → 由 E→F 得 A⁺ = {A, B, C, D, E, F}  = R 的全属性集',
        '',
        '∵ A⁺ 包含了 R 的全部属性，且 A 无法再缩小',
        '∴ A (职工号) 是唯一的候选码。',
        '',
        '主属性：A',
        '非主属性：B, C, D, E, F',
      ],
    },
    {
      title: 'Step 3：判断范式等级',
      icon: GitBranch,
      color: 'text-purple-400',
      bg: 'bg-purple-500/5 border-purple-500/15',
      content: [
        '① 1NF 检查：',
        '   所有属性均为原子类型，满足 1NF。✓',
        '',
        '② 2NF 检查：',
        '   候选码为单属性 A，不存在非主属性对候选码的部分函数依赖。',
        '   满足 2NF。✓',
        '',
        '③ 3NF 检查：',
        '   考察是否存在非主属性对候选码的传递函数依赖：',
        '',
        '   A → E  (职工号决定单位号)',
        '   E → F  (单位号决定单位名)',
        '   ∴ A → F 是传递函数依赖 (A→E, E→F, 且 E↛A)',
        '',
        '   F 通过 E 传递依赖于候选码 A，违反 3NF 条件。',
        '',
        '结论：R ∈ 2NF，但 ∉ 3NF。',
      ],
    },
    {
      title: 'Step 4：规范化为 3NF — 消除传递依赖',
      icon: Database,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/5 border-emerald-500/15',
      content: [
        '消除传递函数依赖 A→E→F，将原关系分解为两个子关系：',
        '',
        '┌─────────────────────────────────────────────────────┐',
        '│  R1 (职工信息)                                       │',
        '│  属性: A(职工号), B(职工名), C(年龄), D(性别), E(单位号) │',
        '│  主码: A                                            │',
        '│  函数依赖: A→B, A→C, A→D, A→E                      │',
        '│  满足 3NF（不存在传递依赖）                            │',
        '├─────────────────────────────────────────────────────┤',
        '│  R2 (单位信息)                                       │',
        '│  属性: E(单位号), F(单位名)                            │',
        '│  主码: E                                            │',
        '│  函数依赖: E→F                                       │',
        '│  满足 3NF                                            │',
        '└─────────────────────────────────────────────────────┘',
        '',
        '分解后 R1 和 R2 均满足 3NF，且通过外码 R1.E → R2.E 保持无损连接。',
      ],
    },
  ],
  summary: '原关系 R 属于 2NF，通过消除传递依赖 A→E→F 分解为 R1(职工信息) 和 R2(单位信息)，两者均满足 3NF。',
}

const mockLogs = [
  '收到图片，启动 OCR 文字识别...',
  'OCR 识别完成，提取题目文本...',
  '题目类型识别：数据库范式规范化问题',
  '提取属性集: {A,B,C,D,E,F}，扫描数据实例...',
  '推断函数依赖: A→B, A→C, A→D, A→E, E→F',
  '计算候选码闭包 A⁺ = {A,B,C,D,E,F}',
  '检测到传递依赖: A→E→F',
  '判定当前范式: 2NF (不满足3NF)',
  '规划3NF分解: R1(A,B,C,D,E), R2(E,F)',
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
}

// ── 解题 ──
async function solve() {
  if (!uploadedImage.value || isSolving.value) return

  isSolving.value = true
  solution.value = null
  solverLog.value = []

  for (const log of mockLogs) {
    await new Promise(r => setTimeout(r, 200 + Math.random() * 300))
    solverLog.value = [...solverLog.value, log]
  }

  await new Promise(r => setTimeout(r, 400))
  solution.value = mockSolution
  isSolving.value = false
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
        <p class="text-zinc-500 text-sm">上传题目图片，AI 导师识别并逐步分析解答</p>
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
          <p class="text-sm text-zinc-400 mb-2">点击上传、拖拽图片到此处，或 <span class="text-blue-400">Ctrl+V</span> 粘贴</p>
          <p class="text-xs text-zinc-600">支持 JPG / PNG / WebP</p>
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
            <!-- OCR 识别中遮罩 -->
            <div
              v-if="isSolving && solverLog.length <= 1"
              class="absolute inset-0 bg-black/60 flex items-center justify-center backdrop-blur-sm"
            >
              <div class="text-center">
                <ScanEye class="w-8 h-8 text-blue-400 mx-auto mb-2 animate-pulse" />
                <p class="text-xs text-blue-300">OCR 识别中...</p>
              </div>
            </div>
          </div>

          <Button
            @click="solve"
            :disabled="isSolving"
            class="w-full rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800/50 text-white text-sm h-11 gap-2"
          >
            <Loader2 v-if="isSolving" class="w-4 h-4 animate-spin" />
            <ArrowRight v-else class="w-4 h-4" />
            {{ isSolving ? '正在解答...' : '开始解答' }}
          </Button>
        </div>
      </div>

      <!-- 求解日志 (流式) -->
      <div v-if="solverLog.length > 0 && !solution" class="bg-[#131314] border border-[#202022] rounded-[2rem] p-6 mb-8 font-mono">
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
          正在推理...
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
            <CheckCircle2 v-if="i < solution.steps.length" class="w-4 h-4 text-emerald-500 ml-auto" />
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
                    : 'text-zinc-300 leading-relaxed'
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
