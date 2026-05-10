import type { AgentLogEntry } from '@/types/factory'

type EventHandler = (data: any) => void

export class EduNexusWebSocket {
  private ws: WebSocket | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private handlers = new Map<string, Set<EventHandler>>()
  private url = ''

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  connect(taskId: string) {
    const token = localStorage.getItem('token')
    const baseUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/api/v1'
    this.url = `${baseUrl}/factory/stream/${taskId}?token=${token}`

    try {
      this.ws = new WebSocket(this.url)

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as AgentLogEntry
          const handlers = this.handlers.get(data.type)
          if (handlers) {
            handlers.forEach((fn) => fn(data))
          }
        } catch {
          // Ignore parse errors
        }
      }

      this.ws.onclose = () => {
        this.reconnectTimer = setTimeout(() => this.connect(taskId), 3000)
      }

      this.ws.onerror = () => {
        this.ws?.close()
      }
    } catch {
      // Connection failed, will retry
      this.reconnectTimer = setTimeout(() => this.connect(taskId), 3000)
    }
  }

  on(eventType: string, handler: EventHandler) {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set())
    }
    this.handlers.get(eventType)!.add(handler)
  }

  off(eventType: string, handler: EventHandler) {
    this.handlers.get(eventType)?.delete(handler)
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    this.ws?.close()
    this.ws = null
    this.handlers.clear()
  }
}
