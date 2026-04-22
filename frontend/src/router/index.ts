import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/views/LayoutView.vue'),
      redirect: '/dashboard',
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue')
        },
        {
          path: 'detection',
          name: 'Detection',
          component: () => import('@/views/DetectionView.vue')
        },
        {
          path: 'history',
          name: 'History',
          component: () => import('@/views/HistoryView.vue')
        },
        {
          path: 'history/:id',
          name: 'HistoryDetail',
          component: () => import('@/views/HistoryDetailView.vue')
        },
        {
          path: 'admin',
          name: 'Admin',
          component: () => import('@/views/AdminView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: 'admin/logs',
          name: 'AuditLogs',
          component: () => import('@/views/AuditLogView.vue'),
          meta: { requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'admin/settings',
          name: 'Settings',
          component: () => import('@/views/SettingsView.vue'),
          meta: { requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('@/views/ProfileView.vue')
        },
        {
          path: '/batch',
          name: 'BatchDetection',
          component: () => import('@/views/BatchDetectionView.vue'),
          meta: { requiresAuth: true }
        }
      ]
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 如果已登录但用户信息为空，先尝试获取
  if (authStore.isLoggedIn && !authStore.userInfo) {
    await authStore.fetchUserInfo()
  }

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresAdmin && authStore.userInfo?.role !== 'admin') {
    next('/dashboard')
  } else {
    next()
  }
})

export default router