import request from './index'

export function loginApi(credentials) {
  return request({ url: '/auth/login', method: 'post', data: credentials })
}

export function getUserInfoApi() {
  return request({ url: '/auth/me', method: 'get' })
}

export function logoutApi() {
  return request({ url: '/auth/logout', method: 'post' })
}
