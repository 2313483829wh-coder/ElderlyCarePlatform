import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { Capacitor } from '@capacitor/core'

const STORAGE_API_BASE = 'elder_api_base'

/** 仅老人端（/m 或 App）使用 localStorage 的服务器地址；管理端始终用当前站点 /api */
export function getApiBase() {
  const isElderSide = typeof window !== 'undefined' && (
    window.location.pathname.startsWith('/m') ||
    Capacitor.isNativePlatform()
  )
  if (isElderSide) {
    const saved = localStorage.getItem(STORAGE_API_BASE)
    if (saved != null && saved.trim() !== '') return saved.trim().replace(/\/+$/, '')
  }
  return (import.meta.env.VITE_API_BASE || '/api').replace(/\/+$/, '')
}

export function setApiBase(url) {
  if (url == null || (typeof url === 'string' && url.trim() === '')) {
    localStorage.removeItem(STORAGE_API_BASE)
    return
  }
  localStorage.setItem(STORAGE_API_BASE, url.trim().replace(/\/+$/, ''))
}

const request = axios.create({ baseURL: '/', timeout: 15000 })

let lastNetworkErrorTip = 0
const NETWORK_ERROR_COOLDOWN = 3000

request.interceptors.request.use(config => {
  config.baseURL = getApiBase()
  const token = localStorage.getItem('token') || localStorage.getItem('elder_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
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
          const isElderSide = router.currentRoute?.value?.path?.startsWith('/m') || Capacitor.isNativePlatform()
          msg = isElderSide
            ? '无法连接服务器。请到【设置 → 服务器地址】填写后端 API 地址（例如 http://你的公网IP/api）。'
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
