<template>
  <div class="m-home">
    <div class="greeting">
      <div class="user-info">
        <h2>{{ elderName }}</h2>
        <p class="date-text">{{ todayText }}</p>
      </div>
    </div>

    <!-- AI 助手提示 -->
    <div class="ai-card" v-if="!submitted">
      <div class="ai-icon">
        <el-icon :size="28"><ChatDotRound /></el-icon>
      </div>
      <div class="ai-content">
        <p class="ai-label">健康助手</p>
        <p class="ai-text">{{ aiMessage }}</p>
      </div>
    </div>

    <div class="ai-card success-card" v-else>
      <div class="ai-icon success-icon">
        <el-icon :size="28"><CircleCheck /></el-icon>
      </div>
      <div class="ai-content">
        <p class="ai-label">提交成功</p>
        <p class="ai-text">今日数据已上传，请注意休息</p>
        <p class="ai-warning" v-if="anomalies.length">
          <el-icon><Warning /></el-icon>
          {{ anomalies.join('、') }}，建议关注或咨询医生
        </p>
      </div>
    </div>

    <!-- 填报表单 -->
    <div class="form-card" v-if="!submitted">
      <div class="form-row">
        <label>
          <el-icon><Aim /></el-icon>
          平均心跳数 <small>(次/分钟)</small>
        </label>
        <input v-model="form.heart_rate" type="number" placeholder="例如: 72" />
      </div>
      <div class="form-row">
        <label>
          <el-icon><WindPower /></el-icon>
          血氧饱和度 <small>(%)</small>
        </label>
        <input v-model="form.blood_oxygen" type="number" step="0.1" placeholder="例如: 97.5" />
      </div>
      <div class="form-row">
        <label>
          <el-icon><TrendCharts /></el-icon>
          血压 <small>(mmHg)</small>
        </label>
        <div class="bp-row">
          <input v-model="form.systolic_bp" type="number" placeholder="高压 130" />
          <span class="bp-sep">/</span>
          <input v-model="form.diastolic_bp" type="number" placeholder="低压 80" />
        </div>
      </div>
      <div class="form-row">
        <label>
          <el-icon><Sunny /></el-icon>
          体温 <small>(℃)</small>
        </label>
        <input v-model="form.temperature" type="number" step="0.1" placeholder="例如: 36.5" />
      </div>
      <div class="form-row">
        <label>
          <el-icon><IceCreamSquare /></el-icon>
          空腹血糖 <small>(mmol/L，选填)</small>
        </label>
        <input v-model="form.blood_sugar" type="number" step="0.1" placeholder="例如: 5.6" />
      </div>
      <div class="form-row">
        <label>
          <el-icon><ChatLineRound /></el-icon>
          今天感觉怎么样？
        </label>
        <textarea v-model="form.feeling" placeholder="随便说说，例如：今天感觉不错" rows="3"></textarea>
      </div>
      <button class="submit-btn" :disabled="submitting" @click="submitData">
        {{ submitting ? '正在提交...' : '提交今日数据' }}
      </button>
    </div>

    <div class="form-card submitted-card" v-else>
      <el-icon :size="48" color="#34c759" style="margin-bottom: 12px;"><CircleCheck /></el-icon>
      <p class="success-text">今日数据已成功提交</p>
      <div class="submitted-info">
        <p><strong>心跳:</strong> {{ form.heart_rate || '-' }} 次/分钟</p>
        <p><strong>血氧:</strong> {{ form.blood_oxygen || '-' }} %</p>
        <p><strong>血压:</strong> {{ form.systolic_bp || '-' }}/{{ form.diastolic_bp || '-' }} mmHg</p>
        <p><strong>体温:</strong> {{ form.temperature || '-' }} ℃</p>
        <p v-if="form.blood_sugar"><strong>血糖:</strong> {{ form.blood_sugar }} mmol/L</p>
        <p v-if="form.feeling"><strong>感觉:</strong> {{ form.feeling }}</p>
      </div>
      <button class="edit-btn" @click="submitted = false">修改今日数据</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, onActivated } from 'vue'
import request from '@/utils/request'
import { ChatDotRound, CircleCheck, Warning, Aim, WindPower, TrendCharts, Sunny, IceCreamSquare, ChatLineRound } from '@element-plus/icons-vue'

const elderName = ref('')
const submitted = ref(false)
const submitting = ref(false)
const anomalies = ref([])
const form = reactive({
  heart_rate: null, blood_oxygen: null, systolic_bp: null, diastolic_bp: null,
  temperature: null, blood_sugar: null, feeling: '',
})

const todayText = computed(() => {
  const d = new Date()
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 星期${weekDays[d.getDay()]}`
})

const aiMessage = computed(() => {
  const hour = new Date().getHours()
  if (hour < 10) return '早上好！请测量并填写今日的健康数据'
  if (hour < 14) return '中午好！今日的健康数据还没上报哦'
  return '下午好！记得测量心跳、血氧、血压后填写提交'
})

// 加载当前老人今日健康数据
async function loadTodayHealth() {
  try {
    const user = await request.get('/auth/users/me/')
    elderName.value = user.name || '用户'
    
    // 无论是否关联档案，都尝试获取今日健康数据
    const res = await request.get(`/health/my-today/`)
    if (res && res.data) { // 如果今天有数据
      Object.assign(form, {
        heart_rate: res.data.heart_rate,
        blood_oxygen: res.data.blood_oxygen,
        systolic_bp: res.data.systolic_bp,
        diastolic_bp: res.data.diastolic_bp,
        temperature: res.data.temperature,
        blood_sugar: res.data.blood_sugar,
        feeling: res.data.feeling,
      })
      anomalies.value = res.data.anomalies || []
      submitted.value = true
    } else {
      // 今天没有数据，清空表单
      Object.assign(form, {
        heart_rate: null, blood_oxygen: null, systolic_bp: null, diastolic_bp: null,
        temperature: null, blood_sugar: null, feeling: '',
      })
      anomalies.value = []
      submitted.value = false
    }
  } catch (e) {
    console.error('加载今日健康数据失败:', e)
    // 即使失败也清空表单并显示未提交状态
    Object.assign(form, {
      heart_rate: null, blood_oxygen: null, systolic_bp: null, diastolic_bp: null,
      temperature: null, blood_sugar: null, feeling: '',
    })
    anomalies.value = []
    submitted.value = false
  }
}

async function submitData() {
  if (!form.heart_rate && !form.blood_oxygen && !form.systolic_bp && !form.diastolic_bp && !form.temperature && !form.blood_sugar) {
    alert('请至少填写一项核心数据')
    return
  }
  submitting.value = true
  try {
    const payload = {}
    // 只添加非空的字段
    if (form.heart_rate !== null) payload.heart_rate = Number(form.heart_rate)
    if (form.blood_oxygen !== null) payload.blood_oxygen = Number(form.blood_oxygen)
    if (form.systolic_bp !== null) payload.systolic_bp = Number(form.systolic_bp)
    if (form.diastolic_bp !== null) payload.diastolic_bp = Number(form.diastolic_bp)
    if (form.temperature !== null) payload.temperature = Number(form.temperature)
    if (form.blood_sugar !== null) payload.blood_sugar = Number(form.blood_sugar)
    if (form.feeling) payload.feeling = form.feeling

    const res = await request.post('/health/submit/', payload)
    anomalies.value = res.anomalies || []
    submitted.value = true
    alert('提交成功！')
    await loadTodayHealth() // 提交成功后重新加载数据，确保显示最新状态
  } catch (e) {
    console.error('提交失败:', e)
    alert('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 将onMounted替换为onActivated
onActivated(() => {
  loadTodayHealth()
})
</script>

<style scoped>
.m-home {
  padding: 24px 16px;
}

.greeting {
  margin-bottom: 24px;
  padding: 24px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.user-info h2 {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: #1d1d1f;
  margin-bottom: 6px;
}

.date-text {
  font-size: 15px;
  color: #86868b;
  font-weight: 400;
}

.ai-card {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 20px;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e5e5e7;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.ai-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #f5f5f7;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #0066cc;
}

.success-card {
  border-color: #34c759;
  background: linear-gradient(135deg, #fff 0%, #f0fdf4 100%);
}

.success-icon {
  background: #34c759;
  color: #fff;
}

.ai-content {
  flex: 1;
}

.ai-label {
  font-size: 13px;
  font-weight: 600;
  color: #86868b;
  margin-bottom: 4px;
}

.ai-text {
  font-size: 16px;
  line-height: 1.5;
  color: #1d1d1f;
  font-weight: 400;
  margin: 0;
}

.ai-warning {
  margin-top: 12px;
  padding: 12px;
  background: #fff3cd;
  border-radius: 8px;
  font-size: 14px;
  color: #ff9500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.form-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.form-row {
  margin-bottom: 24px;
  
  label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 16px;
    font-weight: 600;
    color: #1d1d1f;
    margin-bottom: 8px;
    
    small {
      font-size: 13px;
      color: #86868b;
      font-weight: 400;
    }
    
    .el-icon {
      color: #0066cc;
    }
  }
  
  input,
  textarea {
    width: 100%;
    padding: 14px;
    font-size: 17px;
    border: 1px solid #d2d2d7;
    border-radius: 10px;
    outline: none;
    background: #fff;
    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
    color: #1d1d1f;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
  }
  
  input:focus,
  textarea:focus {
    border-color: #0066cc;
    box-shadow: 0 0 0 4px rgba(0, 102, 204, 0.1);
  }
  
  textarea {
    resize: none;
    line-height: 1.5;
  }
}

.bp-row {
  display: flex;
  align-items: center;
  gap: 12px;
  
  input {
    flex: 1;
  }
  
  .bp-sep {
    font-size: 20px;
    font-weight: 400;
    color: #86868b;
  }
}

.submit-btn {
  width: 100%;
  padding: 16px;
  font-size: 17px;
  font-weight: 600;
  background: #0066cc;
  color: #fff;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  margin-top: 8px;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.submit-btn:active {
  transform: scale(0.98);
}

.submit-btn:disabled {
  opacity: 0.5;
}

.submitted-card {
  text-align: center;
  padding: 40px 24px;
}

.success-text {
  font-size: 18px;
  color: #1d1d1f;
  margin: 0 0 20px;
  font-weight: 600;
}

.submitted-info {
  text-align: left;
  margin: 24px 0;
  padding: 20px;
  background: #f5f5f7;
  border-radius: 12px;
  
  p {
    margin: 8px 0;
    font-size: 15px;
    color: #1d1d1f;
    line-height: 1.6;
    
    strong {
      font-weight: 600;
      color: #0066cc;
      margin-right: 8px;
    }
  }
}

.edit-btn {
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 600;
  background: #f5f5f7;
  color: #1d1d1f;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.edit-btn:active {
  transform: scale(0.95);
  background: #e5e5e7;
}
</style>
