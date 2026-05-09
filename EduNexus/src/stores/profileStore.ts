import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ProfileDimensions } from '@/types/profile'
import { getMyProfile } from '@/api/profile'

export const useProfileStore = defineStore('profile', () => {
  const profileData = ref<ProfileDimensions | null>(null)
  const version = ref(0)
  const isLoading = ref(false)

  const hasProfile = computed(() => profileData.value !== null)

  async function fetchProfile() {
    isLoading.value = true
    try {
      const res = await getMyProfile()
      profileData.value = res.profile_data
      version.value = res.version
    } catch {
      profileData.value = null
    } finally {
      isLoading.value = false
    }
  }

  function setProfile(data: ProfileDimensions, ver: number) {
    profileData.value = data
    version.value = ver
  }

  return { profileData, version, isLoading, hasProfile, fetchProfile, setProfile }
})
