import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/auth'
import { refreshToken as refreshTokenApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))
  const isRefreshing = ref(false)

  const isLoggedIn = computed(() => !!token.value)
  const isOnboarded = computed(() => user.value?.onboarding_completed ?? false)

  function setAuth(authToken: string, authUser: User, refreshTokenValue?: string) {
    token.value = authToken
    user.value = authUser
    localStorage.setItem('token', authToken)
    localStorage.setItem('user', JSON.stringify(authUser))
    if (refreshTokenValue) {
      refreshToken.value = refreshTokenValue
      localStorage.setItem('refreshToken', refreshTokenValue)
    }
  }

  function setOnboardingCompleted() {
    if (user.value) {
      user.value.onboarding_completed = true
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  async function refreshAuthToken() {
    if (!refreshToken.value || isRefreshing.value) {
      return false
    }

    try {
      isRefreshing.value = true
      const result = await refreshTokenApi(refreshToken.value)
      setAuth(result.access_token, user.value!)
      return true
    } catch (error) {
      logout()
      return false
    } finally {
      isRefreshing.value = false
    }
  }

  function logout() {
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  }

  return { token, refreshToken, user, isLoggedIn, isOnboarded, isRefreshing, setAuth, setOnboardingCompleted, refreshAuthToken, logout }
})
