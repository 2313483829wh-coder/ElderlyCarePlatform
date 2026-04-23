import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { Capacitor } from '@capacitor/core'
import { getPreferences } from './preferences'

/** 老人端（/m 或 App）使用打包时的默认地址；管理端始终用当前站点 /api */
export function getApiBase() {
  const isElderSide = typeof window !== 'undefined' && (
    window.location.pathname.startsWith('/m') ||
    Capacitor.isNativePlatform()
  )
  if (isElderSide) {
    const base = import.meta.env.VITE_API_BASE || ''
    if (base) return base.replace(/\/+$/, '')
  }
  return (import.meta.env.VITE_API_BASE || '/api').replace(/\/+$/, '')
}

const request = axios.create({ baseURL: '/', timeout: 25000 })

let lastNetworkErrorTip = 0
const NETWORK_ERROR_COOLDOWN = 3000

request.interceptors.request.use(config => {
  const base = getApiBase()
  const token = localStorage.getItem('token') || localStorage.getItem('elder_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  // axios 在 url 以 / 开头时会忽略 baseURL，必须手动拼接完整路径
  if (config.url && !config.url.startsWith('http') && base) {
    const path = config.url.startsWith('/') ? config.url : '/' + config.url
    config.url = base.replace(/\/+$/, '') + path
    config.baseURL = ''
  } else {
    config.baseURL = base
  }
  return config
})

request.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401) {
      const isLoginRequest = err.config?.url?.includes?.('/auth/login/')
      if (!isLoginRequest) {
        const isMobile = router.currentRoute?.value?.path?.startsWith('/m')
        localStorage.removeItem('token')
        localStorage.removeItem('elder_token')
        router.push(isMobile ? '/m/settings' : '/login')
      }
    } else {
      const skipTip = err.config?.skipGlobalErrorTip === true
      let msg = err.response?.data?.detail
      if (msg == null && err.response?.data && typeof err.response.data === 'object') {
        msg = err.response.data.message || err.response.data.msg
      }
      if (msg == null) {
        const isNetworkError = !err.response ||
          err.code === 'ECONNREFUSED' ||
          err.code === 'ERR_NETWORK' ||
          (err.message && (err.message.includes('Network Error') || err.message.includes('fetch')))
        if (isNetworkError) {
          msg = getPreferences().language === 'en-US'
            ? 'Unable to connect to the server. Please check your network and try again.'
            : '无法连接服务器，请检查网络或稍后重试。'
          const now = Date.now()
          if (now - lastNetworkErrorTip < NETWORK_ERROR_COOLDOWN) return Promise.reject(err)
          lastNetworkErrorTip = now
        } else {
          msg = err.response?.status ? `请求失败 (${err.response.status})` : '请求失败'
        }
      }
      if (!skipTip) ElMessage.error(msg)
    }
    return Promise.reject(err)
  }
)

export default request
