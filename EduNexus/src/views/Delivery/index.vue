<!-- src/views/Delivery/index.vue -->
<script setup lang="ts">
import DeliveryHeader from './components/DeliveryHeader.vue';
import ResourceTimeline from './components/ResourceTimeline.vue';
import AgentInsightPanel from './components/AgentInsightPanel.vue';
import TrendingPanel from './components/TrendingPanel.vue'; // 1. 导入新组件
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-8 pb-20 p-6">
    <DeliveryHeader />

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- 左侧：流式推送主区域 -->
      <div class="lg:col-span-8 space-y-6">
        <!-- ... 原有内容保持不变 ... -->
        <div class="flex items-center justify-between px-2">
          <h2 class="text-xl font-semibold text-white flex items-center gap-2">
            个人专属学习流
            <span class="text-[10px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded-full uppercase tracking-tighter">
              Live Feed
            </span>
          </h2>
        </div>
        <ResourceTimeline />
      </div>

      <!-- 右侧：侧边栏区域 -->
      <div class="lg:col-span-4 space-y-6">
        <!-- 现有智能体面板 -->
        <AgentInsightPanel />
        
        <!-- 2. 添加热点面板 -->
        <TrendingPanel />
      </div>
    </div>
  </div>
</template>