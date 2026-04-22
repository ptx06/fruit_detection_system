<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 左侧：个人信息卡片 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>个人信息</span>
          </template>
          
          <!-- 头像上传 -->
          <div class="avatar-section">
            <el-avatar :size="120" :src="userInfo.avatar || defaultAvatar" class="avatar">
              {{ userInfo.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <el-button type="primary" size="small" @click="avatarDialogVisible = true">更换头像</el-button>
          </div>
          
          <el-divider />
          
          <!-- 个人信息 -->
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag :type="userInfo.role === 'admin' ? 'danger' : 'info'">
                {{ userInfo.role }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">
              {{ userInfo.created_at ? new Date(userInfo.created_at).toLocaleString() : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="个人简介">
              <span v-if="userInfo.bio">{{ userInfo.bio }}</span>
              <span v-else class="empty-bio">暂无简介</span>
            </el-descriptions-item>
          </el-descriptions>
          
          <el-divider />
          
          <div class="action-buttons">
            <el-button type="primary" @click="editInfoDialogVisible = true">编辑资料</el-button>
            <el-button type="warning" @click="passwordDialogVisible = true">修改密码</el-button>
          </div>
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

    <!-- 编辑资料对话框 -->
    <el-dialog v-model="editInfoDialogVisible" title="编辑资料" width="400px">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="个人简介" prop="bio">
          <el-input v-model="editForm.bio" type="textarea" rows="3" placeholder="请输入个人简介" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editInfoDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditInfo" :loading="editing">确定</el-button>
      </template>
    </el-dialog>

    <!-- 更换头像对话框 -->
    <el-dialog v-model="avatarDialogVisible" title="更换头像" width="400px">
      <el-upload
        class="avatar-uploader"
        action="#"
        :auto-upload="false"
        :on-change="handleAvatarChange"
        :show-file-list="true"
        :before-upload="beforeAvatarUpload"
        accept="image/*"
      >
        <img v-if="userInfo.avatar" :src="userInfo.avatar" class="avatar-preview" />
        <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
      </el-upload>
      <template #footer>
        <el-button @click="avatarDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUploadAvatar" :loading="uploading">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import client from '@/api/client'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 用户信息
const userInfo = ref({
  username: authStore.userInfo?.username || '',
  role: authStore.userInfo?.role || '',
  created_at: authStore.userInfo?.created_at || '',
  bio: authStore.userInfo?.bio || '',
  avatar: authStore.userInfo?.avatar || ''
})

// 编辑资料相关
const editInfoDialogVisible = ref(false)
const editing = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = reactive({
  username: '',
  bio: ''
})

const editRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }]
}

// 头像上传相关
const avatarDialogVisible = ref(false)
const uploading = ref(false)
const avatarFile = ref<File | null>(null)

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

// 编辑资料
const handleEditInfo = async () => {
  if (!editFormRef.value) return
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    editing.value = true
    try {
      const { data } = await client.put('/profile', editForm)
      ElMessage.success('资料修改成功')
      editInfoDialogVisible.value = false
      // 更新本地用户信息
      userInfo.value = {
        ...userInfo.value,
        ...data
      }
      // 更新 authStore 中的用户信息
      authStore.updateUserInfo(data)
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '修改失败')
    } finally {
      editing.value = false
    }
  })
}

// 头像上传
const handleAvatarChange = (file: any) => {
  avatarFile.value = file.raw
}

const beforeAvatarUpload = (file: any) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isJpgOrPng) {
    ElMessage.error('只能上传 JPG/PNG 图片')
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
  }
  return isJpgOrPng && isLt2M
}

const handleUploadAvatar = async () => {
  if (!avatarFile.value) {
    ElMessage.warning('请选择图片')
    return
  }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('avatar', avatarFile.value)
    const { data } = await client.post('/profile/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    console.log('上传成功，返回的头像路径:', data.avatar)
    ElMessage.success('头像上传成功')
    avatarDialogVisible.value = false
    // 更新本地用户信息
    userInfo.value.avatar = data.avatar
    console.log('更新后的userInfo.avatar:', userInfo.value.avatar)
    // 更新 authStore 中的用户信息
    authStore.updateUserInfo({ avatar: data.avatar })
  } catch (error: any) {
    console.error('上传失败:', error)
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 打开编辑资料对话框时初始化表单
const openEditDialog = () => {
  editForm.username = userInfo.value.username
  editForm.bio = userInfo.value.bio || ''
  editInfoDialogVisible.value = true
}

onMounted(() => {
  fetchStats()
  // 监听编辑资料对话框打开
  editInfoDialogVisible.value = false
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.stat-row {
  margin-bottom: 20px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.avatar {
  margin-bottom: 15px;
  border: 2px solid #409eff;
}

.avatar-preview {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
}

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.empty-bio {
  color: #909399;
  font-style: italic;
}
</style>