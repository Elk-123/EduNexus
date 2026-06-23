<!-- src/views/ContentFactory/components/TopicInput.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { Send, Loader2, Sparkles } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

const props = defineProps<{ isGenerating: boolean }>()
const emit = defineEmits(['start'])
const topic = ref('')

const handleSubmit = () => {
  if (topic.value.trim() && !props.isGenerating) {
    emit('start', topic.value)
  }
}

const suggestions = ['Transformer 架构中的注意机制', '梯度下降算法的几何解释', 'React Fiber 架构原理']
</script>

<template>
  <div class="max-w-4xl mx-auto w-full">
    <div class="relative group">
      <div class="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>
      <div class="relative flex items-center bg-[#1a1a1a] border border-white/10 rounded-2xl p-1.5 shadow-2xl">
        <div class="flex-1 px-4 flex items-center gap-3">
          <Sparkles class="h-5 w-5 text-blue-400 opacity-60" />
          <input 
            v-model="topic"
            @keyup.enter="handleSubmit"
            placeholder="输入你想学习的主题，AI 专家团将为你定制全套资源..."
            class="w-full bg-transparent border-none focus:ring-0 text-slate-200 placeholder:text-slate-500 py-3 text-lg"
          />
        </div>
        <Button 
          @click="handleSubmit" 
          :disabled="isGenerating || !topic"
          class="bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-8 h-12 transition-all"
        >
          <Loader2 v-if="isGenerating" class="mr-2 h-4 w-4 animate-spin" />
          <Send v-else class="mr-2 h-4 w-4" />
          {{ isGenerating ? '生成中...' : '开始生成' }}
        </Button>
      </div>
    </div>
    
    <!-- 快捷建议 -->
    <div class="mt-4 flex gap-2 justify-center overflow-x-auto no-scrollbar">
      <button
        v-for="s in suggestions"
        :key="s"
        @click="topic = s"
        class="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[11px] text-slate-400 hover:bg-white/10 hover:text-white transition-colors whitespace-nowrap"
      >
        {{ s }}
      </button>
    </div>
  </div>
</template>