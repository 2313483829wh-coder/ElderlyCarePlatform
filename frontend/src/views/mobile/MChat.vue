<template>
  <div class="ds-chat">
    <div class="messages" ref="messagesRef">
      <div
        v-for="m in messages"
        :key="m.id"
        :class="['msg', m.role === 'user' ? 'msg-user' : 'msg-assistant']"
      >
        <div class="msg-avatar" v-if="m.role === 'assistant'">
          <img class="ai-avatar" :src="aiAvatar" alt="AI" />
        </div>
        <div class="msg-bubble">
          <div class="msg-content" v-html="formatContent(m.content)"></div>
        </div>
      </div>
      <div v-if="loading" class="msg msg-assistant">
        <div class="msg-avatar"><img class="ai-avatar" :src="aiAvatar" alt="AI" /></div>
        <div class="msg-bubble loading">
          <span class="dot">·</span><span class="dot">·</span><span class="dot">·</span>
        </div>
      </div>
    </div>

    <!-- 今日数据表 -->
    <div class="form-area" v-if="showForm && isAuthed">
      <div class="form-header">
        <span>今日健康数据</span>
        <el-icon v-if="submitted" class="edit-icon" @click="showFormEdit"><Edit /></el-icon>
      </div>
      <div v-if="!submitted" class="form-fields">
        <div class="form-row">
          <span class="label">心跳</span>
          <input v-model.number="form.heart_rate" type="number" placeholder="次/分" />
        </div>
        <div class="form-row">
          <span class="label">血氧</span>
          <input v-model.number="form.blood_oxygen" type="number" step="0.1" placeholder="%" />
        </div>
        <div class="form-row bp">
          <span class="label">血压</span>
          <input v-model.number="form.systolic_bp" type="number" placeholder="高压" inputmode="numeric" />
          <span class="sep">/</span>
          <input v-model.number="form.diastolic_bp" type="number" placeholder="低压" inputmode="numeric" />
        </div>
        <div class="form-row">
          <span class="label">体温</span>
          <input v-model.number="form.temperature" type="number" step="0.1" placeholder="℃" />
        </div>
        <div class="form-row">
          <span class="label">血糖</span>
          <input v-model.number="form.blood_sugar" type="number" step="0.1" placeholder="选填" />
        </div>
        <div class="form-row">
          <span class="label">感觉</span>
          <input v-model="form.feeling" type="text" placeholder="今天感觉如何" />
        </div>
        <div class="form-buttons">
          <button class="submit-form-btn" :disabled="submitting" @click="submitHealth">
            {{ submitting ? '提交中...' : '提交健康数据' }}
          </button>
          <button class="cancel-form-btn" :disabled="submitting" @click="cancelFormEdit">取消</button>
        </div>
      </div>
      <div v-else class="form-summary">
        <p>心跳 {{ form.heart_rate ?? '-' }} · 血氧 {{ form.blood_oxygen ?? '-' }}% · 血压 {{ form.systolic_bp ?? '-' }}/{{ form.diastolic_bp ?? '-' }} · 体温 {{ form.temperature ?? '-' }}℃</p>
        <p v-if="form.feeling">感觉：{{ form.feeling }}</p>
      </div>
    </div>

    <div class="form-area guest-tip" v-else>
      <div class="form-header">
        <span>今日健康数据</span>
      </div>
      <div class="form-summary">
        目前是游客模式：可以和 AI 对话，但不能上报健康数据、不能保存历史对话。请到【设置 → 账号管理】登录/注册后使用完整功能。
      </div>
      <button class="submit-form-btn" @click="router.push('/m/settings')">去设置</button>
    </div>

    <div class="input-area">
      <input
        v-model="inputText"
        type="text"
        :placeholder="guestLimitReached ? '游客仅可对话 3 条，请登录后继续' : '输入消息，与 AI 交流...'"
        :disabled="guestLimitReached"
        @keydown.enter.exact.prevent="send"
      />
      <button class="send-btn" :disabled="!inputText.trim() || sending || guestLimitReached" @click="send">
        <el-icon :size="20"><Promotion /></el-icon>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, inject, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Edit, Promotion } from '@element-plus/icons-vue'
import request from '@/utils/request'
import aiAvatar from '@/assets/ai-avatar.png'

const route = useRoute()
const router = useRouter()
const messagesRef = ref(null)
const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const sending = ref(false)
const sessionId = ref(null)
const submitted = ref(false)
const showForm = ref(true)
const submitting = ref(false)
const isAuthed = inject('isAuthed', ref(!!localStorage.getItem('elder_token')))

const refreshSessions = inject('refreshSessions', () => {})
const setCurrentSession = inject('setCurrentSession', () => {})

const guestUserMessageCount = computed(() =>
  messages.value.filter(m => m.role === 'user').length
)
const guestLimitReached = computed(() =>
  !isAuthed.value && guestUserMessageCount.value >= 3
)

const form = reactive({
  heart_rate: null, blood_oxygen: null, systolic_bp: null, diastolic_bp: null,
  temperature: null, blood_sugar: null, feeling: '',
})

function formatContent(text) {
  if (!text) return ''
  return text.replace(/\n/g, '<br/>')
}

function scrollBottom() {
  setTimeout(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  }, 50)
}

async function loadTodayHealth() {
  if (!isAuthed.value) {
    submitted.value = false
    return
  }
  try {
    const res = await request.get('/health/my-today/')
    if (res?.data) {
      Object.assign(form, {
        heart_rate: res.data.heart_rate,
        blood_oxygen: res.data.blood_oxygen,
        systolic_bp: res.data.systolic_bp,
        diastolic_bp: res.data.diastolic_bp,
        temperature: res.data.temperature,
        blood_sugar: res.data.blood_sugar,
        feeling: res.data.feeling,
      })
      submitted.value = true
    } else {
      submitted.value = false
    }
  } catch {
    submitted.value = false
  }
}

const editSnapshot = ref(null)

function showFormEdit() {
  editSnapshot.value = {
    heart_rate: form.heart_rate,
    blood_oxygen: form.blood_oxygen,
    systolic_bp: form.systolic_bp,
    diastolic_bp: form.diastolic_bp,
    temperature: form.temperature,
    blood_sugar: form.blood_sugar,
    feeling: form.feeling,
  }
  submitted.value = false
}

function cancelFormEdit() {
  if (editSnapshot.value) {
    Object.assign(form, editSnapshot.value)
    editSnapshot.value = null
  }
  submitted.value = true
}

async function submitHealth() {
  if (!isAuthed.value) {
    alert('登录后才可以上报健康数据')
    router.push('/m/settings')
    return
  }
  if (!form.heart_rate && !form.blood_oxygen && !form.systolic_bp && !form.diastolic_bp && !form.temperature && !form.blood_sugar) {
    alert('请至少填写一项数据')
    return
  }
  submitting.value = true
  try {
    const payload = {}
    if (form.heart_rate != null) payload.heart_rate = Number(form.heart_rate)
    if (form.blood_oxygen != null) payload.blood_oxygen = Number(form.blood_oxygen)
    if (form.systolic_bp != null) payload.systolic_bp = Number(form.systolic_bp)
    if (form.diastolic_bp != null) payload.diastolic_bp = Number(form.diastolic_bp)
    if (form.temperature != null) payload.temperature = Number(form.temperature)
    if (form.blood_sugar != null) payload.blood_sugar = Number(form.blood_sugar)
    if (form.feeling) payload.feeling = form.feeling

    await request.post('/health/submit/', payload)
    submitted.value = true

    const summary = `心跳${form.heart_rate ?? '-'} 血氧${form.blood_oxygen ?? '-'}% 血压${form.systolic_bp ?? '-'}/${form.diastolic_bp ?? '-'} 体温${form.temperature ?? '-'}℃${form.feeling ? ' 感觉：' + form.feeling : ''}`
    if (sessionId.value) {
      await sendToAI(summary)
    }
  } catch (e) {
    if (e?.response?.data?.invalid) {
      form.heart_rate = null
      form.blood_oxygen = null
      form.systolic_bp = null
      form.diastolic_bp = null
      form.temperature = null
      form.blood_sugar = null
      form.feeling = ''
    } else {
      alert('提交失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

async function initOrLoadSession() {
  // 游客模式：不加载/创建会话，仅本地聊天
  if (!isAuthed.value) {
    sessionId.value = null
    messages.value = [{
      id: 'guest-hello',
      role: 'assistant',
      content: '您好！我是您的健康助手郭泽炀。您可以直接问我问题。\n\n如果需要上报今日健康数据或保存历史对话，请先到【设置 → 账号管理】登录/注册。',
      created_at: new Date().toISOString(),
    }]
    scrollBottom()
    return
  }

  const qs = route.query.session
  if (qs) {
    sessionId.value = Number(qs)
    setCurrentSession?.(Number(qs))
    const res = await request.get('/ai/session-messages/', { params: { session_id: qs } })
    messages.value = res.messages || []
    scrollBottom()
    return
  }

  // 如果是从右上角“新建对话”进入，则创建新会话
  if (route.query.new) {
    await createNewSession()
    // 清掉 new 参数，避免刷新重复创建
    const q = { ...route.query }
    delete q.new
    router.replace({ path: '/m/chat', query: q })
    return
  }

  // 否则：默认打开最近一次会话；没有历史才新建
  loading.value = true
  try {
    const list = await request.get('/ai/sessions/')
    const latest = Array.isArray(list) && list.length ? list[0] : null
    if (latest?.id) {
      sessionId.value = Number(latest.id)
      setCurrentSession?.(Number(latest.id))
      const res = await request.get('/ai/session-messages/', { params: { session_id: latest.id } })
      messages.value = res.messages || []
      scrollBottom()
      return
    }
    await createNewSession()
  } catch (e) {
    messages.value = [{
      id: 0,
      role: 'assistant',
      content: '您好！网络好像有点问题，稍后再试试哦。',
      created_at: new Date().toISOString(),
    }]
  } finally {
    loading.value = false
  }
}

async function createNewSession() {
  loading.value = true
  try {
    const res = await request.post('/ai/sessions/new/')
    sessionId.value = res.session_id
    messages.value = res.messages || []
    setCurrentSession?.(res.session_id)
    refreshSessions?.()
    scrollBottom()
  } catch (e) {
    messages.value = [{
      id: 0,
      role: 'assistant',
      content: '您好！请填写下方今日健康数据，或直接输入问题与助手交流。',
      created_at: new Date().toISOString(),
    }]
  } finally {
    loading.value = false
  }
}

async function sendToAI(content) {
  // 游客：走匿名接口
  if (!isAuthed.value) {
    sending.value = true
    loading.value = true
    const userContent = content
    messages.value.push({
      id: 'u' + Date.now(),
      role: 'user',
      content: userContent,
      created_at: new Date().toISOString(),
    })
    inputText.value = ''
    scrollBottom()
    try {
      const history = messages.value
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .slice(-12)
        .map(m => ({ role: m.role, content: m.content }))
      const res = await request.post('/ai/public-chat/', { content: userContent, history })
      messages.value.push({
        id: 'a' + Date.now(),
        role: 'assistant',
        content: res.assistant_message?.content || '（无回复）',
        created_at: new Date().toISOString(),
      })
    } catch (e) {
      const detail = e.response?.data?.detail
      const isGuestLimit = e.response?.status === 403 && typeof detail === 'string' && detail.includes('游客')
      messages.value.push({
        id: 'a' + Date.now(),
        role: 'assistant',
        content: isGuestLimit ? (detail + ' 请到【设置 → 账号管理】登录。') : '抱歉，AI暂时不可用，请稍后再试。',
        created_at: new Date().toISOString(),
      })
    } finally {
      sending.value = false
      loading.value = false
      scrollBottom()
    }
    return
  }

  if (!sessionId.value) return
  sending.value = true
  loading.value = true
  const userContent = content
  messages.value.push({
    id: 'u' + Date.now(),
    role: 'user',
    content: userContent,
    created_at: new Date().toISOString(),
  })
  inputText.value = ''
  scrollBottom()

  try {
    const res = await request.post('/ai/send/', {
      session_id: sessionId.value,
      content: userContent,
    })
    messages.value.push(res.assistant_message)
    refreshSessions?.()
  } catch (e) {
    messages.value.push({
      id: 'a' + Date.now(),
      role: 'assistant',
      content: '抱歉，网络异常，请稍后再试。',
      created_at: new Date().toISOString(),
    })
  } finally {
    sending.value = false
    loading.value = false
    scrollBottom()
  }
}

function send() {
  const t = inputText.value.trim()
  if (!t || sending.value) return
  sendToAI(t)
}

watch(() => route.query.session, () => {
  initOrLoadSession()
})
watch(() => route.query.new, () => {
  initOrLoadSession()
})
// 登录后 isAuthed 变为 true 时，重新加载会话和今日数据
watch(() => (isAuthed?.value ?? false), (v) => {
  if (v) {
    loadTodayHealth()
    initOrLoadSession()
  }
})

onMounted(async () => {
  await loadTodayHealth()
  await initOrLoadSession()
})
</script>

<style scoped>
.ds-chat {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px);
  max-height: calc(100vh - 64px);
  overflow: hidden;
}

.messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
  background: #ffffff;
}

.msg {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.msg-user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #111111;
  flex-shrink: 0;
  overflow: hidden;
}

.ai-avatar {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  object-fit: cover;
  display: block;
}

.msg-user .msg-bubble {
  background: #111111;
  color: #fff;
  border-radius: 16px 16px 4px 16px;
}

.msg-assistant .msg-bubble {
  background: #f2f2f7;
  color: #1d1d1f;
  border-radius: 16px 16px 16px 4px;
}

.msg-bubble {
  max-width: 85%;
  padding: 12px 16px;
  font-size: 16px;
  line-height: 1.6;
}

.msg-bubble.loading {
  color: #6e6e73;
}

.msg-bubble.loading .dot {
  animation: blink 1s infinite;
}

.msg-bubble.loading .dot:nth-child(2) { animation-delay: 0.2s; }
.msg-bubble.loading .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.form-area {
  flex-shrink: 0;
  margin: 0 16px 12px;
  padding: 14px;
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
}

.edit-icon {
  color: #111111;
  cursor: pointer;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.form-row .label {
  width: 56px;
  font-size: 14px;
  color: #6e6e73;
}

.form-row input {
  flex: 1;
  padding: 10px 12px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 10px;
  color: #1d1d1f;
  font-size: 15px;
}

.form-row.bp { min-width: 0; }
.form-row.bp .label { width: 48px; flex-shrink: 0; }
.form-row.bp input { flex: 0.5; min-width: 0; max-width: 95px; }
.form-row.bp .sep { flex-shrink: 0; color: #6e6e73; margin: 0 4px; }

.form-buttons {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.submit-form-btn {
  flex: 1;
  padding: 12px;
  background: #111111;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.submit-form-btn:disabled {
  opacity: 0.5;
}

.cancel-form-btn {
  padding: 12px 20px;
  background: transparent;
  color: #6e6e73;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 10px;
  font-size: 16px;
  cursor: pointer;
}

.cancel-form-btn:disabled {
  opacity: 0.5;
}

.guest-tip {
  margin-bottom: 16px;
}

.form-summary {
  font-size: 14px;
  color: #6e6e73;
  line-height: 1.6;
}

.input-area {
  flex-shrink: 0;
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  padding-bottom: 20px;
  background: rgba(255, 255, 255, 0.96);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.input-area input {
  flex: 1;
  padding: 12px 16px;
  background: #f2f2f7;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 22px;
  color: #1d1d1f;
  font-size: 16px;
}

.input-area input::placeholder {
  color: #6e6e73;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #111111;
  color: #fff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.send-btn:disabled {
  background: #f2f2f7;
  color: #6e6e73;
  cursor: not-allowed;
}
</style>
