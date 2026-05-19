<template>
  <div>
    <el-page-header title="检定管理" style="margin-bottom: 20px">
      <template #content><span style="font-size:18px;font-weight:600">检定记录</span></template>
    </el-page-header>

    <el-card shadow="never">
      <el-form :inline="true" style="margin-bottom: 16px">
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 140px">
            <el-option label="待检定" value="pending" />
            <el-option label="已检定" value="done" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="doSearch">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
        <div>
          <el-button type="primary" @click="openCreate">新增检定记录</el-button>
          <el-button type="success" @click="openGenerate">生成检定计划</el-button>
          <el-button type="warning" @click="openExpiring">即将到期预警</el-button>
        </div>
        <div>
          <el-button @click="agencyDialogVisible = true">管理检测院</el-button>
        </div>
      </div>

      <el-table :data="tableData" border stripe v-loading="loading" style="width: 100%">
        <el-table-column label="仪器编号" width="160">
          <template #default="{ row }">{{ row.instrument_code || '-' }}</template>
        </el-table-column>
        <el-table-column label="计划日期" width="120">
          <template #default="{ row }">{{ row.plan_date || '-' }}</template>
        </el-table-column>
        <el-table-column label="实际日期" width="120">
          <template #default="{ row }">{{ row.actual_date || '待检定' }}</template>
        </el-table-column>
        <el-table-column label="检定结果" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.result" :type="row.result === 'qualified' ? 'success' : 'danger'" size="small">
              {{ row.result === 'qualified' ? '合格' : '不合格' }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column v-for="col in dynamicColumns" :key="col" :label="col" :min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ row.fields?.[col] || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="display: flex; justify-content: flex-end; margin-top: 16px">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total"
          :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @size-change="onSizeChange" @current-change="fetchData" />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑检定记录' : '新增检定记录'" width="600px">
      <el-form ref="formRef" :model="form" label-width="100px">
        <el-form-item label="仪器编号">
          <el-input v-model="form.instrument_code" placeholder="输入仪器编号" />
        </el-form-item>
        <el-form-item label="检测院">
          <el-select v-model="form.agency_id" placeholder="请选择" clearable style="width: 100%">
            <el-option v-for="a in agencies" :key="a.id" :label="a.name" :value="a.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划日期">
          <el-date-picker v-model="form.plan_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="实际日期">
          <el-date-picker v-model="form.actual_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="检定结果">
          <el-select v-model="form.result" placeholder="请选择" clearable style="width: 100%">
            <el-option label="合格" value="qualified" />
            <el-option label="不合格" value="unqualified" />
          </el-select>
        </el-form-item>
        <el-divider>扩展字段</el-divider>
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
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 到期预警对话框 -->
    <el-dialog v-model="expiringVisible" title="即将到期预警" width="700px">
      <el-table :data="expiringList" border stripe v-loading="expiringLoading">
        <el-table-column label="仪器编号" width="160">
          <template #default="{ row }">{{ row.instrument_code || '-' }}</template>
        </el-table-column>
        <el-table-column label="计划日期" width="130">
          <template #default="{ row }">{{ row.plan_date || '-' }}</template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 生成检定计划对话框 -->
    <el-dialog v-model="generateVisible" title="生成检定计划" width="480px">
      <el-form label-width="80px">
        <el-form-item label="选择月份">
          <el-date-picker v-model="generateForm.year_month" type="month" placeholder="选择年月" value-format="YYYY-MM" style="width: 100%" />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="generateForm.department_id" placeholder="全部部门" clearable style="width: 100%">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <div v-if="generateResult" style="margin-top:12px;padding:12px;background:#f5f7fa;border-radius:4px">
        <p style="margin:0 0 4px;font-weight:600;color:#303133">生成结果</p>
        <p style="margin:2px 0;font-size:13px;color:#67c23a">创建：{{ generateResult.created }} 条</p>
        <p style="margin:2px 0;font-size:13px;color:#909399">跳过（日期不符）：{{ generateResult.skipped_invalid_date }} 条</p>
        <p style="margin:2px 0;font-size:13px;color:#e6a23c">跳过（已存在）：{{ generateResult.skipped_existing }} 条</p>
      </div>
      <template #footer>
        <el-button @click="generateVisible = false">关闭</el-button>
        <el-button type="primary" :loading="generating" :disabled="!generateForm.year_month" @click="handleGenerate">开始生成</el-button>
      </template>
    </el-dialog>

    <!-- 检测院管理对话框 -->
    <el-dialog v-model="agencyDialogVisible" title="检测院管理" width="500px">
      <el-table :data="agencies" border stripe>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="contact_person" label="联系人" />
        <el-table-column prop="contact_phone" label="电话" />
      </el-table>
      <div style="margin-top: 16px; border-top: 1px solid #ebeef5; padding-top: 16px">
        <el-form :inline="true">
          <el-form-item label="名称">
            <el-input v-model="newAgency.name" placeholder="检测院名称" />
          </el-form-item>
          <el-form-item label="联系人">
            <el-input v-model="newAgency.contact_person" placeholder="联系人" />
          </el-form-item>
          <el-form-item label="电话">
            <el-input v-model="newAgency.contact_phone" placeholder="电话" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleCreateAgency">添加</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCalibrationList, createCalibration, updateCalibration, getExpiringList, getAgencyList, createAgency, generateCalibrationPlan } from '../../api/calibration'
import { getInstrumentList } from '../../api/instrument'
import { getDepartmentList } from '../../api/system'

const loading = ref(false)
const saving = ref(false)
const tableData = ref([])
const agencies = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = ref({ status: null })
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const form = ref({ instrument_code: '', agency_id: null, plan_date: null, actual_date: null, result: null, fields: {} })
const fieldKeys = ref([])

const dynamicColumns = computed(() => {
  const keys = new Set()
  tableData.value.forEach(item => {
    if (item.fields) Object.keys(item.fields).forEach(k => keys.add(k))
  })
  return Array.from(keys)
})

const expiringVisible = ref(false)
const expiringList = ref([])
const expiringLoading = ref(false)
const agencyDialogVisible = ref(false)
const newAgency = ref({ name: '', contact_person: '', contact_phone: '' })
const generateVisible = ref(false)
const generating = ref(false)
const generateForm = ref({ year_month: '', department_id: null })
const generateResult = ref(null)
const departments = ref([])

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.value.status) params.status = filters.value.status
    const res = await getCalibrationList(params)
    tableData.value = res.data.data || []
    total.value = res.data.meta?.total || 0
  } catch { ElMessage.error('获取列表失败') } finally { loading.value = false }
}

function doSearch() { page.value = 1; fetchData() }
function resetFilters() { filters.value = { status: null }; doSearch() }
function onSizeChange(v) { pageSize.value = v; page.value = 1; fetchData() }

function syncFieldKeys() { fieldKeys.value = Object.keys(form.value.fields || {}) }
function addField() {
  const key = '字段' + (Object.keys(form.value.fields || {}).length + 1)
  form.value.fields = { ...form.value.fields, [key]: '' }
  syncFieldKeys()
}
function removeField(key) {
  const updated = { ...form.value.fields }; delete updated[key]
  form.value.fields = updated; syncFieldKeys()
}

function openCreate() {
  isEdit.value = false; editingId.value = null
  form.value = { instrument_code: '', agency_id: null, plan_date: null, actual_date: null, result: null, fields: {} }
  syncFieldKeys(); dialogVisible.value = true
}

function openEdit(row) {
  isEdit.value = true; editingId.value = row.id
  form.value = {
    instrument_code: row.instrument_code || '', agency_id: row.agency_id,
    plan_date: row.plan_date, actual_date: row.actual_date, result: row.result,
    fields: { ...(row.fields || {}) }
  }
  syncFieldKeys(); dialogVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    const payload = {
      instrument_code: form.value.instrument_code, agency_id: form.value.agency_id,
      plan_date: form.value.plan_date, actual_date: form.value.actual_date,
      result: form.value.result, fields: form.value.fields
    }
    if (isEdit.value) {
      await updateCalibration(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createCalibration(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false; fetchData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') } finally { saving.value = false }
}

async function openExpiring() {
  expiringVisible.value = true; expiringLoading.value = true
  try {
    const res = await getExpiringList(30)
    expiringList.value = res.data.data || []
  } catch { ElMessage.error('获取预警失败') } finally { expiringLoading.value = false }
}

function openGenerate() {
  generateForm.value = { year_month: '', department_id: null }
  generateResult.value = null
  generateVisible.value = true
}

async function handleGenerate() {
  if (!generateForm.value.year_month) return
  generating.value = true
  generateResult.value = null
  try {
    const res = await generateCalibrationPlan(generateForm.value.year_month, generateForm.value.department_id)
    generateResult.value = res.data.data || res.data
    ElMessage.success('检定计划生成完成')
    fetchData()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '生成失败')
  } finally {
    generating.value = false
  }
}

async function handleCreateAgency() {
  if (!newAgency.value.name) { ElMessage.warning('请输入名称'); return }
  try {
    await createAgency(newAgency.value)
    ElMessage.success('添加成功')
    newAgency.value = { name: '', contact_person: '', contact_phone: '' }
    const res = await getAgencyList()
    agencies.value = res.data.data || []
  } catch (e) { ElMessage.error(e.response?.data?.detail || '添加失败') }
}

onMounted(async () => {
  fetchData()
  try { const res = await getAgencyList(); agencies.value = res.data.data || [] } catch {}
  getDepartmentList().then(res => { departments.value = res.data.data || res.data || [] }).catch(() => {})
})
</script>
