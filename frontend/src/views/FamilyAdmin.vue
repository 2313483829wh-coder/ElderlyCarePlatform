<template>
  <div class="page-shell">
    <div class="page-toolbar">
      <el-input v-model="filters.search" clearable placeholder="搜索老人/家属/电话" style="width: 260px" />
      <el-button type="primary" @click="loadContacts">查询</el-button>
      <el-button type="primary" plain @click="openDialog()">新增家属联系人</el-button>
    </div>

    <el-table :data="contacts" border stripe>
      <el-table-column prop="elder_name" label="老人" width="110" />
      <el-table-column prop="community_name" label="社区" width="140" />
      <el-table-column prop="name" label="家属姓名" width="120" />
      <el-table-column prop="relation_display" label="关系" width="100" />
      <el-table-column prop="phone" label="联系电话" width="140" />
      <el-table-column label="主要联系人" width="110">
        <template #default="{ row }">
          <el-tag :type="row.is_primary ? 'success' : 'info'">{{ row.is_primary ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="notes" label="备注" min-width="180" />
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button text type="danger" @click="removeContact(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑家属联系人' : '新增家属联系人'" width="620px">
      <el-form :model="form" label-width="88px">
        <el-form-item label="老人">
          <el-select v-model="form.elder" filterable style="width: 100%" placeholder="请选择老人">
            <el-option v-for="item in elders" :key="item.id" :label="`${item.name} · ${item.community_name}`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="关系">
            <el-select v-model="form.relation" style="width:100%">
              <el-option label="子女" value="child" />
              <el-option label="配偶" value="spouse" />
              <el-option label="兄弟姐妹" value="sibling" />
              <el-option label="亲属" value="relative" />
              <el-option label="邻居" value="neighbor" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item></el-col>
        </el-row>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="主要联系人"><el-switch v-model="form.is_primary" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitContact">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const contacts = ref([])
const elders = ref([])
const dialogVisible = ref(false)
const filters = reactive({ search: '' })
const form = reactive({ id: null, elder: null, name: '', relation: 'child', phone: '', is_primary: false, notes: '' })

function normalizeList(res) { return Array.isArray(res) ? res : (res?.results || []) }

async function loadElders() {
  elders.value = normalizeList(await request.get('/auth/elders/', { params: { is_active: true } }))
}

async function loadContacts() {
  const params = {}
  if (filters.search) params.search = filters.search
  contacts.value = normalizeList(await request.get('/care/families/', { params }))
}

function resetForm() {
  Object.assign(form, { id: null, elder: null, name: '', relation: 'child', phone: '', is_primary: false, notes: '' })
}

function openDialog(row = null) {
  if (!row) {
    resetForm()
  } else {
    Object.assign(form, { id: row.id, elder: row.elder, name: row.name, relation: row.relation, phone: row.phone, is_primary: row.is_primary, notes: row.notes })
  }
  dialogVisible.value = true
}

async function submitContact() {
  if (!form.elder || !form.name.trim() || !form.phone.trim()) {
    ElMessage.warning('请填写完整联系人信息')
    return
  }
  const payload = { elder: form.elder, name: form.name, relation: form.relation, phone: form.phone, is_primary: form.is_primary, notes: form.notes }
  if (form.id) {
    await request.patch(`/care/families/${form.id}/`, payload)
  } else {
    await request.post('/care/families/', payload)
  }
  ElMessage.success('家属联系人已保存')
  dialogVisible.value = false
  await loadContacts()
}

async function removeContact(row) {
  await ElMessageBox.confirm(`确定删除联系人 ${row.name} 吗？`, '提示', { type: 'warning' })
  await request.delete(`/care/families/${row.id}/`)
  ElMessage.success('已删除')
  await loadContacts()
}

onMounted(async () => {
  await loadElders()
  await loadContacts()
})
</script>

<style scoped>
.page-shell { display:grid; gap:16px; }
.page-toolbar { display:flex; gap:12px; align-items:center; justify-content:flex-end; flex-wrap:wrap; }
</style>
