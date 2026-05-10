import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getTodayResources, getTrending, updateProgress as updateProgressApi } from '@/api/resources'
import type { TodayResource, TrendingItem, ResourceProgress } from '@/types/resources'

export const useDeliveryStore = defineStore('delivery', () => {
  const todayResources = ref<TodayResource[]>([])
  const trendingItems = ref<TrendingItem[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const currentResource = computed(() =>
    todayResources.value.find((r) => r.status === 'current') || todayResources.value[0]
  )

  async function fetchToday() {
    try {
      const data = await getTodayResources()
      todayResources.value = data
    } catch (e: any) {
      error.value = e?.response?.data?.detail || '获取今日资源失败'
    }
  }

  async function fetchTrending() {
    try {
      const data = await getTrending()
      trendingItems.value = data
    } catch { /* ignore */ }
  }

  async function fetchAll() {
    isLoading.value = true
    error.value = null
    try {
      await Promise.all([fetchToday(), fetchTrending()])
    } finally {
      isLoading.value = false
    }
  }

  async function updateResourceProgress(resourceId: string, progress: ResourceProgress) {
    await updateProgressApi(resourceId, progress)
    // 更新本地状态
    const idx = todayResources.value.findIndex((r) => r.id === resourceId)
    if (idx !== -1) {
      todayResources.value[idx].status = progress.status as TodayResource['status']
    }
  }

  return { todayResources, trendingItems, isLoading, error,
           currentResource, fetchToday, fetchTrending, fetchAll, updateResourceProgress }
})
