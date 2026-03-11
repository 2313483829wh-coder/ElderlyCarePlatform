import { createRouter, createWebHistory } from 'vue-router'

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
    path: '/m/login',
    component: () => import('@/views/mobile/MLogin.vue'),
    meta: { title: '老人登录' },
  },
  {
    path: '/m',
    component: () => import('@/views/mobile/MLayout.vue'),
    redirect: '/m/home',
    children: [
      {
        path: 'home',
        component: () => import('@/views/mobile/MHome.vue'),
        meta: { title: '健康助手' },
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
  document.title = `${to.meta.title || ''} - 社区养老管理平台`
  const isMobile = to.path.startsWith('/m')
  const loginPath = isMobile ? '/m/login' : '/login'
  const tokenKey = isMobile ? 'elder_token' : 'token'
  
  if (to.path === '/login' || to.path === '/m/login') {
    next()
  } else if (!localStorage.getItem(tokenKey)) {
    next(loginPath)
  } else {
    next()
  }
})

export default router
