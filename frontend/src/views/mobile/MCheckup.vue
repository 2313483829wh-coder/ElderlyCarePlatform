<template>
  <div class="m-checkup">
    <h2 style="padding: 20px 16px 8px; font-size: 22px;">🩺 我的体检报告</h2>

    <div class="checkup-card" v-for="c in checkups" :key="c.id">
      <div class="checkup-header">
        <span class="checkup-title">{{ c.year }}年 第{{ c.sequence }}次体检</span>
        <span class="checkup-date">{{ c.check_date }}</span>
      </div>
      <div class="checkup-hospital" v-if="c.hospital">📍 {{ c.hospital }}</div>
      <div class="checkup-grid">
        <div class="cg-item" v-if="c.blood_pressure">
          <span class="cg-lbl">血压</span>
          <span class="cg-val">{{ c.blood_pressure }}</span>
        </div>
        <div class="cg-item" v-if="c.heart_rate">
          <span class="cg-lbl">心率</span>
          <span class="cg-val">{{ c.heart_rate }}</span>
        </div>
        <div class="cg-item" v-if="c.blood_sugar">
          <span class="cg-lbl">血糖</span>
          <span class="cg-val">{{ c.blood_sugar }}</span>
        </div>
        <div class="cg-item" v-if="c.height">
          <span class="cg-lbl">身高</span>
          <span class="cg-val">{{ c.height }}cm</span>
        </div>
        <div class="cg-item" v-if="c.weight">
          <span class="cg-lbl">体重</span>
          <span class="cg-val">{{ c.weight }}kg</span>
        </div>
      </div>
      <div class="checkup-result" v-if="c.overall_result">
        <strong>综合结论：</strong>{{ c.overall_result }}
      </div>
      <div class="checkup-advice" v-if="c.doctor_advice">
        <strong>医生建议：</strong>{{ c.doctor_advice }}
      </div>
    </div>

    <div v-if="!checkups.length" style="text-align: center; padding: 60px 0; color: #999; font-size: 18px;">
      暂无体检记录
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const checkups = ref([])

onMounted(async () => {
  const user = await request.get('/auth/users/me/')
  if (user.elder_profile) {
    checkups.value = await request.get(`/checkup/elder/${user.elder_profile}/`)
  }
})
</script>

<style scoped>
.m-checkup { padding-bottom: 20px; }
.checkup-card {
  margin: 8px 16px; padding: 18px; background: #fff;
  border-radius: 14px; box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.checkup-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
  .checkup-title { font-size: 20px; font-weight: 700; color: #333; }
  .checkup-date { font-size: 14px; color: #999; }
}
.checkup-hospital { font-size: 15px; color: #888; margin-bottom: 12px; }
.checkup-grid {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 12px;
  .cg-item { text-align: center;
    .cg-lbl { display: block; font-size: 13px; color: #999; }
    .cg-val { display: block; font-size: 20px; font-weight: 700; color: #333; margin-top: 2px; }
  }
}
.checkup-result, .checkup-advice {
  font-size: 17px; line-height: 1.6; color: #555; margin-top: 8px;
  padding: 10px; background: #f5f5f5; border-radius: 8px;
  strong { color: #333; }
}
.checkup-advice { background: #e8f5e9; }
</style>
