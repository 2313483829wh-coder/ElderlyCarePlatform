<template>
  <el-descriptions :column="1" border size="small" v-if="checkup">
    <el-descriptions-item label="体检日期">{{ checkup.check_date }}</el-descriptions-item>
    <el-descriptions-item label="体检机构">{{ checkup.hospital || '—' }}</el-descriptions-item>

    <!-- 核心指标 -->
    <el-descriptions-item label="身高">
      {{ checkup.height || '—' }} cm <CheckupMetricStatus :value="checkup.height" :min="140" :max="200" unit="cm" />
    </el-descriptions-item>
    <el-descriptions-item label="体重">
      {{ checkup.weight || '—' }} kg <CheckupMetricStatus :value="checkup.weight" :min="35" :max="120" unit="kg" />
    </el-descriptions-item>
    <el-descriptions-item label="血压">
      {{ checkup.blood_pressure || '—' }} <CheckupMetricStatus :systolic_bp="checkup.systolic_bp" :diastolic_bp="checkup.diastolic_bp" unit="mmHg" type="blood_pressure" :thresholds="thresholds" />
    </el-descriptions-item>
    <el-descriptions-item label="心率">
      {{ checkup.heart_rate || '—' }} bpm <CheckupMetricStatus :value="checkup.heart_rate" :min="thresholds.heart_rate_min" :max="thresholds.heart_rate_max" unit="bpm" />
    </el-descriptions-item>
    <el-descriptions-item label="血糖">
      {{ checkup.blood_sugar || '—' }} mmol/L <CheckupMetricStatus :value="checkup.blood_sugar" :min="thresholds.blood_sugar_min" :max="thresholds.blood_sugar_max" unit="mmol/L" />
    </el-descriptions-item>

    <!-- 其他检查 -->
    <el-descriptions-item label="血脂">{{ checkup.blood_lipid || '—' }}</el-descriptions-item>
    <el-descriptions-item label="肝功能">{{ checkup.liver_function || '—' }}</el-descriptions-item>
    <el-descriptions-item label="肾功能">{{ checkup.kidney_function || '—' }}</el-descriptions-item>
    <el-descriptions-item label="血常规">{{ checkup.blood_routine || '—' }}</el-descriptions-item>
    <el-descriptions-item label="尿常规">{{ checkup.urine_routine || '—' }}</el-descriptions-item>
    <el-descriptions-item label="心电图">{{ checkup.ecg || '—' }}</el-descriptions-item>
    <el-descriptions-item label="胸部X光">{{ checkup.chest_xray || '—' }}</el-descriptions-item>
    <el-descriptions-item label="B超">{{ checkup.b_ultrasound || '—' }}</el-descriptions-item>
    <el-descriptions-item label="视力">{{ checkup.vision || '—' }}</el-descriptions-item>
    <el-descriptions-item label="听力">{{ checkup.hearing || '—' }}</el-descriptions-item>

    <!-- 结论与建议 -->
    <el-descriptions-item label="综合结论">{{ checkup.overall_result || '—' }}</el-descriptions-item>
    <el-descriptions-item label="医生建议">{{ checkup.doctor_advice || '—' }}</el-descriptions-item>
    <el-descriptions-item label="体检报告">
      <div v-if="reportUrl" class="report-wrap">
        <img v-if="isImageReport" class="report-image" :src="reportUrl" alt="体检报告图片" />
        <el-link :href="reportUrl" target="_blank" type="primary">查看报告</el-link>
      </div>
      <span v-else>无</span>
    </el-descriptions-item>
  </el-descriptions>
</template>

<script setup>
import { defineProps, computed } from 'vue'
import CheckupMetricStatus from './CheckupMetricStatus.vue'

const props = defineProps({
  checkup: Object,
  thresholds: Object, // 接收健康阈值
})

const reportUrl = computed(() => props.checkup?.report_file_url || props.checkup?.report_file || '')
const isImageReport = computed(() => {
  const url = (reportUrl.value || '').toLowerCase()
  return ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.heic'].some(ext => url.includes(ext))
})
</script>

<style scoped>
.report-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.report-image {
  max-width: 100%;
  max-height: 240px;
  object-fit: contain;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fafafa;
}
</style>
