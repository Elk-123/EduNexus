<template>
  <div class="min-h-screen bg-[#0b0b0b]">
    <!-- 背景纹理：网格线 -->
    <div class="absolute inset-0 z-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,#000_70%,transparent_100%)]"></div>

    <!-- 强化背景光晕 -->
    <div class="absolute top-[20%] left-[10%] w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[140px] pointer-events-none"></div>
    <div class="absolute bottom-[20%] right-[10%] w-[600px] h-[600px] bg-pink-600/10 rounded-full blur-[140px] pointer-events-none"></div>

    <div class="relative z-10 container mx-auto px-4 py-8 max-w-6xl">
      <!-- 头部 -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-white mb-2">学习效果评估</h1>
        <p class="text-zinc-400">全面分析您的学习进度，提供个性化提升建议</p>
      </div>

      <!-- 主要内容区 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧：学习进度概览 -->
        <div class="space-y-6">
          <!-- 学习概览卡片 -->
          <div class="bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-6 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
            <h3 class="text-white font-semibold mb-4">本周学习概览</h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-zinc-400 text-sm">学习时长</span>
                <span class="text-white font-medium">12.5 小时</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-zinc-400 text-sm">完成课程</span>
                <span class="text-white font-medium">8 / 12</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-zinc-400 text-sm">测验平均分</span>
                <span class="text-white font-medium">85%</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-zinc-400 text-sm">知识点掌握</span>
                <span class="text-white font-medium">76%</span>
              </div>
            </div>
          </div>

          <!-- 学习建议 -->
          <div class="bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-6 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
            <h3 class="text-white font-semibold mb-4">AI 学习建议</h3>
            <div class="space-y-3">
              <div class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Target class="w-3 h-3 text-white" />
                </div>
                <p class="text-sm text-zinc-300">您的数学进度较快，建议继续保持</p>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <AlertCircle class="w-3 h-3 text-white" />
                </div>
                <p class="text-sm text-zinc-300">物理概念需要加强，建议多做实验题</p>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full bg-green-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <TrendingUp class="w-3 h-3 text-white" />
                </div>
                <p class="text-sm text-zinc-300">编程能力提升显著，可以挑战更高难度</p>
              </div>
            </div>
          </div>

          <!-- 学习目标 -->
          <div class="bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-6 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
            <h3 class="text-white font-semibold mb-4">下月目标</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-sm text-zinc-400">完成微积分基础</span>
                <span class="text-xs bg-green-600/20 text-green-400 px-2 py-1 rounded-full">进行中</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-zinc-400">线性代数进阶</span>
                <span class="text-xs bg-yellow-600/20 text-yellow-400 px-2 py-1 rounded-full">待开始</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-zinc-400">算法练习</span>
                <span class="text-xs bg-blue-600/20 text-blue-400 px-2 py-1 rounded-full">计划中</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 中间：详细分析 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 学习进度雷达图 -->
          <div class="bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-6 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-white font-semibold">能力分析</h3>
              <Button variant="outline" size="sm" class="text-zinc-400 border-[#303134]">
                <Download class="w-4 h-4 mr-1" />
                导出报告
              </Button>
            </div>

            <!-- 雷达图容器 -->
            <div class="h-80 flex items-center justify-center">
              <div class="relative w-64 h-64">
                <!-- 简化的雷达图表示 -->
                <svg viewBox="0 0 200 200" class="w-full h-full">
                  <!-- 背景网格 -->
                  <g stroke="#303134" fill="none">
                    <polygon points="100,40 160,80 160,120 100,160 40,120 40,80" opacity="0.3"/>
                    <polygon points="100,60 140,80 140,120 100,140 60,120 60,80" opacity="0.3"/>
                    <polygon points="100,80 120,90 120,110 100,120 80,110 80,90" opacity="0.3"/>
                  </g>

                  <!-- 数据区域 -->
                  <polygon points="100,50 150,85 145,115 100,135 55,105 55,85"
                           fill="rgba(99, 102, 241, 0.3)"
                           stroke="#6366f1"
                           stroke-width="2"/>

                  <!-- 数据点 -->
                  <g fill="#6366f1">
                    <circle cx="100" cy="50" r="3"/>
                    <circle cx="150" cy="85" r="3"/>
                    <circle cx="145" cy="115" r="3"/>
                    <circle cx="100" cy="135" r="3"/>
                    <circle cx="55" cy="105" r="3"/>
                    <circle cx="55" cy="85" r="3"/>
                  </g>

                  <!-- 标签 -->
                  <g fill="white" font-size="10" text-anchor="middle">
                    <text x="100" y="30">数学</text>
                    <text x="175" y="85">物理</text>
                    <text x="175" y="125">编程</text>
                    <text x="100" y="175">英语</text>
                    <text x="25" y="125">逻辑</text>
                    <text x="25" y="85">创意</text>
                  </g>
                </svg>
              </div>
            </div>

            <!-- 图例 -->
            <div class="mt-6 grid grid-cols-3 gap-4">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-indigo-500 rounded"></div>
                <span class="text-xs text-zinc-400">当前水平</span>
              </div>
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-zinc-600 rounded"></div>
                <span class="text-xs text-zinc-400">平均水平</span>
              </div>
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-green-500 rounded"></div>
                <span class="text-xs text-zinc-400">目标水平</span>
              </div>
            </div>
          </div>

          <!-- 学习记录 -->
          <div class="bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-6 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
            <h3 class="text-white font-semibold mb-4">最近学习记录</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between p-3 bg-[#1a1a1b]/50 rounded-xl">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-blue-600/20 flex items-center justify-center">
                    <BookOpen class="w-4 h-4 text-blue-400" />
                  </div>
                  <div>
                    <p class="text-white text-sm font-medium">微积分导数基础</p>
                    <p class="text-xs text-zinc-400">今天 14:30 · 完成度 100%</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-xs text-green-400 font-medium">优秀</p>
                  <p class="text-xs text-zinc-500">95分</p>
                </div>
              </div>

              <div class="flex items-center justify-between p-3 bg-[#1a1a1b]/50 rounded-xl">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-purple-600/20 flex items-center justify-center">
                    <Brain class="w-4 h-4 text-purple-400" />
                  </div>
                  <div>
                    <p class="text-white text-sm font-medium">线性代数矩阵运算</p>
                    <p class="text-xs text-zinc-400">昨天 16:45 · 完成度 85%</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-xs text-yellow-400 font-medium">良好</p>
                  <p class="text-xs text-zinc-500">88分</p>
                </div>
              </div>

              <div class="flex items-center justify-between p-3 bg-[#1a1a1b]/50 rounded-xl">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-green-600/20 flex items-center justify-center">
                    <Code class="w-4 h-4 text-green-400" />
                  </div>
                  <div>
                    <p class="text-white text-sm font-medium">Python 数据结构</p>
                    <p class="text-xs text-zinc-400">5月9日 19:20 · 完成度 92%</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-xs text-green-400 font-medium">优秀</p>
                  <p class="text-xs text-zinc-500">92分</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Target, AlertCircle, TrendingUp, Download, BookOpen, Brain, Code } from 'lucide-vue-next'
import Button from '@/components/ui/button/Button.vue'
</script>