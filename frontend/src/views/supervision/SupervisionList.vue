<template>
  <div>
    <el-page-header title="监督管理" style="margin-bottom: 20px">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">监督管理</span>
      </template>
    </el-page-header>

    <el-card shadow="never">
      <el-tabs v-model="activeTab" type="border-card" @tab-change="onTabChange">
        <!-- ========== 监督模板 ========== -->
        <el-tab-pane label="监督模板" name="templates">
          <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
            <el-button type="primary" @click="openCreateTemplateDialog">新增模板</el-button>
          </div>

          <el-table :data="templateList" border stripe v-loading="templateLoading" style="width: 100%" empty-text="暂无监督模板">
            <el-table-column prop="name" label="模板名称" min-width="160" show-overflow-tooltip />
            <el-table-column label="类型" width="140" align="center">
              <template #default="{ row }">
                <el-tag :type="row.category === 'central' ? 'primary' : 'success'" size="small" effect="plain">
                  {{ categoryLabel(row.category) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="version" label="版本" width="80" align="center" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="openManageItemsDialog(row)">管理项目</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteTemplate(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- ========== 监督执行 ========== -->
        <el-tab-pane label="监督执行" name="executions">
          <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
            <el-button type="primary" @click="openCreateExecDialog">新增执行</el-button>
          </div>

          <el-table :data="executionList" border stripe v-loading="execLoading" style="width: 100%" empty-text="暂无监督执行记录">
            <el-table-column prop="template_name" label="模板名称" min-width="150" show-overflow-tooltip />
            <el-table-column prop="department_name" label="执行部门" width="140" show-overflow-tooltip />
            <el-table-column prop="execution_date" label="执行日期" width="120" />
            <el-table-column prop="executor_name" label="执行人" width="100" />
            <el-table-column label="状态" width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="execStatusType(row.status)" size="small" effect="plain">
                  {{ execStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="openViewExecDialog(row)">查看</el-button>
                <el-button v-if="row.status === 'completed'" type="warning" link size="small" @click="openReviewExecDialog(row)">审核</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- ========== 不符合项 ========== -->
        <el-tab-pane label="不符合项" name="ncr">
          <!-- 筛选栏 -->
          <el-form :inline="true" :model="ncrFilter" style="margin-bottom: 16px">
            <el-form-item label="部门">
              <el-select v-model="ncrFilter.department_id" placeholder="全部部门" clearable style="width: 160px">
                <el-option v-for="d in departmentList" :key="d.id" :label="d.name" :value="d.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="严重程度">
              <el-select v-model="ncrFilter.severity" placeholder="全部" clearable style="width: 130px">
                <el-option label="一般" value="general" />
                <el-option label="严重" value="serious" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="ncrFilter.status" placeholder="全部" clearable style="width: 140px">
                <el-option label="已开具" value="issued" />
                <el-option label="整改中" value="in_progress" />
                <el-option label="整改完成" value="completed" />
                <el-option label="已复核" value="verified" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchNcrList">查询</el-button>
              <el-button @click="resetNcrFilter">重置</el-button>
            </el-form-item>
          </el-form>

          <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
            <el-button type="primary" @click="openCreateNcrDialog">新增不符合项</el-button>
          </div>

          <el-table :data="ncrList" border stripe v-loading="ncrLoading" style="width: 100%" empty-text="暂无不符合项">
            <el-table-column prop="ncr_no" label="编号" width="150" />
            <el-table-column prop="department_name" label="部门" width="140" show-overflow-tooltip />
            <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
            <el-table-column label="严重程度" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'serious' ? 'danger' : 'warning'" size="small" effect="plain">
                  {{ row.severity === 'serious' ? '严重' : '一般' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="130" align="center">
              <template #default="{ row }">
                <el-tag :type="ncrStatusType(row.status)" size="small" effect="plain">
                  {{ ncrStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="deadline" label="期限" width="110" align="center" />
            <el-table-column label="操作" width="210" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === 'issued'" type="primary" link size="small" @click="handleNcrReceive(row)">接收</el-button>
                <el-button v-if="row.status === 'in_progress'" type="warning" link size="small" @click="openNcrSubmitDialog(row)">提交整改</el-button>
                <el-button v-if="row.status === 'completed'" type="success" link size="small" @click="handleNcrVerify(row)">复核通过</el-button>
                <el-button v-if="row.status === 'completed'" type="danger" link size="small" @click="handleNcrReject(row)">退回</el-button>
                <span v-if="row.status === 'verified'" style="color: #909399; font-size: 13px">已关闭</span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- ========== 新增模板对话框 ========== -->
    <el-dialog v-model="templateDialogVisible" title="新增模板" width="500px" :before-close="() => { templateDialogVisible = false }">
      <el-form ref="templateFormRef" :model="templateForm" :rules="templateRules" label-width="120px" style="padding-right: 20px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="类型" prop="category">
          <el-select v-model="templateForm.category" placeholder="请选择类型" style="width: 100%">
            <el-option label="部门级" value="department" />
            <el-option label="工厂级" value="central" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用部门类型" prop="department_type">
          <el-input v-model="templateForm.department_type" placeholder="如：生产、质检" />
        </el-form-item>
        <el-form-item label="版本" prop="version">
          <el-input v-model="templateForm.version" placeholder="如：v1.0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="templateDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="templateSaving" @click="handleCreateTemplate">保存</el-button>
      </template>
    </el-dialog>

    <!-- ========== 管理项目对话框 ========== -->
    <el-dialog v-model="itemsDialogVisible" :title="'管理项目 - ' + (currentTemplate?.name || '')" width="750px"
      :before-close="() => { itemsDialogVisible = false }">
      <el-table :data="templateItems" border stripe v-loading="itemsLoading" style="width: 100%" empty-text="暂无项目">
        <el-table-column type="index" label="序号" width="55" align="center" />
        <el-table-column prop="item_name" label="项目名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="standard" label="检查标准" min-width="160" show-overflow-tooltip />
        <el-table-column prop="score_standard" label="评分标准" width="100" align="center" />
        <el-table-column prop="sort_order" label="排序" width="60" align="center" />
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click="handleDeleteItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 16px; border-top: 1px solid #ebeef5; padding-top: 16px">
        <span style="font-weight: 600; margin-bottom: 8px; display: block">新增项目</span>
        <el-form :inline="true" :model="newItemForm" label-width="0">
          <el-form-item>
            <el-input v-model="newItemForm.item_name" placeholder="项目名称" style="width: 160px" />
          </el-form-item>
          <el-form-item>
            <el-input v-model="newItemForm.standard" placeholder="检查标准" style="width: 180px" />
          </el-form-item>
          <el-form-item>
            <el-input v-model="newItemForm.score_standard" placeholder="评分标准" style="width: 100px" />
          </el-form-item>
          <el-form-item>
            <el-input-number v-model="newItemForm.sort_order" :min="1" :max="999" style="width: 100px" placeholder="排序" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="itemSaving" @click="handleAddItem">添加</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>

    <!-- ========== 新增执行对话框 ========== -->
    <el-dialog v-model="execDialogVisible" title="新增监督执行" width="750px"
      :before-close="() => { execDialogVisible = false }">
      <el-form ref="execFormRef" :model="execForm" :rules="execRules" label-width="120px" style="padding-right: 20px">
        <el-form-item label="选择模板" prop="template_id">
          <el-select v-model="execForm.template_id" placeholder="请选择监督模板" style="width: 100%" @change="onTemplateChange">
            <el-option v-for="tpl in templateList" :key="tpl.id" :label="tpl.name" :value="tpl.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行部门" prop="target_department_id">
          <el-select v-model="execForm.target_department_id" placeholder="请选择执行部门" style="width: 100%">
            <el-option v-for="d in departmentList" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行日期" prop="execution_date">
          <el-date-picker v-model="execForm.execution_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="执行人" prop="executor_id">
          <el-select v-model="execForm.executor_id" placeholder="请选择执行人" style="width: 100%">
            <el-option v-for="u in userList" :key="u.id" :label="u.name || u.username" :value="u.id" />
          </el-select>
        </el-form-item>
      </el-form>

      <div v-if="execCheckItems.length > 0" style="margin-top: 12px; border-top: 1px solid #ebeef5; padding-top: 16px">
        <span style="font-weight: 600; margin-bottom: 12px; display: block">检查项目结果</span>
        <el-table :data="execCheckItems" border stripe style="width: 100%">
          <el-table-column type="index" label="序号" width="55" align="center" />
          <el-table-column prop="item_name" label="项目名称" min-width="130" show-overflow-tooltip />
          <el-table-column prop="standard" label="检查标准" min-width="140" show-overflow-tooltip />
          <el-table-column label="检查结果" width="260" align="center">
            <template #default="{ row, $index }">
              <el-radio-group v-model="row.result" size="small">
                <el-radio value="pass" border>合格</el-radio>
                <el-radio value="fail" border>不合格</el-radio>
                <el-radio value="na" border>不适用</el-radio>
              </el-radio-group>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <el-button @click="execDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="execSaving" @click="handleCreateExecution">保存</el-button>
      </template>
    </el-dialog>

    <!-- ========== 查看执行详情对话框 ========== -->
    <el-dialog v-model="viewExecDialogVisible" title="执行详情" width="800px"
      :before-close="() => { viewExecDialogVisible = false }">
      <template v-if="currentExec">
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="模板名称">{{ currentExec.template_name }}</el-descriptions-item>
          <el-descriptions-item label="执行部门">{{ currentExec.department_name }}</el-descriptions-item>
          <el-descriptions-item label="执行日期">{{ currentExec.execution_date }}</el-descriptions-item>
          <el-descriptions-item label="执行人">{{ currentExec.executor_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="execStatusType(currentExec.status)" size="small" effect="plain">
              {{ execStatusLabel(currentExec.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentExec.review_opinion" label="审核意见" :span="2">
            {{ currentExec.review_opinion }}
          </el-descriptions-item>
        </el-descriptions>

        <span style="font-weight: 600; margin-bottom: 12px; display: block">检查项目结果</span>
        <el-table :data="viewCheckItems" border stripe v-loading="viewCheckItemsLoading" style="width: 100%" empty-text="暂无检查项目">
          <el-table-column type="index" label="序号" width="55" align="center" />
          <el-table-column prop="item_name" label="项目名称" min-width="140" show-overflow-tooltip />
          <el-table-column prop="standard" label="检查标准" min-width="160" show-overflow-tooltip />
          <el-table-column label="检查结果" width="140" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.result === 'pass'" type="success" size="small" effect="plain">合格</el-tag>
              <el-tag v-else-if="row.result === 'fail'" type="danger" size="small" effect="plain">不合格</el-tag>
              <el-tag v-else-if="row.result === 'na'" type="info" size="small" effect="plain">不适用</el-tag>
              <span v-else style="color: #909399">待检查</span>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-dialog>

    <!-- ========== 审核对话框 ========== -->
    <el-dialog v-model="reviewDialogVisible" title="审核监督执行" width="500px"
      :before-close="() => { reviewDialogVisible = false }">
      <el-form ref="reviewFormRef" :model="reviewForm" :rules="reviewRules" label-width="100px">
        <el-form-item label="审核意见" prop="opinion">
          <el-input v-model="reviewForm.opinion" type="textarea" :rows="4" placeholder="请输入审核意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="reviewSaving" @click="handleReview('rejected')">退回</el-button>
        <el-button type="primary" :loading="reviewSaving" @click="handleReview('approved')">通过</el-button>
      </template>
    </el-dialog>

    <!-- ========== 新增不符合项对话框 ========== -->
    <el-dialog v-model="ncrDialogVisible" title="新增不符合项" width="600px"
      :before-close="() => { ncrDialogVisible = false }">
      <el-form ref="ncrFormRef" :model="ncrForm" :rules="ncrRules" label-width="120px" style="padding-right: 20px">
        <el-form-item label="编号" prop="ncr_no">
          <el-input v-model="ncrForm.ncr_no" placeholder="如：NCR-2026-001" />
        </el-form-item>
        <el-form-item label="部门" prop="department_id">
          <el-select v-model="ncrForm.department_id" placeholder="请选择部门" style="width: 100%">
            <el-option v-for="d in departmentList" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="ncrForm.description" type="textarea" :rows="3" placeholder="请描述不符合项情况" />
        </el-form-item>
        <el-form-item label="严重程度" prop="severity">
          <el-select v-model="ncrForm.severity" placeholder="请选择严重程度" style="width: 100%">
            <el-option label="一般" value="general" />
            <el-option label="严重" value="serious" />
          </el-select>
        </el-form-item>
        <el-form-item label="开具人" prop="issued_by">
          <el-select v-model="ncrForm.issued_by" placeholder="请选择开具人" style="width: 100%">
            <el-option v-for="u in userList" :key="u.id" :label="u.name || u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="期限" prop="deadline">
          <el-date-picker v-model="ncrForm.deadline" type="date" placeholder="选择整改期限" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ncrDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="ncrSaving" @click="handleCreateNcr">保存</el-button>
      </template>
    </el-dialog>

    <!-- ========== 提交整改措施对话框 ========== -->
    <el-dialog v-model="ncrSubmitDialogVisible" title="提交整改措施" width="500px"
      :before-close="() => { ncrSubmitDialogVisible = false }">
      <el-form ref="ncrSubmitFormRef" :model="ncrSubmitForm" :rules="ncrSubmitRules" label-width="100px">
        <el-form-item label="整改措施" prop="corrective_action">
          <el-input v-model="ncrSubmitForm.corrective_action" type="textarea" :rows="4" placeholder="请描述整改措施" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ncrSubmitDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="ncrSubmitSaving" @click="handleNcrSubmit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getTemplateList,
  createTemplate,
  deleteTemplate,
  getTemplateItemList,
  createTemplateItem,
  deleteTemplateItem,
  getExecutionList,
  createExecution,
  reviewExecution,
  getCheckItemList,
  createCheckItem,
  getNcrList,
  createNcr,
  updateNcr,
  getSupervisionDepartments,
  getUserList,
} from '../../api/supervision'

// ===== 状态 =====
const activeTab = ref('templates')

// ===== 工具函数 =====
function categoryLabel(category) {
  const map = { department: '部门级', central: '工厂级' }
  return map[category] || category || '部门级'
}

function execStatusType(status) {
  const map = { in_progress: 'warning', completed: 'success', approved: 'primary', rejected: 'info' }
  return map[status] || 'info'
}

function execStatusLabel(status) {
  const map = { in_progress: '进行中', completed: '已完成', approved: '已审核', rejected: '已退回' }
  return map[status] || status || '未知'
}

function ncrStatusType(status) {
  const map = { issued: 'danger', in_progress: 'warning', completed: 'success', verified: 'primary' }
  return map[status] || 'info'
}

function ncrStatusLabel(status) {
  const map = { issued: '已开具', in_progress: '整改中', completed: '整改完成', verified: '已复核' }
  return map[status] || status || '未知'
}

// ===== 监督模板 =====
const templateList = ref([])
const templateLoading = ref(false)
const templateDialogVisible = ref(false)
const templateSaving = ref(false)
const templateFormRef = ref(null)
const templateForm = reactive({
  name: '',
  category: 'department',
  department_type: '',
  version: '',
})
const templateRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择类型', trigger: 'change' }],
}

// 管理项目
const itemsDialogVisible = ref(false)
const itemsLoading = ref(false)
const itemSaving = ref(false)
const currentTemplate = ref(null)
const templateItems = ref([])
const newItemForm = reactive({
  item_name: '',
  standard: '',
  score_standard: '',
  sort_order: 1,
})

// ===== 监督执行 =====
const executionList = ref([])
const execLoading = ref(false)

const execDialogVisible = ref(false)
const execSaving = ref(false)
const execFormRef = ref(null)
const execForm = reactive({
  template_id: null,
  target_department_id: null,
  execution_date: '',
  executor_id: null,
})
const execRules = {
  template_id: [{ required: true, message: '请选择监督模板', trigger: 'change' }],
  target_department_id: [{ required: true, message: '请选择执行部门', trigger: 'change' }],
  execution_date: [{ required: true, message: '请选择执行日期', trigger: 'change' }],
  executor_id: [{ required: true, message: '请选择执行人', trigger: 'change' }],
}

// 新增执行时加载的检查项目（按模板项目初始化）
const execCheckItems = ref([])

// 查看执行详情
const viewExecDialogVisible = ref(false)
const currentExec = ref(null)
const viewCheckItems = ref([])
const viewCheckItemsLoading = ref(false)

// 审核
const reviewDialogVisible = ref(false)
const reviewSaving = ref(false)
const reviewFormRef = ref(null)
const reviewForm = reactive({ opinion: '' })
const reviewRules = {
  opinion: [{ required: true, message: '请输入审核意见', trigger: 'blur' }],
}
const reviewingExec = ref(null)

// ===== 不符合项 =====
const ncrList = ref([])
const ncrLoading = ref(false)
const ncrFilter = reactive({
  department_id: null,
  severity: null,
  status: null,
})

const ncrDialogVisible = ref(false)
const ncrSaving = ref(false)
const ncrFormRef = ref(null)
const ncrForm = reactive({
  ncr_no: '',
  department_id: null,
  description: '',
  severity: 'general',
  issued_by: null,
  deadline: '',
})
const ncrRules = {
  ncr_no: [{ required: true, message: '请输入不符合项编号', trigger: 'blur' }],
  department_id: [{ required: true, message: '请选择部门', trigger: 'change' }],
  description: [{ required: true, message: '请描述不符合项', trigger: 'blur' }],
  severity: [{ required: true, message: '请选择严重程度', trigger: 'change' }],
  issued_by: [{ required: true, message: '请选择开具人', trigger: 'change' }],
  deadline: [{ required: true, message: '请选择期限', trigger: 'change' }],
}

// 提交整改
const ncrSubmitDialogVisible = ref(false)
const ncrSubmitSaving = ref(false)
const ncrSubmitFormRef = ref(null)
const ncrSubmitForm = reactive({ corrective_action: '' })
const ncrSubmitRules = {
  corrective_action: [{ required: true, message: '请填写整改措施', trigger: 'blur' }],
}
const ncrSubmittingRow = ref(null)

// ===== 公共数据 =====
const departmentList = ref([])
const userList = ref([])

// ===== 公共 API =====
async function fetchDepartments() {
  try {
    const res = await getSupervisionDepartments()
    departmentList.value = res.data || []
  } catch {
    departmentList.value = []
  }
}

async function fetchUsers() {
  try {
    const res = await getUserList()
    userList.value = res.data || []
  } catch {
    userList.value = []
  }
}

// ===== 监督模板 API =====
async function fetchTemplates() {
  templateLoading.value = true
  try {
    const res = await getTemplateList()
    templateList.value = res.data || []
  } catch {
    ElMessage.error('获取模板列表失败')
    templateList.value = []
  } finally {
    templateLoading.value = false
  }
}

function openCreateTemplateDialog() {
  templateForm.name = ''
  templateForm.category = 'department'
  templateForm.department_type = ''
  templateForm.version = ''
  templateDialogVisible.value = true
}

async function handleCreateTemplate() {
  const valid = await templateFormRef.value.validate().catch(() => false)
  if (!valid) return
  templateSaving.value = true
  try {
    await createTemplate({ ...templateForm })
    ElMessage.success('模板创建成功')
    templateDialogVisible.value = false
    await fetchTemplates()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  } finally {
    templateSaving.value = false
  }
}

async function handleDeleteTemplate(row) {
  try {
    await ElMessageBox.confirm(`确定要删除模板「${row.name}」吗？`, '删除确认', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteTemplate(row.id)
    ElMessage.success('模板已删除')
    await fetchTemplates()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// ===== 模板项目 API =====
async function openManageItemsDialog(template) {
  currentTemplate.value = template
  itemsDialogVisible.value = true
  await fetchTemplateItems(template.id)
}

async function fetchTemplateItems(templateId) {
  itemsLoading.value = true
  try {
    const res = await getTemplateItemList(templateId)
    templateItems.value = res.data || []
  } catch {
    ElMessage.error('获取模板项目失败')
    templateItems.value = []
  } finally {
    itemsLoading.value = false
  }
}

async function handleAddItem() {
  if (!newItemForm.item_name) {
    ElMessage.warning('请输入项目名称')
    return
  }
  itemSaving.value = true
  try {
    await createTemplateItem(currentTemplate.value.id, {
      item_name: newItemForm.item_name,
      standard: newItemForm.standard,
      score_standard: newItemForm.score_standard,
      sort_order: newItemForm.sort_order,
    })
    ElMessage.success('项目已添加')
    newItemForm.item_name = ''
    newItemForm.standard = ''
    newItemForm.score_standard = ''
    newItemForm.sort_order = 1
    await fetchTemplateItems(currentTemplate.value.id)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '添加失败')
  } finally {
    itemSaving.value = false
  }
}

async function handleDeleteItem(row) {
  try {
    await ElMessageBox.confirm(`确定要删除项目「${row.item_name}」吗？`, '删除确认', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteTemplateItem(currentTemplate.value.id, row.id)
    ElMessage.success('项目已删除')
    await fetchTemplateItems(currentTemplate.value.id)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// ===== 监督执行 API =====
async function fetchExecutions() {
  execLoading.value = true
  try {
    const res = await getExecutionList()
    executionList.value = res.data || []
  } catch {
    executionList.value = []
  } finally {
    execLoading.value = false
  }
}

function openCreateExecDialog() {
  execForm.template_id = null
  execForm.target_department_id = null
  execForm.execution_date = ''
  execForm.executor_id = null
  execCheckItems.value = []
  execDialogVisible.value = true
}

async function onTemplateChange(templateId) {
  execCheckItems.value = []
  if (!templateId) return
  try {
    const res = await getTemplateItemList(templateId)
    const items = res.data || []
    execCheckItems.value = items.map(item => ({
      item_name: item.item_name,
      standard: item.standard,
      result: null,
    }))
    if (items.length === 0) {
      ElMessage.info('该模板下没有检查项目')
    }
  } catch {
    ElMessage.error('加载模板项目失败')
  }
}

async function handleCreateExecution() {
  const valid = await execFormRef.value.validate().catch(() => false)
  if (!valid) return

  // 验证检查结果是否都已填写
  if (execCheckItems.value.length > 0) {
    const unfilled = execCheckItems.value.some(item => item.result === null)
    if (unfilled) {
      ElMessage.warning('请填写所有检查项目的检查结果')
      return
    }
  }

  execSaving.value = true
  try {
    // 1. 创建执行记录
    const execRes = await createExecution({
      template_id: execForm.template_id,
      target_department_id: execForm.target_department_id,
      execution_date: execForm.execution_date,
      executor_id: execForm.executor_id,
      status: 'in_progress',
    })
    const newExecId = execRes.data?.id || execRes.id

    // 2. 批量创建检查项目结果
    if (execCheckItems.value.length > 0) {
      const promises = execCheckItems.value.map(item =>
        createCheckItem(newExecId, {
          template_item_id: item.id,
          result: item.result,
        })
      )
      await Promise.all(promises)
    }

    ElMessage.success('监督执行创建成功')
    execDialogVisible.value = false
    await fetchExecutions()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建执行失败')
  } finally {
    execSaving.value = false
  }
}

async function openViewExecDialog(row) {
  currentExec.value = row
  viewCheckItems.value = []
  viewExecDialogVisible.value = true

  viewCheckItemsLoading.value = true
  try {
    const res = await getCheckItemList(row.id)
    viewCheckItems.value = res.data || []
  } catch {
    ElMessage.error('获取检查项目失败')
    viewCheckItems.value = []
  } finally {
    viewCheckItemsLoading.value = false
  }
}

function openReviewExecDialog(row) {
  reviewingExec.value = row
  reviewForm.opinion = ''
  reviewDialogVisible.value = true
}

async function handleReview(action) {
  const valid = await reviewFormRef.value.validate().catch(() => false)
  if (!valid) return

  reviewSaving.value = true
  try {
    await reviewExecution(reviewingExec.value.id, {
      opinion: reviewForm.opinion,
      action: action,
    })
    ElMessage.success(action === 'approved' ? '审核通过' : '已退回')
    reviewDialogVisible.value = false
    await fetchExecutions()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '审核失败')
  } finally {
    reviewSaving.value = false
  }
}

// ===== 不符合项 API =====
async function fetchNcrList() {
  ncrLoading.value = true
  try {
    const params = {}
    if (ncrFilter.department_id) params.department_id = ncrFilter.department_id
    if (ncrFilter.severity) params.severity = ncrFilter.severity
    if (ncrFilter.status) params.status = ncrFilter.status
    const res = await getNcrList(params)
    ncrList.value = res.data || []
  } catch {
    ncrList.value = []
  } finally {
    ncrLoading.value = false
  }
}

function resetNcrFilter() {
  ncrFilter.department_id = null
  ncrFilter.severity = null
  ncrFilter.status = null
  fetchNcrList()
}

function openCreateNcrDialog() {
  ncrForm.ncr_no = ''
  ncrForm.department_id = null
  ncrForm.description = ''
  ncrForm.severity = 'general'
  ncrForm.issued_by = null
  ncrForm.deadline = ''
  ncrDialogVisible.value = true
}

async function handleCreateNcr() {
  const valid = await ncrFormRef.value.validate().catch(() => false)
  if (!valid) return
  ncrSaving.value = true
  try {
    await createNcr({
      ncr_no: ncrForm.ncr_no,
      department_id: ncrForm.department_id,
      description: ncrForm.description,
      severity: ncrForm.severity,
      issued_by: ncrForm.issued_by,
      deadline: ncrForm.deadline,
      status: 'issued',
    })
    ElMessage.success('不符合项创建成功')
    ncrDialogVisible.value = false
    await fetchNcrList()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  } finally {
    ncrSaving.value = false
  }
}

async function handleNcrReceive(row) {
  try {
    await ElMessageBox.confirm(`确定要接收不符合项「${row.ncr_no}」吗？`, '接收确认', {
      confirmButtonText: '确定接收',
      cancelButtonText: '取消',
      type: 'info',
    })
    await updateNcr(row.id, { status: 'in_progress' })
    ElMessage.success('已接收，开始整改')
    await fetchNcrList()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

function openNcrSubmitDialog(row) {
  ncrSubmittingRow.value = row
  ncrSubmitForm.corrective_action = ''
  ncrSubmitDialogVisible.value = true
}

async function handleNcrSubmit() {
  const valid = await ncrSubmitFormRef.value.validate().catch(() => false)
  if (!valid) return
  ncrSubmitSaving.value = true
  try {
    await updateNcr(ncrSubmittingRow.value.id, {
      status: 'completed',
      corrective_action: ncrSubmitForm.corrective_action,
    })
    ElMessage.success('整改措施已提交')
    ncrSubmitDialogVisible.value = false
    await fetchNcrList()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally {
    ncrSubmitSaving.value = false
  }
}

async function handleNcrVerify(row) {
  try {
    await ElMessageBox.confirm(`确定要复核通过不符合项「${row.ncr_no}」吗？`, '复核确认', {
      confirmButtonText: '确定通过',
      cancelButtonText: '取消',
      type: 'success',
    })
    await updateNcr(row.id, { status: 'verified' })
    ElMessage.success('复核通过，不符合项已关闭')
    await fetchNcrList()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

async function handleNcrReject(row) {
  try {
    await ElMessageBox.confirm(`确定要退回不符合项「${row.ncr_no}」要求重新整改吗？`, '退回确认', {
      confirmButtonText: '确定退回',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await updateNcr(row.id, { status: 'in_progress' })
    ElMessage.success('已退回，重新整改')
    await fetchNcrList()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

// ===== Tab 切换 =====
function onTabChange(tabName) {
  if (tabName === 'executions') {
    fetchExecutions()
  } else if (tabName === 'ncr') {
    fetchNcrList()
  }
}

// ===== 生命周期 =====
onMounted(async () => {
  await Promise.all([
    fetchTemplates(),
    fetchExecutions(),
    fetchNcrList(),
    fetchDepartments(),
    fetchUsers(),
  ])
})
</script>
