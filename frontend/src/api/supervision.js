import request from './index'

// === 监督模板 ===
export function getTemplateList(params) {
  return request({ url: '/supervision-templates/', method: 'get', params })
}

export function createTemplate(data) {
  return request({ url: '/supervision-templates/', method: 'post', data })
}

export function deleteTemplate(id) {
  return request({ url: `/supervision-templates/${id}`, method: 'delete' })
}

// === 监督模板项目（路由嵌套在模板下） ===
export function getTemplateItemList(templateId, params) {
  return request({ url: `/supervision-templates/${templateId}/items`, method: 'get', params })
}

export function createTemplateItem(templateId, data) {
  return request({ url: `/supervision-templates/${templateId}/items`, method: 'post', data })
}

export function deleteTemplateItem(templateId, itemId) {
  return request({ url: `/supervision-templates/${templateId}/items/${itemId}`, method: 'delete' })
}

// === 监督计划 ===
export function getPlanList(params) {
  return request({ url: '/supervision-plans/', method: 'get', params })
}

export function createPlan(data) {
  return request({ url: '/supervision-plans/', method: 'post', data })
}

// === 监督执行 ===
export function getExecutionList(params) {
  return request({ url: '/supervision-executions/', method: 'get', params })
}

export function createExecution(data) {
  return request({ url: '/supervision-executions/', method: 'post', data })
}

export function reviewExecution(id, data) {
  return request({ url: `/supervision-executions/${id}/review`, method: 'put', data })
}

// === 检查项目（嵌套在监督执行下） ===
export function getCheckItemList(execId) {
  return request({ url: `/supervision-executions/${execId}/check-items`, method: 'get' })
}

export function createCheckItem(execId, data) {
  return request({ url: `/supervision-executions/${execId}/check-items`, method: 'post', data })
}

export function updateCheckItem(execId, itemId, data) {
  return request({ url: `/supervision-executions/${execId}/check-items/${itemId}`, method: 'put', data })
}

// === 不符合项 ===
export function getNcrList(params) {
  return request({ url: '/non-conformities/', method: 'get', params })
}

export function createNcr(data) {
  return request({ url: '/non-conformities/', method: 'post', data })
}

export function updateNcr(id, data) {
  return request({ url: `/non-conformities/${id}`, method: 'put', data })
}

// === 部门列表 ===
export function getSupervisionDepartments() {
  return request({ url: '/departments/all', method: 'get' })
}

// === 用户列表 ===
export function getUserList() {
  return request({ url: '/users/', method: 'get' })
}
