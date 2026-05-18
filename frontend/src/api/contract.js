import request from './index'

export function getContractList(params) {
  return request({ url: '/contracts/', method: 'get', params })
}

export function getContract(id) {
  return request({ url: `/contracts/${id}`, method: 'get' })
}

export function createContract(data) {
  return request({ url: '/contracts/', method: 'post', data })
}

export function addContractItem(contractId, data) {
  return request({ url: `/contracts/${contractId}/items`, method: 'post', data })
}

export function deleteContractItem(contractId, itemId) {
  return request({ url: `/contracts/${contractId}/items/${itemId}`, method: 'delete' })
}

export function addExecution(contractId, itemId, data) {
  return request({ url: `/contracts/${contractId}/items/${itemId}/executions`, method: 'post', data })
}

export function getReconciliation(contractId) {
  return request({ url: `/contracts/${contractId}/reconciliation`, method: 'get' })
}

export function getCalibrationAgencies() {
  return request({ url: '/calibration/agencies', method: 'get' })
}
