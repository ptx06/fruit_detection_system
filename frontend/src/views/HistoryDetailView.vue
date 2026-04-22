<template>
  <div class="detail-container">
    <el-card>
      <template #header>
        <el-page-header @back="$router.back()" content="检测详情" />
      </template>
      <div v-loading="loading">
        <el-row :gutter="20">
          <el-col :span="12">
            <div v-if="detail.image_base64" class="image-preview">
              <AnnotatedImage
                :imageSrc="'data:image/jpeg;base64,' + detail.image_base64"
                :detections="detail.result_json || []"
                :maxWidth="500"
              />
            </div>
            <el-empty v-else description="图片丢失" />
          </el-col>
          <el-col :span="12">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="文件名">{{ detail.original_filename }}</el-descriptions-item>
              <el-descriptions-item label="检测时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="水果数量">{{ detail.fruit_count }}</el-descriptions-item>
            </el-descriptions>
            <el-table :data="detail.result_json" style="margin-top: 20px">
              <el-table-column prop="fruit_type" label="种类" width="100" />
              <el-table-column prop="maturity" label="成熟度" />
              <el-table-column prop="fruit_conf" label="检测置信度">
                <template #default="{ row }">
                  {{ (row.fruit_conf * 100).toFixed(1) }}%
                </template>
              </el-table-column>
              <el-table-column prop="maturity_conf" label="分类置信度">
                <template #default="{ row }">
                  {{ (row.maturity_conf * 100).toFixed(1) }}%
                </template>
              </el-table-column>
            </el-table>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getHistoryDetail, type HistoryDetail } from '@/api/history'
import { ElMessage } from 'element-plus'
import AnnotatedImage from '@/components/AnnotatedImage.vue'

const route = useRoute()
const loading = ref(false)
const detail = ref<HistoryDetail>({
  id: 0,
  original_filename: '',
  fruit_count: 0,
  created_at: '',
  result_json: [],
  image_base64: null
})

const fetchDetail = async () => {
  const id = Number(route.params.id)
  if (!id) return
  loading.value = true
  try {
    detail.value = await getHistoryDetail(id)
  } catch (error) {
    ElMessage.error('获取详情失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString()
}

onMounted(fetchDetail)
</script>

<style scoped>
.detail-container {
  padding: 20px;
}
.image-preview img {
  max-width: 100%;
  max-height: 500px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}
</style>