<template>
  <div class="m-app">
    <router-view :key="$route.fullPath" />
    <nav class="m-tab">
      <router-link to="/m/home" class="tab-item" active-class="active">
        <el-icon :size="24"><EditPen /></el-icon>
        <span>今日上报</span>
      </router-link>
      <router-link to="/m/history" class="tab-item" active-class="active">
        <el-icon :size="24"><DataLine /></el-icon>
        <span>历史记录</span>
      </router-link>
      <router-link to="/m/checkup" class="tab-item" active-class="active">
        <el-icon :size="24"><Document /></el-icon>
        <span>体检报告</span>
      </router-link>
      <div @click="handleLogout" class="tab-item">
        <el-icon :size="24"><SwitchButton /></el-icon>
        <span>退出</span>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('elder_token')
  router.push('/m/login')
}
</script>

<style scoped>
.m-app {
  min-height: 100vh;
  background: #f5f5f7;
  padding-bottom: 80px;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
  max-width: 500px;
  margin: 0 auto;
}

.m-tab {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 500px;
  display: flex;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-top: 1px solid #e5e5e7;
  padding: 8px 8px 20px;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  text-decoration: none;
  color: #86868b;
  font-size: 11px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
}

.tab-item.active {
  color: #0066cc;
  font-weight: 600;
}

.tab-item:active {
  transform: scale(0.95);
  opacity: 0.6;
}
</style>
