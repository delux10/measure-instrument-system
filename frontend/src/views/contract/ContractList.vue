<template>
  <div>
    <el-page-header title="合同管理" style="margin-bottom: 20px">
      <template #content><span style="font-size:18px;font-weight:600">合同管理与对账</span></template>
    </el-page-header>

    <el-card shadow="never">
      <el-tabs v-model="activeTab" type="border-card" @tab-change="onTabChange">
        <!-- 合同列表 -->
        <el-tab-pane label="合同管理" name="contracts">
          <el-form :inline="true" style="margin-bottom: 16px">
            <el-form-item label="年份">
              <el-input v-model="filters.year" placeholder="如 2026" clearable style="width: 140px" @keyup.enter="doSearch" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="doSearch">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
            </el-form-item>
          </el-form>

          <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
            <el-button type="primary" @click="openCreate">新增合同</el-button>
          </div>

          <el-table :data="tableData" border stripe v-loading="loading" style="width: 100%">
            <el-table-column prop="contract_no" label="合同编号" width="160" />
            <el-table-column label="检测院" width="180">
              <template #default="{ row }">{{ row.agency_name || '-' }}</template>
            </el-table-column>
            <el-table-column prop="year" label="年份" width="80" align="center" />
            <el-table-column label="合同金额" width="130" align="right">
              <template #default="{ row }">{{ row.total_amount ? '¥' + Number(row.total_amount).toLocaleString() : '-' }}</template>
            </el-table-column>
            <el-table-column label="明细数" width="80" align="center">
              <template #default="{ row }">{{ row.items_count || 0 }}</template>
            </el-table-column>
            <el-table-column v-for="col in dynamicColumns" :key="col" :label="col" :min-width="130" show-overflow-tooltip>
              <template #default="{ row }">{{ row.fields?.[col] || '-' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="240" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="openItems(row)">明细</el-button>
                <el-button type="warning" link size="small" @click="openRecon(row)">对账</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div style="display: flex; justify-content: flex-end; margin-top: 16px">
            <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total"
              :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @size-change="onSizeChange" @current-change="fetchData" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 新增合同对话框 -->
    <el-dialog v-model="dialogVisible" title="新增合同" width="600px">
      <el-form ref="formRef" :model="form" label-width="100px">
        <el-form-item label="合同编号" required>
          <el-input v-model="form.contract_no" placeholder="请输入合同编号" />
        </el-form-item>
        <el-form-item label="检测院" required>
          <el-select v-model="form.agency_id" placeholder="请选择" style="width: 100%">
            <el-option v-for="a in agencies" :key="a.id" :label="a.name" :value="a.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="年份" required>
          <el-input-number v-model="form.year" :min="2020" :max="2100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="合同金额">
          <el-input-number v-model="form.total_amount" :precision="2" :min="0" style="width: 100%" />
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

    <!-- 合同明细对话框 -->
    <el-dialog v-model="itemsVisible" :title="'合同明细 - ' + (currentContract?.contract_no || '')" width="800px">
      <el-table :data="items" border stripe v-loading="itemsLoading">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="instrument_name" label="仪器名称" min-width="150" />
        <el-table-column prop="quantity" label="数量" width="80" align="center" />
        <el-table-column label="单价" width="120" align="right">
          <template #default="{ row }">{{ row.unit_price ? '¥' + Number(row.unit_price).toLocaleString() : '-' }}</template>
        </el-table-column>
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">{{ row.amount ? '¥' + Number(row.amount).toLocaleString() : '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click="handleDeleteItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 16px; border-top: 1px solid #ebeef5; padding-top: 16px">
        <span style="font-weight:600; display:block; margin-bottom:8px">新增明细</span>
        <el-form :inline="true">
          <el-form-item label="仪器名称">
            <el-input v-model="newItem.instrument_name" placeholder="仪器名称" style="width:160px" />
          </el-form-item>
          <el-form-item label="数量">
            <el-input-number v-model="newItem.quantity" :min="1" style="width:100px" />
          </el-form-item>
          <el-form-item label="单价">
            <el-input-number v-model="newItem.unit_price" :precision="2" :min="0" style="width:130px" />
          </el-form-item>
          <el-form-item label="金额">
            <el-input-number v-model="newItem.amount" :precision="2" :min="0" style="width:130px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="itemSaving" @click="handleAddItem">添加</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 执行记录 -->
      <div style="margin-top: 16px; border-top: 1px solid #ebeef5; padding-top: 16px">
        <span style="font-weight:600; display:block; margin-bottom:8px">执行记录</span>
        <el-table :data="executions" border stripe v-loading="execLoading" v-if="selectedItemId">
          <el-table-column label="实际日期" width="130">
            <template #default="{ row }">{{ row.actual_date || '-' }}</template>
          </el-table-column>
          <el-table-column prop="actual_quantity" label="数量" width="80" />
          <el-table-column label="金额" width="120" align="right">
            <template #default="{ row }">{{ row.actual_amount ? '¥' + Number(row.actual_amount).toLocaleString() : '-' }}</template>
          </el-table-column>
        </el-table>
        <div v-if="selectedItemId" style="margin-top: 8px">
          <el-form :inline="true">
            <el-form-item label="日期">
              <el-date-picker v-model="newExec.actual_date" type="date" value-format="YYYY-MM-DD" style="width:150px" />
            </el-form-item>
            <el-form-item label="数量">
              <el-input-number v-model="newExec.actual_quantity" :min="1" style="width:100px" />
            </el-form-item>
            <el-form-item label="金额">
              <el-input-number v-model="newExec.actual_amount" :precision="2" :min="0" style="width:130px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="execSaving" @click="handleAddExec">记录执行</el-button>
            </el-form-item>
          </el-form>
        </div>
        <p v-else style="color:#909399;font-size:13px">点击明细行查看/新增执行记录</p>
      </div>
    </el-dialog>

    <!-- 对账结果对话框 -->
    <el-dialog v-model="reconVisible" :title="'对账结果 - ' + (currentContract?.contract_no || '')" width="700px">
      <div v-if="reconData">
        <el-descriptions :column="3" border style="margin-bottom: 16px">
          <el-descriptions-item label="合同总额">¥{{ Number(reconData.summary?.total_contract_amount || 0).toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="实际总额">¥{{ Number(reconData.summary?.total_actual_amount || 0).toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="差异金额">
            <span :style="{ color: (reconData.summary?.diff_amount || 0) !== 0 ? '#F56C6C' : '#67C23A' }">
              ¥{{ Number(reconData.summary?.diff_amount || 0).toLocaleString() }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
        <el-table :data="reconData.diffs || []" border stripe v-if="reconData.diffs?.length">
          <el-table-column label="差异类型" width="120">
            <template #default="{ row }">
              <el-tag :type="row.diff_type === 'missing' ? 'danger' : 'warning'" size="small">
                {{ row.diff_type === 'quantity' ? '数量差异' : row.diff_type === 'amount' ? '金额差异' : '缺失' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="合同值" width="120"><template #default="{ row }">{{ row.contract_value }}</template></el-table-column>
          <el-table-column label="实际值" width="120"><template #default="{ row }">{{ row.actual_value }}</template></el-table-column>
          <el-table-column label="差异金额" width="130" align="right">
            <template #default="{ row }">{{ row.diff_amount ? '¥' + Number(row.diff_amount).toLocaleString() : '-' }}</template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'resolved' ? 'success' : 'warning'" size="small">
                {{ row.status === 'resolved' ? '已处理' : '待处理' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="无差异" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getContractList, getContract, createContract, addContractItem, deleteContractItem, addExecution, getReconciliation, getCalibrationAgencies } from '../../api/contract'

const activeTab = ref('contracts')
const loading = ref(false)
const saving = ref(false)
const tableData = ref([])
const agencies = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = ref({ year: null })

const dialogVisible = ref(false)
const formRef = ref(null)
const form = ref({ contract_no: '', agency_id: null, year: new Date().getFullYear(), total_amount: null, fields: {} })
const fieldKeys = ref([])

const dynamicColumns = computed(() => {
  const keys = new Set()
  tableData.value.forEach(item => {
    if (item.fields) Object.keys(item.fields).forEach(k => keys.add(k))
  })
  return Array.from(keys)
})

const itemsVisible = ref(false)
const itemsLoading = ref(false)
const itemSaving = ref(false)
const currentContract = ref(null)
const items = ref([])
const newItem = ref({ instrument_name: '', quantity: 1, unit_price: 0, amount: 0 })

const selectedItemId = ref(null)
const executions = ref([])
const execLoading = ref(false)
const execSaving = ref(false)
const newExec = ref({ actual_date: null, actual_quantity: 1, actual_amount: 0 })

const reconVisible = ref(false)
const reconLoading = ref(false)
const reconData = ref(null)

function syncFieldKeys() { fieldKeys.value = Object.keys(form.value.fields || {}) }
function addField() {
  const key = '字段' + (Object.keys(form.value.fields || {}).length + 1)
  form.value.fields = { ...form.value.fields, [key]: '' }; syncFieldKeys()
}
function removeField(key) {
  const updated = { ...form.value.fields }; delete updated[key]
  form.value.fields = updated; syncFieldKeys()
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.value.year) params.year = filters.value.year
    const res = await getContractList(params)
    tableData.value = res.data.data || []
    total.value = res.data.meta?.total || 0
  } catch { ElMessage.error('获取列表失败') } finally { loading.value = false }
}

function doSearch() { page.value = 1; fetchData() }
function resetFilters() { filters.value = { year: null }; doSearch() }
function onSizeChange(v) { pageSize.value = v; page.value = 1; fetchData() }

function openCreate() {
  form.value = { contract_no: '', agency_id: null, year: new Date().getFullYear(), total_amount: null, fields: {} }
  syncFieldKeys(); dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.contract_no || !form.value.agency_id) {
    ElMessage.warning('请填写合同编号和检测院'); return
  }
  saving.value = true
  try {
    await createContract(form.value)
    ElMessage.success('创建成功'); dialogVisible.value = false; fetchData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') } finally { saving.value = false }
}

async function openItems(row) {
  currentContract.value = row; itemsVisible.value = true; selectedItemId.value = null; executions.value = []
  itemsLoading.value = true
  try {
    const res = await getContract(row.id)
    items.value = res.data.data?.items || []
  } catch { items.value = [] } finally { itemsLoading.value = false }
}

async function handleAddItem() {
  if (!newItem.value.instrument_name) { ElMessage.warning('请输入仪器名称'); return }
  itemSaving.value = true
  try {
    await addContractItem(currentContract.value.id, { ...newItem.value, department_id: currentContract.value.department_id })
    ElMessage.success('明细已添加')
    newItem.value = { instrument_name: '', quantity: 1, unit_price: 0, amount: 0 }
    const res = await getContract(currentContract.value.id)
    items.value = res.data.data?.items || []
  } catch (e) { ElMessage.error(e.response?.data?.detail || '添加失败') } finally { itemSaving.value = false }
}

async function handleDeleteItem(row) {
  try {
    await ElMessageBox.confirm('确定删除该明细？', '确认', { type: 'warning' })
    await deleteContractItem(currentContract.value.id, row.id)
    ElMessage.success('已删除')
    const res = await getContract(currentContract.value.id)
    items.value = res.data.data?.items || []
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

async function handleAddExec() {
  if (!selectedItemId.value) return
  execSaving.value = true
  try {
    await addExecution(currentContract.value.id, selectedItemId.value, { ...newExec.value })
    ElMessage.success('执行记录已添加')
    newExec.value = { actual_date: null, actual_quantity: 1, actual_amount: 0 }
    const res = await getContract(currentContract.value.id)
    items.value = res.data.data?.items || []
  } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') } finally { execSaving.value = false }
}

async function openRecon(row) {
  currentContract.value = row; reconVisible.value = true; reconLoading.value = true
  try {
    const res = await getReconciliation(row.id)
    reconData.value = res.data.data
  } catch { ElMessage.error('获取对账失败') } finally { reconLoading.value = false }
}

function onTabChange() {}

onMounted(async () => {
  fetchData()
  try { const res = await getCalibrationAgencies(); agencies.value = res.data.data || [] } catch {}
})
</script>
