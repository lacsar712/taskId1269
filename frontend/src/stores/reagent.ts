import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { laboratoryApi } from '@/api'

const INITIAL_REAGENTS = [
  { id: 1, reagent_no: 'RGT20240101001', name: '浓硫酸', specification: '500ml/瓶', manufacturer: '国药集团', current_stock: 2, min_safe_stock: 5, storage_location: '酸柜A1', expiry_date: '2025-06-30', unit: '瓶', category: '酸类', purity: '分析纯', cas_no: '7664-93-9', status: 'active', created_at: '2024-01-15 10:30:00' },
  { id: 2, reagent_no: 'RGT20240101002', name: '氢氧化钠', specification: '500g/瓶', manufacturer: '西陇化工', current_stock: 3, min_safe_stock: 10, storage_location: '碱柜B2', expiry_date: '2025-12-31', unit: '瓶', category: '碱类', purity: '分析纯', cas_no: '1310-73-2', status: 'active', created_at: '2024-01-15 10:31:00' },
  { id: 3, reagent_no: 'RGT20240101003', name: '重铬酸钾', specification: '500g/瓶', manufacturer: '国药集团', current_stock: 1, min_safe_stock: 3, storage_location: '盐柜C1', expiry_date: '2025-03-15', unit: '瓶', category: '盐类', purity: '基准试剂', cas_no: '7778-50-9', status: 'active', created_at: '2024-01-15 10:32:00' },
  { id: 4, reagent_no: 'RGT20240101004', name: '硫酸银', specification: '25g/瓶', manufacturer: '阿拉丁', current_stock: 0, min_safe_stock: 2, storage_location: '冷藏柜D1', expiry_date: '2024-08-20', unit: '瓶', category: '盐类', purity: '分析纯', cas_no: '10294-26-5', status: 'active', created_at: '2024-01-15 10:33:00' },
  { id: 5, reagent_no: 'RGT20240101005', name: '酚酞指示剂', specification: '100ml/瓶', manufacturer: '国药集团', current_stock: 8, min_safe_stock: 5, storage_location: '指示剂架', expiry_date: '2026-01-01', unit: '瓶', category: '指示剂', purity: '指示剂', cas_no: '77-09-8', status: 'active', created_at: '2024-01-15 10:34:00' },
  { id: 6, reagent_no: 'RGT20240101006', name: '甲醇', specification: '500ml/瓶', manufacturer: '西陇化工', current_stock: 12, min_safe_stock: 6, storage_location: '有机柜E1', expiry_date: '2025-09-10', unit: '瓶', category: '有机试剂', purity: '色谱纯', cas_no: '67-56-1', status: 'active', created_at: '2024-01-15 10:35:00' },
  { id: 7, reagent_no: 'RGT20240101007', name: '盐酸', specification: '500ml/瓶', manufacturer: '国药集团', current_stock: 6, min_safe_stock: 4, storage_location: '酸柜A2', expiry_date: '2025-07-20', unit: '瓶', category: '酸类', purity: '分析纯', cas_no: '7647-01-0', status: 'active', created_at: '2024-01-15 10:36:00' },
  { id: 8, reagent_no: 'RGT20240101008', name: '硝酸', specification: '500ml/瓶', manufacturer: '西陇化工', current_stock: 4, min_safe_stock: 3, storage_location: '酸柜A3', expiry_date: '2025-05-15', unit: '瓶', category: '酸类', purity: '优级纯', cas_no: '7697-37-2', status: 'active', created_at: '2024-01-15 10:37:00' }
]

const INITIAL_REPLENISHMENTS = [
  { id: 1, application_no: 'RPL20240115001', reagent_id: 1, reagent_name: '浓硫酸', specification: '500ml/瓶', apply_quantity: 10, unit: '瓶', urgency: 'urgent', purpose: 'COD检测日常消耗，库存不足', applicant_name: '李化验员', apply_time: '2024-01-15 09:30:00', status: 'pending', approver_name: null as string | null, approve_time: null as string | null, approve_remark: null as string | null, purchase_quantity: null as number | null, purchase_status: 'not_started', purchaser: null as string | null, expected_date: null as string | null, purchase_remark: null as string | null },
  { id: 2, application_no: 'RPL20240115002', reagent_id: 4, reagent_name: '硫酸银', specification: '25g/瓶', apply_quantity: 5, unit: '瓶', urgency: 'urgent', purpose: 'COD检测急需，已断货', applicant_name: '张化验员', apply_time: '2024-01-15 10:15:00', status: 'approved', approver_name: '王主任', approve_time: '2024-01-15 11:00:00', approve_remark: '同意采购，尽快安排', purchase_quantity: 5, purchase_status: 'in_progress', purchaser: '刘采购', expected_date: '2024-01-20', purchase_remark: '已向国药集团下单' },
  { id: 3, application_no: 'RPL20240114003', reagent_id: 2, reagent_name: '氢氧化钠', specification: '500g/瓶', apply_quantity: 20, unit: '瓶', urgency: 'normal', purpose: '月度常规补货', applicant_name: '李化验员', apply_time: '2024-01-14 14:20:00', status: 'purchasing', approver_name: '王主任', approve_time: '2024-01-14 16:00:00', approve_remark: '同意，本月采购计划内', purchase_quantity: 20, purchase_status: 'delivered', purchaser: '刘采购', expected_date: '2024-01-18', purchase_remark: '货物已到，待验收入库' },
  { id: 4, application_no: 'RPL20240110004', reagent_id: 5, reagent_name: '酚酞指示剂', specification: '100ml/瓶', apply_quantity: 10, unit: '瓶', urgency: 'low', purpose: '备用库存补充', applicant_name: '赵化验员', apply_time: '2024-01-10 08:45:00', status: 'completed', approver_name: '王主任', approve_time: '2024-01-10 10:30:00', approve_remark: '同意', purchase_quantity: 10, purchase_status: 'completed', purchaser: '刘采购', expected_date: '2024-01-15', purchase_remark: '已验收入库' },
  { id: 5, application_no: 'RPL20240108005', reagent_id: 3, reagent_name: '重铬酸钾', specification: '500g/瓶', apply_quantity: 3, unit: '瓶', urgency: 'normal', purpose: '基准试剂补充', applicant_name: '张化验员', apply_time: '2024-01-08 15:30:00', status: 'completed', approver_name: '王主任', approve_time: '2024-01-08 17:00:00', approve_remark: '同意采购', purchase_quantity: 3, purchase_status: 'completed', purchaser: '刘采购', expected_date: '2024-01-12', purchase_remark: '已到货并验收' },
  { id: 6, application_no: 'RPL20240105006', reagent_id: 6, reagent_name: '甲醇', specification: '500ml/瓶', apply_quantity: 10, unit: '瓶', urgency: 'normal', purpose: '色谱分析用', applicant_name: '李化验员', apply_time: '2024-01-05 09:00:00', status: 'rejected', approver_name: '王主任', approve_time: '2024-01-05 11:00:00', approve_remark: '库存还充足，下月再采购', purchase_quantity: null, purchase_status: 'not_started', purchaser: null, expected_date: null, purchase_remark: null }
]

let nextReagentId = 100
let nextReplenishmentId = 100

export const useReagentStore = defineStore('reagent', () => {
  const reagents = ref<any[]>([...INITIAL_REAGENTS])
  const replenishments = ref<any[]>([...INITIAL_REPLENISHMENTS])
  const categories = ref<{ name: string; count: number }[]>([])

  const lowStockReagents = computed(() =>
    reagents.value.filter(r => r.status === 'active' && r.current_stock <= r.min_safe_stock)
  )

  const activeReagents = computed(() =>
    reagents.value.filter(r => r.status === 'active')
  )

  const stats = computed(() => {
    const active = activeReagents.value
    const thirtyDaysLater = new Date()
    thirtyDaysLater.setDate(thirtyDaysLater.getDate() + 30)
    return {
      total: active.length,
      low_stock: lowStockReagents.value.length,
      near_expiry: active.filter(r => {
        if (!r.expiry_date) return false
        return new Date(r.expiry_date) <= thirtyDaysLater
      }).length,
      categories: new Set(active.map(r => r.category).filter(Boolean)).size
    }
  })

  const replenishmentStats = computed(() => {
    const list = replenishments.value
    return {
      pending: list.filter(r => r.status === 'pending').length,
      approved: list.filter(r => r.status === 'approved').length,
      purchasing: list.filter(r => r.status === 'purchasing').length,
      completed: list.filter(r => r.status === 'completed').length
    }
  })

  const fetchReagents = async () => {
    try {
      const res: any = await laboratoryApi.getReagents({ page_size: 100 })
      if (res.items && res.items.length > 0) {
        reagents.value = res.items
      }
    } catch (_e) {
      // keep local data
    }
  }

  const fetchReplenishments = async () => {
    try {
      const res: any = await laboratoryApi.getReplenishments({ page_size: 100 })
      if (res.items && res.items.length > 0) {
        replenishments.value = res.items
      }
    } catch (_e) {
      // keep local data
    }
  }

  const fetchCategories = async () => {
    try {
      const res: any = await laboratoryApi.getReagentCategories()
      if (res && res.length > 0) {
        categories.value = res
      }
    } catch (_e) {
      const catMap = new Map<string, number>()
      activeReagents.value.forEach(r => {
        if (r.category) {
          catMap.set(r.category, (catMap.get(r.category) || 0) + 1)
        }
      })
      categories.value = Array.from(catMap.entries()).map(([name, count]) => ({ name, count }))
    }
  }

  const addReagent = (data: any) => {
    const id = ++nextReagentId
    const reagent = {
      id,
      reagent_no: `RGT${Date.now()}`,
      ...data,
      status: 'active',
      created_at: new Date().toLocaleString()
    }
    reagents.value.unshift(reagent)
    return reagent
  }

  const updateReagent = (id: number, data: any) => {
    const idx = reagents.value.findIndex(r => r.id === id)
    if (idx > -1) {
      Object.assign(reagents.value[idx], data)
    }
  }

  const deactivateReagent = (id: number) => {
    const idx = reagents.value.findIndex(r => r.id === id)
    if (idx > -1) {
      reagents.value[idx].status = 'inactive'
    }
  }

  const addReplenishment = (data: { reagent_id: number; apply_quantity: number; urgency: string; purpose?: string }) => {
    const reagent = reagents.value.find(r => r.id === data.reagent_id)
    if (!reagent) return null

    const id = ++nextReplenishmentId
    const item = {
      id,
      application_no: `RPL${Date.now()}`,
      reagent_id: data.reagent_id,
      reagent_name: reagent.name,
      specification: reagent.specification,
      apply_quantity: data.apply_quantity,
      unit: reagent.unit,
      urgency: data.urgency,
      purpose: data.purpose || '',
      applicant_name: '当前用户',
      apply_time: new Date().toLocaleString(),
      status: 'pending',
      approver_name: null as string | null,
      approve_time: null as string | null,
      approve_remark: null as string | null,
      purchase_quantity: null as number | null,
      purchase_status: 'not_started' as string,
      purchaser: null as string | null,
      expected_date: null as string | null,
      purchase_remark: null as string | null
    }
    replenishments.value.unshift(item)
    return item
  }

  const approveReplenishment = (id: number, data: { status: string; approve_remark?: string; purchase_quantity?: number }) => {
    const idx = replenishments.value.findIndex(r => r.id === id)
    if (idx === -1) return null
    const item = replenishments.value[idx]
    if (item.status !== 'pending') return null

    item.status = data.status
    item.approver_name = '当前用户'
    item.approve_time = new Date().toLocaleString()
    item.approve_remark = data.approve_remark || ''

    if (data.status === 'approved') {
      item.purchase_quantity = data.purchase_quantity || item.apply_quantity
      item.purchase_status = 'not_started'
    }

    return item
  }

  const updatePurchaseStatus = (id: number, data: { purchase_status: string; purchaser?: string; expected_date?: string; purchase_remark?: string }) => {
    const idx = replenishments.value.findIndex(r => r.id === id)
    if (idx === -1) return null
    const item = replenishments.value[idx]

    if (item.status !== 'approved' && item.status !== 'purchasing') return null

    item.purchase_status = data.purchase_status
    if (data.purchaser) item.purchaser = data.purchaser
    if (data.expected_date) item.expected_date = data.expected_date
    if (data.purchase_remark) item.purchase_remark = data.purchase_remark

    if (data.purchase_status === 'completed') {
      item.status = 'completed'
      const qty = item.purchase_quantity || item.apply_quantity
      const reagentIdx = reagents.value.findIndex(r => r.id === item.reagent_id)
      if (reagentIdx > -1) {
        reagents.value[reagentIdx].current_stock += qty
      }
    } else if (['in_progress', 'delivered'].includes(data.purchase_status)) {
      item.status = 'purchasing'
    }

    return item
  }

  return {
    reagents,
    replenishments,
    categories,
    lowStockReagents,
    activeReagents,
    stats,
    replenishmentStats,
    fetchReagents,
    fetchReplenishments,
    fetchCategories,
    addReagent,
    updateReagent,
    deactivateReagent,
    addReplenishment,
    approveReplenishment,
    updatePurchaseStatus
  }
})
