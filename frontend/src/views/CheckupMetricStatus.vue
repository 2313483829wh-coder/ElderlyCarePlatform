<template>
  <span v-if="showRange" class="metric-range">
    (标准: <template v-if="type === 'blood_pressure'">{{ thresholds.systolic_bp_min }}-{{ thresholds.systolic_bp_max }}/{{ thresholds.diastolic_bp_min }}-{{ thresholds.diastolic_bp_max }} {{ unit }}</template>
    <template v-else-if="min !== undefined && max !== undefined">{{ min }}-{{ max }} {{ unit }}</template>
    <template v-else-if="min !== undefined">&gt;={{ min }} {{ unit }}</template>
    <template v-else-if="max !== undefined">&lt;={{ max }} {{ unit }}</template>
    )
  </span>
  <el-tag :type="statusType" size="small" v-if="statusText">
    {{ statusText }}
  </el-tag>
</template>

<script setup>
import { defineProps, computed } from 'vue'

const props = defineProps({
  value: [Number, String, null],
  systolic_bp: [Number, null], // for blood pressure
  diastolic_bp: [Number, null], // for blood pressure
  min: [Number, null],
  max: [Number, null],
  unit: String,
  type: String, // 'blood_pressure' or other
  thresholds: Object, // 健康阈值对象
})

const statusType = computed(() => {
  if (statusText.value === '正常') return 'success'
  if (statusText.value && statusText.value.includes('低')) return 'warning'
  if (statusText.value && statusText.value.includes('高')) return 'danger'
  if (statusText.value === '未录入') return 'info'
  return ''
})

const statusText = computed(() => {
  if (props.type === 'blood_pressure') {
    if (props.systolic_bp === null || props.diastolic_bp === null) return '未录入'
    const sbp = props.systolic_bp
    const dbp = props.diastolic_bp
    const t = props.thresholds

    let problems = []
    if (sbp < t.systolic_bp_min || dbp < t.diastolic_bp_min) problems.push('血压偏低')
    if (sbp > t.systolic_bp_max || dbp > t.diastolic_bp_max) problems.push('血压偏高')
    
    if (problems.length) return problems.join('/')
    return '正常'
  } else {
    if (props.value === null || props.value === '') return '未录入'
    const v = Number(props.value)

    if (props.min !== undefined && v < props.min) return '偏低'
    if (props.max !== undefined && v > props.max) return '偏高'

    return '正常'
  }
})

const showRange = computed(() => {
  return props.min !== undefined || props.max !== undefined || props.type === 'blood_pressure'
})
</script>

<style scoped>
.metric-range {
  font-size: 12px;
  color: #888;
  margin-left: 8px;
}
.el-tag {
  margin-left: 8px;
}
</style>