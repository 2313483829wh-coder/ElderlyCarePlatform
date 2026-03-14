<template>
  <el-container class="app-layout">
    <el-aside width="240px" class="app-aside">
      <div class="logo">
        <el-icon :size="28"><House /></el-icon>
        <span>养老管理</span>
      </div>
      <el-menu :default-active="$route.path" router>
        <el-menu-item index="/communities">
          <el-icon><OfficeBuilding /></el-icon>
          <span>社区管理</span>
        </el-menu-item>
        <el-menu-item index="/checkup">
          <el-icon><Document /></el-icon>
          <span>体检管理</span>
        </el-menu-item>
        <el-menu-item index="/alerts" class="alerts-menu-item">
          <el-icon><Bell /></el-icon>
          <span>预警中心</span>
          <span v-if="pendingAlerts > 0" class="alert-dot">{{ pendingAlerts }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <span class="page-title">{{ $route.meta.title }}</span>
        <el-dropdown @command="cmd => { if (cmd === 'logout') handleLogout() }">
          <div class="header-user">
            <el-icon :size="20"><User /></el-icon>
            <span>管理员</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const router = useRouter()
const pendingAlerts = ref(0)

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

onMounted(async () => {
  try {
    const res = await request.get('/alerts/pending/', { skipGlobalErrorTip: true })
    pendingAlerts.value = (res || []).filter(a => a.alert_type === 'health').length
  } catch {}
})
</script>

<style lang="scss" scoped>
.app-layout { 
  height: 100vh; 
  background: #f5f5f7;
}
.app-aside {
  background: #fff;
  border-right: 1px solid #e5e5e7;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  
  .logo {
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.5px;
    color: #1d1d1f;
    border-bottom: 1px solid #e5e5e7;
  }
  
  .el-menu {
    border-right: none;
    background: transparent;
    padding: 12px;
    
    :deep(.el-menu-item) {
      margin: 4px 0;
      border-radius: 10px;
      height: 44px;
      line-height: 44px;
      font-size: 15px;
      color: #1d1d1f;
      transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
      
      &:hover {
        background: #f5f5f7;
        color: #0066cc;
      }
      
      &.is-active {
        background: #0066cc;
        color: #fff;
        font-weight: 500;
      }
      
      .el-icon {
        margin-right: 8px;
      }
    }
  }
  
  .alerts-menu-item {
    position: relative;
  }
  
  .alert-dot {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    min-width: 20px;
    height: 20px;
    line-height: 20px;
    text-align: center;
    font-size: 12px;
    font-weight: 600;
    color: #fff;
    background: #ff3b30;
    border-radius: 10px;
    padding: 0 6px;
    box-shadow: 0 2px 6px rgba(255, 59, 48, 0.4);
  }
}

.app-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid #e5e5e7;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  
  .page-title {
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.5px;
    color: #1d1d1f;
  }
  
  .header-user {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-size: 15px;
    color: #1d1d1f;
    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
    
    &:hover {
      background: #f5f5f7;
    }
  }
}

:deep(.el-main) {
  padding: 32px;
  background: #f5f5f7;
}
</style>
