<template>
  <div>
    <el-button text icon="ArrowLeft" @click="$router.back()" style="margin-bottom: 16px;">返回</el-button>
    
    <el-card v-loading="loading">
      <template #header>
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <el-icon :size="32" color="#0066cc"><User /></el-icon>
            <div>
              <h2 style="margin: 0; font-size: 24px; font-weight: 700; color: #1d1d1f;">{{ elder.name }}</h2>
              <p style="margin: 4px 0 0; color: #86868b; font-size: 14px;">{{ elder.community_name }}</p>
            </div>
          </div>
          <div style="display: flex; gap: 8px;">
            <el-button v-if="!editing" type="primary" @click="startEdit">
              <el-icon><Edit /></el-icon>
              修改
            </el-button>
            <template v-else>
              <el-button type="success" @click="saveEdit">
                <el-icon><Check /></el-icon>
                完成
              </el-button>
              <el-button @click="cancelEdit">
                <el-icon><Close /></el-icon>
                取消
              </el-button>
            </template>
          </div>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="姓名">
          <span style="font-weight: 600; font-size: 16px;">{{ elder.name }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="性别">
          <el-select v-if="editing" v-model="editForm.gender" style="width: 100%;">
            <el-option label="男" value="M" />
            <el-option label="女" value="F" />
          </el-select>
          <span v-else>{{ elder.gender === 'M' ? '男' : '女' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="年龄">
          {{ elder.age }}岁
        </el-descriptions-item>
        <el-descriptions-item label="出生日期">
          <el-date-picker v-if="editing" v-model="editForm.birth_date" type="date" 
            value-format="YYYY-MM-DD" style="width: 100%;" />
          <span v-else>{{ elder.birth_date }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="身份证号" :span="2">
          {{ elder.id_card }}
        </el-descriptions-item>
        <el-descriptions-item label="联系电话" :span="2">
          <el-input v-if="editing" v-model="editForm.phone" maxlength="11" />
          <el-link v-else :href="`tel:${elder.phone}`" type="primary">
            <el-icon><Phone /></el-icon>
            {{ elder.phone }}
          </el-link>
        </el-descriptions-item>
        <el-descriptions-item label="家庭住址" :span="2">
          <el-input v-if="editing" v-model="editForm.address" />
          <span v-else>{{ elder.address }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="紧急联系人">
          <el-input v-if="editing" v-model="editForm.emergency_contact" />
          <span v-else>{{ elder.emergency_contact }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="紧急联系电话">
          <el-input v-if="editing" v-model="editForm.emergency_phone" maxlength="11" />
          <el-link v-else :href="`tel:${elder.emergency_phone}`" type="primary">
            <el-icon><Phone /></el-icon>
            {{ elder.emergency_phone }}
          </el-link>
        </el-descriptions-item>
        <el-descriptions-item label="既往病史" :span="2">
          <el-input v-if="editing" v-model="editForm.medical_history" type="textarea" :rows="2" />
          <template v-else>
            <el-tag v-if="elder.medical_history" type="warning">{{ elder.medical_history }}</el-tag>
            <span v-else style="color: #86868b;">无</span>
          </template>
        </el-descriptions-item>
        <el-descriptions-item label="入住时间">
          {{ elder.created_at ? new Date(elder.created_at).toLocaleDateString() : '—' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-switch v-if="editing" v-model="editForm.is_active" 
            active-text="在住" inactive-text="已离开" />
          <el-tag v-else :type="elder.is_active ? 'success' : 'info'">
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
import { ElMessage } from 'element-plus'
import { User, Phone, TrendCharts, Document, Edit, Check, Close } from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const loading = ref(true)
const elder = ref({})
const editing = ref(false)
const editForm = ref({})

async function loadData() {
  try {
    const elderId = route.params.id
    elder.value = await request.get(`/auth/elders/${elderId}/`)
  } finally {
    loading.value = false
  }
}

function startEdit() {
  editing.value = true
  editForm.value = {
    gender: elder.value.gender,
    birth_date: elder.value.birth_date,
    phone: elder.value.phone,
    address: elder.value.address,
    emergency_contact: elder.value.emergency_contact,
    emergency_phone: elder.value.emergency_phone,
    medical_history: elder.value.medical_history || '',
    is_active: elder.value.is_active
  }
}

function cancelEdit() {
  editing.value = false
  editForm.value = {}
}

async function saveEdit() {
  try {
    loading.value = true
    await request.put(`/auth/elders/${elder.value.id}/`, editForm.value)
    ElMessage.success('修改成功')
    editing.value = false
    await loadData()
  } catch (error) {
    ElMessage.error('修改失败：' + (error.response?.data?.detail || '未知错误'))
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
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
