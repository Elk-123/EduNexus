<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2, GraduationCap, User, Mail, Lock, ShieldCheck, UserPlus } from 'lucide-vue-next'

const router = useRouter()
const isLoading = ref(false)

const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const handleRegister = async () => {
  isLoading.value = true
  setTimeout(() => {
    isLoading.value = false
    router.push('/login')
  }, 1000)
}
</script>

<template>
  <!-- 容器：使用 items-center justify-center 确保居中，p-4 防止贴边 -->
  <div class="min-h-screen w-full flex flex-col items-center justify-center bg-[#0b0b0b] relative overflow-hidden p-4">
    
    <!-- 背景纹理 -->
    <div class="absolute inset-0 z-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,#000_70%,transparent_100%)]"></div>

    <!-- 背景光晕 -->
    <div class="absolute top-[10%] left-[10%] w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[140px] pointer-events-none"></div>
    <div class="absolute bottom-[10%] right-[10%] w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[140px] pointer-events-none"></div>

    <!-- 容器：max-w-[600px] 宽屏设计 -->
    <div class="relative z-10 w-full max-w-[600px] flex flex-col items-center">
      
      <!-- 头部： mb-6 压缩空间 -->
      <div class="flex flex-col items-center mb-6 text-center">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-[0_0_30px_rgba(37,99,235,0.3)] mb-3">
          <GraduationCap class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-3xl font-bold tracking-tight text-white mb-1 bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-400">
          EduNexus
        </h1>
        <p class="text-zinc-500 text-sm">专业的智慧教育管理生态系统</p>
      </div>

      <!-- 注册主卡片：p-8 平衡高度 -->
      <div class="w-full bg-[#131314]/90 backdrop-blur-2xl border border-[#303134] rounded-[2.5rem] p-8 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)]">
        <div class="space-y-4">
          
          <div class="space-y-0.5">
            <h2 class="text-2xl font-semibold text-white">创建新账号</h2>
            <p class="text-zinc-500 text-sm">请完善以下信息完成注册</p>
          </div>

          <!-- 表单区域：text-lg 字体，h-[52px] 高度 -->
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

      <!-- 底部脚注：压缩到 mt-4 以防超出屏幕 -->
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
</style>