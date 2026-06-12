<template>
  <div class="page-container">
    <div class="page-header detail-header">
      <div class="header-left">
        <a-button type="text" @click="goBack">
          <template #icon><icon-left /></template>
          返回列表
        </a-button>
        <h2>维保合同详情</h2>
        <a-tag v-if="contract" :color="getStatusColor(contract.status)" class="status-tag">
          {{ getStatusText(contract.status, contract.end_date) }}
        </a-tag>
      </div>
      <div class="header-right">
        <a-space>
          <a-button @click="handlePrint">
            <template #icon><icon-printer /></template>
            打印
          </a-button>
          <a-button @click="handleEdit">
            <template #icon><icon-edit /></template>
            编辑
          </a-button>
          <a-button type="primary" @click="handleRenew" v-if="contract && contract.status !== 'pending'">
            <template #icon><icon-sync /></template>
            续签
          </a-button>
        </a-space>
      </div>
    </div>

    <a-spin :loading="loading" tip="加载中...">
      <template v-if="contract">
        <a-row :gutter="16">
          <a-col :span="16">
            <a-card class="info-card" :bordered="false">
              <template #title>
                <div class="card-title">
                  <icon-file /> 合同基本信息
                </div>
              </template>
              <a-descriptions :column="2" bordered size="default">
                <a-descriptions-item label="合同编号">{{ contract.contract_no }}</a-descriptions-item>
                <a-descriptions-item label="合同名称">{{ contract.contract_name }}</a-descriptions-item>
                <a-descriptions-item label="签约供应商">
                  <a-button type="text">{{ contract.supplier_name }}</a-button>
                </a-descriptions-item>
                <a-descriptions-item label="合同金额">
                  <span class="amount-text">¥{{ formatNumber(contract.amount) }}</span>
                </a-descriptions-item>
                <a-descriptions-item label="合同起始日期">{{ contract.start_date }}</a-descriptions-item>
                <a-descriptions-item label="合同终止日期">{{ contract.end_date }}</a-descriptions-item>
                <a-descriptions-item label="服务频次">{{ getFrequencyText(contract.service_frequency) }}</a-descriptions-item>
                <a-descriptions-item label="响应时限">{{ contract.response_time }} 小时</a-descriptions-item>
                <a-descriptions-item label="关联设备数" :span="2">
                  <a-tag color="arcoblue">{{ contract.equipment_count }} 台设备</a-tag>
                </a-descriptions-item>
              </a-descriptions>
            </a-card>

            <a-card class="info-card" :bordered="false">
              <template #title>
                <div class="card-title">
                  <icon-file-text /> 合同条款摘要
                </div>
              </template>
              <a-empty v-if="!contract.terms_summary" description="暂无条款摘要" />
              <div v-else class="terms-content">
                {{ contract.terms_summary }}
              </div>
            </a-card>

            <a-card class="info-card" :bordered="false">
              <template #title>
                <div class="card-title">
                  <icon-list /> 服务范围描述
                </div>
              </template>
              <a-empty v-if="!contract.service_scope" description="暂无服务范围描述" />
              <div v-else class="scope-content">
                {{ contract.service_scope }}
              </div>
            </a-card>

            <a-card class="info-card" :bordered="false">
              <template #title>
                <div class="card-title">
                  <icon-swap /> 历次续签记录
                  <a-badge :count="renewHistory.length" :number-style="{ backgroundColor: '#165DFF' }" class="badge-count" />
                </div>
              </template>
              <a-table
                :columns="renewColumns"
                :data="renewHistory"
                :pagination="false"
                size="small"
                border
              >
                <template #amount="{ record }">
                  ¥{{ formatNumber(record.amount) }}
                </template>
                <template #date_range="{ record }">
                  <div>{{ record.start_date }} ~ {{ record.end_date }}</div>
                </template>
              </a-table>
            </a-card>
          </a-col>

          <a-col :span="8">
            <a-card class="info-card" :bordered="false">
              <template #title>
                <div class="card-title">
                  <icon-clock /> 合同进度
                </div>
              </template>
              <div class="progress-section">
                <a-progress
                  type="circle"
                  :percent="contract.progress"
                  :status="contract.progress >= 90 ? 'warning' : 'normal'"
                  :width="140"
                />
                <div class="progress-info">
                  <a-descriptions :column="1" size="small" class="progress-desc">
                    <a-descriptions-item label="剩余天数">
                      <span :class="daysLeft <= 30 ? 'danger-text' : ''">{{ daysLeft }} 天</span>
                    </a-descriptions-item>
                    <a-descriptions-item label="已执行天数">{{ daysPassed }} 天</a-descriptions-item>
                    <a-descriptions-item label="总天数">{{ totalDays }} 天</a-descriptions-item>
                  </a-descriptions>
                </div>
              </div>
            </a-card>

            <a-card class="info-card" :bordered="false">
              <template #title>
                <div class="card-title">
                  <icon-user /> 供应商信息
                </div>
              </template>
              <a-descriptions :column="1" size="small" bordered>
                <a-descriptions-item label="供应商名称">{{ contract.supplier_name }}</a-descriptions-item>
                <a-descriptions-item label="联系人">{{ supplierInfo.contact_person }}</a-descriptions-item>
                <a-descriptions-item label="联系电话">{{ supplierInfo.contact_phone }}</a-descriptions-item>
                <a-descriptions-item label="资质状态">
                  <a-tag :color="supplierInfo.qualification_status === 'qualified' ? 'green' : 'red'">
                    {{ supplierInfo.qualification_status === 'qualified' ? '合格' : '不合格' }}
                  </a-tag>
                </a-descriptions-item>
              </a-descriptions>
            </a-card>

            <a-card class="info-card" :bordered="false">
              <template #title>
                <div class="card-title">
                  <icon-storage /> 维保执行概况
                </div>
              </template>
              <a-row :gutter="8" class="stat-grid">
                <a-col :span="12">
                  <div class="mini-stat">
                    <div class="stat-value blue">{{ execStats.planned }}</div>
                    <div class="stat-label">计划维保次数</div>
                  </div>
                </a-col>
                <a-col :span="12">
                  <div class="mini-stat">
                    <div class="stat-value green">{{ execStats.completed }}</div>
                    <div class="stat-label">已完成次数</div>
                  </div>
                </a-col>
                <a-col :span="12">
                  <div class="mini-stat">
                    <div class="stat-value orange">{{ execStats.pending }}</div>
                    <div class="stat-label">待执行次数</div>
                  </div>
                </a-col>
                <a-col :span="12">
                  <div class="mini-stat">
                    <div class="stat-value red">{{ execStats.overdue }}</div>
                    <div class="stat-label">超期次数</div>
                  </div>
                </a-col>
              </a-row>
              <div class="exec-rate">
                <div class="rate-header">
                  <span>执行率</span>
                  <span class="rate-value">{{ execRate }}%</span>
                </div>
                <a-progress :percent="execRate" :status="execRate >= 90 ? 'success' : execRate >= 70 ? 'normal' : 'warning'" :show-text="false" />
              </div>
              <div class="avg-response">
                <icon-time /> 平均响应时长：<strong>{{ execStats.avg_response }}</strong> 小时
              </div>
            </a-card>
          </a-col>
        </a-row>

        <a-card class="info-card" :bordered="false">
          <template #title>
            <div class="card-title">
              <icon-computer /> 关联设备维保执行详情
            </div>
          </template>
          <a-table
            :columns="equipmentColumns"
            :data="equipmentExecList"
            :pagination="{ pageSize: 5 }"
            border
            :scroll="{ x: 1000 }"
          >
            <template #completed="{ record }">
              <a-tag color="green">{{ record.completed }}</a-tag>
            </template>
            <template #pending="{ record }">
              <a-tag color="orange">{{ record.pending }}</a-tag>
            </template>
            <template #overdue="{ record }">
              <a-tag color="red">{{ record.overdue }}</a-tag>
            </template>
            <template #rate="{ record }">
              <a-progress :percent="record.rate" size="small" :show-text="true" />
            </template>
            <template #last_date="{ record }">
              <div v-if="record.last_date">
                {{ record.last_date }}
                <div v-if="record.last_operator" class="sub-text">执行人：{{ record.last_operator }}</div>
              </div>
              <span v-else class="sub-text">暂无</span>
            </template>
            <template #next_date="{ record }">
              <a-tag v-if="record.next_date" :color="isNear(record.next_date) ? 'orange' : 'blue'">
                {{ record.next_date }}
              </a-tag>
              <span v-else class="sub-text">暂无</span>
            </template>
          </a-table>
        </a-card>
      </template>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const contract = ref<any>(null)

const supplierInfo = reactive({
  contact_person: '张经理',
  contact_phone: '13800138001',
  qualification_status: 'qualified'
})

const renewHistory = ref<any[]>([])
const equipmentExecList = ref<any[]>([])

const execStats = reactive({
  planned: 0,
  completed: 0,
  pending: 0,
  overdue: 0,
  avg_response: '2.5'
})

const renewColumns = [
  { title: '续签编号', dataIndex: 'renew_no', width: 140 },
  { title: '续签周期', slotName: 'date_range', width: 260 },
  { title: '续签金额', slotName: 'amount', width: 130, align: 'right' },
  { title: '续签日期', dataIndex: 'sign_date', width: 120 },
  { title: '经办人', dataIndex: 'operator', width: 100 },
  { title: '备注', dataIndex: 'remark', ellipsis: true }
]

const equipmentColumns = [
  { title: '设备编号', dataIndex: 'code', width: 110 },
  { title: '设备名称', dataIndex: 'name', width: 140 },
  { title: '安装位置', dataIndex: 'location', width: 120 },
  { title: '已完成', slotName: 'completed', width: 90, align: 'center' },
  { title: '待执行', slotName: 'pending', width: 90, align: 'center' },
  { title: '超期', slotName: 'overdue', width: 90, align: 'center' },
  { title: '执行率', slotName: 'rate', width: 150 },
  { title: '上次维保', slotName: 'last_date', width: 180 },
  { title: '下次维保', slotName: 'next_date', width: 140 }
]

const formatNumber = (num: number | string) => {
  if (num === null || num === undefined) return '0'
  return Number(num).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const getStatusColor = (s: string) => {
  const map: Record<string, string> = { active: 'green', warning: 'orange', expired: 'red', pending: 'gray' }
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

const getFrequencyText = (f: string) => {
  const map: Record<string, string> = {
    weekly: '每周', biweekly: '每两周', monthly: '每月', bimonthly: '每两月',
    quarterly: '每季度', semiyearly: '每半年', yearly: '每年', ondemand: '按需'
  }
  return map[f] || f
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

const daysLeft = computed(() => {
  if (!contract.value) return 0
  return Math.max(0, dayjs(contract.value.end_date).diff(dayjs(), 'day'))
})

const daysPassed = computed(() => {
  if (!contract.value) return 0
  return Math.max(0, dayjs().diff(dayjs(contract.value.start_date), 'day'))
})

const totalDays = computed(() => {
  if (!contract.value) return 0
  return dayjs(contract.value.end_date).diff(dayjs(contract.value.start_date), 'day')
})

const execRate = computed(() => {
  if (execStats.planned === 0) return 0
  return Math.round((execStats.completed / execStats.planned) * 100)
})

const isNear = (dateStr: string) => {
  return dayjs(dateStr).diff(dayjs(), 'day') <= 7
}

const fetchDetail = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 400))
    const id = Number(route.query.id) || 1
    const contractMap: Record<number, any> = {
      1: {
        id: 1, contract_no: 'WB2024001', contract_name: '曝气系统年度维保合同',
        supplier_id: 1, supplier_name: 'XX环保设备有限公司',
        amount: 128000, start_date: '2024-01-01', end_date: '2026-06-20',
        service_frequency: 'monthly', response_time: 4, equipment_count: 8,
        terms_summary: '1. 付款方式：合同签订后预付30%，每季度结算一次，尾款5%作为质保金期满后支付。\n2. 乙方需提供7×24小时紧急响应服务，故障报修后4小时内到场处理。\n3. 违约责任：乙方未按时到场每延迟1小时扣除合同金额0.1%，累计不超过合同金额的10%。\n4. 保密条款：双方对合同内容及履行过程中获取的对方商业信息负有保密义务。\n5. 质保期内同一故障维修三次以上仍不能正常使用，乙方应免费更换相应部件。',
        service_scope: '1. 曝气系统设备日常巡检与保养（每月1次），包含风机、曝气管路、阀门等；\n2. 设备故障维修与备件更换（不含大型设备整机更换）；\n3. 每季度进行一次设备性能检测与参数校准；\n4. 每年进行一次系统全面检修与评估，出具维保报告；\n5. 提供技术咨询与操作人员培训服务。'
      },
      2: {
        id: 2, contract_no: 'WB2024002', contract_name: '水泵组季度维保合同',
        supplier_id: 2, supplier_name: 'YY泵业技术服务公司',
        amount: 56000, start_date: '2024-03-01', end_date: '2026-07-15',
        service_frequency: 'quarterly', response_time: 2, equipment_count: 12,
        terms_summary: '1. 付款方式：合同签订后一次性支付全年费用；\n2. 紧急响应：主城区2小时内到达现场；\n3. 质保期：维保后设备质保3个月。',
        service_scope: '水泵组季度保养、故障维修、密封件更换、泵体清洁除锈等。'
      },
      3: {
        id: 3, contract_no: 'WB2023058', contract_name: '生化池搅拌设备维保合同',
        supplier_id: 3, supplier_name: 'ZZ机械维保服务中心',
        amount: 98000, start_date: '2023-07-01', end_date: '2025-06-30',
        service_frequency: 'monthly', response_time: 6, equipment_count: 5,
        terms_summary: '按月结算，6小时到场响应，维保范围含搅拌机械、减速装置等。',
        service_scope: '搅拌设备月度巡检、润滑保养、齿轮箱检修、叶片磨损检查等。'
      }
    }

    const baseContract = contractMap[id] || contractMap[1]
    contract.value = {
      ...baseContract,
      status: calcStatus(baseContract.start_date, baseContract.end_date),
      progress: calcProgress(baseContract.start_date, baseContract.end_date)
    }

    renewHistory.value = id === 1 ? [
      {
        renew_no: 'XQ2025001',
        start_date: '2025-01-01',
        end_date: '2025-12-31',
        amount: 120000,
        sign_date: '2024-12-20',
        operator: '李四',
        remark: '首次续签，合同金额上浮3%'
      },
      {
        renew_no: 'XQ2024001',
        start_date: '2024-01-01',
        end_date: '2024-12-31',
        amount: 116500,
        sign_date: '2023-12-18',
        operator: '王五',
        remark: '原始合同签订'
      }
    ] : []

    execStats.planned = 30
    execStats.completed = 27
    execStats.pending = 2
    execStats.overdue = 1
    execStats.avg_response = '3.2'

    equipmentExecList.value = [
      { code: 'EQ001', name: '曝气风机#1', location: '风机房', completed: 4, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-15', last_operator: '赵工', next_date: '2025-01-15' },
      { code: 'EQ002', name: '曝气风机#2', location: '风机房', completed: 3, pending: 1, overdue: 0, rate: 75, last_date: '2024-11-20', last_operator: '钱工', next_date: '2025-01-20' },
      { code: 'EQ003', name: '曝气风机#3', location: '风机房', completed: 4, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-18', last_operator: '赵工', next_date: '2025-01-18' },
      { code: 'EQ010', name: '曝气管阀组A', location: '生化池A段', completed: 4, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-10', last_operator: '孙工', next_date: '2025-01-10' },
      { code: 'EQ011', name: '曝气管阀组B', location: '生化池B段', completed: 3, pending: 0, overdue: 1, rate: 60, last_date: '2024-10-22', last_operator: '钱工', next_date: '2024-12-22' },
      { code: 'EQ012', name: '曝气主管路', location: '管廊', completed: 4, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-08', last_operator: '孙工', next_date: '2025-01-08' },
      { code: 'EQ013', name: '曝气支管组1', location: '生化池', completed: 3, pending: 1, overdue: 0, rate: 75, last_date: '2024-11-25', last_operator: '周工', next_date: '2025-01-05' },
      { code: 'EQ014', name: '曝气支管组2', location: '生化池', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-01', last_operator: '周工', next_date: '2025-01-01' }
    ]
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({ path: '/equipment/contract' })
}

const handlePrint = () => {
  Message.info('打印功能：调用浏览器打印')
  window.print()
}

const handleEdit = () => {
  Message.info('编辑合同：跳转至编辑表单')
}

const handleRenew = () => {
  Message.info('续签合同：打开续签弹窗')
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-right { display: flex; }
.status-tag { margin-left: 8px; }
.info-card { margin-bottom: 16px; border-radius: 8px; }
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
.badge-count { margin-left: 8px; }
.amount-text {
  font-size: 18px;
  font-weight: 700;
  color: #F53F3F;
}
.terms-content,
.scope-content {
  line-height: 1.8;
  white-space: pre-wrap;
  color: #4e5969;
  padding: 8px 0;
}
.progress-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 0;
}
.progress-desc { width: 100%; }
.danger-text { color: #F53F3F; font-weight: 600; }
.stat-grid { margin-bottom: 16px; }
.mini-stat {
  text-align: center;
  padding: 16px 8px;
  background: #F7F8FA;
  border-radius: 8px;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}
.stat-value.blue { color: #165DFF; }
.stat-value.green { color: #00B42A; }
.stat-value.orange { color: #FF7D00; }
.stat-value.red { color: #F53F3F; }
.stat-label {
  font-size: 12px;
  color: #86909c;
  margin-top: 4px;
}
.exec-rate { margin-bottom: 16px; }
.rate-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}
.rate-value { font-weight: 600; color: #165DFF; }
.avg-response {
  padding: 10px 12px;
  background: #F2F3F5;
  border-radius: 6px;
  font-size: 13px;
  color: #4e5969;
  display: flex;
  align-items: center;
  gap: 6px;
}
.sub-text { color: #86909c; font-size: 12px; }
</style>
