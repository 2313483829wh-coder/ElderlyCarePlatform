<template>
  <div class="m-login">
    <div class="m-logo-area">
      <div class="m-logo-icon">
        <el-icon :size="64"><House /></el-icon>
      </div>
      <h1>健康助手</h1>
      <p>社区养老健康管理</p>
    </div>
    <div class="m-form">
      <div class="m-field">
        <label>身份证号</label>
        <input v-model="form.username" placeholder="请输入身份证号" maxlength="18" />
      </div>
      <div class="m-field">
        <label>密码</label>
        <input v-model="form.password" type="password" placeholder="请输入密码" />
      </div>
      <button class="m-btn" :disabled="loading" @click="onLogin">
        {{ loading ? '登录中...' : '登 录' }}
      </button>
      <p class="m-tip">密码统一为：123</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '123' })

async function onLogin() {
  if (!form.username) {
    alert('请输入身份证号')
    return
  }
  loading.value = true
  try {
    const res = await request.post('/auth/login/', form)
    localStorage.setItem('elder_token', res.access)
    localStorage.setItem('token', res.access)
    router.push('/m/home')
  } catch {
    alert('身份证号或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.m-login {
  min-height: 100vh;
  background: #f5f5f7;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
}

.m-logo-area {
  text-align: center;
  margin-bottom: 48px;
  animation: fadeInUp 0.6s cubic-bezier(0.25, 0.8, 0.25, 1);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.m-logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  background: #fff;
  border-radius: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  color: #0066cc;
}

.m-logo-area h1 {
  font-size: 32px;
  margin: 12px 0 8px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: #1d1d1f;
}

.m-logo-area p {
  color: #86868b;
  font-size: 16px;
  font-weight: 400;
}

.m-form {
  width: 100%;
  max-width: 380px;
  background: #fff;
  padding: 32px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  animation: fadeInUp 0.6s cubic-bezier(0.25, 0.8, 0.25, 1) 0.1s backwards;
}

.m-field {
  margin-bottom: 20px;
}

.m-field label {
  display: block;
  font-size: 15px;
  color: #1d1d1f;
  margin-bottom: 8px;
  font-weight: 600;
}

.m-field input {
  width: 100%;
  padding: 16px;
  font-size: 17px;
  border: 1px solid #d2d2d7;
  border-radius: 12px;
  outline: none;
  background: #fff;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  color: #1d1d1f;
}

.m-field input:focus {
  border-color: #0066cc;
  box-shadow: 0 0 0 4px rgba(0, 102, 204, 0.1);
}

.m-btn {
  width: 100%;
  padding: 16px;
  font-size: 17px;
  font-weight: 600;
  background: #0066cc;
  color: #fff;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  margin-top: 12px;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.m-btn:active {
  transform: scale(0.98);
}

.m-btn:disabled {
  opacity: 0.5;
}

.m-tip {
  text-align: center;
  color: #86868b;
  font-size: 13px;
  margin-top: 20px;
  font-weight: 400;
}
</style>
