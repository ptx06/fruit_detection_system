import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

// 请求拦截器
client.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
client.interceptors.response.use(
  (response) => {
    if (response.config.responseType === 'blob') {
      return response
    }
    return response
  },
  (error) => {
    console.error('请求错误:', error)  // 添加日志
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    // 其他错误不再弹窗，统一返回 reject
    return Promise.reject(error)
  }
)

export default client