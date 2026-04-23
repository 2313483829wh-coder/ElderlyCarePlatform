<template>
  <div class="page-shell">
    <div class="page-toolbar">
      <el-button type="primary" @click="openDialog()">新增活动</el-button>
    </div>

    <el-table :data="activities" border stripe>
      <el-table-column prop="title" label="活动名称" min-width="160" />
      <el-table-column prop="location" label="地点" width="160" />
      <el-table-column prop="starts_at" label="开始时间" width="180" />
      <el-table-column prop="ends_at" label="结束时间" width="180" />
      <el-table-column prop="max_participants" label="人数上限" width="100" />
      <el-table-column prop="registration_count" label="已报名" width="90" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <div class="action-cell">
            <el-button text type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button text type="primary" @click="viewRegistrations(row)">报名名单</el-button>
            <el-button text type="danger" @click="removeActivity(row)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑活动' : '新增活动'" width="720px">
      <el-form :model="form" label-width="88px">
        <el-form-item label="活动名称"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="活动摘要"><el-input v-model="form.summary" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="活动地点"><el-input v-model="form.location" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="人数上限"><el-input-number v-model="form.max_participants" :min="1" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="开始时间"><el-date-picker v-model="form.starts_at" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="结束时间"><el-date-picker v-model="form.ends_at" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="活动状态"><el-switch v-model="form.is_active" /></el-form-item>
        <el-form-item label="活动介绍"><el-input v-model="form.content" type="textarea" :rows="5" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitActivity">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="registrationDialogVisible" title="报名列表" width="640px">
      <el-table :data="registrations" border stripe>
        <el-table-column prop="elder_name" label="老人" />
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="notes" label="备注" />
        <el-table-column prop="created_at" label="报名时间" width="180" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const activities = ref([])
const registrations = ref([])
const dialogVisible = ref(false)
const registrationDialogVisible = ref(false)
const form = reactive({
  id: null, title: '', summary: '', content: '', location: '',
  starts_at: '', ends_at: '', max_participants: 30, is_active: true,
})

function normalizeList(res) { return Array.isArray(res) ? res : (res?.results || []) }

async function loadActivities() {
  activities.value = normalizeList(await request.get('/care/activities/'))
}

function resetForm() {
  Object.assign(form, { id: null, title: '', summary: '', content: '', location: '', starts_at: '', ends_at: '', max_participants: 30, is_active: true })
}

function openDialog(row = null) {
  if (!row) {
    resetForm()
  } else {
    Object.assign(form, { ...row })
  }
  dialogVisible.value = true
}

async function submitActivity() {
  if (!form.title.trim() || !form.starts_at) {
    ElMessage.warning('请填写活动名称和开始时间')
    return
  }
  const payload = {
    title: form.title, summary: form.summary, content: form.content, location: form.location,
    starts_at: form.starts_at, ends_at: form.ends_at || null, max_participants: form.max_participants,
    is_active: form.is_active,
  }
  if (form.id) {
    await request.patch(`/care/activities/${form.id}/`, payload)
  } else {
    await request.post('/care/activities/', payload)
  }
  ElMessage.success('活动已保存')
  dialogVisible.value = false
  await loadActivities()
}

async function viewRegistrations(row) {
  registrations.value = normalizeList(await request.get(`/care/activities/${row.id}/registrations/`, { skipGlobalErrorTip: true }))
  registrationDialogVisible.value = true
}

async function removeActivity(row) {
  await ElMessageBox.confirm(`确定删除活动「${row.title}」吗？`, '提示', { type: 'warning' })
  await request.delete(`/care/activities/${row.id}/`)
  ElMessage.success('已删除')
  await loadActivities()
}

onMounted(loadActivities)
</script>

<style scoped>
.page-shell { display: grid; gap: 16px; }
.page-toolbar { display:flex; justify-content:flex-end; }
.action-cell { display:flex; align-items:center; gap:6px; flex-wrap:wrap; }
</style>
