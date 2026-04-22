
<template>
  <div class="history-container">
    <el-card>
      <template #header>
        <span>检测历史</span>
        <div style="float: right">
          <el-button type="success" @click="exportCSV">导出CSV</el-button>
          <el-button type="primary" @click="$router.push('/detection')">新检测</el-button>
        </div>
      </template>
      <el-table :data="records" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="original_filename" label="文件名" />
        <el-table-column prop="fruit_count" label="水果数量" width="100" />
        <el-table-column prop="created_at" label="检测时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row.id)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        style="margin-top: 20px"
        background
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        @current-change="handlePageChange"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHistoryList, type HistoryRecord } from '@/api/history'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const loading = ref(false)
const records = ref<HistoryRecord[]>([])
const currentPage = ref(1)
const pageSize = 20
const total = ref(0)

const fetchRecords = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize
    const data = await getHistoryList(skip, pageSize)
    records.value = data
    // 注意：后端未返回total，可暂时用records.length，或修改后端返回总数
  } catch (error) {
    ElMessage.error('获取历史记录失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchRecords()
}

const viewDetail = (id: number) => {
  router.push(`/history/${id}`)
}
const exportCSV = async () => {
  try {
    const authStore = useAuthStore()
    const response = await fetch('/api/v1/history/export/csv', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Accept': 'text/csv'
      }
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`网络响应错误: ${errorText}`)
    }
    
    // 确保获取正确的文件名
    const contentDisposition = response.headers.get('content-disposition')
    let filename = `history_${Date.now()}.csv`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="([^"]+)"/)
      if (match) {
        filename = match[1]
      }
    }
    
    const blob = await response.blob()
    // 确保blob类型正确
    const csvBlob = new Blob([blob], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(csvBlob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.style.display = 'none'
    document.body.appendChild(a)
    a.click()
    
    // 延迟清理，确保下载完成
    setTimeout(() => {
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }, 100)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请稍后重试')
  }
}
onMounted(fetchRecords)
</script>

<style scoped>
.history-container {
  padding: 20px;
}
</style>