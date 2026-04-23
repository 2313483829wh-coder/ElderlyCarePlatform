<template>
  <div class="mobile-shell">
    <section class="hero-card">
      <p class="hero-eyebrow">Emergency Help</p>
      <h2 class="hero-title">紧急求助</h2>
      <p class="hero-subtitle">遇到突发不适或需要社区协助时，可快速提交求助信息。</p>
    </section>

    <section class="form-card">
      <div class="field-row">
        <label>联系电话</label>
        <input v-model="form.contact_phone" placeholder="方便社区尽快联系你" />
      </div>
      <div class="field-row">
        <label>位置说明</label>
        <input v-model="form.preferred_time" placeholder="例如：家中 3 栋 2 单元 501" />
      </div>
      <div class="field-row textarea">
        <label>求助说明</label>
        <textarea v-model="form.description" rows="4" placeholder="例如：胸闷、头晕，需要尽快上门查看"></textarea>
      </div>
      <button class="primary-btn danger" @click="submitSOS">立即求助</button>
    </section>

    <section class="list-section">
      <div class="section-title">求助记录</div>
      <div v-if="orders.length" class="card-list">
        <article v-for="item in orders" :key="item.id" class="order-card">
          <div class="order-head">
            <strong>{{ item.title }}</strong>
            <span class="status-chip" :class="item.status">{{ item.status_display }}</span>
          </div>
          <p class="order-desc">{{ item.description || '暂无详细说明' }}</p>
          <p v-if="item.response_note" class="order-note">社区反馈：{{ item.response_note }}</p>
        </article>
      </div>
      <section v-else class="empty-state">
        <p class="empty-title">还没有紧急求助记录</p>
      </section>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const orders = ref([])
const form = reactive({ contact_phone: '', preferred_time: '', description: '' })

function normalizeList(res) { return Array.isArray(res) ? res : (res?.results || []) }

async function loadOrders() {
  const res = await request.get('/care/service-orders/my/')
  orders.value = normalizeList(res).filter(item => item.request_type === 'sos')
}

async function submitSOS() {
  if (!form.description.trim()) {
    ElMessage.warning('请填写求助说明')
    return
  }
  await request.post('/care/service-orders/request/', {
    request_type: 'sos',
    service_kind: 'emergency',
    title: '紧急求助',
    contact_phone: form.contact_phone,
    preferred_time: form.preferred_time,
    description: form.description,
    urgency: 'critical',
  })
  ElMessage.success('求助信息已发送，请保持电话畅通')
  form.contact_phone = ''
  form.preferred_time = ''
  form.description = ''
  await loadOrders()
}

onMounted(loadOrders)
</script>

<style scoped>
.mobile-shell { min-height: calc(100vh - 64px); padding:16px; background: radial-gradient(120% 70% at 15% -5%, rgba(255, 59, 48, 0.08), transparent 55%), radial-gradient(90% 60% at 95% 0%, rgba(255, 149, 0, 0.08), transparent 55%), #f5f5f7; display:grid; gap:14px; }
.hero-card,.form-card,.order-card,.empty-state { background: linear-gradient(145deg, #ffffff 0%, #f7f8fa 100%); border:1px solid rgba(0,0,0,0.08); border-radius:22px; box-shadow:0 12px 28px rgba(0,0,0,0.06); }
.hero-card,.form-card,.empty-state { padding:18px; }
.hero-eyebrow { margin:0 0 4px; font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:#8a8a8e; }
.hero-title { margin:0; font-size:28px; color:#111; }
.hero-subtitle { margin:8px 0 0; font-size:14px; color:#6e6e73; }
.field-row { display:grid; grid-template-columns:78px 1fr; gap:8px; align-items:center; margin-bottom:10px; }
.field-row.textarea { align-items:start; }
.field-row label { font-size:13px; color:#6e6e73; padding-top:10px; }
.field-row input,.field-row textarea { width:100%; border:1px solid rgba(0,0,0,0.08); border-radius:12px; padding:10px 12px; background:#fff; color:#111; }
.primary-btn { width:100%; border:none; border-radius:14px; padding:12px; font-size:15px; font-weight:700; color:#fff; background:linear-gradient(135deg,#0a84ff,#0071e3); }
.primary-btn.danger { background:linear-gradient(135deg,#ff453a,#d70015); }
.section-title { padding:0 4px; font-size:17px; font-weight:700; color:#111; }
.card-list { display:grid; gap:10px; margin-top:10px; }
.order-card { padding:14px; }
.order-head { display:flex; justify-content:space-between; gap:8px; align-items:flex-start; }
.status-chip { padding:4px 8px; border-radius:999px; font-size:11px; font-weight:600; }
.status-chip.pending { background:rgba(245,158,11,.12); color:#b45309; }
.status-chip.processing { background:rgba(10,132,255,.12); color:#0a84ff; }
.status-chip.completed { background:rgba(10,125,63,.12); color:#0a7d3f; }
.status-chip.cancelled { background:#f2f2f7; color:#6e6e73; }
.order-desc,.order-note { margin:8px 0 0; font-size:13px; line-height:1.6; color:#6e6e73; }
.order-note { color:#111; }
.empty-title { margin:0; font-size:16px; color:#6e6e73; text-align:center; }
</style>
