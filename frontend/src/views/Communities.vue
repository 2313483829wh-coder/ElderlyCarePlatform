<template>
  <div>
    <!-- 顶部操作栏 -->
    <div style="margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center;">
      <div style="display: flex; align-items: center; gap: 16px;">
        <h2 style="margin: 0; font-size: 24px; font-weight: 700; color: #1d1d1f;">社区管理</h2>
        <el-input
          v-model="searchQuery"
          placeholder="搜索社区名称、地址、负责人"
          clearable
          style="width: 250px;"
          @input="loadData"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-radio-group v-model="statusFilter" size="default" @change="loadData">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="active">在用</el-radio-button>
          <el-radio-button label="inactive">停用</el-radio-button>
        </el-radio-group>
        <el-tag type="info">共 {{ communities.length }} 个社区</el-tag>
      </div>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><Plus /></el-icon>
        添加社区
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="8" v-for="c in filteredCommunities" :key="c.id">
        <el-card 
          class="community-card" 
          :class="{ inactive: !c.is_active }"
          shadow="hover" 
          @click="$router.push(`/community/${c.id}`)"
          @contextmenu.prevent="openEditDialog(c)">
          <!-- 右上角状态标签 -->
          <div class="status-badge">
            <el-tag :type="c.is_active ? 'success' : 'info'" size="small">
              {{ c.is_active ? '在用' : '停用' }}
            </el-tag>
          </div>
          <div class="card-top">
            <el-icon :size="36" color="#1a73e8"><OfficeBuilding /></el-icon>
            <div>
              <h3>{{ c.name }}</h3>
              <p class="addr">{{ c.address }}</p>
            </div>
          </div>
          <el-divider style="margin: 12px 0;" />
          <div class="card-stats">
            <div class="stat">
              <span class="val">{{ c.elder_count }}</span>
              <span class="lbl">管理老人</span>
            </div>
            <div class="stat">
              <span class="val" :class="{ warn: c.today_reported < c.elder_count }">
                {{ c.today_reported }}/{{ c.elder_count }}
              </span>
              <span class="lbl">今日已上报</span>
            </div>
            <div class="stat">
              <span class="val alert" v-if="c.alert_count > 0">{{ c.alert_count }}</span>
              <span class="val ok" v-else>0</span>
              <span class="lbl">待处理预警</span>
            </div>
          </div>
          <div class="card-footer">
            <span>负责人: {{ c.contact_person }}</span>
            <span>{{ c.contact_phone }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加/编辑社区对话框 -->
    <el-dialog v-model="showEditDialog" :title="isAddMode ? '添加社区' : '编辑社区信息'" width="500px">
      <el-form :model="editForm" label-width="100px" ref="formRef">
        <el-form-item label="社区名称" prop="name" :rules="[{required:true, message:'请输入社区名称'}]">
          <el-input v-model="editForm.name" placeholder="请输入社区名称" />
        </el-form-item>
        <el-form-item label="社区地址" prop="address" :rules="[{required:true, message:'请输入社区地址'}]">
          <el-input v-model="editForm.address" placeholder="请输入社区地址" />
        </el-form-item>
        <el-form-item label="负责人姓名" prop="contact_person" :rules="[{required:true, message:'请输入负责人姓名'}]">
          <el-input v-model="editForm.contact_person" placeholder="请输入负责人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone" :rules="[{required:true, message:'请输入联系电话'}]">
          <el-input v-model="editForm.contact_phone" placeholder="请输入联系电话" maxlength="11" />
        </el-form-item>
        <el-form-item label="社区简介" prop="description">
          <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
        <el-form-item v-if="!isAddMode" label="状态" prop="is_active">
          <el-switch 
            v-model="editForm.is_active" 
            active-text="在用" 
            inactive-text="停用"
            :active-value="true"
            :inactive-value="false" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">{{ isAddMode ? '添加' : '保存' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'

const communities = ref([])
const statusFilter = ref('active')
const searchQuery = ref('') // 新增搜索查询变量
const showEditDialog = ref(false)
const isAddMode = ref(false)
const formRef = ref()
const editForm = reactive({
  id: null,
  name: '',
  address: '',
  contact_person: '',
  contact_phone: '',
  description: '',
  is_active: true,
})

const filteredCommunities = computed(() => {
  let filtered = communities.value
  
  // 状态筛选
  if (statusFilter.value === 'active') {
    filtered = filtered.filter(c => c.is_active)
  } else if (statusFilter.value === 'inactive') {
    filtered = filtered.filter(c => !c.is_active)
  }
  
  // 搜索筛选 (目前在loadData中实现，这里保留以防万一或作为本地过滤备用)
  // if (searchQuery.value) {
  //   const query = searchQuery.value.toLowerCase()
  //   filtered = filtered.filter(c => 
  //     c.name.toLowerCase().includes(query) ||
  //     c.address.toLowerCase().includes(query) ||
  //     c.contact_person.toLowerCase().includes(query)
  //   )
  // }
  
  return filtered
})

async function loadData() {
  const params = {
    search: searchQuery.value, // 将搜索查询参数传递给后端
    is_active: statusFilter.value === 'all' ? undefined : statusFilter.value === 'active' // 将状态筛选参数传递给后端
  }
  const res = await request.get('/communities/', { params })
  communities.value = res.results || res
}

function openAddDialog() {
  isAddMode.value = true
  editForm.id = null
  editForm.name = ''
  editForm.address = ''
  editForm.contact_person = ''
  editForm.contact_phone = ''
  editForm.description = ''
  editForm.is_active = true
  showEditDialog.value = true
}

function openEditDialog(community) {
  isAddMode.value = false
  editForm.id = community.id
  editForm.name = community.name
  editForm.address = community.address
  editForm.contact_person = community.contact_person
  editForm.contact_phone = community.contact_phone
  editForm.description = community.description || ''
  editForm.is_active = community.is_active
  showEditDialog.value = true
}

async function saveEdit() {
  try {
    await formRef.value.validate()
    const data = {
      name: editForm.name,
      address: editForm.address,
      contact_person: editForm.contact_person,
      contact_phone: editForm.contact_phone,
      description: editForm.description || '',
      is_active: editForm.is_active,
    }
    
    if (isAddMode.value) {
      await request.post('/communities/', data)
      ElMessage.success('添加成功')
    } else {
      await request.put(`/communities/${editForm.id}/`, data)
      ElMessage.success('修改成功')
    }
    
    showEditDialog.value = false
    loadData()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(isAddMode.value ? '添加失败，请重试' : '修改失败，请重试')
    }
  }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.community-card {
  cursor: pointer;
  margin-bottom: 24px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  border-radius: 16px;
  background: #fff;
  border: 1px solid #e5e5e7;
  position: relative;
  
  &.inactive {
    opacity: 0.6;
    filter: grayscale(30%);
  }
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
    border-color: #d2d2d7;
  }
  
  :deep(.el-card__body) {
    padding: 28px;
  }
  
  .status-badge {
    position: absolute;
    right: 16px;
    top: 16px;
    z-index: 1;
  }
  
  .card-top {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 4px;
    
    .el-icon {
      color: #0066cc;
    }
    
    h3 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      letter-spacing: -0.3px;
      color: #1d1d1f;
    }
    
    .addr {
      color: #86868b;
      font-size: 14px;
      margin-top: 4px;
      font-weight: 400;
    }
  }
  
  .card-stats {
    display: flex;
    justify-content: space-around;
    text-align: center;
    padding: 20px 0 12px;
    
    .stat {
      .val {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -1px;
        color: #1d1d1f;
        display: block;
      }
      
      .val.warn {
        color: #ff9500;
      }
      
      .val.alert {
        color: #ff3b30;
      }
      
      .val.ok {
        color: #34c759;
      }
      
      .lbl {
        font-size: 13px;
        color: #86868b;
        font-weight: 400;
        margin-top: 4px;
      }
    }
  }
  
  .card-footer {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #f5f5f7;
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    color: #86868b;
    font-weight: 400;
  }
}
</style>
