<template>
  <div class="feedback-container">
    <el-card>
      <template #header>
        <div class="header-content">
          <span>反馈中心</span>
          <el-button type="primary" @click="showCreateDialog = true">提交反馈</el-button>
        </div>
      </template>
      
      <div v-if="loading" class="loading">
        <el-icon class="is-loading"><Loading /></el-icon> 加载中...
      </div>
      
      <div v-else-if="feedbacks.length === 0" class="empty">
        <el-empty description="暂无反馈记录" />
      </div>
      
      <div v-else class="feedback-list">
        <el-timeline>
          <el-timeline-item
            v-for="feedback in feedbacks"
            :key="feedback.id"
            :timestamp="formatTime(feedback.created_at)"
            type="primary"
            placement="top"
          >
            <div class="feedback-item">
              <h4 class="feedback-title">{{ feedback.title }}</h4>
              <p class="feedback-content">{{ feedback.content }}</p>
              <div class="feedback-meta">
                <el-tag :type="getStatusType(feedback.status)">{{ getStatusText(feedback.status) }}</el-tag>
                <span v-if="feedback.updated_at && feedback.updated_at !== feedback.created_at" class="updated-time">
                  更新于: {{ formatTime(feedback.updated_at) }}
                </span>
              </div>
              <div v-if="feedback.admin_reply" class="admin-reply">
                <h5 class="reply-title">管理员回复:</h5>
                <p class="reply-content">{{ feedback.admin_reply }}</p>
              </div>
              <div v-if="authStore.userInfo?.role === 'admin'" class="feedback-actions">
                <el-button size="small" @click="showReplyDialog(feedback)">回复</el-button>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>

    <!-- 提交反馈对话框 -->
    <el-dialog v-model="showCreateDialog" title="提交反馈" width="500px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入反馈标题" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="createForm.content" type="textarea" rows="4" placeholder="请输入反馈内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateFeedback" :loading="creating">提交</el-button>
      </template>
    </el-dialog>

    <!-- 管理员回复对话框 -->
    <el-dialog v-model="showReplyDialogVisible" title="回复反馈" width="500px">
      <el-form :model="replyForm" :rules="replyRules" ref="replyFormRef" label-width="80px">
        <el-form-item label="状态" prop="status">
          <el-select v-model="replyForm.status" placeholder="请选择状态">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" />
          </el-select>
        </el-form-item>
        <el-form-item label="回复内容" prop="admin_reply">
          <el-input v-model="replyForm.admin_reply" type="textarea" rows="4" placeholder="请输入回复内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReplyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleReplyFeedback" :loading="replying">回复</el-button>
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

interface Feedback {
  id: number
  title: string
  content: string
  user_id: number
  status: string
  admin_reply: string | null
  created_at: string | Date
  updated_at: string | Date
}

const authStore = useAuthStore()
const loading = ref(false)
const creating = ref(false)
const replying = ref(false)
const showCreateDialog = ref(false)
const showReplyDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const replyFormRef = ref<FormInstance>()
const feedbacks = ref<Feedback[]>([])
const currentFeedback = ref<Feedback | null>(null)

const createForm = ref({
  title: '',
  content: ''
})

const replyForm = ref({
  status: 'pending',
  admin_reply: ''
})

const createRules: FormRules = {
  title: [{ required: true, message: '请输入反馈标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入反馈内容', trigger: 'blur' }]
}

const replyRules: FormRules = {
  status: [{ required: true, message: '请选择状态', trigger: 'blur' }],
  admin_reply: [{ required: true, message: '请输入回复内容', trigger: 'blur' }]
}

const fetchFeedbacks = async () => {
  loading.value = true
  try {
    const { data } = await client.get('/feedback')
    feedbacks.value = data
  } catch (error) {
    ElMessage.error('获取反馈列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreateFeedback = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate(async (valid) => {
    if (!valid) return
    creating.value = true
    try {
      await client.post('/feedback', createForm.value)
      ElMessage.success('反馈提交成功')
      showCreateDialog.value = false
      createForm.value.title = ''
      createForm.value.content = ''
      fetchFeedbacks()
    } catch (error) {
      ElMessage.error('提交失败')
    } finally {
      creating.value = false
    }
  })
}

const showReplyDialog = (feedback: Feedback) => {
  currentFeedback.value = feedback
  replyForm.value.status = feedback.status
  replyForm.value.admin_reply = feedback.admin_reply || ''
  showReplyDialogVisible.value = true
}

const handleReplyFeedback = async () => {
  if (!replyFormRef.value || !currentFeedback.value) return
  await replyFormRef.value.validate(async (valid) => {
    if (!valid) return
    replying.value = true
    try {
      await client.put(`/feedback/${currentFeedback.value.id}`, replyForm.value)
      ElMessage.success('回复成功')
      showReplyDialogVisible.value = false
      fetchFeedbacks()
    } catch (error) {
      ElMessage.error('回复失败')
    } finally {
      replying.value = false
    }
  })
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'pending': return 'info'
    case 'processing': return 'warning'
    case 'resolved': return 'success'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending': return '待处理'
    case 'processing': return '处理中'
    case 'resolved': return '已解决'
    default: return status
  }
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString()
}

onMounted(() => {
  fetchFeedbacks()
})
</script>

<style scoped>
.feedback-container {
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

.feedback-list {
  margin-top: 20px;
}

.feedback-item {
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  margin-bottom: 15px;
  background-color: #fafafa;
}

.feedback-title {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: bold;
}

.feedback-content {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.feedback-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 12px;
  color: #909399;
}

.updated-time {
  font-size: 12px;
  color: #909399;
}

.admin-reply {
  margin-top: 15px;
  padding: 10px;
  background-color: #f0f9eb;
  border: 1px solid #b7eb8f;
  border-radius: 4px;
}

.reply-title {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
  color: #52c41a;
}

.reply-content {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.feedback-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}
</style>