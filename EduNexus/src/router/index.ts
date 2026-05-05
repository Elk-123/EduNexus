import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      component: DashboardLayout,
      children: [
        {
          path: '', 
          name: 'home',
          component: HomeView
        }
      ]
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: () => import('../views/OnboardingView.vue'),
    },
    {
      path: '/factory',
      component: () => import('@/layouts/DashboardLayout.vue'),
      children: [
        {
          path: '',
          name: 'content-factory',
          component: () => import('@/views/ContentFactory/index.vue'),
        }
      ]
    },
    {
      path: '/path',
      component: () => import('@/layouts/DashboardLayout.vue'),
      children: [
        {
          path: '',
          name: 'learning-path',
          component: () => import('@/views/LearningPath/index.vue'),
        }
      ]
    }
  ]
})

export default router