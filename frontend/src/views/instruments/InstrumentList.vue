<template>
  <div>
    <el-page-header title="仪器管理" style="margin-bottom: 20px">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">仪器台账</span>
      </template>
    </el-page-header>

    <el-card shadow="never">
      <!-- 搜索栏 -->
      <el-form :inline="true" style="margin-bottom: 16px">
        <el-form-item label="搜索">
          <el-input
            v-model="searchQuery"
            placeholder="仪器名称 / 编号"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filters.status"
            placeholder="全部状态"
            clearable
            style="width: 140px"
            @change="handleSearch"
          >
            <el-option label="在用" value="in_use" />
            <el-option label="停用" value="stopped" />
            <el-option label="封存" value="idle" />
            <el-option label="报废" value="scrapped" />
            <el-option label="送检" value="calibrating" />
            <el-option label="维修" value="repair" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-select
            v-model="filters.department_id"
            placeholder="全部部门"
            clearable
            style="width: 180px"
            @change="handleSearch"
          >
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            v-model="filters.category_id"
            placeholder="全部分类"
            clearable
            style="width: 180px"
            filterable
            @change="handleSearch"
          >
            <el-option
              v-for="cat in flattenedCategories"
              :key="cat.id"
              :label="cat.label"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 工具栏 -->
      <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
        <div>
          <el-button type="primary" @click="openCreateDialog">新增仪器</el-button>
        </div>
        <div>
          <el-button @click="handleExport">导出 Excel</el-button>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        :data="paginatedData"
        border
        stripe
        v-loading="loading"
        style="width: 100%"
        empty-text="暂无仪器数据"
      >
        <el-table-column prop="code" label="编号" width="120" />
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="model" label="型号" width="130" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small" effect="plain">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department_id" label="所属部门" width="120">
          <template #default="{ row }">
            {{ deptName(row.department_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="keeper" label="保管人" width="100" />
        <el-table-column prop="location" label="存放地点" width="140" show-overflow-tooltip />
        <el-table-column prop="last_cal_date" label="上次检定日期" width="130">
          <template #default="{ row }">{{ formatDate(row.last_cal_date) }}</template>
        </el-table-column>
        <el-table-column prop="next_cal_date" label="下次检定日期" width="130">
          <template #default="{ row }">
            <span :style="isOverdue(row.next_cal_date) ? 'color: #f56c6c; font-weight: bold' : ''">
              {{ formatDate(row.next_cal_date) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="display: flex; justify-content: flex-end; margin-top: 16px">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredData.length"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="onPageSizeChange"
          @current-change="onPageChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑仪器对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑仪器' : '新增仪器'"
      width="700px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        size="default"
        style="padding-right: 20px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="仪器编号" prop="code">
              <el-input v-model="form.code" placeholder="请输入仪器编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="仪器名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入仪器名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="型号" prop="model">
              <el-input v-model="form.model" placeholder="请输入型号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出厂编号" prop="serial_no">
              <el-input v-model="form.serial_no" placeholder="请输入出厂编号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="仪器分类" prop="category_id">
              <el-select
                v-model="form.category_id"
                placeholder="请选择分类"
                style="width: 100%"
                filterable
                clearable
              >
                <el-option
                  v-for="cat in flattenedCategories"
                  :key="cat.id"
                  :label="cat.label"
                  :value="cat.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="精度" prop="accuracy">
              <el-input v-model="form.accuracy" placeholder="请输入精度" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="测量范围" prop="range_value">
          <el-input v-model="form.range_value" placeholder="请输入测量范围" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生产厂家" prop="manufacturer">
              <el-input v-model="form.manufacturer" placeholder="请输入生产厂家" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="购入日期" prop="purchase_date">
              <el-date-picker
                v-model="form.purchase_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="资产原值" prop="price">
              <el-input-number
                v-model="form.price"
                :min="0"
                :precision="2"
                style="width: 100%"
                placeholder="请输入资产原值"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="管理部门" prop="department_id">
              <el-select
                v-model="form.department_id"
                placeholder="请选择部门"
                style="width: 100%"
                clearable
              >
                <el-option
                  v-for="dept in departments"
                  :key="dept.id"
                  :label="dept.name"
                  :value="dept.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="保管人" prop="keeper">
              <el-input v-model="form.keeper" placeholder="请输入保管人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="存放地点" prop="location">
              <el-input v-model="form.location" placeholder="请输入存放地点" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="在用" value="in_use" />
                <el-option label="停用" value="stopped" />
                <el-option label="封存" value="idle" />
                <el-option label="报废" value="scrapped" />
                <el-option label="送检" value="calibrating" />
                <el-option label="维修" value="repair" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="检定周期(月)" prop="calibration_cycle">
              <el-input-number
                v-model="form.calibration_cycle"
                :min="0"
                :max="120"
                style="width: 100%"
                placeholder="月数"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="检定方式" prop="cal_method">
              <el-select v-model="form.cal_method" placeholder="请选择" style="width: 100%" clearable>
                <el-option label="送检" value="external" />
                <el-option label="现场" value="onsite" />
                <el-option label="自检" value="self" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="上次检定日期" prop="last_cal_date">
              <el-date-picker
                v-model="form.last_cal_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="下次检定日期" prop="next_cal_date">
          <el-date-picker
            v-model="form.next_cal_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getInstrumentList,
  createInstrument,
  updateInstrument,
  deleteInstrument,
  getInstrumentCategories,
} from '../../api/instrument'
import { getDepartmentList } from '../../api/system'

// === 状态 ===
const loading = ref(false)
const saving = ref(false)
const instrumentList = ref([])
const departments = ref([])
const categories = ref([])
const flattenedCategories = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const currentPage = ref(1)
const pageSize = ref(20)

const filters = ref({
  status: null,
  department_id: null,
  category_id: null,
})

const formRef = ref(null)
function initForm() {
  return {
    code: '',
    name: '',
    model: '',
    serial_no: '',
    category_id: null,
    accuracy: '',
    range_value: '',
    manufacturer: '',
    purchase_date: null,
    price: null,
    department_id: null,
    keeper: '',
    location: '',
    status: 'in_use',
    calibration_cycle: null,
    cal_method: '',
    last_cal_date: null,
    next_cal_date: null,
    remark: '',
  }
}
const form = ref(initForm())

// === 表单校验规则 ===
const rules = {
  code: [{ required: true, message: '请输入仪器编号', trigger: 'blur' }],
  model: [{ required: true, message: '请输入型号', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  department_id: [{ required: true, message: '请选择管理部门', trigger: 'change' }],
}

// === 计算属性：前端过滤与分页 ===
const filteredData = computed(() => {
  let data = instrumentList.value
  const query = searchQuery.value?.trim().toLowerCase()
  if (query) {
    data = data.filter((item) => {
      return (
        (item.name && item.name.toLowerCase().includes(query)) ||
        (item.code && item.code.toLowerCase().includes(query))
      )
    })
  }
  if (filters.value.status) {
    data = data.filter((item) => item.status === filters.value.status)
  }
  if (filters.value.department_id) {
    data = data.filter((item) => item.department_id === filters.value.department_id)
  }
  if (filters.value.category_id) {
    data = data.filter((item) => item.category_id === filters.value.category_id)
  }
  return data
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// === 状态标签样式 ===
function statusLabel(status) {
  const map = {
    'in_use': '在用',
    'stopped': '停用',
    'idle': '封存',
    'scrapped': '报废',
    'calibrating': '送检',
    'repair': '维修',
  }
  return map[status] || status
}

function statusTagType(status) {
  const map = {
    'in_use': 'success',
    'stopped': 'info',
    'idle': 'warning',
    'scrapped': 'danger',
    'calibrating': 'primary',
    'repair': '',
  }
  return map[status] || 'info'
}

// === 部门名称 ===
function deptName(id) {
  if (!id) return '-'
  const d = departments.value.find((d) => d.id === id)
  return d ? d.name : '-'
}

// === 日期格式化 ===
function formatDate(d) {
  if (!d) return '-'
  return d
}

// === 是否过期 ===
function isOverdue(date) {
  if (!date) return false
  return new Date(date) < new Date()
}

// === 扁平化分类树 ===
function flattenCategories(tree, prefix = '') {
  const result = []
  for (const node of tree) {
    const label = prefix ? `${prefix} / ${node.name}` : node.name

    result.push({ id: node.id, label, name: node.name })
    if (node.children && node.children.length > 0) {
      result.push(...flattenCategories(node.children, label))
    }
  }
  return result
}

// === 数据加载 ===
async function fetchInstruments() {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.department_id) params.department_id = filters.value.department_id
    const res = await getInstrumentList(params)
    instrumentList.value = res.data || []
    currentPage.value = 1
  } catch (e) {
    ElMessage.error('获取仪器列表失败')
    instrumentList.value = []
  } finally {
    loading.value = false
  }
}

async function fetchDepartments() {
  try {
    const res = await getDepartmentList()
    departments.value = res.data || []
  } catch (e) {}
}

async function fetchCategories() {
  try {
    const res = await getInstrumentCategories()
    categories.value = res.data || []
    flattenedCategories.value = flattenCategories(categories.value)
  } catch (e) {}
}

// === 搜索与重置 ===
function handleSearch() {
  currentPage.value = 1
  fetchInstruments()
}

function handleReset() {
  searchQuery.value = ''
  filters.value = { status: null, department_id: null, category_id: null }
  currentPage.value = 1
  fetchInstruments()
}

// === 分页 ===
function onPageSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
}

function onPageChange(val) {
  currentPage.value = val
}

// === 导出 ===
function handleExport() {
  ElMessage.info('导出功能开发中')
}

// === 对话框 ===
function openCreateDialog() {
  isEdit.value = false
  editingId.value = null
  form.value = initForm()
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editingId.value = row.id
  form.value = {
    code: row.code || '',
    name: row.name || '',
    model: row.model || '',
    serial_no: row.serial_no || '',
    category_id: row.category_id || null,
    accuracy: row.accuracy || '',
    range_value: row.range_value || '',
    manufacturer: row.manufacturer || '',
    purchase_date: row.purchase_date || '',
    price: row.price ?? null,
    department_id: row.department_id || null,
    keeper: row.keeper || '',
    location: row.location || '',
    status: row.status || 'in_use',
    calibration_cycle: row.calibration_cycle ?? null,
    cal_method: row.cal_method || '',
    last_cal_date: row.last_cal_date || '',
    next_cal_date: row.next_cal_date || '',
    remark: row.remark || '',
  }
  dialogVisible.value = true
}

function handleDialogClose() {
  dialogVisible.value = false
}

// === 保存 ===
async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) {
      await updateInstrument(editingId.value, form.value)
      ElMessage.success('仪器更新成功')
    } else {
      await createInstrument(form.value)
      ElMessage.success('仪器创建成功')
    }
    dialogVisible.value = false
    await fetchInstruments()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    saving.value = false
  }
}

// === 删除 ===
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除仪器「${row.name}」（编号：${row.code}）吗？此操作不可恢复。`,
      '删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteInstrument(row.id)
    ElMessage.success('仪器已删除')
    await fetchInstruments()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// === 生命周期 ===
onMounted(() => {
  fetchInstruments()
  fetchDepartments()
  fetchCategories()
})
</script>
