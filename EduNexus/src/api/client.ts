import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：自动注入 Token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：处理 401 错误并尝试刷新 Token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const authStore = useAuthStore()

    // 如果是 401 错误且还没有尝试刷新过
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // 尝试刷新 token
      const refreshSuccess = await authStore.refreshAuthToken()
      if (refreshSuccess) {
        // 使用新的 token 重试原请求
        originalRequest.headers.Authorization = `Bearer ${authStore.token}`
        return apiClient(originalRequest)
      }
    }

    // 如果刷新失败，抛出错误
    return Promise.reject(error)
  }
)

export default apiClient