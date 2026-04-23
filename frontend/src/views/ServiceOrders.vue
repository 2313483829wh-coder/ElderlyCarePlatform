<template>
  <div class="page-shell">
    <div class="page-toolbar">
      <el-select v-model="filters.request_type" clearable placeholder="类型" style="width: 140px">
        <el-option label="服务预约" value="service" />
        <el-option label="紧急求助" value="sos" />
      </el-select>
      <el-select v-model="filters.status" clearable placeholder="状态" style="width: 140px">
        <el-option label="待处理" value="pending" />
        <el-option label="处理中" value="processing" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-input v-model="filters.search" clearable placeholder="搜索老人/标题" style="width: 220px" />
      <el-button type="primary" @click="loadOrders">查询</el-button>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-head">
          <span class="stat-label">待处理</span>
          <span class="stat-hint">需要尽快跟进</span>
        </div>
        <strong>{{ summary.pending || 0 }}</strong>
      </div>
      <div class="stat-card">
        <div class="stat-head">
          <span class="stat-label">处理中</span>
          <span class="stat-hint">已进入服务流程</span>
        </div>
        <strong>{{ summary.processing || 0 }}</strong>
      </div>
      <div class="stat-card">
        <div class="stat-head">
          <span class="stat-label">已完成</span>
          <span class="stat-hint">本次服务已结束</span>
        </div>
        <strong>{{ summary.completed || 0 }}</strong>
      </div>
      <div class="stat-card danger">
        <div class="stat-head">
          <span class="stat-label">紧急求助</span>
          <span class="stat-hint">需优先响应</span>
        </div>
        <strong>{{ summary.sos || 0 }}</strong>
      </div>
    </div>

    <el-table :data="orders" border stripe>
      <el-table-column prop="community_name" label="社区" width="140" />
      <el-table-column prop="elder_name" label="老人" width="100" />
      <el-table-column prop="request_type_display" label="类型" width="100" />
      <el-table-column prop="service_kind_display" label="事项" width="120" />
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column prop="contact_phone" label="联系电话" width="130" />
      <el-table-column label="紧急程度" width="100">
        <template #default="{ row }">
          <el-tag :type="urgencyTagType(row.urgency)">{{ row.urgency_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="提交时间" width="170" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click="openDialog(row)">处理</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="处理工单" width="640px">
      <template v-if="currentOrder">
        <div class="detail-panel">
          <div class="detail-line"><strong>{{ currentOrder.title }}</strong></div>
          <div class="detail-line">{{ currentOrder.elder_name }} · {{ currentOrder.community_name }}</div>
          <div class="detail-line">{{ currentOrder.description || '暂无详细说明' }}</div>
        </div>
        <el-form :model="editForm" label-width="88px">
          <el-form-item label="状态">
            <el-select v-model="editForm.status" style="width: 100%">
              <el-option label="待处理" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          <el-form-item label="处理人">
            <el-input v-model="editForm.handled_by" placeholder="例如：张主任" />
          </el-form-item>
          <el-form-item label="处理反馈">
            <el-input v-model="editForm.response_note" type="textarea" :rows="4" placeholder="填写回访、处理进度或完成说明" />
          </el-form-item>
        </el-form>
      </template>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOrder">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const orders = ref([])
const summary = ref({})
const dialogVisible = ref(false)
const currentOrder = ref(null)
const filters = reactive({ request_type: '', status: '', search: '' })
const editForm = reactive({ status: 'pending', handled_by: '', response_note: '' })

function normalizeList(res) {
  return Array.isArray(res) ? res : (res?.results || [])
}

function statusTagType(status) {
  return { pending: 'warning', processing: 'primary', completed: 'success', cancelled: 'info' }[status] || 'info'
}

function urgencyTagType(urgency) {
  return { normal: 'info', high: 'warning', critical: 'danger' }[urgency] || 'info'
}

async function loadOrders() {
  const params = {}
  if (filters.request_type) params.request_type = filters.request_type
  if (filters.status) params.status = filters.status
  if (filters.search) params.search = filters.search
  const [list, stats] = await Promise.all([
    request.get('/care/service-orders/', { params }),
    request.get('/care/service-orders/summary/', { params, skipGlobalErrorTip: true }),
  ])
  orders.value = normalizeList(list)
  summary.value = stats || {}
}

function openDialog(row) {
  currentOrder.value = row
  editForm.status = row.status
  editForm.handled_by = row.handled_by || ''
  editForm.response_note = row.response_note || ''
  dialogVisible.value = true
}

async function submitOrder() {
  if (!currentOrder.value) return
  await request.patch(`/care/service-orders/${currentOrder.value.id}/`, {
    status: editForm.status,
    handled_by: editForm.handled_by,
    response_note: editForm.response_note,
  })
  ElMessage.success('工单已更新')
  dialogVisible.value = false
  await loadOrders()
}

onMounted(loadOrders)
</script>

<style scoped>
.page-shell { display: grid; gap: 16px; }
.page-toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.stats-row { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.stat-card { background:#fff; border:1px solid #e5e5e7; border-radius:18px; padding:18px; display:flex; flex-direction:column; gap:12px; box-shadow:0 8px 24px rgba(15,23,42,.04); }
.stat-head { display:grid; gap:4px; }
.stat-card strong { font-size:30px; line-height:1; color:#1d1d1f; }
.stat-card.danger strong { color:#d70015; }
.stat-label { color:#1d1d1f; font-size:16px; font-weight:600; }
.stat-hint { color:#8a8a8e; font-size:12px; }
.detail-panel { background:#f5f5f7; border-radius:14px; padding:14px 16px; margin-bottom:16px; }
.detail-line { color:#1d1d1f; line-height:1.7; }
@media (max-width: 1100px) {
  .stats-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
