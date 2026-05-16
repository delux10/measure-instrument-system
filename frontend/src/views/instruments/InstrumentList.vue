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
          <el-button type="success" @click="openImportDialog">导入 Excel</el-button>
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
        <el-table-column prop="code" label="仪器编号" width="120" />
        <el-table-column prop="name" label="仪器名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="model" label="型号规格" width="130" show-overflow-tooltip />
        <el-table-column prop="serial_no" label="出厂编号" width="130" show-overflow-tooltip />
        <el-table-column prop="range_value" label="测量范围" width="120" show-overflow-tooltip />
        <el-table-column prop="accuracy" label="精度等级" width="110" show-overflow-tooltip />
        <el-table-column prop="scale_interval" label="分度值" width="90" />
        <el-table-column prop="manufacturer" label="生产厂家" width="140" show-overflow-tooltip />
        <el-table-column prop="keeper" label="责任人" width="100" />
        <el-table-column prop="cal_agency" label="检定/校准单位" width="140" show-overflow-tooltip />
        <el-table-column prop="certificate_no" label="证书编号" width="130" show-overflow-tooltip />
        <el-table-column prop="last_cal_date" label="检定日期" width="110">
          <template #default="{ row }">{{ formatDate(row.last_cal_date) }}</template>
        </el-table-column>
        <el-table-column prop="next_cal_date" label="有效期至" width="110">
          <template #default="{ row }">
            <span :style="isOverdue(row.next_cal_date) ? 'color: #f56c6c; font-weight: bold' : ''">
              {{ formatDate(row.next_cal_date) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="cert_confirmed" label="证书确认" width="100" />
        <el-table-column prop="metrology_characteristic" label="计量特性" width="120" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small" effect="plain">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department_id" label="使用部门" width="120">
          <template #default="{ row }">
            {{ deptName(row.department_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="location" label="安装地点" width="130" show-overflow-tooltip />
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
      width="900px"
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
          <el-col :span="8">
            <el-form-item label="仪器编号" prop="code">
              <el-input v-model="form.code" placeholder="请输入仪器编号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="仪器名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入仪器名称" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
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
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="型号规格" prop="model">
              <el-input v-model="form.model" placeholder="请输入型号规格" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="出厂编号" prop="serial_no">
              <el-input v-model="form.serial_no" placeholder="请输入出厂编号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="出厂日期">
              <el-date-picker
                v-model="form.manufacture_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="测量范围">
              <el-input v-model="form.range_value" placeholder="如：0-150mm" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="精度等级/不确定度">
              <el-input v-model="form.accuracy" placeholder="如：0.01mm" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="分度值">
              <el-input v-model="form.scale_interval" placeholder="如：0.01mm" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="生产厂家">
              <el-input v-model="form.manufacturer" placeholder="请输入生产厂家" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="购入日期">
              <el-date-picker
                v-model="form.purchase_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="资产原值">
              <el-input-number
                v-model="form.price"
                :min="0"
                :precision="2"
                style="width: 100%"
                placeholder="请输入资产原值"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="责任人">
              <el-input v-model="form.keeper" placeholder="请输入责任人" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="使用部门" prop="department_id">
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
          <el-col :span="8">
            <el-form-item label="安装地点">
              <el-input v-model="form.location" placeholder="请输入安装地点" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="检定/校准单位">
              <el-input v-model="form.cal_agency" placeholder="如：XX省计量科学研究院" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="证书编号">
              <el-input v-model="form.certificate_no" placeholder="请输入证书编号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="证书确认">
              <el-select v-model="form.cert_confirmed" placeholder="请选择" style="width: 100%" clearable>
                <el-option label="已确认" value="confirmed" />
                <el-option label="未确认" value="unconfirmed" />
                <el-option label="待确认" value="pending" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="计量特性">
              <el-input v-model="form.metrology_characteristic" placeholder="请输入计量特性" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
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
          <el-col :span="8">
            <el-form-item label="检定周期(月)">
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
          <el-col :span="8">
            <el-form-item label="检定日期">
              <el-date-picker
                v-model="form.last_cal_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="有效期至">
              <el-date-picker
                v-model="form.next_cal_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="检定方式">
              <el-select v-model="form.cal_method" placeholder="请选择" style="width: 100%" clearable>
                <el-option label="送检" value="external" />
                <el-option label="现场" value="onsite" />
                <el-option label="自检" value="self" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 导入 Excel 对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入 Excel 台账" width="700px">
      <div style="margin-bottom: 16px; padding: 12px; background: #f5f7fa; border-radius: 4px">
        <p style="margin: 0 0 8px 0; font-weight: 600">支持识别的表头列名：</p>
        <p style="margin: 0; color: #666; font-size: 13px; line-height: 1.8">
          仪器编号、仪器名称、型号规格/型号、出厂编号、测量范围、精度等级/不确定度、
          分度值、出厂日期、生产厂家/厂家、责任人/保管人、检定/校准单位、证书编号、
          检定日期、有效期/有效期至、证书确认、计量特性、状态、使用部门/部门、
          安装地点/存放地点、备注、检定周期
        </p>
      </div>

      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        style="margin-bottom: 16px"
      >
        <el-icon style="font-size: 48px; color: #c0c4cc; margin-bottom: 8px"><UploadFilled /></el-icon>
        <div style="font-size: 14px; color: #606266">
          将 Excel 文件拖拽到此处，或 <em style="color: #409eff">点击上传</em>
        </div>
        <template #tip>
          <div style="margin-top: 8px; font-size: 12px; color: #999">
            仅支持 .xlsx / .xls 格式，第一行为表头，从第二行开始为数据
          </div>
        </template>
      </el-upload>

      <!-- 导入结果 -->
      <div v-if="importResult" style="padding: 16px; background: #f0f9eb; border-radius: 4px">
        <p style="margin: 0 0 8px 0; font-weight: 600; color: #67c23a">
          {{ importResult.message }}
        </p>
        <div v-if="importResult.errors && importResult.errors.length > 0" style="margin-top: 8px">
          <p style="margin: 0 0 4px 0; color: #e6a23c; font-size: 13px">
            跳过 {{ importResult.errors.length }} 条：
          </p>
          <div style="max-height: 200px; overflow-y: auto; font-size: 12px">
            <div
              v-for="(err, i) in importResult.errors"
              :key="i"
              style="padding: 2px 0; color: #909399"
            >
              第 {{ err.row }} 行：{{ err.msg }}
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="importDialogVisible = false">关闭</el-button>
        <el-button
          type="primary"
          :loading="importing"
          :disabled="!selectedFile"
          @click="handleImport"
        >
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import {
  getInstrumentList,
  createInstrument,
  updateInstrument,
  deleteInstrument,
  getInstrumentCategories,
  importInstruments,
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

const importDialogVisible = ref(false)
const selectedFile = ref(null)
const importResult = ref(null)
const importing = ref(false)

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
    range_value: '',
    accuracy: '',
    scale_interval: '',
    manufacture_date: null,
    manufacturer: '',
    purchase_date: null,
    price: null,
    keeper: '',
    department_id: null,
    location: '',
    cal_agency: '',
    certificate_no: '',
    cert_confirmed: '',
    metrology_characteristic: '',
    status: 'in_use',
    calibration_cycle: null,
    last_cal_date: null,
    next_cal_date: null,
    cal_method: '',
    remark: '',
  }
}
const form = ref(initForm())

// === 表单校验规则 ===
const rules = {
  code: [{ required: true, message: '请输入仪器编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入仪器名称', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  department_id: [{ required: true, message: '请选择使用部门', trigger: 'change' }],
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
    range_value: row.range_value || '',
    accuracy: row.accuracy || '',
    scale_interval: row.scale_interval || '',
    manufacture_date: row.manufacture_date || '',
    manufacturer: row.manufacturer || '',
    purchase_date: row.purchase_date || '',
    price: row.price ?? null,
    keeper: row.keeper || '',
    department_id: row.department_id || null,
    location: row.location || '',
    cal_agency: row.cal_agency || '',
    certificate_no: row.certificate_no || '',
    cert_confirmed: row.cert_confirmed || '',
    metrology_characteristic: row.metrology_characteristic || '',
    status: row.status || 'in_use',
    calibration_cycle: row.calibration_cycle ?? null,
    last_cal_date: row.last_cal_date || '',
    next_cal_date: row.next_cal_date || '',
    cal_method: row.cal_method || '',
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

// === Excel 导入 ===
function openImportDialog() {
  selectedFile.value = null
  importResult.value = null
  importDialogVisible.value = true
}

function handleFileChange(file) {
  selectedFile.value = file.raw
}

function handleFileRemove() {
  selectedFile.value = null
}

async function handleImport() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  importing.value = true
  importResult.value = null
  try {
    const res = await importInstruments(selectedFile.value)
    importResult.value = res.data
    ElMessage.success(res.data.message || '导入完成')
    await fetchInstruments()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

// === 生命周期 ===
onMounted(() => {
  fetchInstruments()
  fetchDepartments()
  fetchCategories()
})
</script>
