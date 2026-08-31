import api from './index'

// 设备
export const getDevices = (params?: Record<string, any>) =>
  api.get('/api/dcim/devices/', { params })

export const getDevice = (id: number) =>
  api.get(`/api/dcim/devices/${id}/`)

// 设备配置
export const getDeviceConfigs = (params?: Record<string, any>) =>
  api.get('/api/dcim/device-configs/', { params })

export const getDeviceConfig = (id: number) =>
  api.get(`/api/dcim/device-configs/${id}/`)

// 导入设备
export const importDevices = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/api/dcim/import-devices/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  })
}

// DCIM
export const getDatacenters = (params?: Record<string, any>) =>
  api.get('/api/dcim/datacenters/', { params })

export const getRooms = (params?: Record<string, any>) =>
  api.get('/api/dcim/rooms/', { params })

export const getCabinets = (params?: Record<string, any>) =>
  api.get('/api/dcim/cabinets/', { params })
