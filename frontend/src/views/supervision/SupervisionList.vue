<template>
  <div>
    <el-page-header title="监督管理" style="margin-bottom: 20px">
      <template #content><span style="font-size:18px;font-weight:600">监督管理</span></template>
    </el-page-header>

    <el-card shadow="never">
      <el-tabs v-model="activeTab" type="border-card" @tab-change="onTabChange">
        <!-- 监督执行 -->
        <el-tab-pane label="监督执行" name="executions">
          <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
            <el-button type="primary" @click="openCreateExec">新增执行</el-button>
          </div>

          <el-table :data="executionList" border stripe v-loading="execLoading" style="width: 100%">
            <el-table-column prop="template_name" label="模板名称" min-width="140" />
            <el-table-column label="执行部门" width="160">
              <template #default="{ row }">{{ row.department_name || '-' }}</template>
            </el-table-column>
            <el-table-column label="计划日期" width="120">
              <template #default="{ row }">{{ row.plan_date || '-' }}</template>
            </el-table-column>
            <el-table-column label="执行日期" width="120">
              <template #default="{ row }">{{ row.executed_date || '-' }}</template>
            </el-table-column>
            <el-table-column label="状态" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="execStatusType(row.status)" size="small">{{ execStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="openExecDetail(row)">查看</el-button>
                <el-button type="warning" link size="small" @click="openExecEdit(row)">填写</el-button>
                <el-button v-if="row.status === 'completed'" type="success" link size="small" @click="openReview(row)">审核</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div style="display: flex; justify-content: flex-end; margin-top: 16px">
            <el-pagination v-model:current-page="execPage" :page-size="execPageSize" :total="execTotal"
              :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @size-change="onExecSizeChange" @current-change="fetchExecutions" />
          </div>
        </el-tab-pane>

        <!-- 不符合项 -->
        <el-tab-pane label="不符合项" name="ncr">
          <el-form :inline="true" :model="ncrFilter" style="margin-bottom: 16px">
            <el-form-item label="严重程度">
              <el-select v-model="ncrFilter.severity" placeholder="全部" clearable style="width: 120px">
                <el-option label="一般" value="general" />
                <el-option label="严重" value="serious" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="ncrFilter.status" placeholder="全部" clearable style="width: 130px">
                <el-option label="已开具" value="issued" />
                <el-option label="整改中" value="in_progress" />
                <el-option label="整改完成" value="completed" />
                <el-option label="已复核" value="verified" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchNcrs">查询</el-button>
              <el-button @click="resetNcrFilter">重置</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="ncrList" border stripe v-loading="ncrLoading" style="width: 100%">
            <el-table-column prop="ncr_no" label="编号" width="150" />
            <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
            <el-table-column label="严重程度" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'serious' ? 'danger' : 'warning'" size="small">
                  {{ row.severity === 'serious' ? '严重' : '一般' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="ncrStatusType(row.status)" size="small">{{ ncrStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="期限" width="110">
              <template #default="{ row }">{{ row.deadline || '-' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === 'issued'" type="primary" link size="small" @click="handleNcrReceive(row)">接收</el-button>
                <el-button v-if="row.status === 'in_progress'" type="warning" link size="small" @click="openNcrSubmit(row)">提交整改</el-button>
                <el-button v-if="row.status === 'completed'" type="success" link size="small" @click="handleNcrVerify(row)">复核通过</el-button>
                <el-button v-if="row.status === 'completed'" type="danger" link size="small" @click="handleNcrReject(row)">退回</el-button>
                <span v-if="row.status === 'verified'" style="color:#909399;font-size:13px">已关闭</span>
              </template>
            </el-table-column>
          </el-table>

          <div style="display: flex; justify-content: flex-end; margin-top: 16px">
            <el-pagination v-model:current-page="ncrPage" :page-size="ncrPageSize" :total="ncrTotal"
              :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @size-change="onNcrSizeChange" @current-change="fetchNcrs" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 新增执行对话框 -->
    <el-dialog v-model="execDialogVisible" title="新增监督执行" width="600px">
      <el-form ref="execFormRef" :model="execForm" label-width="100px">
        <el-form-item label="模板名称">
          <el-input v-model="execForm.template_name" placeholder="如：月度检查表" />
        </el-form-item>
        <el-form-item label="执行部门" required>
          <el-select v-model="execForm.department_id" placeholder="请选择" style="width: 100%">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划日期">
          <el-date-picker v-model="execForm.plan_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-divider>检查项目</el-divider>
        <div v-for="(item, idx) in execForm.check_items" :key="idx" style="margin-bottom: 8px">
          <el-row :gutter="8">
            <el-col :span="10"><el-input v-model="item.item_name" placeholder="项目名称" /></el-col>
            <el-col :span="8"><el-input v-model="item.standard" placeholder="检查标准" /></el-col>
            <el-col :span="4">
              <el-select v-model="item.result" placeholder="结果" size="small">
                <el-option label="合格" value="pass" />
                <el-option label="不合格" value="fail" />
                <el-option label="不适用" value="na" />
              </el-select>
            </el-col>
            <el-col :span="2"><el-button @click="removeCheckItem(idx)" icon="Delete" circle size="small" /></el-col>
          </el-row>
        </div>
        <el-button @click="addCheckItem" size="small" type="primary" plain>+ 添加检查项</el-button>
      </el-form>
      <template #footer>
        <el-button @click="execDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="execSaving" @click="handleCreateExec">保存</el-button>
      </template>
    </el-dialog>

    <!-- 查看执行详情 -->
    <el-dialog v-model="execDetailVisible" title="执行详情" width="800px">
      <template v-if="currentExec">
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="模板">{{ currentExec.template_name }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ currentExec.department_name }}</el-descriptions-item>
          <el-descriptions-item label="计划日期">{{ currentExec.plan_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="执行日期">{{ currentExec.executed_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="execStatusType(currentExec.status)" size="small">{{ execStatusLabel(currentExec.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentExec.review_opinion" label="审核意见" :span="2">{{ currentExec.review_opinion }}</el-descriptions-item>
        </el-descriptions>
        <el-table :data="currentExec.check_items || []" border stripe>
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="item_name" label="项目名称" min-width="140" />
          <el-table-column prop="standard" label="检查标准" min-width="160" />
          <el-table-column label="结果" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.result === 'pass'" type="success" size="small">合格</el-tag>
              <el-tag v-else-if="row.result === 'fail'" type="danger" size="small">不合格</el-tag>
              <el-tag v-else-if="row.result === 'na'" type="info" size="small">不适用</el-tag>
              <span v-else style="color:#909399">待检查</span>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-dialog>

    <!-- 填写检查结果 -->
    <el-dialog v-model="execEditVisible" title="填写检查结果" width="800px">
      <el-table :data="editCheckItems" border stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="item_name" label="项目名称" min-width="140" />
        <el-table-column prop="standard" label="检查标准" min-width="160" />
        <el-table-column label="检查结果" width="260" align="center">
          <template #default="{ row }">
            <el-radio-group v-model="row.result" size="small">
              <el-radio value="pass" border>合格</el-radio>
              <el-radio value="fail" border>不合格</el-radio>
              <el-radio value="na" border>不适用</el-radio>
            </el-radio-group>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="execEditVisible = false">取消</el-button>
        <el-button type="primary" :loading="execSaving" @click="handleSubmitExec">提交结果</el-button>
      </template>
    </el-dialog>

    <!-- 审核对话框 -->
    <el-dialog v-model="reviewVisible" title="审核" width="500px">
      <el-form ref="reviewFormRef" :model="reviewForm" label-width="100px">
        <el-form-item label="审核意见" required>
          <el-input v-model="reviewForm.opinion" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="danger" :loading="reviewSaving" @click="handleReview('rejected')">退回</el-button>
        <el-button type="primary" :loading="reviewSaving" @click="handleReview('approved')">通过</el-button>
      </template>
    </el-dialog>

    <!-- 提交整改对话框 -->
    <el-dialog v-model="ncrSubmitVisible" title="提交整改措施" width="500px">
      <el-form ref="ncrSubmitFormRef" :model="ncrSubmitForm" label-width="100px">
        <el-form-item label="整改措施" required>
          <el-input v-model="ncrSubmitForm.corrective_action" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ncrSubmitVisible = false">取消</el-button>
        <el-button type="primary" :loading="ncrSubmitSaving" @click="handleNcrSubmit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExecutionList, createExecution, updateExecution, reviewExecution, getNcrList, updateNcr, getDepartmentList, getUserList } from '../../api/supervision'

// State
const activeTab = ref('executions')

function execStatusType(s) {
  const m = { in_progress: 'warning', completed: 'success', approved: 'primary', rejected: 'info' }
  return m[s] || 'info'
}
function execStatusLabel(s) {
  const m = { in_progress: '进行中', completed: '已完成', approved: '已审核', rejected: '已退回' }
  return m[s] || s || '未知'
}
function ncrStatusType(s) {
  const m = { issued: 'danger', in_progress: 'warning', completed: 'success', verified: 'primary' }
  return m[s] || 'info'
}
function ncrStatusLabel(s) {
  const m = { issued: '已开具', in_progress: '整改中', completed: '整改完成', verified: '已复核' }
  return m[s] || s || '未知'
}

// Executions
const executionList = ref([])
const execLoading = ref(false)
const execPage = ref(1)
const execPageSize = ref(20)
const execTotal = ref(0)
const execDialogVisible = ref(false)
const execSaving = ref(false)
const execFormRef = ref(null)
const execForm = reactive({ template_name: '', department_id: null, plan_date: null, check_items: [] })
const departments = ref([])

function addCheckItem() { execForm.check_items.push({ item_name: '', standard: '', result: null }) }
function removeCheckItem(idx) { execForm.check_items.splice(idx, 1) }

const execDetailVisible = ref(false)
const currentExec = ref(null)
const execEditVisible = ref(false)
const editCheckItems = ref([])
const editingExecId = ref(null)

const reviewVisible = ref(false)
const reviewSaving = ref(false)
const reviewFormRef = ref(null)
const reviewForm = reactive({ opinion: '' })
const reviewingId = ref(null)

// NCRs
const ncrList = ref([])
const ncrLoading = ref(false)
const ncrPage = ref(1)
const ncrPageSize = ref(20)
const ncrTotal = ref(0)
const ncrFilter = reactive({ severity: null, status: null })

const ncrSubmitVisible = ref(false)
const ncrSubmitSaving = ref(false)
const ncrSubmitFormRef = ref(null)
const ncrSubmitForm = reactive({ corrective_action: '' })
const ncrSubmittingRow = ref(null)

async function fetchExecutions() {
  execLoading.value = true
  try {
    const res = await getExecutionList({ page: execPage.value, page_size: execPageSize.value })
    executionList.value = res.data.data || []
    execTotal.value = res.data.meta?.total || 0
  } catch { executionList.value = [] } finally { execLoading.value = false }
}
function onExecSizeChange(v) { execPageSize.value = v; execPage.value = 1; fetchExecutions() }

function openCreateExec() {
  execForm.template_name = ''; execForm.department_id = null; execForm.plan_date = null; execForm.check_items = []
  execDialogVisible.value = true
}

async function handleCreateExec() {
  if (!execForm.department_id) { ElMessage.warning('请选择执行部门'); return }
  execSaving.value = true
  try {
    await createExecution({ ...execForm })
    ElMessage.success('创建成功'); execDialogVisible.value = false; fetchExecutions()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '创建失败') } finally { execSaving.value = false }
}

function openExecDetail(row) { currentExec.value = row; execDetailVisible.value = true }

function openExecEdit(row) {
  editingExecId.value = row.id
  editCheckItems.value = JSON.parse(JSON.stringify(row.check_items || []))
  execEditVisible.value = true
}

async function handleSubmitExec() {
  execSaving.value = true
  try {
    await updateExecution(editingExecId.value, {
      check_items: editCheckItems.value,
      executed_date: new Date().toISOString().slice(0, 10),
      status: 'completed'
    })
    ElMessage.success('结果已提交'); execEditVisible.value = false; fetchExecutions()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '提交失败') } finally { execSaving.value = false }
}

function openReview(row) { reviewingId.value = row.id; reviewForm.opinion = ''; reviewVisible.value = true }

async function handleReview(action) {
  if (!reviewForm.opinion) { ElMessage.warning('请输入审核意见'); return }
  reviewSaving.value = true
  try {
    await reviewExecution(reviewingId.value, { action, opinion: reviewForm.opinion })
    ElMessage.success(action === 'approved' ? '审核通过' : '已退回')
    reviewVisible.value = false; fetchExecutions()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '审核失败') } finally { reviewSaving.value = false }
}

async function fetchNcrs() {
  ncrLoading.value = true
  try {
    const params = { page: ncrPage.value, page_size: ncrPageSize.value }
    if (ncrFilter.severity) params.severity = ncrFilter.severity
    if (ncrFilter.status) params.status = ncrFilter.status
    const res = await getNcrList(params)
    ncrList.value = res.data.data || []
    ncrTotal.value = res.data.meta?.total || 0
  } catch { ncrList.value = [] } finally { ncrLoading.value = false }
}
function onNcrSizeChange(v) { ncrPageSize.value = v; ncrPage.value = 1; fetchNcrs() }
function resetNcrFilter() { ncrFilter.severity = null; ncrFilter.status = null; ncrPage.value = 1; fetchNcrs() }

async function handleNcrReceive(row) {
  try {
    await ElMessageBox.confirm(`确定接收不符合项「${row.ncr_no}」？`, '确认', { type: 'info' })
    await updateNcr(row.id, { status: 'in_progress' })
    ElMessage.success('已接收'); fetchNcrs()
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

function openNcrSubmit(row) { ncrSubmittingRow.value = row; ncrSubmitForm.corrective_action = ''; ncrSubmitVisible.value = true }

async function handleNcrSubmit() {
  if (!ncrSubmitForm.corrective_action) { ElMessage.warning('请填写整改措施'); return }
  ncrSubmitSaving.value = true
  try {
    await updateNcr(ncrSubmittingRow.value.id, { status: 'completed', corrective_action: ncrSubmitForm.corrective_action })
    ElMessage.success('已提交'); ncrSubmitVisible.value = false; fetchNcrs()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '提交失败') } finally { ncrSubmitSaving.value = false }
}

async function handleNcrVerify(row) {
  try {
    await ElMessageBox.confirm(`确定复核通过「${row.ncr_no}」？`, '确认', { type: 'success' })
    await updateNcr(row.id, { status: 'verified' })
    ElMessage.success('已通过'); fetchNcrs()
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

async function handleNcrReject(row) {
  try {
    await ElMessageBox.confirm(`确定退回「${row.ncr_no}」？`, '确认', { type: 'warning' })
    await updateNcr(row.id, { status: 'in_progress' })
    ElMessage.success('已退回'); fetchNcrs()
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

function onTabChange(tab) {
  if (tab === 'executions') fetchExecutions()
  else if (tab === 'ncr') fetchNcrs()
}

onMounted(async () => {
  await Promise.all([fetchExecutions(), fetchNcrs()])
  try { const res = await getDepartmentList(); departments.value = res.data.data || [] } catch {}
})
</script>
