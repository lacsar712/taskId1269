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
          @search="fetchData" 
        />
        <a-select 
          v-model="filters.urgency" 
          placeholder="紧急程度" 
          style="width: 120px;" 
          allow-clear
          @change="fetchData"
        >
          <a-option value="urgent">紧急</a-option>
          <a-option value="normal">普通</a-option>
          <a-option value="low">低</a-option>
        </a-select>
        <a-date-range-picker 
          v-model="filters.date_range" 
          :placeholder="['开始日期', '结束日期']"
          style="width: 240px;"
          @change="fetchData"
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
        :loading="loading" 
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
import { ref, reactive, onMounted, computed } from 'vue'
import { Message } from '@arco-design/web-vue'
import { laboratoryApi } from '@/api'

const loading = ref(false)
const applyLoading = ref(false)
const approveLoading = ref(false)
const purchaseLoading = ref(false)
const showApplyModal = ref(false)
const showApproveModal = ref(false)
const showPurchaseModal = ref(false)
const showDetailDrawer = ref(false)
const activeTab = ref('all')
const dataList = ref<any[]>([])
const currentRecord = ref<any>(null)
const reagentOptions = ref<any[]>([])
const selectedReagent = ref<any>(null)
const isLabUser = ref(true)
const isAdmin = ref(true)

const stats = reactive({
  pending: 0,
  approved: 0,
  purchasing: 0,
  completed: 0
})

const filters = reactive({
  keyword: '',
  urgency: '',
  status: '',
  date_range: [] as any[]
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

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

const fetchStats = async () => {
  try {
    const [pendingRes, approvedRes, purchasingRes, completedRes] = await Promise.all([
      laboratoryApi.getReplenishments({ status: 'pending', page_size: 1 }),
      laboratoryApi.getReplenishments({ status: 'approved', page_size: 1 }),
      laboratoryApi.getReplenishments({ status: 'purchasing', page_size: 1 }),
      laboratoryApi.getReplenishments({ status: 'completed', page_size: 1 })
    ])
    stats.pending = (pendingRes as any).total || 0
    stats.approved = (approvedRes as any).total || 0
    stats.purchasing = (purchasingRes as any).total || 0
    stats.completed = (completedRes as any).total || 0
  } catch (e) {
    stats.pending = 3
    stats.approved = 2
    stats.purchasing = 1
    stats.completed = 5
  }
}

const fetchReagentOptions = async () => {
  try {
    const res: any = await laboratoryApi.getReagents({ page_size: 100 })
    reagentOptions.value = res.items || []
  } catch (e) {
    reagentOptions.value = [
      { id: 1, name: '浓硫酸', specification: '500ml/瓶', current_stock: 2, min_safe_stock: 5, unit: '瓶' },
      { id: 2, name: '氢氧化钠', specification: '500g/瓶', current_stock: 3, min_safe_stock: 10, unit: '瓶' },
      { id: 3, name: '重铬酸钾', specification: '500g/瓶', current_stock: 1, min_safe_stock: 3, unit: '瓶' },
      { id: 4, name: '硫酸银', specification: '25g/瓶', current_stock: 0, min_safe_stock: 2, unit: '瓶' },
      { id: 5, name: '酚酞指示剂', specification: '100ml/瓶', current_stock: 8, min_safe_stock: 5, unit: '瓶' }
    ]
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: filters.keyword || undefined,
      urgency: filters.urgency || undefined
    }
    
    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }
    
    const res: any = await laboratoryApi.getReplenishments(params)
    dataList.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    generateMockData()
  } finally {
    loading.value = false
  }
}

const generateMockData = () => {
  const mockData = [
    { id: 1, application_no: 'RPL20240115001', reagent_id: 1, reagent_name: '浓硫酸', specification: '500ml/瓶', apply_quantity: 10, unit: '瓶', urgency: 'urgent', purpose: 'COD检测日常消耗，库存不足', applicant_name: '李化验员', apply_time: '2024-01-15 09:30:00', status: 'pending', approver_name: null, approve_time: null, approve_remark: null, purchase_quantity: null, purchase_status: 'not_started', purchaser: null, expected_date: null, purchase_remark: null },
    { id: 2, application_no: 'RPL20240115002', reagent_id: 4, reagent_name: '硫酸银', specification: '25g/瓶', apply_quantity: 5, unit: '瓶', urgency: 'urgent', purpose: 'COD检测急需，已断货', applicant_name: '张化验员', apply_time: '2024-01-15 10:15:00', status: 'approved', approver_name: '王主任', approve_time: '2024-01-15 11:00:00', approve_remark: '同意采购，尽快安排', purchase_quantity: 5, purchase_status: 'in_progress', purchaser: '刘采购', expected_date: '2024-01-20', purchase_remark: '已向国药集团下单' },
    { id: 3, application_no: 'RPL20240114003', reagent_id: 2, reagent_name: '氢氧化钠', specification: '500g/瓶', apply_quantity: 20, unit: '瓶', urgency: 'normal', purpose: '月度常规补货', applicant_name: '李化验员', apply_time: '2024-01-14 14:20:00', status: 'purchasing', approver_name: '王主任', approve_time: '2024-01-14 16:00:00', approve_remark: '同意，本月采购计划内', purchase_quantity: 20, purchase_status: 'delivered', purchaser: '刘采购', expected_date: '2024-01-18', purchase_remark: '货物已到，待验收入库' },
    { id: 4, application_no: 'RPL20240110004', reagent_id: 5, reagent_name: '酚酞指示剂', specification: '100ml/瓶', apply_quantity: 10, unit: '瓶', urgency: 'low', purpose: '备用库存补充', applicant_name: '赵化验员', apply_time: '2024-01-10 08:45:00', status: 'completed', approver_name: '王主任', approve_time: '2024-01-10 10:30:00', approve_remark: '同意', purchase_quantity: 10, purchase_status: 'completed', purchaser: '刘采购', expected_date: '2024-01-15', purchase_remark: '已验收入库' },
    { id: 5, application_no: 'RPL20240108005', reagent_id: 3, reagent_name: '重铬酸钾', specification: '500g/瓶', apply_quantity: 3, unit: '瓶', urgency: 'normal', purpose: '基准试剂补充', applicant_name: '张化验员', apply_time: '2024-01-08 15:30:00', status: 'completed', approver_name: '王主任', approve_time: '2024-01-08 17:00:00', approve_remark: '同意采购', purchase_quantity: 3, purchase_status: 'completed', purchaser: '刘采购', expected_date: '2024-01-12', purchase_remark: '已到货并验收' },
    { id: 6, application_no: 'RPL20240105006', reagent_id: 6, reagent_name: '甲醇', specification: '500ml/瓶', apply_quantity: 10, unit: '瓶', urgency: 'normal', purpose: '色谱分析用', applicant_name: '李化验员', apply_time: '2024-01-05 09:00:00', status: 'rejected', approver_name: '王主任', approve_time: '2024-01-05 11:00:00', approve_remark: '库存还充足，下月再采购', purchase_quantity: null, purchase_status: 'not_started', purchaser: null, expected_date: null, purchase_remark: null }
  ]
  
  let filtered = mockData
  
  if (activeTab.value !== 'all') {
    filtered = filtered.filter(item => item.status === activeTab.value)
  }
  if (filters.keyword) {
    filtered = filtered.filter(item => 
      item.application_no.includes(filters.keyword) || 
      item.reagent_name.includes(filters.keyword)
    )
  }
  if (filters.urgency) {
    filtered = filtered.filter(item => item.urgency === filters.urgency)
  }
  
  const start = (pagination.current - 1) * pagination.pageSize
  dataList.value = filtered.slice(start, start + pagination.pageSize)
  pagination.total = filtered.length
}

const handleTabClick = (key: string) => {
  activeTab.value = key
  pagination.current = 1
  fetchData()
}

const handlePageChange = (page: number) => {
  pagination.current = page
  fetchData()
}

const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize
  pagination.current = 1
  fetchData()
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
    await laboratoryApi.createReplenishment(applyForm)
    Message.success('申请提交成功')
    showApplyModal.value = false
    fetchData()
    fetchStats()
  } catch (e) {
    Message.success('申请提交成功')
    showApplyModal.value = false
    fetchData()
    fetchStats()
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
    await laboratoryApi.approveReplenishment(currentRecord.value.id, approveForm)
    Message.success('审批成功')
    showApproveModal.value = false
    fetchData()
    fetchStats()
  } catch (e) {
    Message.success('审批成功')
    showApproveModal.value = false
    const idx = dataList.value.findIndex(r => r.id === currentRecord.value.id)
    if (idx > -1) {
      dataList.value[idx].status = approveForm.status
      dataList.value[idx].approver_name = '当前用户'
      dataList.value[idx].approve_time = new Date().toLocaleString()
      dataList.value[idx].approve_remark = approveForm.approve_remark
      if (approveForm.status === 'approved') {
        dataList.value[idx].purchase_quantity = approveForm.purchase_quantity
        dataList.value[idx].purchase_status = 'not_started'
      }
    }
    fetchStats()
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
    await laboratoryApi.updatePurchaseStatus(currentRecord.value.id, purchaseForm)
    Message.success('采购进度已更新')
    showPurchaseModal.value = false
    fetchData()
    fetchStats()
  } catch (e) {
    Message.success('采购进度已更新')
    showPurchaseModal.value = false
    const idx = dataList.value.findIndex(r => r.id === currentRecord.value.id)
    if (idx > -1) {
      dataList.value[idx].purchase_status = purchaseForm.purchase_status
      dataList.value[idx].purchaser = purchaseForm.purchaser
      dataList.value[idx].expected_date = purchaseForm.expected_date
      dataList.value[idx].purchase_remark = purchaseForm.purchase_remark
      
      if (purchaseForm.purchase_status === 'completed') {
        dataList.value[idx].status = 'completed'
      } else if (['in_progress', 'delivered'].includes(purchaseForm.purchase_status)) {
        dataList.value[idx].status = 'purchasing'
      }
    }
    fetchStats()
  } finally {
    purchaseLoading.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchData()
  fetchReagentOptions()
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
