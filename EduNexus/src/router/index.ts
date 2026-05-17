import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
// import DashboardLayout from '@/layouts/DashboardLayout.simple.vue'
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
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue')
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: () => import('@/views/OnboardingView.vue')
    },
    {
      path: '/',
      component: DashboardLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: HomeView
        },
        {
          path: 'simple',
          name: 'simple',
          component: () => import('@/views/SimpleTest.vue')
        },
        {
          path: 'factory',
          name: 'content-factory',
          component: () => import('@/views/ContentFactory/index.vue')
        },
        {
          path: 'path',
          name: 'learning-path',
          component: () => import('@/views/LearningPath/index.vue')
        },
        {
          path: 'delivery',
          name: 'resource-delivery',
          component: () => import('@/views/Delivery/index.vue')
        },
        {
          path: 'tutor',
          name: 'tutor',
          component: () => import('@/views/Tutor/index.vue')
        },
        {
          path: 'assessment',
          name: 'assessment',
          component: () => import('@/views/Assessment/index.vue')
        }
      ]
    }
  ]
})

// 全局前置守卫
router.beforeEach((to, _from, next) => {
  // 白名单路径不需要认证
  const publicPaths = ['/login', '/register']
  const isPublicPath = publicPaths.includes(to.path)

  if (!isPublicPath) {
    // 延迟检查认证状态，避免 Pinia 未初始化
    setTimeout(async () => {
      const { useAuthStore } = await import('@/stores/authStore')
      const authStore = useAuthStore()

      if (!authStore.isLoggedIn) {
        // 未登录访问受保护页面，重定向到登录页
        next('/login')
      } else {
        next()
      }
    }, 0)
  } else if (isPublicPath && to.path === '/login') {
    // 检查是否已登录用户访问登录页
    setTimeout(async () => {
      const { useAuthStore } = await import('@/stores/authStore')
      const authStore = useAuthStore()

      if (authStore.isLoggedIn) {
        // 已登录用户访问登录页，重定向到首页
        next('/')
      } else {
        next()
      }
    }, 0)
  } else {
    next()
  }
})

export default router