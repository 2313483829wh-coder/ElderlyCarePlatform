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

    <div class="form-area" v-if="showForm && isAuthed">
      <div class="form-header">
        <span>{{ t('todayHealthData') }}</span>
        <el-icon v-if="submitted" class="edit-icon" @click="showFormEdit"><Edit /></el-icon>
      </div>
      <div v-if="!submitted" class="form-fields">
        <div class="form-row">
          <span class="label">{{ t('heartRate') }}</span>
          <input v-model.number="form.heart_rate" type="number" :placeholder="t('heartRateUnit')" />
        </div>
        <div class="form-row">
          <span class="label">{{ t('bloodOxygen') }}</span>
          <input v-model.number="form.blood_oxygen" type="number" step="0.1" placeholder="%" />
        </div>
        <div class="form-row bp">
          <span class="label">{{ t('bloodPressure') }}</span>
          <input v-model.number="form.systolic_bp" type="number" :placeholder="t('highPressure')" inputmode="numeric" />
          <span class="sep">/</span>
          <input v-model.number="form.diastolic_bp" type="number" :placeholder="t('lowPressure')" inputmode="numeric" />
        </div>
        <div class="form-row">
          <span class="label">{{ t('temperature') }}</span>
          <input v-model.number="form.temperature" type="number" step="0.1" placeholder="℃" />
        </div>
        <div class="form-row">
          <span class="label">{{ t('bloodSugar') }}</span>
          <input v-model.number="form.blood_sugar" type="number" step="0.1" :placeholder="t('optional')" />
        </div>
        <div class="form-row">
          <span class="label">{{ t('feeling') }}</span>
          <input v-model="form.feeling" type="text" :placeholder="t('howFeelingToday')" />
        </div>
        <div class="form-buttons">
          <button class="submit-form-btn" :disabled="submitting" @click="submitHealth">
            {{ submitting ? t('submitting') : t('submitHealthData') }}
          </button>
          <button class="cancel-form-btn" :disabled="submitting" @click="cancelFormEdit">{{ t('cancel') }}</button>
        </div>
      </div>
      <div v-else class="form-summary">
        <p>{{ t('heartRate') }} {{ form.heart_rate ?? '-' }} · {{ t('bloodOxygen') }} {{ form.blood_oxygen ?? '-' }}% · {{ t('bloodPressure') }} {{ form.systolic_bp ?? '-' }}/{{ form.diastolic_bp ?? '-' }} · {{ t('temperature') }} {{ form.temperature ?? '-' }}℃</p>
        <p v-if="form.feeling">{{ t('feelingPrefix') }}{{ form.feeling }}</p>
      </div>
    </div>

    <div class="form-area guest-tip" v-else>
      <div class="form-header">
        <span>{{ t('todayHealthData') }}</span>
      </div>
      <div class="form-summary">{{ t('guestHealthTip') }}</div>
      <button class="submit-form-btn" @click="router.push('/m/settings')">{{ t('goAccount') }}</button>
    </div>

    <div v-if="attachments.length" class="attachment-bar">
      <div v-for="item in attachments" :key="item.id" class="attachment-chip">
        <img v-if="item.preview" :src="item.preview" alt="附件预览" class="attachment-thumb" />
        <span class="attachment-name">{{ item.name }}</span>
        <button class="attachment-remove" @click="removeAttachment(item.id)">×</button>
      </div>
      <div class="attachment-tip">{{ t('attachTip') }}</div>
    </div>

    <div class="input-area">
      <button class="tool-btn" :class="{ active: recognizing }" @click="toggleVoice" :disabled="sending || guestLimitReached">
        <el-icon :size="18"><Microphone /></el-icon>
      </button>
      <button class="tool-btn" @click="pickPhoto" :disabled="sending || guestLimitReached">
        <el-icon :size="18"><CameraFilled /></el-icon>
      </button>
      <button class="tool-btn" @click="pickFile" :disabled="sending || guestLimitReached">
        <el-icon :size="18"><FolderAdd /></el-icon>
      </button>
      <input
        v-model="inputText"
        type="text"
        :placeholder="guestLimitReached ? t('guestLimit') : t('chatPlaceholder')"
        :disabled="guestLimitReached"
        @keydown.enter.exact.prevent="send"
      />
      <button class="send-btn" :disabled="(!inputText.trim() && !attachments.length) || sending || guestLimitReached" @click="send">
        <el-icon :size="20"><Promotion /></el-icon>
      </button>
    </div>

    <input ref="photoInputRef" type="file" accept="image/*" capture="environment" hidden @change="onFileSelected($event, true)" />
    <input ref="fileInputRef" type="file" accept="image/*,.pdf,.doc,.docx,.txt" hidden @change="onFileSelected($event, false)" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, inject, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Edit, Promotion, Microphone, FolderAdd, CameraFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import aiAvatar from '@/assets/ai-avatar.png'
import { getPreferences } from '@/utils/preferences'
import { useMobileI18n } from '@/utils/mobileI18n'

const route = useRoute()
const router = useRouter()
const { t } = useMobileI18n()
const messagesRef = ref(null)
const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const sending = ref(false)
const sessionId = ref(null)
const submitted = ref(false)
const showForm = ref(true)
const submitting = ref(false)
const photoInputRef = ref(null)
const fileInputRef = ref(null)
const attachments = ref([])
const recognizing = ref(false)
let recognition = null

const isAuthed = inject('isAuthed', ref(!!localStorage.getItem('elder_token')))
const refreshSessions = inject('refreshSessions', () => {})
const setCurrentSession = inject('setCurrentSession', () => {})

const guestUserMessageCount = computed(() => messages.value.filter(m => m.role === 'user').length)
const guestLimitReached = computed(() => !isAuthed.value && guestUserMessageCount.value >= 3)

const form = reactive({
  heart_rate: null,
  blood_oxygen: null,
  systolic_bp: null,
  diastolic_bp: null,
  temperature: null,
  blood_sugar: null,
  feeling: '',
})

const editSnapshot = ref(null)

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

function getSpeechLanguage() {
  return getPreferences().language || 'zh-CN'
}

function buildAttachmentContext() {
  if (!attachments.value.length) return ''
  const summary = attachments.value.map(item => `${item.name}（${item.typeLabel}）`).join('、')
  return `${t('attachedContextPrefix')}${summary}${t('attachedContextSuffix')}`
}

function clearAttachments() {
  attachments.value.forEach(item => {
    if (item.preview) URL.revokeObjectURL(item.preview)
  })
  attachments.value = []
}

function removeAttachment(id) {
  const current = attachments.value.find(item => item.id === id)
  if (current?.preview) URL.revokeObjectURL(current.preview)
  attachments.value = attachments.value.filter(item => item.id !== id)
}

function pickPhoto() {
  photoInputRef.value?.click()
}

function pickFile() {
  fileInputRef.value?.click()
}

function onFileSelected(event, fromCamera) {
  const file = event.target.files?.[0]
  if (!file) return
  const isImage = file.type.startsWith('image/')
  attachments.value.push({
    id: `${Date.now()}-${Math.random()}`,
    name: file.name,
    typeLabel: fromCamera ? t('photoImage') : (isImage ? t('image') : file.type || t('file')),
    preview: isImage ? URL.createObjectURL(file) : '',
  })
  event.target.value = ''
}

function createRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) return null
  const instance = new SpeechRecognition()
  instance.lang = getSpeechLanguage()
  instance.interimResults = false
  instance.maxAlternatives = 1
  instance.onstart = () => { recognizing.value = true }
  instance.onend = () => { recognizing.value = false }
  instance.onerror = () => {
    recognizing.value = false
    ElMessage.warning(t('voiceUnavailable'))
  }
  instance.onresult = event => {
    const transcript = event.results?.[0]?.[0]?.transcript || ''
    inputText.value = [inputText.value.trim(), transcript.trim()].filter(Boolean).join(' ')
  }
  return instance
}

function toggleVoice() {
  if (recognizing.value && recognition) {
    recognition.stop()
    return
  }
  recognition = createRecognition()
  if (!recognition) {
    ElMessage.warning(t('browserNoVoice'))
    return
  }
  recognition.lang = getSpeechLanguage()
  recognition.start()
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
    alert(t('loginRequiredForHealth'))
    router.push('/m/settings')
    return
  }
  if (!form.heart_rate && !form.blood_oxygen && !form.systolic_bp && !form.diastolic_bp && !form.temperature && !form.blood_sugar) {
    alert(t('fillAtLeastOne'))
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

  if (route.query.new) {
    await createNewSession()
    const q = { ...route.query }
    delete q.new
    router.replace({ path: '/m/chat', query: q })
    return
  }

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
  const userContent = [buildAttachmentContext(), content].filter(Boolean).join('\n')

  if (!isAuthed.value) {
    sending.value = true
    loading.value = true
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
      clearAttachments()
      scrollBottom()
    }
    return
  }

  if (!sessionId.value) return
  sending.value = true
  loading.value = true
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
    clearAttachments()
    scrollBottom()
  }
}

function send() {
  const t = inputText.value.trim()
  if ((!t && !attachments.value.length) || sending.value) return
  sendToAI(t)
}

watch(() => route.query.session, () => {
  initOrLoadSession()
})

watch(() => route.query.new, () => {
  initOrLoadSession()
})

watch(() => (isAuthed?.value ?? false), v => {
  if (v) {
    loadTodayHealth()
    initOrLoadSession()
  }
})

onMounted(async () => {
  await loadTodayHealth()
  await initOrLoadSession()
})

onBeforeUnmount(() => {
  if (recognition) {
    recognition.onend = null
    recognition.onerror = null
    recognition.onresult = null
    try {
      recognition.stop()
    } catch {}
  }
  clearAttachments()
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
  margin: 0 14px 10px;
  padding: 12px 14px;
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
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
  gap: 10px;
  margin-top: 10px;
}

.submit-form-btn {
  flex: 1;
  height: 40px;
  background: #111111;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.submit-form-btn:disabled {
  opacity: 0.5;
}

.cancel-form-btn {
  min-width: 72px;
  height: 40px;
  background: transparent;
  color: #6e6e73;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 12px;
  font-size: 14px;
  cursor: pointer;
}

.cancel-form-btn:disabled {
  opacity: 0.5;
}

.guest-tip {
  margin-bottom: 12px;
}

.form-summary {
  font-size: 14px;
  color: #6e6e73;
  line-height: 1.6;
}

.attachment-bar {
  padding: 0 14px 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  background: rgba(255, 255, 255, 0.96);
}

.attachment-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #f2f2f7;
  padding: 6px 10px;
  border-radius: 12px;
}

.attachment-thumb {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  object-fit: cover;
}

.attachment-name {
  font-size: 13px;
  color: #1d1d1f;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-remove {
  border: none;
  background: transparent;
  color: #6e6e73;
  font-size: 18px;
  cursor: pointer;
}

.attachment-tip {
  width: 100%;
  font-size: 12px;
  color: #6e6e73;
  line-height: 1.4;
}

.input-area {
  flex-shrink: 0;
  display: flex;
  gap: 8px;
  padding: 10px 14px 16px;
  background: rgba(255, 255, 255, 0.96);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.tool-btn {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: #f6f6f8;
  color: #4b5563;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.tool-btn.active {
  background: #e9eef7;
  color: #111111;
  border-color: rgba(17, 17, 17, 0.08);
}

.input-area input {
  flex: 1;
  height: 38px;
  padding: 0 14px;
  background: #f2f2f7;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 14px;
  color: #1d1d1f;
  font-size: 15px;
}

.input-area input::placeholder {
  color: #6e6e73;
}

.send-btn {
  width: 38px;
  height: 38px;
  border-radius: 12px;
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
