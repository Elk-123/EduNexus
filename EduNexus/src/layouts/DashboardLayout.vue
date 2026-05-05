<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar'
import { Search, User } from 'lucide-vue-next'
</script>

<template>
  <SidebarProvider>
    <div class="flex min-h-screen w-full bg-[#0b0b0b] text-zinc-200 font-sans relative overflow-hidden">
      <!-- 延续登录页的背景网格 -->
      <div class="absolute inset-0 z-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none"></div>

      <!-- 侧边栏 -->
      <AppSidebar />

      <SidebarInset class="flex flex-col flex-1 bg-transparent relative z-10">
        <!-- 顶部导航栏 (Header) -->
        <header class="flex h-16 items-center justify-between border-b border-[#303134] px-6 bg-[#0b0b0b]/50 backdrop-blur-xl sticky top-0 z-50">
          <div class="flex items-center gap-4">
            <SidebarTrigger class="text-zinc-400 hover:text-white transition-colors" />
          </div>

          <!-- 右侧工具栏 -->
          <div class="flex items-center gap-6">
            <div class="relative hidden md:block">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <input 
                type="text" 
                placeholder="搜索资源..." 
                class="bg-[#131314] border border-[#303134] rounded-full pl-10 pr-4 py-1.5 text-sm w-64 focus:outline-none focus:border-blue-500/50 transition-all placeholder:text-zinc-600"
              />
            </div>
          </div>
        </header>

        <!-- 主内容区 -->
        <main class="flex-1 p-8 overflow-y-auto custom-scrollbar">
          <div class="max-w-7xl mx-auto">
            <router-view />
          </div>
        </main>
      </SidebarInset>
    </div>
  </SidebarProvider>
</template>

<style>
/* 滚动条美化 */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #303134;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #3c4043;
}
</style>