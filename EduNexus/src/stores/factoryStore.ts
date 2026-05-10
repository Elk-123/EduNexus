import { defineStore } from 'pinia'
import { ref } from 'vue'
import { generateContent, getTaskStatus, getTaskResources } from '@/api/factory'
import { EduNexusWebSocket } from '@/api/websocket'
import type { GeneratedResource } from '@/types/factory'

export interface AgentState {
  id: string
  name: string
  role: string
  status: 'idle' | 'running' | 'success' | 'error'
  icon: any
  color: string
}

export interface LogEntry {
  id: number
  agent: string
  message: string
  type: 'info' | 'success' | 'warn'
}

export const useFactoryStore = defineStore('factory', () => {
  const isGenerating = ref(false)
  const currentTaskId = ref<string | null>(null)
  const currentTopic = ref('')
  const logs = ref<LogEntry[]>([])
  const resources = ref<GeneratedResource[]>([])
  const agentsStatus = ref<Record<string, string>>({})
  const error = ref<string | null>(null)
  let logCounter = 0
  let ws: EduNexusWebSocket | null = null
  let pollTimer: ReturnType<typeof setInterval> | null = null

  function addLog(agent: string, message: string, type: 'info' | 'success' | 'warn' = 'info') {
    logs.value.push({ id: ++logCounter, agent, message, type })
  }

  async function startGeneration(topic: string) {
    isGenerating.value = true
    currentTopic.value = topic
    logs.value = []
    resources.value = []
    agentsStatus.value = {}
    error.value = null
    logCounter = 0

    try {
      const result = await generateContent({ topic })
      currentTaskId.value = result.task_id

      // 连接 WebSocket 接收实时事件
      ws = new EduNexusWebSocket()
      ws.on('agent_status', (data) => {
        const agentId = (data.agent as string).toLowerCase()
        agentsStatus.value = { ...agentsStatus.value, [agentId]: data.status }
        if (data.status === 'running') {
          addLog(data.agent, `开始执行任务...`, 'info')
        } else if (data.status === 'success') {
          addLog(data.agent, `任务完成`, 'success')
        }
      })
      ws.on('agent_log', (data) => {
        addLog(data.agent, data.message, data.type || 'info')
      })
      ws.on('task_complete', async () => {
        isGenerating.value = false
        stopPolling()
        if (currentTaskId.value) {
          try {
            resources.value = await getTaskResources(currentTaskId.value)
          } catch { /* ignore */ }
        }
      })
      ws.on('error', (data) => {
        error.value = data.message
        isGenerating.value = false
      })
      ws.connect(result.task_id)

      // 启动轮询作为 WebSocket 断线时的兜底
      startPolling()
    } catch (e: any) {
      error.value = e?.response?.data?.detail || '生成任务失败'
      isGenerating.value = false
    }
  }

  function startPolling() {
    stopPolling()
    pollTimer = setInterval(async () => {
      if (!currentTaskId.value) return
      try {
        const status = await getTaskStatus(currentTaskId.value)
        if (status.status === 'completed' || status.status === 'failed') {
          isGenerating.value = false
          stopPolling()
          if (status.status === 'completed') {
            resources.value = await getTaskResources(currentTaskId.value)
          }
        }
      } catch { /* ignore poll errors */ }
    }, 3000)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  function reset() {
    isGenerating.value = false
    currentTaskId.value = null
    currentTopic.value = ''
    logs.value = []
    resources.value = []
    error.value = null
    ws?.disconnect()
    ws = null
    stopPolling()
  }

  return { isGenerating, currentTaskId, currentTopic, logs, resources, agentsStatus, error,
           addLog, startGeneration, reset }
})
