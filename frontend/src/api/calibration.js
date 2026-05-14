import request from './index'

// === 检定记录 ===
export function getCalibrationList(params) {
  return request({ url: '/calibration-records/', method: 'get', params })
}

export function createCalibration(data) {
  return request({ url: '/calibration-records/', method: 'post', data })
}

export function updateCalibration(id, data) {
  return request({ url: `/calibration-records/${id}`, method: 'put', data })
}

export function deleteCalibration(id) {
  return request({ url: `/calibration-records/${id}`, method: 'delete' })
}

// === 检测院 ===
export function getAgencyList() {
  return request({ url: '/calibration-agencies/', method: 'get' })
}

export function createAgency(data) {
  return request({ url: '/calibration-agencies/', method: 'post', data })
}
