import { createRouter, createWebHistory } from 'vue-router'
import { Capacitor } from '@capacitor/core'

const routes = [
  {
    path: '/login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/',
    component: () => import('@/layout/Layout.vue'),
    redirect: '/communities',
    children: [
      {
        path: 'communities',
        component: () => import('@/views/Communities.vue'),
        meta: { title: '社区列表' },
      },
      {
        path: 'community/:id',
        component: () => import('@/views/CommunityDetail.vue'),
        meta: { title: '社区详情' },
      },
      {
        path: 'elder/:id',
        component: () => import('@/views/ElderDetail.vue'),
        meta: { title: '老人详情' },
      },
      {
        path: 'checkup',
        component: () => import('@/views/Checkup.vue'),
        meta: { title: '体检管理' },
      },
      {
        path: 'checkup/elder/:elderId',
        component: () => import('@/views/CheckupDetail.vue'),
        meta: { title: '体检记录' },
      },
      {
        path: 'alerts',
        component: () => import('@/views/Alerts.vue'),
        meta: { title: '预警中心' },
      },
      {
        path: 'elder/:id/health',
        component: () => import('@/views/ElderHealth.vue'),
        meta: { title: '健康详情' },
      },
    ],
  },
  {
    path: '/m',
    component: () => import('@/views/mobile/MLayout.vue'),
    redirect: '/m/chat',
    children: [
      {
        path: 'chat',
        component: () => import('@/views/mobile/MChat.vue'),
        meta: { title: '健康助手' },
      },
      {
        path: 'settings',
        component: () => import('@/views/mobile/MPerson.vue'),
        meta: { title: '设置' },
      },
      {
        path: 'account',
        component: () => import('@/views/mobile/MAccount.vue'),
        meta: { title: '账号管理' },
      },
      {
        path: 'history',
        component: () => import('@/views/mobile/MHistory.vue'),
        meta: { title: '历史记录' },
      },
      {
        path: 'checkup',
        component: () => import('@/views/mobile/MCheckup.vue'),
        meta: { title: '体检报告' },
      },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  // 老人端 App：打开时直接进入 /m/chat
  if (to.path === '/' && Capacitor.isNativePlatform()) {
    next('/m/chat')
    return
  }
  document.title = `${to.meta.title || ''} - 社区养老管理平台`
  const isMobile = to.path.startsWith('/m')
  const loginPath = isMobile ? '/m/settings' : '/login'
  const tokenKey = isMobile ? 'elder_token' : 'token'
  
  // 老人端：允许游客进入对话页、设置、账号管理
  if (to.path === '/login' || to.path === '/m/settings' || to.path === '/m/chat' || to.path === '/m/account') {
    next()
  } else if (!localStorage.getItem(tokenKey)) {
    next(loginPath)
  } else {
    next()
  }
})

export default router
