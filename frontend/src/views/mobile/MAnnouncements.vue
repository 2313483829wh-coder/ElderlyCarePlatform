<template>
  <div class="announcements-page">
    <div class="page-header">
      <button class="back-btn" @click="router.push('/m/chat')" aria-label="返回">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <div>
        <h1 class="page-title">社区公告</h1>
        <p class="page-subtitle">查看活动通知、服务提醒和社区动态</p>
      </div>
    </div>

    <div class="hero-card">
      <div>
        <div class="hero-label">本周关注</div>
        <div class="hero-title">{{ pinnedAnnouncement?.title || '公告实时同步中' }}</div>
        <div class="hero-text">
          {{ pinnedAnnouncement?.summary || '这里会优先展示社区的重要通知和最近活动。' }}
        </div>
      </div>
      <div class="hero-chip">{{ pinnedAnnouncement ? '置顶公告' : '实时提醒' }}</div>
    </div>

    <div class="filter-bar">
      <button
        v-for="item in filters"
        :key="item.value"
        class="filter-chip"
        :class="{ active: activeFilter === item.value }"
        @click="activeFilter = item.value"
      >
        {{ item.label }}
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="4" animated />
    </div>

    <div v-else-if="filteredList.length" class="card-list">
      <article
        v-for="item in filteredList"
        :key="item.id"
        class="announcement-card"
        :class="{ pinned: item.is_pinned }"
      >
        <div class="card-top">
          <div class="meta-group">
            <span class="category">{{ item.category_display }}</span>
            <span v-if="item.is_pinned" class="pin-badge">置顶</span>
          </div>
          <span class="publish-date">{{ formatDate(item.publish_at || item.created_at) }}</span>
        </div>
        <div class="card-title">{{ item.title }}</div>
        <div class="card-summary">{{ item.summary || item.content }}</div>
        <img
          v-if="item.cover_url"
          :src="item.cover_url"
          class="cover-image"
          alt="公告封面"
        />
        <div class="card-footer">
          <span class="audience">{{ item.audience_display }}</span>
          <button class="detail-btn" @click="openDetail(item)">查看详情</button>
        </div>
      </article>
    </div>

    <el-empty v-else description="当前暂无公告" />

    <el-dialog v-model="detailVisible" title="公告详情" width="92%" class="detail-dialog">
      <template v-if="currentItem">
        <div class="detail-meta">
          <span>{{ currentItem.category_display }}</span>
          <span>{{ formatDate(currentItem.publish_at || currentItem.created_at) }}</span>
        </div>
        <h2 class="detail-title">{{ currentItem.title }}</h2>
        <img
          v-if="currentItem.cover_url"
          :src="currentItem.cover_url"
          class="detail-image"
          alt="公告封面"
        />
        <p class="detail-content">{{ currentItem.content }}</p>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const detailVisible = ref(false)
const currentItem = ref(null)
const announcements = ref([])
const activeFilter = ref('all')

const filters = [
  { label: '全部', value: 'all' },
  { label: '活动', value: 'activity' },
  { label: '服务', value: 'service' },
  { label: '提醒', value: 'notice' },
]

const pinnedAnnouncement = computed(() =>
  announcements.value.find(item => item.is_pinned) || announcements.value[0] || null
)

const filteredList = computed(() => {
  if (activeFilter.value === 'all') return announcements.value
  return announcements.value.filter(item => item.category === activeFilter.value)
})

function formatDate(value) {
  if (!value) return ''
  const dt = new Date(value)
  return `${dt.getMonth() + 1}月${dt.getDate()}日 ${String(dt.getHours()).padStart(2, '0')}:${String(dt.getMinutes()).padStart(2, '0')}`
}

function openDetail(item) {
  currentItem.value = item
  detailVisible.value = true
}

async function loadAnnouncements() {
  loading.value = true
  try {
    const res = await request.get('/announcements/mobile/')
    announcements.value = res.results || res || []
  } catch {
    announcements.value = []
    ElMessage.warning('公告暂时加载失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

onMounted(loadAnnouncements)
</script>

<style scoped>
.announcements-page {
  min-height: calc(100vh - 64px);
  background:
    radial-gradient(circle at top right, rgba(60, 60, 67, 0.06), transparent 28%),
    linear-gradient(180deg, #f7f7fa 0%, #ffffff 38%, #fbfbfd 100%);
  padding: 18px 16px 28px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 18px;
}

.back-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  cursor: pointer;
  color: #1d1d1f;
}

.page-title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.04em;
  color: #111827;
}

.page-subtitle {
  margin: 6px 0 0;
  color: #6b7280;
  font-size: 14px;
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  padding: 16px 18px;
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #f7f7f9 100%);
  color: #1d1d1f;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
}

.hero-label {
  font-size: 12px;
  letter-spacing: 0.08em;
  color: #8a8a8e;
  text-transform: uppercase;
}

.hero-title {
  margin-top: 8px;
  font-size: 20px;
  font-weight: 700;
}

.hero-text {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.6;
  color: #6e6e73;
}

.hero-chip {
  align-self: flex-start;
  padding: 6px 10px;
  border-radius: 999px;
  background: #f2f2f7;
  color: #4b5563;
  font-size: 12px;
}

.filter-bar {
  display: flex;
  gap: 8px;
  margin: 14px 0 14px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.filter-chip {
  border: none;
  border-radius: 999px;
  padding: 8px 13px;
  background: rgba(255, 255, 255, 0.92);
  color: #6b7280;
  font-size: 13px;
  box-shadow: 0 5px 14px rgba(15, 23, 42, 0.04);
  cursor: pointer;
  white-space: nowrap;
}

.filter-chip.active {
  background: #111827;
  color: #fff;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.announcement-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 18px;
  padding: 15px;
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
}

.announcement-card.pinned {
  border-color: rgba(245, 158, 11, 0.22);
}

.card-top,
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.meta-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category,
.pin-badge,
.audience {
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.category {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.pin-badge {
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
}

.publish-date {
  font-size: 12px;
  color: #9ca3af;
}

.card-title {
  margin-top: 12px;
  font-size: 18px;
  line-height: 1.4;
  font-weight: 700;
  color: #111827;
}

.card-summary {
  margin-top: 8px;
  color: #4b5563;
  font-size: 13px;
  line-height: 1.6;
}

.cover-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 14px;
  margin-top: 12px;
}

.card-footer {
  margin-top: 14px;
}

.audience {
  background: rgba(17, 24, 39, 0.06);
  color: #4b5563;
}

.detail-btn {
  border: none;
  background: #f2f2f7;
  color: #1d1d1f;
  border-radius: 999px;
  padding: 8px 12px;
  font-size: 13px;
  cursor: pointer;
}

.detail-meta {
  display: flex;
  justify-content: space-between;
  color: #6b7280;
  font-size: 13px;
  margin-bottom: 8px;
}

.detail-title {
  margin: 0 0 16px;
  font-size: 24px;
  color: #111827;
}

.detail-image {
  width: 100%;
  border-radius: 18px;
  max-height: 220px;
  object-fit: cover;
  margin-bottom: 16px;
}

.detail-content {
  white-space: pre-line;
  line-height: 1.8;
  color: #374151;
  margin: 0;
}

.loading-state {
  padding: 8px 0;
}
</style>
