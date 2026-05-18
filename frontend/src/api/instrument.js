import request from './index'

export function getInstrumentList(params) {
  return request({ url: '/instruments/', method: 'get', params })
}

export function createInstrument(data) {
  return request({ url: '/instruments/', method: 'post', data })
}

export function getInstrument(id) {
  return request({ url: `/instruments/${id}`, method: 'get' })
}

export function updateInstrument(id, data) {
  return request({ url: `/instruments/${id}`, method: 'put', data })
}

export function deleteInstrument(id) {
  return request({ url: `/instruments/${id}`, method: 'delete' })
}

export function clearAllInstruments() {
  return request({ url: '/instruments/batch/clear', method: 'delete' })
}

export function importInstruments(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({ url: '/instruments/import', method: 'post', data: formData, timeout: 120000 })
}

export function exportInstruments(params) {
  return request({ url: '/instruments/export/excel', method: 'get', params, responseType: 'blob' })
}

export function getInstrumentCategories() {
  return request({ url: '/admin/categories', method: 'get' })
}

export function getCalibrationAgencies() {
  return request({ url: '/calibration/agencies', method: 'get' })
}
