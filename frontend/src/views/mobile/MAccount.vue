<template>
  <div class="ds-account">
    <div class="page-header">
      <button class="back-btn" @click="router.push('/m/settings')" aria-label="返回">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <h1 class="page-title">账号管理</h1>
    </div>

    <!-- 已登录：仅显示修改手机号 -->
    <div v-if="isAuthed" class="auth-card">
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
          <input v-model="regForm.phone" maxlength="20" placeholder="请输入电话号码" />
        </div>
        <div class="field">
          <label>身份证号</label>
          <input v-model="regForm.id_card" maxlength="18" placeholder="请输入身份证号" />
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
import request from '@/utils/request'

const router = useRouter()
const refreshAuth = inject('refreshAuth', () => {})
const isAuthed = inject('isAuthed', ref(!!localStorage.getItem('elder_token')))

const phone = ref('')
const phoneLoading = ref(false)
const authTab = ref('login')
const authLoading = ref(false)
const communities = ref([])

const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({ community_id: null, name: '', phone: '', id_card: '', password: '' })

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
    alert('登录失败，请检查身份证号或密码')
  } finally {
    authLoading.value = false
  }
}

async function doRegister() {
  if (!regForm.community_id) return alert('请选择小区')
  if (!regForm.name) return alert('请输入姓名')
  if (!regForm.phone) return alert('请输入电话号码')
  if (!regForm.id_card) return alert('请输入身份证号')
  if (!regForm.password || regForm.password.length < 6) return alert('密码至少6位')
  authLoading.value = true
  try {
    await request.post('/auth/users/elder-register/', regForm)
    loginForm.username = regForm.id_card
    loginForm.password = regForm.password
    authTab.value = 'login'
    await doLogin()
  } catch (e) {
    const msg = e?.response?.data?.id_card || e?.response?.data?.community_id || '注册失败，请重试'
    alert(typeof msg === 'string' ? msg : '注册失败，请重试')
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

.auth-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
  padding: 22px 18px;
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
