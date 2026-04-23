<template>
  <div class="mobile-shell">
    <section class="hero-card">
      <p class="hero-eyebrow">Activity Sign-up</p>
      <h2 class="hero-title">活动报名</h2>
      <p class="hero-subtitle">查看社区活动、在线报名，也能随时查看自己已经报名的活动安排。</p>
      <div v-if="isAuthed" class="hero-stats">
        <div class="stat-pill">
          <span class="stat-label">可报名</span>
          <strong class="stat-value">{{ availableCount }}</strong>
        </div>
        <div class="stat-pill">
          <span class="stat-label">已报名</span>
          <strong class="stat-value">{{ registeredCount }}</strong>
        </div>
      </div>
    </section>

    <section v-if="!isAuthed" class="empty-state">
      <p class="empty-title">登录后可报名社区活动</p>
      <p class="empty-subtitle">进入设置页登录老人账号后，就能查看活动名额并在线报名。</p>
      <button class="login-btn" @click="router.push('/m/settings')">前往登录</button>
    </section>

    <template v-else>
      <section class="filter-bar">
        <button
          class="filter-btn"
          :class="{ active: currentTab === 'available' }"
          @click="currentTab = 'available'"
        >
          可报名
        </button>
        <button
          class="filter-btn"
          :class="{ active: currentTab === 'registered' }"
          @click="currentTab = 'registered'"
        >
          已报名
        </button>
      </section>

      <section v-if="filteredActivities.length" class="card-list">
        <article v-for="item in filteredActivities" :key="item.id" class="activity-card">
          <div class="activity-head">
            <div class="activity-copy">
              <h3 class="activity-title">{{ item.title }}</h3>
              <p class="activity-meta">{{ formatDateTime(item.starts_at) }}<span v-if="item.location"> · {{ item.location }}</span></p>
            </div>
            <span class="status-chip" :class="{ active: item.is_registered }">
              {{ item.is_registered ? '已报名' : '可报名' }}
            </span>
          </div>

          <p class="activity-summary">{{ item.summary || item.content || '暂无活动介绍' }}</p>

          <div class="activity-footer">
            <div class="activity-info">
              <span class="spots-left">{{ item.max_participants ? `剩余名额 ${item.spots_left}` : '名额不限' }}</span>
              <span class="activity-count">已报名 {{ item.registration_count }} 人</span>
            </div>
            <button
              class="action-btn"
              :class="{ secondary: item.is_registered }"
              :disabled="loadingId === item.id || (!item.is_registered && item.max_participants && item.spots_left <= 0)"
              @click="toggleRegistration(item)"
            >
              {{ item.is_registered ? '取消报名' : ((item.max_participants && item.spots_left <= 0) ? '名额已满' : '立即报名') }}
            </button>
          </div>
        </article>
      </section>

      <section v-else class="empty-state">
        <p class="empty-title">{{ currentTab === 'registered' ? '还没有已报名的活动' : '当前还没有可报名的活动' }}</p>
        <p class="empty-subtitle">{{ currentTab === 'registered' ? '报名成功后的活动会显示在这里，方便你随时查看安排。' : '等社区发布新活动后，你就可以在这里报名参加。' }}</p>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const activities = ref([])
const loadingId = ref(null)
const currentTab = ref('available')
const isAuthed = ref(!!localStorage.getItem('elder_token'))

function normalizeList(res) {
  return Array.isArray(res) ? res : (res?.results || [])
}

const registeredActivities = computed(() => activities.value.filter(item => item.is_registered))
const availableActivities = computed(() => activities.value.filter(item => item.is_registered || !item.max_participants || item.spots_left > 0))
const filteredActivities = computed(() => currentTab.value === 'registered' ? registeredActivities.value : availableActivities.value)
const registeredCount = computed(() => registeredActivities.value.length)
const availableCount = computed(() => activities.value.filter(item => !item.is_registered && (!item.max_participants || item.spots_left > 0)).length)

function formatDateTime(value) {
  if (!value) return ''
  const date = new Date(String(value).replace(' ', 'T'))
  if (Number.isNaN(date.getTime())) return value
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${month}-${day} ${hour}:${minute}`
}

async function loadActivities() {
  if (!isAuthed.value) return
  activities.value = normalizeList(await request.get('/care/activities/mobile-list/'))
}

async function toggleRegistration(item) {
  loadingId.value = item.id
  try {
    if (item.is_registered) {
      await request.post('/care/activities/cancel-registration/', { activity_id: item.id })
      ElMessage.success('已取消报名')
    } else {
      await request.post('/care/activities/register/', { activity_id: item.id })
      ElMessage.success('报名成功')
    }
    await loadActivities()
  } finally {
    loadingId.value = null
  }
}

onMounted(() => {
  isAuthed.value = !!localStorage.getItem('elder_token')
  loadActivities()
})
</script>

<style scoped>
.mobile-shell { min-height: calc(100vh - 64px); padding:16px; background: radial-gradient(120% 70% at 15% -5%, rgba(0, 122, 255, 0.08), transparent 55%), radial-gradient(90% 60% at 95% 0%, rgba(52, 199, 89, 0.08), transparent 55%), #f5f5f7; display:grid; gap:14px; }
.hero-card,.activity-card,.empty-state,.filter-bar { background: linear-gradient(145deg, #ffffff 0%, #f7f8fa 100%); border:1px solid rgba(0,0,0,0.08); border-radius:22px; box-shadow:0 12px 28px rgba(0,0,0,0.06); }
.hero-card,.empty-state { padding:18px; }
.activity-card { padding:16px; }
.hero-eyebrow { margin:0 0 4px; font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:#8a8a8e; }
.hero-title { margin:0; font-size:28px; color:#111; }
.hero-subtitle { margin:8px 0 0; font-size:14px; color:#6e6e73; line-height:1.6; }
.hero-stats { display:flex; gap:10px; margin-top:14px; }
.stat-pill { flex:1; padding:10px 12px; border-radius:16px; background:#f2f2f7; display:grid; gap:2px; }
.stat-label { font-size:12px; color:#8a8a8e; }
.stat-value { font-size:18px; color:#111; }
.filter-bar { display:grid; grid-template-columns:1fr 1fr; padding:6px; gap:6px; }
.filter-btn { height:40px; border:none; border-radius:16px; background:transparent; color:#6e6e73; font-size:14px; font-weight:600; }
.filter-btn.active { background:#111; color:#fff; }
.card-list { display:grid; gap:12px; }
.activity-head { display:flex; justify-content:space-between; gap:10px; align-items:flex-start; }
.activity-copy { min-width:0; }
.activity-title { margin:0; font-size:18px; color:#111; }
.activity-meta { margin:6px 0 0; font-size:12px; color:#6e6e73; line-height:1.6; }
.status-chip { padding:5px 10px; border-radius:999px; font-size:11px; font-weight:600; color:#0a84ff; background:rgba(10,132,255,.12); white-space:nowrap; }
.status-chip.active { color:#0a7d3f; background:rgba(10,125,63,.12); }
.activity-summary { margin:10px 0 0; font-size:13px; line-height:1.7; color:#6e6e73; }
.activity-footer { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-top:14px; }
.activity-info { display:grid; gap:4px; }
.spots-left,.activity-count { font-size:12px; color:#8a8a8e; }
.action-btn,.login-btn { border:none; border-radius:12px; padding:10px 14px; font-size:13px; font-weight:700; color:#fff; background:linear-gradient(135deg,#0a84ff,#0071e3); }
.action-btn.secondary { background:#f2f2f7; color:#111; }
.action-btn:disabled { opacity:.55; cursor:not-allowed; }
.empty-title { margin:0; font-size:16px; color:#111; text-align:center; }
.empty-subtitle { margin:8px 0 0; font-size:13px; color:#6e6e73; text-align:center; line-height:1.6; }
.login-btn { width:100%; margin-top:14px; }
</style>
