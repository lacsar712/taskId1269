<template>
  <div class="page-container reagent-replenishment">
    <div class="page-header">
      <h2>试剂补货申请管理</h2>
      <p>化验员发起补货申请，管理员审批并跟踪采购进度，形成试剂从预警到补货的完整管理链路</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card pending">
        <div class="stat-icon">
          <icon-clock-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待审批</div>
        </div>
      </div>
      <div class="stat-card approved">
        <div class="stat-icon">
          <icon-check-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.approved }}</div>
          <div class="stat-label">已批准</div>
        </div>
      </div>
      <div class="stat-card purchasing">
        <div class="stat-icon">
          <icon-sync />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.purchasing }}</div>
          <div class="stat-label">采购中</div>
        </div>
      </div>
      <div class="stat-card completed">
        <div class="stat-icon">
          <icon-inbox />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.completed }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
    </div>

    <!-- Tab切换 -->
    <a-tabs v-model:active-key="activeTab" @tab-click="handleTabClick">
      <a-tab-pane key="all" title="全部申请" />
      <a-tab-pane key="pending" title="待审批">
        <template #title>
          <span>待审批 <a-badge :count="stats.pending" v-if="stats.pending > 0" :number-style="{ backgroundColor: '#ff7d00' }" /></span>
        </template>
      </a-tab-pane>
      <a-tab-pane key="purchasing" title="采购中" />
      <a-tab-pane key="completed" title="已完成" />
    </a-tabs>

    <!-- 操作栏 -->
    <div class="table-operations">
      <a-space :size="12">
        <a-input-search 
          v-model="filters.keyword" 
          placeholder="搜索申请编号/试剂名称" 
          style="width: 240px;" 
        />
        <a-select 
          v-model="filters.urgency" 
          placeholder="紧急程度" 
          style="width: 120px;" 
          allow-clear
        >
          <a-option value="urgent">紧急</a-option>
          <a-option value="normal">普通</a-option>
          <a-option value="low">低</a-option>
        </a-select>
        <a-date-range-picker 
          v-model="filters.date_range" 
          :placeholder="['开始日期', '结束日期']"
          style="width: 240px;"
        />
      </a-space>
      <a-button type="primary" @click="openApplyModal" v-if="isLabUser">
        <template #icon><icon-plus /></template>
        发起申请
      </a-button>
    </div>

    <!-- 申请列表 -->
    <div class="table-wrapper">
      <a-table 
        :columns="columns" 
        :data="dataList" 
        :loading="false" 
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        :scroll="{ x: 1300 }"
      >
        <template #urgency="{ record }">
          <a-tag :color="getUrgencyColor(record.urgency)">
            {{ getUrgencyText(record.urgency) }}
          </a-tag>
        </template>

        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </a-tag>
        </template>

        <template #purchase_status="{ record }">
          <a-tag v-if="record.status === 'approved' || record.status === 'purchasing' || record.status === 'completed'" 
            :color="getPurchaseStatusColor(record.purchase_status)">
            {{ getPurchaseStatusText(record.purchase_status) }}
          </a-tag>
          <span v-else>-</span>
        </template>

        <template #quantity="{ record }">
          <span>{{ record.apply_quantity }} {{ record.unit }}</span>
        </template>

        <template #operations="{ record }">
          <a-space :size="4">
            <a-button type="text" size="small" @click="viewDetail(record)">详情</a-button>
            <a-button 
              type="text" 
              size="small" 
              v-if="record.status === 'pending' && isAdmin"
              @click="openApproveModal(record)"
            >
              审批
            </a-button>
            <a-button 
              type="text" 
              size="small" 
              v-if="(record.status === 'approved' || record.status === 'purchasing') && isAdmin"
              @click="openPurchaseModal(record)"
            >
              采购进度
            </a-button>
          </a-space>
        </template>
      </a-table>
    </div>

    <!-- 发起申请弹窗 -->
    <a-modal 
      v-model:visible="showApplyModal" 
      title="发起补货申请" 
      @ok="submitApply" 
      :ok-loading="applyLoading"
      width="560px"
    >
      <a-form :model="applyForm" layout="vertical">
        <a-form-item label="选择试剂" required>
          <a-select 
            v-model="applyForm.reagent_id" 
            placeholder="请选择需要补货的试剂"
            show-search
            :option-filter="(inputValue: string, option: any) => option.label?.toLowerCase().includes(inputValue.toLowerCase())"
            @change="onReagentSelect"
          >
            <a-option 
              v-for="reagent in reagentOptions" 
              :key="reagent.id" 
              :value="reagent.id"
              :label="reagent.name"
            >
              <div class="reagent-option">
                <span class="reagent-name">{{ reagent.name }}</span>
                <span class="reagent-spec">{{ reagent.specification || '-' }}</span>
                <span 
                  class="reagent-stock"
                  :class="{ 'low': reagent.current_stock <= reagent.min_safe_stock }"
                >
                  库存: {{ reagent.current_stock }}/{{ reagent.min_safe_stock }}
                </span>
              </div>
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="申请数量" required>
          <a-input-number 
            v-model="applyForm.apply_quantity" 
            :min="1" 
            :style="{ width: '100%' }"
            :addon-after="selectedReagent?.unit || '瓶'"
          />
        </a-form-item>
        <a-form-item label="紧急程度" required>
          <a-radio-group v-model="applyForm.urgency">
            <a-radio value="urgent">紧急</a-radio>
            <a-radio value="normal">普通</a-radio>
            <a-radio value="low">低</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="用途说明">
          <a-textarea 
            v-model="applyForm.purpose" 
            placeholder="请简要说明试剂用途"
            :auto-size="{ minRows: 3, maxRows: 5 }"
            :max-length="200"
            show-word-limit
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 审批弹窗 -->
    <a-modal 
      v-model:visible="showApproveModal" 
      title="审批补货申请" 
      @ok="submitApprove" 
      :ok-loading="approveLoading"
      width="600px"
    >
      <div v-if="currentRecord">
        <a-descriptions :column="2" size="small" bordered style="margin-bottom: 16px;">
          <a-descriptions-item label="申请编号">{{ currentRecord.application_no }}</a-descriptions-item>
          <a-descriptions-item label="试剂名称">{{ currentRecord.reagent_name }}</a-descriptions-item>
          <a-descriptions-item label="规格">{{ currentRecord.specification || '-' }}</a-descriptions-item>
          <a-descriptions-item label="申请数量">{{ currentRecord.apply_quantity }} {{ currentRecord.unit }}</a-descriptions-item>
          <a-descriptions-item label="紧急程度">
            <a-tag :color="getUrgencyColor(currentRecord.urgency)">
              {{ getUrgencyText(currentRecord.urgency) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="申请人">{{ currentRecord.applicant_name }}</a-descriptions-item>
          <a-descriptions-item label="申请时间">{{ currentRecord.apply_time }}</a-descriptions-item>
          <a-descriptions-item label="用途" :span="2">{{ currentRecord.purpose || '-' }}</a-descriptions-item>
        </a-descriptions>

        <a-form :model="approveForm" layout="vertical">
          <a-form-item label="审批结果" required>
            <a-radio-group v-model="approveForm.status">
              <a-radio value="approved">通过</a-radio>
              <a-radio value="rejected">拒绝</a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item label="采购数量" v-if="approveForm.status === 'approved'">
            <a-input-number 
              v-model="approveForm.purchase_quantity" 
              :min="0" 
              :style="{ width: '100%' }"
              :addon-after="currentRecord.unit"
            />
            <span class="form-tip">可根据实际情况调整采购数量</span>
          </a-form-item>
          <a-form-item label="审批备注">
            <a-textarea 
              v-model="approveForm.approve_remark" 
              placeholder="请输入审批意见"
              :auto-size="{ minRows: 2, maxRows: 4 }"
            />
          </a-form-item>
        </a-form>
      </div>
    </a-modal>

    <!-- 采购进度更新弹窗 -->
    <a-modal 
      v-model:visible="showPurchaseModal" 
      title="更新采购进度" 
      @ok="submitPurchaseUpdate" 
      :ok-loading="purchaseLoading"
      width="520px"
    >
      <div v-if="currentRecord">
        <a-descriptions :column="2" size="small" bordered style="margin-bottom: 16px;">
          <a-descriptions-item label="申请编号">{{ currentRecord.application_no }}</a-descriptions-item>
          <a-descriptions-item label="试剂名称">{{ currentRecord.reagent_name }}</a-descriptions-item>
          <a-descriptions-item label="采购数量">
            {{ currentRecord.purchase_quantity || currentRecord.apply_quantity }} {{ currentRecord.unit }}
          </a-descriptions-item>
          <a-descriptions-item label="当前状态">
            <a-tag :color="getPurchaseStatusColor(currentRecord.purchase_status)">
              {{ getPurchaseStatusText(currentRecord.purchase_status) }}
            </a-tag>
          </a-descriptions-item>
        </a-descriptions>

        <a-form :model="purchaseForm" layout="vertical">
          <a-form-item label="采购状态" required>
            <a-select v-model="purchaseForm.purchase_status" style="width: 100%;">
              <a-option value="not_started">未开始</a-option>
              <a-option value="in_progress">采购中</a-option>
              <a-option value="delivered">已到货</a-option>
              <a-option value="completed">采购完成</a-option>
            </a-select>
          </a-form-item>
          <a-form-item label="采购员">
            <a-input v-model="purchaseForm.purchaser" placeholder="请输入采购员姓名" />
          </a-form-item>
          <a-form-item label="预计到货日期">
            <a-date-picker v-model="purchaseForm.expected_date" style="width: 100%;" />
          </a-form-item>
          <a-form-item label="采购备注">
            <a-textarea 
              v-model="purchaseForm.purchase_remark" 
              placeholder="请输入采购进度说明"
              :auto-size="{ minRows: 2, maxRows: 4 }"
            />
          </a-form-item>
        </a-form>
      </div>
    </a-modal>

    <!-- 申请详情抽屉 -->
    <a-drawer v-model:visible="showDetailDrawer" title="补货申请详情" :width="560">
      <div v-if="currentRecord">
        <a-steps :current="getStepIndex()" line-less size="small" style="margin-bottom: 24px;">
          <a-step title="提交申请" :description="currentRecord.apply_time" />
          <a-step 
            title="审批" 
            :description="currentRecord.approve_time || '待审批'"
            :status="getApprovalStepStatus()"
          />
          <a-step 
            title="采购中" 
            :description="currentRecord.status === 'completed' ? '已完成' : getPurchaseStatusText(currentRecord.purchase_status)"
            :status="getPurchaseStepStatus()"
          />
          <a-step 
            title="到货入库" 
            :description="currentRecord.status === 'completed' ? '已完成' : ''"
            :status="currentRecord.status === 'completed' ? 'finish' : 'wait'"
          />
        </a-steps>

        <a-descriptions :column="2" bordered size="small">
          <a-descriptions-item label="申请编号">{{ currentRecord.application_no }}</a-descriptions-item>
          <a-descriptions-item label="试剂名称">{{ currentRecord.reagent_name }}</a-descriptions-item>
          <a-descriptions-item label="规格">{{ currentRecord.specification || '-' }}</a-descriptions-item>
          <a-descriptions-item label="申请数量">{{ currentRecord.apply_quantity }} {{ currentRecord.unit }}</a-descriptions-item>
          <a-descriptions-item label="紧急程度">
            <a-tag :color="getUrgencyColor(currentRecord.urgency)">
              {{ getUrgencyText(currentRecord.urgency) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="申请人">{{ currentRecord.applicant_name }}</a-descriptions-item>
          <a-descriptions-item label="申请时间">{{ currentRecord.apply_time }}</a-descriptions-item>
          <a-descriptions-item label="申请状态">
            <a-tag :color="getStatusColor(currentRecord.status)">
              {{ getStatusText(currentRecord.status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="用途" :span="2">{{ currentRecord.purpose || '-' }}</a-descriptions-item>
        </a-descriptions>

        <a-divider style="margin: 20px 0;" />

        <div v-if="currentRecord.approver_name" class="section-title">审批信息</div>
        <a-descriptions v-if="currentRecord.approver_name" :column="2" bordered size="small">
          <a-descriptions-item label="审批人">{{ currentRecord.approver_name }}</a-descriptions-item>
          <a-descriptions-item label="审批时间">{{ currentRecord.approve_time }}</a-descriptions-item>
          <a-descriptions-item label="采购数量">
            {{ currentRecord.purchase_quantity || '-' }} {{ currentRecord.unit }}
          </a-descriptions-item>
          <a-descriptions-item label="审批结果">
            <a-tag :color="currentRecord.status === 'approved' ? 'green' : 'red'">
              {{ currentRecord.status === 'approved' ? '通过' : '拒绝' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="审批备注" :span="2">
            {{ currentRecord.approve_remark || '-' }}
          </a-descriptions-item>
        </a-descriptions>

        <a-divider style="margin: 20px 0;" />

        <div 
          v-if="currentRecord.status === 'approved' || currentRecord.status === 'purchasing' || currentRecord.status === 'completed'"
          class="section-title"
        >
          采购信息
        </div>
        <a-descriptions 
          v-if="currentRecord.status === 'approved' || currentRecord.status === 'purchasing' || currentRecord.status === 'completed'"
          :column="2" 
          bordered 
          size="small"
        >
          <a-descriptions-item label="采购状态">
            <a-tag :color="getPurchaseStatusColor(currentRecord.purchase_status)">
              {{ getPurchaseStatusText(currentRecord.purchase_status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="采购员">{{ currentRecord.purchaser || '-' }}</a-descriptions-item>
          <a-descriptions-item label="预计到货">{{ currentRecord.expected_date || '-' }}</a-descriptions-item>
          <a-descriptions-item label="采购数量">
            {{ currentRecord.purchase_quantity || '-' }} {{ currentRecord.unit }}
          </a-descriptions-item>
          <a-descriptions-item label="采购备注" :span="2">
            {{ currentRecord.purchase_remark || '-' }}
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useReagentStore } from '@/stores/reagent'

const store = useReagentStore()

const applyLoading = ref(false)
const approveLoading = ref(false)
const purchaseLoading = ref(false)
const showApplyModal = ref(false)
const showApproveModal = ref(false)
const showPurchaseModal = ref(false)
const showDetailDrawer = ref(false)
const activeTab = ref('all')
const currentRecord = ref<any>(null)
const selectedReagent = ref<any>(null)
const isLabUser = ref(true)
const isAdmin = ref(true)

const stats = computed(() => store.replenishmentStats)

const filters = reactive({
  keyword: '',
  urgency: '',
  date_range: [] as any[]
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const reagentOptions = computed(() => store.activeReagents)

const applyForm = reactive({
  reagent_id: null as number | null,
  apply_quantity: 1,
  urgency: 'normal',
  purpose: ''
})

const approveForm = reactive({
  status: 'approved',
  purchase_quantity: 0,
  approve_remark: ''
})

const purchaseForm = reactive({
  purchase_status: 'not_started',
  purchaser: '',
  expected_date: '',
  purchase_remark: ''
})

const filteredReplenishments = computed(() => {
  let list = [...store.replenishments]
  if (activeTab.value !== 'all') {
    list = list.filter(item => item.status === activeTab.value)
  }
  if (filters.keyword) {
    const kw = filters.keyword.toLowerCase()
    list = list.filter(item =>
      item.application_no.toLowerCase().includes(kw) ||
      item.reagent_name.toLowerCase().includes(kw)
    )
  }
  if (filters.urgency) {
    list = list.filter(item => item.urgency === filters.urgency)
  }
  if (filters.date_range && filters.date_range.length === 2) {
    const start = new Date(filters.date_range[0])
    const end = new Date(filters.date_range[1])
    list = list.filter(item => {
      const d = new Date(item.apply_time)
      return d >= start && d <= end
    })
  }
  return list
})

const dataList = computed(() => {
  const start = (pagination.current - 1) * pagination.pageSize
  pagination.total = filteredReplenishments.value.length
  return filteredReplenishments.value.slice(start, start + pagination.pageSize)
})

const columns = [
  { title: '申请编号', dataIndex: 'application_no', width: 160 },
  { title: '试剂名称', dataIndex: 'reagent_name', width: 130 },
  { title: '规格', dataIndex: 'specification', width: 120 },
  { title: '申请数量', dataIndex: 'quantity', slotName: 'quantity', width: 110 },
  { title: '紧急程度', dataIndex: 'urgency', slotName: 'urgency', width: 100 },
  { title: '申请人', dataIndex: 'applicant_name', width: 100 },
  { title: '申请时间', dataIndex: 'apply_time', width: 160 },
  { title: '申请状态', dataIndex: 'status', slotName: 'status', width: 100 },
  { title: '采购进度', dataIndex: 'purchase_status', slotName: 'purchase_status', width: 110 },
  { title: '操作', dataIndex: 'operations', slotName: 'operations', width: 180, fixed: 'right' }
]

const getUrgencyColor = (urgency: string) => {
  const map: Record<string, string> = { urgent: 'red', normal: 'blue', low: 'gray' }
  return map[urgency] || 'gray'
}

const getUrgencyText = (urgency: string) => {
  const map: Record<string, string> = { urgent: '紧急', normal: '普通', low: '低' }
  return map[urgency] || '未知'
}

const getStatusColor = (status: string) => {
  const map: Record<string, string> = {
    pending: 'orange',
    approved: 'arcoblue',
    rejected: 'red',
    purchasing: 'gold',
    completed: 'green'
  }
  return map[status] || 'gray'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝',
    purchasing: '采购中',
    completed: '已完成'
  }
  return map[status] || '未知'
}

const getPurchaseStatusColor = (status: string) => {
  const map: Record<string, string> = {
    not_started: 'gray',
    in_progress: 'orange',
    delivered: 'blue',
    completed: 'green'
  }
  return map[status] || 'gray'
}

const getPurchaseStatusText = (status: string) => {
  const map: Record<string, string> = {
    not_started: '未开始',
    in_progress: '采购中',
    delivered: '已到货',
    completed: '已完成'
  }
  return map[status] || '未知'
}

const getStepIndex = () => {
  if (!currentRecord.value) return 0
  const status = currentRecord.value.status
  if (status === 'pending') return 0
  if (status === 'approved') return 1
  if (status === 'purchasing') return 2
  if (status === 'completed') return 3
  return 0
}

const getApprovalStepStatus = () => {
  if (!currentRecord.value) return 'wait'
  if (currentRecord.value.status === 'pending') return 'process'
  if (currentRecord.value.status === 'rejected') return 'error'
  if (['approved', 'purchasing', 'completed'].includes(currentRecord.value.status)) return 'finish'
  return 'wait'
}

const getPurchaseStepStatus = () => {
  if (!currentRecord.value) return 'wait'
  if (currentRecord.value.status === 'completed') return 'finish'
  if (currentRecord.value.status === 'purchasing') return 'process'
  if (currentRecord.value.status === 'approved') return 'wait'
  return 'wait'
}

const handleTabClick = (key: string) => {
  activeTab.value = key
  pagination.current = 1
}

const handlePageChange = (page: number) => {
  pagination.current = page
}

const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize
  pagination.current = 1
}

const openApplyModal = () => {
  applyForm.reagent_id = null
  applyForm.apply_quantity = 1
  applyForm.urgency = 'normal'
  applyForm.purpose = ''
  selectedReagent.value = null
  showApplyModal.value = true
}

const onReagentSelect = (value: number) => {
  const reagent = reagentOptions.value.find(r => r.id === value)
  if (reagent) {
    selectedReagent.value = reagent
    const diff = reagent.min_safe_stock - reagent.current_stock
    applyForm.apply_quantity = Math.max(1, diff > 0 ? diff : reagent.min_safe_stock)
    applyForm.urgency = reagent.current_stock <= 0 ? 'urgent' : (reagent.current_stock <= reagent.min_safe_stock / 2 ? 'urgent' : 'normal')
  }
}

const submitApply = async () => {
  if (!applyForm.reagent_id) {
    Message.warning('请选择试剂')
    return
  }
  if (!applyForm.apply_quantity || applyForm.apply_quantity <= 0) {
    Message.warning('请输入申请数量')
    return
  }
  
  applyLoading.value = true
  try {
    const result = store.addReplenishment({
      reagent_id: applyForm.reagent_id,
      apply_quantity: applyForm.apply_quantity,
      urgency: applyForm.urgency,
      purpose: applyForm.purpose
    })
    if (result) {
      Message.success('申请提交成功')
      showApplyModal.value = false
    } else {
      Message.error('提交失败，未找到对应试剂')
    }
  } finally {
    applyLoading.value = false
  }
}

const viewDetail = (record: any) => {
  currentRecord.value = record
  showDetailDrawer.value = true
}

const openApproveModal = (record: any) => {
  currentRecord.value = record
  approveForm.status = 'approved'
  approveForm.purchase_quantity = record.apply_quantity
  approveForm.approve_remark = ''
  showApproveModal.value = true
}

const submitApprove = async () => {
  approveLoading.value = true
  try {
    const result = store.approveReplenishment(currentRecord.value.id, {
      status: approveForm.status,
      approve_remark: approveForm.approve_remark,
      purchase_quantity: approveForm.purchase_quantity
    })
    if (result) {
      Message.success(approveForm.status === 'approved' ? '已批准，等待采购' : '已拒绝')
      showApproveModal.value = false
    } else {
      Message.error('审批失败，该申请当前状态不允许审批')
    }
  } finally {
    approveLoading.value = false
  }
}

const openPurchaseModal = (record: any) => {
  currentRecord.value = record
  purchaseForm.purchase_status = record.purchase_status || 'not_started'
  purchaseForm.purchaser = record.purchaser || ''
  purchaseForm.expected_date = record.expected_date || ''
  purchaseForm.purchase_remark = record.purchase_remark || ''
  showPurchaseModal.value = true
}

const submitPurchaseUpdate = async () => {
  purchaseLoading.value = true
  try {
    const result = store.updatePurchaseStatus(currentRecord.value.id, {
      purchase_status: purchaseForm.purchase_status,
      purchaser: purchaseForm.purchaser,
      expected_date: purchaseForm.expected_date,
      purchase_remark: purchaseForm.purchase_remark
    })
    if (result) {
      if (purchaseForm.purchase_status === 'completed') {
        Message.success('采购完成，库存已自动更新')
      } else {
        Message.success('采购进度已更新')
      }
      showPurchaseModal.value = false
    } else {
      Message.error('更新失败，该申请当前状态不允许更新采购进度')
    }
  } finally {
    purchaseLoading.value = false
  }
}

onMounted(() => {
  store.fetchReplenishments()
  store.fetchReagents()
})
</script>

<style scoped>
.reagent-replenishment {
  min-height: calc(100vh - 120px);
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 16px;
}

.stat-card.pending .stat-icon {
  background: linear-gradient(135deg, #fff7e8, #ffe7c8);
  color: #ff7d00;
}

.stat-card.approved .stat-icon {
  background: linear-gradient(135deg, #e8f3ff, #d6e4ff);
  color: #165DFF;
}

.stat-card.purchasing .stat-icon {
  background: linear-gradient(135deg, #e8ffea, #c8ffcd);
  color: #00b42a;
}

.stat-card.completed .stat-icon {
  background: linear-gradient(135deg, #f0f5ff, #e8f3ff);
  color: #4e5969;
}

.stat-info .stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  line-height: 1.2;
}

.stat-card.pending .stat-value { color: #ff7d00; }
.stat-card.approved .stat-value { color: #165DFF; }
.stat-card.purchasing .stat-value { color: #00b42a; }
.stat-card.completed .stat-value { color: #4e5969; }

.stat-info .stat-label {
  font-size: 14px;
  color: #86909c;
  margin-top: 4px;
}

.table-operations {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
}

.table-wrapper {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  padding: 16px;
}

.reagent-option {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.reagent-name {
  font-weight: 500;
  color: #1d2129;
}

.reagent-spec {
  font-size: 12px;
  color: #86909c;
}

.reagent-stock {
  margin-left: auto;
  font-size: 12px;
  color: #00b42a;
}

.reagent-stock.low {
  color: #f53f3f;
  font-weight: 500;
}

.form-tip {
  display: block;
  font-size: 12px;
  color: #86909c;
  margin-top: 4px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 12px;
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .table-operations {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>
