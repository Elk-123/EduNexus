<!-- src/views/ContentFactory/components/AgentDetailView.vue -->
<script setup lang="ts">
import { ref } from 'vue'
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
    content: `你好！我是你的${props.agent.name}。关于"${props.topic}"，我已经为你准备好了初步的${props.agent.role === 'Hacker' ? '代码实验' : '分析文档'}。你想针对哪个细节进行深入探讨？`
  }
])

const input = ref('')
const isTyping = ref(false)

const sendMessage = async () => {
  if (!input.value.trim() || isTyping.value) return

  messages.value.push({ role: 'user', content: input.value })
  const userQuery = input.value
  input.value = ''
  isTyping.value = true

  try {
    const response = await chatWithAgent(props.agent.id, { message: userQuery })
    messages.value.push({ role: 'assistant', content: response.reply })
  } catch {
    messages.value.push({ role: 'assistant', content: `抱歉，作为${props.agent.role}智能体，我暂时无法回答这个问题。请稍后重试。` })
  } finally {
    isTyping.value = false
  }
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
      </div>
      <Button variant="ghost" size="icon" @click="emit('close')" class="rounded-full hover:bg-white/10">
        <X class="h-5 w-5" />
      </Button>
    </header>

    <main class="flex-1 flex overflow-hidden">
      <!-- 左侧/中间：内容展示区 (继承之前的 ResourceDisplay 逻辑) -->
      <div class="flex-[1.2] border-r border-white/10 p-8 overflow-y-auto bg-black/20 custom-scrollbar">
        <div class="max-w-3xl mx-auto">
          <div class="flex items-center gap-2 mb-6">
            <MessageSquareQuote class="h-5 w-5 text-blue-500" />
            <span class="text-xs font-bold text-slate-500 uppercase">当前专家产出内容</span>
          </div>
          
          <!-- 这里根据角色显示不同的静态预览 -->
          <div v-if="agent.role === 'Hacker'" class="bg-[#1e1e1e] rounded-2xl border border-white/10 p-6 font-mono text-sm">
             <pre class="text-green-400"><code># 正在与 {{ agent.name }} 联调中...
def optimize():
    pass</code></pre>
          </div>
          <div v-else class="prose prose-invert max-w-none">
             <h1 class="text-blue-400">专家深度报告：{{ topic }}</h1>
             <p class="text-slate-400">此处展示的是该 Agent 已经生成的详细资源，方便你边看内容边提问。</p>
             <div class="h-64 bg-white/5 rounded-xl border border-dashed border-white/10 flex items-center justify-center italic text-slate-600">
                [ 完整内容渲染区 ]
             </div>
          </div>
        </div>
      </div>

      <!-- 右侧：对话区 -->
      <div class="flex-1 flex flex-col bg-[#0f0f0f]">
        <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          <div v-for="(msg, idx) in messages" :key="idx" 
            :class="['flex gap-4 animate-in slide-in-from-bottom-2', msg.role === 'user' ? 'flex-row-reverse' : '']">
            <div :class="['h-8 w-8 rounded-full flex items-center justify-center shrink-0', 
              msg.role === 'assistant' ? 'bg-blue-600/20 text-blue-400' : 'bg-slate-700 text-slate-200']">
              <Bot v-if="msg.role === 'assistant'" class="h-4 w-4" />
              <User v-else class="h-4 w-4" />
            </div>
            <div :class="['max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed',
              msg.role === 'assistant' ? 'bg-white/5 text-slate-300' : 'bg-blue-600 text-white shadow-lg shadow-blue-900/20']">
              {{ msg.content }}
            </div>
          </div>
          <div v-if="isTyping" class="flex gap-4">
             <div class="h-8 w-8 rounded-full bg-blue-600/20 flex items-center justify-center">
                <Sparkles class="h-4 w-4 text-blue-400 animate-spin" />
             </div>
             <div class="bg-white/5 p-4 rounded-2xl flex gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-blue-500/50 animate-bounce"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-blue-500/50 animate-bounce [animation-delay:0.2s]"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-blue-500/50 animate-bounce [animation-delay:0.4s]"></span>
             </div>
          </div>
        </div>

        <!-- 对话输入 -->
        <div class="p-6 border-t border-white/10">
          <div class="relative flex items-center">
            <input 
              v-model="input"
              @keyup.enter="sendMessage"
              placeholder="向专家提问或要求修改内容..."
              class="w-full bg-[#1a1a1a] border border-white/10 rounded-xl pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
            />
            <button @click="sendMessage" class="absolute right-2 p-2 text-blue-500 hover:text-blue-400">
              <Send class="h-5 w-5" />
            </button>
          </div>
          <p class="text-[10px] text-center text-slate-600 mt-3">对话内容将实时更新到左侧的生成资源中</p>
        </div>
      </div>
    </main>
  </div>
</template>