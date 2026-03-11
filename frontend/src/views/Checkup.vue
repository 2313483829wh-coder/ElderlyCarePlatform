<template>
  <div>
    <h3 style="margin-bottom: 16px;">{{ currentYear }}年 体检完成情况</h3>

    <el-alert v-if="missingList.length" type="warning" :closable="false" style="margin-bottom: 16px;"
              :title="`有 ${missingList.length} 位老人今年体检未完成，请尽快安排！`" />

    <el-table :data="missingList" stripe border>
      <el-table-column prop="community_name" label="社区" width="160" />
      <el-table-column prop="elder_name" label="老人姓名" width="120" />
      <el-table-column label="已完成次数" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="row.done === 0 ? 'danger' : 'warning'" size="default">
            {{ row.done }} / 2
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="还差" width="100" align="center">
        <template #default="{ row }">
          <span style="color: #f56c6c; font-weight: 700; font-size: 16px;">{{ row.missing }}次</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button type="primary" size="small"
                     @click="$router.push(`/checkup/elder/${row.elder_id}`)">查看/录入体检</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const currentYear = new Date().getFullYear()
const missingList = ref([])

onMounted(async () => {
  missingList.value = await request.get('/checkup/missing/')
})
</script>
