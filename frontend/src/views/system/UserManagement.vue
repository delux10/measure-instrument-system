<template>
  <div>
    <el-card shadow="never">
      <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
        <div>
          <el-button type="primary" @click="openCreateDialog">新增用户</el-button>
        </div>
        <div>
          <el-input v-model="searchQuery" placeholder="搜索用户名/姓名" clearable style="width: 240px" @input="fetchUsers" />
        </div>
      </div>

      <el-table :data="userList" border stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="140">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department_id" label="所属部门" width="180">
          <template #default="{ row }">
            {{ deptName(row.department_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="is_active" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button
              :type="row.is_active ? 'warning' : 'success'"
              link
              size="small"
              @click="toggleActive(row)"
            >
              {{ row.is_active ? '停用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑用户对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" size="large">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="系统管理员（全部权限）" value="admin" />
            <el-option label="体系管理员（全厂查看+审核）" value="system_manager" />
            <el-option label="部门测量员（本部门管理）" value="dept_measurer" />
            <el-option label="部门领导（本部门审批）" value="dept_leader" />
            <el-option label="只读用户" value="readonly" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属部门" prop="department_id">
          <el-select v-model="form.department_id" style="width: 100%" clearable>
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="功能模块">
          <el-checkbox-group v-model="form.module_permissions">
            <el-checkbox label="dashboard">仪表盘</el-checkbox>
            <el-checkbox label="instruments">仪器台账</el-checkbox>
            <el-checkbox label="calibration">检定计划</el-checkbox>
            <el-checkbox label="contracts">合同管理</el-checkbox>
            <el-checkbox label="supervision">监督管理</el-checkbox>
            <el-checkbox label="user_management">用户管理</el-checkbox>
          </el-checkbox-group>
          <span style="font-size: 12px; color: #909399">留空表示拥有所有模块权限</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserList, createUser, updateUser, deleteUser } from '../../api/system'
import { getDepartmentList } from '../../api/system'

const loading = ref(false)
const saving = ref(false)
const userList = ref([])
const departments = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const formRef = ref(null)
const form = ref({
  username: '',
  password: '',
  name: '',
  role: 'dept_measurer',
  department_id: null,
  phone: '',
  email: '',
  module_permissions: null,
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

function roleLabel(role) {
  const map = {
    admin: '系统管理员',
    system_manager: '体系管理员',
    dept_measurer: '部门测量员',
    dept_leader: '部门领导',
    readonly: '只读用户',
    user: '普通用户',
  }
  return map[role] || role
}

function roleTagType(role) {
  const map = { admin: 'danger', system_manager: 'warning', dept_leader: '', dept_measurer: 'primary', readonly: 'info' }
  return map[role] || 'info'
}

function deptName(id) {
  if (!id) return '-'
  const d = departments.value.find(d => d.id === id)
  return d ? d.name : '-'
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('zh-CN')
}

async function fetchUsers() {
  loading.value = true
  try {
    const res = await getUserList({ search: searchQuery.value })
    userList.value = res.data
  } catch (e) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchDepartments() {
  try {
    const res = await getDepartmentList()
    departments.value = res.data
  } catch (e) {
    // ignore
  }
}

function openCreateDialog() {
  isEdit.value = false
  editingId.value = null
  form.value = { username: '', password: '', name: '', role: 'dept_measurer', department_id: null, phone: '', email: '', module_permissions: null }
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editingId.value = row.id
  form.value = {
    username: row.username,
    name: row.name,
    role: row.role,
    department_id: row.department_id,
    phone: row.phone || '',
    email: row.email || '',
    module_permissions: row.module_permissions,
  }
  dialogVisible.value = true
}

async function saveUser() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (isEdit.value) {
      await updateUser(editingId.value, form.value)
      ElMessage.success('用户更新成功')
    } else {
      await createUser(form.value)
      ElMessage.success('用户创建成功')
    }
    dialogVisible.value = false
    await fetchUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    saving.value = false
  }
}

async function toggleActive(row) {
  try {
    await ElMessageBox.confirm(
      row.is_active ? '确定停用该用户？' : '确定启用该用户？',
      '提示'
    )
    await updateUser(row.id, { is_active: !row.is_active })
    ElMessage.success(row.is_active ? '已停用' : '已启用')
    await fetchUsers()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchUsers()
  fetchDepartments()
})
</script>
