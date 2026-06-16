import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    const { data } = response
    if (data.code === 0) {
      return data.data
    }
    ElMessage.error(data.message || '请求失败')
    return Promise.reject(new Error(data.message))
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '网络错误'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 用例管理API
export const caseApi = {
  getList: (params) => api.get('/case/list', { params }),
  getDetail: (id) => api.get(`/case/${id}`),
  create: (data) => api.post('/case/create', data),
  update: (id, data) => api.put(`/case/${id}`, data),
  delete: (id) => api.delete(`/case/${id}`),
  batchDelete: (ids) => api.post('/case/batch-delete', ids),
  copy: (id) => api.post(`/case/copy/${id}`),
  export: (ids) => api.post('/case/export', ids),
  import: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/case/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getModules: () => api.get('/case/modules/list'),
  getTags: () => api.get('/case/tags/list'),
}

// 元素管理API
export const elementApi = {
  getList: (params) => api.get('/element/list', { params }),
  getDetail: (id) => api.get(`/element/${id}`),
  create: (data) => api.post('/element/create', data),
  update: (id, data) => api.put(`/element/${id}`, data),
  delete: (id) => api.delete(`/element/${id}`),
  batchDelete: (ids) => api.post('/element/batch-delete', ids),
  healthCheck: (params) => api.post('/element/health-check', params),
  getPages: () => api.get('/element/pages/list'),
  getModules: () => api.get('/element/modules/list'),
  export: (ids) => api.post('/element/export', ids),
  import: (data) => api.post('/element/import', data),
  batchSync: (params) => api.post('/element/batch-sync', null, { params }),
}

// 执行引擎API
export const execApi = {
  run: (data) => api.post('/exec/run', data),
  runSuite: (suiteId, params) => api.post(`/exec/run-suite/${suiteId}`, null, { params }),
  getStatus: (taskId) => api.get(`/exec/status/${taskId}`),
  control: (taskId, action) => api.post(`/exec/control/${taskId}`, { action }),
  getLog: (taskId, params) => api.get(`/exec/log/${taskId}`, { params }),
  getScreenshot: (taskId, params) => api.get(`/exec/screenshot/${taskId}`, { params }),
  getTasks: (params) => api.get('/exec/tasks', { params }),
  debugStep: (data) => api.post('/exec/debug/step', data),
  debugBreakpoint: (data) => api.post('/exec/debug/breakpoint', data),
}

// 报告API
export const reportApi = {
  getList: (params) => api.get('/report/list', { params }),
  getDetail: (taskId) => api.get(`/report/${taskId}`),
  getHtml: (taskId) => `/api/report/${taskId}/html`,
  getSteps: (taskId, params) => api.get(`/report/${taskId}/steps`, { params }),
  getFailureAnalysis: (taskId) => api.get(`/report/${taskId}/failure-analysis`),
  getStatisticsOverview: () => api.get('/report/statistics/overview'),
  getStatisticsTrend: (params) => api.get('/report/statistics/trend', { params }),
  exportDefect: (taskId, params) => api.post(`/report/${taskId}/export-defect`, null, { params }),
  replay: (taskId, caseId) => api.post(`/report/${taskId}/replay`, null, { params: { case_id: caseId } }),
}

// 设备管理API
export const deviceApi = {
  getList: (params) => api.get('/device/list', { params }),
  getDetail: (deviceId) => api.get(`/device/${deviceId}`),
  scan: (platform) => api.post('/device/scan', null, { params: { platform } }),
  connect: (deviceId) => api.post(`/device/${deviceId}/connect`),
  disconnect: (deviceId) => api.post(`/device/${deviceId}/disconnect`),
  screenshot: (deviceId) => api.get(`/device/${deviceId}/screenshot`),
  installApp: (deviceId, appPath) => api.post(`/device/${deviceId}/install-app`, null, { params: { app_path: appPath } }),
  uninstallApp: (deviceId, packageName) => api.post(`/device/${deviceId}/uninstall-app`, null, { params: { package_name: packageName } }),
  getBrowsers: () => api.get('/device/browsers'),
  checkDriver: (browserType) => api.post('/device/browsers/driver-check', null, { params: { browser_type: browserType } }),
}

// 任务调度API
export const schedulerApi = {
  getSuites: () => api.get('/scheduler/suites'),
  getSuiteDetail: (id) => api.get(`/scheduler/suites/${id}`),
  createSuite: (data) => api.post('/scheduler/suites', data),
  updateSuite: (id, data) => api.put(`/scheduler/suites/${id}`, data),
  deleteSuite: (id) => api.delete(`/scheduler/suites/${id}`),
  getTasks: () => api.get('/scheduler/tasks'),
  getTaskDetail: (id) => api.get(`/scheduler/tasks/${id}`),
  createTask: (data) => api.post('/scheduler/tasks', data),
  updateTask: (id, data) => api.put(`/scheduler/tasks/${id}`, data),
  deleteTask: (id) => api.delete(`/scheduler/tasks/${id}`),
  toggleTask: (id) => api.post(`/scheduler/tasks/${id}/toggle`),
}

// 系统设置API
export const systemApi = {
  getConfigs: () => api.get('/system/configs'),
  getConfig: (key) => api.get(`/system/configs/${key}`),
  updateConfig: (data) => api.put('/system/configs', data),
  batchUpdateConfigs: (data) => api.put('/system/configs/batch', data),
  getVariables: () => api.get('/system/variables'),
  createVariable: (data) => api.post('/system/variables', data),
  updateVariable: (id, data) => api.put(`/system/variables/${id}`, data),
  deleteVariable: (id) => api.delete(`/system/variables/${id}`),
  backup: () => api.post('/system/backup'),
  restore: (path) => api.post('/system/restore', null, { params: { backup_path: path } }),
  clearCache: () => api.post('/system/clear-cache'),
  getSystemInfo: () => api.get('/system/system-info'),
}

// AI辅助API
export const aiApi = {
  generateCase: (data) => api.post('/ai/generate-case', data),
  repairElement: (data) => api.post('/ai/repair-element', data),
  analyzeFailure: (data) => api.post('/ai/analyze-failure', data),
  getFailureStatistics: (params) => api.get('/ai/failure-statistics', { params }),
  getConfig: () => api.get('/ai/config'),
  updateConfig: (data) => api.put('/ai/config', data),
}

export default api
