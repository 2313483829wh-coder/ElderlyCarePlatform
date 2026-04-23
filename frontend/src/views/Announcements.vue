<template>
  <div class="announcement-page">
    <div class="page-toolbar">
      <div>
        <h2 class="page-title">公告中心</h2>
        <p class="page-subtitle">统一发布社区通知、活动安排和服务提醒</p>
      </div>
      <el-button type="primary" @click="openCreate">新建公告</el-button>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :span="8">
        <div class="stat-card">
          <div class="stat-label">生效公告</div>
          <div class="stat-value">{{ activeCount }}</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-card">
          <div class="stat-label">置顶公告</div>
          <div class="stat-value">{{ pinnedCount }}</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-card">
          <div class="stat-label">本周新增</div>
          <div class="stat-value">{{ weeklyCount }}</div>
        </div>
      </el-col>
    </el-row>

    <el-card shadow="never" class="filter-card">
      <el-form :inline="true">
        <el-form-item label="关键词">
          <el-input v-model="filters.search" placeholder="标题 / 内容" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filters.category" clearable placeholder="全部分类">
            <el-option label="活动" value="activity" />
            <el-option label="服务" value="service" />
            <el-option label="提醒" value="notice" />
            <el-option label="政策" value="policy" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.is_active" clearable placeholder="全部状态">
            <el-option label="生效中" :value="true" />
            <el-option label="已停用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button @click="loadData">筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="announcements" stripe border>
      <el-table-column prop="title" label="标题" min-width="220" />
      <el-table-column prop="category_display" label="分类" width="110" />
      <el-table-column prop="audience_display" label="对象" width="120" />
      <el-table-column label="封面" width="110" align="center">
        <template #default="{ row }">
          <el-image
            v-if="row.cover_url"
            :src="row.cover_url"
            fit="cover"
            style="width: 56px; height: 56px; border-radius: 12px;"
            :preview-src-list="[row.cover_url]"
            preview-teleported
          />
          <span v-else style="color: #999;">无</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="140">
        <template #default="{ row }">
          <el-space>
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '生效中' : '已停用' }}</el-tag>
            <el-tag v-if="row.is_pinned" type="warning">置顶</el-tag>
          </el-space>
        </template>
      </el-table-column>
      <el-table-column prop="publish_at" label="发布时间" width="170" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="toggleStatus(row)">
            {{ row.is_active ? '停用' : '启用' }}
          </el-button>
          <el-button link type="danger" @click="removeRow(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        background
        layout="prev, pager, next"
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        @current-change="val => { page = val; loadData() }"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="isEditing ? '编辑公告' : '新建公告'" width="720px">
      <el-form label-width="96px">
        <el-form-item label="标题">
          <el-input v-model="form.title" maxlength="80" show-word-limit />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="2" maxlength="160" show-word-limit />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" style="width: 100%;">
            <el-option label="活动" value="activity" />
            <el-option label="服务" value="service" />
            <el-option label="提醒" value="notice" />
            <el-option label="政策" value="policy" />
          </el-select>
        </el-form-item>
        <el-form-item label="发布对象">
          <el-select v-model="form.audience" style="width: 100%;">
            <el-option label="全部老人" value="all" />
            <el-option label="高龄老人" value="senior" />
            <el-option label="慢病老人" value="chronic" />
            <el-option label="家属可见" value="family" />
          </el-select>
        </el-form-item>
        <el-form-item label="正文">
          <el-input v-model="form.content" type="textarea" :rows="6" />
        </el-form-item>
        <el-form-item label="封面图片">
          <input type="file" accept="image/*" @change="onFileChange" />
          <div v-if="form.coverPreview || form.cover_url" class="preview-wrap">
            <img :src="form.coverPreview || form.cover_url" alt="封面预览" class="preview-image" />
          </div>
        </el-form-item>
        <el-form-item label="发布时间">
          <el-date-picker
            v-model="form.publish_at"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="立即发布或指定时间"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="附加设置">
          <el-space wrap>
            <el-checkbox v-model="form.is_active">立即生效</el-checkbox>
            <el-checkbox v-model="form.is_pinned">置顶显示</el-checkbox>
          </el-space>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const announcements = ref([])
const dialogVisible = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const total = ref(0)
const pageSize = 10
const page = ref(1)

const filters = reactive({
  search: '',
  category: '',
  is_active: '',
})

const form = reactive({
  title: '',
  summary: '',
  category: 'notice',
  audience: 'all',
  content: '',
  publish_at: '',
  is_active: true,
  is_pinned: false,
  cover_file: null,
  cover_url: '',
  coverPreview: '',
})

const activeCount = computed(() => announcements.value.filter(item => item.is_active).length)
const pinnedCount = computed(() => announcements.value.filter(item => item.is_pinned).length)
const weeklyCount = computed(() => {
  const now = Date.now()
  return announcements.value.filter(item => {
    const created = new Date(item.created_at).getTime()
    return now - created <= 7 * 24 * 60 * 60 * 1000
  }).length
})

function resetForm() {
  if (form.coverPreview) {
    URL.revokeObjectURL(form.coverPreview)
  }
  Object.assign(form, {
    title: '',
    summary: '',
    category: 'notice',
    audience: 'all',
    content: '',
    publish_at: '',
    is_active: true,
    is_pinned: false,
    cover_file: null,
    cover_url: '',
    coverPreview: '',
  })
}

function openCreate() {
  isEditing.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  isEditing.value = true
  editingId.value = row.id
  Object.assign(form, {
    title: row.title,
    summary: row.summary,
    category: row.category,
    audience: row.audience,
    content: row.content,
    publish_at: row.publish_at,
    is_active: row.is_active,
    is_pinned: row.is_pinned,
    cover_file: null,
    cover_url: row.cover_url,
    coverPreview: '',
  })
  dialogVisible.value = true
}

function onFileChange(event) {
  const file = event.target.files?.[0]
  if (form.coverPreview) {
    URL.revokeObjectURL(form.coverPreview)
  }
  form.cover_file = file || null
  form.coverPreview = file ? URL.createObjectURL(file) : ''
}

function buildPayload() {
  const data = new FormData()
  data.append('title', form.title)
  data.append('summary', form.summary)
  data.append('category', form.category)
  data.append('audience', form.audience)
  data.append('content', form.content)
  data.append('is_active', String(form.is_active))
  data.append('is_pinned', String(form.is_pinned))
  if (form.publish_at) data.append('publish_at', form.publish_at)
  if (form.cover_file) data.append('cover_image', form.cover_file)
  return data
}

async function submitForm() {
  if (!form.title.trim() || !form.content.trim()) {
    ElMessage.warning('请填写标题和正文')
    return
  }
  saving.value = true
  try {
    const payload = buildPayload()
    if (isEditing.value && editingId.value) {
      await request.patch(`/announcements/${editingId.value}/`, payload)
    } else {
      await request.post('/announcements/', payload)
    }
    ElMessage.success('公告已保存')
    dialogVisible.value = false
    loadData()
  } finally {
    saving.value = false
  }
}

async function toggleStatus(row) {
  await request.patch(`/announcements/${row.id}/`, {
    is_active: !row.is_active,
  })
  ElMessage.success(row.is_active ? '公告已停用' : '公告已启用')
  loadData()
}

async function removeRow(row) {
  await ElMessageBox.confirm(`确认删除公告“${row.title}”吗？`, '删除公告', {
    type: 'warning',
  })
  await request.delete(`/announcements/${row.id}/`)
  ElMessage.success('已删除')
  loadData()
}

async function loadData() {
  const params = {
    page: page.value,
    search: filters.search || undefined,
    category: filters.category || undefined,
  }
  if (filters.is_active !== '') params.is_active = filters.is_active
  const res = await request.get('/announcements/', { params })
  announcements.value = res.results || []
  total.value = res.count || announcements.value.length
}

function resetFilters() {
  filters.search = ''
  filters.category = ''
  filters.is_active = ''
  page.value = 1
  loadData()
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.announcement-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.page-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #1d1d1f;
}

.page-subtitle {
  margin: 6px 0 0;
  font-size: 14px;
  color: #6e6e73;
}

.stats-row {
  margin: 0;
}

.stat-card,
.filter-card {
  border-radius: 18px;
}

.stat-card {
  padding: 22px;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.stat-label {
  font-size: 14px;
  color: #6e6e73;
}

.stat-value {
  margin-top: 10px;
  font-size: 32px;
  font-weight: 700;
  color: #1d1d1f;
}

.preview-wrap {
  margin-top: 12px;
}

.preview-image {
  width: 120px;
  height: 120px;
  border-radius: 16px;
  object-fit: cover;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.pager {
  display: flex;
  justify-content: flex-end;
}
</style>
