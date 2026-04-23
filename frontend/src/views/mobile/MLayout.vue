<template>
  <div class="ds-app">
    <header v-if="route.path !== '/m/settings' && route.path !== '/m/account'" class="ds-header">
      <div v-if="route.path !== '/m/settings'" class="ds-hamburger" @click="drawerVisible = true">
        <el-icon :size="24"><Fold /></el-icon>
      </div>
      <h1 v-if="route.path !== '/m/settings'" class="ds-title">{{ t('healthAssistant') }}</h1>
      <div class="ds-header-spacer"></div>
      <button
        v-if="route.path !== '/m/settings'"
        class="ds-newchat"
        :disabled="!isAuthed"
        @click="newChatFromTop"
        :title="isAuthed ? '新建对话' : '登录后可新建对话'"
      >
        <el-icon :size="20"><Plus /></el-icon>
      </button>
    </header>

    <main class="ds-main">
      <router-view :key="$route.fullPath" />
    </main>

    <el-drawer
      v-model="drawerVisible"
      :title="t('historyChats')"
      direction="ltr"
      size="85%"
      class="history-drawer"
    >
      <div v-if="isAuthed" class="session-list">
        <div
          v-for="s in sessions"
          :key="s.id"
          class="session-item"
          :class="{ active: s.id === currentSessionId, pinned: s.is_pinned }"
          @click="longPressTarget === s.id ? null : switchSession(s.id)"
          @touchstart="onSessionTouchStart($event, s.id)"
          @touchend="onSessionTouchEnd"
          @touchmove="onSessionTouchEnd"
          @contextmenu.prevent="openSessionMenu(s)"
        >
          <span class="session-title">{{ s.title }}</span>
          <span class="session-date">{{ formatDate(s.updated_at) }}</span>
        </div>
        <div v-if="!sessions.length" class="empty-sessions">暂无历史对话</div>
      </div>

      <div v-else class="guest-drawer">
        <div class="guest-title">{{ t('guestMode') }}</div>
        <div class="guest-desc">{{ t('guestDesc') }}</div>
        <button class="guest-btn" @click="goPerson">{{ t('goAccount') }}</button>
      </div>

      <div v-if="isAuthed" class="drawer-footer">
        <div class="footer-item" @click="goTo('/m/history')">
          <el-icon><Document /></el-icon>
          <span>{{ t('myHealthRecords') }}</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
        <div class="footer-item" @click="goTo('/m/service')">
          <el-icon><Calendar /></el-icon>
          <span>服务预约</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
        <div class="footer-item" @click="goTo('/m/sos')">
          <el-icon><Warning /></el-icon>
          <span>紧急求助</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
        <div class="footer-item" @click="goTo('/m/medication')">
          <el-icon><FirstAidKit /></el-icon>
          <span>我的用药</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
        <div class="footer-item" @click="goTo('/m/checkup')">
          <el-icon><Notebook /></el-icon>
          <span>{{ t('myCheckupReports') }}</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
        <div class="footer-item" @click="goTo('/m/announcements')">
          <el-icon><Bell /></el-icon>
          <span>社区公告</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
        <div class="footer-item" @click="goTo('/m/activities')">
          <el-icon><Flag /></el-icon>
          <span>活动报名</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
        <div class="footer-item" @click="goPerson">
          <el-icon><User /></el-icon>
          <span>{{ t('settings') }}</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
      </div>

      <Teleport to="body">
        <div v-if="menuSession" class="session-menu-overlay" @click.self="closeSessionMenu">
          <div class="session-menu">
            <button class="menu-btn" @click="doPinSession">{{ menuSession.is_pinned ? '取消置顶' : '置顶' }}</button>
            <button class="menu-btn" @click="doRenameSession">重命名</button>
            <button class="menu-btn danger" @click="doDeleteSession">删除</button>
            <button class="menu-btn" @click="closeSessionMenu">取消</button>
          </div>
        </div>
      </Teleport>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, provide, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Fold, User, Plus, ArrowRight, Document, Notebook, Bell, Calendar, Warning, FirstAidKit, Flag } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { useMobileI18n } from '@/utils/mobileI18n'

const router = useRouter()
const route = useRoute()
const { t } = useMobileI18n()
const drawerVisible = ref(false)
const sessions = ref([])
const currentSessionId = ref(null)
const isAuthed = ref(!!localStorage.getItem('elder_token'))
const longPressTarget = ref(null)
const longPressTimer = ref(null)
const menuSession = ref(null)

function refreshAuth() {
  isAuthed.value = !!localStorage.getItem('elder_token')
  if (isAuthed.value) loadSessions()
}

provide('sessions', sessions)
provide('currentSessionId', currentSessionId)
provide('refreshSessions', loadSessions)
provide('setCurrentSession', id => { currentSessionId.value = id })
provide('isAuthed', isAuthed)
provide('refreshAuth', refreshAuth)

async function loadSessions() {
  try {
    sessions.value = await request.get('/ai/sessions/')
  } catch (e) {
    ElMessage.error('加载历史对话失败，请稍后重试')
  }
}

function formatDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const day = String(dt.getDate()).padStart(2, '0')
  const h = String(dt.getHours()).padStart(2, '0')
  const min = String(dt.getMinutes()).padStart(2, '0')
  const sec = String(dt.getSeconds()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}:${sec}`
}

function switchSession(id) {
  if (!isAuthed.value) return
  currentSessionId.value = id
  router.push({ path: '/m/chat', query: { session: id } })
  drawerVisible.value = false
}

function newChatFromTop() {
  if (!isAuthed.value) {
    router.push('/m/settings')
    return
  }
  currentSessionId.value = null
  router.push({ path: '/m/chat', query: { new: Date.now() } })
}

function goPerson() {
  router.push('/m/settings')
  drawerVisible.value = false
}

function goTo(path) {
  router.push(path)
  drawerVisible.value = false
}

function onSessionTouchStart(ev, id) {
  longPressTarget.value = null
  if (longPressTimer.value) clearTimeout(longPressTimer.value)
  const session = sessions.value.find(item => item.id === id)
  if (!session) return
  longPressTimer.value = setTimeout(() => {
    longPressTarget.value = id
    menuSession.value = session
    longPressTimer.value = null
  }, 500)
}

function onSessionTouchEnd() {
  if (longPressTimer.value) {
    clearTimeout(longPressTimer.value)
    longPressTimer.value = null
  }
}

function openSessionMenu(session) {
  menuSession.value = session
  longPressTarget.value = session.id
}

function closeSessionMenu() {
  menuSession.value = null
  longPressTarget.value = null
}

async function doDeleteSession() {
  const session = menuSession.value
  if (!session) return
  try {
    await ElMessageBox.confirm('确定删除该对话？', '提示', { type: 'warning' })
    await request.delete('/ai/session-delete/', { params: { session_id: session.id } })
    const wasCurrent = currentSessionId.value === session.id
    if (wasCurrent) currentSessionId.value = null
    await loadSessions()
    if (sessions.value.length === 0) {
      const res = await request.post('/ai/sessions/new/')
      currentSessionId.value = res.session_id
      await loadSessions()
      drawerVisible.value = false
      router.push({ path: '/m/chat', query: { session: res.session_id } })
    } else if (wasCurrent) {
      router.push('/m/chat')
    }
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') ElMessage.error('删除失败，请稍后重试')
  }
  closeSessionMenu()
}

async function doRenameSession() {
  const session = menuSession.value
  if (!session) return
  try {
    const { value } = await ElMessageBox.prompt('输入新名称', '重命名对话', {
      inputValue: session.title || '健康咨询',
      inputPlaceholder: '请输入对话名称',
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValidator: value => (value || '').trim() ? true : '请输入对话名称',
    })
    const name = (value || '').trim()
    if (!name) {
      closeSessionMenu()
      return
    }
    await request.patch('/ai/session-update/', { session_id: session.id, title: name })
    const idx = sessions.value.findIndex(item => item.id === session.id)
    if (idx >= 0) sessions.value[idx].title = name
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') ElMessage.error('重命名失败，请稍后重试')
  }
  closeSessionMenu()
}

async function doPinSession() {
  const session = menuSession.value
  if (!session) return
  try {
    await request.patch('/ai/session-update/', { session_id: session.id, is_pinned: !session.is_pinned })
    const idx = sessions.value.findIndex(item => item.id === session.id)
    if (idx >= 0) sessions.value[idx].is_pinned = !session.is_pinned
    await loadSessions()
  } catch (e) {
    ElMessage.error('操作失败，请稍后重试')
  }
  closeSessionMenu()
}

onMounted(() => {
  if (isAuthed.value) loadSessions()
})

watch(() => route.path, () => { refreshAuth() })
</script>

<style scoped>
.ds-app {
  min-height: 100vh;
  background: #ffffff;
  padding-bottom: 0;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", sans-serif;
  max-width: 500px;
  margin: 0 auto;
}

.ds-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.ds-header-spacer {
  flex: 1;
}

.ds-newchat {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: #ffffff;
  color: #1d1d1f;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.ds-newchat:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.ds-newchat:active {
  transform: scale(0.98);
  background: #f2f2f7;
}

.ds-hamburger {
  padding: 8px;
  margin: -8px 8px -8px -8px;
  color: #1d1d1f;
  cursor: pointer;
}

.ds-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
}

.ds-main {
  min-height: calc(100vh - 64px);
}

.session-list {
  padding: 8px 0;
}

.session-item {
  padding: 14px 16px;
  border-radius: 12px;
  margin-bottom: 4px;
  cursor: pointer;
}

.session-item:hover,
.session-item.active {
  background: rgba(0, 0, 0, 0.06);
}

.session-item.pinned {
  border-left: 3px solid #111111;
}

.session-menu-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 0 0 40px;
}

.session-menu {
  background: #fff;
  border-radius: 16px;
  padding: 12px;
  width: calc(100% - 32px);
  max-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.session-menu .menu-btn {
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: #f2f2f7;
  font-size: 16px;
  color: #1d1d1f;
  cursor: pointer;
}

.session-menu .menu-btn.danger {
  background: #fef0f0;
  color: #d70015;
}

.session-title {
  display: block;
  font-size: 15px;
  color: #1d1d1f;
}

.session-date {
  font-size: 12px;
  color: #6e6e73;
  margin-top: 4px;
  display: block;
}

.empty-sessions {
  text-align: center;
  color: #6e6e73;
  padding: 40px;
}

.guest-drawer {
  padding: 12px 8px 18px;
}

.guest-title {
  font-size: 16px;
  font-weight: 700;
  color: #1d1d1f;
  margin-bottom: 8px;
}

.guest-desc {
  font-size: 14px;
  line-height: 1.6;
  color: #6e6e73;
  margin-bottom: 14px;
}

.guest-btn {
  width: 100%;
  height: 40px;
  background: #111111;
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.guest-btn:active {
  transform: scale(0.99);
}

.drawer-footer {
  position: sticky;
  bottom: 0;
  background: #ffffff;
  padding: 10px 0 6px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 12px;
  border-radius: 12px;
  cursor: pointer;
  color: #1d1d1f;
  font-size: 15px;
}

.footer-item:hover {
  background: rgba(0, 0, 0, 0.04);
}

.footer-item .el-icon {
  color: #1d1d1f;
  font-size: 18px;
}

.footer-item .arrow {
  margin-left: auto;
  color: #6e6e73;
  font-size: 14px;
}

:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 16px;
  color: #1d1d1f;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

:deep(.el-drawer__body) {
  background: #ffffff;
  padding: 8px 8px 0;
}

:deep(.el-drawer__header-title) {
  color: #1d1d1f;
}
</style>
