/**
 * API 接口封装层 / API interface encapsulation layer
 * @Function: 封装所有后端 API 调用，统一请求/响应处理 / Encapsulate all backend API calls with unified request/response handling
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例 / Create axios instance
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 / Request interceptor
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等认证信息 / Add token or auth info here
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 / Response interceptor
api.interceptors.response.use(
  (response) => {
    const { data } = response
    // 业务成功 / Business success
    if (data.code === 0) {
      return data.data
    }
    // 业务失败，弹出错误提示 / Business failure, show error message
    ElMessage.error(data.message || '请求失败')
    return Promise.reject(new Error(data.message))
  },
  (error) => {
    // HTTP 错误处理 / HTTP error handling
    const message = error.response?.data?.detail || error.message || '网络错误'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// ==================== 用例管理 API / Test Case API ====================
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

// ==================== 元素管理 API / Element Management API ====================
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

// ==================== 执行引擎 API / Execution Engine API ====================
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

// ==================== 测试报告 API / Test Report API ====================
export const reportApi = {
  getList: (params) => api.get('/report/list', { params }),
  getDetail: (taskId) => api.get(`/report/${taskId}`),
  getHtml: (taskId) => `/api/report/${taskId}/html`,
  getSteps: (taskId, params) => api.get(`/report/${taskId}/steps`, { params }),
  getFailureAnalysis: (taskId) => api.get(`/report/${taskId}/failure-analysis`),
  getStatisticsOverview: () => api.get('/report/statistics/overview'),
  getCaseDistribution: () => api.get('/report/statistics/distribution'),
  getStatisticsTrend: (params) => api.get('/report/statistics/trend', { params }),
  exportDefect: (taskId, params) => api.post(`/report/${taskId}/export-defect`, null, { params }),
  replay: (taskId, caseId) => api.post(`/report/${taskId}/replay`, null, { params: { case_id: caseId } }),
}

// ==================== 设备管理 API / Device Management API ====================
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

// ==================== 任务调度 API / Task Scheduler API ====================
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

// ==================== 系统设置 API / System Settings API ====================
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

// ==================== AI 辅助 API / AI Assistant API ====================
export const aiApi = {
  generateCase: (data) => api.post('/ai/generate-case', data),
  repairElement: (data) => api.post('/ai/repair-element', data),
  analyzeFailure: (data) => api.post('/ai/analyze-failure', data),
  getFailureStatistics: (params) => api.get('/ai/failure-statistics', { params }),
  getConfig: () => api.get('/ai/config'),
  updateConfig: (data) => api.put('/ai/config', data),
}

// ==================== 页面录制 API / Page Recording API ====================
export const recordApi = {
  // 任务相关 / Task related
  getTaskList: (params) => api.get('/record/tasks/list', { params }),
  getTaskDetail: (id) => api.get(`/record/tasks/${id}`),
  createTask: (data) => api.post('/record/tasks/create', data),
  updateTask: (id, data) => api.put(`/record/tasks/${id}`, data),
  deleteTask: (id) => api.delete(`/record/tasks/${id}`),
  startRecording: (id) => api.post(`/record/tasks/${id}/start`),
  stopRecording: (id) => api.post(`/record/tasks/${id}/stop`),
  getRecordingStatus: (id) => api.get(`/record/tasks/${id}/status`),

  // 步骤相关 / Step related
  getSteps: (taskId) => api.get(`/record/tasks/${taskId}/steps`),
  createStep: (data) => api.post('/record/steps/create', data),
  updateStep: (id, data) => api.put(`/record/steps/${id}`, data),
  deleteStep: (id) => api.delete(`/record/steps/${id}`),
  moveStep: (id, direction) => api.post(`/record/steps/${id}/move`, { direction }),
  batchCreateSteps: (taskId, data) => api.post(`/record/steps/batch-create?task_id=${taskId}`, data),

  // 转换相关 / Conversion related
  convertToCase: (taskId, data) => api.post(`/record/tasks/${taskId}/convert`, data),
}

export default api

// ==================== 调试运行 API / Debug Run API ====================
export const debugApi = {
  // 启动调试运行 / Start debug run
  startDebug: (data) => api.post('/debug/run', data),
  // 获取调试状态 / Get debug status
  getDebugStatus: (taskId) => api.get(`/debug/status/${taskId}`),
  // 停止调试 / Stop debug
  stopDebug: (taskId) => api.post(`/debug/stop/${taskId}`),
  // 提交人工验证码 / Submit manual captcha
  submitCaptcha: (taskId, captchaText) => api.post(`/debug/captcha/${taskId}`, { captcha_text: captchaText }),
}

