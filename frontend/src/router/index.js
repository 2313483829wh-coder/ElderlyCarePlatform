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
        path: 'announcements',
        component: () => import('@/views/Announcements.vue'),
        meta: { title: '公告中心' },
      },
      {
        path: 'service-orders',
        component: () => import('@/views/ServiceOrders.vue'),
        meta: { title: '工单中心' },
      },
      {
        path: 'medications',
        component: () => import('@/views/MedicationAdmin.vue'),
        meta: { title: '用药管理' },
      },
      {
        path: 'activities',
        component: () => import('@/views/Activities.vue'),
        meta: { title: '活动管理' },
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
      {
        path: 'announcements',
        component: () => import('@/views/mobile/MAnnouncements.vue'),
        meta: { title: '社区公告' },
      },
      {
        path: 'activities',
        component: () => import('@/views/mobile/MActivities.vue'),
        meta: { title: '活动报名' },
      },
      {
        path: 'service',
        component: () => import('@/views/mobile/MService.vue'),
        meta: { title: '服务预约' },
      },
      {
        path: 'sos',
        component: () => import('@/views/mobile/MSOS.vue'),
        meta: { title: '紧急求助' },
      },
      {
        path: 'medication',
        component: () => import('@/views/mobile/MMedication.vue'),
        meta: { title: '我的用药' },
      },
    ],
  },
]

const router = createRouter({ history: createWebHistory(import.meta.env.BASE_URL), routes })

router.beforeEach((to, from, next) => {
  if (Capacitor.isNativePlatform() && !to.path.startsWith('/m')) {
    next('/m/chat')
    return
  }
  document.title = `${to.meta.title || ''} - 社区养老管理平台`
  const isMobile = to.path.startsWith('/m')
  const loginPath = isMobile ? '/m/settings' : '/login'
  const tokenKey = isMobile ? 'elder_token' : 'token'

  if (
    to.path === '/login' ||
    to.path === '/m/settings' ||
    to.path === '/m/chat' ||
    to.path === '/m/account' ||
    to.path === '/m/announcements' ||
    to.path === '/m/activities' ||
    to.path === '/m/service' ||
    to.path === '/m/sos' ||
    to.path === '/m/medication'
  ) {
    next()
  } else if (!localStorage.getItem(tokenKey)) {
    next(loginPath)
  } else {
    next()
  }
})

export default router
