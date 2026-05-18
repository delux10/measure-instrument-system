<template>
  <div>
    <el-page-header title="仪器管理" style="margin-bottom: 20px">
      <template #content><span style="font-size:18px;font-weight:600">仪器台账</span></template>
    </el-page-header>

    <el-card shadow="never">
      <!-- 搜索栏 -->
      <el-form :inline="true" style="margin-bottom: 16px">
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="任意字段搜索" clearable style="width: 220px" @keyup.enter="doSearch" />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="filters.department_id" placeholder="全部" clearable style="width: 180px">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="doSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 工具栏 -->
      <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
        <div>
          <el-button type="primary" @click="openCreate">新增仪器</el-button>
          <el-button type="success" @click="openImport">导入 Excel</el-button>
        </div>
        <div>
          <el-button @click="handleExport">导出 Excel</el-button>
          <el-button v-if="userStore.isAdmin" type="danger" @click="handleClearAll">一键清空</el-button>
        </div>
      </div>

      <!-- 表格 -->
      <el-table :data="tableData" border stripe v-loading="loading" style="width: 100%" empty-text="暂无数据">
        <el-table-column prop="code" label="仪器编号" width="160" fixed />
        <el-table-column v-for="col in dynamicColumns" :key="col" :label="col" :min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ row.fields?.[col] || '-' }}</template>
        </el-table-column>
        <el-table-column label="部门" width="120">
          <template #default="{ row }">{{ row.department_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="更新时间" width="170">
          <template #default="{ row }">{{ row.updated_at?.slice(0,19) || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="display: flex; justify-content: flex-end; margin-top: 16px">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total"
          :page-sizes="[10,20,50,100]" layout="total,sizes,prev,pager,next" @size-change="onSizeChange" @current-change="fetchData" />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑仪器' : '新增仪器'" width="700px">
      <el-form ref="formRef" :model="form" label-width="100px">
        <el-form-item label="部门">
          <el-select v-model="form.department_id" placeholder="请选择" clearable style="width: 100%">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-divider>字段</el-divider>
        <div v-for="(key, idx) in fieldKeys" :key="idx" style="margin-bottom: 8px">
          <el-row :gutter="8">
            <el-col :span="8"><el-input v-model="fieldKeys[idx]" placeholder="字段名" /></el-col>
            <el-col :span="14"><el-input v-model="form.fields[key]" placeholder="字段值" /></el-col>
            <el-col :span="2"><el-button @click="removeField(key)" icon="Delete" circle size="small" /></el-col>
          </el-row>
        </div>
        <el-button @click="addField" size="small" type="primary" plain>+ 添加字段</el-button>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="importVisible" title="导入 Excel" width="500px">
      <p style="color:#666;font-size:13px;margin-bottom:16px">所有列原样导入，表头即为字段名。</p>
      <el-upload ref="uploadRef" drag :auto-upload="false" :limit="1" accept=".xlsx,.xls" :on-change="onFileChange">
        <el-icon style="font-size:48px;color:#c0c4cc;margin-bottom:8px"><UploadFilled /></el-icon>
        <div style="font-size:14px;color:#606266">拖拽或<em style="color:#409eff">点击上传</em></div>
      </el-upload>
      <div v-if="importResult" style="margin-top:12px;padding:12px;background:#f5f7fa;border-radius:4px">
        {{ importResult.message }}
      </div>
      <template #footer>
        <el-button @click="importVisible=false">关闭</el-button>
        <el-button type="primary" :loading="importing" :disabled="!importFile" @click="doImport">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { useUserStore } from '../../store/user'
import { getInstrumentList, createInstrument, updateInstrument, deleteInstrument, clearAllInstruments, importInstruments, exportInstruments } from '../../api/instrument'
import { getDepartmentList } from '../../api/system'

const userStore = useUserStore()
const loading = ref(false)
const saving = ref(false)
const tableData = ref([])
const departments = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = ref({ search: '', department_id: null })
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const form = ref({ department_id: null, fields: {} })
const fieldKeys = ref([])

// Import
const importVisible = ref(false)
const importFile = ref(null)
const importing = ref(false)
const importResult = ref(null)

const dynamicColumns = computed(() => {
  const keys = new Set()
  tableData.value.forEach(item => {
    if (item.fields) Object.keys(item.fields).forEach(k => keys.add(k))
  })
  return Array.from(keys)
})

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.department_id) params.department_id = filters.value.department_id
    const res = await getInstrumentList(params)
    tableData.value = res.data.data || []
    total.value = res.data.meta?.total || 0
  } catch { ElMessage.error('获取列表失败') } finally { loading.value = false }
}

function doSearch() { page.value = 1; fetchData() }
function resetSearch() { filters.value = { search: '', department_id: null }; doSearch() }
function onSizeChange(v) { pageSize.value = v; page.value = 1; fetchData() }

function syncFieldKeys() { fieldKeys.value = Object.keys(form.value.fields || {}) }
function addField() {
  const key = '新字段' + (Object.keys(form.value.fields || {}).length + 1)
  form.value.fields = { ...form.value.fields, [key]: '' }
  syncFieldKeys()
}
function removeField(key) {
  const updated = { ...form.value.fields }; delete updated[key]
  form.value.fields = updated; syncFieldKeys()
}

function openCreate() { isEdit.value = false; editingId.value = null; form.value = { department_id: null, fields: {} }; syncFieldKeys(); dialogVisible.value = true }
function openEdit(row) {
  isEdit.value = true; editingId.value = row.id
  form.value = { department_id: row.department_id, fields: { ...(row.fields || {}) } }
  syncFieldKeys(); dialogVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (isEdit.value) {
      await updateInstrument(editingId.value, { department_id: form.value.department_id, fields: form.value.fields })
      ElMessage.success('更新成功')
    } else {
      await createInstrument({ department_id: form.value.department_id, fields: form.value.fields })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false; fetchData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') } finally { saving.value = false }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除仪器「${row.code}」吗？`, '确认', { type: 'warning' })
    await deleteInstrument(row.id)
    ElMessage.success('已删除'); fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

async function handleClearAll() {
  try {
    await ElMessageBox.confirm('将清空全部仪器，不可恢复！', '警告', { type: 'error' })
    await ElMessageBox.prompt('输入"确认清空"以继续', '二次确认', { inputPattern: /^确认清空$/, inputErrorMessage: '请输入"确认清空"' })
    const res = await clearAllInstruments()
    ElMessage.success(res.data?.data?.message || '已清空'); fetchData()
  } catch (e) { if (e !== 'cancel' && e !== 'close') ElMessage.error('清空失败') }
}

function handleExport() {
  const params = {}
  if (filters.value.search) params.search = filters.value.search
  exportInstruments(params).then(res => {
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'instruments.xlsx'; a.click()
    URL.revokeObjectURL(url)
  }).catch(() => ElMessage.error('导出失败'))
}

// Import
function openImport() { importFile.value = null; importResult.value = null; importVisible.value = true }
function onFileChange(file) { importFile.value = file.raw }
async function doImport() {
  if (!importFile.value) return
  importing.value = true; importResult.value = null
  try {
    const res = await importInstruments(importFile.value)
    importResult.value = res.data.data || res.data
    ElMessage.success('导入完成'); fetchData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '导入失败') } finally { importing.value = false }
}

onMounted(async () => {
  fetchData()
  try { const res = await getDepartmentList(); departments.value = res.data.data || res.data || [] } catch {}
})
</script>
