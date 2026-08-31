import api from './index'

export interface LoginResponse {
  token: string
  user: { id: number; username: string }
}

export interface UserInfo {
  id: number
  username: string
  email?: string
  is_staff?: boolean
  phone?: string
  avatar?: string
}

export const login = (username: string, password: string) =>
  api.post<LoginResponse>('/api/auth/login/', { username, password }).then((r) => r.data)

export const logout = () => api.post('/api/auth/logout/')

export const getCurrentUser = () =>
  api.get<UserInfo>('/api/me/').then((r) => r.data)
