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
      <el-link v-if="checkup.report_file" :href="checkup.report_file" target="_blank" type="primary">
        查看报告
      </el-link>
      <span v-else>无</span>
    </el-descriptions-item>
  </el-descriptions>
</template>

<script setup>
import { defineProps } from 'vue'
import CheckupMetricStatus from './CheckupMetricStatus.vue'

const props = defineProps({
  checkup: Object,
  thresholds: Object, // 接收健康阈值
})
</script>
