<!-- src/views/Delivery/index.vue -->
<script setup lang="ts">
import { onMounted, computed } from 'vue'
import DeliveryHeader from './components/DeliveryHeader.vue'
import ResourceTimeline from './components/ResourceTimeline.vue'
import AgentInsightPanel from './components/AgentInsightPanel.vue'
import TrendingPanel from './components/TrendingPanel.vue'
import { useDeliveryStore } from '@/stores/deliveryStore'
import type { ResourceProgress } from '@/types/resources'

const deliveryStore = useDeliveryStore()

const courseTitle = computed(() => {
  return deliveryStore.todayResources[0]?.title || '学习内容加载中...'
})

const todayProgress = computed(() => {
  const total = deliveryStore.todayResources.length
  if (total === 0) return 0
  const completed = deliveryStore.todayResources.filter(r => r.status === 'completed').length
  return Math.round((completed / total) * 100)
})

const handleProgressUpdate = async (resourceId: string, progress: ResourceProgress) => {
  await deliveryStore.updateResourceProgress(resourceId, progress)
}

onMounted(() => {
  deliveryStore.fetchAll()
})
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-8 pb-20 p-6">
    <DeliveryHeader :course-title="courseTitle" :progress="todayProgress" />

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <div class="lg:col-span-8 space-y-6">
        <div class="flex items-center justify-between px-2">
          <h2 class="text-xl font-semibold text-white flex items-center gap-2">
            个人专属学习流
            <span class="text-[10px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded-full uppercase tracking-tighter">
              Live Feed
            </span>
          </h2>
        </div>
        <ResourceTimeline
          :resources="deliveryStore.todayResources"
          :is-loading="deliveryStore.isLoading"
          @update-progress="handleProgressUpdate"
        />
      </div>

      <div class="lg:col-span-4 space-y-6">
        <AgentInsightPanel />
        <TrendingPanel :items="deliveryStore.trendingItems" />
      </div>
    </div>
  </div>
</template>