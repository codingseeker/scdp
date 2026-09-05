import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('[API Error]', err?.response?.data || err.message)
    return Promise.reject(err)
  }
)

export const networkApi = {
  getGraph: (filters = {}) => api.get('/network', { params: filters }).then(r => r.data),
}

export const supplierApi = {
  list: (params = {}) => api.get('/suppliers', { params }).then(r => r.data),
  getDetail: (id) => api.get(`/suppliers/${id}`).then(r => r.data),
}

export const metricsApi = {
  getMetrics: () => api.get('/metrics').then(r => r.data),
}

export const simulationApi = {
  runScenario: (payload) => api.post('/simulation', payload).then(r => r.data),
  reportUrl: (id) => `/api/v1/simulations/${id}/report`,
}

export const threatsApi = {
  getThreats: () => api.get('/threats').then(r => r.data),
}

export const risksApi = {
  getSummary: () => api.get('/risks').then(r => r.data),
  getBreakdown: (id) => api.get(`/risks/${id}`).then(r => r.data),
}

export const intelligenceApi = {
  getNews: () => api.get('/intelligence/news').then(r => r.data),
  getWeather: () => api.get('/intelligence/weather').then(r => r.data),
}

export const mitigationApi = {
  getRoutes: () => api.get('/mitigation/routes').then(r => r.data),
  getSuppliers: () => api.get('/mitigation/suppliers').then(r => r.data),
}

export const healthApi = {
  getHealth: () => api.get('/health').then(r => r.data),
}

export default api
