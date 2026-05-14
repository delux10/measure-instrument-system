import request from './index'

// === 合同管理 ===
export function getContractList(params) {
  return request({ url: '/contracts/', method: 'get', params })
}

export function createContract(data) {
  return request({ url: '/contracts/', method: 'post', data })
}

export function updateContract(id, data) {
  return request({ url: `/contracts/${id}`, method: 'put', data })
}

export function deleteContract(id) {
  return request({ url: `/contracts/${id}`, method: 'delete' })
}

// === 合同明细 ===
export function getContractItems(params) {
  return request({ url: '/contract-items/', method: 'get', params })
}

export function createContractItem(data) {
  return request({ url: '/contract-items/', method: 'post', data })
}

export function updateContractItem(id, data) {
  return request({ url: `/contract-items/${id}`, method: 'put', data })
}

export function deleteContractItem(id) {
  return request({ url: `/contract-items/${id}`, method: 'delete' })
}

// === 合同版本 ===
export function getContractVersions(params) {
  return request({ url: '/contract-versions/', method: 'get', params })
}

export function uploadContractVersion(formData) {
  return request({
    url: '/contract-versions/',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// === 检测院 ===
export function getCalibrationAgencies() {
  return request({ url: '/calibration-agencies/', method: 'get' })
}

// === 执行记录 ===
export function getExecutionRecords(params) {
  return request({ url: '/execution-records/', method: 'get', params })
}

// === 对账分析 ===
export function analyzeReconciliation(id) {
  return request({ url: `/reconciliation/analyze/${id}`, method: 'post' })
}

export function getReconciliationDiffs(params) {
  return request({ url: '/reconciliation/diffs/', method: 'get', params })
}

export function confirmOrAdjustDiff(id, data) {
  return request({ url: `/reconciliation/diffs/${id}`, method: 'put', data })
}
