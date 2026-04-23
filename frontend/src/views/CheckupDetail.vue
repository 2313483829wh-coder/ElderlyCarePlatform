<template>
  <div>
    <div style="margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center;">
      <h3 style="margin: 0; display: inline;" v-if="elderName">
        <el-button text icon="ArrowLeft" @click="$router.back()">返回</el-button>
        {{ elderName }} — {{ currentYear }}年体检记录
      </h3>
      <el-button type="primary" icon="Plus" @click="openAddDialog">
        录入体检结果
      </el-button>
    </div>

    <!-- 体检记录展示区域 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-main">
                <span>第一次体检 (上半年)</span>
                <el-tag :type="firstCheckup?.id ? 'success' : 'info'" size="small">
                  {{ firstCheckup?.id ? '已录入' : '未录入' }}
                </el-tag>
              </div>
              <el-button v-if="firstCheckup?.id" text type="primary" @click="openEditDialog(firstCheckup)">
                修改体检结果
              </el-button>
            </div>
          </template>
          <el-empty v-if="!firstCheckup?.id" description="暂无第一次体检记录" />
          <CheckupDisplay v-else :checkup="firstCheckup" :thresholds="healthThresholds" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-main">
                <span>第二次体检 (下半年)</span>
                <el-tag :type="secondCheckup?.id ? 'success' : 'info'" size="small">
                  {{ secondCheckup?.id ? '已录入' : '未录入' }}
                </el-tag>
              </div>
              <el-button v-if="secondCheckup?.id" text type="primary" @click="openEditDialog(secondCheckup)">
                修改体检结果
              </el-button>
            </div>
          </template>
          <el-empty v-if="!secondCheckup?.id" description="暂无第二次体检记录" />
          <CheckupDisplay v-else :checkup="secondCheckup" :thresholds="healthThresholds" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 录入体检结果对话框 -->
    <el-dialog v-model="showAddDialog" :title="`录入${form.year}年第${form.sequence}次体检结果`" width="800px" @close="resetForm">
      <el-form :model="form" label-width="110px" ref="formRef">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="年度" prop="year" :rules="[{required:true}]">
              <el-input-number v-model="form.year" :min="2020" :max="new Date().getFullYear()" controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="第几次体检" prop="sequence" :rules="[{required:true}]">
              <el-select v-model="form.sequence" style="width: 100%" placeholder="请选择">
                <el-option :value="1" label="第1次(上半年)" :disabled="!!firstCheckup?.id && form.sequence !== 1" />
                <el-option :value="2" label="第2次(下半年)" :disabled="!!secondCheckup?.id && form.sequence !== 2" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="体检日期" prop="check_date" :rules="[{required:true, message:'请选择体检日期'}]">
              <el-date-picker v-model="form.check_date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="体检机构">
              <el-input v-model="form.hospital" placeholder="可选" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="血脂">
              <el-input v-model="form.blood_lipid" placeholder="可选" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>核心指标</el-divider>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="身高(cm)">
              <el-input-number v-model="form.height" :min="0" :max="250" :precision="1" 
                               controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="体重(kg)">
              <el-input-number v-model="form.weight" :min="0" :max="200" :precision="1" 
                               controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="心率(bpm)">
              <el-input-number v-model="form.heart_rate" :min="0" :max="200" 
                               controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="收缩压(mmHg)">
              <el-input-number v-model="form.systolic_bp" :min="0" :max="300" 
                               controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="舒张压(mmHg)">
              <el-input-number v-model="form.diastolic_bp" :min="0" :max="200" 
                               controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="血糖(mmol/L)">
              <el-input-number v-model="form.blood_sugar" :min="0" :max="30" :precision="1" 
                               controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider>其他检查</el-divider>

        <el-form-item label="肝功能"><el-input v-model="form.liver_function" placeholder="可选" /></el-form-item>
        <el-form-item label="肾功能"><el-input v-model="form.kidney_function" placeholder="可选" /></el-form-item>
        <el-form-item label="血常规"><el-input v-model="form.blood_routine" placeholder="可选" /></el-form-item>
        <el-form-item label="尿常规"><el-input v-model="form.urine_routine" placeholder="可选" /></el-form-item>
        <el-form-item label="心电图"><el-input v-model="form.ecg" placeholder="可选" /></el-form-item>
        <el-form-item label="胸部X光"><el-input v-model="form.chest_xray" placeholder="可选" /></el-form-item>
        <el-form-item label="B超"><el-input v-model="form.b_ultrasound" placeholder="可选" /></el-form-item>
        <el-form-item label="视力"><el-input v-model="form.vision" placeholder="可选" /></el-form-item>
        <el-form-item label="听力"><el-input v-model="form.hearing" placeholder="可选" /></el-form-item>

        <el-divider>结论与建议</el-divider>
        
        <el-form-item label="综合结论" prop="overall_result" :rules="[{required:true, message:'请输入综合结论'}]">
          <el-input v-model="form.overall_result" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="医生建议" prop="doctor_advice" :rules="[{required:true, message:'请输入医生建议'}]">
          <el-input v-model="form.doctor_advice" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCheckup">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1d1d1f;
  font-size: 16px;
}
.header-main {
  display: flex;
  align-items: center;
  gap: 8px;
}
:deep(.el-card__body) {
  min-height: 200px;
}
:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #1d1d1f;
  background: #f5f5f7;
}
:deep(.el-descriptions__content) {
  color: #1d1d1f;
}
.metric-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px dashed #eee;
}
.metric-item:last-child {
  border-bottom: none;
}
.metric-label {
  font-weight: 500;
  color: #555;
}
.metric-value {
  font-weight: 600;
}
.metric-status .el-tag {
  margin-left: 8px;
}
</style>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, ArrowLeft } from '@element-plus/icons-vue'
import request from '@/utils/request'
import CheckupDisplay from './CheckupDisplay.vue' // 导入新组件

const route = useRoute()
const elderId = route.params.elderId
const elderName = ref('')
const currentYear = ref(new Date().getFullYear())
const records = ref([]) // 所有体检记录
const firstCheckup = ref(null)
const secondCheckup = ref(null)
const showAddDialog = ref(false)
const formRef = ref()
const healthThresholds = ref({}) // 健康阈值

const form = reactive({
  id: null, // 用于编辑
  elder: Number(elderId), 
  year: currentYear.value, 
  sequence: 1,
  check_date: '', 
  hospital: '', 
  height: null, 
  weight: null,
  systolic_bp: null, // 新增收缩压
  diastolic_bp: null, // 新增舒张压
  heart_rate: null, 
  blood_sugar: null, 
  blood_lipid: '',
  liver_function: '',
  kidney_function: '',
  blood_routine: '',
  urine_routine: '',
  ecg: '', 
  chest_xray: '',
  b_ultrasound: '',
  vision: '',
  hearing: '',
  overall_result: '', 
  doctor_advice: '',
  report_file: null, // 体检报告文件
})

function fillFormFromRecord(existingRecord) {
  if (!existingRecord) return
  Object.assign(form, {
    id: existingRecord.id,
    check_date: existingRecord.check_date,
    hospital: existingRecord.hospital,
    height: existingRecord.height,
    weight: existingRecord.weight,
    systolic_bp: existingRecord.systolic_bp,
    diastolic_bp: existingRecord.diastolic_bp,
    heart_rate: existingRecord.heart_rate,
    blood_sugar: existingRecord.blood_sugar,
    blood_lipid: existingRecord.blood_lipid,
    liver_function: existingRecord.liver_function,
    kidney_function: existingRecord.kidney_function,
    blood_routine: existingRecord.blood_routine,
    urine_routine: existingRecord.urine_routine,
    ecg: existingRecord.ecg,
    chest_xray: existingRecord.chest_xray,
    b_ultrasound: existingRecord.b_ultrasound,
    vision: existingRecord.vision,
    hearing: existingRecord.hearing,
    overall_result: existingRecord.overall_result,
    doctor_advice: existingRecord.doctor_advice,
    report_file: existingRecord.report_file,
  })
}

function clearEditableFields() {
  const resetFields = ['id', 'check_date', 'hospital', 'height', 'weight', 'systolic_bp', 'diastolic_bp', 'heart_rate', 'blood_sugar', 'blood_lipid', 'liver_function', 'kidney_function', 'blood_routine', 'urine_routine', 'ecg', 'chest_xray', 'b_ultrasound', 'vision', 'hearing', 'overall_result', 'doctor_advice', 'report_file']
  resetFields.forEach(field => { form[field] = null })
  form.hospital = ''
  form.blood_lipid = ''
  form.liver_function = ''
  form.kidney_function = ''
  form.blood_routine = ''
  form.urine_routine = ''
  form.ecg = ''
  form.chest_xray = ''
  form.b_ultrasound = ''
  form.vision = ''
  form.hearing = ''
  form.overall_result = ''
  form.doctor_advice = ''
}

// 监听 year + sequence 变化，预填充表单
watch(() => [form.year, form.sequence], ([newYear, newSequence]) => {
  const existingRecord = records.value.find(r => r.year === newYear && r.sequence === newSequence)
  if (existingRecord) {
    fillFormFromRecord(existingRecord)
  } else {
    clearEditableFields()
  }
}, { immediate: true })

async function loadData() {
  try {
    // 获取老人姓名
    const elderRes = await request.get(`/auth/elders/${elderId}/`)
    elderName.value = elderRes.name

    // 获取当年所有体检记录
    const recordsRes = await request.get(`/checkup/elder/${elderId}/`, {
      params: { year: currentYear.value } // 筛选当年的体检记录
    })
    records.value = recordsRes || []
    firstCheckup.value = records.value.find(r => r.sequence === 1)
    secondCheckup.value = records.value.find(r => r.sequence === 2)

    // 获取健康阈值
    healthThresholds.value = await request.get('/health/thresholds/')

  } finally {
    // loading.value = false // 暂时注释，避免和组件内loading冲突
  }
}

function openAddDialog() {
  showAddDialog.value = true
  form.id = null
  form.year = currentYear.value
  // 默认选择未录入的sequence
  if (!firstCheckup.value) {
    form.sequence = 1
  } else if (!secondCheckup.value) {
    form.sequence = 2
  } else {
    // 如果都录入了，默认选择第一次进行编辑
    form.sequence = 1
  }
  // 触发watch，预填充表单
  // resetForm() // 在watch中处理了
}

function openEditDialog(record) {
  if (!record) return
  showAddDialog.value = true
  form.year = record.year
  form.sequence = record.sequence
  fillFormFromRecord(record)
}

function resetForm() {
  formRef.value.resetFields() // 重置表单验证状态
  Object.assign(form, {
    id: null,
    year: currentYear.value,
    sequence: 1,
    check_date: '',
    hospital: '',
    height: null,
    weight: null,
    systolic_bp: null,
    diastolic_bp: null,
    heart_rate: null,
    blood_sugar: null,
    blood_lipid: '',
    liver_function: '',
    kidney_function: '',
    blood_routine: '',
    urine_routine: '',
    ecg: '',
    chest_xray: '',
    b_ultrasound: '',
    vision: '',
    hearing: '',
    overall_result: '',
    doctor_advice: '',
    report_file: null,
  })
}

async function submitCheckup() {
  try {
    await formRef.value.validate()
    
    const payload = {
      elder: form.elder,
      year: form.year,
      sequence: form.sequence,
      check_date: form.check_date,
      hospital: form.hospital || undefined, // 传递undefined可以确保后端Default值生效
      height: form.height || undefined,
      weight: form.weight || undefined,
      systolic_bp: form.systolic_bp || undefined,
      diastolic_bp: form.diastolic_bp || undefined,
      heart_rate: form.heart_rate || undefined,
      blood_sugar: form.blood_sugar || undefined,
      blood_lipid: form.blood_lipid || undefined,
      liver_function: form.liver_function || undefined,
      kidney_function: form.kidney_function || undefined,
      blood_routine: form.blood_routine || undefined,
      urine_routine: form.urine_routine || undefined,
      ecg: form.ecg || undefined,
      chest_xray: form.chest_xray || undefined,
      b_ultrasound: form.b_ultrasound || undefined,
      vision: form.vision || undefined,
      hearing: form.hearing || undefined,
      overall_result: form.overall_result,
      doctor_advice: form.doctor_advice,
    }

    if (form.id) {
      // 编辑现有记录
      await request.patch(`/checkup/${form.id}/`, payload)
      ElMessage.success('体检记录更新成功')
    } else {
      // 创建新记录
      await request.post('/checkup/', payload)
      ElMessage.success('体检记录录入成功')
    }
    
    showAddDialog.value = false
    await loadData()
  } catch (error) {
    console.error('提交失败:', error)
    const data = error.response?.data
    const firstFieldError = data && typeof data === 'object'
      ? Object.values(data).flat().find(item => typeof item === 'string')
      : null
    ElMessage.error(firstFieldError || data?.detail || '录入失败，请检查输入')
  }
}

onMounted(loadData)
</script>
