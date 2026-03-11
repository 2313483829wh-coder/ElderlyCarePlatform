<template>
  <div>
    <el-tabs v-model="tab" @tab-change="loadData">
      <el-tab-pane label="待处理" name="pending" />
      <el-tab-pane label="全部" name="all" />
    </el-tabs>

    <!-- 健康异常预警 -->
    <div v-if="alerts.length > 0">
      <h3 style="font-size: 18px; font-weight: 600; color: #1d1d1f; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
        <el-icon color="#ff3b30" :size="20"><WarningFilled /></el-icon>
        健康异常预警
        <el-tag type="danger" size="small">{{ alerts.length }}</el-tag>
      </h3>
      <el-table :data="alerts" stripe border>
        <el-table-column prop="community_name" label="社区" width="140" />
        <el-table-column prop="elder_name" label="老人" width="100" />
        <el-table-column prop="level_display" label="级别" width="80">
          <template #default="{ row }">
            <el-tag :type="row.level === 'critical' ? 'danger' : 'warning'" size="small">
              {{ row.level_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" show-overflow-tooltip />
        <el-table-column prop="detail" label="详情" show-overflow-tooltip />
        <el-table-column prop="status_display" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'danger' : 'success'" size="small">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" link type="primary" size="small"
                       @click="resolveAlert(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 无预警提示 -->
    <el-empty v-else description="暂无健康异常预警" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const tab = ref('pending')
const alerts = ref([])

async function loadData() {
  let data = []
  if (tab.value === 'pending') {
    data = await request.get('/alerts/pending/')
  } else {
    const res = await request.get('/alerts/')
    data = res.results || res
  }
  // 只显示健康异常预警
  alerts.value = data.filter(a => a.alert_type === 'health')
}

async function resolveAlert(row) {
  const { value } = await ElMessageBox.prompt('处理备注', '处理预警', {
    inputPlaceholder: '备注（可选）',
    confirmButtonText: '已处理',
  })
  await request.put(`/alerts/${row.id}/resolve/`, { note: value || '' })
  ElMessage.success('已处理')
  loadData()
}

onMounted(loadData)
</script>
