import api from './index'

// SLB
export const getLtmVirtualServers = (params?: Record<string, any>) =>
  api.get('/api/assets/ltm-virtual-servers/', { params })

export const getLtmPools = (params?: Record<string, any>) =>
  api.get('/api/assets/ltm-pools/', { params })

// GSLB
export const getGtmWideips = (params?: Record<string, any>) =>
  api.get('/api/assets/gtm-wideips/', { params })

export const getGtmPools = (params?: Record<string, any>) =>
  api.get('/api/assets/gtm-pools/', { params })

// Firewall
export const getPolicies = (params?: Record<string, any>) =>
  api.get('/api/assets/policies/', { params })

export const getNatRules = (params?: Record<string, any>) =>
  api.get('/api/assets/nat-rules/', { params })

export const getAddressBooks = (params?: Record<string, any>) =>
  api.get('/api/assets/address-books/', { params })

export const getServices = (params?: Record<string, any>) =>
  api.get('/api/assets/services/', { params })
