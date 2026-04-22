<template>
  <div class="batch-container">
    <el-card>
      <template #header>
        <span>批量检测</span>
      </template>

      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        multiple
        :auto-upload="false"
        :before-upload="beforeUpload"
        :on-change="handleFileChange"
        :file-list="fileList"
        accept="image/*"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将图片拖到此处或<em>点击上传</em>（最多10张）</div>
      </el-upload>

      <div style="margin-top: 20px; text-align: center">
        <el-button type="primary" @click="submitBatch" :loading="loading" :disabled="fileList.length === 0">
          开始批量检测
        </el-button>
      </div>

      <el-divider v-if="results.length > 0" />

      <div v-if="results.length > 0">
        <h3>检测结果</h3>
        <el-table :data="results" stripe>
          <el-table-column prop="filename" label="文件名" />
          <el-table-column prop="success" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.success ? 'success' : 'danger'">
                {{ row.success ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="fruit_count" label="水果数量" width="120" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button v-if="row.success" type="primary" size="small" @click="viewDetail(row.record_id)">
                查看详情
              </el-button>
              <span v-else style="color: #f56c6c">{{ row.error }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type UploadInstance, type UploadFile } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import client from '@/api/client'

const router = useRouter()
const uploadRef = ref<UploadInstance>()
const fileList = ref<UploadFile[]>([])
const loading = ref(false)
const results = ref<any[]>([])

const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB!')
    return false
  }
  return true
}

const handleFileChange = (file: UploadFile, files: UploadFile[]) => {
  if (files.length > 10) {
    ElMessage.warning('最多只能上传10张图片')
    // 截断到10个
    fileList.value = files.slice(0, 10)
  } else {
    fileList.value = files
  }
}

const submitBatch = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择图片')
    return
  }

  loading.value = true
  const formData = new FormData()
  fileList.value.forEach(file => {
    formData.append('files', file.raw!)
  })

  try {
    const { data } = await client.post('/detect/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (data.code === 200) {
      results.value = data.data
      ElMessage.success(`批量检测完成，成功${data.data.filter((r: any) => r.success).length}张`)
    }
  } catch (error) {
    ElMessage.error('批量检测失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (recordId: number) => {
  router.push(`/history/${recordId}`)
}
</script>

<style scoped>
.batch-container {
  padding: 20px;
}
.upload-area {
  width: 100%;
}
</style>