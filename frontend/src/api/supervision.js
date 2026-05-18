import request from './index'

export function getExecutionList(params) {
  return request({ url: '/supervision/executions', method: 'get', params })
}

export function createExecution(data) {
  return request({ url: '/supervision/executions', method: 'post', data })
}

export function updateExecution(id, data) {
  return request({ url: `/supervision/executions/${id}`, method: 'put', data })
}

export function reviewExecution(id, data) {
  return request({ url: `/supervision/executions/${id}/review`, method: 'post', data })
}

export function getNcrList(params) {
  return request({ url: '/supervision/non-conformities', method: 'get', params })
}

export function createNcr(data) {
  return request({ url: '/supervision/non-conformities', method: 'post', data })
}

export function updateNcr(id, data) {
  return request({ url: `/supervision/non-conformities/${id}`, method: 'put', data })
}

export function getDepartmentList() {
  return request({ url: '/admin/departments', method: 'get' })
}

export function getUserList() {
  return request({ url: '/admin/users', method: 'get' })
}
