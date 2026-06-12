<template>
  <div class="page-container">
    <div class="page-header">
      <h2>维保合同管理</h2>
      <p>集中维护厂内设备对外维保合同的完整档案</p>
    </div>

    <div class="stat-cards">
      <a-row :gutter="16">
        <a-col :span="6">
          <a-card class="stat-card" :bordered="false">
            <a-statistic title="合同总数" :value="stats.total" :value-style="{ color: '#165DFF' }" />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card" :bordered="false">
            <a-statistic title="生效中" :value="stats.active" :value-style="{ color: '#00B42A' }" />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card warn" :bordered="false">
            <a-statistic title="30天内到期" :value="stats.warning" :value-style="{ color: '#FF7D00' }" />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card danger" :bordered="false">
            <a-statistic title="已过期" :value="stats.expired" :value-style="{ color: '#F53F3F' }" />
          </a-card>
        </a-col>
      </a-row>
    </div>

    <div class="table-operations">
      <a-space>
        <a-input-search v-model="keyword" placeholder="搜索合同编号/供应商" style="width: 240px;" @search="fetchData" />
        <a-select v-model="status" placeholder="合同状态" style="width: 140px;" allow-clear @change="fetchData">
          <a-option value="active">生效中</a-option>
          <a-option value="warning">即将到期</a-option>
          <a-option value="expired">已过期</a-option>
          <a-option value="pending">待生效</a-option>
        </a-select>
        <a-range-picker v-model="dateRange" style="width: 280px;" @change="fetchData" />
      </a-space>
      <a-space>
        <a-button @click="handleExport">
          <template #icon><icon-download /></template>
          导出
        </a-button>
        <a-button type="primary" @click="handleOpenAddModal">
          <template #icon><icon-plus /></template>
          新增合同
        </a-button>
      </a-space>
    </div>

    <a-table
      :columns="columns"
      :data="contracts"
      :loading="loading"
      :pagination="pagination"
      :row-class-name="getRowClassName"
      :scroll="{ x: 1400 }"
    >
      <template #contract_no="{ record }">
        <a-button type="text" @click="viewDetail(record)">{{ record.contract_no }}</a-button>
      </template>
      <template #amount="{ record }">
        <span class="amount">¥{{ formatNumber(record.amount) }}</span>
      </template>
      <template #equipment_count="{ record }">
        <a-tag color="arcoblue">{{ record.equipment_count }} 台</a-tag>
      </template>
      <template #date_range="{ record }">
        <div>
          <div>{{ record.start_date }}</div>
          <div class="sub-text">至 {{ record.end_date }}</div>
        </div>
      </template>
      <template #status="{ record }">
        <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status, record.end_date) }}</a-tag>
      </template>
      <template #progress="{ record }">
        <div class="progress-wrap">
          <a-progress :percent="record.progress || 0" :status="record.progress >= 90 ? 'warning' : 'normal'" :show-text="true" size="small" />
        </div>
      </template>
      <template #operations="{ record }">
        <a-space>
          <a-button type="text" size="small" @click="viewDetail(record)">详情</a-button>
          <a-button type="text" size="small" @click="editContract(record)">编辑</a-button>
          <a-button type="text" size="small" @click="handleRenew(record)">续签</a-button>
          <a-dropdown @select="(val: string) => handleMoreAction(val, record)">
            <a-button type="text" size="small">
              更多
              <template #icon><icon-down /></template>
            </a-button>
            <template #content>
              <a-doption value="terminate">终止合同</a-doption>
              <a-doption value="delete">删除</a-doption>
            </template>
          </a-dropdown>
        </a-space>
      </template>
    </a-table>

    <a-modal
      v-model:visible="showAddModal"
      :title="editingContract ? '编辑维保合同' : '新增维保合同'"
      @ok="handleSave"
      :ok-loading="submitLoading"
      width="780px"
    >
      <a-form :model="form" layout="vertical" ref="formRef">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="合同编号" field="contract_no" required>
              <a-input v-model="form.contract_no" placeholder="如：WB202401001" :disabled="!!editingContract" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="合同名称" field="contract_name" required>
              <a-input v-model="form.contract_name" placeholder="请输入合同名称" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="签约供应商" field="supplier_id" required>
              <a-select v-model="form.supplier_id" placeholder="请选择供应商" allow-clear show-search>
                <a-option v-for="s in supplierList" :key="s.id" :value="s.id">{{ s.name }}</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="合同金额(元)" field="amount" required>
              <a-input-number v-model="form.amount" :min="0" style="width: 100%" placeholder="请输入合同金额" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="合同起始日期" field="start_date" required>
              <a-date-picker v-model="form.start_date" style="width: 100%" placeholder="选择起始日期" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="合同终止日期" field="end_date" required>
              <a-date-picker v-model="form.end_date" style="width: 100%" placeholder="选择终止日期" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="服务频次" field="service_frequency" required>
              <a-select v-model="form.service_frequency" placeholder="请选择服务频次">
                <a-option value="weekly">每周</a-option>
                <a-option value="biweekly">每两周</a-option>
                <a-option value="monthly">每月</a-option>
                <a-option value="bimonthly">每两月</a-option>
                <a-option value="quarterly">每季度</a-option>
                <a-option value="semiyearly">每半年</a-option>
                <a-option value="yearly">每年</a-option>
                <a-option value="ondemand">按需</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="响应时限(小时)" field="response_time" required>
              <a-input-number v-model="form.response_time" :min="0" style="width: 100%" placeholder="紧急响应时限" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="关联设备" field="equipment_ids">
          <a-transfer
            v-model:target-keys="form.equipment_ids"
            :data-source="equipmentList"
            :titles="['可选设备', '已选设备']"
            show-search
            :list-style="{ width: '330px', height: '200px' }"
          >
            <template #item="{ record }">
              {{ record.name }} ({{ record.code }})
            </template>
          </a-transfer>
        </a-form-item>
        <a-form-item label="服务范围描述" field="service_scope">
          <a-textarea v-model="form.service_scope" :max-length="1000" show-word-limit placeholder="请详细描述维保服务范围、内容、标准等" />
        </a-form-item>
        <a-form-item label="条款摘要" field="terms_summary">
          <a-textarea v-model="form.terms_summary" :max-length="500" show-word-limit placeholder="合同关键条款摘要，如付款方式、违约责任、保密条款等" />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:visible="showRenewModal"
      title="合同续签"
      @ok="handleSubmitRenew"
      :ok-loading="renewLoading"
      width="520px"
    >
      <a-form :model="renewForm" layout="vertical">
        <a-form-item label="原合同编号">
          <a-input :model-value="renewForm.original_contract_no" disabled />
        </a-form-item>
        <a-form-item label="新合同编号" field="new_contract_no" required>
          <a-input v-model="renewForm.new_contract_no" placeholder="请输入新合同编号" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="续签起始日期" field="renew_start_date" required>
              <a-date-picker v-model="renewForm.renew_start_date" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="续签终止日期" field="renew_end_date" required>
              <a-date-picker v-model="renewForm.renew_end_date" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="续签金额(元)" field="renew_amount" required>
          <a-input-number v-model="renewForm.renew_amount" :min="0" style="width: 100%" />
        </a-form-item>
        <a-form-item label="备注" field="remark">
          <a-textarea v-model="renewForm.remark" :max-length="300" show-word-limit />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message, Modal } from '@arco-design/web-vue'
import { equipmentApi, materialApi } from '@/api'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const submitLoading = ref(false)
const renewLoading = ref(false)
const showAddModal = ref(false)
const showRenewModal = ref(false)
const keyword = ref('')
const status = ref('')
const dateRange = ref<any[]>([])
const contracts = ref<any[]>([])
const supplierList = ref<any[]>([])
const equipmentList = ref<any[]>([])
const editingContract = ref<any>(null)
const renewContract = ref<any>(null)
const formRef = ref()
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const stats = reactive({
  total: 0,
  active: 0,
  warning: 0,
  expired: 0
})

const form = reactive({
  contract_no: '',
  contract_name: '',
  supplier_id: null as any,
  amount: null as any,
  start_date: '',
  end_date: '',
  service_frequency: '',
  response_time: null as any,
  equipment_ids: [] as any[],
  service_scope: '',
  terms_summary: ''
})

const renewForm = reactive({
  original_contract_no: '',
  new_contract_no: '',
  renew_start_date: '',
  renew_end_date: '',
  renew_amount: null as any,
  remark: ''
})

const columns = [
  { title: '合同编号', dataIndex: 'contract_no', slotName: 'contract_no', width: 140, fixed: 'left' },
  { title: '合同名称', dataIndex: 'contract_name', width: 180, ellipsis: true },
  { title: '签约供应商', dataIndex: 'supplier_name', width: 160 },
  { title: '关联设备', slotName: 'equipment_count', width: 100, align: 'center' },
  { title: '合同金额', slotName: 'amount', width: 130, align: 'right' },
  { title: '起止日期', slotName: 'date_range', width: 200 },
  { title: '服务频次', dataIndex: 'service_frequency_text', width: 100 },
  { title: '响应时限', dataIndex: 'response_time_text', width: 100 },
  { title: '合同状态', slotName: 'status', width: 110, align: 'center' },
  { title: '履约进度', slotName: 'progress', width: 140 },
  { title: '操作', slotName: 'operations', width: 200, fixed: 'right' }
]

const formatNumber = (num: number | string) => {
  if (num === null || num === undefined) return '0'
  return Number(num).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const getStatusColor = (s: string) => {
  const map: Record<string, string> = {
    active: 'green',
    warning: 'orange',
    expired: 'red',
    pending: 'gray'
  }
  return map[s] || 'gray'
}

const getStatusText = (s: string, endDate?: string) => {
  if (s === 'expired') return '已过期'
  if (s === 'pending') return '待生效'
  if (s === 'warning') {
    const days = dayjs(endDate).diff(dayjs(), 'day')
    return `${days}天后到期`
  }
  return '生效中'
}

const getRowClassName = (record: any) => {
  if (record.status === 'expired') return 'row-expired'
  if (record.status === 'warning') return 'row-warning'
  return ''
}

const calcStatus = (startDate: string, endDate: string): string => {
  const now = dayjs()
  const start = dayjs(startDate)
  const end = dayjs(endDate)
  if (now.isAfter(end)) return 'expired'
  if (now.isBefore(start)) return 'pending'
  const daysLeft = end.diff(now, 'day')
  if (daysLeft <= 30) return 'warning'
  return 'active'
}

const calcProgress = (startDate: string, endDate: string): number => {
  const start = dayjs(startDate).valueOf()
  const end = dayjs(endDate).valueOf()
  const now = dayjs().valueOf()
  if (now >= end) return 100
  if (now <= start) return 0
  return Math.round(((now - start) / (end - start)) * 100)
}

const getFrequencyText = (f: string) => {
  const map: Record<string, string> = {
    weekly: '每周', biweekly: '每两周', monthly: '每月', bimonthly: '每两月',
    quarterly: '每季度', semiyearly: '每半年', yearly: '每年', ondemand: '按需'
  }
  return map[f] || f
}

const fetchData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 400))
    const rawData = [
      {
        id: 1, contract_no: 'WB2024001', contract_name: '曝气系统年度维保合同', supplier_id: 1, supplier_name: 'XX环保设备有限公司',
        amount: 128000, start_date: '2024-01-01', end_date: '2026-06-20', service_frequency: 'monthly', response_time: 4,
        equipment_count: 8, progress: 0
      },
      {
        id: 2, contract_no: 'WB2024002', contract_name: '水泵组季度维保合同', supplier_id: 2, supplier_name: 'YY泵业技术服务公司',
        amount: 56000, start_date: '2024-03-01', end_date: '2026-07-15', service_frequency: 'quarterly', response_time: 2,
        equipment_count: 12, progress: 0
      },
      {
        id: 3, contract_no: 'WB2023058', contract_name: '生化池搅拌设备维保合同', supplier_id: 3, supplier_name: 'ZZ机械维保服务中心',
        amount: 98000, start_date: '2023-07-01', end_date: '2025-06-30', service_frequency: 'monthly', response_time: 6,
        equipment_count: 5, progress: 0
      },
      {
        id: 4, contract_no: 'WB2023076', contract_name: '污泥脱水机维保合同', supplier_id: 1, supplier_name: 'XX环保设备有限公司',
        amount: 72000, start_date: '2023-09-10', end_date: '2025-09-09', service_frequency: 'biweekly', response_time: 3,
        equipment_count: 3, progress: 0
      },
      {
        id: 5, contract_no: 'WB2022110', contract_name: '电气控制系统维保合同', supplier_id: 4, supplier_name: 'AA自动化科技公司',
        amount: 156000, start_date: '2023-01-01', end_date: '2025-01-15', service_frequency: 'semiyearly', response_time: 2,
        equipment_count: 20, progress: 0
      },
      {
        id: 6, contract_no: 'WB2024015', contract_name: '加药系统维保合同', supplier_id: 2, supplier_name: 'YY泵业技术服务公司',
        amount: 45000, start_date: '2024-06-01', end_date: '2026-05-31', service_frequency: 'monthly', response_time: 4,
        equipment_count: 6, progress: 0
      },
      {
        id: 7, contract_no: 'WB2023122', contract_name: '阀门组年度维保合同', supplier_id: 5, supplier_name: 'BB阀门技术服务部',
        amount: 38000, start_date: '2023-11-01', end_date: '2025-10-31', service_frequency: 'yearly', response_time: 8,
        equipment_count: 45, progress: 0
      },
      {
        id: 8, contract_no: 'WB2024003', contract_name: '仪表设备校准维保合同', supplier_id: 6, supplier_name: 'CC计量检测研究院',
        amount: 68000, start_date: '2024-02-01', end_date: '2026-01-31', service_frequency: 'quarterly', response_time: 24,
        equipment_count: 60, progress: 0
      }
    ]
    contracts.value = rawData.map(item => ({
      ...item,
      status: calcStatus(item.start_date, item.end_date),
      progress: calcProgress(item.start_date, item.end_date),
      service_frequency_text: getFrequencyText(item.service_frequency),
      response_time_text: `${item.response_time}小时`
    })).filter(item => {
      if (keyword.value) {
        const kw = keyword.value.toLowerCase()
        if (!item.contract_no.toLowerCase().includes(kw) && !item.supplier_name.toLowerCase().includes(kw)) {
          return false
        }
      }
      if (status.value && item.status !== status.value) return false
      if (dateRange.value && dateRange.value.length === 2) {
        const [start, end] = dateRange.value
        if (dayjs(item.end_date).isBefore(dayjs(start)) || dayjs(item.start_date).isAfter(dayjs(end))) {
          return false
        }
      }
      return true
    })
    pagination.total = contracts.value.length

    stats.total = contracts.value.length
    stats.active = contracts.value.filter(c => c.status === 'active').length
    stats.warning = contracts.value.filter(c => c.status === 'warning').length
    stats.expired = contracts.value.filter(c => c.status === 'expired').length
  } finally {
    loading.value = false
  }
}

const fetchSuppliers = async () => {
  try {
    const res: any = await materialApi.getSuppliers()
    supplierList.value = res || []
  } catch (e) {
    supplierList.value = [
      { id: 1, name: 'XX环保设备有限公司' },
      { id: 2, name: 'YY泵业技术服务公司' },
      { id: 3, name: 'ZZ机械维保服务中心' },
      { id: 4, name: 'AA自动化科技公司' },
      { id: 5, name: 'BB阀门技术服务部' },
      { id: 6, name: 'CC计量检测研究院' }
    ]
  }
}

const fetchEquipments = async () => {
  try {
    const res: any = await equipmentApi.getList({ page_size: 500 })
    equipmentList.value = (res.items || []).map((e: any) => ({ key: e.id, title: `${e.name} (${e.code})`, name: e.name, code: e.code }))
  } catch (e) {
    equipmentList.value = [
      { key: 'EQ001', title: '曝气风机#1 (EQ001)', name: '曝气风机#1', code: 'EQ001' },
      { key: 'EQ002', title: '曝气风机#2 (EQ002)', name: '曝气风机#2', code: 'EQ002' },
      { key: 'EQ003', title: '提升泵#1 (EQ003)', name: '提升泵#1', code: 'EQ003' },
      { key: 'EQ004', title: '刮泥机 (EQ004)', name: '刮泥机', code: 'EQ004' },
      { key: 'EQ005', title: '回流泵#1 (EQ005)', name: '回流泵#1', code: 'EQ005' },
      { key: 'EQ006', title: '污泥泵#1 (EQ006)', name: '污泥泵#1', code: 'EQ006' },
      { key: 'EQ007', title: '加药泵#1 (EQ007)', name: '加药泵#1', code: 'EQ007' },
      { key: 'EQ008', title: '搅拌机#1 (EQ008)', name: '搅拌机#1', code: 'EQ008' }
    ]
  }
}

const viewDetail = (record: any) => {
  router.push({ path: '/equipment/contract-detail', query: { id: record.id } })
}

const handleOpenAddModal = () => {
  resetForm()
  showAddModal.value = true
}

const editContract = (record: any) => {
  editingContract.value = record
  Object.assign(form, {
    contract_no: record.contract_no,
    contract_name: record.contract_name,
    supplier_id: record.supplier_id,
    amount: record.amount,
    start_date: record.start_date,
    end_date: record.end_date,
    service_frequency: record.service_frequency,
    response_time: record.response_time,
    equipment_ids: record.equipment_ids || [],
    service_scope: record.service_scope || '',
    terms_summary: record.terms_summary || ''
  })
  showAddModal.value = true
}

const resetForm = () => {
  Object.assign(form, {
    contract_no: '',
    contract_name: '',
    supplier_id: null,
    amount: null,
    start_date: '',
    end_date: '',
    service_frequency: '',
    response_time: null,
    equipment_ids: [],
    service_scope: '',
    terms_summary: ''
  })
  editingContract.value = null
}

const handleSave = async () => {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    if (editingContract.value) {
      const idx = contracts.value.findIndex(c => c.id === editingContract.value.id)
      if (idx > -1) {
        contracts.value[idx] = {
          ...contracts.value[idx],
          ...form,
          status: calcStatus(form.start_date, form.end_date),
          progress: calcProgress(form.start_date, form.end_date),
          service_frequency_text: getFrequencyText(form.service_frequency),
          response_time_text: `${form.response_time}小时`,
          equipment_count: form.equipment_ids?.length || contracts.value[idx].equipment_count
        }
      }
      Message.success('编辑成功')
    } else {
      const supplier = supplierList.value.find(s => s.id === form.supplier_id)
      contracts.value.unshift({
        id: Date.now(),
        ...form,
        supplier_name: supplier?.name || '',
        equipment_count: form.equipment_ids?.length || 0,
        status: calcStatus(form.start_date, form.end_date),
        progress: calcProgress(form.start_date, form.end_date),
        service_frequency_text: getFrequencyText(form.service_frequency),
        response_time_text: `${form.response_time}小时`
      })
      Message.success('新增成功')
    }
    showAddModal.value = false
    resetForm()
    fetchData()
  } catch (e) {
    Message.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleRenew = (record: any) => {
  renewContract.value = record
  Object.assign(renewForm, {
    original_contract_no: record.contract_no,
    new_contract_no: '',
    renew_start_date: dayjs(record.end_date).add(1, 'day').format('YYYY-MM-DD'),
    renew_end_date: dayjs(record.end_date).add(1, 'year').format('YYYY-MM-DD'),
    renew_amount: record.amount,
    remark: ''
  })
  showRenewModal.value = true
}

const handleSubmitRenew = async () => {
  renewLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    Message.success('续签成功')
    showRenewModal.value = false
    fetchData()
  } catch (e) {
    Message.error('续签失败')
  } finally {
    renewLoading.value = false
  }
}

const handleMoreAction = (val: string, record: any) => {
  if (val === 'terminate') {
    Modal.confirm({
      title: '确认终止合同?',
      content: `确定要终止合同【${record.contract_no}】吗？此操作将提前结束合同有效期。`,
      onOk: () => Message.success('合同已终止')
    })
  } else if (val === 'delete') {
    Modal.confirm({
      title: '确认删除?',
      content: `确定要删除合同【${record.contract_no}】吗？删除后不可恢复。`,
      okButtonProps: { status: 'danger' },
      onOk: () => {
        contracts.value = contracts.value.filter(c => c.id !== record.id)
        Message.success('删除成功')
      }
    })
  }
}

const handleExport = () => {
  Message.info('导出功能待对接后端接口')
}

onMounted(() => {
  fetchData()
  fetchSuppliers()
  fetchEquipments()
})
</script>

<style scoped>
.stat-cards { margin-bottom: 20px; }
.stat-card { border-radius: 8px; }
.stat-card.warn { background: linear-gradient(135deg, #fff7e8 0%, #fff 100%); }
.stat-card.danger { background: linear-gradient(135deg, #ffece8 0%, #fff 100%); }
.table-operations { display: flex; justify-content: space-between; margin-bottom: 16px; }
.amount { font-weight: 600; color: #1d2129; }
.sub-text { color: #86909c; font-size: 12px; }
.progress-wrap { padding: 0 8px; }
:deep(.row-warning) { background-color: #fff7e8 !important; }
:deep(.row-warning:hover) { background-color: #fff1d6 !important; }
:deep(.row-expired) { background-color: #ffece8 !important; }
:deep(.row-expired:hover) { background-color: #ffd9d0 !important; }
</style>
