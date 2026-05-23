<!-- src/views/ContentFactory/index.vue -->
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  BrainCircuit, FileText, GitFork, ClipboardCheck, Video, Code2, ShieldCheck
} from 'lucide-vue-next'
import TopicInput from './components/TopicInput.vue'
import AgentTerminal from './components/AgentTerminal.vue'
import ResourceDisplay from './components/ResourceDisplay.vue'
import AgentStatusCard from './components/AgentStatusCard.vue'
import AgentDetailView from './components/AgentDetailView.vue'
import { useFactoryStore } from '@/stores/factoryStore'
import apiClient from '@/api/client'

const route = useRoute()
const factoryStore = useFactoryStore()

// 从URL参数获取默认标签
const defaultTab = computed(() => {
  const tab = route.query.tab as string
  const tabMapping: Record<string, string> = {
    'professor': 'professor',
    'architect': 'mindmap',
    'examiner': 'quiz',
    'director': 'video',
    'hacker': 'code'
  }
  return tabMapping[tab] || 'professor'
})

// 智能体定义
const agentDefs = [
  { id: 'manager', name: '主控中枢', role: 'Manager', icon: BrainCircuit, color: 'text-purple-400' },
  { id: 'professor', name: '教授智能体', role: 'Professor', icon: FileText, color: 'text-blue-400' },
  { id: 'architect', name: '架构师智能体', role: 'Architect', icon: GitFork, color: 'text-orange-400' },
  { id: 'examiner', name: '考官智能体', role: 'Examiner', icon: ClipboardCheck, color: 'text-pink-400' },
  { id: 'director', name: '导演智能体', role: 'Director', icon: Video, color: 'text-cyan-400' },
  { id: 'hacker', name: '极客智能体', role: 'Hacker', icon: Code2, color: 'text-green-400' },
  { id: 'reviewer', name: '质量审查', role: 'Reviewer', icon: ShieldCheck, color: 'text-red-400' },
]

const selectedAgent = ref<any>(null)

// 从 store 状态推导智能体状态列表
const agents = computed(() =>
  agentDefs.map((def) => {
    const statusFromStore = factoryStore.agentsStatus[def.id]
    const status = (statusFromStore || 'idle') as 'idle' | 'running' | 'success' | 'error'
    return {
      ...def,
      status,
    }
  })
)

const isGenerating = computed(() => factoryStore.isGenerating)
const currentTopic = computed(() => factoryStore.currentTopic)
const logs = computed(() => factoryStore.logs)

// 启动生成流水线
const runWorkflow = async (topic: string) => {
  selectedAgent.value = null
  console.log('Starting generation for topic:', topic)
  try {
    await factoryStore.startGeneration(topic)
    console.log('Generation completed. Resources:', factoryStore.resources)
    console.log('Current topic:', factoryStore.currentTopic)
  } catch (error) {
    console.error('Generation failed:', error)
  }
}

// 页面加载时尝试加载最新的任务数据
onMounted(async () => {
  try {
    // 获取最新任务
    console.log('Fetching latest task...')
    const response = await apiClient.get('/factory/latest')
    console.log('Latest task response:', response)
    if (response.data) {
      const taskId = response.data.id
      await factoryStore.loadTaskData(taskId)
      console.log('Loaded latest task:', taskId, response.data)
    }
  } catch (error) {
    console.log('No existing task found, waiting for user to generate new one')
  }
})

// 调试：监听store状态
watch(() => factoryStore.resources, (newResources) => {
  console.log('ContentFactory: Store resources updated', {
    count: newResources?.length,
    types: newResources?.map(r => r.agent_type),
    isGenerating: factoryStore.isGenerating
  })
}, { deep: true })

// 点击智能体卡片进入详情
const handleAgentClick = (agent: any) => {
  if (agent.status === 'success') {
    selectedAgent.value = agent
  }
}
</script>

<template>
  <div class="flex flex-col h-full bg-[#0b0b0b] text-slate-200 overflow-hidden relative">
    <!-- 顶部输入 -->
    <header class="border-b border-white/5 py-10 px-6 bg-gradient-to-b from-blue-900/5 to-transparent">
      <TopicInput :isGenerating="isGenerating" @start="runWorkflow" />
    </header>

    <main class="flex-1 flex overflow-hidden p-6 gap-6">
      <!-- 左侧：工作台控制面板 -->
      <aside class="w-80 flex flex-col gap-6">
        <div class="bg-[#141414] border border-white/5 rounded-3xl p-5 flex-1 flex flex-col shadow-2xl relative overflow-hidden">
          <h3 class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-5 flex items-center gap-2 px-1">
            <span class="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse"></span>
            专家集群状态
          </h3>
          
          <!-- 智能体列表 -->
          <div class="space-y-3 overflow-y-auto pr-1 custom-scrollbar">
            <AgentStatusCard 
              v-for="agent in agents" 
              :key="agent.id" 
              :agent="agent" 
              @click="handleAgentClick(agent)"
              :class="[
                agent.status === 'success' ? 'cursor-pointer hover:translate-x-1 active:scale-95 transition-all' : ''
              ]"
            />
          </div>

          <!-- 底部提示 -->
          <div v-if="!isGenerating && currentTopic" class="mt-4 p-3 bg-blue-500/5 rounded-xl border border-blue-500/10">
            <p class="text-[10px] text-blue-400/80 leading-relaxed">
              💡 点击带有 <span class="font-bold">READY/DONE</span> 标记的专家，可进入深度研讨室进行 1-on-1 对话。
            </p>
          </div>
        </div>

        <!-- 终端日志 -->
        <div class="h-60">
           <AgentTerminal :logs="logs" />
        </div>
      </aside>

      <!-- 右侧：主展示区 -->
      <section class="flex-1 min-w-0">
        <ResourceDisplay
          :resources="factoryStore.resources"
          :isGenerating="factoryStore.isGenerating"
          :topic="factoryStore.currentTopic"
          :defaultTab="defaultTab"
        />
      </section>
    </main>

    <!-- 深度对话研讨室 (Overlay) -->
    <Transition
      enter-active-class="transition duration-500 ease-out"
      enter-from-class="opacity-0 translate-y-10 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition duration-300 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-10 scale-95"
    >
      <AgentDetailView
        v-if="selectedAgent"
        :agent="selectedAgent"
        :topic="currentTopic"
        :resources="factoryStore.resources"
        @close="selectedAgent = null"
      />
    </Transition>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #222; border-radius: 10px; }
</style>