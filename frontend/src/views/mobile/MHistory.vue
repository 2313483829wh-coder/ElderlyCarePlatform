<template>
  <div class="m-history">
    <h2 style="padding: 20px 16px 8px; font-size: 22px;">📊 我的健康记录</h2>

    <div class="record-card" v-for="r in records" :key="r.id">
      <div class="record-date">{{ r.date }}</div>
      <div class="record-grid">
        <div class="record-item">
          <span class="item-icon">❤️</span>
          <span class="item-val" :class="{ danger: isHigh(r.heart_rate, 120) || isLow(r.heart_rate, 50) }">
            {{ r.heart_rate ?? '—' }}
          </span>
          <span class="item-lbl">心跳</span>
        </div>
        <div class="record-item">
          <span class="item-icon">💨</span>
          <span class="item-val" :class="{ danger: isLow(r.blood_oxygen, 90) }">
            {{ r.blood_oxygen ?? '—' }}
          </span>
          <span class="item-lbl">血氧</span>
        </div>
        <div class="record-item">
          <span class="item-icon">🩸</span>
          <span class="item-val" :class="{ danger: isHigh(r.systolic_bp, 160) }">
            {{ r.systolic_bp ?? '—' }}/{{ r.diastolic_bp ?? '—' }}
          </span>
          <span class="item-lbl">血压</span>
        </div>
        <div class="record-item">
          <span class="item-icon">🌡️</span>
          <span class="item-val" :class="{ danger: isHigh(r.temperature, 37.5) }">
            {{ r.temperature ?? '—' }}
          </span>
          <span class="item-lbl">体温</span>
        </div>
      </div>
      <div class="record-feeling" v-if="r.feeling">💬 {{ r.feeling }}</div>
      <div class="record-anomaly" v-if="r.anomalies?.length">
        ⚠️ {{ r.anomalies.join('、') }}
      </div>
    </div>

    <div v-if="!records.length" style="text-align: center; padding: 60px 0; color: #999; font-size: 18px;">
      暂无记录
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const records = ref([])
const isHigh = (v, max) => v != null && Number(v) > max
const isLow = (v, min) => v != null && Number(v) < min

onMounted(async () => {
  records.value = await request.get('/health/my-history/')
})
</script>

<style scoped>
.m-history { padding-bottom: 20px; }
.record-card {
  margin: 8px 16px; padding: 16px; background: #fff;
  border-radius: 14px; box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.record-date {
  font-size: 16px; font-weight: 700; color: #4caf50; margin-bottom: 10px;
}
.record-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.record-item {
  display: flex; align-items: center; gap: 6px;
  .item-icon { font-size: 20px; }
  .item-val { font-size: 22px; font-weight: 700; color: #333; }
  .item-val.danger { color: #f44336; }
  .item-lbl { font-size: 14px; color: #999; }
}
.record-feeling { margin-top: 10px; font-size: 16px; color: #666; }
.record-anomaly {
  margin-top: 8px; font-size: 16px; color: #f44336; font-weight: 600;
  background: #ffebee; padding: 8px 12px; border-radius: 8px;
}
</style>
