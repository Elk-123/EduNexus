<!-- src/views/ContentFactory/components/ResourceDisplay.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { 
  FileText, 
  GitFork, 
  ClipboardCheck, 
  Video, 
  Code2, 
  CheckCircle2,
  Download,
  Copy,
  ExternalLink,
  PlayCircle,
  BrainCircuit
} from 'lucide-vue-next'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

interface Props {
  isGenerating: boolean
  topic: string
}

const props = defineProps<Props>()

const mockQuizzes = [
  {
    question: "梯度下降中，学习率 (Learning Rate) 过大可能会导致什么结果？",
    options: ["收敛速度变慢", "模型无法收敛，在极值点附近震荡", "模型陷入局部最优解", "梯度消失"],
    answer: 1,
    type: "单选题"
  },
  {
    question: "在随机梯度下降 (SGD) 中，每个批次使用多少个样本进行更新？",
    options: ["全部样本", "1个样本", "固定比例的样本", "0个样本"],
    answer: 1,
    type: "单选题"
  }
]
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- 未开始状态 -->
    <div v-if="!topic && !isGenerating" class="flex-1 flex flex-col items-center justify-center text-slate-500 bg-white/5 rounded-3xl border border-dashed border-white/10">
      <div class="p-4 rounded-full bg-white/5 mb-4">
        <FileText class="h-10 w-10 opacity-20" />
      </div>
      <p class="text-sm">在上方输入主题并点击“协作生成”</p>
      <p class="text-[11px] mt-2 opacity-50">AI 专家团将为您构建多模态学习包</p>
    </div>

    <!-- 生成中状态 -->
    <div v-else-if="isGenerating" class="flex-1 flex flex-col items-center justify-center bg-white/5 rounded-3xl border border-white/5">
      <div class="relative w-24 h-24 mb-6">
        <div class="absolute inset-0 border-4 border-blue-500/20 rounded-full"></div>
        <div class="absolute inset-0 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <div class="absolute inset-0 flex items-center justify-center">
          <BrainCircuit class="h-8 w-8 text-blue-400 animate-pulse" />
        </div>
      </div>
      <h3 class="text-xl font-medium text-white mb-2">资源构建中...</h3>
      <p class="text-slate-400 text-sm italic">“{{ topic }}”的知识体系正在由专家团协同建模</p>
    </div>

    <!-- 内容展示区 -->
    <Tabs v-else defaultValue="doc" class="flex-1 flex flex-col">
      <div class="flex items-center justify-between mb-4">
        <TabsList class="bg-[#1a1a1a] border border-white/10 p-1">
          <TabsTrigger value="doc" class="gap-2"><FileText class="h-4 w-4" /> 文档</TabsTrigger>
          <TabsTrigger value="mindmap" class="gap-2"><GitFork class="h-4 w-4" /> 脑图</TabsTrigger>
          <TabsTrigger value="quiz" class="gap-2"><ClipboardCheck class="h-4 w-4" /> 测验</TabsTrigger>
          <TabsTrigger value="video" class="gap-2"><Video class="h-4 w-4" /> 脚本</TabsTrigger>
          <TabsTrigger value="code" class="gap-2"><Code2 class="h-4 w-4" /> 实验</TabsTrigger>
        </TabsList>

        <div class="flex items-center gap-2">
          <Badge variant="outline" class="bg-green-500/10 text-green-400 border-green-500/20 gap-1.5 py-1">
            <CheckCircle2 class="h-3.5 w-3.5" /> 质量已由 Reviewer 审核
          </Badge>
          <Button variant="ghost" size="icon" class="text-slate-400 hover:text-white">
            <Download class="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        <!-- 1. 教授：课程文档 -->
        <TabsContent value="doc" class="m-0">
          <Card class="bg-[#141414] border-white/5 shadow-2xl">
            <CardContent class="p-8 prose prose-invert prose-blue max-w-none">
              <h1 class="text-3xl font-bold mb-6 underline decoration-blue-500/30">深度理解：{{ topic }}</h1>
              <div class="bg-blue-500/5 border-l-4 border-blue-500 p-4 mb-6 rounded-r-lg">
                <p class="text-sm m-0 italic text-slate-300">
                  摘要：本篇由教授智能体生成，结合 RAG 技术检索了最新的教学大纲。我们将从数学直观、算法逻辑及收敛特性三个维度深入剖析。
                </p>
              </div>
              <h2 class="text-xl text-blue-400">1. 核心概念回顾</h2>
              <p>在机器学习的语境下，优化算法的目标是寻找损失函数 $J(\theta)$ 的全局最小值。梯度下降通过迭代计算参数在负梯度方向上的增量来实现这一目标...</p>
              <h2 class="text-xl text-blue-400">2. 数学推导</h2>
              <div class="bg-black/30 p-4 rounded-lg font-mono text-center my-4 border border-white/5">
                θ_next = θ_current - η · ∇J(θ)
              </div>
              <p>其中 η 代表学习率，∇J(θ) 是损失函数对参数的偏导数向量。</p>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- 2. 架构师：思维导图 -->
        <TabsContent value="mindmap" class="m-0 h-full">
          <div class="bg-[#141414] border border-white/5 rounded-2xl h-[600px] flex flex-col items-center justify-center relative overflow-hidden group">
            <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-500/5 via-transparent to-transparent"></div>
            <GitFork class="h-16 w-16 text-blue-500/20 mb-4 group-hover:scale-110 transition-transform duration-700" />
            <p class="text-slate-400 font-medium">Mermaid 交互式图表预览</p>
            <p class="text-slate-600 text-xs mt-2 italic">正在渲染高度结构化的知识点联系...</p>
            <Button variant="outline" class="mt-6 border-white/10 hover:bg-white/5">
              <ExternalLink class="h-4 w-4 mr-2" /> 在全屏编辑器中打开
            </Button>
          </div>
        </TabsContent>

        <!-- 3. 考官：测验题目 -->
        <TabsContent value="quiz" class="m-0 space-y-4">
          <div v-for="(q, idx) in mockQuizzes" :key="idx" class="bg-[#141414] border border-white/5 p-6 rounded-2xl">
            <div class="flex justify-between items-start mb-4">
              <Badge class="bg-blue-500/20 text-blue-400 border-none">{{ q.type }}</Badge>
              <span class="text-slate-600 text-xs">Difficulty: Adaptive</span>
            </div>
            <h4 class="text-slate-200 font-medium mb-6">Q{{ idx + 1 }}: {{ q.question }}</h4>
            <div class="space-y-3">
              <div 
                v-for="(opt, oIdx) in q.options" 
                :key="oIdx"
                class="p-4 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 hover:border-blue-500/30 cursor-pointer transition-all flex items-center group"
              >
                <div class="h-6 w-6 rounded-full border border-white/20 flex items-center justify-center mr-3 group-hover:border-blue-500/50 text-[10px]">
                  {{ String.fromCharCode(65 + oIdx) }}
                </div>
                <span class="text-slate-400 text-sm">{{ opt }}</span>
              </div>
            </div>
          </div>
        </TabsContent>

        <!-- 4. 导演：视频脚本 -->
        <TabsContent value="video" class="m-0">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card v-for="i in 4" :key="i" class="bg-[#141414] border-white/5 overflow-hidden">
              <div class="aspect-video bg-black/40 flex items-center justify-center relative group">
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <PlayCircle class="h-10 w-10 text-white/20 group-hover:text-blue-500 transition-colors" />
                <Badge class="absolute top-3 left-3 bg-black/60 backdrop-blur-md border-none">Scene {{ i }}</Badge>
              </div>
              <CardContent class="p-4">
                <p class="text-xs text-blue-400 mb-1">视觉画面：</p>
                <p class="text-[13px] text-slate-400 mb-3 leading-relaxed">
                  {{ i === 1 ? '展示一个起伏的 3D 损失函数地形图，一个小球停在山顶。' : '小球沿着最陡峭的方向缓缓滚下，轨迹留下深蓝色的线条。' }}
                </p>
                <p class="text-xs text-orange-400 mb-1">旁白脚本：</p>
                <p class="text-[13px] text-slate-300 italic">
                  “想象你在迷雾笼罩的山顶，只能通过脚下的坡度来判断方向...”
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <!-- 5. 极客：实操案例 -->
        <TabsContent value="code" class="m-0">
          <div class="bg-[#1e1e1e] rounded-2xl border border-white/5 overflow-hidden">
            <div class="bg-white/5 px-4 py-3 border-b border-white/5 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="flex gap-1.5 mr-2">
                  <div class="h-2.5 w-2.5 rounded-full bg-red-500/20"></div>
                  <div class="h-2.5 w-2.5 rounded-full bg-yellow-500/20"></div>
                  <div class="h-2.5 w-2.5 rounded-full bg-green-500/20"></div>
                </div>
                <span class="text-xs text-slate-400 font-mono italic">gradient_descent_lab.py</span>
              </div>
              <Button variant="ghost" size="sm" class="h-7 text-xs gap-1.5 hover:bg-white/10 text-slate-400">
                <Copy class="h-3 w-3" /> Copy
              </Button>
            </div>
            <!-- 使用 v-pre 解决 {{ }} 冲突 -->
            <pre v-pre class="p-6 text-sm font-mono leading-relaxed overflow-x-auto"><code class="text-green-400/90">import numpy as np

def compute_gradient(x, y, theta):
    """
    极客智能体：实现最基础的梯度计算
    """
    m = len(y)
    prediction = x.dot(theta)
    return (1/m) * x.T.dot(prediction - y)

# 初始化参数
learning_rate = 0.01
iterations = 1000
theta = np.random.randn(2, 1)

print(f"Starting optimization process...")</code></pre>
          </div>
        </TabsContent>
      </div>
    </Tabs>
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
</style>