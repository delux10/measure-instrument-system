import request from './index'

export function getUserList(params) {
  return request({ url: '/admin/users', method: 'get', params })
}

export function createUser(data) {
  return request({ url: '/admin/users', method: 'post', data })
}

export function updateUser(id, data) {
  return request({ url: `/admin/users/${id}`, method: 'put', data })
}

export function deleteUser(id) {
  return request({ url: `/admin/users/${id}`, method: 'delete' })
}

export function getDepartmentList() {
  return request({ url: '/admin/departments', method: 'get' })
}
