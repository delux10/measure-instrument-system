import request from './index'

export function loginApi(data) {
  const formData = new URLSearchParams()
  formData.append('username', data.username)
  formData.append('password', data.password)
  return request({
    url: '/auth/login',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

export function getUserInfoApi() {
  return request({ url: '/auth/me', method: 'get' })
}

export function logoutApi() {
  return Promise.resolve()
}
