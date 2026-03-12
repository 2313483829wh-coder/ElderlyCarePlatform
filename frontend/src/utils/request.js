import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const baseURL = import.meta.env.VITE_API_BASE || '/api'
const request = axios.create({ baseURL, timeout: 15000 })

request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

request.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401) {
      const isMobile = router.currentRoute?.value?.path?.startsWith('/m')
      localStorage.removeItem('token')
      localStorage.removeItem('elder_token')
      router.push(isMobile ? '/m/settings' : '/login')
    } else {
      ElMessage.error(err.response?.data?.detail || '请求失败')
    }
    return Promise.reject(err)
  }
)

export default request
