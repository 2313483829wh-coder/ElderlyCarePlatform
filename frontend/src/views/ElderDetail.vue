<template>
  <div>
    <el-button text icon="ArrowLeft" @click="$router.back()" style="margin-bottom: 16px;">返回</el-button>
    
    <el-card v-loading="loading">
      <template #header>
        <div style="display: flex; align-items: center; gap: 12px;">
          <el-icon :size="32" color="#0066cc"><User /></el-icon>
          <div>
            <h2 style="margin: 0; font-size: 24px; font-weight: 700; color: #1d1d1f;">{{ elder.name }}</h2>
            <p style="margin: 4px 0 0; color: #86868b; font-size: 14px;">{{ elder.community_name }}</p>
          </div>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="姓名">
          <span style="font-weight: 600; font-size: 16px;">{{ elder.name }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="性别">
          {{ elder.gender === 'M' ? '男' : '女' }}
        </el-descriptions-item>
        <el-descriptions-item label="年龄">
          {{ elder.age }}岁
        </el-descriptions-item>
        <el-descriptions-item label="出生日期">
          {{ elder.birth_date }}
        </el-descriptions-item>
        <el-descriptions-item label="身份证号" :span="2">
          {{ elder.id_card }}
        </el-descriptions-item>
        <el-descriptions-item label="联系电话" :span="2">
          <el-link :href="`tel:${elder.phone}`" type="primary">
            <el-icon><Phone /></el-icon>
            {{ elder.phone }}
          </el-link>
        </el-descriptions-item>
        <el-descriptions-item label="家庭住址" :span="2">
          {{ elder.address }}
        </el-descriptions-item>
        <el-descriptions-item label="紧急联系人">
          {{ elder.emergency_contact }}
        </el-descriptions-item>
        <el-descriptions-item label="紧急联系电话">
          <el-link :href="`tel:${elder.emergency_phone}`" type="primary">
            <el-icon><Phone /></el-icon>
            {{ elder.emergency_phone }}
          </el-link>
        </el-descriptions-item>
        <el-descriptions-item label="既往病史" :span="2">
          <el-tag v-if="elder.medical_history" type="warning">{{ elder.medical_history }}</el-tag>
          <span v-else style="color: #86868b;">无</span>
        </el-descriptions-item>
        <el-descriptions-item label="入住时间">
          {{ elder.created_at ? new Date(elder.created_at).toLocaleDateString() : '—' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="elder.is_active ? 'success' : 'info'">
            {{ elder.is_active ? '在住' : '已离开' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <div style="margin-top: 24px; display: flex; gap: 12px;">
        <el-button type="primary" @click="$router.push(`/elder/${elder.id}/health`)">
          <el-icon><TrendCharts /></el-icon>
          查看健康数据
        </el-button>
        <el-button @click="$router.push(`/checkup/elder/${elder.id}`)">
          <el-icon><Document /></el-icon>
          查看体检记录
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { User, Phone, TrendCharts, Document } from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const loading = ref(true)
const elder = ref({})

onMounted(async () => {
  try {
    const elderId = route.params.id
    elder.value = await request.get(`/auth/elders/${elderId}/`)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #1d1d1f;
  background: #f5f5f7;
}
:deep(.el-descriptions__content) {
  color: #1d1d1f;
}
</style>
