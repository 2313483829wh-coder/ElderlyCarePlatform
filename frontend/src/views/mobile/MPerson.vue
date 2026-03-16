<template>
  <div class="ds-person">
    <div class="page-header">
      <button class="back-btn" @click="router.push('/m/chat')" aria-label="返回">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <h1 class="page-title">设置</h1>
    </div>

    <div class="menu-list">
      <div class="menu-item" @click="router.push('/m/account')">
        <el-icon><User /></el-icon>
        <span>账号管理</span>
        <el-icon class="arrow"><ArrowRight /></el-icon>
      </div>
      <template v-if="isAuthed">
        <div class="menu-item" @click="router.push('/m/history')">
          <el-icon><Document /></el-icon>
          <span>我的健康记录</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
        <div class="menu-item" @click="router.push('/m/checkup')">
          <el-icon><Notebook /></el-icon>
          <span>我的体检报告</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
      </template>
      <div v-if="isAuthed" class="menu-item" @click="handleLogout">
        <el-icon><SwitchButton /></el-icon>
        <span>退出登录</span>
        <el-icon class="arrow"><ArrowRight /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, inject, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { User, SwitchButton, ArrowRight, ArrowLeft, Document, Notebook } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const refreshAuth = inject('refreshAuth', () => {})
const isAuthed = inject('isAuthed', ref(!!localStorage.getItem('elder_token')))
const elderName = ref('')
const submitting = ref(false)
const authTab = ref('login')
const authLoading = ref(false)
const communities = ref([])

const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({ community_id: null, name: '', phone: '', id_card: '', password: '' })

const form = reactive({
  heart_rate: null, blood_oxygen: null, systolic_bp: null, diastolic_bp: null,
  temperature: null, blood_sugar: null, feeling: '',
})

async function loadTodayHealth() {
  try {
    const user = await request.get('/auth/users/me/')
    elderName.value = user.name || '用户'

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
    }
  } catch (e) {
    console.error(e)
  }
}

async function loadPublicCommunities() {
  try {
    communities.value = await request.get('/communities/public/')
  } catch (e) {
    communities.value = []
  }
}

async function doLogin() {
  if (!loginForm.username) return alert('请输入身份证号')
  if (!loginForm.password) return alert('请输入密码')
  authLoading.value = true
  try {
    const res = await request.post('/auth/login/', loginForm)
    localStorage.setItem('elder_token', res.access)
    localStorage.setItem('token', res.access)
    refreshAuth() // 立即同步更新 MLayout 及所有子组件的 isAuthed 状态
    await loadTodayHealth()
    await nextTick() // 确保 MLayout 的 isAuthed 已同步
    await router.push('/m/chat')
  } catch (e) {
    const d = e.response?.data?.detail
    const msg = typeof d === 'string' ? d : Array.isArray(d) ? d[0] : null
    ElMessage.error(msg || '账户不存在或密码错误')
  } finally {
    authLoading.value = false
  }
}

function validateIdCard(v) {
  const s = (v || '').trim()
  if (!s) return '请输入身份证号'
  if (s.length !== 18) return '身份证号为18位'
  if (!/^\d{17}[\dXx]$/.test(s)) return '身份证号格式不正确'
  return null
}
function validatePhone(v) {
  const s = (v || '').trim()
  if (!s) return '请输入电话号码'
  if (s.length !== 11 || !/^\d+$/.test(s)) return '请输入正确的11位电话号码'
  return null
}

async function doRegister() {
  if (!regForm.community_id) {
    ElMessage.warning('请选择小区')
    return
  }
  if (!(regForm.name || '').trim()) {
    ElMessage.warning('请输入姓名')
    return
  }
  const phoneErr = validatePhone(regForm.phone)
  if (phoneErr) {
    ElMessage.warning(phoneErr)
    return
  }
  const idCardErr = validateIdCard(regForm.id_card)
  if (idCardErr) {
    ElMessage.warning(idCardErr)
    return
  }
  if (!regForm.password || regForm.password.length < 6) {
    ElMessage.warning('密码至少6位')
    return
  }
  authLoading.value = true
  try {
    await request.post('/auth/users/elder-register/', {
      ...regForm,
      phone: (regForm.phone || '').trim(),
      id_card: (regForm.id_card || '').trim().toUpperCase(),
    })
    // 注册成功后自动登录
    loginForm.username = regForm.id_card
    loginForm.password = regForm.password
    authTab.value = 'login'
    await doLogin()
  } catch (e) {
    const msg = e?.response?.data?.id_card || e?.response?.data?.community_id || e?.response?.data?.phone || '注册失败，请重试'
    ElMessage.error(typeof msg === 'string' ? msg : Array.isArray(msg) ? msg[0] : '注册失败，请重试')
  } finally {
    authLoading.value = false
  }
}

async function submitEdit() {
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
    alert('修改成功')
    showEditModal.value = false
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
      alert('保存失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

function handleLogout() {
  localStorage.removeItem('elder_token')
  localStorage.removeItem('token')
  isAuthed.value = false
  router.push('/m/settings')
}

onMounted(async () => {
  if (isAuthed.value) {
    await loadTodayHealth()
  } else {
    await loadPublicCommunities()
  }
})
</script>

<style scoped>
.ds-person {
  padding: 24px 16px;
  min-height: calc(100vh - 64px);
  background: #ffffff;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.back-btn {
  padding: 8px;
  margin: -8px 0 0 -8px;
  border: none;
  background: transparent;
  color: #1d1d1f;
  cursor: pointer;
  border-radius: 8px;
}

.back-btn:hover {
  background: rgba(0, 0, 0, 0.06);
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1d1d1f;
}

.section-block {
  margin-bottom: 24px;
}

.section-title {
  margin: 0 0 12px;
  font-size: 17px;
  font-weight: 600;
  color: #1d1d1f;
}

.auth-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
  padding: 22px 18px;
}

.auth-title {
  margin: 0 0 14px;
  font-size: 20px;
  color: #1d1d1f;
  font-weight: 700;
}

.auth-tabs {
  display: flex;
  background: #f2f2f7;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 16px;
}

.tab {
  flex: 1;
  border: none;
  background: transparent;
  padding: 10px 0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #6e6e73;
  cursor: pointer;
}

.tab.active {
  background: #ffffff;
  color: #1d1d1f;
  box-shadow: 0 6px 14px rgba(0,0,0,0.08);
}

.auth-form .field {
  margin-bottom: 14px;
}

.auth-form label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 8px;
}

.auth-form input,
.auth-form select {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid rgba(0,0,0,0.12);
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  background: #ffffff;
}

.primary-btn {
  width: 100%;
  padding: 14px;
  background: #111111;
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.primary-btn:disabled {
  opacity: 0.5;
}

.auth-tip {
  margin: 12px 0 0;
  color: #6e6e73;
  font-size: 13px;
  text-align: center;
}

.person-card {
  text-align: center;
  padding: 32px 24px;
  background: #ffffff;
  border-radius: 16px;
  margin-bottom: 24px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}

.avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #111111;
}

.person-card h2 {
  font-size: 22px;
  color: #1d1d1f;
  margin: 0 0 8px;
}

.tip {
  font-size: 14px;
  color: #6e6e73;
  margin: 0;
}

.menu-list {
  background: #ffffff;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  color: #1d1d1f;
  font-size: 16px;
  cursor: pointer;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item .menu-extra {
  flex: 1;
  text-align: right;
  font-size: 13px;
  color: #6e6e73;
  margin-right: 4px;
}

.dialog-tip,
.dialog-example,
.dialog-tip-small {
  margin: 0 0 8px;
  font-size: 14px;
  color: #6e6e73;
}
.dialog-example {
  font-family: monospace;
  color: #1d1d1f;
}
.dialog-tip-small {
  font-size: 12px;
  margin-bottom: 12px;
}
.server-url-dialog :deep(.el-input) {
  margin-top: 8px;
}

.menu-item .el-icon {
  font-size: 22px;
  color: #111111;
}

.menu-item .arrow {
  margin-left: auto;
  color: #6e6e73;
  font-size: 16px;
}

.edit-form {
  padding: 8px 0;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.form-row .label {
  width: 60px;
  font-size: 15px;
  color: #333;
}

.form-row input {
  flex: 1;
  padding: 12px 14px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 15px;
}

.form-row.bp input { flex: 0.5; }
.form-row.bp .sep { color: #666; }

.submit-btn {
  width: 100%;
  padding: 14px;
  margin-top: 20px;
  background: #111111;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.5;
}

:deep(.el-dialog) {
  background: #fff;
  border-radius: 16px;
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid #eee;
}
</style>
