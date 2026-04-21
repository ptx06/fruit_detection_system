<template>
  <div class="detection-container">
    <el-card class="upload-card">
      <h2>水果成熟度分级系统</h2>
      <el-upload
        class="upload-area"
        drag
        :before-upload="beforeUpload"
        :http-request="handleUpload"
        :show-file-list="false"
        accept="image/*"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将图片拖到此处或<em>点击上传</em></div>
      </el-upload>
      <div v-if="loading" class="loading">
        <el-icon class="is-loading"><Loading /></el-icon> 检测中，请稍候...
      </div>
    </el-card>

    <el-row :gutter="20" v-if="result">
      <el-col :span="12">
        <el-card header="原始图片">
          <div class="image-wrapper">
            <img :src="'data:image/jpeg;base64,' + result.data.image_base64" alt="原图" />
            <!-- 可选：在Canvas上绘制检测框，这里为了简洁直接展示原图 -->
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="检测结果">
          <div v-if="result.data.detections.length === 0" class="empty-tip">
            未检测到水果目标
          </div>
          <el-table :data="result.data.detections" stripe style="width: 100%">
            <el-table-column prop="fruit_type" label="水果种类" width="100" />
            <el-table-column prop="fruit_conf" label="检测置信度" width="120">
              <template #default="{ row }">
                {{ (row.fruit_conf * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="maturity" label="成熟度" width="100">
              <template #default="{ row }">
                <el-tag :type="getMaturityTagType(row.maturity_id)">{{ row.maturity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="maturity_conf" label="分类置信度" width="120">
              <template #default="{ row }">
                {{ (row.maturity_conf * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column label="边界框坐标" min-width="180">
              <template #default="{ row }">
                [{{ row.bbox.map(v => Math.round(v)).join(', ') }}]
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Loading } from '@element-plus/icons-vue'
import { detectFruitMaturity, type DetectResponse } from '../api/detection'

const loading = ref(false)
const result = ref<DetectResponse | null>(null)

const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
  }
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
  }
  return isImage && isLt5M
}

const handleUpload = async (options: any) => {
  loading.value = true
  try {
    const response = await detectFruitMaturity(options.file)
    if (response.code === 200) {
      result.value = response
      ElMessage.success(`检测完成，发现 ${response.data.count} 个水果`)
    } else {
      ElMessage.error(response.message || '检测失败')
    }
  } catch (error: any) {
    ElMessage.error('请求失败：' + (error.message || '服务器错误'))
  } finally {
    loading.value = false
  }
}

const getMaturityTagType = (maturityId: number) => {
  // 0:未熟(info), 1:成熟(success), 2:过熟(danger)
  const types = ['info', 'success', 'danger']
  return types[maturityId] || 'info'
}
</script>

<style scoped>
.detection-container {
  max-width: 1400px;
  margin: 20px auto;
  padding: 0 20px;
}
.upload-card {
  margin-bottom: 20px;
}
.upload-area {
  width: 100%;
}
.image-wrapper {
  text-align: center;
}
.image-wrapper img {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
}
.loading {
  margin-top: 15px;
  color: #409eff;
}
.empty-tip {
  text-align: center;
  padding: 40px 0;
  color: #909399;
}
</style>