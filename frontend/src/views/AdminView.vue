<template>
  <div class="admin-container">
    <el-card>
      <template #header>
        <span>用户管理</span>
        <div style="float: right">
          <el-button type="info" @click="$router.push('/admin/logs')">操作日志</el-button>
        </div>
      </template>
      <el-table :data="users" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              v-if="row.id !== currentUserId"
              type="primary"
              size="small"
              @click="openRoleDialog(row)"
            >
              修改角色
            </el-button>
            <el-button
              v-if="row.id !== currentUserId"
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
            <span v-else style="color: #999">当前用户</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 修改角色对话框 -->
    <el-dialog v-model="roleDialogVisible" title="修改角色" width="400px">
      <el-form :model="roleForm">
        <el-form-item label="用户名">
          <span>{{ roleForm.username }}</span>
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="roleForm.role">
            <el-radio label="user">普通用户</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmUpdateRole">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getUsers, updateUserRole, deleteUser, type UserItem } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()
const currentUserId = authStore.userInfo?.id

const users = ref<UserItem[]>([])
const loading = ref(false)

// 角色修改相关
const roleDialogVisible = ref(false)
const roleForm = ref({
  id: 0,
  username: '',
  role: ''
})

const fetchUsers = async () => {
  loading.value = true
  try {
    users.value = await getUsers()
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const openRoleDialog = (user: UserItem) => {
  roleForm.value = {
    id: user.id,
    username: user.username,
    role: user.role
  }
  roleDialogVisible.value = true
}

const confirmUpdateRole = async () => {
  try {
    await updateUserRole(roleForm.value.id, roleForm.value.role)
    ElMessage.success('角色更新成功')
    roleDialogVisible.value = false
    fetchUsers()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleDelete = async (user: UserItem) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${user.username}" 吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteUser(user.id)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    // 取消删除不处理
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.admin-container {
  padding: 20px;
}
</style>