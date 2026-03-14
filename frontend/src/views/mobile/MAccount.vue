<template>
  <div class="ds-account">
    <div class="page-header">
      <button class="back-btn" @click="router.push('/m/settings')" aria-label="返回">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <h1 class="page-title">账号管理</h1>
    </div>

    <!-- 已登录：修改手机号 + 修改密码 -->
    <div v-if="isAuthed" class="logged-in-section">
      <div class="auth-card">
        <h2 class="card-title">修改手机号</h2>
        <div class="auth-form">
          <div class="field">
            <label>手机号</label>
            <input v-model="phone" type="tel" maxlength="11" placeholder="请输入11位手机号" />
          </div>
          <button class="primary-btn" :disabled="phoneLoading || !phone.trim()" @click="savePhone">
            {{ phoneLoading ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
      <div class="auth-card">
        <h2 class="card-title">修改密码</h2>
        <div class="auth-form">
          <div class="field">
            <label>旧密码</label>
            <input v-model="pwdForm.old_password" type="password" placeholder="请输入当前密码" />
          </div>
          <div class="field">
            <label>新密码</label>
            <input v-model="pwdForm.new_password" type="password" placeholder="请设置新密码(至少6位)" />
          </div>
          <div class="field">
            <label>确认新密码</label>
            <input v-model="pwdForm.confirm_password" type="password" placeholder="再次输入新密码" />
          </div>
          <button
            class="primary-btn"
            :disabled="pwdLoading || !pwdForm.old_password || !pwdForm.new_password || !pwdForm.confirm_password"
            @click="changePassword"
          >
            {{ pwdLoading ? '提交中...' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 未登录：登录和注册 -->
    <div v-else class="auth-card">
      <div class="auth-tabs">
        <button :class="['tab', authTab === 'login' ? 'active' : '']" @click="authTab = 'login'">登录</button>
        <button :class="['tab', authTab === 'register' ? 'active' : '']" @click="authTab = 'register'">注册</button>
      </div>

      <div v-if="authTab === 'login'" class="auth-form">
        <div class="field">
          <label>身份证号</label>
          <input v-model="loginForm.username" maxlength="18" placeholder="请输入身份证号" />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="loginForm.password" type="password" placeholder="请输入密码" />
        </div>
        <button class="primary-btn" :disabled="authLoading" @click="doLogin">
          {{ authLoading ? '登录中...' : '登 录' }}
        </button>
      </div>

      <div v-else class="auth-form">
        <div class="field">
          <label>选择小区</label>
          <select v-model.number="regForm.community_id">
            <option :value="null" disabled>请选择社区</option>
            <option v-for="c in communities" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="field">
          <label>姓名</label>
          <input v-model="regForm.name" maxlength="20" placeholder="请输入姓名" />
        </div>
        <div class="field">
          <label>电话号码</label>
          <input v-model="regForm.phone" type="tel" maxlength="11" placeholder="请输入11位电话号码" />
        </div>
        <div class="field">
          <label>身份证号</label>
          <input v-model="regForm.id_card" maxlength="18" placeholder="请输入18位身份证号" />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="regForm.password" type="password" placeholder="请设置密码(至少6位)" />
        </div>
        <button class="primary-btn" :disabled="authLoading" @click="doRegister">
          {{ authLoading ? '注册中...' : '注 册' }}
        </button>
        <p class="auth-tip">注册成功后会自动登录</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, inject, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const refreshAuth = inject('refreshAuth', () => {})
const isAuthed = inject('isAuthed', ref(!!localStorage.getItem('elder_token')))

const phone = ref('')
const phoneLoading = ref(false)
const pwdLoading = ref(false)
const authTab = ref('login')
const authLoading = ref(false)
const communities = ref([])

const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({ community_id: null, name: '', phone: '', id_card: '', password: '' })
const pwdForm = reactive({ old_password: '', new_password: '', confirm_password: '' })

async function loadMyPhone() {
  try {
    const user = await request.get('/auth/users/me/')
    phone.value = user.phone || ''
  } catch (e) {
    console.error(e)
  }
}

async function savePhone() {
  const v = (phone.value || '').trim()
  if (!v) return alert('请输入手机号')
  if (v.length !== 11 || !/^\d+$/.test(v)) return alert('请输入正确的11位手机号')
  phoneLoading.value = true
  try {
    await request.patch('/auth/users/update-phone/', { phone: v })
    alert('修改成功')
  } catch (e) {
    const msg = e?.response?.data?.phone?.[0] || '修改失败，请重试'
    alert(msg)
  } finally {
    phoneLoading.value = false
  }
}

async function changePassword() {
  const { old_password, new_password, confirm_password } = pwdForm
  if (!old_password) return ElMessage.warning('请输入旧密码')
  if (!new_password) return ElMessage.warning('请输入新密码')
  if (new_password.length < 6) return ElMessage.warning('新密码至少6位')
  if (new_password !== confirm_password) return ElMessage.warning('两次输入的新密码不一致')
  pwdLoading.value = true
  try {
    await request.post('/auth/users/change-password/', {
      old_password,
      new_password,
    })
    ElMessage.success('密码修改成功，请重新登录')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm_password = ''
    localStorage.removeItem('elder_token')
    localStorage.removeItem('token')
    refreshAuth()
    await nextTick()
    router.push('/m/account')
  } catch (e) {
    const data = e.response?.data
    const msg = data?.old_password?.[0] || data?.new_password?.[0] || '修改失败，请重试'
    ElMessage.error(typeof msg === 'string' ? msg : '修改失败，请重试')
  } finally {
    pwdLoading.value = false
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
    refreshAuth()
    await nextTick()
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

onMounted(() => {
  if (isAuthed.value) {
    loadMyPhone()
  } else {
    loadPublicCommunities()
  }
})
</script>

<style scoped>
.ds-account {
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

.logged-in-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.auth-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
  padding: 22px 18px;
}

.card-title {
  margin: 0 0 14px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
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
</style>
