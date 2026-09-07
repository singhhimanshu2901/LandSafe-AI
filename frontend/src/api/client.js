import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1'

export const api = axios.create({ baseURL: API_BASE })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const login = (username, password) => {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)
  return api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  }).then(r => r.data)
}

export const getRiskList = () => api.get('/risk').then(r => r.data)
export const getLocations = () => api.get('/locations').then(r => r.data)
export const getReports = () => api.get('/reports').then(r => r.data)
export const createReport = (payload) => api.post('/reports', payload).then(r => r.data)
export const uploadEvidence = (reportId, file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/reports/${reportId}/evidence`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then(r => r.data)
}
export const getAlerts = () => api.get('/alerts').then(r => r.data)
export const getIntelligence = (id) => api.get(`/intelligence/${id}`).then(r => r.data)
export const getRiskHistory = (id) => api.get(`/risk?location_id=${id}&limit=100`).then(r => r.data)

