<template>
  <div>
    <el-button text icon="ArrowLeft" @click="$router.back()">返回</el-button>
    <h3 style="display: inline; margin-left: 8px;" v-if="elderName">
      {{ elderName }} — 体检记录
    </h3>

    <el-button type="primary" style="float: right;" icon="Plus" @click="showAdd = true">
      录入体检结果
    </el-button>

    <el-table :data="records" stripe border style="margin-top: 16px;">
      <el-table-column prop="year" label="年度" width="80" />
      <el-table-column label="第几次" width="80" align="center">
        <template #default="{ row }">第{{ row.sequence }}次</template>
      </el-table-column>
      <el-table-column prop="check_date" label="体检日期" width="120" />
      <el-table-column prop="hospital" label="体检机构" width="160" />
      <el-table-column prop="blood_pressure" label="血压" width="100" />
      <el-table-column prop="heart_rate" label="心率" width="80" />
      <el-table-column prop="blood_sugar" label="血糖" width="80" />
      <el-table-column prop="overall_result" label="综合结论" show-overflow-tooltip />
      <el-table-column prop="doctor_advice" label="医生建议" show-overflow-tooltip />
    </el-table>

    <el-dialog v-model="showAdd" title="录入体检结果" width="600px">
      <el-form :model="form" label-width="90px" ref="formRef">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="年度" prop="year" :rules="[{required:true}]">
              <el-input-number v-model="form.year" :min="2020" :max="2030" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="第几次" prop="sequence" :rules="[{required:true}]">
              <el-select v-model="form.sequence" style="width: 100%">
                <el-option :value="1" label="第1次(上半年)" />
                <el-option :value="2" label="第2次(下半年)" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="体检日期" prop="check_date" :rules="[{required:true}]">
              <el-date-picker v-model="form.check_date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="体检机构">
              <el-input v-model="form.hospital" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="身高(cm)">
              <el-input-number v-model="form.height" :min="0" :max="250" :precision="1" 
                               controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="体重(kg)">
              <el-input-number v-model="form.weight" :min="0" :max="200" :precision="1" 
                               controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="血压">
              <el-input v-model="form.blood_pressure" placeholder="120/80" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="心率">
              <el-input-number v-model="form.heart_rate" :min="0" :max="200" 
                               controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="血糖">
              <el-input-number v-model="form.blood_sugar" :min="0" :max="30" :precision="1" 
                               controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item label="血脂">
              <el-input v-model="form.blood_lipid" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="心电图"><el-input v-model="form.ecg" /></el-form-item>
        <el-form-item label="综合结论"><el-input v-model="form.overall_result" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="医生建议"><el-input v-model="form.doctor_advice" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" @click="submitCheckup">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const elderId = route.params.elderId
const elderName = ref('')
const records = ref([])
const showAdd = ref(false)
const formRef = ref()
const form = reactive({
  elder: Number(elderId), 
  year: new Date().getFullYear(), 
  sequence: 1,
  check_date: '', 
  hospital: '', 
  height: null, 
  weight: null,
  blood_pressure: '', 
  heart_rate: null, 
  blood_sugar: null, 
  blood_lipid: '',
  ecg: '', 
  overall_result: '', 
  doctor_advice: '',
})

async function loadData() {
  records.value = await request.get(`/checkup/elder/${elderId}/`)
  if (records.value.length) elderName.value = records.value[0].elder_name
  else {
    const e = await request.get(`/auth/elders/${elderId}/`)
    elderName.value = e.name
  }
}

async function submitCheckup() {
  try {
    await formRef.value.validate()
    
    // 构建提交数据，过滤掉空值
    const payload = {
      elder: form.elder,
      year: form.year,
      sequence: form.sequence,
      check_date: form.check_date,
    }
    
    // 只添加非空的字段
    if (form.hospital) payload.hospital = form.hospital
    if (form.height) payload.height = Number(form.height)
    if (form.weight) payload.weight = Number(form.weight)
    if (form.blood_pressure) payload.blood_pressure = form.blood_pressure
    if (form.heart_rate) payload.heart_rate = Number(form.heart_rate)
    if (form.blood_sugar) payload.blood_sugar = Number(form.blood_sugar)
    if (form.blood_lipid) payload.blood_lipid = form.blood_lipid
    if (form.ecg) payload.ecg = form.ecg
    if (form.overall_result) payload.overall_result = form.overall_result
    if (form.doctor_advice) payload.doctor_advice = form.doctor_advice
    
    await request.post('/checkup/', payload)
    ElMessage.success('录入成功')
    showAdd.value = false
    
    // 重置表单
    form.year = new Date().getFullYear()
    form.sequence = 1
    form.check_date = ''
    form.hospital = ''
    form.height = null
    form.weight = null
    form.blood_pressure = ''
    form.heart_rate = null
    form.blood_sugar = null
    form.blood_lipid = ''
    form.ecg = ''
    form.overall_result = ''
    form.doctor_advice = ''
    
    loadData()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error.response?.data?.detail || '录入失败，请检查输入')
  }
}

onMounted(loadData)
</script>
