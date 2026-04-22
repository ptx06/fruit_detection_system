<template>
  <div class="settings-container">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      
      <el-form :model="form" label-width="160px" v-loading="loading">
        <el-divider content-position="left">检测参数</el-divider>
        
        <el-form-item label="置信度阈值">
          <el-slider
            v-model="form.detection.conf_threshold"
            :min="0.01"
            :max="1.0"
            :step="0.01"
            show-input
            :show-input-controls="false"
          />
          <div class="hint">值越高，检测框越少但更准确</div>
        </el-form-item>
        
        <el-form-item label="IOU阈值">
          <el-slider
            v-model="form.detection.iou_threshold"
            :min="0.01"
            :max="1.0"
            :step="0.01"
            show-input
            :show-input-controls="false"
          />
          <div class="hint">非极大值抑制阈值，值越高重叠框越多</div>
        </el-form-item>
        
        <el-divider />
        
        <el-form-item>
          <el-button type="primary" @click="saveSettings" :loading="saving">保存设置</el-button>
          <el-button @click="resetSettings">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-alert
        title="提示"
        type="info"
        description="修改设置后立即生效，无需重启服务。"
        show-icon
        :closable="false"
        style="margin-top: 20px"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import client from '@/api/client'
import { ElMessage } from 'element-plus'

interface DetectionSettings {
  conf_threshold: number
  iou_threshold: number
}

interface SystemSettings {
  detection: DetectionSettings
}

const loading = ref(false)
const saving = ref(false)
const originalSettings = ref<SystemSettings>({
  detection: { conf_threshold: 0.25, iou_threshold: 0.45 }
})

const form = reactive<SystemSettings>({
  detection: { conf_threshold: 0.25, iou_threshold: 0.45 }
})

const fetchSettings = async () => {
  loading.value = true
  try {
    const { data } = await client.get('/settings')
    originalSettings.value = data
    form.detection.conf_threshold = data.detection.conf_threshold
    form.detection.iou_threshold = data.detection.iou_threshold
  } catch (error) {
    ElMessage.error('获取设置失败')
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    await client.put('/settings', form)
    ElMessage.success('设置保存成功，已立即生效')
    originalSettings.value = JSON.parse(JSON.stringify(form))
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const resetSettings = () => {
  form.detection.conf_threshold = originalSettings.value.detection.conf_threshold
  form.detection.iou_threshold = originalSettings.value.detection.iou_threshold
}

onMounted(fetchSettings)
</script>

<style scoped>
.settings-container {
  padding: 20px;
  max-width: 800px;
}
.hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>