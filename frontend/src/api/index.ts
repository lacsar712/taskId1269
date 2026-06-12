import request from './request'

// 认证接口
export const authApi = {
  login: (data: { username: string; password: string }) => 
    request.post('/auth/login', data),
  logout: () => request.post('/auth/logout'),
  getCurrentUser: () => request.get('/auth/me')
}

// 仪表盘接口
export const dashboardApi = {
  getOverview: () => request.get('/dashboard/overview'),
  getTrends: () => request.get('/dashboard/trends')
}

// 用户管理接口
export const userApi = {
  getList: (params?: any) => request.get('/users', { params }),
  getById: (id: number) => request.get(`/users/${id}`),
  create: (data: any) => request.post('/users', data),
  update: (id: number, data: any) => request.put(`/users/${id}`, data),
  delete: (id: number) => request.delete(`/users/${id}`),
  getRoles: () => request.get('/users/roles/list')
}

// 生产管理接口
export const productionApi = {
  getParameters: (params?: any) => request.get('/production/parameters', { params }),
  getPlans: (params?: any) => request.get('/production/plans', { params }),
  createPlan: (data: any) => request.post('/production/plans', data),
  getLogs: (params?: any) => request.get('/production/logs', { params }),
  createLog: (data: any) => request.post('/production/logs', data),
  getAlarms: (params?: any) => request.get('/production/alarms', { params }),
  handleAlarm: (id: number, data: any) => request.put(`/production/alarms/${id}/handle`, data),
  getOptimizations: (params?: any) => request.get('/production/optimizations', { params })
}

// 安全管理接口
export const safetyApi = {
  getInspectionPlans: (params?: any) => request.get('/safety/inspections/plans', { params }),
  createInspectionPlan: (data: any) => request.post('/safety/inspections/plans', data),
  getInspectionRecords: (params?: any) => request.get('/safety/inspections/records', { params }),
  createInspectionRecord: (data: any) => request.post('/safety/inspections/records', data),
  getRisks: (params?: any) => request.get('/safety/risks', { params }),
  createRisk: (data: any) => request.post('/safety/risks', data),
  getEmergencyPlans: (params?: any) => request.get('/safety/emergency/plans', { params }),
  getTrainings: (params?: any) => request.get('/safety/trainings', { params }),
  getPermits: (params?: any) => request.get('/safety/permits', { params }),
  createPermit: (data: any) => request.post('/safety/permits', data),
  approvePermit: (id: number, approved: boolean) => request.put(`/safety/permits/${id}/approve`, null, { params: { approved } })
}

// 设备管理接口
export const equipmentApi = {
  getCategories: () => request.get('/equipment/categories'),
  getList: (params?: any) => request.get('/equipment', { params }),
  getById: (id: number) => request.get(`/equipment/${id}`),
  create: (data: any) => request.post('/equipment', data),
  getMaintenancePlans: (params?: any) => request.get('/equipment/maintenance/plans', { params }),
  getMaintenanceRecords: (params?: any) => request.get('/equipment/maintenance/records', { params }),
  getFaults: (params?: any) => request.get('/equipment/faults', { params }),
  createFault: (data: any) => request.post('/equipment/faults', data),
  getSpareParts: (params?: any) => request.get('/equipment/spareparts', { params })
}

// 化验管理接口
export const laboratoryApi = {
  getSamples: (params?: any) => request.get('/laboratory/samples', { params }),
  createSample: (data: any) => request.post('/laboratory/samples', data),
  getTasks: (params?: any) => request.get('/laboratory/tasks', { params }),
  getData: (params?: any) => request.get('/laboratory/data', { params }),
  getReports: (params?: any) => request.get('/laboratory/reports', { params }),
  getQC: (params?: any) => request.get('/laboratory/qc', { params }),
  getStandards: (params?: any) => request.get('/laboratory/standards', { params })
}

// 报表管理接口
export const reportApi = {
  getTemplates: (params?: any) => request.get('/reports/templates', { params }),
  getCustomReports: (params?: any) => request.get('/reports/custom', { params }),
  createCustomReport: (data: any) => request.post('/reports/custom', data),
  getDailyStats: (params?: any) => request.get('/reports/statistics/daily', { params }),
  getMonthlyStats: (params?: any) => request.get('/reports/statistics/monthly', { params })
}

// 能耗管理接口
export const energyApi = {
  getRealtime: (params?: any) => request.get('/energy/realtime', { params }),
  getHistory: (params?: any) => request.get('/energy/history', { params }),
  getSectionAnalysis: (params?: any) => request.get('/energy/analysis/section', { params }),
  getEquipmentAnalysis: (params?: any) => request.get('/energy/analysis/equipment', { params }),
  getSavingPlans: (params?: any) => request.get('/energy/saving/plans', { params }),
  getSuggestions: () => request.get('/energy/saving/suggestions'),
  getCosts: (params?: any) => request.get('/energy/costs', { params }),
  getCostSummary: (params?: any) => request.get('/energy/costs/summary', { params })
}

// 资料管理接口
export const documentApi = {
  getCategories: () => request.get('/documents/categories'),
  createCategory: (data: any) => request.post('/documents/categories', null, { params: data }),
  getList: (params?: any) => request.get('/documents', { params }),
  create: (data: any) => request.post('/documents', data),
  getById: (id: number) => request.get(`/documents/${id}`),
  toggleFavorite: (id: number) => request.put(`/documents/${id}/favorite`),
  archive: (id: number) => request.put(`/documents/${id}/archive`),
  delete: (id: number) => request.delete(`/documents/${id}`),
  getHot: (params?: any) => request.get('/documents/hot/list', { params }),
  getFavorites: () => request.get('/documents/favorites/list')
}

// 物资管理接口
export const materialApi = {
  getCategories: () => request.get('/materials/categories'),
  getList: (params?: any) => request.get('/materials', { params }),
  create: (data: any) => request.post('/materials', data),
  getInbound: (params?: any) => request.get('/materials/inbound', { params }),
  createInbound: (data: any) => request.post('/materials/inbound', data),
  getOutbound: (params?: any) => request.get('/materials/outbound', { params }),
  createOutbound: (data: any) => request.post('/materials/outbound', data),
  getSuppliers: (params?: any) => request.get('/materials/suppliers', { params })
}

// 绩效管理接口
export const performanceApi = {
  getIndicators: (params?: any) => request.get('/performance/indicators', { params }),
  createIndicator: (data: any) => request.post('/performance/indicators', data),
  getData: (params?: any) => request.get('/performance/data', { params }),
  getResults: (params?: any) => request.get('/performance/results', { params }),
  getPersonalStats: (params?: any) => request.get('/performance/statistics/personal', { params }),
  getTeamStats: (params?: any) => request.get('/performance/statistics/team', { params })
}

// 系统管理接口
export const systemApi = {
  getConfigs: (params?: any) => request.get('/system/configs', { params }),
  updateConfig: (key: string, data: any) => request.put(`/system/configs/${key}`, data),
  getLogs: (params?: any) => request.get('/system/logs', { params }),
  getInterfaces: (params?: any) => request.get('/system/interfaces', { params }),
  createInterface: (data: any) => request.post('/system/interfaces', data),
  toggleInterfaceStatus: (id: number) => request.put(`/system/interfaces/${id}/status`),
  createBackup: () => request.post('/system/backup'),
  getBackupList: () => request.get('/system/backup/list')
}
