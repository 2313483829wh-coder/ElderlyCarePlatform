import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const STORAGE_API_BASE = 'elder_api_base'

export function getApiBase() {
  const saved = localStorage.getItem(STORAGE_API_BASE)
  if (saved != null && saved.trim() !== '') return saved.trim().replace(/\/+$/, '')
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
          msg = '无法连接服务器。请在【设置 → 服务器地址】填写电脑上的后端地址（如 http://192.168.1.100:8000/api），并确保手机与电脑在同一 WiFi。'
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
