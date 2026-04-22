<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 左侧：个人信息卡片 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>个人信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">{{ authStore.userInfo?.username }}</el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag :type="authStore.userInfo?.role === 'admin' ? 'danger' : 'info'">
                {{ authStore.userInfo?.role }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">
              {{ authStore.userInfo?.created_at ? new Date(authStore.userInfo.created_at).toLocaleString() : '-' }}
            </el-descriptions-item>
          </el-descriptions>
          <el-divider />
          <el-button type="primary" @click="passwordDialogVisible = true">修改密码</el-button>
        </el-card>
      </el-col>

      <!-- 右侧：个人统计 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>我的检测统计</span>
          </template>
          <el-row :gutter="20" class="stat-row">
            <el-col :span="12">
              <el-statistic title="总检测次数" :value="stats.total_detections" />
            </el-col>
            <el-col :span="12">
              <el-statistic title="总水果数量" :value="stats.total_fruits" />
            </el-col>
          </el-row>
          <el-divider />
          <h4>最近检测记录</h4>
          <el-table :data="stats.recent_detections" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="original_filename" label="文件名" />
            <el-table-column prop="fruit_count" label="水果数" width="100" />
            <el-table-column prop="created_at" label="检测时间" width="180">
              <template #default="{ row }">
                {{ new Date(row.created_at).toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="$router.push(`/history/${row.id}`)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="changing">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import client from '@/api/client'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

const authStore = useAuthStore()

interface Stats {
  total_detections: number
  total_fruits: number
  recent_detections: any[]
}

const stats = ref<Stats>({
  total_detections: 0,
  total_fruits: 0,
  recent_detections: []
})

const fetchStats = async () => {
  try {
    const { data } = await client.get('/profile/stats')
    stats.value = data
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

// 修改密码相关
const passwordDialogVisible = ref(false)
const changing = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPass = (rule: any, value: string, callback: any) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPass, trigger: 'blur' }
  ]
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return
    changing.value = true
    try {
      await client.post('/auth/change-password', {
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      })
      ElMessage.success('密码修改成功，请重新登录')
      passwordDialogVisible.value = false
      // 清除登录状态并跳转登录页
      authStore.logout()
      window.location.href = '/login'
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '修改失败')
    } finally {
      changing.value = false
    }
  })
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}
.stat-row {
  margin-bottom: 20px;
}
</style>