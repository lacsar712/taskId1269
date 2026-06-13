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
  getOptimizations: (params?: any) => request.get('/production/optimizations', { params }),
  getWaterQualityWarnings: (params?: any) => request.get('/production/water-quality-warnings', { params }),
  confirmWaterQualityWarning: (id: number, data: any) => request.put(`/production/water-quality-warnings/${id}/confirm`, data),
  handleWaterQualityWarning: (id: number, data: any) => request.put(`/production/water-quality-warnings/${id}/handle`, data),
  getWaterQualityWarningSnapshot: (id: number) => request.get(`/production/water-quality-warnings/${id}/snapshot`),
  getWaterQualityTrend: (params?: any) => request.get('/production/water-quality-trend', { params }),
  getSludgeTransportOrders: (params?: any) => request.get('/production/sludge-transport/orders', { params }),
  getSludgeTransportStats: () => request.get('/production/sludge-transport/stats'),
  createSludgeTransportOrder: (data: any) => request.post('/production/sludge-transport/orders', data),
  updateSludgeTransportOrder: (id: number, data: any) => request.put(`/production/sludge-transport/orders/${id}`, data),
  dispatchSludgeTransport: (id: number, data: any) => request.post(`/production/sludge-transport/orders/${id}/dispatch`, data),
  updateSludgeTransportStatus: (id: number, data: any) => request.put(`/production/sludge-transport/orders/${id}/status`, data),
  getVehicles: () => request.get('/production/sludge-transport/vehicles'),
  getDrivers: () => request.get('/production/sludge-transport/drivers'),
  getDestinations: () => request.get('/production/sludge-transport/destinations'),
  getDosingRecords: (params?: any) => request.get('/production/dosing-records', { params }),
  createDosingRecord: (data: any) => request.post('/production/dosing-records', data),
  updateDosingRecord: (id: number, data: any) => request.put(`/production/dosing-records/${id}`, data),
  deleteDosingRecord: (id: number) => request.delete(`/production/dosing-records/${id}`),
  getDosingStats: (params?: any) => request.get('/production/dosing-stats', { params }),
  getShiftHandovers: (params?: any) => request.get('/production/shift-handovers', { params }),
  getShiftHandover: (id: number) => request.get(`/production/shift-handovers/${id}`),
  createShiftHandover: (data: any) => request.post('/production/shift-handovers', data),
  updateShiftHandover: (id: number, data: any) => request.put(`/production/shift-handovers/${id}`, data),
  deleteShiftHandover: (id: number) => request.delete(`/production/shift-handovers/${id}`),
  confirmShiftHandover: (id: number, data: any) => request.post(`/production/shift-handovers/${id}/confirm`, data),
  getHandoverFollowUps: (id: number) => request.get(`/production/shift-handovers/${id}/follow-ups`),
  createHandoverFollowUp: (id: number, data: any) => request.post(`/production/shift-handovers/${id}/follow-ups`, data),
  updateHandoverFollowUp: (id: number, data: any) => request.put(`/production/shift-handovers/follow-ups/${id}`, data),
  deleteHandoverFollowUp: (id: number) => request.delete(`/production/shift-handovers/follow-ups/${id}`),
  getFactoryMapData: () => request.get('/production/factory-map'),
  getEffluentQualityDisplay: () => request.get('/production/effluent-quality/display'),
  getEffluentQualityTrend: (params?: any) => request.get('/production/effluent-quality/trend', { params }),
  getNoiseOdorMonitorData: () => request.get('/production/noise-odor/monitor'),
  getNoiseOdorOverRecords: (params?: any) => request.get('/production/noise-odor/over-records', { params }),
  getNoiseOdorLimits: () => request.get('/production/noise-odor/limits'),
  createNoiseOdorLimit: (data: any) => request.post('/production/noise-odor/limits', data),
  updateNoiseOdorLimit: (id: number, data: any) => request.put(`/production/noise-odor/limits/${id}`, data),
  deleteNoiseOdorLimit: (id: number) => request.delete(`/production/noise-odor/limits/${id}`)
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
  approvePermit: (id: number, approved: boolean) => request.put(`/safety/permits/${id}/approve`, null, { params: { approved } }),
  getVisitors: (params?: any) => request.get('/safety/visitors', { params }),
  createVisitor: (data: any) => request.post('/safety/visitors', data),
  updateVisitor: (id: number, data: any) => request.put(`/safety/visitors/${id}`, data),
  deleteVisitor: (id: number) => request.delete(`/safety/visitors/${id}`),
  checkinVisitor: (id: number, data: any) => request.post(`/safety/visitors/${id}/checkin`, data),
  checkoutVisitor: (id: number, data: any) => request.post(`/safety/visitors/${id}/checkout`, data),
  getVisitorStats: (params?: any) => request.get('/safety/visitors/stats', { params })
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
  getSpareParts: (params?: any) => request.get('/equipment/spareparts', { params }),
  getMaintenanceContracts: (params?: any) => request.get('/equipment/maintenance-contracts', { params }),
  getMaintenanceContractById: (id: number) => request.get(`/equipment/maintenance-contracts/${id}`),
  createMaintenanceContract: (data: any) => request.post('/equipment/maintenance-contracts', data),
  updateMaintenanceContract: (id: number, data: any) => request.put(`/equipment/maintenance-contracts/${id}`, data),
  deleteMaintenanceContract: (id: number) => request.delete(`/equipment/maintenance-contracts/${id}`),
  renewMaintenanceContract: (id: number, data: any) => request.post(`/equipment/maintenance-contracts/${id}/renew`, data),
  terminateMaintenanceContract: (id: number, data: any) => request.put(`/equipment/maintenance-contracts/${id}/terminate`, data),
  getContractRenewHistory: (id: number) => request.get(`/equipment/maintenance-contracts/${id}/renew-history`),
  getContractEquipmentExec: (id: number, params?: any) => request.get(`/equipment/maintenance-contracts/${id}/equipment-exec`, { params }),
  getContractStats: () => request.get('/equipment/maintenance-contracts/stats'),
  exportMaintenanceContracts: (params?: any) => request.get('/equipment/maintenance-contracts/export', { params, responseType: 'blob' })
}

// 化验管理接口
export const laboratoryApi = {
  getSamples: (params?: any) => request.get('/laboratory/samples', { params }),
  createSample: (data: any) => request.post('/laboratory/samples', data),
  getTasks: (params?: any) => request.get('/laboratory/tasks', { params }),
  getData: (params?: any) => request.get('/laboratory/data', { params }),
  getReports: (params?: any) => request.get('/laboratory/reports', { params }),
  getQC: (params?: any) => request.get('/laboratory/qc', { params }),
  getStandards: (params?: any) => request.get('/laboratory/standards', { params }),
  getReagents: (params?: any) => request.get('/laboratory/reagents', { params }),
  getReagentStats: () => request.get('/laboratory/reagents/stats'),
  getReagentById: (id: number) => request.get(`/laboratory/reagents/${id}`),
  createReagent: (data: any) => request.post('/laboratory/reagents', data),
  updateReagent: (id: number, data: any) => request.put(`/laboratory/reagents/${id}`, data),
  deleteReagent: (id: number) => request.delete(`/laboratory/reagents/${id}`),
  getReagentCategories: () => request.get('/laboratory/reagents/categories/list'),
  getReplenishments: (params?: any) => request.get('/laboratory/reagent-replenishments', { params }),
  getReplenishmentById: (id: number) => request.get(`/laboratory/reagent-replenishments/${id}`),
  createReplenishment: (data: any) => request.post('/laboratory/reagent-replenishments', data),
  approveReplenishment: (id: number, data: any) => request.put(`/laboratory/reagent-replenishments/${id}/approve`, data),
  updatePurchaseStatus: (id: number, data: any) => request.put(`/laboratory/reagent-replenishments/${id}/purchase`, data)
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
