import request from './index'

// === 用户管理 ===
export function getUserList(params) {
  return request({ url: '/users/', method: 'get', params })
}

export function createUser(data) {
  return request({ url: '/users/', method: 'post', data })
}

export function updateUser(id, data) {
  return request({ url: `/users/${id}`, method: 'put', data })
}

export function deleteUser(id) {
  return request({ url: `/users/${id}`, method: 'delete' })
}

// === 部门管理 ===
export function getDepartmentList() {
  return request({ url: '/departments/all', method: 'get' })
}

export function createDepartment(data) {
  return request({ url: '/departments/', method: 'post', data })
}

// === 仪器分类 ===
export function getCategoryList() {
  return request({ url: '/instrument-categories/', method: 'get' })
}
