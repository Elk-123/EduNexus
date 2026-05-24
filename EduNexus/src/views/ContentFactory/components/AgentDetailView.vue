<!-- src/views/ContentFactory/components/AgentDetailView.vue -->
<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { X, Send, Bot, User, Sparkles, FileText, Copy, CheckCircle2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { chatWithAgent } from '@/api/factory'
import type { GeneratedResource } from '@/types/factory'
import ManagerPreview from './ManagerPreview.vue'

const props = defineProps<{
  agent: any
  topic: string
  resources: GeneratedResource[]
}>()

const emit = defineEmits(['close'])

// 从传入资源中找到对应 agent 的资源
const agentResource = computed(() => {
  const r = props.resources.find(item => item.agent_type === props.agent.role.toLowerCase())
  return r as typeof r | undefined
})

// 测验题目（带难度标签和选项字母）
const quizQuestions = computed(() => {
  const questions = agentResource.value?.content?.questions ?? []
  const levels = ['基础', '进阶', '高级'] as const
  return questions.map((q: any, i: number) => ({
    ...q,
    _index: i,
    _difficulty: levels[i % 3],
    _optionLetters: ['A', 'B', 'C', 'D', 'E', 'F'].slice(0, q.options.length),
  }))
})

// 幻觉风险标签
const riskLabel = computed(() => {
  const risk = agentResource.value?.content?.hallucination_risk
  return risk ? (risk === 'low' ? '低风险' : risk === 'medium' ? '中风险' : '高风险') : ''
})

// 用于架构师思维导图渲染的 refs
const mindmapRef = ref<HTMLElement | null>(null)

// 初始化和渲染 mermaid
const initAndRenderMindmap = async (retryCount = 0) => {
  if (!mindmapRef.value) {
    if (retryCount < 3) {
      setTimeout(() => {
        initAndRenderMindmap(retryCount + 1)
      }, 100 * (retryCount + 1))
      return
    } else {
      return
    }
  }

  if (!agentResource.value?.content?.mindmap) {
    mindmapRef.value.innerHTML = '<p class="text-slate-500 text-sm">暂无思维导图数据</p>'
    return
  }

  try {
    if (typeof window.mermaid === 'undefined') {
      await new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js'
        script.onload = resolve
        script.onerror = reject
        document.head.appendChild(script)
      })
    }

    if (!mermaidInitialized) {
      await window.mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        themeVariables: {
          background: 'transparent',
          primaryColor: '#3b82f6',
          primaryTextColor: '#ffffff',
          primaryBorderColor: '#3b82f6',
          lineColor: '#4b5563'
        }
      })
      mermaidInitialized = true
    }

    renderMindmap()
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error)
    if (mindmapRef.value) {
      mindmapRef.value.innerHTML = `<p class="text-red-500 text-sm">图表加载失败: ${errorMessage}</p>`
    }
  }
}

const renderMindmap = async () => {
  try {
    if (!agentResource.value?.content?.mindmap) {
      throw new Error('No mindmap data available')
    }

    const definition = generateMermaidDefinition(agentResource.value.content.mindmap)

    if (!mindmapRef.value) {
      return
    }

    mindmapRef.value.innerHTML = '<div id="mermaid-chart-container" class="w-full h-full"></div>'
    const container = document.getElementById('mermaid-chart-container')
    if (!container) {
      return
    }

    container.innerHTML = ''

    // @ts-ignore - mermaid is loaded from CDN
    const renderResult = await window.mermaid.render('mindmap-chart-' + Date.now(), definition)

    let svgContent = ''
    if (typeof renderResult === 'object' && 'svg' in renderResult) {
      svgContent = renderResult.svg
    } else if (typeof renderResult === 'string') {
      svgContent = renderResult
    } else {
      throw new Error(`Unexpected return type: ${typeof renderResult}`)
    }

    if (svgContent && svgContent.length > 0) {
      container.innerHTML = svgContent

      // 强制设置 SVG 样式
      setTimeout(() => {
        const svgElement = container.querySelector('svg')
        if (svgElement) {
          svgElement.style.width = '100%'
          svgElement.style.height = 'auto'
          svgElement.style.background = 'transparent'

          // 设置所有文本的颜色
          const texts = svgElement.querySelectorAll('text')
          texts.forEach(text => {
            text.style.fill = '#e2e8f0'
            text.style.fontFamily = 'Inter, sans-serif'
          })
        }
      }, 100)
    } else {
      throw new Error('SVG content is empty')
    }

    // 添加自定义样式
    const style = document.createElement('style')
    style.textContent = `
      .mermaid svg {
        background: transparent !important;
        width: 100% !important;
        height: auto !important;
      }
      .mermaid .node {
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3)) !important;
      }
      .mermaid .edge {
        stroke: #4b5563 !important;
      }
      .mermaid text {
        fill: #e2e8f0 !important;
        font-family: Inter, sans-serif !important;
      }
    `
    container.appendChild(style)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error)
    if (mindmapRef.value) {
      mindmapRef.value.innerHTML = `<p class="text-red-500 text-sm">图表渲染失败: ${errorMessage}</p>`
    }
  }
}

// 生成 mermaid 定义
const generateMermaidDefinition = (mindmap: any) => {
  if (!mindmap || !mindmap.root) {
    throw new Error('Invalid mindmap structure: missing root')
  }

  // 1. 处理根节点 (确保它是 root((内容)) 格式)
  let rootNode = mindmap.root;
  // 如果后端传来的 root 只是纯文字，包装它；如果是 root((...))，保持原样
  if (!rootNode.includes('((')) {
    rootNode = `root((${rootNode}))`;
  }

  let lines = ['mindmap', rootNode];

  // 递归处理节点
  const processNode = (nodes: any[], level: number) => {
    const indent = '  '.repeat(level);

    nodes.forEach((node) => {
      if (!node.name) return;

      // 【关键修复】：清洗节点名
      // 1. 将双引号转义或替换为单引号
      // 2. 移除节点名中可能存在的方括号 [ ]，防止解析错误
      let safeName = node.name
        .replace(/"/g, "'")    // 双引转单引
        .replace(/\[/g, "")    // 移除左中括号
        .replace(/\]/g, "");   // 移除右中括号

      // 3. 统一使用 ["内容"] 包裹，这是 Mermaid 处理特殊字符最安全的方式
      lines.push(`${indent}["${safeName}"]`);

      if (node.children && Array.isArray(node.children)) {
        processNode(node.children, level + 1);
      }
    });
  };

  if (mindmap.children) {
    processNode(mindmap.children, 1);
  }

  const definition = lines.join('\n') + '\n';
  return definition;
}

// 全局的 mermaid 初始化状态
let mermaidInitialized = false

// 获取所有视频资源（从场景中提取嵌套的 video 类型资源）
const allVideos = computed(() => {
  if (!agentResource.value?.content?.scenes) return []
  const videos = []
  for (const scene of agentResource.value.content.scenes) {
    if (scene.resources) {
      for (const resource of scene.resources) {
        if (resource.type === 'video') {
          // 添加场景信息到视频
          videos.push({
            ...resource,
            sceneTitle: scene.title,
            sceneNumber: scene.scene_number
          })
        }
      }
    }
  }
  return videos
})

// 构建专家上下文信息
const buildExpertContext = () => {
  let contextInfo = ''

  switch (props.agent.role.toLowerCase()) {
    case 'professor':
      contextInfo = agentResource.value?.content?.title
        ? `我已为"${props.topic}"生成了教学文档《${agentResource.value.content.title}》，包含多个章节和详细内容。`
        : '我已为你生成了教学文档内容。'
      break
    case 'architect':
      contextInfo = agentResource.value?.content?.mindmap?.root
        ? `我已为"${props.topic}"构建了思维导图，根节点为"${agentResource.value.content.mindmap.root}"，包含多个分支和层级结构。`
        : '我已为你构建了知识图谱思维导图。'
      break
    case 'examiner':
      contextInfo = quizQuestions.value.length > 0
        ? `我已为"${props.topic}"生成了${quizQuestions.value.length}道测验题目，涵盖不同难度级别，包含详细解析。`
        : '我已为你生成了知识测验题目。'
      break
    case 'director':
      contextInfo = allVideos.value.length > 0
        ? `我已为"${props.topic}"规划了视频分镜，包含${allVideos.value.length}个场景，每个场景都有视觉描述、旁白和时长安排。`
        : '我已为你规划了视频分镜脚本。'
      break
    case 'hacker':
      contextInfo = agentResource.value?.content?.code
        ? `我已为"${props.topic}"编写了代码示例，包含完整实现、预期输出和扩展练习。`
        : '我已为你编写了代码示例。'
      break
    case 'reviewer':
      contextInfo = agentResource.value?.content?.quality_score !== undefined
        ? `我对"${props.topic}"的生成内容进行了质量审查，综合评分为${agentResource.value.content.quality_score}分，幻觉风险为${riskLabel.value}。`
        : '我已对生成内容进行了质量审查。'
      break
    default:
      contextInfo = `我已为"${props.topic}"生成了相关内容。`
  }

  return contextInfo
}

const messages = ref([
  {
    role: 'assistant',
    content: `你好！我是${props.agent.name}专家。${buildExpertContext()} 有什么问题或需要优化的地方，请随时告诉我！`,
    timestamp: new Date().toISOString()
  }
])

const input = ref('')
const isTyping = ref(false)
const agentResponse = ref('')
const showSuggestions = ref(true)
const suggestions = ref<string[]>([])

// 根据智能体角色生成不同的建议
const generateSuggestions = () => {
  const suggestionMap: Record<string, string[]> = {
    'professor': [
      '解释这个概念的核心思想',
      '提供更多的例子说明',
      '总结关键要点',
      '与其他概念对比分析'
    ],
    'architect': [
      '优化思维导图结构',
      '添加更多分支内容',
      '调整层级关系',
      '提供可视化建议'
    ],
    'examiner': [
      '生成更多练习题',
      '调整题目难度',
      '添加解析说明',
      '创建模拟测试'
    ],
    'director': [
      '增加更多场景',
      '优化脚本文本',
      '调整时长分配',
      '提供视觉建议'
    ],
    'hacker': [
      '优化代码结构',
      '添加注释说明',
      '创建测试用例',
      '改进性能'
    ],
    'reviewer': [
      '提高内容质量',
      '减少错误风险',
      '增强实用性',
      '完善细节'
    ]
  }

  suggestions.value = suggestionMap[props.agent.role.toLowerCase()] || [
    '深入解释',
    '优化内容',
    '添加例子',
    '总结要点'
  ]
}

const scrollToBottom = () => {
  nextTick(() => {
    const container = document.querySelector('.custom-scrollbar')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

const sendMessage = async () => {
  if (!input.value.trim() || isTyping.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: input.value,
    timestamp: new Date().toISOString()
  })

  const userQuery = input.value
  input.value = ''
  showSuggestions.value = false
  isTyping.value = true
  scrollToBottom()

  try {
    agentResponse.value = ''
    const response = await chatWithAgent(props.agent.id, { message: userQuery })
    await typeMessage(response.reply)

    messages.value.push({
      role: 'assistant',
      content: agentResponse.value,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Chat error:', error)
    const errorMsg = `抱歉，作为${props.agent.role}智能体，我遇到了一些问题。请稍后重试或尝试其他问题。`
    messages.value.push({
      role: 'assistant',
      content: errorMsg,
      timestamp: new Date().toISOString()
    })
  } finally {
    isTyping.value = false
    showSuggestions.value = true
    scrollToBottom()
  }
}

// 打字效果
const typeMessage = async (text: string) => {
  const words = text.split('')
  for (let i = 0; i < words.length; i++) {
    await new Promise(resolve => setTimeout(resolve, 20))
    agentResponse.value += words[i]
  }
}

const askSuggestion = (question: string) => {
  input.value = question
  sendMessage()
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// 打开外部链接
const openExternalLink = (url: string) => {
  window.open(url, '_blank')
}

// 处理图片加载失败
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTggMTZWN0M1IDE5Ljc1IDIwLjY1IDUgMTYgNEM2IDI5LjIxIDAgNCAyLjIxIDRDNC44NSAxNiAxNCAxOS41NSAxNCAxNlYxNloiIGZpbGw9IiM0NDQ0NDQiLz4KPC9zdmc+'
}

onMounted(() => {
  generateSuggestions()
  scrollToBottom()

  // 如果是架构师智能体，尝试渲染思维导图
  if (props.agent.role.toLowerCase() === 'architect' && agentResource.value?.content?.mindmap) {
    nextTick(() => {
      initAndRenderMindmap()
    })
  }
})

// 监听资源变化并渲染
watch(() => agentResource.value, () => {
  if (props.agent.role.toLowerCase() === 'architect' && agentResource.value?.content?.mindmap) {
    nextTick(() => {
      initAndRenderMindmap()
    })
  }
}, { deep: true })

// Markdown 渲染函数
const renderMarkdown = (text: string): string => {
  if (!text) return ''

  // 处理标题
  let html = text
    .replace(/^# (.*)$/gm, '<h1 class="text-xl font-bold text-blue-400 mt-6 mb-3">$1</h1>')
    .replace(/^## (.*)$/gm, '<h2 class="text-lg font-semibold text-blue-300 mt-5 mb-2">$1</h2>')
    .replace(/^### (.*)$/gm, '<h3 class="text-base font-medium text-blue-200 mt-4 mb-1">$1</h3>')

  // 处理粗体
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

  // 处理斜体
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')

  // 处理列表项
  html = html.replace(/^- (.*?)(?=\n|$)/gm, '<li class="ml-4 text-slate-300">$1</li>')

  // 处理段落和换行
  html = html.replace(/\n\n/g, '</p><p class="text-slate-300 leading-relaxed">')
  html = html.replace(/\n/g, '<br/>')
  html = `<p class="text-slate-300 leading-relaxed">${html}</p>`

  // 处理无序列表
  html = html.replace(/<li>(.*?)<\/li>/gs, '<div class="flex items-start gap-2 mt-1"><span class="text-blue-400 mt-1">•</span><span class="text-slate-300">$1</span></div>')

  return html
}
</script>

<template>
  <div class="fixed inset-0 z-50 bg-[#0b0b0b] flex flex-col animate-in fade-in duration-300">
    <!-- 顶栏 -->
    <header class="h-16 border-b border-white/10 flex items-center justify-between px-6 bg-[#111]">
      <div class="flex items-center gap-4">
        <div :class="['p-2 rounded-lg bg-black/40', agent.color]">
          <component :is="agent.icon" class="h-5 w-5" />
        </div>
        <div>
          <h2 class="text-sm font-semibold text-white">{{ agent.name }} <span class="text-slate-500 font-normal">| 深度研讨室</span></h2>
          <p class="text-[10px] text-slate-500 uppercase tracking-widest">Topic: {{ topic }}</p>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span class="text-xs text-green-500">在线</span>
        </div>
      </div>
      <Button variant="ghost" size="icon" @click="emit('close')" class="rounded-full hover:bg-white/10">
        <X class="h-5 w-5" />
      </Button>
    </header>

    <main class="flex-1 flex overflow-hidden">
      <!-- 左侧：内容展示区 -->
      <div class="flex-[1.2] border-r border-white/10 p-8 overflow-y-auto bg-black/20 custom-scrollbar">
        <div class="max-w-3xl mx-auto">
          <div class="flex items-center gap-2 mb-6">
            <FileText class="h-5 w-5 text-blue-500" />
            <span class="text-xs font-bold text-slate-500 uppercase">{{ agent.role }} 专家产出</span>
          </div>

          <!-- Professor: 文档 -->
          <div v-if="agent.role.toLowerCase() === 'professor' && agentResource?.content?.sections" class="space-y-6 bg-[#1a1a1a] rounded-2xl border border-white/5 p-6">
            <h3 class="text-xl font-bold text-blue-400">{{ agentResource.content.title }}</h3>
            <div v-for="section in agentResource.content.sections" :key="section.heading" class="prose prose-invert max-w-none">
              <h4 class="text-lg text-blue-300 mt-6 mb-3">{{ section.heading }}</h4>
              <div v-if="section.subsections" class="ml-4 space-y-4">
                <div v-for="subsection in section.subsections" :key="subsection.subheading" class="border-l-2 border-white/10 pl-4">
                  <h5 class="text-base text-blue-300 mt-4 mb-2">{{ subsection.subheading }}</h5>
                  <p class="text-slate-300 leading-relaxed text-sm">{{ subsection.body }}</p>
                </div>
              </div>
              <p v-else class="text-slate-300 leading-relaxed">{{ section.body }}</p>
            </div>
          </div>

          <!-- Architect: 思维导图 -->
          <div v-else-if="agent.role.toLowerCase() === 'architect'" class="bg-[#1a1a1a] rounded-2xl border border-white/5 p-6">
            <h3 class="text-xl font-bold text-orange-400 mb-4">{{ topic }} - 知识图谱</h3>
            <div v-if="agentResource?.content?.mindmap" ref="mindmapRef" class="min-h-[400px] bg-white/5 rounded-xl border border-dashed border-white/10">
              <p class="text-slate-500 text-sm p-4">正在加载思维导图...</p>
            </div>
            <div v-else class="text-center py-16 text-slate-500">暂无思维导图数据</div>
          </div>

          <!-- Examiner: 测验 -->
          <div v-else-if="agent.role.toLowerCase() === 'examiner' && quizQuestions.length > 0" class="space-y-4 bg-[#1a1a1a] rounded-2xl border border-white/5 p-6">
            <h3 class="text-xl font-bold text-pink-400 mb-4">知识测验</h3>
            <div v-for="q in quizQuestions" :key="q._index" class="bg-white/5 rounded-xl border border-white/5 p-4">
              <div class="flex justify-between items-start mb-3">
                <Badge class="bg-blue-500/20 text-blue-400 border-none text-[10px]">单选题</Badge>
                <span class="text-slate-600 text-[10px]">{{ q._difficulty }}</span>
              </div>
              <h5 class="text-slate-200 text-sm font-medium mb-3">Q{{ q._index + 1 }}: {{ q.question }}</h5>
              <div class="space-y-2">
                <div
                  v-for="(opt, oIdx) in q.options"
                  :key="oIdx"
                  class="flex items-center gap-2 text-sm text-slate-400 px-2 py-1.5 rounded-md hover:bg-white/5 transition-colors"
                >
                  <span class="text-[10px] w-4 text-right opacity-60">{{ q._optionLetters[oIdx] }}</span>
                  <span>{{ opt }}</span>
                  <CheckCircle2 v-if="oIdx === q.answer" class="h-3.5 w-3.5 text-green-400 ml-auto" />
                </div>
              </div>
              <div class="mt-2 text-xs text-blue-300/80">解析：{{ q.explanation }}</div>
            </div>
          </div>

          <!-- Director: 视频资源 -->
          <div v-else-if="agent.role.toLowerCase() === 'director' && allVideos.length > 0" class="space-y-4 bg-[#1a1a1a] rounded-2xl border border-white/5 p-6">
            <h3 class="text-xl font-bold text-cyan-400 mb-4">视频教程推荐</h3>
            <div class="grid gap-4">
              <div v-for="video in allVideos" :key="video.title" class="group bg-white/5 rounded-xl overflow-hidden border border-white/5 hover:border-cyan-500/30 transition-all">
                <!-- 视频封面 -->
                <div class="relative aspect-video bg-black/40 overflow-hidden cursor-pointer" @click="openExternalLink(video.url)">
                  <img :src="video.thumbnail" :alt="video.title" class="w-full h-full object-cover" @error="handleImageError">
                  <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/40"></div>
                  <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button variant="ghost" size="lg" class="h-16 w-16 rounded-full bg-cyan-600/90 hover:bg-cyan-500 text-white shadow-lg">
                      <PlayCircle class="h-8 w-8" />
                    </Button>
                  </div>
                  <!-- 时长标签 -->
                  <div class="absolute bottom-3 right-3 bg-black/60 backdrop-blur-md px-2 py-1 rounded text-white text-xs">{{ video.duration }}</div>
                  <!-- 平台标签 -->
                  <div class="absolute top-3 left-3 px-2 py-1 bg-cyan-500/20 text-cyan-400 rounded text-xs">{{ video.platform }}</div>
                </div>
                <!-- 视频信息 -->
                <div class="p-4">
                  <h5 class="font-semibold text-white mb-2 line-clamp-2">{{ video.title }}</h5>
                  <p class="text-slate-400 text-sm line-clamp-2">{{ video.description }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Director: 分镜脚本（当没有嵌套视频资源时） -->
          <div v-else-if="agent.role.toLowerCase() === 'director' && agentResource?.content?.scenes" class="space-y-4 bg-[#1a1a1a] rounded-2xl border border-white/5 p-6">
            <h3 class="text-xl font-bold text-cyan-400 mb-4">视频分镜脚本</h3>
            <div v-for="scene in agentResource.content.scenes" :key="scene.scene_number" class="bg-white/5 rounded-xl border border-white/5 p-4">
              <div class="flex items-center gap-2 mb-2">
                <Badge variant="outline" class="text-cyan-400 border-cyan-500/30 text-[10px]">场景 {{ scene.scene_number }}</Badge>
                <span class="text-slate-500 text-xs">{{ scene.duration_seconds }}秒</span>
              </div>
              <h5 class="text-white font-medium text-sm mb-2">{{ scene.title }}</h5>
              <p class="text-slate-400 text-xs leading-relaxed">{{ scene.visual }}</p>
              <div class="mt-2 text-xs text-slate-500 italic">旁白：{{ scene.voiceover }}</div>
            </div>
          </div>

          <!-- Hacker: 代码 -->
          <div v-else-if="agent.role.toLowerCase() === 'hacker' && agentResource?.content" class="bg-[#1e1e1e] rounded-2xl border border-white/5 overflow-hidden">
            <div class="bg-white/5 px-4 py-2 border-b border-white/5 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="flex gap-1.5 mr-2">
                  <div class="h-2.5 w-2.5 rounded-full bg-red-500/20"></div>
                  <div class="h-2.5 w-2.5 rounded-full bg-yellow-500/20"></div>
                  <div class="h-2.5 w-2.5 rounded-full bg-green-500/20"></div>
                </div>
                <span class="text-xs text-slate-400 font-mono">{{ (agentResource.content.title || 'code').toLowerCase().replace(/\s+/g, '_') }}.py</span>
              </div>
              <Button variant="ghost" size="sm" class="h-6 text-xs gap-1 hover:bg-white/10 text-slate-400" @click="copyToClipboard(agentResource.content.code)">
                <Copy class="h-3 w-3" /> Copy
              </Button>
            </div>
            <pre class="p-4 text-sm leading-relaxed overflow-auto max-h-[400px]"><code class="hljs python">{{ agentResource.content.code }}</code></pre>
            <div class="border-t border-white/5 px-4 py-3">
              <p class="text-xs text-slate-400 mb-1">预期输出：</p>
              <pre class="text-xs font-mono text-slate-300 bg-black/30 p-2 rounded overflow-x-auto">{{ agentResource.content.expected_output }}</pre>
            </div>
            <div v-if="agentResource.content.exercises?.length" class="border-t border-white/5 px-4 py-3">
              <p class="text-xs text-slate-400 mb-1">扩展练习：</p>
              <ul class="text-xs text-slate-300 space-y-1">
                <li v-for="(exercise, idx) in agentResource.content.exercises" :key="idx" class="flex items-start gap-2">
                  <span class="text-blue-400">•</span><span>{{ exercise }}</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Reviewer: 审查报告 -->
          <div v-else-if="agent.role.toLowerCase() === 'reviewer' && agentResource?.content" class="space-y-4 bg-[#1a1a1a] rounded-2xl border border-white/5 p-6">
            <h3 class="text-xl font-bold text-red-400 mb-4">质量审查报告</h3>
            <div class="bg-white/5 rounded-xl p-4 border border-white/5">
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm text-white">幻觉风险</span>
                <Badge
                  :class="[
                    agentResource.content.hallucination_risk === 'low' ? 'bg-green-500/20 text-green-400' :
                    agentResource.content.hallucination_risk === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  ]"
                  class="border-none text-[10px]"
                >
                  {{ riskLabel }}
                </Badge>
              </div>
              <p class="text-xs text-slate-400 leading-relaxed">{{ agentResource.content.difficulty_assessment }}</p>
            </div>
            <div class="bg-white/5 rounded-xl p-4 border border-white/5">
              <div class="flex justify-between items-center">
                <span class="text-sm text-white">综合得分</span>
                <span class="text-2xl font-bold text-blue-400">{{ agentResource.content.quality_score }}</span>
              </div>
              <div class="mt-2 w-full bg-white/10 rounded-full h-1.5">
                <div
                  class="bg-gradient-to-r from-blue-500 to-blue-600 h-1.5 rounded-full transition-all"
                  :style="{ width: `${agentResource.content.quality_score}%` }"
                ></div>
              </div>
            </div>
            <div v-if="agentResource.content.suggestions?.length">
              <h4 class="text-sm text-white mb-2">改进建议</h4>
              <div class="space-y-2">
                <div
                  v-for="(suggestion, index) in agentResource.content.suggestions"
                  :key="index"
                  class="bg-white/5 rounded-lg p-3 border border-white/5"
                >
                  <div class="flex items-start gap-2">
                    <span class="text-blue-400 mt-1">•</span>
                    <p class="text-xs text-slate-300 leading-relaxed">{{ suggestion }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Manager: 主控中枢预览 -->
          <div v-else-if="agent.role.toLowerCase() === 'manager'" class="h-full p-6">
            <ManagerPreview
              :topic="topic"
              :isGenerating="true"
              :agentsStatus="{}"
              :resources="resources"
              :logs="[]"
            />
          </div>

          <!-- 无数据时 -->
          <div v-else class="flex items-center justify-center h-64 text-slate-500 bg-white/5 rounded-2xl border border-dashed border-white/10">
            <p class="text-sm">等待生成资源数据...</p>
          </div>
        </div>
      </div>

      <!-- 右侧：对话区 -->
      <div class="flex-1 flex flex-col bg-[#0f0f0f]">
        <!-- 快捷建议 -->
        <div v-if="showSuggestions" class="p-4 border-b border-white/10 bg-black/30">
          <p class="text-xs text-slate-500 mb-2">快速提问：</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="(suggestion, idx) in suggestions"
              :key="idx"
              @click="askSuggestion(suggestion)"
              class="text-xs bg-white/10 hover:bg-white/20 text-slate-300 px-3 py-1.5 rounded-full transition-colors"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>

        <!-- 对话内容 -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          <div v-for="(msg, idx) in messages" :key="idx"
            :class="['flex gap-4 animate-in slide-in-from-bottom-2 duration-300', msg.role === 'user' ? 'flex-row-reverse' : '']">
            <div :class="['h-8 w-8 rounded-full flex items-center justify-center shrink-0 flex-shrink-0',
              msg.role === 'assistant' ? 'bg-blue-600/20 text-blue-400' : 'bg-slate-700 text-slate-200']">
              <Bot v-if="msg.role === 'assistant'" class="h-4 w-4" />
              <User v-else class="h-4 w-4" />
            </div>
            <div :class="['max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed break-words',
              msg.role === 'assistant' ? 'bg-white/5 text-slate-300' : 'bg-blue-600 text-white shadow-lg shadow-blue-900/20']">
              <div v-if="msg.role === 'assistant' && agent.role.toLowerCase() === 'hacker'" class="font-mono text-green-400">
                {{ msg.content }}
              </div>
              <div v-else-if="msg.role === 'assistant' && agent.role.toLowerCase() === 'professor'" class="prose prose-invert max-w-none">
                <div v-html="renderMarkdown(msg.content)"></div>
              </div>
              <div v-else>{{ msg.content }}</div>
              <div class="text-xs text-slate-500 mt-2">
                {{ new Date(msg.timestamp).toLocaleTimeString() }}
              </div>
            </div>
          </div>

          <!-- 正在输入指示器 -->
          <div v-if="isTyping" class="flex gap-4">
            <div class="h-8 w-8 rounded-full bg-blue-600/20 flex items-center justify-center">
              <Sparkles class="h-4 w-4 text-blue-400 animate-spin" />
            </div>
            <div class="bg-white/5 p-4 rounded-2xl">
              <div class="flex gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-blue-500/50 animate-bounce"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-blue-500/50 animate-bounce [animation-delay:0.2s]"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-blue-500/50 animate-bounce [animation-delay:0.4s]"></span>
              </div>
              <p class="text-xs text-slate-400 mt-2">{{ agent.name }} 正在思考...</p>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="p-6 border-t border-white/10">
          <div class="relative">
            <textarea
              v-model="input"
              @keyup.enter.ctrl="sendMessage"
              placeholder="输入您的问题或要求（Ctrl+Enter 发送）..."
              class="w-full bg-[#1a1a1a] border border-white/10 rounded-xl pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all resize-none"
              rows="2"
            ></textarea>
            <div class="absolute right-2 bottom-2 flex items-center gap-2">
              <Button
                @click="sendMessage"
                :disabled="!input.trim() || isTyping"
                size="icon"
                class="rounded-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800"
              >
                <Send class="h-5 w-5" />
              </Button>
            </div>
          </div>
          <div class="flex justify-between items-center mt-3">
            <p class="text-xs text-slate-500">对话将实时更新左侧生成内容</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #222; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #333; }
</style>
