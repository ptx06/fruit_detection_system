import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/api/auth'
import { getCurrentUser } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('access_token', newToken)
  }

  function setUserInfo(info: UserInfo | null) {
    userInfo.value = info
  }

  async function fetchUserInfo() {
    if (!token.value) return
    try {
      const info = await getCurrentUser(token.value)
      userInfo.value = info
    } catch (error) {
      // token 无效或过期，清除
      logout()
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
  }

  return { token, userInfo, isLoggedIn, setToken, setUserInfo, fetchUserInfo, logout }
})