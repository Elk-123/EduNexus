<!-- src/views/ContentFactory/components/ResourceDisplay.vue -->
<script setup lang="ts">
import {
  FileText,
  GitFork,
  ClipboardCheck,
  Video,
  Code2,
  CheckCircle2,
  Download,
  Copy,
  PlayCircle,
  BrainCircuit,
  AlertCircle
} from 'lucide-vue-next'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import type { GeneratedResource } from '@/types/factory'
import { computed, watch, onMounted, nextTick, ref } from 'vue'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

// 声明 mermaid 全局变量
declare global {
  interface Window {
    mermaid: any
  }
}

// Refs
const codePre = ref<HTMLElement>()
const codeElement = ref<HTMLElement>()
const mindmapRef = ref<HTMLElement | null>(null)

// 调试函数：检查组件状态
const debugComponentState = () => {
  console.log('=== 组件状态调试 ===')
  console.log('1. mindmapRef 存在:', !!mindmapRef.value)
  if (mindmapRef.value) {
    console.log('2. mindmapRef 元素:', mindmapRef.value)
  }
  console.log('3. architectResource 存在:', !!architectResource.value)
  if (architectResource.value) {
    console.log('4. architectResource 有内容:', !!architectResource.value.content)
    if (architectResource.value.content) {
      console.log('5. mindmap 数据存在:', !!architectResource.value.content.mindmap)
    }
  }
  console.log('6. 资源总数:', props.resources.length)
  console.log('7. 是否正在生成:', props.isGenerating)
  console.log('8. 主题:', props.topic)
  console.log('===================')
}

interface Props {
  resources: GeneratedResource[]
  isGenerating: boolean
  topic: string
  defaultTab?: string
}

const props = defineProps<Props>()
const activeTab = ref(props.defaultTab || 'professor')

// 调试：监听资源变化
watch(() => props.resources, (newResources) => {
  console.log('ResourceDisplay: Resources updated', newResources)
  debugComponentState()
  // 打印 architectResource 的详细信息
  console.log('Architect resource:', architectResource.value)
  if (architectResource.value?.content?.mindmap) {
    console.log('Mindmap structure:', architectResource.value.content.mindmap)
    console.log('Mindmap root:', architectResource.value.content.mindmap.root)
    console.log('Mindmap children:', architectResource.value.content.mindmap.children)
  }
}, { deep: true })

// 获取各个智能体的资源
const professorResource = computed(() => props.resources.find(r => r.agent_type === 'professor'))
const architectResource = computed(() => props.resources.find(r => r.agent_type === 'architect'))
const examinerResource = computed(() => props.resources.find(r => r.agent_type === 'examiner'))
const directorResource = computed(() => props.resources.find(r => r.agent_type === 'director'))
const hackerResource = computed(() => props.resources.find(r => r.agent_type === 'hacker'))
const reviewerResource = computed(() => props.resources.find(r => r.agent_type === 'reviewer'))

// 复制代码到剪贴板
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// 渲染 mermaid 图表
// const mindmapRef = ref<HTMLElement | null>(null)

// 获取所有视频资源
const getAllVideos = () => {
  if (!directorResource.value?.content?.scenes) return []

  const videos = []
  for (const scene of directorResource.value.content.scenes) {
    if (scene.resources) {
      for (const video of scene.resources) {
        if (video.type === 'video') {
          // 添加场景信息到视频
          videos.push({
            ...video,
            sceneTitle: scene.title,
            sceneNumber: scene.scene_number
          })
        }
      }
    }
  }
  return videos
}

// 初始化和渲染 mermaid
const initAndRenderMindmap = async (retryCount = 0) => {
  console.log('initAndRenderMindmap called, retryCount:', retryCount)
  console.log('mindmapRef exists:', !!mindmapRef.value)
  console.log('architectResource:', architectResource.value)

  // 如果 mindmapRef 还未设置，最多重试3次
  if (!mindmapRef.value) {
    if (retryCount < 3) {
      console.warn(`mindmapRef is null, retrying (${retryCount + 1}/3)...`)
      setTimeout(() => {
        initAndRenderMindmap(retryCount + 1)
      }, 100 * (retryCount + 1))
      return
    } else {
      console.error('mindmapRef is null after 3 retries')
      return
    }
  }

  if (!architectResource.value?.content?.mindmap) {
    console.log('No mindmap data available')
    mindmapRef.value.innerHTML = '<p class="text-slate-500">暂无思维导图数据</p>'
    return
  }

  try {
    console.log('Checking if mermaid is available...')
    if (typeof window.mermaid === 'undefined') {
      console.log('Loading mermaid from CDN...')
      await new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js'
        script.onload = resolve
        script.onerror = reject
        document.head.appendChild(script)
      })
      console.log('Mermaid loaded from CDN')
    }

    // 初始化 mermaid
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
      console.log('Mermaid initialized')
    }

    renderMindmap()
  } catch (error) {
    console.error('Mermaid loading failed:', error)
    const errorMessage = error instanceof Error ? error.message : String(error)
    mindmapRef.value.innerHTML = `<p class="text-red-500">图表加载失败: ${errorMessage}</p>`
  }
}

const renderMindmap = async () => {
  try {
    console.log('renderMindmap called')

    if (!architectResource.value?.content?.mindmap) {
      console.error('No mindmap data available')
      throw new Error('No mindmap data available')
    }

    console.log('Mindmap data found:', architectResource.value.content.mindmap)
    console.log('Mindmap root:', architectResource.value.content.mindmap.root)
    console.log('Mindmap children:', architectResource.value.content.mindmap.children)
    console.log('Mindmap data type:', typeof architectResource.value.content.mindmap)

    const definition = generateMermaidDefinition(architectResource.value.content.mindmap)
    console.log('Chart definition generated:', definition)
    console.log('Definition length:', definition.length)

    const svgId = 'mindmap-chart-' + Date.now()
    console.log('Using SVG ID:', svgId)

    // 清空容器
    if (!mindmapRef.value) {
      console.error('mindmapRef is null')
      return
    }

    // 清空容器并添加新的容器
    mindmapRef.value.innerHTML = '<div id="mermaid-chart-container" class="w-full h-full"></div>'
    const container = document.getElementById('mermaid-chart-container')
    if (!container) {
      console.error('Container not found')
      return
    }

    console.log('Container created, rendering mermaid...')

    // 先清空容器，防止内容残留
    container.innerHTML = ''

    // @ts-ignore - mermaid is loaded from CDN
    const renderResult = await window.mermaid.render(svgId, definition)
    console.log('Mermaid render result type:', typeof renderResult)
    console.log('Render result preview:', JSON.stringify(renderResult).substring(0, 200))

    let svgContent = ''
    if (typeof renderResult === 'object' && 'svg' in renderResult) {
      // 新版本 mermaid 返回对象 { svg: string }
      svgContent = renderResult.svg
      console.log('从对象获取 SVG，类型:', typeof svgContent)
    } else if (typeof renderResult === 'string') {
      // 旧版本 mermaid 返回字符串
      svgContent = renderResult
      console.log('直接使用字符串 SVG，类型:', typeof svgContent)
    } else {
      throw new Error(`意外的返回值类型: ${typeof renderResult}`)
    }

    console.log('SVG 内容长度:', svgContent.length)

    if (svgContent && svgContent.length > 0) {
      // 直接设置 innerHTML
      container.innerHTML = svgContent
      console.log('SVG 内容已添加到容器')

      // 验证内容是否成功添加
      const svgElement = container.querySelector('svg')
      console.log('SVG 元素是否存在:', !!svgElement)
      console.log('SVG 元素内容长度:', svgElement ? svgElement.innerHTML.length : 0)

      // 强制设置 SVG 样式
      setTimeout(() => {
        if (svgElement) {
          console.log('Applying styles to SVG')
          svgElement.style.width = '100%'
          svgElement.style.height = 'auto'
          svgElement.style.background = 'transparent'

          // 设置所有文本的颜色
          const texts = svgElement.querySelectorAll('text')
          texts.forEach(text => {
            text.style.fill = '#e2e8f0'
            text.style.fontFamily = 'Inter, sans-serif'
          })

          console.log('SVG styles applied')
        } else {
          console.warn('SVG element not found for styling')
        }
      }, 100)
    } else {
      throw new Error('SVG 内容为空')
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
    console.log('Mindmap rendered successfully')
  } catch (error) {
    console.error('Mermaid rendering failed:', error)
    const errorMessage = error instanceof Error ? error.message : String(error)
    console.error('Error details:', errorMessage)
    if (mindmapRef.value) {
      mindmapRef.value.innerHTML = `<p class="text-red-500">图表渲染失败: ${errorMessage}</p>`
    }
  }
}

// 生成 mermaid 定义 - 修复版本
const generateMermaidDefinition = (mindmap: any) => {
  console.log('Generating mindmap definition for:', mindmap)

  // 确保数据结构正确
  if (!mindmap || !mindmap.root) {
    throw new Error('Invalid mindmap structure: missing root')
  }

  // 1. 处理根节点 (确保它是 root((内容)) 格式)
  let rootNode = mindmap.root;
  // 如果后端传来的 root 只是纯文字，包装它；如果是 root((...))，保持原样
  if (!rootNode.includes('((')) {
    rootNode = `root((${rootNode}))`;
  }

  console.log('Processed root node:', rootNode);

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

      console.log(`Processing node at level ${level}: "${node.name}" -> "${safeName}"`);

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

  console.log('Final generated definition:', definition);
  return definition;
}

// 监听资源变化并渲染
watch(() => architectResource.value, () => {
  console.log('architectResource changed:', architectResource.value)
  nextTick(() => {
    // 确保DOM已经渲染
    if (!mindmapRef.value) {
      console.warn('mindmapRef is null, retrying in 100ms...')
      setTimeout(() => {
        initAndRenderMindmap()
      }, 100)
    } else {
      initAndRenderMindmap()
    }
  })
}, { deep: true })

// 添加一个全局的 mermaid 初始化状态
let mermaidInitialized = false

// 组件挂载后尝试渲染
onMounted(() => {
  console.log('ResourceDisplay mounted')
  debugComponentState()
  // 使用 nextTick 确保 DOM 已渲染
  nextTick(() => {
    // 双重检查，确保 mindmapRef 已经设置
    if (mindmapRef.value) {
      initAndRenderMindmap()
    } else {
      console.warn('mindmapRef is still null on mounted, retrying...')
      setTimeout(() => {
        initAndRenderMindmap()
      }, 200)
    }
  })
})

// 打开外部链接
const openExternalLink = (url: string) => {
  window.open(url, '_blank')
}

// 处理图片加载失败
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTggMTZWN0M1IDE5Ljc1IDIwLjY1IDUgMTYgNEM2IDI5LjIxIDAgNCAyLjIxIDRDNC44NSAxNiAxNCAxOS41NSAxNCAxNlYxNloiIGZpbGw9IiM0NDQ0NDQiLz4KPC9zdmc+'
}

// 代码高亮函数
const highlightCode = () => {
  nextTick(() => {
    if (codeElement.value) {
      // 使用 highlight.js 高亮代码
      hljs.highlightElement(codeElement.value)
    }
  })
}

// 监听 hackerResource 变化，当代码内容变化时重新高亮
watch(() => hackerResource.value?.content?.code, (newCode, oldCode) => {
  if (newCode && newCode !== oldCode) {
    highlightCode()
  }
}, { immediate: true })
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- 未开始状态 -->
    <div v-if="!props.topic && !props.isGenerating" class="flex-1 flex flex-col items-center justify-center text-slate-500 bg-white/5 rounded-3xl border border-dashed border-white/10">
      <div class="p-4 rounded-full bg-white/5 mb-4">
        <FileText class="h-10 w-10 opacity-20" />
      </div>
      <h3 class="text-lg font-medium text-slate-400 mb-1">等待输入主题</h3>
      <p class="text-sm text-slate-600">在左侧输入关键词，开始智能内容生成</p>
    </div>

    <!-- 生成中状态 -->
    <div v-else-if="props.isGenerating" class="flex-1 flex flex-col items-center justify-center text-slate-500 bg-white/5 rounded-3xl border border-white/10">
      <div class="relative">
        <div class="h-16 w-16 rounded-full border-4 border-blue-500 border-t-transparent animate-spin"></div>
      </div>
      <p class="mt-4 text-sm text-slate-400">正在生成内容，请稍候...</p>
    </div>


    <!-- 错误提示 -->
    <div v-if="props.resources.length === 0 && !props.isGenerating && props.topic" class="p-4 bg-red-900/20 border border-red-500/50 rounded-lg mb-4">
      <p class="text-xs text-red-400">⚠️ 没有加载到资源数据</p>
      <p class="text-xs text-red-400 mt-1">请检查后端服务是否正常运行</p>
    </div>

    <!-- 生成完成状态 -->
    <div v-else-if="props.resources.length > 0" class="flex-1 flex flex-col">

      <Tabs :default-value="activeTab" class="h-full flex flex-col">
        <TabsList class="w-full justify-start bg-transparent p-0 border-b border-white/10">
          <TabsTrigger value="professor" class="flex items-center gap-2 px-4 py-2 data-[state=active]:bg-transparent">
            <FileText class="h-4 w-4" />
            <span class="text-sm">教授文档</span>
          </TabsTrigger>
          <TabsTrigger value="mindmap" class="flex items-center gap-2 px-4 py-2 data-[state=active]:bg-transparent" @click="nextTick(() => initAndRenderMindmap())">
            <GitFork class="h-4 w-4" />
            <span class="text-sm">思维导图</span>
          </TabsTrigger>
          <TabsTrigger value="quiz" class="flex items-center gap-2 px-4 py-2 data-[state=active]:bg-transparent">
            <ClipboardCheck class="h-4 w-4" />
            <span class="text-sm">测验题目</span>
          </TabsTrigger>
          <TabsTrigger value="video" class="flex items-center gap-2 px-4 py-2 data-[state=active]:bg-transparent">
            <Video class="h-4 w-4" />
            <span class="text-sm">视频资源</span>
          </TabsTrigger>
          <TabsTrigger value="code" class="flex items-center gap-2 px-4 py-2 data-[state=active]:bg-transparent">
            <Code2 class="h-4 w-4" />
            <span class="text-sm">代码实验</span>
          </TabsTrigger>
          <TabsTrigger value="review" class="flex items-center gap-2 px-4 py-2 data-[state=active]:bg-transparent">
            <CheckCircle2 class="h-4 w-4" />
            <span class="text-sm">审查报告</span>
          </TabsTrigger>
        </TabsList>

        <div class="flex-1 overflow-auto p-1">
          <!-- 1. 教授：文档 -->
          <TabsContent value="professor" class="m-0">
            <div v-if="professorResource?.content?.sections" class="space-y-6">
              <h2 class="text-2xl font-bold text-white">{{ professorResource.content.title }}</h2>
              <div class="space-y-8">
                <div v-for="section in professorResource.content.sections" :key="section.heading" class="prose prose-invert max-w-none">
                  <h3 class="text-xl text-blue-400 mt-8 mb-4">{{ section.heading }}</h3>

                  <!-- 如果有二级标题（subsections）则渲染层级结构 -->
                  <div v-if="section.subsections" class="space-y-6 ml-4">
                    <div v-for="subsection in section.subsections" :key="subsection.subheading" class="border-l-2 border-white/10 pl-4">
                      <h4 class="text-lg text-blue-300 mt-6 mb-3">{{ subsection.subheading }}</h4>
                      <p class="text-slate-300 leading-relaxed">{{ subsection.body }}</p>
                    </div>
                  </div>

                  <!-- 保持向后兼容，如果没有二级标题则渲染原有格式 -->
                  <p v-else class="text-slate-300 leading-relaxed">{{ section.body }}</p>
                </div>
              </div>
            </div>
            <div v-else class="flex items-center justify-center h-full">
              <div class="text-center">
                <AlertCircle class="h-12 w-12 text-slate-600 mx-auto mb-4" />
                <p class="text-slate-500">暂无文档内容</p>
              </div>
            </div>
          </TabsContent>

          <!-- 2. 架构师：思维导图 -->
          <TabsContent value="mindmap" class="m-0">
            <div v-if="architectResource?.content?.mindmap" class="p-6">
              <h2 class="text-2xl font-bold text-white mb-6">思维导图</h2>
              <div
                ref="mindmapRef"
                class="bg-[#1a1a1a] rounded-xl p-6 border border-white/10 min-h-[600px] w-full"
                style="display: flex; align-items: center; justify-content: center;"
              >
                <p class="text-slate-500">正在加载思维导图...</p>
              </div>
            </div>
            <div v-else class="flex items-center justify-center h-full">
              <div class="text-center">
                <BrainCircuit class="h-12 w-12 text-slate-600 mx-auto mb-4" />
                <p class="text-slate-500">暂无思维导图</p>
              </div>
            </div>
          </TabsContent>

          <!-- 3. 考官：测验题目 -->
          <TabsContent value="quiz" class="m-0">
            <div v-if="examinerResource?.content?.questions" class="space-y-6 p-6">
              <h2 class="text-2xl font-bold text-white mb-6">知识测验</h2>
              <div v-for="(question, index) in examinerResource.content.questions" :key="index" class="bg-[#141414] border border-white/5 p-6 rounded-2xl">
                <div class="flex justify-between items-start mb-4">
                  <Badge class="bg-blue-500/20 text-blue-400 border-none">单选题</Badge>
                  <span class="text-slate-600 text-xs">难度: {{ (index as number) === 0 ? '基础' : (index as number) === 1 ? '进阶' : '高级' }}</span>
                </div>
                <h4 class="text-slate-200 font-medium mb-6">Q{{ (index as number) + 1 }}: {{ question.question }}</h4>
                <div class="space-y-3">
                  <div
                    v-for="(opt, oIdx) in question.options"
                    :key="oIdx"
                    class="p-4 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 hover:border-blue-500/30 cursor-pointer transition-all flex items-center group"
                  >
                    <div class="h-6 w-6 rounded-full border border-white/20 flex items-center justify-center mr-3 group-hover:border-blue-500/50 text-[10px]">
                      {{ String.fromCharCode(65 + (oIdx as number)) }}
                    </div>
                    <span class="text-slate-400 text-sm">{{ opt }}</span>
                    <CheckCircle2 v-if="oIdx === question.answer" class="h-4 w-4 text-green-400 ml-auto flex-shrink-0" />
                  </div>
                </div>
                <div class="mt-4 p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                  <p class="text-xs text-blue-300 flex items-center">
                    <BrainCircuit class="h-3 w-3 inline mr-1" />
                    解析：{{ question.explanation }}
                  </p>
                </div>
              </div>
            </div>
            <div v-else class="flex items-center justify-center h-full">
              <div class="text-center">
                <ClipboardCheck class="h-12 w-12 text-slate-600 mx-auto mb-4" />
                <p class="text-slate-500">暂无测验题目</p>
              </div>
            </div>
          </TabsContent>

          <!-- 4. 导演：视频资源 -->
          <TabsContent value="video" class="m-0">
            <div v-if="directorResource?.content?.scenes" class="p-6">
              <h2 class="text-2xl font-bold text-white mb-6">视频教程</h2>
              <div class="grid gap-6">
                <!-- 直接展示所有视频资源，不按场景分组 -->
                <div v-for="video in getAllVideos()" :key="video.title"
                     class="group">
                  <!-- 视频卡片 -->
                  <div class="bg-white/5 rounded-2xl overflow-hidden border border-white/10 hover:border-blue-500/30 transition-all hover:shadow-xl hover:shadow-blue-500/10">
                    <!-- 视频封面 -->
                    <div class="relative aspect-video bg-black/40 overflow-hidden cursor-pointer"
                         @click="openExternalLink(video.url)">
                      <img :src="video.thumbnail" :alt="video.title"
                           class="w-full h-full object-cover"
                           @error="handleImageError">
                      <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/40"></div>
                      <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button variant="ghost" size="lg"
                                class="h-16 w-16 rounded-full bg-blue-600/90 hover:bg-blue-500 text-white shadow-lg hover:scale-110 transition-all">
                          <PlayCircle class="h-8 w-8" />
                        </Button>
                      </div>
                      <!-- 时长标签 -->
                      <div class="absolute bottom-3 right-3 bg-black/60 backdrop-blur-md px-2 py-1 rounded text-white text-xs">
                        {{ video.duration }}
                      </div>
                      <!-- 平台标签 -->
                      <div class="absolute top-3 left-3 px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">
                        {{ video.platform }}
                      </div>
                    </div>

                    <!-- 视频信息 -->
                    <div class="p-4">
                      <h5 class="font-semibold text-white mb-2 line-clamp-2">{{ video.title }}</h5>
                      <p class="text-slate-400 text-sm line-clamp-2">{{ video.description }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 无视频时的提示 -->
              <div v-if="getAllVideos().length === 0" class="flex items-center justify-center h-full">
                <div class="text-center">
                  <Video class="h-12 w-12 text-slate-600 mx-auto mb-4" />
                  <p class="text-slate-500">暂无视频资源</p>
                </div>
              </div>
            </div>
            <div v-else class="flex items-center justify-center h-full">
              <div class="text-center">
                <Video class="h-12 w-12 text-slate-600 mx-auto mb-4" />
                <p class="text-slate-500">暂无视频资源</p>
              </div>
            </div>
          </TabsContent>

          <!-- 5. 极客：代码实验 -->
          <TabsContent value="code" class="m-0">
            <div v-if="hackerResource?.content" class="bg-[#1e1e1e] rounded-2xl border border-white/5 overflow-hidden h-full flex flex-col">
              <div class="bg-white/5 px-4 py-3 border-b border-white/5 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="flex gap-1.5 mr-2">
                    <div class="h-2.5 w-2.5 rounded-full bg-red-500/20"></div>
                    <div class="h-2.5 w-2.5 rounded-full bg-yellow-500/20"></div>
                    <div class="h-2.5 w-2.5 rounded-full bg-green-500/20"></div>
                  </div>
                  <span class="text-xs text-slate-400 font-mono italic">{{ hackerResource.content.title.toLowerCase().replace(/\s+/g, '_') }}.py</span>
                </div>
                <div class="flex gap-2">
                  <Button variant="ghost" size="sm" class="h-7 text-xs gap-1.5 hover:bg-white/10 text-slate-400" @click="copyToClipboard(hackerResource.content.code)">
                    <Copy class="h-3 w-3" /> Copy
                  </Button>
                  <Button variant="ghost" size="sm" class="h-7 text-xs gap-1.5 hover:bg-white/10 text-slate-400">
                    <Download class="h-3 w-3" /> Download
                  </Button>
                </div>
              </div>
              <pre ref="codePre" class="flex-1 p-6 text-sm leading-relaxed overflow-auto"><code ref="codeElement" class="hljs python">{{ hackerResource.content.code }}</code></pre>
              <div class="border-t border-white/5 px-4 py-3 bg-white/2">
                <p class="text-xs text-slate-400 mb-2">预期输出：</p>
                <pre class="text-xs font-mono text-slate-300 bg-black/30 p-3 rounded overflow-x-auto">{{ hackerResource.content.expected_output }}</pre>
              </div>
              <div class="border-t border-white/5 px-4 py-3">
                <p class="text-xs text-slate-400 mb-2">扩展练习：</p>
                <ul class="text-xs text-slate-300 space-y-1">
                  <li v-for="(exercise, index) in hackerResource.content.exercises" :key="index" class="flex items-start gap-2">
                    <span class="text-blue-400">•</span>
                    <span>{{ exercise }}</span>
                  </li>
                </ul>
              </div>
            </div>
            <div v-else class="flex items-center justify-center h-full">
              <div class="text-center">
                <Code2 class="h-12 w-12 text-slate-600 mx-auto mb-4" />
                <p class="text-slate-500">暂无代码实验</p>
              </div>
            </div>
          </TabsContent>

          <!-- 6. 审查员：质量审查 -->
          <TabsContent value="review" class="m-0">
            <div v-if="reviewerResource?.content" class="p-6">
              <h2 class="text-2xl font-bold text-white mb-6">质量审查报告</h2>

              <!-- 风险评估 -->
              <div class="mb-8">
                <h3 class="text-lg font-semibold text-blue-400 mb-4 flex items-center gap-2">
                  <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                  幻觉风险评估
                </h3>
                <div class="bg-[#1a1a1a] rounded-xl p-5 border border-white/10">
                  <div class="flex items-center justify-between mb-4">
                    <span class="text-white font-medium">风险等级</span>
                    <Badge
                      :class="[
                        reviewerResource.content.hallucination_risk === 'low' ? 'bg-green-500/20 text-green-400' :
                        reviewerResource.content.hallucination_risk === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-red-500/20 text-red-400'
                      ]"
                      class="border-none"
                    >
                      {{ reviewerResource.content.hallucination_risk === 'low' ? '低风险' : reviewerResource.content.hallucination_risk === 'medium' ? '中风险' : '高风险' }}
                    </Badge>
                  </div>
                  <p class="text-sm text-slate-300 leading-relaxed">
                    {{ reviewerResource.content.difficulty_assessment }}
                  </p>
                </div>
              </div>

              <!-- 质量分数 -->
              <div class="mb-8">
                <h3 class="text-lg font-semibold text-blue-400 mb-4 flex items-center gap-2">
                  <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                  质量评分
                </h3>
                <div class="bg-[#1a1a1a] rounded-xl p-5 border border-white/10">
                  <div class="flex items-center justify-between">
                    <span class="text-white font-medium">综合得分</span>
                    <span class="text-3xl font-bold text-blue-400">{{ reviewerResource.content.quality_score }}</span>
                  </div>
                  <div class="mt-2 w-full bg-white/10 rounded-full h-2">
                    <div
                      class="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                      :style="{ width: `${reviewerResource.content.quality_score}%` }"
                    ></div>
                  </div>
                </div>
              </div>

              <!-- 改进建议 -->
              <div v-if="reviewerResource.content.suggestions?.length > 0">
                <h3 class="text-lg font-semibold text-blue-400 mb-4 flex items-center gap-2">
                  <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                  改进建议
                </h3>
                <div class="space-y-3">
                  <div
                    v-for="(suggestion, index) in reviewerResource.content.suggestions"
                    :key="index"
                    class="bg-[#1a1a1a] rounded-lg p-4 border border-white/10 hover:border-blue-500/30 transition-colors"
                  >
                    <div class="flex items-start gap-3">
                      <span class="text-blue-400 mt-1">•</span>
                      <p class="text-sm text-slate-300 leading-relaxed">{{ suggestion }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="flex items-center justify-center h-full">
              <div class="text-center">
                <CheckCircle2 class="h-12 w-12 text-slate-600 mx-auto mb-4" />
                <p class="text-slate-500">暂无审查报告</p>
              </div>
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </div>

    <!-- 生成失败或无内容 -->
    <div v-else class="flex-1 flex flex-col items-center justify-center text-slate-500 bg-white/5 rounded-3xl border border-dashed border-white/10">
      <AlertCircle class="h-10 w-10 opacity-20 mb-4" />
      <h3 class="text-lg font-medium text-slate-400 mb-1">生成完成</h3>
      <p class="text-sm text-slate-600">但没有找到可展示的内容</p>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #222;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #333;
}

/* 确保中文正确显示 */
.prose-invert {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
.text-slate-300,
.text-slate-400,
.text-slate-500,
.text-slate-600 {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* 视频卡片动画 */
.video-card-enter-active {
  transition: all 0.3s ease-out;
}
.video-card-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* 视频封面悬停效果 */
.video-thumbnail {
  position: relative;
  overflow: hidden;
}

.video-thumbnail::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(59, 130, 246, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.video-thumbnail:hover::before {
  opacity: 1;
}

/* 文本截断样式 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>