<!-- src/views/ContentFactory/index.vue -->
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { 
  BrainCircuit, 
  FileText, 
  GitFork, 
  ClipboardCheck, 
  Video, 
  Code2, 
  ShieldCheck,
  Send,
  Loader2
} from 'lucide-vue-next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'

// 模拟智能体状态
const agents = reactive([
  { id: 'manager', name: '主控中枢', role: 'Manager', status: 'idle', icon: BrainCircuit },
  { id: 'professor', name: '教授智能体', role: 'Professor', status: 'idle', icon: FileText },
  { id: 'architect', name: '架构师智能体', role: 'Architect', status: 'idle', icon: GitFork },
  { id: 'examiner', name: '考官智能体', role: 'Examiner', status: 'idle', icon: ClipboardCheck },
  { id: 'director', name: '导演智能体', role: 'Director', status: 'idle', icon: Video },
  { id: 'hacker', name: '极客智能体', role: 'Hacker', status: 'idle', icon: Code2 },
  { id: 'reviewer', name: '质量审查', role: 'Reviewer', status: 'idle', icon: ShieldCheck },
])

const topic = ref('')
const isGenerating = ref(false)
const progress = ref(0)

// 模拟生成流程
const startGeneration = async () => {
  if (!topic.value) return
  isGenerating.value = true
  
  // 1. Manager 启动
  agents[0].status = 'running'
  
  // 模拟各个 Agent 依次启动的视觉效果
  for (let i = 1; i < agents.length - 1; i++) {
    await new Promise(resolve => setTimeout(resolve, 800))
    agents[i].status = 'running'
    progress.value = (i / (agents.length - 1)) * 100
  }

  // 模拟审查
  await new Promise(resolve => setTimeout(resolve, 1500))
  agents[agents.length - 1].status = 'running'
  
  // 全部完成
  agents.forEach(a => a.status = 'success')
  isGenerating.value = false
}
</script>

<template>
  <div class="flex flex-col h-full bg-[#0b0b0b] text-slate-200">
    <!-- 顶部输入区: Google AI Studio Style -->
    <header class="border-b border-white/10 p-6">
      <div class="max-w-5xl mx-auto">
        <h1 class="text-2xl font-semibold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          内容制造车间 (Content Factory)
        </h1>
        <div class="relative flex items-center">
          <input 
            v-model="topic"
            placeholder="输入教学主题 (例如: 梯度下降算法的几何解释...)"
            class="w-full bg-[#1e1e1e] border border-white/10 rounded-xl px-5 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all pr-32"
          />
          <Button 
            @click="startGeneration" 
            :disabled="isGenerating"
            class="absolute right-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-6"
          >
            <Loader2 v-if="isGenerating" class="mr-2 h-4 w-4 animate-spin" />
            <Send v-else class="mr-2 h-4 w-4" />
            协作生成
          </Button>
        </div>
      </div>
    </header>

    <main class="flex-1 flex overflow-hidden">
      <!-- 左侧：智能体流水线状态 -->
      <aside class="w-80 border-r border-white/10 p-4 overflow-y-auto bg-[#0f0f0f]">
        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">智能体集群状态</h3>
        <div class="space-y-3">
          <div 
            v-for="agent in agents" 
            :key="agent.id"
            :class="[
              'p-3 rounded-lg border transition-all duration-500',
              agent.status === 'running' ? 'bg-blue-500/10 border-blue-500/50 animate-pulse' : 
              agent.status === 'success' ? 'bg-green-500/5 border-green-500/30' : 'bg-[#1a1a1a] border-white/5'
            ]"
          >
            <div class="flex items-center gap-3">
              <component :is="agent.icon" :class="['h-5 w-5', agent.status === 'running' ? 'text-blue-400' : 'text-slate-400']" />
              <div class="flex-1">
                <div class="text-sm font-medium">{{ agent.name }}</div>
                <div class="text-[10px] text-slate-500">{{ agent.role }}</div>
              </div>
              <Badge v-if="agent.status === 'success'" class="bg-green-500/20 text-green-400 border-none h-5 text-[10px]">PASS</Badge>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧：多模态内容预览区 -->
      <section class="flex-1 overflow-y-auto p-6">
        <Tabs defaultValue="doc" class="w-full">
          <TabsList class="bg-[#1e1e1e] border-white/5 mb-6">
            <TabsTrigger value="doc">课程文档</TabsTrigger>
            <TabsTrigger value="mindmap">知识图谱</TabsTrigger>
            <TabsTrigger value="quiz">评测题目</TabsTrigger>
            <TabsTrigger value="video">视频脚本</TabsTrigger>
            <TabsTrigger value="code">实操代码</TabsTrigger>
          </TabsList>

          <!-- 模拟内容展示：此处后续对接具体的渲染组件 -->
          <TabsContent value="doc" class="space-y-4">
             <Card class="bg-[#1a1a1a] border-white/10 text-slate-300">
               <CardContent class="p-6 prose prose-invert max-w-none">
                  <div v-if="!isGenerating && progress === 0" class="text-slate-500 italic">等待主题输入...</div>
                  <div v-else>
                    <h2 class="text-blue-400"># 梯度下降算法 (Gradient Descent)</h2>
                    <p>梯度下降是机器学习中最重要的优化算法之一...</p>
                    <!-- 此处可集成 Markdown 渲染 -->
                  </div>
               </CardContent>
             </Card>
          </TabsContent>
          
          <TabsContent value="mindmap">
             <div class="h-[500px] w-full bg-[#1a1a1a] rounded-xl border border-white/10 flex items-center justify-center">
                <div class="text-slate-500 text-center">
                  <GitFork class="h-12 w-12 mx-auto mb-2 opacity-20" />
                  <p>Mermaid 流程图加载中...</p>
                </div>
             </div>
          </TabsContent>

          <TabsContent value="code">
             <div class="rounded-xl overflow-hidden border border-white/10">
                <div class="bg-[#2d2d2d] px-4 py-2 text-xs text-slate-400 flex justify-between">
                  <span>gradient_descent.py</span>
                  <span>Python</span>
                </div>
                <pre class="p-4 bg-[#1e1e1e] text-green-400 font-mono text-sm"><code>def gradient_descent(x, y, lr=0.01):
    # 极客智能体生成的代码模板
    pass</code></pre>
             </div>
          </TabsContent>
        </Tabs>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* 隐藏滚动条但保持功能 */
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 10px;
}
</style>