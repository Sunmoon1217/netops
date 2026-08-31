import api from './index'

export const getDevices = (params?: Record<string, any>) =>
  api.get('/api/dcim/datacenters/', { params })

export const getDatacenters = (params?: Record<string, any>) =>
  api.get('/api/dcim/datacenters/', { params })

export const getRooms = (params?: Record<string, any>) =>
  api.get('/api/dcim/rooms/', { params })

export const getCabinets = (params?: Record<string, any>) =>
  api.get('/api/dcim/cabinets/', { params })

export const getSecurityZones = (params?: Record<string, any>) =>
  api.get('/api/dcim/security-zones/', { params })
