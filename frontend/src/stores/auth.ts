import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/http'
import router from '@/router'

interface UserInfo {
  id: number
  username: string
  real_name: string
  role: string
  enterprise_id: number | null
  must_change_password: boolean
  language: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('zjfl_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('zjfl_refresh_token'))
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'platform_admin')
  const isMediator = computed(() => user.value?.role === 'mediator')
  const isEnterpriseUser = computed(() =>
    ['enterprise_admin', 'legal', 'salesperson'].includes(user.value?.role || '')
  )

  function setTokens(access: string, refresh: string) {
    token.value = access
    refreshToken.value = refresh
    localStorage.setItem('zjfl_token', access)
    localStorage.setItem('zjfl_refresh_token', refresh)
  }

  async function login(loginField: string, password: string, captchaToken: string, captchaCode: string) {
    const res = await api.post('/api/v1/auth/login', {
      email: loginField,
      password,
      captcha_id: captchaToken,
      captcha_code: captchaCode,
    })
    const data = res.data.data
    // refresh_token 在演示模式下可能为空，兼容处理
    setTokens(data.access_token, data.refresh_token || '')
    user.value = data.user
    return data
  }

  async function fetchCurrentUser() {
    try {
      const res = await api.get('/api/v1/auth/me')
      user.value = res.data.data
    } catch {
      await logout()
    }
  }

  async function logout() {
    try {
      await api.post('/api/v1/auth/logout')
    } catch {}
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('zjfl_token')
    localStorage.removeItem('zjfl_refresh_token')
    router.push('/auth/login')
  }

  return {
    token,
    refreshToken,
    user,
    isLoggedIn,
    isAdmin,
    isMediator,
    isEnterpriseUser,
    login,
    fetchCurrentUser,
    logout,
    setTokens,
  }
})
