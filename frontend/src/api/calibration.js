import request from './index'

export function getCalibrationList(params) {
  return request({ url: '/calibration/records', method: 'get', params })
}

export function createCalibration(data) {
  return request({ url: '/calibration/records', method: 'post', data })
}

export function updateCalibration(id, data) {
  return request({ url: `/calibration/records/${id}`, method: 'put', data })
}

export function getExpiringList(days = 30) {
  return request({ url: '/calibration/expiring', method: 'get', params: { days } })
}

export function getAgencyList() {
  return request({ url: '/calibration/agencies', method: 'get' })
}

export function createAgency(data) {
  return request({ url: '/calibration/agencies', method: 'post', data })
}

export function generateCalibrationPlan(year_month, department_id) {
  return request({ url: '/calibration/generate-plan', method: 'post', params: { year_month, department_id } })
}

export function deleteCalibration(id) {
  return request({ url: `/calibration/records/${id}`, method: 'delete' })
}
