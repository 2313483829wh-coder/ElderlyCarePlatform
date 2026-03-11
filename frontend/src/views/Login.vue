<template>
  <div class="login-page">
    <div class="login-card">
      <h2>社区养老管理平台</h2>
      <p class="subtitle">Community Elderly Care Platform</p>
      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="onLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" prefix-icon="User" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" prefix-icon="Lock"
                    placeholder="密码" size="large" show-password />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" style="width: 100%"
                   @click="onLogin">登 录</el-button>
      </el-form>
      <div class="tip">管理员: admin / admin123</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: 'admin', password: 'admin123' })
const rules = {
  username: [{ required: true, message: '请输入用户名' }],
  password: [{ required: true, message: '请输入密码' }],
}

async function onLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await request.post('/auth/login/', form)
    localStorage.setItem('token', res.access)
    router.push('/communities')
  } catch {
    ElMessage.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f7;
  position: relative;
  overflow: hidden;
}

.login-page::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 20% 50%, rgba(0, 102, 204, 0.03) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(175, 82, 222, 0.03) 0%, transparent 50%);
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(30px, -30px) rotate(120deg); }
  66% { transform: translate(-20px, 20px) rotate(240deg); }
}

.login-card {
  width: 420px;
  padding: 56px 48px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  text-align: center;
  position: relative;
  animation: slideUp 0.6s cubic-bezier(0.25, 0.8, 0.25, 1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-card h2 {
  margin-bottom: 8px;
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -1px;
  color: #1d1d1f;
}

.subtitle {
  color: #86868b;
  font-size: 15px;
  margin-bottom: 40px;
  font-weight: 400;
  letter-spacing: 0.2px;
}

.tip {
  margin-top: 24px;
  color: #86868b;
  font-size: 13px;
  font-weight: 400;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: none;
  border: 1px solid #d2d2d7;
  background: #fff;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  padding: 12px 16px;
}

:deep(.el-input__wrapper:hover) {
  border-color: #0066cc;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #0066cc !important;
  box-shadow: 0 0 0 4px rgba(0, 102, 204, 0.1) !important;
}

:deep(.el-input__inner) {
  font-size: 16px;
  color: #1d1d1f;
}

:deep(.el-button--primary) {
  background: #0066cc;
  border: none;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 0.3px;
  border-radius: 12px;
  height: 48px;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
}

:deep(.el-button--primary:hover) {
  background: #0077ed;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0, 102, 204, 0.3);
}

:deep(.el-button--primary:active) {
  transform: translateY(0);
}
</style>
