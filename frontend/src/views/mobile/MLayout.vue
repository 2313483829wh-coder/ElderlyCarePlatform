<template>
  <div class="ds-app">
    <header v-if="route.path !== '/m/settings' && route.path !== '/m/account'" class="ds-header">
      <div v-if="route.path !== '/m/settings'" class="ds-hamburger" @click="drawerVisible = true">
        <el-icon :size="24"><Fold /></el-icon>
      </div>
      <h1 v-if="route.path !== '/m/settings'" class="ds-title">健康助手</h1>
      <div class="ds-header-spacer"></div>
      <button v-if="route.path !== '/m/settings'" class="ds-newchat" :disabled="!isAuthed" @click="newChatFromTop" :title="isAuthed ? '新建对话' : '登录后可新建对话'">
        <el-icon :size="20"><Plus /></el-icon>
      </button>
    </header>

    <main class="ds-main">
      <router-view :key="$route.fullPath" />
    </main>

    <el-drawer
      v-model="drawerVisible"
      title="历史对话"
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
        <div class="guest-title">游客模式</div>
        <div class="guest-desc">
          你可以直接在首页和 AI 对话；登录后可上报健康数据、保存历史对话、创建新对话。
        </div>
        <button class="guest-btn" @click="goPerson">去设置 → 账号管理 登录/注册</button>
      </div>

      <div v-if="isAuthed" class="drawer-footer">
        <div class="footer-item" @click="goTo('/m/history')">
          <el-icon><Document /></el-icon>
          <span>我的健康记录</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
        <div class="footer-item" @click="goTo('/m/checkup')">
          <el-icon><Notebook /></el-icon>
          <span>我的体检报告</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
        <div class="footer-item" @click="goPerson">
          <el-icon><User /></el-icon>
          <span>设置</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
      </div>

      <!-- 长按菜单 -->
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
import { Fold, User, Plus, ArrowRight, Document, Notebook } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()
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
provide('setCurrentSession', (id) => { currentSessionId.value = id })
provide('isAuthed', isAuthed)
provide('refreshAuth', refreshAuth)

async function loadSessions() {
  try {
    sessions.value = await request.get('/ai/sessions/')
  } catch (e) {
    console.error('加载会话失败', e)
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
  const s = sessions.value.find((x) => x.id === id)
  if (!s) return
  longPressTimer.value = setTimeout(() => {
    longPressTarget.value = id
    menuSession.value = s
    longPressTimer.value = null
  }, 500)
}

function onSessionTouchEnd() {
  if (longPressTimer.value) {
    clearTimeout(longPressTimer.value)
    longPressTimer.value = null
  }
}

function openSessionMenu(s) {
  menuSession.value = s
  longPressTarget.value = s.id
}

function closeSessionMenu() {
  menuSession.value = null
  longPressTarget.value = null
}

async function doDeleteSession() {
  const s = menuSession.value
  if (!s) return
  if (!confirm('确定删除该对话？')) return
  try {
    await request.delete('/ai/session-delete/', { params: { session_id: s.id } })
    const wasCurrent = currentSessionId.value === s.id
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
    alert('删除失败')
  }
  closeSessionMenu()
}

async function doRenameSession() {
  const s = menuSession.value
  if (!s) return
  const name = prompt('输入新名称', s.title || '健康咨询')
  if (name == null || name.trim() === '') {
    closeSessionMenu()
    return
  }
  try {
    await request.patch('/ai/session-update/', { session_id: s.id, title: name.trim() })
    const idx = sessions.value.findIndex((x) => x.id === s.id)
    if (idx >= 0) sessions.value[idx].title = name.trim()
  } catch (e) {
    alert('重命名失败')
  }
  closeSessionMenu()
}

async function doPinSession() {
  const s = menuSession.value
  if (!s) return
  try {
    await request.patch('/ai/session-update/', { session_id: s.id, is_pinned: !s.is_pinned })
    const idx = sessions.value.findIndex((x) => x.id === s.id)
    if (idx >= 0) sessions.value[idx].is_pinned = !s.is_pinned
    loadSessions()
  } catch (e) {
    alert('操作失败')
  }
  closeSessionMenu()
}

onMounted(() => {
  if (isAuthed.value) loadSessions()
})
// 路由变化时同步 auth 状态，确保登录后跳转时子组件拿到最新 isAuthed
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
  z-index: 3000;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.session-menu {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 16px 16px 0 0;
  padding: 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}

.session-menu .menu-btn {
  display: block;
  width: 100%;
  padding: 14px;
  margin-bottom: 8px;
  border: none;
  border-radius: 12px;
  background: #f2f2f7;
  color: #1d1d1f;
  font-size: 16px;
  cursor: pointer;
}

.session-menu .menu-btn.danger {
  background: #fff5f5;
  color: #d70015;
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
  padding: 12px 14px;
  background: #111111;
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
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

.footer-item.danger {
  color: #d70015;
}

.footer-item.danger .el-icon {
  color: #d70015;
}

:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 16px;
  color: #1d1d1f;
  border-bottom: 1px solid rgba(0,0,0,0.08);
}

:deep(.el-drawer__body) {
  background: #ffffff;
  padding: 8px 8px 0;
}

:deep(.el-drawer__header-title) {
  color: #1d1d1f;
}
</style>
