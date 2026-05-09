<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Loader2, 
  GraduationCap, 
  User, 
  Mail, 
  Lock, 
  ShieldCheck, 
  UserPlus,
  AlertCircle 
} from 'lucide-vue-next'
import apiClient from '@/api/client'
import type { AuthResponse } from '@/types/auth'

const router = useRouter()
const isLoading = ref(false)
const errorMessage = ref('')

const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const handleRegister = async () => {
  // 1. 基础校验
  if (!formData.value.username || !formData.value.email || !formData.value.password) {
    errorMessage.value = '请填写所有必填信息'
    return
  }

  if (formData.value.password.length < 6) {
    errorMessage.value = '密码长度至少需要 6 位'
    return
  }

  if (formData.value.password !== formData.value.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    // 2. 发起注册请求
    const { data } = await apiClient.post<AuthResponse>('/auth/register', {
      username: formData.value.username,
      email: formData.value.email,
      password: formData.value.password
    })

    // 3. 注册成功逻辑：存储 Token 并跳转
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    // 注册后默认进入破冰流程
    router.push('/onboarding')
  } catch (error: any) {
    console.error('Registration error:', error)
    if (error.response && error.response.data) {
      errorMessage.value = error.response.data.detail || '注册失败，请稍后重试'
    } else {
      errorMessage.value = '无法连接到服务器，请检查网络'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <!-- 容器 -->
  <div class="min-h-screen w-full flex flex-col items-center justify-center bg-[#0b0b0b] relative overflow-hidden p-4">
    
    <!-- 背景纹理 -->
    <div class="absolute inset-0 z-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,#000_70%,transparent_100%)]"></div>

    <!-- 背景光晕 -->
    <div class="absolute top-[10%] left-[10%] w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[140px] pointer-events-none"></div>
    <div class="absolute bottom-[10%] right-[10%] w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[140px] pointer-events-none"></div>

    <div class="relative z-10 w-full max-w-[600px] flex flex-col items-center">
      
      <!-- 头部 -->
      <div class="flex flex-col items-center mb-6 text-center">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-[0_0_30px_rgba(37,99,235,0.3)] mb-3">
          <GraduationCap class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-3xl font-bold tracking-tight text-white mb-1 bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-400">
          EduNexus
        </h1>
        <p class="text-zinc-500 text-sm">专业的智慧教育管理生态系统</p>
      </div>

      <!-- 注册主卡片 -->
      <div class="w-full bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-8 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
        <div class="space-y-4">
          
          <div class="space-y-0.5">
            <h2 class="text-2xl font-semibold text-white">创建新账号</h2>
            <p class="text-zinc-500 text-sm">请完善以下信息完成注册</p>
          </div>

          <!-- 错误提示 -->
          <Transition name="fade">
            <Alert v-if="errorMessage" variant="destructive" class="bg-red-500/10 border-red-500/20 text-red-400 rounded-xl py-3">
              <AlertCircle class="h-4 w-4" />
              <AlertDescription>{{ errorMessage }}</AlertDescription>
            </Alert>
          </Transition>

          <!-- 表单区域 -->
          <div class="space-y-3.5">
            <!-- 用户名 -->
            <div class="space-y-1.5">
              <Label for="username" class="text-xs font-bold text-zinc-500 ml-1 uppercase tracking-[0.2em]">全名</Label>
              <div class="relative group">
                <User class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600 group-focus-within:text-blue-500 transition-colors" />
                <Input 
                  id="username" 
                  v-model="formData.username"
                  placeholder="您的姓名" 
                  @keyup.enter="handleRegister"
                  class="h-[52px] pl-14 bg-[#0b0b0b] border-[#3c4043] focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-2xl text-white text-lg transition-all placeholder:text-zinc-800"
                />
              </div>
            </div>

            <!-- 电子邮箱 -->
            <div class="space-y-1.5">
              <Label for="email" class="text-xs font-bold text-zinc-500 ml-1 uppercase tracking-[0.2em]">电子邮箱</Label>
              <div class="relative group">
                <Mail class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600 group-focus-within:text-blue-500 transition-colors" />
                <Input 
                  id="email" 
                  type="email"
                  v-model="formData.email"
                  placeholder="name@edunexus.com" 
                  @keyup.enter="handleRegister"
                  class="h-[52px] pl-14 bg-[#0b0b0b] border-[#3c4043] focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-2xl text-white text-lg transition-all placeholder:text-zinc-800"
                />
              </div>
            </div>
            
            <!-- 密码 -->
            <div class="space-y-1.5">
              <Label for="password" class="text-xs font-bold text-zinc-500 ml-1 uppercase tracking-[0.2em]">设置密码</Label>
              <div class="relative group">
                <Lock class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600 group-focus-within:text-blue-500 transition-colors" />
                <Input 
                  id="password" 
                  type="password" 
                  v-model="formData.password"
                  placeholder="••••••••"
                  @keyup.enter="handleRegister"
                  class="h-[52px] pl-14 bg-[#0b0b0b] border-[#3c4043] focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-2xl text-white text-lg transition-all placeholder:text-zinc-800"
                />
              </div>
            </div>

            <!-- 确认密码 -->
            <div class="space-y-1.5">
              <Label for="confirm" class="text-xs font-bold text-zinc-500 ml-1 uppercase tracking-[0.2em]">确认密码</Label>
              <div class="relative group">
                <ShieldCheck class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600 group-focus-within:text-blue-500 transition-colors" />
                <Input 
                  id="confirm" 
                  type="password" 
                  v-model="formData.confirmPassword"
                  placeholder="••••••••"
                  @keyup.enter="handleRegister"
                  class="h-[52px] pl-14 bg-[#0b0b0b] border-[#3c4043] focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-2xl text-white text-lg transition-all placeholder:text-zinc-800"
                />
              </div>
            </div>

            <Button 
              @click="handleRegister" 
              :disabled="isLoading"
              class="w-full h-14 bg-blue-600 hover:bg-blue-500 text-white text-lg font-bold rounded-2xl mt-2 shadow-xl shadow-blue-900/40 active:scale-[0.98] transition-all flex items-center justify-center gap-3"
            >
              <Loader2 v-if="isLoading" class="h-5 w-5 animate-spin" />
              <span v-else>立即注册系统</span>
              <UserPlus v-if="!isLoading" class="h-5 w-5" />
            </Button>
          </div>

          <!-- 底部链接 -->
          <div class="pt-4 border-t border-[#303134] text-center">
            <p class="text-zinc-400 text-sm">
              已有账号？ 
              <router-link to="/login" class="text-blue-500 hover:text-blue-400 font-bold ml-1 transition-colors">
                登录系统
              </router-link>
            </p>
          </div>
        </div>
      </div>

      <!-- 底部脚注 -->
      <div class="mt-4 flex items-center justify-center gap-4">
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
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus {
  -webkit-text-fill-color: white;
  -webkit-box-shadow: 0 0 0px 1000px #0b0b0b inset;
  transition: background-color 5000s ease-in-out 0s;
}

.relative.z-10 {
  animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
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