<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  Sidebar, SidebarContent, SidebarHeader, SidebarFooter, SidebarMenu, 
  SidebarMenuItem, SidebarMenuButton, SidebarGroup 
} from '@/components/ui/sidebar'
import { 
  Popover, PopoverContent, PopoverTrigger 
} from '@/components/ui/popover'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { 
  LayoutDashboard, Factory, Route, Send, MessageSquareQuote, 
  BarChart3, Settings, GraduationCap, Camera, LogOut, Check, Pencil 
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const menuItems = [
  { title: '控制台首页', icon: LayoutDashboard, path: '/' },
  { title: '资源生成', icon: Factory, path: '/factory' },
  { title: '学习路径规划', icon: Route, path: '/path' },
  { title: '资源推送', icon: Send, path: '/delivery' },
  { title: '智能指导', icon: MessageSquareQuote, path: '/tutor' },
  { title: '学习效果评估', icon: BarChart3, path: '/assessment' },
]

// Profile 状态管理
const username = ref('JD / Meng Archi')
const email = ref('meng.archi6829@gmail.com')
const isEditing = ref(false) // 强制默认为 false

// 切换编辑状态
const toggleEdit = () => {
  isEditing.value = !isEditing.value
}

// 退出登录
const handleLogout = () => {
  router.push('/login')
}
</script>

<template>
  <Sidebar class="border-r border-[#303134] bg-[#0b0b0b]">
    <!-- 1. 顶部 Logo -->
    <SidebarHeader 
      class="h-16 flex items-center px-6 border-b border-[#303134] cursor-pointer hover:bg-white/5 transition-colors"
      @click="router.push('/')"
    >
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-900/20">
          <GraduationCap class="w-5 h-5 text-white" />
        </div>
        <span class="text-lg font-bold tracking-tight text-white">EduNexus</span>
      </div>
    </SidebarHeader>

    <!-- 2. 中间主导航 -->
    <SidebarContent class="px-3 py-4 bg-transparent">
      <SidebarGroup>
        <SidebarMenu class="gap-1">
          <SidebarMenuItem v-for="item in menuItems" :key="item.path">
            <SidebarMenuButton 
              :is-active="route.path === item.path"
              @click="router.push(item.path)"
              class="w-full h-10 rounded-xl transition-all duration-200 group text-[14px] font-medium hover:bg-[#1e1f20] data-[active=true]:bg-[#2d2e30]"
            >
              <div class="flex items-center gap-3 px-3 cursor-pointer w-full">
                <component 
                  :is="item.icon" 
                  class="w-4.5 h-4.5 transition-colors" 
                  :class="route.path === item.path ? 'text-blue-500' : 'text-zinc-500 group-hover:text-zinc-300'" 
                />
                <span :class="route.path === item.path ? 'text-white' : 'text-zinc-400 group-hover:text-zinc-200'">
                  {{ item.title }}
                </span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarGroup>
    </SidebarContent>

    <!-- 3. 底部区域 -->
    <SidebarFooter class="px-3 pb-6 mt-auto space-y-4 bg-transparent">
      
      <!-- Settings 按钮 -->
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton class="w-full h-10 rounded-xl transition-all hover:bg-[#1e1f20] text-[14px] group">
            <div class="flex items-center gap-3 px-3 cursor-pointer w-full">
              <Settings class="w-4.5 h-4.5 text-zinc-500 group-hover:text-zinc-300" />
              <span class="text-zinc-400 group-hover:text-zinc-200">Settings</span>
            </div>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>

      <!-- Profile Popover -->
      <Popover @update:open="(val) => !val && (isEditing = false)">
        <PopoverTrigger as-child>
          <div class="flex items-center gap-3 px-3 py-2 rounded-xl hover:bg-[#1e1f20] transition-all cursor-pointer group outline-none">
            <div class="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex-shrink-0 flex items-center justify-center text-[10px] font-bold text-white shadow-lg transition-all group-hover:ring-2 ring-blue-500/20">
              JD
            </div>
            <div class="flex flex-col truncate">
              <!-- 列表处的邮箱也稍微加亮一点 -->
              <span class="text-[12px] text-zinc-300 font-medium group-hover:text-white transition-colors truncate">
                {{ email }}
              </span>
            </div>
          </div>
        </PopoverTrigger>

        <!-- @openAutoFocus.prevent 阻止自动聚焦到输入框 -->
        <PopoverContent 
          @openAutoFocus.prevent
          side="top" 
          align="center" 
          :sideOffset="12"
          class="w-80 p-0 bg-[#202124] border border-[#3c4043] rounded-[1.5rem] shadow-[0_8px_30px_rgb(0,0,0,0.5)] overflow-hidden outline-none z-[100]"
        >
          <!-- 头部：去掉托管字样，颜色加深 -->
          <div class="p-6 flex flex-col items-center border-b border-[#3c4043]">
            <div class="relative group cursor-pointer mb-3">
              <div class="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-2xl font-bold text-white shadow-xl">
                JD
              </div>
              <div class="absolute inset-0 bg-black/40 rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <Camera class="w-5 h-5 text-white" />
              </div>
            </div>
            <!-- 加深邮箱显示：使用 text-white -->
            <p class="text-sm font-bold text-white">{{ email }}</p>
          </div>

          <!-- 表单区域 -->
          <div class="p-6 space-y-5">
            <div class="space-y-2">
              <label class="text-[10px] uppercase tracking-[0.15em] font-bold text-zinc-500 px-1">用户名</label>
              <div class="flex items-center gap-2 min-h-[36px]">
                <!-- 关键修改：默认显示 Span，编辑时才显示 Input -->
                <template v-if="!isEditing">
                  <span class="flex-1 px-1 text-sm font-bold text-white py-2">
                    {{ username }}
                  </span>
                </template>
                <template v-else>
                  <Input 
                    v-model="username" 
                    class="h-9 bg-[#28292c] border-[#3c4043] text-white rounded-xl text-sm transition-all focus-visible:ring-blue-500/40"
                    autofocus
                  />
                </template>

                <button 
                  @click="toggleEdit" 
                  class="p-2 hover:bg-zinc-700/50 rounded-lg text-zinc-400 hover:text-white transition-colors shrink-0"
                >
                  <component :is="isEditing ? Check : Pencil" class="w-4 h-4" :class="isEditing && 'text-blue-400'" />
                </button>
              </div>
            </div>
          </div>

          <!-- 底部操作区：路由跳转 -->
          <div class="px-6 py-4 bg-[#1a1b1e] flex justify-center border-t border-[#3c4043]">
            <Button 
              @click="handleLogout"
              variant="ghost" 
              class="w-full text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-xl gap-2 font-bold transition-all text-xs"
            >
              <LogOut class="w-3.5 h-3.5" />
              退出 EduNexus 帐号
            </Button>
          </div>
        </PopoverContent>
      </Popover>
    </SidebarFooter>
  </Sidebar>
</template>

<style scoped>
:deep([data-active="true"]) {
  background-color: #2d2e30 !important;
}
</style>