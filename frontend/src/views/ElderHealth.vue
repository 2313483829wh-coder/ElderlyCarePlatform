<template>
  <div>
    <el-button text icon="ArrowLeft" @click="$router.back()">返回</el-button>
    <h3 style="display: inline; margin-left: 8px;">{{ elderName }} — 近期健康数据</h3>

    <el-table :data="records" stripe border style="margin-top: 16px;">
      <el-table-column prop="date" label="日期" width="120" />
      <el-table-column prop="heart_rate" label="心跳" width="90" align="center">
        <template #default="{ row }">
          <span :style="{ color: isAnomaly(row.heart_rate, 50, 120) ? '#f56c6c' : '' , fontWeight: isAnomaly(row.heart_rate, 50, 120) ? 700 : 400 }">
            {{ row.heart_rate ?? '—' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="blood_oxygen" label="血氧" width="90" align="center" />
      <el-table-column label="血压" width="120" align="center">
        <template #default="{ row }">{{ row.systolic_bp }}/{{ row.diastolic_bp }}</template>
      </el-table-column>
      <el-table-column prop="temperature" label="体温" width="90" align="center" />
      <el-table-column prop="blood_sugar" label="血糖" width="90" align="center" />
      <el-table-column prop="weight" label="体重" width="90" align="center" />
      <el-table-column prop="feeling" label="自述" show-overflow-tooltip />
      <el-table-column label="异常" width="140">
        <template #default="{ row }">
          <el-tag v-for="a in row.anomalies" :key="a" type="danger" size="small"
                  style="margin: 2px;">{{ a }}</el-tag>
          <el-tag v-if="!row.anomalies?.length" type="success" size="small">正常</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'

const route = useRoute()
const records = ref([])
const elderName = ref('')

function isAnomaly(val, min, max) {
  if (val == null) return false
  return Number(val) < min || Number(val) > max
}

onMounted(async () => {
  const eid = route.params.id
  const [data, elder] = await Promise.all([
    request.get(`/health/history/${eid}/`),
    request.get(`/auth/elders/${eid}/`),
  ])
  records.value = data
  elderName.value = elder.name
})
</script>
