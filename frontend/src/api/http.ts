import axios from 'axios'
import { ElMessage, ElLoading } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

export const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求计数器，用于显示全局加载状态
let requestCount = 0
let loadingInstance: any = null

const showLoading = () => {
  requestCount++
  if (requestCount === 1 && !loadingInstance) {
    loadingInstance = ElLoading.service({
      lock: true,
      text: '加载中...',
      background: 'rgba(0, 0, 0, 0.1)',
    })
  }
}

const hideLoading = () => {
  requestCount = Math.max(0, requestCount - 1)
  if (requestCount === 0 && loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

// 请求拦截器：注入 JWT Token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    // 不在登录/注册/验证码接口显示加载
    const noLoadingUrls = ['/auth/login', '/auth/register', '/captcha']
    const isNoLoading = noLoadingUrls.some(url => config.url?.includes(url))
    if (!isNoLoading) {
      showLoading()
    }
    return config
  },
  (error) => {
    hideLoading()
    return Promise.reject(error)
  }
)

// 响应拦截器：统一处理错误
api.interceptors.response.use(
  (response) => {
    hideLoading()
    const data = response.data
    // 业务错误
    if (data && data.code && data.code !== 200) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
    return response
  },
  async (error) => {
    hideLoading()
    const authStore = useAuthStore()
    
    // 网络错误处理
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        ElMessage.error('请求超时，请稍后重试')
      } else if (error.message?.includes('Network Error')) {
        ElMessage.error('网络连接失败，请检查网络')
      } else {
        ElMessage.error('网络请求失败，请稍后重试')
      }
      return Promise.reject(error)
    }
    
    if (error.response?.status === 401) {
      // 尝试刷新 token
      try {
        const refresh = authStore.refreshToken
        if (refresh) {
          const res = await axios.post('/api/v1/auth/refresh', { refresh_token: refresh })
          const newToken = res.data.data.access_token
          authStore.setTokens(newToken, refresh)
          error.config.headers.Authorization = `Bearer ${newToken}`
          return api.request(error.config)
        }
      } catch {
        await authStore.logout()
      }
    }
    
    // FastAPI detail 可能是字符串或对象 {code, message, data}
    const detail = error.response?.data?.detail
    const msg = (typeof detail === 'string' ? detail : detail?.message)
      || error.response?.data?.message
      || '网络请求失败'
    
    // 避免重复显示错误提示（静默处理某些错误）
    const silentErrors = [401, 403]
    if (!silentErrors.includes(error.response?.status)) {
      ElMessage.error(msg)
    }
    
    return Promise.reject(error)
  }
)
