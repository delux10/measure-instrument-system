<template>
  <div>
    <el-page-header title="合同管理" style="margin-bottom: 20px">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">合同管理与对账</span>
      </template>
    </el-page-header>

    <el-card shadow="never">
      <el-tabs v-model="activeTab" type="border-card" @tab-change="onTabChange">
        <!-- ========== 合同管理 ========== -->
        <el-tab-pane label="合同管理" name="contracts">
          <!-- 搜索栏 -->
          <el-form :inline="true" style="margin-bottom: 16px">
            <el-form-item label="合同编号">
              <el-input v-model="searchForm.contract_no" placeholder="请输入合同编号" clearable style="width: 180px" @keyup.enter="handleSearch" />
            </el-form-item>
            <el-form-item label="检测院">
              <el-select v-model="searchForm.agency_id" placeholder="全部检测院" clearable style="width: 200px" filterable>
                <el-option v-for="a in agencyList" :key="a.id" :label="a.name" :value="a.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 140px">
                <el-option label="待生效" value="pending" />
                <el-option label="进行中" value="executing" />
                <el-option label="已完成" value="completed" />
                <el-option label="已终止" value="archived" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">查询</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 工具栏 -->
          <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
            <el-button type="primary" @click="openCreateDialog">新增合同</el-button>
          </div>

          <!-- 表格 -->
          <el-table :data="contractList" border stripe v-loading="loading" style="width: 100%" empty-text="暂无合同数据">
            <el-table-column prop="contract_no" label="合同编号" width="150" show-overflow-tooltip />
            <el-table-column prop="name" label="合同名称" min-width="180" show-overflow-tooltip />
            <el-table-column label="检测院" width="160" show-overflow-tooltip>
              <template #default="{ row }">
                {{ agencyName(row.agency_id) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)" size="small" effect="plain">
                  {{ statusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_amount" label="合同金额" width="130" align="right">
              <template #default="{ row }">
                {{ row.total_amount ? '¥ ' + Number(row.total_amount).toLocaleString() : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="contract_date" label="签订日期" width="120" align="center" />
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="openEditDialog(row)">编辑</el-button>
                <el-button type="primary" link size="small" @click="openItemsDialog(row)">明细</el-button>
                <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div style="display: flex; justify-content: center; margin-top: 16px">
            <el-pagination
              v-if="total > 0"
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              @size-change="fetchContractList"
              @current-change="fetchContractList"
            />
          </div>
        </el-tab-pane>

        <!-- ========== 合同对账 ========== -->
        <el-tab-pane label="合同对账" name="reconciliation">
          <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px">
            <span style="white-space: nowrap">选择合同：</span>
            <el-select v-model="reconContractId" placeholder="请选择合同" clearable filterable style="width: 300px">
              <el-option
                v-for="c in contractListForSelect"
                :key="c.id"
                :label="c.contract_no + ' - ' + c.name"
                :value="c.id"
              />
            </el-select>
            <el-button type="primary" :disabled="!reconContractId" :loading="reconAnalyzing" @click="handleAnalyze">
              分析对账
            </el-button>
          </div>

          <el-table
            v-if="reconDiffs.length > 0"
            :data="reconDiffs"
            border
            stripe
            v-loading="reconLoading"
            style="width: 100%"
            empty-text="暂无对账差异"
          >
            <el-table-column prop="contract_value" label="合同值" width="120" align="right">
              <template #default="{ row }">
                {{ row.contract_value ?? '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="actual_value" label="实际值" width="120" align="right">
              <template #default="{ row }">
                {{ row.actual_value ?? '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="diff_type" label="差异类型" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="row.diff_type === 'over' ? 'danger' : 'warning'" size="small" effect="plain">
                  {{ row.diff_type === 'over' ? '超出' : '不足' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="diff_amount" label="差异金额" width="120" align="right">
              <template #default="{ row }">
                {{ row.diff_amount ? '¥ ' + Number(row.diff_amount).toLocaleString() : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 'resolved' ? 'success' : 'warning'" size="small" effect="plain">
                  {{ row.status === 'resolved' ? '已处理' : '待处理' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="row.status !== 'resolved'"
                  type="success"
                  link
                  size="small"
                  @click="handleConfirmDiff(row)"
                >
                  确认
                </el-button>
                <el-button
                  v-if="row.status !== 'resolved'"
                  type="warning"
                  link
                  size="small"
                  @click="openAdjustDialog(row)"
                >
                  调整
                </el-button>
                <span v-else style="color: #909399; font-size: 13px">已处理</span>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-else-if="!reconAnalyzing" description="请选择合同并点击分析" />
        </el-tab-pane>

        <!-- ========== 合同版本 ========== -->
        <el-tab-pane label="合同版本" name="versions">
          <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px">
            <span style="white-space: nowrap">选择合同：</span>
            <el-select v-model="versionContractId" placeholder="请选择合同" clearable filterable style="width: 300px">
              <el-option
                v-for="c in contractListForSelect"
                :key="c.id"
                :label="c.contract_no + ' - ' + c.name"
                :value="c.id"
              />
            </el-select>
          </div>

          <!-- 上传区域 -->
          <div v-if="versionContractId" style="margin-bottom: 16px">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :on-change="onVersionFileChange"
              :show-file-list="false"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.zip,.rar"
            >
              <template #trigger>
                <el-button type="primary">选择文件</el-button>
              </template>
              <el-button
                type="success"
                style="margin-left: 12px"
                :loading="versionUploading"
                :disabled="!versionFile"
                @click="handleUploadVersion"
              >
                上传新版本
              </el-button>
            </el-upload>
            <span v-if="versionFile" style="margin-left: 12px; color: #606266">{{ versionFile.name }}</span>
          </div>

          <!-- 版本列表 -->
          <el-table
            v-if="versionList.length > 0"
            :data="versionList"
            border
            stripe
            v-loading="versionLoading"
            style="width: 100%"
            empty-text="暂无版本记录"
          >
            <el-table-column prop="version_no" label="版本号" width="120" align="center" />
            <el-table-column prop="file_name" label="文件名" min-width="200" show-overflow-tooltip />
            <el-table-column prop="file_size" label="文件大小" width="120" align="right">
              <template #default="{ row }">
                {{ formatFileSize(row.file_size) }}
              </template>
            </el-table-column>
            <el-table-column prop="uploader_name" label="上传人" width="120" align="center" />
            <el-table-column prop="created_at" label="上传时间" width="170" align="center" />
            <el-table-column label="操作" width="120" fixed="right" align="center">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleDownloadVersion(row)">下载</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-else-if="versionContractId && !versionLoading" description="暂无版本记录" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- ========== 新增/编辑合同对话框 ========== -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑合同' : '新增合同'"
      width="750px"
      :before-close="() => { dialogVisible = false }"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px" style="padding-right: 20px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同编号" prop="contract_no">
              <el-input v-model="form.contract_no" placeholder="请输入合同编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合同名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入合同名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="检测院" prop="agency_id">
              <el-select v-model="form.agency_id" placeholder="请选择检测院" style="width: 100%" filterable>
                <el-option v-for="a in agencyList" :key="a.id" :label="a.name" :value="a.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="签订日期" prop="contract_date">
              <el-date-picker v-model="form.contract_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker v-model="form.start_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker v-model="form.end_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同金额" prop="total_amount">
              <el-input-number v-model="form.total_amount" :precision="2" :min="0" style="width: 100%" placeholder="请输入金额" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="待生效" value="pending" />
                <el-option label="进行中" value="executing" />
                <el-option label="已完成" value="completed" />
                <el-option label="已终止" value="archived" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="付款方式" prop="payment_terms">
              <el-input v-model="form.payment_terms" placeholder="如：月结30天" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发票类型" prop="invoice_type">
              <el-select v-model="form.invoice_type" placeholder="请选择" style="width: 100%" clearable>
                <el-option label="增值税专用发票" value="special" />
                <el-option label="增值税普通发票" value="normal" />
                <el-option label="不开票" value="none" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="发票抬头" prop="invoice_title">
              <el-input v-model="form.invoice_title" placeholder="请输入发票抬头" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="税号" prop="tax_id">
              <el-input v-model="form.tax_id" placeholder="请输入税号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="税率(%)" prop="tax_rate">
              <el-input-number v-model="form.tax_rate" :precision="2" :min="0" :max="100" style="width: 100%" placeholder="如：13" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- ========== 合同明细对话框 ========== -->
    <el-dialog
      v-model="itemsDialogVisible"
      :title="'合同明细 - ' + (currentContract?.contract_no || '')"
      width="800px"
      :before-close="() => { itemsDialogVisible = false }"
    >
      <el-table :data="contractItems" border stripe v-loading="itemsLoading" style="width: 100%" empty-text="暂无明细">
        <el-table-column type="index" label="序号" width="55" align="center" />
        <el-table-column prop="instrument_name" label="仪器名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="specification" label="规格型号" width="140" show-overflow-tooltip />
        <el-table-column prop="quantity" label="数量" width="70" align="center" />
        <el-table-column prop="unit_price" label="单价" width="110" align="right">
          <template #default="{ row }">
            {{ row.unit_price ? '¥ ' + Number(row.unit_price).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="小计" width="110" align="right">
          <template #default="{ row }">
            {{ row.amount ? '¥ ' + Number(row.amount).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click="handleDeleteItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 新增明细 -->
      <div style="margin-top: 16px; border-top: 1px solid #ebeef5; padding-top: 16px">
        <span style="font-weight: 600; margin-bottom: 8px; display: block">新增明细</span>
        <el-form :inline="true" :model="newItemForm" label-width="0">
          <el-form-item>
            <el-input v-model="newItemForm.instrument_name" placeholder="仪器名称" style="width: 150px" />
          </el-form-item>
          <el-form-item>
            <el-input v-model="newItemForm.specification" placeholder="规格型号" style="width: 120px" />
          </el-form-item>
          <el-form-item>
            <el-input-number v-model="newItemForm.quantity" :min="1" :max="99999" style="width: 100px" placeholder="数量" />
          </el-form-item>
          <el-form-item>
            <el-input-number v-model="newItemForm.unit_price" :precision="2" :min="0" style="width: 120px" placeholder="单价" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="itemSaving" @click="handleAddItem">添加</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>

    <!-- ========== 差异调整对话框 ========== -->
    <el-dialog
      v-model="adjustDialogVisible"
      title="调整差异"
      width="450px"
      :before-close="() => { adjustDialogVisible = false }"
    >
      <el-form ref="adjustFormRef" :model="adjustForm" label-width="100px">
        <el-form-item label="调整值">
          <el-input-number v-model="adjustForm.adjusted_value" :precision="2" :min="0" style="width: 100%" placeholder="请输入调整后的值" />
        </el-form-item>
        <el-form-item label="调整说明">
          <el-input v-model="adjustForm.remark" type="textarea" :rows="3" placeholder="请输入调整原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="adjustSaving" @click="handleAdjustDiff">提交调整</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getContractList,
  createContract,
  updateContract,
  deleteContract,
  getContractItems,
  createContractItem,
  deleteContractItem,
  getContractVersions,
  uploadContractVersion,
  getCalibrationAgencies,
  analyzeReconciliation,
  getReconciliationDiffs,
  confirmOrAdjustDiff,
} from '../../api/contract'

// ===== 工具函数 =====
function statusLabel(status) {
  const map = { pending: '待生效', executing: '进行中', completed: '已完成', archived: '已终止' }
  return map[status] || status || '未知'
}

function statusTagType(status) {
  const map = { pending: 'info', executing: 'primary', completed: 'success', archived: 'danger' }
  return map[status] || 'info'
}

function formatFileSize(bytes) {
  if (!bytes && bytes !== 0) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIdx = 0
  while (size >= 1024 && unitIdx < units.length - 1) {
    size /= 1024
    unitIdx++
  }
  return size.toFixed(1) + ' ' + units[unitIdx]
}

// ===== Tab 切换状态 =====
const activeTab = ref('contracts')

// ===== 检测院列表 =====
const agencyList = ref([])

async function fetchAgencies() {
  try {
    const res = await getCalibrationAgencies()
    agencyList.value = res.data || []
  } catch {
    agencyList.value = []
  }
}

function agencyName(id) {
  if (!id) return '-'
  const a = agencyList.value.find(a => a.id === id)
  return a ? a.name : '-'
}

// ===== 合同管理 =====
const loading = ref(false)
const saving = ref(false)
const contractList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const searchForm = reactive({
  contract_no: '',
  agency_id: null,
  status: null,
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const formRef = ref(null)

function initForm() {
  return {
    contract_no: '',
    name: '',
    agency_id: null,
    contract_date: null,
    start_date: null,
    end_date: null,
    total_amount: null,
    payment_terms: '',
    invoice_title: '',
    tax_id: '',
    invoice_type: null,
    tax_rate: null,
    status: 'pending',
    remark: '',
  }
}

const form = ref(initForm())

const rules = {
  contract_no: [{ required: true, message: '请输入合同编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入合同名称', trigger: 'blur' }],
  agency_id: [{ required: true, message: '请选择检测院', trigger: 'change' }],
  contract_date: [{ required: true, message: '请选择签订日期', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

async function fetchContractList() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchForm.contract_no) params.contract_no = searchForm.contract_no
    if (searchForm.agency_id) params.agency_id = searchForm.agency_id
    if (searchForm.status) params.status = searchForm.status
    const res = await getContractList(params)
    const data = res.data
    if (data && data.results) {
      contractList.value = data.results
      total.value = data.count || data.results.length
    } else if (Array.isArray(data)) {
      contractList.value = data
      total.value = data.length
    } else {
      contractList.value = data || []
      total.value = contractList.value.length
    }
  } catch {
    contractList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  fetchContractList()
}

function handleReset() {
  searchForm.contract_no = ''
  searchForm.agency_id = null
  searchForm.status = null
  currentPage.value = 1
  fetchContractList()
}

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
    contract_no: row.contract_no,
    name: row.name,
    agency_id: row.agency_id,
    contract_date: row.contract_date,
    start_date: row.start_date,
    end_date: row.end_date,
    total_amount: row.total_amount,
    payment_terms: row.payment_terms || '',
    invoice_title: row.invoice_title || '',
    tax_id: row.tax_id || '',
    invoice_type: row.invoice_type || null,
    tax_rate: row.tax_rate,
    status: row.status,
    remark: row.remark || '',
  }
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) {
      await updateContract(editingId.value, form.value)
      ElMessage.success('合同更新成功')
    } else {
      await createContract(form.value)
      ElMessage.success('合同创建成功')
    }
    dialogVisible.value = false
    await fetchContractList()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除合同「${row.contract_no} - ${row.name}」吗？`, '删除确认', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteContract(row.id)
    ElMessage.success('合同已删除')
    await fetchContractList()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// ===== 合同明细 =====
const itemsDialogVisible = ref(false)
const itemsLoading = ref(false)
const itemSaving = ref(false)
const currentContract = ref(null)
const contractItems = ref([])
const newItemForm = reactive({
  instrument_name: '',
  specification: '',
  quantity: 1,
  unit_price: 0,
})

async function openItemsDialog(row) {
  currentContract.value = row
  itemsDialogVisible.value = true
  await fetchContractItems(row.id)
}

async function fetchContractItems(contractId) {
  itemsLoading.value = true
  try {
    const res = await getContractItems({ contract_id: contractId })
    contractItems.value = res.data || []
  } catch {
    contractItems.value = []
  } finally {
    itemsLoading.value = false
  }
}

async function handleAddItem() {
  if (!newItemForm.instrument_name) {
    ElMessage.warning('请输入仪器名称')
    return
  }
  itemSaving.value = true
  try {
    await createContractItem({
      contract_id: currentContract.value.id,
      instrument_name: newItemForm.instrument_name,
      specification: newItemForm.specification,
      quantity: newItemForm.quantity,
      unit_price: newItemForm.unit_price,
      amount: newItemForm.quantity * newItemForm.unit_price,
    })
    ElMessage.success('明细已添加')
    newItemForm.instrument_name = ''
    newItemForm.specification = ''
    newItemForm.quantity = 1
    newItemForm.unit_price = 0
    await fetchContractItems(currentContract.value.id)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '添加失败')
  } finally {
    itemSaving.value = false
  }
}

async function handleDeleteItem(row) {
  try {
    await ElMessageBox.confirm(`确定要删除明细「${row.instrument_name}」吗？`, '删除确认', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteContractItem(row.id)
    ElMessage.success('明细已删除')
    await fetchContractItems(currentContract.value.id)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// ===== 合同对账 =====
const contractListForSelect = ref([])
const reconContractId = ref(null)
const reconAnalyzing = ref(false)
const reconLoading = ref(false)
const reconDiffs = ref([])

async function fetchContractsForSelect() {
  try {
    const res = await getContractList({ page_size: 999 })
    const data = res.data
    if (data && data.results) {
      contractListForSelect.value = data.results
    } else if (Array.isArray(data)) {
      contractListForSelect.value = data
    } else {
      contractListForSelect.value = data || []
    }
  } catch {
    contractListForSelect.value = []
  }
}

async function handleAnalyze() {
  if (!reconContractId.value) return
  reconAnalyzing.value = true
  reconDiffs.value = []
  try {
    await analyzeReconciliation(reconContractId.value)
    await fetchReconDiffs()
    ElMessage.success('对账分析完成')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '对账分析失败')
  } finally {
    reconAnalyzing.value = false
  }
}

async function fetchReconDiffs() {
  reconLoading.value = true
  try {
    const res = await getReconciliationDiffs({ contract_id: reconContractId.value })
    reconDiffs.value = res.data || []
  } catch {
    reconDiffs.value = []
  } finally {
    reconLoading.value = false
  }
}

async function handleConfirmDiff(row) {
  try {
    await ElMessageBox.confirm('确定确认此差异吗？', '确认差异', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info',
    })
    await confirmOrAdjustDiff(row.id, { status: 'resolved', action: 'confirm' })
    ElMessage.success('差异已确认')
    await fetchReconDiffs()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

// 差异调整
const adjustDialogVisible = ref(false)
const adjustSaving = ref(false)
const adjustFormRef = ref(null)
const adjustingDiffId = ref(null)
const adjustForm = reactive({
  adjusted_value: 0,
  remark: '',
})

function openAdjustDialog(row) {
  adjustingDiffId.value = row.id
  adjustForm.adjusted_value = row.actual_value || 0
  adjustForm.remark = ''
  adjustDialogVisible.value = true
}

async function handleAdjustDiff() {
  adjustSaving.value = true
  try {
    await confirmOrAdjustDiff(adjustingDiffId.value, {
      action: 'adjust',
      adjusted_value: adjustForm.adjusted_value,
      remark: adjustForm.remark,
    })
    ElMessage.success('调整已提交')
    adjustDialogVisible.value = false
    await fetchReconDiffs()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '调整失败')
  } finally {
    adjustSaving.value = false
  }
}

// ===== 合同版本 =====
const versionContractId = ref(null)
const versionLoading = ref(false)
const versionUploading = ref(false)
const versionList = ref([])
const versionFile = ref(null)
const uploadRef = ref(null)

function onVersionFileChange(file) {
  versionFile.value = file.raw || file
}

async function fetchVersionList() {
  if (!versionContractId.value) {
    versionList.value = []
    return
  }
  versionLoading.value = true
  try {
    const res = await getContractVersions({ contract_id: versionContractId.value })
    versionList.value = res.data || []
  } catch {
    versionList.value = []
  } finally {
    versionLoading.value = false
  }
}

async function handleUploadVersion() {
  if (!versionFile.value || !versionContractId.value) return
  versionUploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', versionFile.value)
    fd.append('contract_id', versionContractId.value)
    await uploadContractVersion(fd)
    ElMessage.success('版本上传成功')
    versionFile.value = null
    await fetchVersionList()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  } finally {
    versionUploading.value = false
  }
}

function handleDownloadVersion(row) {
  if (row.file_url) {
    window.open(row.file_url, '_blank')
  } else {
    ElMessage.info('文件地址不可用')
  }
}

// ===== Tab 切换 =====
function onTabChange(tabName) {
  if (tabName === 'reconciliation') {
    fetchContractsForSelect()
  } else if (tabName === 'versions') {
    fetchContractsForSelect()
  }
}

// ===== 生命周期 =====
onMounted(async () => {
  await Promise.all([fetchContractList(), fetchAgencies(), fetchContractsForSelect()])
})
</script>
