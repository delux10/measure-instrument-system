import request from './index'

// === 仪器管理 ===
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

// === 仪器分类树 ===
export function getInstrumentCategories() {
  return request({ url: '/instrument-categories/', method: 'get' })
}

// === 检测院列表 ===
export function getCalibrationAgencies() {
  return request({ url: '/calibration-agencies/', method: 'get' })
}

// === 到期预警 ===
export function getExpiringInstruments() {
  return request({ url: '/instruments/expiring', method: 'get' })
}

// === Excel 导入 ===
export function importInstruments(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/instruments/import',
    method: 'post',
    data: formData,
  })
}
