<template>
  <div>
    <div class="page-top">
      <el-button text icon="ArrowLeft" @click="$router.push('/communities')">返回社区列表</el-button>
      <h2 v-if="communityName">{{ communityName }} — 老人健康实时总览</h2>
    </div>

    <el-table :data="elders" v-loading="loading" stripe border size="default"
              :row-class-name="rowClass" style="width: 100%;">
      <el-table-column prop="name" label="姓名" width="90" fixed>
        <template #default="{ row }">
          <el-link 
            type="primary" 
            @click="$router.push(`/elder/${row.id}`)"
            style="font-weight: 600; font-size: 15px;">
            {{ row.name }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="年龄" width="60" align="center">
        <template #default="{ row }">{{ row.age }}岁</template>
      </el-table-column>
      <el-table-column label="心跳(bpm)" width="110" align="center">
        <template #default="{ row }">
          <span v-if="row.today_health" :class="cellClass(row.today_health.heart_rate, 50, 120)">
            {{ row.today_health.heart_rate ?? '—' }}
          </span>
          <el-tag v-else size="small" type="info">未上报</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="血氧(%)" width="100" align="center">
        <template #default="{ row }">
          <span v-if="row.today_health" :class="cellClassMin(row.today_health.blood_oxygen, 90)">
            {{ row.today_health.blood_oxygen ?? '—' }}
          </span>
          <el-tag v-else size="small" type="info">未上报</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="收缩压" width="100" align="center">
        <template #default="{ row }">
          <span v-if="row.today_health" :class="cellClassMax(row.today_health.systolic_bp, 160)">
            {{ row.today_health.systolic_bp ?? '—' }}
          </span>
          <el-tag v-else size="small" type="info">未上报</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="舒张压" width="100" align="center">
        <template #default="{ row }">
          <span v-if="row.today_health" :class="cellClassMax(row.today_health.diastolic_bp, 100)">
            {{ row.today_health.diastolic_bp ?? '—' }}
          </span>
          <el-tag v-else size="small" type="info">未上报</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="体温(℃)" width="100" align="center">
        <template #default="{ row }">
          <span v-if="row.today_health" :class="cellClassMax(row.today_health.temperature, 37.5)">
            {{ row.today_health.temperature ?? '—' }}
          </span>
          <el-tag v-else size="small" type="info">未上报</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="血糖" width="90" align="center">
        <template #default="{ row }">
          <span v-if="row.today_health" :class="cellClassMax(row.today_health.blood_sugar, 7.0)">
            {{ row.today_health.blood_sugar ?? '—' }}
          </span>
          <el-tag v-else size="small" type="info">未上报</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="自述" min-width="120">
        <template #default="{ row }">
          {{ row.today_health?.feeling || '' }}
        </template>
      </el-table-column>
      <el-table-column label="异常项" width="140">
        <template #default="{ row }">
          <template v-if="row.today_health?.anomalies?.length">
            <el-tag v-for="a in row.today_health.anomalies" :key="a" type="danger"
                    size="small" style="margin: 2px;">{{ a }}</el-tag>
          </template>
          <el-tag v-else-if="row.today_health" type="success" size="small">正常</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="体检" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.checkup_status?.ok ? 'success' : 'danger'" size="small">
            {{ row.checkup_status?.done }}/2
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small"
                     @click="$router.push(`/elder/${row.id}/health`)">健康详情</el-button>
          <el-button link type="primary" size="small"
                     @click="$router.push(`/checkup/elder/${row.id}`)">体检</el-button>
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
const loading = ref(true)
const elders = ref([])
const communityName = ref('')

function cellClass(val, min, max) {
  if (val == null) return ''
  const v = Number(val)
  if (v < min || v > max) return 'cell-danger'
  return 'cell-ok'
}
function cellClassMin(val, min) {
  if (val == null) return ''
  return Number(val) < min ? 'cell-danger' : 'cell-ok'
}
function cellClassMax(val, max) {
  if (val == null) return ''
  return Number(val) > max ? 'cell-danger' : 'cell-ok'
}
function rowClass({ row }) {
  if (row.today_health?.anomalies?.length) return 'row-alert'
  if (!row.today_health) return 'row-missing'
  return ''
}

onMounted(async () => {
  const cid = route.params.id
  try {
    const [cRes, eRes] = await Promise.all([
      request.get(`/communities/${cid}/`),
      request.get(`/auth/elders/by-community/${cid}/`),
    ])
    communityName.value = cRes.name
    elders.value = eRes
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
.page-top {
  margin-bottom: 16px;
  h2 { display: inline; margin-left: 8px; font-size: 18px; }
}
:deep(.cell-danger) {
  color: #f56c6c; font-weight: 700; font-size: 15px;
}
:deep(.cell-ok) {
  color: #333;
}
:deep(.row-alert) {
  background-color: #fef0f0 !important;
}
:deep(.row-missing) {
  background-color: #fafafa !important;
  color: #c0c4cc;
}
</style>
