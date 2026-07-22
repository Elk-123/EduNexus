import { defineStore } from 'pinia'
import { ref } from 'vue'
// [已注释] v1.0 API — 保留兼容
// import { generateContent, getTaskStatus, getTaskResources } from '@/api/factory'
import { generateV2 } from '@/api/factory'
import type { V2PipelineResult } from '@/api/factory'
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
  type: 'info' | 'success' | 'warn' | 'tool'
  /** tool call 详情（type === 'tool' 时） */
  tool?: {
    name: string
    input?: string
    output?: string
    duration_ms?: number
    status?: 'running' | 'success' | 'error'
  }
}

/** v1.0 agent_type → resource_type 映射 */
const AGENT_RESOURCE_MAP: Record<string, string> = {
  manager: 'task_plan',
  professor: 'document',
  architect: 'mindmap',
  examiner: 'quiz',
  director: 'video_script',
  hacker: 'code_lab',
  reviewer: 'review_report',
}

export const useFactoryStore = defineStore('factory', () => {
  const isGenerating = ref(false)
  const currentTaskId = ref<string | null>(null)
  const currentTopic = ref('')
  const logs = ref<LogEntry[]>([])
  const resources = ref<GeneratedResource[]>([])
  const agentsStatus = ref<Record<string, string>>({})
  const error = ref<string | null>(null)
  /** v2.0 累积上下文（所有 Agent 的输出） */
  const accumulatedContext = ref<Record<string, any>>({})
  /** v2.0 Markdown 报告 */
  const markdownReport = ref<string>('')
  let logCounter = 0
  let ws: EduNexusWebSocket | null = null
  let pollTimer: ReturnType<typeof setInterval> | null = null

  function addLog(agent: string, message: string, type: 'info' | 'success' | 'warn' | 'tool' = 'info') {
    logs.value.push({ id: ++logCounter, agent, message, type })
  }

  // ═══════════════════════════════════════════════════════════
  //  [已注释] v1.0 startGeneration — 保留兼容
  // ═══════════════════════════════════════════════════════════
  // async function startGeneration(topic: string) {
  //   ... (旧代码保留，使用旧的 /factory/generate 端点)
  // }

  // ═══════════════════════════════════════════════════════════
  //  v2.0 startV2Generation — 使用新的 Agent 引擎
  // ═══════════════════════════════════════════════════════════
  async function startV2Generation(topic: string) {
    isGenerating.value = true
    currentTopic.value = topic
    logs.value = []
    resources.value = []
    agentsStatus.value = {}
    accumulatedContext.value = {}
    markdownReport.value = ''
    error.value = null
    logCounter = 0

    try {
      const result = await generateV2(topic)
      currentTaskId.value = result.task_id
      addLog('System', `🚀 v2.0 Agent 管道启动: ${topic}`, 'info')
      console.log('[V2] Task created:', result.task_id)

      // 连接 WebSocket 接收实时事件
      ws = new EduNexusWebSocket()
      ws.on('agent_status', (data: any) => {
        const agentId = (data.agent as string).toLowerCase()
        agentsStatus.value = { ...agentsStatus.value, [agentId]: data.status }
        if (data.status === 'running') {
          addLog(data.agent, `开始执行...`, 'info')
        } else if (data.status === 'success') {
          addLog(data.agent, `完成 ✓`, 'success')
        } else if (data.status === 'error') {
          addLog(data.agent, `执行失败`, 'warn')
        }
      })
      ws.on('agent_log', (data: any) => {
        addLog(data.agent, data.message, data.type || 'info')
      })
      ws.on('tool_call', (data: any) => {
        // ★ v2.3: 工具调用事件 — Claude Code 风格展示，完整输出
        const toolName = data.tool || 'unknown'
        const agent = data.agent || 'System'
        if (data.status === 'running') {
          const input = (data.input || '').slice(0, 100)
          const dots = (data.input || '').length > 100 ? '...' : ''
          addLog(agent, `🔧 调用工具: ${toolName}("${input}${dots}")`, 'tool')
        } else if (data.status === 'success') {
          const ms = data.duration_ms ? ` (${data.duration_ms}ms)` : ''
          // 完整输出，按换行拆分多条日志
          const fullOutput = data.output || ''
          const lines = fullOutput.split('\n')
          lines.forEach((line: string, i: number) => {
            addLog(agent, i === 0 ? `  → ${line}${ms}` : `    ${line}`, 'info')
          })
        } else if (data.status === 'error') {
          addLog(agent, `  ⚠ 工具调用失败: ${data.error || '未知错误'}`, 'warn')
        }
      })
      ws.on('task_complete', () => {
        isGenerating.value = false
        stopPolling()
        addLog('System', '所有 Agent 执行完毕', 'success')
      })
      ws.on('v2_result', (data: V2PipelineResult) => {
        console.log('[V2] Pipeline result received:', data)
        accumulatedContext.value = data.accumulated_context || {}
        markdownReport.value = data.markdown_report || ''

        // 将 v2 Agent 输出转换为 GeneratedResource 格式
        const converted: GeneratedResource[] = []
        const ctx = data.accumulated_context || {}
        for (const [agentId, content] of Object.entries(ctx)) {
          converted.push({
            id: `${agentId}-${Date.now()}` as any,
            task_id: (currentTaskId.value || '') as any,
            agent_type: agentId,
            resource_type: (AGENT_RESOURCE_MAP[agentId] || 'document') as any,
            content: content as Record<string, any>,
            status: 'completed',
          })
        }
        resources.value = converted
        console.log('[V2] Converted resources:', converted.length, 'agents')
      })
      ws.on('error', (data: any) => {
        error.value = data.message
        isGenerating.value = false
        addLog('System', `错误: ${data.message}`, 'warn')
      })
      ws.connect(result.task_id)

      // 轮询兜底
      startV2Polling()
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'v2.0 生成任务失败'
      isGenerating.value = false
      addLog('System', `管道启动失败: ${error.value}`, 'warn')
    }
  }

  function startV2Polling() {
    stopPolling()
    pollTimer = setInterval(async () => {
      if (!currentTaskId.value) return
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1'}/factory/status/${currentTaskId.value}`,
          { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
        )
        if (!response.ok) return
        const status = await response.json()
        if (status.status === 'completed' || status.status === 'failed') {
          isGenerating.value = false
          stopPolling()
        }
      } catch { /* ignore */ }
    }, 3000)
  }

  // ═══════════════════════════════════════════════════════════
  //  [已注释] v1.0 loadTaskData — 保留兼容
  // ═══════════════════════════════════════════════════════════
  // async function loadTaskData(taskId: string) { ... }

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
    accumulatedContext.value = {}
    markdownReport.value = ''
    error.value = null
    ws?.disconnect()
    ws = null
    stopPolling()
  }

  return {
    isGenerating, currentTaskId, currentTopic, logs, resources, agentsStatus, error,
    accumulatedContext, markdownReport,
    addLog, reset,
    // v2.0 入口
    startV2Generation,
  }
})
