<template>
  <div class="announcement-container">
    <el-card>
      <template #header>
        <div class="header-content">
          <span>通知公告</span>
          <el-button v-if="authStore.userInfo?.role === 'admin'" type="primary" @click="showCreateDialog = true">
            发布公告
          </el-button>
        </div>
      </template>
      
      <div v-if="loading" class="loading">
        <el-icon class="is-loading"><Loading /></el-icon> 加载中...
      </div>
      
      <div v-else-if="announcements.length === 0" class="empty">
        <el-empty description="暂无公告" />
      </div>
      
      <div v-else class="announcement-list">
        <el-timeline>
          <el-timeline-item
            v-for="announcement in announcements"
            :key="announcement.id"
            :timestamp="formatTime(announcement.created_at)"
            type="primary"
            placement="top"
          >
            <div class="announcement-item">
              <h4 class="announcement-title">{{ announcement.title }}</h4>
              <p class="announcement-content">{{ announcement.content }}</p>
              <div v-if="authStore.userInfo?.role === 'admin'" class="announcement-actions">
                <el-button size="small" type="danger" @click="deleteAnnouncement(announcement.id)">
                  删除
                </el-button>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>

    <!-- 创建公告对话框 -->
    <el-dialog v-model="showCreateDialog" title="发布公告" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" rows="4" placeholder="请输入公告内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createAnnouncement" :loading="creating">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import client from '@/api/client'

interface Announcement {
  id: number
  title: string
  content: string
  created_by: number
  created_at: string | Date
  updated_at: string | Date
}

const authStore = useAuthStore()
const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const formRef = ref<FormInstance>()
const announcements = ref<Announcement[]>([])

const form = ref({
  title: '',
  content: ''
})

const rules = ref<FormRules>({
  title: [{ required: true, message: '请输入公告标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入公告内容', trigger: 'blur' }]
})

const fetchAnnouncements = async () => {
  loading.value = true
  try {
    const { data } = await client.get('/announcements')
    announcements.value = data
  } catch (error) {
    ElMessage.error('获取公告失败')
  } finally {
    loading.value = false
  }
}

const createAnnouncement = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    creating.value = true
    try {
      await client.post('/announcements', form.value)
      ElMessage.success('公告发布成功')
      showCreateDialog.value = false
      form.value.title = ''
      form.value.content = ''
      fetchAnnouncements()
    } catch (error) {
      ElMessage.error('发布失败')
    } finally {
      creating.value = false
    }
  })
}

const deleteAnnouncement = async (id: number) => {
  try {
    await client.delete(`/announcements/${id}`)
    ElMessage.success('公告删除成功')
    fetchAnnouncements()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString()
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<style scoped>
.announcement-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading {
  padding: 40px;
  text-align: center;
  color: #409eff;
}

.empty {
  padding: 60px 0;
}

.announcement-list {
  margin-top: 20px;
}

.announcement-item {
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  margin-bottom: 15px;
  background-color: #fafafa;
}

.announcement-title {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: bold;
}

.announcement-content {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.announcement-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}
</style>