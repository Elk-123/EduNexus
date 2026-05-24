# Agent模块使用示例

以下是如何在EduNexus系统中使用新创建的Agent模块的示例代码。

## 1. 在ContentFactory模块中的集成示例

```typescript
// src/views/ContentFactory/index.vue (更新后的版本)
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
import { AgentCoordinator, LangChainUtils } from '@/agents'

const route = useRoute()
const factoryStore = useFactoryStore()

// 初始化LangChain模型
LangChainUtils.initializeModel(import.meta.env.VITE_GEMINI_API_KEY, 'gemini-2.5-flash')

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

// 创建Agent协调器
const coordinator = new AgentCoordinator()

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
    // 启动Agent流水线
    const results = await coordinator.executePipeline(topic)
    console.log('Agent pipeline completed:', results)
    
    // 处理结果并更新store
    const resources = processAgentResults(results)
    factoryStore.resources = resources
    factoryStore.currentTopic = topic
    
    // 更新智能体状态
    results.forEach(result => {
      if (result.status === 'success' && result.result) {
        factoryStore.agentsStatus[result.agentId] = 'success'
      } else {
        factoryStore.agentsStatus[result.agentId] = 'error'
      }
    })
    
    console.log('Generation completed. Resources:', factoryStore.resources)
  } catch (error) {
    console.error('Generation failed:', error)
  }
}

// 处理Agent执行结果
const processAgentResults = (results: any[]) => {
  // 将Agent结果转换为当前系统所需的资源格式
  return results
    .filter(result => result.status === 'success' && result.result)
    .map(result => ({
      id: `${result.agentId}-${Date.now()}`,
      task_id: '',
      agent_type: result.agentId,
      resource_type: result.result.type,
      content: result.result.content,
      status: 'completed'
    }))
}

// 页面加载时尝试加载最新的任务数据
onMounted(async () => {
  try {
    // 获取最新任务
    console.log('Fetching latest task...')
    // 此处可以调用现有的API获取最新任务数据
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
```

## 2. Agent状态管理示例

```typescript
// src/utils/agent-status-manager.ts
import { AgentStatus } from '@/agents/types'

export class AgentStatusManager {
  private statuses: Map<string, AgentStatus> = new Map()

  updateStatus(agentId: string, status: AgentStatus['status']): void {
    const existingStatus = this.statuses.get(agentId)
    if (existingStatus) {
      existingStatus.status = status
      existingStatus.lastUpdated = new Date()
    } else {
      this.statuses.set(agentId, {
        agentId,
        status,
        lastUpdated: new Date(),
        successCount: 0,
        failureCount: 0
      })
    }
  }

  getStatus(agentId: string): AgentStatus | undefined {
    return this.statuses.get(agentId)
  }

  getAllStatuses(): AgentStatus[] {
    return Array.from(this.statuses.values())
  }
}
```

## 3. 集成后的优势

通过集成Agent模块，我们获得了以下增强功能：

1. **更好的结构化输出**：每个Agent专注于特定领域，输出更加专业化
2. **更强的协作能力**：Agent之间可以更好地协作和共享信息
3. **更高的可扩展性**：新增Agent类型非常容易，只需继承BaseAgent
4. **更灵活的任务编排**：通过AgentCoordinator可以灵活地改变执行顺序和流程
5. **更完善的错误处理**：每个Agent都有独立的错误处理和恢复机制
6. **更好的性能控制**：支持超时控制和中断机制

## 4. 配置和部署

为了使Agent模块正常工作，需要在`.env`文件中添加必要的配置：

```bash
# .env 文件
VITE_GEMINI_API_KEY=your_google_gemini_api_key_here
```

然后在项目中导入和初始化：

```typescript
// src/main.ts
import { LangChainUtils } from '@/agents'

// 初始化LangChain
LangChainUtils.initializeModel(import.meta.env.VITE_GEMINI_API_KEY)
```

这个Agent模块完全独立于现有代码，可以在不影响当前功能的情况下进行集成和测试。