import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ProfileDimensions, OnboardingSubmission } from '@/types/profile'
import { getMyProfile, updateMyProfile } from '@/api/profile'

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

  async function updateProfile(payload: OnboardingSubmission) {
    isLoading.value = true
    try {
      const res = await updateMyProfile(payload)
      profileData.value = res.profile_data
      version.value = res.version
      return true
    } catch {
      return false
    } finally {
      isLoading.value = false
    }
  }

  return { profileData, version, isLoading, hasProfile, fetchProfile, setProfile, updateProfile }
})
