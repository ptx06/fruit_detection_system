
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
      
      <!-- 筛选区域 -->
      <div class="filter-section">
        <el-form :model="filters" inline>
          <el-form-item label="搜索">
            <el-input
              v-model="filters.keyword"
              placeholder="输入文件名关键词"
              class="search-input"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="水果类型">
            <el-select v-model="filters.fruit_type" placeholder="选择水果类型" clearable>
              <el-option label="苹果" value="apple" />
              <el-option label="香蕉" value="banana" />
              <el-option label="橘子" value="orange" />
            </el-select>
          </el-form-item>
          <el-form-item label="成熟度">
            <el-select v-model="filters.maturity" placeholder="选择成熟度" clearable>
              <el-option label="未成熟" value="unripe" />
              <el-option label="成熟" value="ripe" />
              <el-option label="过熟" value="overripe" />
            </el-select>
          </el-form-item>
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="handleDateChange"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHistoryList, type HistoryRecord, type HistoryFilter } from '@/api/history'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const loading = ref(false)
const records = ref<HistoryRecord[]>([])
const currentPage = ref(1)
const pageSize = 20
const total = ref(0)
const dateRange = ref<[string, string] | null>(null)

const filters = reactive<HistoryFilter>({
  keyword: '',
  fruit_type: '',
  maturity: '',
  start_date: '',
  end_date: ''
})

const fetchRecords = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize
    const data = await getHistoryList(skip, pageSize, filters)
    records.value = data.records
    total.value = data.total
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

const handleSearch = () => {
  currentPage.value = 1
  fetchRecords()
}

const handleDateChange = (range: [string, string] | null) => {
  if (range && range.length === 2) {
    filters.start_date = range[0]
    filters.end_date = range[1]
  } else {
    filters.start_date = ''
    filters.end_date = ''
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.fruit_type = ''
  filters.maturity = ''
  filters.start_date = ''
  filters.end_date = ''
  dateRange.value = null
  currentPage.value = 1
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
    
    const contentDisposition = response.headers.get('content-disposition')
    let filename = `history_${Date.now()}.csv`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="([^"]+)"/)
      if (match) {
        filename = match[1]
      }
    }
    
    const blob = await response.blob()
    const csvBlob = new Blob([blob], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(csvBlob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.style.display = 'none'
    document.body.appendChild(a)
    a.click()
    
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

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.search-input {
  width: 200px;
}
</style>