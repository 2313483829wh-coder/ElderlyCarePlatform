<template>
  <div class="page-shell">
    <div class="page-toolbar">
      <el-select v-model="filters.elder" clearable filterable placeholder="选择老人" style="width: 220px">
        <el-option v-for="item in elders" :key="item.id" :label="`${item.name} · ${item.community_name}`" :value="item.id" />
      </el-select>
      <el-select v-model="filters.is_active" clearable placeholder="状态" style="width: 120px">
        <el-option label="启用" :value="true" />
        <el-option label="停用" :value="false" />
      </el-select>
      <el-button @click="loadPlans">查询</el-button>
      <el-button type="primary" @click="openDialog()">新增用药计划</el-button>
    </div>

    <el-table :data="plans" border stripe>
      <el-table-column prop="elder_name" label="老人" width="120" />
      <el-table-column prop="community_name" label="社区" width="140" />
      <el-table-column prop="medicine_name" label="药品" width="150" />
      <el-table-column prop="dosage" label="剂量" width="100" />
      <el-table-column prop="frequency" label="频次" width="120" />
      <el-table-column prop="schedule_time" label="提醒时间" width="140" />
      <el-table-column prop="instructions" label="说明" min-width="180" show-overflow-tooltip />
      <el-table-column prop="last_taken_at" label="最近确认服药" width="170" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <div class="action-cell">
            <el-button text type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button text type="danger" @click="removePlan(row)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑用药计划' : '新增用药计划'" width="680px">
      <el-form :model="form" label-width="92px">
        <el-form-item label="老人">
          <el-select v-model="form.elder" filterable style="width: 100%" placeholder="请选择老人">
            <el-option v-for="item in elders" :key="item.id" :label="`${item.name} · ${item.community_name}`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="药品名称"><el-input v-model="form.medicine_name" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="剂量"><el-input v-model="form.dosage" placeholder="例如：1片" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="频次"><el-input v-model="form.frequency" placeholder="例如：每日2次" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="提醒时间"><el-input v-model="form.schedule_time" placeholder="例如：08:00 / 20:00" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="状态"><el-switch v-model="form.is_active" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="开始日期"><el-date-picker v-model="form.start_date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="结束日期"><el-date-picker v-model="form.end_date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="服药说明"><el-input v-model="form.instructions" type="textarea" :rows="4" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPlan">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const plans = ref([])
const elders = ref([])
const dialogVisible = ref(false)
const filters = reactive({ elder: '', is_active: '' })
const form = reactive({
  id: null,
  elder: null,
  medicine_name: '',
  dosage: '',
  frequency: '',
  schedule_time: '',
  instructions: '',
  start_date: '',
  end_date: '',
  is_active: true,
})

function normalizeList(res) { return Array.isArray(res) ? res : (res?.results || []) }

async function loadElders() {
  elders.value = normalizeList(await request.get('/auth/elders/', { params: { is_active: true } }))
}

async function loadPlans() {
  const params = {}
  if (filters.elder) params.elder = filters.elder
  if (filters.is_active !== '') params.is_active = filters.is_active
  plans.value = normalizeList(await request.get('/care/medications/', { params }))
}

function resetForm() {
  Object.assign(form, {
    id: null, elder: null, medicine_name: '', dosage: '', frequency: '',
    schedule_time: '', instructions: '', start_date: '', end_date: '', is_active: true,
  })
}

function openDialog(row = null) {
  if (!row) {
    resetForm()
  } else {
    Object.assign(form, {
      id: row.id,
      elder: row.elder,
      medicine_name: row.medicine_name,
      dosage: row.dosage,
      frequency: row.frequency,
      schedule_time: row.schedule_time,
      instructions: row.instructions,
      start_date: row.start_date,
      end_date: row.end_date,
      is_active: row.is_active,
    })
  }
  dialogVisible.value = true
}

async function submitPlan() {
  if (!form.elder || !form.medicine_name.trim()) {
    ElMessage.warning('请先选择老人并填写药品名称')
    return
  }
  const payload = {
    elder: form.elder,
    medicine_name: form.medicine_name,
    dosage: form.dosage,
    frequency: form.frequency,
    schedule_time: form.schedule_time,
    instructions: form.instructions,
    start_date: form.start_date || null,
    end_date: form.end_date || null,
    is_active: form.is_active,
  }
  if (form.id) {
    await request.patch(`/care/medications/${form.id}/`, payload)
  } else {
    await request.post('/care/medications/', payload)
  }
  ElMessage.success('用药计划已保存')
  dialogVisible.value = false
  await loadPlans()
}

async function removePlan(row) {
  await ElMessageBox.confirm(`确定删除 ${row.medicine_name} 的用药计划吗？`, '提示', { type: 'warning' })
  await request.delete(`/care/medications/${row.id}/`)
  ElMessage.success('已删除')
  await loadPlans()
}

onMounted(async () => {
  await loadElders()
  await loadPlans()
})
</script>

<style scoped>
.page-shell { display: grid; gap: 16px; }
.page-toolbar { display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
.action-cell { display:flex; align-items:center; gap:6px; flex-wrap:wrap; }
</style>
