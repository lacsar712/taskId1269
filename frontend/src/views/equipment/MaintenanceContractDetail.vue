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

            <a-card class="info-card supplier-card" :bordered="false">
              <template #title>
                <div class="card-title">
                  <icon-user /> 供应商联系方式
                </div>
              </template>
              <a-descriptions :column="1" size="small" bordered>
                <a-descriptions-item label="供应商全称">{{ supplierInfo.name }}</a-descriptions-item>
                <a-descriptions-item label="项目对接人">
                  <span class="contact-name">{{ supplierInfo.contact_person }}</span>
                </a-descriptions-item>
                <a-descriptions-item label="联系电话">
                  <a-button type="text" size="small" class="phone-link" @click="callPhone(supplierInfo.contact_phone)">
                    <template #icon><icon-phone /></template>
                    {{ supplierInfo.contact_phone }}
                  </a-button>
                </a-descriptions-item>
                <a-descriptions-item label="电子邮箱">
                  <a-button type="text" size="small" class="email-link" @click="sendEmail(supplierInfo.contact_email)">
                    <template #icon><icon-email /></template>
                    {{ supplierInfo.contact_email }}
                  </a-button>
                </a-descriptions-item>
                <a-descriptions-item label="公司地址">{{ supplierInfo.company_address }}</a-descriptions-item>
                <a-descriptions-item label="资质状态">
                  <a-space>
                    <a-tag :color="supplierInfo.qualification_status === 'qualified' ? 'green' : 'red'">
                      {{ supplierInfo.qualification_status === 'qualified' ? '合格' : '不合格' }}
                    </a-tag>
                    <span class="sub-text">有效期至 {{ supplierInfo.qualification_expire }}</span>
                  </a-space>
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

const supplierInfo = ref({
  contact_person: '',
  contact_phone: '',
  qualification_status: 'qualified'
})

const renewHistory = ref<any[]>([])
const equipmentExecList = ref<any[]>([])

const execStats = ref({
  planned: 0,
  completed: 0,
  pending: 0,
  overdue: 0,
  avg_response: '0'
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
  if (execStats.value.planned === 0) return 0
  return Math.round((execStats.value.completed / execStats.value.planned) * 100)
})

const isNear = (dateStr: string) => {
  return dayjs(dateStr).diff(dayjs(), 'day') <= 7
}

const supplierMap: Record<number, any> = {
  1: {
    name: 'XX环保设备有限公司',
    contact_person: '张建国',
    contact_phone: '13800138101',
    contact_email: 'zhangjg@xxhb.com',
    company_address: '上海市浦东新区张江高科技园区科苑路88号',
    qualification_status: 'qualified',
    qualification_expire: '2026-12-31',
    bank_account: '6222 0812 0000 1234 567'
  },
  2: {
    name: 'YY泵业技术服务公司',
    contact_person: '李明辉',
    contact_phone: '13900139202',
    contact_email: 'limh@yy-pump.com',
    company_address: '江苏省苏州市工业园区星湖街328号',
    qualification_status: 'qualified',
    qualification_expire: '2025-08-15',
    bank_account: '6228 4812 0000 9876 543'
  },
  3: {
    name: 'ZZ机械维保服务中心',
    contact_person: '王志强',
    contact_phone: '13700137303',
    contact_email: 'wangzq@zzjixie.com',
    company_address: '浙江省杭州市余杭区未来科技城海曙路28号',
    qualification_status: 'qualified',
    qualification_expire: '2026-03-20',
    bank_account: '6217 0031 0000 4567 890'
  },
  4: {
    name: 'AA自动化科技公司',
    contact_person: '陈雪峰',
    contact_phone: '13600136404',
    contact_email: 'chenxf@aauto.com',
    company_address: '北京市海淀区中关村软件园二期西二旗大街39号',
    qualification_status: 'unqualified',
    qualification_expire: '2024-11-30',
    bank_account: '6222 0202 0000 2345 678'
  },
  5: {
    name: 'BB阀门技术服务部',
    contact_person: '刘卫东',
    contact_phone: '13500135505',
    contact_email: 'liuwd@bbvalve.com',
    company_address: '天津市滨海新区塘沽海洋科技园海缘路199号',
    qualification_status: 'qualified',
    qualification_expire: '2027-01-10',
    bank_account: '6228 4802 0000 3456 789'
  },
  6: {
    name: 'CC计量检测研究院',
    contact_person: '赵春华',
    contact_phone: '13400134606',
    contact_email: 'zhaoch@ccjl.org.cn',
    company_address: '南京市玄武区珠江路688号卓越骇客天街15楼',
    qualification_status: 'qualified',
    qualification_expire: '2026-09-01',
    bank_account: '6217 9965 0000 5678 901'
  }
}

const contractExecData: Record<number, any> = {
  1: {
    execStats: { planned: 30, completed: 27, pending: 2, overdue: 1, avg_response: '3.2' },
    equipmentList: [
      { code: 'EQ001', name: '曝气风机#1', location: '风机房', completed: 4, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-15', last_operator: '赵工（XX环保）', next_date: '2025-01-15' },
      { code: 'EQ002', name: '曝气风机#2', location: '风机房', completed: 3, pending: 1, overdue: 0, rate: 75, last_date: '2024-11-20', last_operator: '钱工（XX环保）', next_date: '2025-01-20' },
      { code: 'EQ003', name: '曝气风机#3', location: '风机房', completed: 4, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-18', last_operator: '赵工（XX环保）', next_date: '2025-01-18' },
      { code: 'EQ010', name: '曝气管阀组A', location: '生化池A段', completed: 4, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-10', last_operator: '孙工（XX环保）', next_date: '2025-01-10' },
      { code: 'EQ011', name: '曝气管阀组B', location: '生化池B段', completed: 3, pending: 0, overdue: 1, rate: 60, last_date: '2024-10-22', last_operator: '钱工（XX环保）', next_date: '2024-12-22' },
      { code: 'EQ012', name: '曝气主管路', location: '管廊', completed: 4, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-08', last_operator: '孙工（XX环保）', next_date: '2025-01-08' },
      { code: 'EQ013', name: '曝气支管组1', location: '生化池', completed: 3, pending: 1, overdue: 0, rate: 75, last_date: '2024-11-25', last_operator: '周工（XX环保）', next_date: '2025-01-05' },
      { code: 'EQ014', name: '曝气支管组2', location: '生化池', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-01', last_operator: '周工（XX环保）', next_date: '2025-01-01' }
    ]
  },
  2: {
    execStats: { planned: 8, completed: 7, pending: 1, overdue: 0, avg_response: '1.8' },
    equipmentList: [
      { code: 'EQ201', name: '提升泵#1', location: '进水泵房', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-05', last_operator: '郑工（YY泵业）', next_date: '2025-03-05' },
      { code: 'EQ202', name: '提升泵#2', location: '进水泵房', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-05', last_operator: '郑工（YY泵业）', next_date: '2025-03-05' },
      { code: 'EQ203', name: '提升泵#3', location: '进水泵房', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-06', last_operator: '郑工（YY泵业）', next_date: '2025-03-06' },
      { code: 'EQ204', name: '回流泵#1', location: '回流泵房', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-10', last_operator: '黄工（YY泵业）', next_date: '2025-03-10' },
      { code: 'EQ205', name: '回流泵#2', location: '回流泵房', completed: 1, pending: 1, overdue: 0, rate: 50, last_date: '2024-09-12', last_operator: '黄工（YY泵业）', next_date: '2025-01-12' },
      { code: 'EQ206', name: '污泥泵#1', location: '污泥泵房', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-12', last_operator: '郑工（YY泵业）', next_date: '2025-03-12' },
      { code: 'EQ207', name: '污泥泵#2', location: '污泥泵房', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-13', last_operator: '黄工（YY泵业）', next_date: '2025-03-13' },
      { code: 'EQ208', name: '剩余污泥泵', location: '污泥泵房', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-14', last_operator: '郑工（YY泵业）', next_date: '2025-03-14' },
      { code: 'EQ209', name: '加药泵#1', location: '加药间', completed: 1, pending: 0, overdue: 0, rate: 100, last_date: '2024-11-20', last_operator: '黄工（YY泵业）', next_date: '2025-02-20' },
      { code: 'EQ210', name: '加药泵#2', location: '加药间', completed: 1, pending: 0, overdue: 0, rate: 100, last_date: '2024-11-20', last_operator: '黄工（YY泵业）', next_date: '2025-02-20' },
      { code: 'EQ211', name: 'PAC加药泵', location: '加药间', completed: 1, pending: 0, overdue: 0, rate: 100, last_date: '2024-11-21', last_operator: '郑工（YY泵业）', next_date: '2025-02-21' },
      { code: 'EQ212', name: 'PAM加药泵', location: '加药间', completed: 1, pending: 0, overdue: 0, rate: 100, last_date: '2024-11-21', last_operator: '郑工（YY泵业）', next_date: '2025-02-21' }
    ]
  },
  3: {
    execStats: { planned: 18, completed: 14, pending: 2, overdue: 2, avg_response: '5.6' },
    equipmentList: [
      { code: 'EQ301', name: '厌氧池搅拌机#1', location: '厌氧池', completed: 3, pending: 0, overdue: 1, rate: 75, last_date: '2024-10-28', last_operator: '吴工（ZZ机械）', next_date: '2024-12-28' },
      { code: 'EQ302', name: '厌氧池搅拌机#2', location: '厌氧池', completed: 3, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-15', last_operator: '吴工（ZZ机械）', next_date: '2025-01-15' },
      { code: 'EQ303', name: '缺氧池搅拌机', location: '缺氧池', completed: 3, pending: 0, overdue: 1, rate: 75, last_date: '2024-10-30', last_operator: '马工（ZZ机械）', next_date: '2024-12-30' },
      { code: 'EQ304', name: '好氧池搅拌器A', location: '好氧池', completed: 2, pending: 1, overdue: 0, rate: 66, last_date: '2024-11-25', last_operator: '马工（ZZ机械）', next_date: '2025-01-10' },
      { code: 'EQ305', name: '好氧池搅拌器B', location: '好氧池', completed: 3, pending: 1, overdue: 0, rate: 75, last_date: '2024-12-02', last_operator: '吴工（ZZ机械）', next_date: '2025-01-08' }
    ]
  },
  4: {
    execStats: { planned: 4, completed: 4, pending: 0, overdue: 0, avg_response: '2.8' },
    equipmentList: [
      { code: 'EQ401', name: '污泥脱水机#1', location: '脱水车间', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-01', last_operator: '赵工（XX环保）', next_date: '2025-01-15' },
      { code: 'EQ402', name: '污泥脱水机#2', location: '脱水车间', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-02', last_operator: '钱工（XX环保）', next_date: '2025-01-16' },
      { code: 'EQ403', name: '污泥输送螺旋机', location: '脱水车间', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-03', last_operator: '孙工（XX环保）', next_date: '2025-01-17' }
    ]
  },
  5: {
    execStats: { planned: 12, completed: 8, pending: 2, overdue: 2, avg_response: '6.5' },
    equipmentList: [
      { code: 'EQ501', name: 'PLC控制柜#1', location: '中控室', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-06-15', last_operator: '林工（AA自动化）', next_date: '2025-01-15' },
      { code: 'EQ502', name: 'PLC控制柜#2', location: '中控室', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-06-16', last_operator: '林工（AA自动化）', next_date: '2025-01-16' },
      { code: 'EQ503', name: 'SCADA服务器', location: '中控室', completed: 1, pending: 1, overdue: 0, rate: 50, last_date: '2024-06-20', last_operator: '何工（AA自动化）', next_date: '2025-01-20' },
      { code: 'EQ504', name: '现场远程IO站', location: '各工段', completed: 1, pending: 1, overdue: 1, rate: 33, last_date: '2024-05-10', last_operator: '林工（AA自动化）', next_date: '2024-12-10' },
      { code: 'EQ505', name: '变频器组', location: '各工段', completed: 1, pending: 0, overdue: 1, rate: 50, last_date: '2024-05-15', last_operator: '何工（AA自动化）', next_date: '2024-12-15' }
    ]
  },
  6: {
    execStats: { planned: 6, completed: 6, pending: 0, overdue: 0, avg_response: '22.0' },
    equipmentList: [
      { code: 'EQ601', name: '电磁流量计', location: '各工段（共15台）', completed: 15, pending: 0, overdue: 0, rate: 100, last_date: '2024-11-10', last_operator: '计量院检测组', next_date: '2025-05-10' },
      { code: 'EQ602', name: '液位计', location: '各水池（共20台）', completed: 20, pending: 0, overdue: 0, rate: 100, last_date: '2024-11-12', last_operator: '计量院检测组', next_date: '2025-05-12' },
      { code: 'EQ603', name: '在线COD分析仪', location: '进出口（共2台）', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-11-15', last_operator: '计量院检测组', next_date: '2025-05-15' },
      { code: 'EQ604', name: '在线NH3-N分析仪', location: '进出口（共2台）', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-11-15', last_operator: '计量院检测组', next_date: '2025-05-15' },
      { code: 'EQ605', name: '在线TP分析仪', location: '进出口（共2台）', completed: 2, pending: 0, overdue: 0, rate: 100, last_date: '2024-11-16', last_operator: '计量院检测组', next_date: '2025-05-16' },
      { code: 'EQ606', name: 'pH计', location: '各工艺点（共8台）', completed: 8, pending: 0, overdue: 0, rate: 100, last_date: '2024-11-18', last_operator: '计量院检测组', next_date: '2025-05-18' }
    ]
  },
  7: {
    execStats: { planned: 2, completed: 1, pending: 0, overdue: 1, avg_response: '9.5' },
    equipmentList: [
      { code: 'EQ701', name: '进水电动阀门组', location: '进水泵房（共10台）', completed: 10, pending: 0, overdue: 0, rate: 100, last_date: '2024-05-20', last_operator: '阀门巡检组（BB）', next_date: '2025-05-20' },
      { code: 'EQ702', name: '工艺管线阀门组', location: '各工艺段（共20台）', completed: 15, pending: 0, overdue: 5, rate: 75, last_date: '2024-04-10', last_operator: '阀门巡检组（BB）', next_date: '2024-12-10' },
      { code: 'EQ703', name: '污泥管线阀门', location: '污泥工段（共15台）', completed: 0, pending: 0, overdue: 15, rate: 0, last_date: '-', last_operator: '-', next_date: '2024-11-01' }
    ]
  },
  8: {
    execStats: { planned: 36, completed: 30, pending: 4, overdue: 2, avg_response: '3.8' },
    equipmentList: [
      { code: 'EQ601', name: '加药泵组', location: '加药间', completed: 5, pending: 1, overdue: 0, rate: 83, last_date: '2024-12-10', last_operator: '郑工（YY泵业）', next_date: '2025-01-10' },
      { code: 'EQ602', name: '加药搅拌机', location: '加药间', completed: 5, pending: 1, overdue: 0, rate: 83, last_date: '2024-12-10', last_operator: '黄工（YY泵业）', next_date: '2025-01-10' },
      { code: 'EQ603', name: '加药罐', location: '加药间', completed: 5, pending: 0, overdue: 0, rate: 100, last_date: '2024-12-15', last_operator: '郑工（YY泵业）', next_date: '2025-01-15' },
      { code: 'EQ604', name: '计量泵组', location: '加药间', completed: 5, pending: 1, overdue: 1, rate: 71, last_date: '2024-11-10', last_operator: '黄工（YY泵业）', next_date: '2024-12-25' },
      { code: 'EQ605', name: 'PAM制备系统', location: '加药间', completed: 5, pending: 0, overdue: 1, rate: 83, last_date: '2024-11-05', last_operator: '郑工（YY泵业）', next_date: '2024-12-20' },
      { code: 'EQ606', name: '阀门及管路', location: '加药间', completed: 5, pending: 1, overdue: 0, rate: 83, last_date: '2024-12-20', last_operator: '黄工（YY泵业）', next_date: '2025-01-20' }
    ]
  }
}

const renewHistoryMap: Record<number, any[]> = {
  1: [
    { renew_no: 'XQ2025001', start_date: '2025-01-01', end_date: '2025-12-31', amount: 120000, sign_date: '2024-12-20', operator: '李四', remark: '首次续签，合同金额上浮3%' },
    { renew_no: 'XQ2024001', start_date: '2024-01-01', end_date: '2024-12-31', amount: 116500, sign_date: '2023-12-18', operator: '王五', remark: '原始合同签订' }
  ],
  3: [
    { renew_no: 'XQ2024003', start_date: '2024-07-01', end_date: '2025-06-30', amount: 98000, sign_date: '2024-06-15', operator: '赵六', remark: '续签，服务内容补充' }
  ],
  5: [
    { renew_no: 'XQ2024005', start_date: '2024-01-01', end_date: '2025-01-15', amount: 156000, sign_date: '2023-12-28', operator: '钱七', remark: '年度续签，供应商资质需复核' }
  ]
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
      },
      4: {
        id: 4, contract_no: 'WB2023076', contract_name: '污泥脱水机维保合同',
        supplier_id: 1, supplier_name: 'XX环保设备有限公司',
        amount: 72000, start_date: '2023-09-10', end_date: '2025-09-09',
        service_frequency: 'biweekly', response_time: 3, equipment_count: 3,
        terms_summary: '两周一次保养，3小时到场响应。',
        service_scope: '污泥脱水机及输送设备每两周一次的例行保养、易损件检查更换、故障维修等。'
      },
      5: {
        id: 5, contract_no: 'WB2022110', contract_name: '电气控制系统维保合同',
        supplier_id: 4, supplier_name: 'AA自动化科技公司',
        amount: 156000, start_date: '2023-01-01', end_date: '2025-01-15',
        service_frequency: 'semiyearly', response_time: 2, equipment_count: 20,
        terms_summary: '每半年系统巡检，紧急故障2小时到场。',
        service_scope: 'PLC、SCADA系统、变频器、远程IO站等电气控制系统的半年巡检和故障维修。'
      },
      6: {
        id: 6, contract_no: 'WB2024015', contract_name: '加药系统维保合同',
        supplier_id: 2, supplier_name: 'YY泵业技术服务公司',
        amount: 45000, start_date: '2024-06-01', end_date: '2026-05-31',
        service_frequency: 'monthly', response_time: 4, equipment_count: 6,
        terms_summary: '月度巡检保养，4小时响应。',
        service_scope: '加药泵、加药搅拌机、计量泵、加药罐等设备月度保养及维修。'
      },
      7: {
        id: 7, contract_no: 'WB2023122', contract_name: '阀门组年度维保合同',
        supplier_id: 5, supplier_name: 'BB阀门技术服务部',
        amount: 38000, start_date: '2023-11-01', end_date: '2025-10-31',
        service_frequency: 'yearly', response_time: 8, equipment_count: 45,
        terms_summary: '年度阀门检测，8小时到场响应。',
        service_scope: '全厂工艺管线、加药管线、污泥管线共45台阀门的年度检测、保养与维修。'
      },
      8: {
        id: 8, contract_no: 'WB2024003', contract_name: '仪表设备校准维保合同',
        supplier_id: 6, supplier_name: 'CC计量检测研究院',
        amount: 68000, start_date: '2024-02-01', end_date: '2026-01-31',
        service_frequency: 'quarterly', response_time: 24, equipment_count: 60,
        terms_summary: '每季度定期校准，24小时内响应。',
        service_scope: '全厂60台在线仪表（流量计、液位计、COD/氨氮/总磷分析仪、pH计等）的季度校准与维修。'
      }
    }

    const baseContract = contractMap[id] || contractMap[1]
    contract.value = {
      ...baseContract,
      status: calcStatus(baseContract.start_date, baseContract.end_date),
      progress: calcProgress(baseContract.start_date, baseContract.end_date)
    }

    const supplier = supplierMap[baseContract.supplier_id] || supplierMap[1]
    supplierInfo.value = { ...supplier }

    const execData = contractExecData[id] || contractExecData[1]
    execStats.value = { ...execData.execStats }
    equipmentExecList.value = [...execData.equipmentList]

    renewHistory.value = renewHistoryMap[id] || []
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

const callPhone = (phone: string) => {
  window.location.href = `tel:${phone}`
}

const sendEmail = (email: string) => {
  window.location.href = `mailto:${email}`
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
.contact-name {
  font-weight: 600;
  color: #1d2129;
  font-size: 14px;
}
.phone-link,
.email-link {
  padding: 0 !important;
  height: auto !important;
  color: #165DFF !important;
  font-size: 13px;
}
.phone-link:hover,
.email-link:hover {
  color: #0E42D2 !important;
  text-decoration: underline;
}
.supplier-card {
  background: linear-gradient(135deg, #F0F7FF 0%, #FFFFFF 100%);
}
</style>
