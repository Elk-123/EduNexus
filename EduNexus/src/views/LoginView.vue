<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2, GraduationCap, ArrowRight, AlertCircle } from 'lucide-vue-next'
import { Alert, AlertDescription } from '@/components/ui/alert'
import apiClient from '@/api/client'
import type { AuthResponse } from '@/types/auth'

const router = useRouter()
const isLoading = ref(false)
const errorMessage = ref('')

// 表单数据响应式对象
const form = reactive({
  email: '',
  password: ''
})

const handleLogin = async () => {
  // 基础表单校验
  if (!form.email || !form.password) {
    errorMessage.value = '请输入电子邮箱和密码'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    // 1. 发起 API 请求
    // 注意：确保后端 app/api/v1/auth.py 中的 login 路由接受 email 和 password
    const { data } = await apiClient.post<AuthResponse>('/auth/login', {
      email: form.email,
      password: form.password
    })

    // 2. 持久化存储认证信息
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    // 3. 逻辑跳转：已完成画像去首页，未完成去破冰
    if (data.user.onboarding_completed) {
      router.push('/')
    } else {
      router.push('/onboarding')
    }
  } catch (error: any) {
    // 4. 错误处理：提取后端 FastAPI 返回的 detail 信息
    console.error('Login failed:', error)
    if (error.response && error.response.data) {
      errorMessage.value = error.response.data.detail || '登录失败，请检查您的凭据'
    } else {
      errorMessage.value = '无法连接到服务器，请检查网络设置'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <!-- 容器：深色背景 + 动态网格 -->
  <div class="min-h-screen w-full flex flex-col items-center justify-center bg-[#0b0b0b] relative overflow-hidden p-6">
    
    <!-- 背景纹理：网格线 -->
    <div class="absolute inset-0 z-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,#000_70%,transparent_100%)]"></div>

    <!-- 强化背景光晕 -->
    <div class="absolute top-[20%] left-[10%] w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[140px] pointer-events-none"></div>
    <div class="absolute bottom-[20%] right-[10%] w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[140px] pointer-events-none"></div>

    <div class="relative z-10 w-full max-w-[500px]">
      
      <!-- 头部：Hero Header -->
      <div class="flex flex-col items-center mb-12 text-center">
        <div class="w-20 h-20 rounded-[1.5rem] bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-[0_0_50px_rgba(37,99,235,0.4)] mb-8">
          <GraduationCap class="w-12 h-12 text-white" />
        </div>
        <h1 class="text-5xl font-bold tracking-tight text-white mb-4 bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-400 font-sans">
          EduNexus
        </h1>
        <p class="text-zinc-400 text-lg max-w-[350px] leading-relaxed">
          专业的智慧教育管理生态系统
        </p>
      </div>

      <!-- 登录主卡片 -->
      <div class="bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-10 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
        <div class="space-y-8">
          
          <!-- 卡片内头部 -->
          <div class="space-y-2">
            <h2 class="text-2xl font-semibold text-white">欢迎回来</h2>
            <p class="text-zinc-500 text-sm">请输入您的账号凭据以继续</p>
          </div>

          <!-- 错误提示组件 -->
          <Transition name="fade">
            <Alert v-if="errorMessage" variant="destructive" class="bg-red-500/10 border-red-500/20 text-red-400 rounded-xl">
              <AlertCircle class="h-4 w-4" />
              <AlertDescription>{{ errorMessage }}</AlertDescription>
            </Alert>
          </Transition>

          <!-- 表单区域 -->
          <div class="space-y-6">
            <div class="space-y-2">
              <Label for="email" class="text-xs font-bold text-zinc-500 ml-1 uppercase tracking-[0.2em]">电子邮箱</Label>
              <Input 
                id="email" 
                v-model="form.email"
                type="email"
                placeholder="name@edunexus.com" 
                @keyup.enter="handleLogin"
                class="h-14 bg-[#0b0b0b] border-[#3c4043] focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-2xl text-white text-lg px-6 transition-all placeholder:text-zinc-800"
              />
            </div>
            
            <div class="space-y-2">
              <div class="flex items-center justify-between ml-1">
                <Label for="password" class="text-xs font-bold text-zinc-500 uppercase tracking-[0.2em]">安全密码</Label>
                <a href="#" class="text-sm text-blue-500 hover:text-blue-400 font-medium transition-colors">忘记密码？</a>
              </div>
              <Input 
                id="password" 
                v-model="form.password"
                type="password" 
                placeholder="••••••••"
                @keyup.enter="handleLogin"
                class="h-14 bg-[#0b0b0b] border-[#3c4043] focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-2xl text-white text-lg px-6 transition-all placeholder:text-zinc-800"
              />
            </div>

            <Button 
              @click="handleLogin" 
              :disabled="isLoading"
              class="w-full h-14 bg-blue-600 hover:bg-blue-500 text-white text-lg font-bold rounded-2xl mt-4 shadow-xl shadow-blue-900/40 active:scale-[0.98] transition-all flex items-center justify-center gap-3"
            >
              <Loader2 v-if="isLoading" class="h-5 w-5 animate-spin" />
              <span v-else>登录系统</span>
              <ArrowRight v-if="!isLoading" class="h-5 w-5" />
            </Button>
          </div>

          <!-- 底部链接 -->
          <div class="pt-6 border-t border-[#303134] text-center">
            <p class="text-zinc-400">
              新用户？ 
              <a href="#" @click.prevent="router.push('/register')" class="text-blue-500 hover:text-blue-400 font-bold ml-1 transition-colors">
                注册教育账号
              </a>
            </p>
          </div>
        </div>
      </div>

      <!-- 底部脚注 -->
      <div class="mt-16 flex items-center justify-center gap-4">
        <span class="h-px w-8 bg-zinc-800"></span>
        <p class="text-[10px] uppercase tracking-[0.5em] text-zinc-600 font-bold">
          EduNexus Intelligence
        </p>
        <span class="h-px w-8 bg-zinc-800"></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 强制覆盖 Chrome 自动填充 */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus {
  -webkit-text-fill-color: white;
  -webkit-box-shadow: 0 0 0px 1000px #0b0b0b inset;
  transition: background-color 5000s ease-in-out 0s;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>