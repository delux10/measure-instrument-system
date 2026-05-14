<template>
  <div>
    <el-page-header title="检定管理" style="margin-bottom: 20px">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">检定计划</span>
      </template>
    </el-page-header>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-card shadow="never">
          <div style="display: flex; align-items: center; justify-content: space-between">
            <div>
              <div style="font-size: 13px; color: #909399; margin-bottom: 4px">计划总数</div>
              <div style="font-size: 26px; font-weight: 600; color: #303133">{{ stats.total }}</div>
            </div>
            <el-icon :size="36" color="#409eff"><Document /></el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div style="display: flex; align-items: center; justify-content: space-between">
            <div>
              <div style="font-size: 13px; color: #909399; margin-bottom: 4px">已完成</div>
              <div style="font-size: 26px; font-weight: 600; color: #67c23a">{{ stats.completed }}</div>
            </div>
            <el-icon :size="36" color="#67c23a"><CircleCheckFilled /></el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div style="display: flex; align-items: center; justify-content: space-between">
            <div>
              <div style="font-size: 13px; color: #909399; margin-bottom: 4px">待执行</div>
              <div style="font-size: 26px; font-weight: 600; color: #e6a23c">{{ stats.pending }}</div>
            </div>
            <el-icon :size="36" color="#e6a23c"><Clock /></el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div style="display: flex; align-items: center; justify-content: space-between">
            <div>
              <div style="font-size: 13px; color: #909399; margin-bottom: 4px">已超期</div>
              <div style="font-size: 26px; font-weight: 600; color: #f56c6c">{{ stats.overdue }}</div>
            </div>
            <el-icon :size="36" color="#f56c6c"><WarningFilled /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <!-- 搜索栏 -->
      <el-form :inline="true" style="margin-bottom: 16px">
        <el-form-item label="仪器名称">
          <el-input
            v-model="searchQuery"
            placeholder="仪器名称"
            clearable
            style="width: 180px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="检测院">
          <el-select
            v-model="filters.agency_id"
            placeholder="全部检测院"
            clearable
            style="width: 180px"
            @change="handleSearch"
          >
            <el-option
              v-for="a in agencies"
              :key="a.id"
              :label="a.name"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filters.status"
            placeholder="全部状态"
            clearable
            style="width: 140px"
            @change="handleSearch"
          >
            <el-option label="待执行" value="pending" />
            <el-option label="已完成" value="completed" />
            <el-option label="已超期" value="overdue" />
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
          <el-button type="primary" @click="openCreateDialog">新增检定记录</el-button>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        :data="paginatedData"
        border
        stripe
        v-loading="loading"
        style="width: 100%"
        empty-text="暂无检定计划数据"
      >
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column label="仪器名称" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.instrument?.name || row.instrument_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="plan_date" label="计划日期" width="120" />
        <el-table-column prop="actual_date" label="实际日期" width="120" />
        <el-table-column label="检测院" width="160" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.agency?.name || row.agency_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="检定结果" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              v-if="row.result"
              :type="resultTagType(row.result)"
              size="small"
              effect="plain"
            >
              {{ resultLabel(row.result) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="certificate_no" label="证书编号" width="150" show-overflow-tooltip />
        <el-table-column prop="cost" label="费用" width="100" align="right">
          <template #default="{ row }">
            {{ row.cost != null ? row.cost.toFixed(2) : '-' }}
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

    <!-- 新增/编辑检定记录对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑检定记录' : '新增检定记录'"
      width="600px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="110px"
        size="default"
        style="padding-right: 20px"
      >
        <el-form-item label="选择仪器" prop="instrument_id">
          <el-select
            v-model="form.instrument_id"
            placeholder="请选择仪器"
            style="width: 100%"
            filterable
            clearable
          >
            <el-option
              v-for="inst in instruments"
              :key="inst.id"
              :label="`${inst.name} (${inst.code || inst.id})`"
              :value="inst.id"
            />
          </el-select>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划日期" prop="plan_date">
              <el-date-picker
                v-model="form.plan_date"
                type="date"
                placeholder="选择计划日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际日期" prop="actual_date">
              <el-date-picker
                v-model="form.actual_date"
                type="date"
                placeholder="选择实际日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="检测院" prop="agency_id">
          <el-select
            v-model="form.agency_id"
            placeholder="请选择检测院"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="a in agencies"
              :key="a.id"
              :label="a.name"
              :value="a.id"
            />
          </el-select>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="检定结果" prop="result">
              <el-select
                v-model="form.result"
                placeholder="请选择"
                style="width: 100%"
                clearable
              >
                <el-option label="合格" value="pass" />
                <el-option label="不合格" value="fail" />
                <el-option label="需调整" value="adjust" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="证书编号" prop="certificate_no">
              <el-input v-model="form.certificate_no" placeholder="请输入证书编号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="费用" prop="cost">
          <el-input-number
            v-model="form.cost"
            :min="0"
            :precision="2"
            style="width: 100%"
            placeholder="请输入费用"
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
  Document,
  CircleCheckFilled,
  Clock,
  WarningFilled,
} from '@element-plus/icons-vue'
import {
  getCalibrationList,
  createCalibration,
  updateCalibration,
  deleteCalibration,
  getAgencyList,
} from '../../api/calibration'
import { getInstrumentList } from '../../api/instrument'

// === 状态 ===
const loading = ref(false)
const saving = ref(false)
const calibrationList = ref([])
const agencies = ref([])
const instruments = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const currentPage = ref(1)
const pageSize = ref(20)

const filters = ref({
  agency_id: null,
  status: null,
})

const formRef = ref(null)
function initForm() {
  return {
    instrument_id: null,
    plan_date: null,
    actual_date: null,
    agency_id: null,
    result: null,
    certificate_no: '',
    cost: null,
    remark: '',
  }
}
const form = ref(initForm())

// === 表单校验规则 ===
const rules = {
  instrument_id: [
    { required: true, message: '请选择仪器', trigger: 'change' },
  ],
  plan_date: [
    { required: true, message: '请选择计划日期', trigger: 'change' },
  ],
  agency_id: [
    { required: true, message: '请选择检测院', trigger: 'change' },
  ],
}

// === 计算统计 ===
const stats = computed(() => {
  const all = calibrationList.value
  const total = all.length
  const completed = all.filter((r) => r.actual_date).length
  const pending = all.filter((r) => !r.actual_date && !isOverdue(r.plan_date)).length
  const overdue = all.filter((r) => !r.actual_date && r.plan_date && isOverdue(r.plan_date)).length
  return { total, completed, pending, overdue }
})

// === 计算属性：前端过滤与分页 ===
const filteredData = computed(() => {
  let data = calibrationList.value
  const query = searchQuery.value?.trim().toLowerCase()
  if (query) {
    data = data.filter((item) => {
      const name = item.instrument?.name || item.instrument_name || ''
      return name.toLowerCase().includes(query)
    })
  }
  if (filters.value.agency_id) {
    data = data.filter((item) => item.agency_id === filters.value.agency_id)
  }
  if (filters.value.status) {
    if (filters.value.status === 'completed') {
      data = data.filter((r) => r.actual_date)
    } else if (filters.value.status === 'pending') {
      data = data.filter((r) => !r.actual_date && !isOverdue(r.plan_date))
    } else if (filters.value.status === 'overdue') {
      data = data.filter((r) => !r.actual_date && r.plan_date && isOverdue(r.plan_date))
    }
  }
  return data
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// === 结果标签 ===
function resultLabel(result) {
  const map = {
    pass: '合格',
    fail: '不合格',
    adjust: '需调整',
  }
  return map[result] || result
}

function resultTagType(result) {
  const map = {
    pass: 'success',
    fail: 'danger',
    adjust: 'warning',
  }
  return map[result] || 'info'
}

// === 日期工具 ===
function isOverdue(date) {
  if (!date) return false
  return new Date(date) < new Date(new Date().toDateString())
}

// === 数据加载 ===
async function fetchCalibrations() {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (filters.value.agency_id) params.agency_id = filters.value.agency_id
    if (filters.value.status) params.status = filters.value.status
    const res = await getCalibrationList(params)
    calibrationList.value = res.data || res.data?.results || []
    currentPage.value = 1
  } catch (e) {
    ElMessage.error('获取检定计划列表失败')
    calibrationList.value = []
  } finally {
    loading.value = false
  }
}

async function fetchAgencies() {
  try {
    const res = await getAgencyList()
    agencies.value = res.data || res.data?.results || []
  } catch (e) {
    agencies.value = []
  }
}

async function fetchInstruments() {
  try {
    const res = await getInstrumentList()
    instruments.value = res.data || res.data?.results || []
  } catch (e) {
    instruments.value = []
  }
}

// === 搜索与重置 ===
function handleSearch() {
  currentPage.value = 1
  fetchCalibrations()
}

function handleReset() {
  searchQuery.value = ''
  filters.value = { agency_id: null, status: null }
  currentPage.value = 1
  fetchCalibrations()
}

// === 分页 ===
function onPageSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
}

function onPageChange(val) {
  currentPage.value = val
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
    instrument_id: row.instrument_id || null,
    plan_date: row.plan_date || null,
    actual_date: row.actual_date || null,
    agency_id: row.agency_id || null,
    result: row.result || null,
    certificate_no: row.certificate_no || '',
    cost: row.cost ?? null,
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
      await updateCalibration(editingId.value, form.value)
      ElMessage.success('检定记录更新成功')
    } else {
      await createCalibration(form.value)
      ElMessage.success('检定记录创建成功')
    }
    dialogVisible.value = false
    await fetchCalibrations()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    saving.value = false
  }
}

// === 删除 ===
async function handleDelete(row) {
  const instrumentName = row.instrument?.name || row.instrument_name || `ID:${row.instrument_id}`
  try {
    await ElMessageBox.confirm(
      `确定要删除仪器「${instrumentName}」的检定记录吗？此操作不可恢复。`,
      '删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteCalibration(row.id)
    ElMessage.success('检定记录已删除')
    await fetchCalibrations()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// === 生命周期 ===
onMounted(() => {
  fetchCalibrations()
  fetchAgencies()
  fetchInstruments()
})
</script>
