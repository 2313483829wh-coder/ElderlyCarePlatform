<template>
  <div class="mobile-shell">
    <section class="hero-card">
      <p class="hero-eyebrow">Medication Plan</p>
      <h2 class="hero-title">我的用药</h2>
      <p class="hero-subtitle">查看当前用药提醒，并在服药后手动确认。</p>
    </section>

    <section v-if="plans.length" class="card-list">
      <article v-for="item in plans" :key="item.id" class="plan-card">
        <div class="plan-head">
          <div>
            <h3 class="plan-title">{{ item.medicine_name }}</h3>
            <p class="plan-meta">{{ item.dosage || '按需服用' }} · {{ item.frequency || '频次待定' }}</p>
          </div>
          <span class="time-chip">{{ item.schedule_time || '时间待定' }}</span>
        </div>
        <p class="plan-desc">{{ item.instructions || '暂无额外说明' }}</p>
        <div class="plan-footer">
          <p class="plan-last">最近确认：{{ item.last_taken_at || '还没有记录' }}</p>
          <span v-if="item.taken_today" class="done-badge">今日已服用</span>
        </div>
        <button class="primary-btn" :class="{ done: item.taken_today }" :disabled="item.taken_today || markingId === item.id" @click="markTaken(item)">
          {{ item.taken_today ? '今日已完成' : (markingId === item.id ? '记录中...' : '我已服用') }}
        </button>
      </article>
    </section>

    <section v-else class="empty-state">
      <p class="empty-title">当前还没有用药计划</p>
      <p class="empty-subtitle">管理员添加后，这里会显示你的用药清单和提醒时间。</p>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const plans = ref([])
const markingId = ref(null)

function normalizeList(res) { return Array.isArray(res) ? res : (res?.results || []) }

async function loadPlans() {
  plans.value = normalizeList(await request.get('/care/medications/my/'))
}

async function markTaken(item) {
  if (item.taken_today) return
  markingId.value = item.id
  try {
    await request.post(`/care/medications/${item.id}/mark-taken/`)
    ElMessage.success('已记录本次服药')
    await loadPlans()
  } finally {
    markingId.value = null
  }
}

onMounted(loadPlans)
</script>

<style scoped>
.mobile-shell { min-height: calc(100vh - 64px); padding:16px; background: radial-gradient(120% 70% at 15% -5%, rgba(0, 122, 255, 0.08), transparent 55%), radial-gradient(90% 60% at 95% 0%, rgba(52, 199, 89, 0.08), transparent 55%), #f5f5f7; display:grid; gap:12px; }
.hero-card,.plan-card,.empty-state { background: linear-gradient(145deg, #ffffff 0%, #f7f8fa 100%); border:1px solid rgba(0,0,0,0.08); border-radius:22px; box-shadow:0 12px 28px rgba(0,0,0,0.06); }
.hero-card,.empty-state { padding:18px; }
.plan-card { padding:12px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); }
.hero-eyebrow { margin:0 0 4px; font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:#8a8a8e; }
.hero-title { margin:0; font-size:28px; color:#111; }
.hero-subtitle { margin:8px 0 0; font-size:14px; color:#6e6e73; }
.card-list { display:grid; gap:10px; }
.plan-head { display:flex; justify-content:space-between; gap:10px; align-items:flex-start; }
.plan-title { margin:0; font-size:16px; letter-spacing:-0.01em; color:#111; }
.plan-meta,.plan-desc,.plan-last { margin:6px 0 0; font-size:12px; line-height:1.55; color:#6e6e73; }
.time-chip { padding:4px 8px; border-radius:999px; font-size:10px; font-weight:600; color:#0a84ff; background:rgba(10,132,255,.12); }
.plan-footer { display:flex; align-items:center; justify-content:space-between; gap:8px; margin-top:8px; }
.done-badge { flex-shrink:0; padding:4px 9px; border-radius:999px; font-size:11px; font-weight:600; color:#0a7d3f; background:rgba(10,125,63,.12); }
.primary-btn { width:100%; border:none; border-radius:12px; padding:10px; margin-top:10px; font-size:13px; font-weight:700; color:#fff; background:linear-gradient(135deg,#0a84ff,#0071e3); }
.primary-btn.done { background:#e8f5ec; color:#0a7d3f; }
.primary-btn:disabled { cursor:not-allowed; opacity:1; }
.empty-title { margin:0; font-size:16px; color:#111; text-align:center; }
.empty-subtitle { margin:8px 0 0; font-size:13px; color:#6e6e73; text-align:center; line-height:1.6; }
</style>
