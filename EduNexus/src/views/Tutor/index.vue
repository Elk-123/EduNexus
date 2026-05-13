<template>
  <div class="min-h-screen bg-[#0b0b0b]">
    <!-- 背景纹理：网格线 -->
    <div class="absolute inset-0 z-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,#000_70%,transparent_100%)]"></div>

    <!-- 强化背景光晕 -->
    <div class="absolute top-[20%] left-[10%] w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[140px] pointer-events-none"></div>
    <div class="absolute bottom-[20%] right-[10%] w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[140px] pointer-events-none"></div>

    <div class="relative z-10 container mx-auto px-4 py-8 max-w-6xl">
      <!-- 头部 -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-white mb-2">智能辅导</h1>
        <p class="text-zinc-400">AI 导师 24/7 在线，解答您的学习疑问</p>
      </div>

      <!-- 主要内容区 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 聊天区域 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 聊天窗口 -->
          <div class="bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-6 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)] h-[500px] overflow-hidden">
            <div class="h-full flex flex-col">
              <!-- 聊天头部 -->
              <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center">
                  <Bot class="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 class="text-white font-semibold">AI 导师</h3>
                  <p class="text-xs text-green-400">在线</p>
                </div>
              </div>

              <!-- 聊天消息区 -->
              <div class="flex-1 overflow-y-auto space-y-4 pr-2" ref="messageContainer">
                <div class="flex gap-3">
                  <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                    <Bot class="w-5 h-5 text-white" />
                  </div>
                  <div class="bg-[#1a1a1b]/80 backdrop-blur rounded-[1.5rem] p-4 max-w-[80%]">
                    <p class="text-white text-sm">您好！我是您的 AI 学习导师，有什么可以帮助您的吗？</p>
                  </div>
                </div>
              </div>

              <!-- 输入区域 -->
              <div class="mt-4 pt-4 border-t border-[#303134]">
                <div class="flex gap-3">
                  <input
                    v-model="userInput"
                    @keyup.enter="sendMessage"
                    type="text"
                    placeholder="输入您的问题..."
                    class="flex-1 bg-[#1a1a1b]/80 backdrop-blur border border-[#303134] rounded-[1.5rem] px-4 py-3 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                  <button
                    @click="sendMessage"
                    :disabled="!userInput || isLoading"
                    class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-3 rounded-[1.5rem] transition-colors disabled:opacity-50"
                  >
                    <Send v-if="!isLoading" class="w-5 h-5" />
                    <Loader2 v-else class="w-5 h-5 animate-spin" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 快捷问题 -->
          <div class="bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-6 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
            <h3 class="text-white font-semibold mb-4">常见问题</h3>
            <div class="grid grid-cols-2 gap-3">
              <button
                v-for="question in quickQuestions"
                :key="question"
                @click="askQuickQuestion(question)"
                class="text-left bg-[#1a1a1b]/80 backdrop-blur hover:bg-[#2a2a2b] border border-[#303134] rounded-xl px-4 py-3 text-sm text-zinc-300 transition-colors"
              >
                {{ question }}
              </button>
            </div>
          </div>
        </div>

        <!-- 侧边栏 -->
        <div class="space-y-6">
          <!-- 学习统计 -->
          <div class="bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-6 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
            <h3 class="text-white font-semibold mb-4">今日统计</h3>
            <div class="space-y-4">
              <div>
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-zinc-400">会话次数</span>
                  <span class="text-white font-medium">{{ sessionCount }}</span>
                </div>
                <div class="w-full bg-[#1a1a1b]/50 rounded-full h-2">
                  <div class="bg-blue-600 h-2 rounded-full" style="width: 75%"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-zinc-400">问题解决率</span>
                  <span class="text-white font-medium">92%</span>
                </div>
                <div class="w-full bg-[#1a1a1b]/50 rounded-full h-2">
                  <div class="bg-green-600 h-2 rounded-full" style="width: 92%"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-zinc-400">平均响应时间</span>
                  <span class="text-white font-medium">1.2s</span>
                </div>
                <div class="w-full bg-[#1a1a1b]/50 rounded-full h-2">
                  <div class="bg-purple-600 h-2 rounded-full" style="width: 60%"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 学习建议 -->
          <div class="bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-6 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
            <h3 class="text-white font-semibold mb-4">个性化建议</h3>
            <div class="space-y-3">
              <div class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Lightbulb class="w-3 h-3 text-white" />
                </div>
                <p class="text-sm text-zinc-300">您在数学概念方面需要加强，建议多做练习题</p>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <BookOpen class="w-3 h-3 text-white" />
                </div>
                <p class="text-sm text-zinc-300">可以尝试观看相关的视频教程加深理解</p>
              </div>
            </div>
          </div>

          <!-- 历史记录 -->
          <div class="bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-6 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-white font-semibold">历史对话</h3>
              <Button variant="ghost" size="sm" class="text-zinc-400 hover:text-white">
                <List class="w-4 h-4 mr-1" />
                查看
              </Button>
            </div>
            <div class="space-y-2">
              <div class="flex items-center gap-3 p-2 hover:bg-[#1a1a1b]/50 rounded-lg cursor-pointer transition-colors">
                <div class="w-2 h-2 rounded-full bg-green-500"></div>
                <p class="text-sm text-zinc-300 flex-1">微积分基础问题</p>
                <span class="text-xs text-zinc-500">10:30</span>
              </div>
              <div class="flex items-center gap-3 p-2 hover:bg-[#1a1a1b]/50 rounded-lg cursor-pointer transition-colors">
                <div class="w-2 h-2 rounded-full bg-green-500"></div>
                <p class="text-sm text-zinc-300 flex-1">线性代数矩阵运算</p>
                <span class="text-xs text-zinc-500">昨天</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Bot, Send, Loader2, Lightbulb, BookOpen, List } from 'lucide-vue-next'
import Button from '@/components/ui/button/Button.vue'
import { askQuestion } from '@/api/tutor'

const userInput = ref('')
const isLoading = ref(false)
const messageContainer = ref<HTMLElement>()
const sessionCount = ref(5)

const quickQuestions = [
  '如何理解微积分的基本概念？',
  '线性代数有什么实际应用？',
  '如何提高编程能力？',
  '学习方法有哪些推荐？',
  '如何准备考试？',
  '如何进行时间管理？'
]

// 发送消息
const sendMessage = async () => {
  if (!userInput.value || isLoading.value) return

  const message = userInput.value.trim()
  if (!message) return

  // 添加用户消息
  addMessage(message, 'user')

  // 清空输入
  userInput.value = ''
  isLoading.value = true

  // 调用真实 API
  try {
    const response = await askQuestion({ message })
    addMessage(response.reply, 'ai')
    sessionCount.value++
  } catch (error) {
    console.error('发送消息失败:', error)
    addMessage('抱歉，服务暂时不可用，请稍后再试。', 'ai')
  } finally {
    isLoading.value = false
  }
}

// 快捷提问
const askQuickQuestion = (question: string) => {
  userInput.value = question
  sendMessage()
}

// 添加消息到聊天窗口
const addMessage = (content: string, type: 'user' | 'ai') => {
  const messageDiv = document.createElement('div')
  messageDiv.className = 'flex gap-3'

  if (type === 'user') {
    messageDiv.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-zinc-600 flex items-center justify-center flex-shrink-0 ml-auto">
        <User class="w-5 h-5 text-white" />
      </div>
      <div class="bg-blue-600/20 backdrop-blur border border-blue-600/50 rounded-[1.5rem] p-4 max-w-[80%] ml-auto">
        <p class="text-white text-sm">${content}</p>
      </div>
    `
  } else {
    messageDiv.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
        <Bot class="w-5 h-5 text-white" />
      </div>
      <div class="bg-[#1a1a1b]/80 backdrop-blur border border-[#303134] rounded-[1.5rem] p-4 max-w-[80%]">
        <p class="text-white text-sm">${content}</p>
      </div>
    `
  }

  const container = messageContainer.value
  if (container) {
    container.appendChild(messageDiv)
    container.scrollTop = container.scrollHeight
  }
}

onMounted(() => {
  // 模拟加载历史消息
  setTimeout(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  }, 100)
})
</script>