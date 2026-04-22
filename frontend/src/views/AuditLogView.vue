<template>
  <div class="audit-container">
    <el-card>
      <template #header>
        <span>操作日志审计</span>
      </template>
      <el-table :data="logs" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="action" label="操作" width="100" />
        <el-table-column prop="details" label="详情" />
        <el-table-column prop="ip_address" label="IP地址" width="150" />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '@/api/client'
import { ElMessage } from 'element-plus'

const logs = ref([])
const loading = ref(false)

const fetchLogs = async () => {
  loading.value = true
  try {
    const { data } = await client.get('/admin/logs')
    logs.value = data
  } catch (error) {
    ElMessage.error('获取日志失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchLogs)
</script>

<style scoped>
.audit-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}
</style>