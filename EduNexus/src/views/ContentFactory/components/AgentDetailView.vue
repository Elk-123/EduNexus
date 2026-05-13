<!-- src/views/ContentFactory/components/AgentDetailView.vue -->
<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { X, Send, Bot, User, Sparkles, MessageSquareQuote } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { chatWithAgent } from '@/api/factory'

const props = defineProps<{
  agent: any
  topic: string
}>()

const emit = defineEmits(['close'])

const messages = ref([
  {
    role: 'assistant',
    content: `你好！我是你的${props.agent.name}专家。关于"${props.topic}"，我已经为你生成了初步内容。现在我们可以一起深入探讨、优化和改进。你想从哪个方面开始？`,
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
    'Professor': [
      '解释这个概念的核心思想',
      '提供更多的例子说明',
      '总结关键要点',
      '与其他概念对比分析'
    ],
    'Architect': [
      '优化思维导图结构',
      '添加更多分支内容',
      '调整层级关系',
      '提供可视化建议'
    ],
    'Examiner': [
      '生成更多练习题',
      '调整题目难度',
      '添加解析说明',
      '创建模拟测试'
    ],
    'Director': [
      '增加更多场景',
      '优化脚本文本',
      '调整时长分配',
      '提供视觉建议'
    ],
    'Hacker': [
      '优化代码结构',
      '添加注释说明',
      '创建测试用例',
      '改进性能'
    ],
    'Reviewer': [
      '提高内容质量',
      '减少错误风险',
      '增强实用性',
      '完善细节'
    ]
  }

  suggestions.value = suggestionMap[props.agent.role] || [
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
    // 模拟打字效果
    agentResponse.value = ''
    const response = await chatWithAgent(props.agent.id, { message: userQuery })

    // 逐字显示 AI 回复
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

// 快速提问
const askSuggestion = (question: string) => {
  input.value = question
  sendMessage()
}

// 格式化代码块
const formatCode = (text: string) => {
  if (props.agent.role === 'Hacker') {
    return text.replace(/```/g, '').replace(/\n/g, '<br>')
  }
  return text
}

onMounted(() => {
  generateSuggestions()
  scrollToBottom()
})
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
            <MessageSquareQuote class="h-5 w-5 text-blue-500" />
            <span class="text-xs font-bold text-slate-500 uppercase">{{ agent.role }} 专家产出</span>
          </div>

          <!-- 根据角色显示不同格式的预览 -->
          <div v-if="agent.role === 'Hacker'" class="bg-[#1e1e1e] rounded-2xl border border-white/10 p-6 font-mono text-sm">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-green-400 font-semibold">{{ topic }} - 代码实现</h3>
              <Button variant="ghost" size="sm" class="text-xs text-green-400 hover:text-green-300">
                <Code2 class="w-3 h-3 mr-1" />
                运行
              </Button>
            </div>
            <pre class="text-green-400"><code># 正在与 {{ agent.name }} 协作开发...
# 已根据对话实时更新代码
def generate_solution():
    """自动生成的解决方案"""
    return optimized_code</code></pre>
          </div>
          <div v-else class="bg-[#1e1e1e] rounded-2xl border border-white/10 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-blue-400 font-semibold">{{ topic }} - {{ agent.role }}分析</h3>
              <Button variant="ghost" size="sm" class="text-xs text-blue-400 hover:text-blue-300">
                <FileText class="w-3 h-3 mr-1" />
                导出
              </Button>
            </div>
            <div class="prose prose-invert max-w-none text-sm">
              <p class="text-slate-400">AI 专家正在根据您的对话实时优化内容...</p>
              <div class="h-64 bg-white/5 rounded-xl border border-dashed border-white/10 flex items-center justify-center italic text-slate-600">
                <Brain class="w-8 h-8 mr-2 text-blue-500" />
                内容将随着对话动态生成
              </div>
            </div>
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
              <div v-if="msg.role === 'assistant' && agent.role === 'Hacker'" class="font-mono text-green-400">
                {{ formatCode(msg.content) }}
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
            <Button variant="ghost" size="sm" class="text-xs text-slate-400 hover:text-white">
              <Lightbulb class="w-3 h-3 mr-1" />
              获取建议
            </Button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>