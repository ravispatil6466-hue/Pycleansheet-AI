import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export default api

// --- Datasets ---
export const uploadDataset = (file, onProgress) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/datasets/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  })
}
export const listDatasets = () => api.get('/datasets')
export const getDataset = (id) => api.get(`/datasets/${id}`)
export const previewDataset = (id, limit = 100, offset = 0) =>
  api.get(`/datasets/${id}/preview`, { params: { limit, offset } })
export const deleteDataset = (id) => api.delete(`/datasets/${id}`)

// --- Cleaning ---
export const qualityReport = (id) => api.get(`/cleaning/${id}/quality-report`)
export const cleanMissing = (id, payload) => api.post(`/cleaning/${id}/missing`, payload)
export const cleanDuplicates = (id, payload) => api.post(`/cleaning/${id}/duplicates`, payload)
export const cleanOutliers = (id, payload) => api.post(`/cleaning/${id}/outliers`, payload)
export const convertType = (id, payload) => api.post(`/cleaning/${id}/type-conversion`, payload)
export const renameColumns = (id, payload) => api.post(`/cleaning/${id}/rename`, payload)
export const normalizeColumns = (id, payload) => api.post(`/cleaning/${id}/normalize`, payload)
export const encodeColumns = (id, payload) => api.post(`/cleaning/${id}/encode`, payload)

// --- EDA ---
export const edaSummary = (id) => api.get(`/eda/${id}/summary`)
export const edaCorrelation = (id) => api.get(`/eda/${id}/correlation`)
export const edaDistribution = (id, column) => api.get(`/eda/${id}/distribution/${column}`)
export const edaReport = (id) => api.get(`/eda/${id}/report`)

// --- Charts ---
export const fetchChartData = (id, payload) => api.post(`/charts/${id}/data`, payload)

// --- Code Execution ---
export const executeCode = (payload) => api.post(`/code/execute`, payload)

// --- AI Chat ---
export const sendChatMessage = (payload) => api.post(`/ai/chat`, payload)
export const chatHistory = (id) => api.get(`/ai/chat/${id}/history`)

// --- Export ---
export const exportUrl = (id, fmt) => `/api/export/${id}/${fmt}`

// --- Dashboards ---
export const saveDashboard = (payload) => api.post('/dashboards', payload)
export const updateDashboard = (id, payload) => api.put(`/dashboards/${id}`, payload)
export const listDashboards = () => api.get('/dashboards')
export const getDashboard = (id) => api.get(`/dashboards/${id}`)
export const deleteDashboard = (id) => api.delete(`/dashboards/${id}`)
