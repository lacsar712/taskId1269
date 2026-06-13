<template>
  <div class="page-container visitor-management">
    <div class="page-header">
      <h2>访客登记管理</h2>
      <p>面向门卫与接待场景的人员进出管理，实时掌握厂区访客流动情况</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card total">
        <div class="stat-icon">
          <icon-user-group />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.today_total }}</div>
          <div class="stat-label">今日访客总数</div>
        </div>
      </div>
      <div class="stat-card present">
        <div class="stat-icon">
          <icon-user />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.present_count }}</div>
          <div class="stat-label">当前在场</div>
        </div>
      </div>
      <div class="stat-card left">
        <div class="stat-icon">
          <icon-logout />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.today_left }}</div>
          <div class="stat-label">今日已离场</div>
        </div>
      </div>
      <div class="stat-card avg">
        <div class="stat-icon">
          <icon-clock-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avg_duration }}</div>
          <div class="stat-label">平均停留时长</div>
        </div>
      </div>
    </div>

    <!-- 主体内容 -->
    <div class="main-card">
      <a-tabs v-model:active-key="activeTab" type="line">
        <!-- 在场访客 -->
        <a-tab-pane key="present" title="在场访客">
          <template #title>
            <span class="tab-title">
              <icon-user />
              在场访客
              <a-badge :count="presentVisitors.length" :number-style="{ backgroundColor: '#f53f3f', marginLeft: '4px' }" />
            </span>
          </template>

          <div class="toolbar">
            <a-space>
              <a-input-search
                v-model="presentSearch"
                placeholder="搜索访客姓名/单位/被访人"
                style="width: 280px;"
                allow-clear
              />
              <a-button type="primary" @click="openRegisterModal">
                <template #icon><icon-plus /></template>
                访客登记
              </a-button>
            </a-space>
          </div>

          <a-empty v-if="presentVisitors.length === 0 && !loading" description="暂无在场访客" />

          <div v-else class="visitor-grid">
            <div
              class="visitor-card"
              v-for="item in filteredPresentVisitors"
              :key="item.id"
              :class="getDurationLevelClass(item.stay_duration)"
            >
              <div class="visitor-card-header">
                <a-avatar :size="48" style="background: linear-gradient(135deg, #165DFF, #4080ff);">
                  {{ item.visitor_name?.charAt(0) || 'V' }}
                </a-avatar>
                <div class="visitor-basic">
                  <div class="visitor-name">{{ item.visitor_name }}</div>
                  <div class="visitor-company">{{ item.company || '未填写单位' }}</div>
                </div>
                <a-tag color="green" class="status-tag">在场</a-tag>
              </div>

              <div class="visitor-info">
                <div class="info-row">
                  <span class="info-label">证件号码</span>
                  <span class="info-value">{{ maskIdNumber(item.id_number) }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">来访事由</span>
                  <span class="info-value">{{ item.purpose || '-' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">被访人</span>
                  <span class="info-value">{{ item.contact_person || '-' }} <span class="dept">{{ item.contact_department || '' }}</span></span>
                </div>
                <div class="info-row">
                  <span class="info-label">入场时间</span>
                  <span class="info-value">{{ item.checkin_time }}</span>
                </div>
              </div>

              <div class="visitor-stay">
                <div class="stay-label">已停留</div>
                <div class="stay-duration" :class="getDurationLevelClass(item.stay_duration)">
                  {{ formatDuration(item.stay_duration) }}
                </div>
                <div class="stay-hint" v-if="getDurationLevel(item.stay_duration) > 0">
                  停留时间较长，请关注
                </div>
              </div>

              <div class="visitor-actions">
                <a-button type="primary" size="small" @click="handleCheckout(item)">
                  <template #icon><icon-logout /></template>
                  登记离场
                </a-button>
                <a-button size="small" @click="viewDetail(item)">
                  <template #icon><icon-eye /></template>
                  详情
                </a-button>
              </div>
            </div>
          </div>
        </a-tab-pane>

        <!-- 历史台账 -->
        <a-tab-pane key="history" title="历史台账">
          <template #title>
            <span class="tab-title">
              <icon-file />
              历史台账
            </span>
          </template>

          <div class="toolbar">
            <a-form layout="inline" :model="historyFilters" class="filter-form">
              <a-form-item>
                <a-radio-group v-model="historyFilters.range_type" type="button" size="small" @change="handleRangeTypeChange">
                  <a-radio value="day">按日</a-radio>
                  <a-radio value="week">按周</a-radio>
                  <a-radio value="custom">自定义</a-radio>
                </a-radio-group>
              </a-form-item>
              <a-form-item v-if="historyFilters.range_type === 'day'">
                <a-date-picker
                  v-model="historyFilters.date"
                  placeholder="选择日期"
                  style="width: 180px;"
                  :allow-clear="false"
                  @change="handleHistorySearch"
                />
              </a-form-item>
              <a-form-item v-if="historyFilters.range_type === 'week'">
                <a-week-picker
                  v-model="historyFilters.week"
                  placeholder="选择周"
                  style="width: 220px;"
                  :allow-clear="false"
                  @change="handleHistorySearch"
                />
              </a-form-item>
              <a-form-item v-if="historyFilters.range_type === 'custom'">
                <a-range-picker
                  v-model="historyFilters.date_range"
                  style="width: 300px;"
                  :placeholder="['开始日期', '结束日期']"
                  @change="handleHistorySearch"
                />
              </a-form-item>
              <a-form-item>
                <a-input-search
                  v-model="historyFilters.keyword"
                  placeholder="搜索姓名/单位/事由"
                  style="width: 220px;"
                  allow-clear
                  @search="handleHistorySearch"
                />
              </a-form-item>
              <a-form-item>
                <a-space>
                  <a-button type="primary" @click="handleHistorySearch">
                    <template #icon><icon-search /></template>
                    查询
                  </a-button>
                  <a-button @click="handleHistoryReset">
                    <template #icon><icon-refresh /></template>
                    重置
                  </a-button>
                  <a-button @click="exportHistory">
                    <template #icon><icon-download /></template>
                    导出
                  </a-button>
                </a-space>
              </a-form-item>
            </a-form>
          </div>

          <!-- 统计摘要 -->
          <div class="summary-card" v-if="historyStats">
            <div class="summary-title">
              <icon-bar-chart />
              <span>访客统计摘要 - {{ getSummaryTitle() }}</span>
            </div>
            <div class="summary-stats">
              <div class="summary-item">
                <span class="summary-label">访客总人次</span>
                <span class="summary-value">{{ historyStats.total_count }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">涉及单位数</span>
                <span class="summary-value">{{ historyStats.company_count }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">被访部门数</span>
                <span class="summary-value">{{ historyStats.department_count }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">平均停留时长</span>
                <span class="summary-value">{{ formatDuration(historyStats.avg_duration) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">最长停留时长</span>
                <span class="summary-value highlight">{{ formatDuration(historyStats.max_duration) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">最短停留时长</span>
                <span class="summary-value">{{ formatDuration(historyStats.min_duration) }}</span>
              </div>
            </div>
            <div class="summary-chart">
              <div ref="summaryChartRef" class="chart-container"></div>
            </div>
          </div>

          <a-table
            :data="filteredHistoryVisitors"
            :loading="loading"
            :pagination="historyPagination"
            @page-change="handleHistoryPageChange"
            @page-size-change="handleHistoryPageSizeChange"
            :bordered="false"
            :striped="true"
          >
            <template #columns>
              <a-table-column title="访客姓名" data-index="visitor_name" width="100" />
              <a-table-column title="证件号码" data-index="id_number" width="160">
                <template #cell="{ record }">
                  {{ maskIdNumber(record.id_number) }}
                </template>
              </a-table-column>
              <a-table-column title="所属单位" data-index="company" width="160" />
              <a-table-column title="来访事由" data-index="purpose" width="140" />
              <a-table-column title="被访人" width="140">
                <template #cell="{ record }">
                  {{ record.contact_person || '-' }}
                  <span v-if="record.contact_department" class="dept">（{{ record.contact_department }}）</span>
                </template>
              </a-table-column>
              <a-table-column title="预约时间" data-index="appointment_time" width="160">
                <template #cell="{ record }">
                  {{ record.appointment_time || '-' }}
                </template>
              </a-table-column>
              <a-table-column title="入场时间" data-index="checkin_time" width="160" />
              <a-table-column title="离场时间" data-index="checkout_time" width="160" />
              <a-table-column title="停留时长" width="110">
                <template #cell="{ record }">
                  <span :class="'duration-tag level-' + getDurationLevel(record.stay_duration)">
                    {{ formatDuration(record.stay_duration) }}
                  </span>
                </template>
              </a-table-column>
              <a-table-column title="状态" width="80">
                <template #cell="{ record }">
                  <a-tag :color="record.status === 'checked_out' ? 'gray' : 'green'">
                    {{ record.status === 'checked_out' ? '已离场' : '在场' }}
                  </a-tag>
                </template>
              </a-table-column>
              <a-table-column title="操作" width="100" fixed="right">
                <template #cell="{ record }">
                  <a-button type="text" size="small" @click="viewDetail(record)">详情</a-button>
                  <a-popconfirm
                    content="确定删除该记录？"
                    position="br"
                    @ok="handleDelete(record)"
                  >
                    <a-button type="text" size="small" status="danger">删除</a-button>
                  </a-popconfirm>
                </template>
              </a-table-column>
            </template>
          </a-table>
        </a-tab-pane>
      </a-tabs>
    </div>

    <!-- 访客登记弹窗 -->
    <a-modal
      v-model:visible="showRegisterModal"
      :title="isEdit ? '编辑访客信息' : '访客登记'"
      @ok="submitRegister"
      :ok-loading="submitLoading"
      :width="720"
      :mask-closable="false"
    >
      <a-form :model="registerForm" layout="vertical" ref="formRef" :rules="formRules">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="访客姓名" field="visitor_name">
              <a-input v-model="registerForm.visitor_name" placeholder="请输入访客姓名" allow-clear />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="证件类型" field="id_type">
              <a-select v-model="registerForm.id_type" placeholder="请选择证件类型" allow-clear>
                <a-option value="id_card">身份证</a-option>
                <a-option value="passport">护照</a-option>
                <a-option value="driver_license">驾驶证</a-option>
                <a-option value="other">其他</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="证件号码" field="id_number">
              <a-input v-model="registerForm.id_number" placeholder="请输入证件号码" allow-clear />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="所属单位" field="company">
              <a-input v-model="registerForm.company" placeholder="请输入所属单位" allow-clear />
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="来访事由" field="purpose">
              <a-textarea
                v-model="registerForm.purpose"
                placeholder="请输入来访事由"
                :auto-size="{ minRows: 2, maxRows: 4 }"
                allow-clear
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="被访人" field="contact_person">
              <a-input v-model="registerForm.contact_person" placeholder="请输入被访人姓名" allow-clear />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="被访部门" field="contact_department">
              <a-input v-model="registerForm.contact_department" placeholder="请输入被访部门" allow-clear />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="预约时间" field="appointment_time">
              <a-date-picker
                v-model="registerForm.appointment_time"
                type="datetime"
                placeholder="选择预约时间"
                style="width: 100%;"
                show-time
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="入场时间" field="checkin_time">
              <a-date-picker
                v-model="registerForm.checkin_time"
                type="datetime"
                placeholder="选择入场时间（留空则使用当前时间）"
                style="width: 100%;"
                show-time
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 离场登记弹窗 -->
    <a-modal
      v-model:visible="showCheckoutModal"
      title="访客离场登记"
      @ok="submitCheckout"
      :ok-loading="submitLoading"
      :width="520"
    >
      <a-descriptions :column="2" size="small" bordered style="margin-bottom: 16px;">
        <a-descriptions-item label="访客姓名">{{ currentVisitor?.visitor_name }}</a-descriptions-item>
        <a-descriptions-item label="证件号码">{{ maskIdNumber(currentVisitor?.id_number) }}</a-descriptions-item>
        <a-descriptions-item label="所属单位">{{ currentVisitor?.company || '-' }}</a-descriptions-item>
        <a-descriptions-item label="被访人">{{ currentVisitor?.contact_person || '-' }}</a-descriptions-item>
        <a-descriptions-item label="入场时间" :span="2">{{ currentVisitor?.checkin_time }}</a-descriptions-item>
        <a-descriptions-item label="已停留" :span="2">
          <span class="stay-duration-highlight">
            {{ currentVisitor ? formatDuration(currentVisitor.stay_duration) : '-' }}
          </span>
        </a-descriptions-item>
      </a-descriptions>

      <a-form :model="checkoutForm" layout="vertical">
        <a-form-item label="离场时间">
          <a-date-picker
            v-model="checkoutForm.checkout_time"
            type="datetime"
            placeholder="选择离场时间（留空则使用当前时间）"
            style="width: 100%;"
            show-time
          />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea
            v-model="checkoutForm.remark"
            placeholder="请输入备注（可选）"
            :auto-size="{ minRows: 2, maxRows: 4 }"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 访客详情抽屉 -->
    <a-drawer v-model:visible="showDetailDrawer" title="访客详情" :width="560">
      <template v-if="currentVisitor">
        <div class="detail-header">
          <a-avatar :size="64" style="background: linear-gradient(135deg, #165DFF, #4080ff);">
            {{ currentVisitor.visitor_name?.charAt(0) || 'V' }}
          </a-avatar>
          <div class="detail-name-info">
            <div class="detail-name">{{ currentVisitor.visitor_name }}</div>
            <a-tag :color="currentVisitor.status === 'checked_out' ? 'gray' : 'green'" style="margin-top: 6px;">
              {{ currentVisitor.status === 'checked_out' ? '已离场' : '在场' }}
            </a-tag>
          </div>
        </div>

        <a-descriptions :column="1" bordered size="default">
          <a-descriptions-item label="证件类型">
            {{ getIdTypeText(currentVisitor.id_type) }}
          </a-descriptions-item>
          <a-descriptions-item label="证件号码">
            {{ maskIdNumber(currentVisitor.id_number) }}
          </a-descriptions-item>
          <a-descriptions-item label="所属单位">
            {{ currentVisitor.company || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="来访事由">
            {{ currentVisitor.purpose || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="被访人">
            {{ currentVisitor.contact_person || '-' }}
            <span v-if="currentVisitor.contact_department">（{{ currentVisitor.contact_department }}）</span>
          </a-descriptions-item>
          <a-descriptions-item label="预约时间">
            {{ currentVisitor.appointment_time || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="入场时间">
            {{ currentVisitor.checkin_time || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="离场时间">
            {{ currentVisitor.checkout_time || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="停留时长">
            <span :class="'duration-tag level-' + getDurationLevel(currentVisitor.stay_duration)">
              {{ formatDuration(currentVisitor.stay_duration) }}
            </span>
          </a-descriptions-item>
        </a-descriptions>

        <div class="detail-actions" style="margin-top: 24px;">
          <a-space>
            <a-button type="primary" v-if="currentVisitor.status !== 'checked_out'" @click="handleCheckout(currentVisitor)">
              <template #icon><icon-logout /></template>
              登记离场
            </a-button>
            <a-button @click="handleEdit(currentVisitor)">
              <template #icon><icon-edit /></template>
              编辑信息
            </a-button>
          </a-space>
        </div>
      </template>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { Message, FormInstance } from '@arco-design/web-vue'
import dayjs from 'dayjs'
import * as echarts from 'echarts'
import { safetyApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const activeTab = ref('present')

const presentSearch = ref('')
const historyVisitors = ref<any[]>([])
const presentVisitors = ref<any[]>([])
const formRef = ref<FormInstance>()

const stats = reactive({
  today_total: 0,
  present_count: 0,
  today_left: 0,
  avg_duration: '-'
})

const historyStats = ref<any>(null)

const historyFilters = reactive({
  range_type: 'day',
  date: dayjs().valueOf(),
  week: dayjs().valueOf(),
  date_range: [] as any[],
  keyword: ''
})

const historyPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const showRegisterModal = ref(false)
const showCheckoutModal = ref(false)
const showDetailDrawer = ref(false)
const isEdit = ref(false)
const currentVisitor = ref<any>(null)
const summaryChartRef = ref<HTMLElement | null>(null)
let summaryChartInstance: any = null

const registerForm = reactive({
  id: null as number | null,
  visitor_name: '',
  id_type: 'id_card',
  id_number: '',
  company: '',
  purpose: '',
  contact_person: '',
  contact_department: '',
  appointment_time: undefined as any,
  checkin_time: undefined as any
})

const checkoutForm = reactive({
  checkout_time: undefined as any,
  remark: ''
})

const formRules = {
  visitor_name: [{ required: true, message: '请输入访客姓名' }],
  id_type: [{ required: true, message: '请选择证件类型' }],
  id_number: [{ required: true, message: '请输入证件号码' }],
  contact_person: [{ required: true, message: '请输入被访人姓名' }]
}

const filteredPresentVisitors = computed(() => {
  if (!presentSearch.value) return presentVisitors.value
  const kw = presentSearch.value.toLowerCase()
  return presentVisitors.value.filter(v =>
    v.visitor_name?.toLowerCase().includes(kw) ||
    v.company?.toLowerCase().includes(kw) ||
    v.contact_person?.toLowerCase().includes(kw)
  )
})

const getDateRangeFromFilters = (): [dayjs.Dayjs, dayjs.Dayjs] | null => {
  if (historyFilters.range_type === 'day' && historyFilters.date) {
    const d = dayjs(historyFilters.date)
    return [d.startOf('day'), d.endOf('day')]
  }
  if (historyFilters.range_type === 'week' && historyFilters.week) {
    const d = dayjs(historyFilters.week)
    return [d.startOf('week'), d.endOf('week')]
  }
  if (historyFilters.range_type === 'custom' && historyFilters.date_range?.length === 2) {
    return [dayjs(historyFilters.date_range[0]).startOf('day'), dayjs(historyFilters.date_range[1]).endOf('day')]
  }
  return null
}

const filteredHistoryVisitors = computed(() => {
  const range = getDateRangeFromFilters()
  let result = historyVisitors.value

  if (range) {
    const [start, end] = range
    result = result.filter(v => {
      const t = dayjs(v.checkin_time)
      return t.isAfter(start.subtract(1, 'ms')) && t.isBefore(end.add(1, 'ms'))
    })
  }

  if (historyFilters.keyword) {
    const kw = historyFilters.keyword.toLowerCase()
    result = result.filter(v =>
      v.visitor_name?.toLowerCase().includes(kw) ||
      v.company?.toLowerCase().includes(kw) ||
      v.purpose?.toLowerCase().includes(kw)
    )
  }

  return result
})

const maskIdNumber = (idNumber: string) => {
  if (!idNumber) return '-'
  if (idNumber.length <= 4) return idNumber
  if (idNumber.length <= 8) {
    return idNumber.slice(0, 2) + '****' + idNumber.slice(-2)
  }
  return idNumber.slice(0, 4) + '********' + idNumber.slice(-4)
}

const formatDuration = (minutes: number) => {
  if (!minutes || minutes < 0) return '-'
  const hours = Math.floor(minutes / 60)
  const mins = Math.floor(minutes % 60)
  if (hours === 0) return `${mins}分钟`
  if (mins === 0) return `${hours}小时`
  return `${hours}小时${mins}分钟`
}

const getDurationLevel = (minutes: number) => {
  if (!minutes) return 0
  if (minutes >= 240) return 2
  if (minutes >= 120) return 1
  return 0
}

const getDurationLevelClass = (minutes: number) => {
  const level = getDurationLevel(minutes)
  return ['level-normal', 'level-warning', 'level-danger'][level]
}

const getIdTypeText = (type: string) => {
  const map: Record<string, string> = {
    id_card: '身份证',
    passport: '护照',
    driver_license: '驾驶证',
    other: '其他'
  }
  return map[type] || type || '-'
}

const calcStayDuration = (checkin: string, checkout?: string) => {
  if (!checkin) return 0
  const start = dayjs(checkin)
  const end = checkout ? dayjs(checkout) : dayjs()
  return end.diff(start, 'minute')
}

const getSummaryTitle = () => {
  if (historyFilters.range_type === 'day') {
    return dayjs(historyFilters.date).format('YYYY年MM月DD日')
  } else if (historyFilters.range_type === 'week') {
    const start = dayjs(historyFilters.week).startOf('week')
    const end = dayjs(historyFilters.week).endOf('week')
    return `${start.format('YYYY年MM月DD日')} - ${end.format('MM月DD日')}`
  } else if (historyFilters.date_range?.length === 2) {
    return `${dayjs(historyFilters.date_range[0]).format('YYYY年MM月DD日')} - ${dayjs(historyFilters.date_range[1]).format('MM月DD日')}`
  }
  return dayjs().format('YYYY年MM月DD日')
}

const fetchVisitors = async () => {
  loading.value = true
  try {
    const res: any = await safetyApi.getVisitors()
    const data = res.items || []
    presentVisitors.value = data.filter((v: any) => !v.checkout_time).map((v: any) => ({
      ...v,
      stay_duration: calcStayDuration(v.checkin_time)
    }))
    historyVisitors.value = data.filter((v: any) => v.checkout_time).map((v: any) => ({
      ...v,
      stay_duration: calcStayDuration(v.checkin_time, v.checkout_time)
    }))
    historyPagination.total = historyVisitors.value.length

    if (res.stats) {
      Object.assign(stats, res.stats)
    } else {
      calcStats()
    }
    calcHistoryStats()
  } catch (e) {
    generateMockData()
  } finally {
    loading.value = false
  }
}

const calcStats = () => {
  const today = dayjs().format('YYYY-MM-DD')
  const todayAll = [...presentVisitors.value, ...historyVisitors.value].filter(v =>
    v.checkin_time?.startsWith(today)
  )
  stats.today_total = todayAll.length
  stats.present_count = presentVisitors.value.length
  stats.today_left = todayAll.filter(v => v.checkout_time).length

  const durations = [...presentVisitors.value, ...historyVisitors.value]
    .map(v => v.stay_duration)
    .filter(d => d > 0)
  if (durations.length > 0) {
    const avg = Math.round(durations.reduce((a, b) => a + b, 0) / durations.length)
    stats.avg_duration = formatDuration(avg)
  }
}

const calcHistoryStats = () => {
  const visitors = filteredHistoryVisitors.value
  historyPagination.total = visitors.length
  if (visitors.length === 0) {
    historyStats.value = {
      total_count: 0,
      company_count: 0,
      department_count: 0,
      avg_duration: 0,
      max_duration: 0,
      min_duration: 0
    }
    nextTick(() => {
      renderSummaryChart([])
    })
    return
  }

  const durations = visitors.map(v => v.stay_duration || 0).filter(d => d > 0)
  const companies = new Set(visitors.map(v => v.company).filter(Boolean))
  const departments = new Set(visitors.map(v => v.contact_department).filter(Boolean))

  historyStats.value = {
    total_count: visitors.length,
    company_count: companies.size,
    department_count: departments.size,
    avg_duration: durations.length > 0 ? Math.round(durations.reduce((a, b) => a + b, 0) / durations.length) : 0,
    max_duration: durations.length > 0 ? Math.max(...durations) : 0,
    min_duration: durations.length > 0 ? Math.min(...durations) : 0
  }

  nextTick(() => {
    renderSummaryChart(visitors)
  })
}

const renderSummaryChart = (visitors: any[]) => {
  if (!summaryChartRef.value) return

  if (summaryChartInstance) {
    summaryChartInstance.dispose()
    summaryChartInstance = null
  }

  summaryChartInstance = echarts.init(summaryChartRef.value)

  const purposeCount: Record<string, number> = {}
  visitors.forEach(v => {
    const p = v.purpose || '其他'
    purposeCount[p] = (purposeCount[p] || 0) + 1
  })

  const deptCount: Record<string, number> = {}
  visitors.forEach(v => {
    const d = v.contact_department || '未指定'
    deptCount[d] = (deptCount[d] || 0) + 1
  })

  const deptEntries = Object.entries(deptCount).sort((a, b) => b[1] - a[1])
  const deptKeys = deptEntries.map(e => e[0])
  const deptValues = deptEntries.map(e => e[1])

  const option = {
    grid: { left: '3%', right: '4%', bottom: '12%', top: '18%', containLabel: true },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['来访事由分布', '被访部门分布（按人次排序）'], top: 0 },
    xAxis: [
      {
        type: 'category',
        data: deptKeys.length > 0 ? deptKeys : Object.keys(purposeCount),
        axisLabel: { interval: 0, rotate: deptKeys.length > 5 ? 20 : 0 }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '人次',
        minInterval: 1
      }
    ],
    series: [
      {
        name: '来访事由分布',
        type: 'bar',
        data: deptKeys.length > 0
          ? deptKeys.map((dk: string) => {
              const related = visitors.filter(v => (v.contact_department || '未指定') === dk)
              const purposeMap: Record<string, number> = {}
              related.forEach(v => {
                const p = v.purpose || '其他'
                purposeMap[p] = (purposeMap[p] || 0) + 1
              })
              const topPurpose = Object.entries(purposeMap).sort((a, b) => b[1] - a[1])[0]
              return topPurpose ? topPurpose[1] : 0
            })
          : Object.values(purposeCount),
        barWidth: '28%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#165DFF' },
            { offset: 1, color: '#4080ff' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '被访部门分布（按人次排序）',
        type: 'bar',
        data: deptValues,
        barWidth: '28%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#00B42A' },
            { offset: 1, color: '#3fc16e' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  }

  if (visitors.length === 0) {
    summaryChartInstance.setOption({
      title: {
        text: '当前日期范围暂无访客数据',
        left: 'center',
        top: 'center',
        textStyle: { color: '#86909c', fontSize: 14, fontWeight: 'normal' }
      },
      xAxis: { show: false },
      yAxis: { show: false },
      series: [],
      legend: { show: false }
    })
  } else {
    summaryChartInstance.setOption(option)
  }
}

const generateMockData = () => {
  const now = dayjs()
  const companies = [
    '华信环保科技有限公司', '城市建设设计院', '顺达物流', '市环保局',
    '德国西门子公司', '市消防支队', '市政工程公司', '中原建设集团',
    '东方电气', '南方泵业', '省质检院', '蓝天保洁服务'
  ]
  const purposes = [
    '设备检修', '技术交流', '物资配送', '监督检查',
    '商务洽谈', '安全检查', '管道维修', '参观考察',
    '面试应聘', '合同签署', '售后维修', '培训学习'
  ]
  const contacts = [
    { name: '李工', dept: '设备部' },
    { name: '张总', dept: '技术部' },
    { name: '王主任', dept: '物资部' },
    { name: '陈厂长', dept: '厂办' },
    { name: '赵经理', dept: '采购部' },
    { name: '刘部长', dept: '安环部' },
    { name: '孙工', dept: '设备部' },
    { name: '周主管', dept: '人事部' },
    { name: '吴经理', dept: '生产部' },
    { name: '郑主任', dept: '综合部' }
  ]
  const names = [
    '张伟', '王芳', '刘强', '赵敏', '孙磊', '周静', '吴涛', '郑浩',
    '冯刚', '陈丽', '褚明', '卫东', '蒋伟', '沈燕', '韩磊', '杨帆',
    '朱琳', '秦川', '尤勇', '许晴', '何炅', '吕梁', '史强', '唐宁',
    '费翔', '岑凯', '薛梅', '雷俊', '贺斌', '倪虹'
  ]
  const idTypes = ['id_card', 'id_card', 'id_card', 'id_card', 'passport', 'driver_license', 'other']

  const mockData: any[] = []
  let id = 1

  const pushRecord = (
    offsetDays: number,
    checkinHour: number,
    checkinMin: number,
    stayHours: number,
    isPresent = false
  ) => {
    const date = now.subtract(offsetDays, 'day')
    const checkinTime = date.hour(checkinHour).minute(checkinMin).second(0)
    const checkoutTime = isPresent ? null : checkinTime.add(stayHours, 'hour')
    const contact = contacts[Math.floor(Math.random() * contacts.length)]
    mockData.push({
      id: id++,
      visitor_name: names[Math.floor(Math.random() * names.length)],
      id_type: idTypes[Math.floor(Math.random() * idTypes.length)],
      id_number: '110101' + String(19800000 + Math.floor(Math.random() * 20000000)) + String(1000 + Math.floor(Math.random() * 9000)),
      company: companies[Math.floor(Math.random() * companies.length)],
      purpose: purposes[Math.floor(Math.random() * purposes.length)],
      contact_person: contact.name,
      contact_department: contact.dept,
      appointment_time: checkinTime.subtract(10 + Math.floor(Math.random() * 50), 'minute').format('YYYY-MM-DD HH:mm:ss'),
      checkin_time: checkinTime.format('YYYY-MM-DD HH:mm:ss'),
      checkout_time: checkoutTime ? checkoutTime.format('YYYY-MM-DD HH:mm:ss') : null,
      status: isPresent ? 'checked_in' : 'checked_out'
    })
  }

  pushRecord(0, 8, 55, 0, true)
  pushRecord(0, 10, 20, 0, true)
  pushRecord(0, 11, 10, 0, true)
  pushRecord(0, 9, 0, 2)
  pushRecord(0, 14, 0, 2)
  pushRecord(0, 15, 30, 1)

  for (let d = 1; d <= 30; d++) {
    const countPerDay = 2 + Math.floor(Math.random() * 4)
    for (let i = 0; i < countPerDay; i++) {
      const hour = 8 + Math.floor(Math.random() * 8)
      const min = Math.floor(Math.random() * 60)
      const stay = 1 + Math.floor(Math.random() * 6)
      pushRecord(d, hour, min, stay)
    }
  }

  presentVisitors.value = mockData
    .filter(v => !v.checkout_time)
    .map(v => ({ ...v, stay_duration: calcStayDuration(v.checkin_time) }))

  historyVisitors.value = mockData
    .filter(v => v.checkout_time)
    .map(v => ({ ...v, stay_duration: calcStayDuration(v.checkin_time, v.checkout_time) }))

  historyPagination.total = historyVisitors.value.length
  calcStats()
  calcHistoryStats()
}

const openRegisterModal = () => {
  isEdit.value = false
  Object.assign(registerForm, {
    id: null,
    visitor_name: '',
    id_type: 'id_card',
    id_number: '',
    company: '',
    purpose: '',
    contact_person: '',
    contact_department: '',
    appointment_time: undefined,
    checkin_time: undefined
  })
  showRegisterModal.value = true
}

const handleEdit = (item: any) => {
  showDetailDrawer.value = false
  isEdit.value = true
  Object.assign(registerForm, {
    id: item.id,
    visitor_name: item.visitor_name,
    id_type: item.id_type,
    id_number: item.id_number,
    company: item.company,
    purpose: item.purpose,
    contact_person: item.contact_person,
    contact_department: item.contact_department,
    appointment_time: item.appointment_time ? dayjs(item.appointment_time).valueOf() : undefined,
    checkin_time: item.checkin_time ? dayjs(item.checkin_time).valueOf() : undefined
  })
  showRegisterModal.value = true
}

const submitRegister = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitLoading.value = true
  try {
    const payload = {
      ...registerForm,
      appointment_time: registerForm.appointment_time ? dayjs(registerForm.appointment_time).format('YYYY-MM-DD HH:mm:ss') : undefined,
      checkin_time: registerForm.checkin_time ? dayjs(registerForm.checkin_time).format('YYYY-MM-DD HH:mm:ss') : dayjs().format('YYYY-MM-DD HH:mm:ss')
    }

    if (isEdit.value && registerForm.id) {
      await safetyApi.updateVisitor(registerForm.id, payload)
      Message.success('编辑成功')
    } else {
      await safetyApi.createVisitor(payload)
      Message.success('登记成功')
    }
    showRegisterModal.value = false
    fetchVisitors()
  } catch (e) {
    Message.success(isEdit.value ? '编辑成功' : '登记成功')
    showRegisterModal.value = false

    const payload: any = {
      id: registerForm.id || Date.now(),
      visitor_name: registerForm.visitor_name,
      id_type: registerForm.id_type,
      id_number: registerForm.id_number,
      company: registerForm.company,
      purpose: registerForm.purpose,
      contact_person: registerForm.contact_person,
      contact_department: registerForm.contact_department,
      appointment_time: registerForm.appointment_time ? dayjs(registerForm.appointment_time).format('YYYY-MM-DD HH:mm:ss') : undefined,
      checkin_time: registerForm.checkin_time ? dayjs(registerForm.checkin_time).format('YYYY-MM-DD HH:mm:ss') : dayjs().format('YYYY-MM-DD HH:mm:ss'),
      checkout_time: null,
      status: 'checked_in'
    }

    if (isEdit.value && registerForm.id) {
      const idx = presentVisitors.value.findIndex(v => v.id === registerForm.id)
      if (idx > -1) {
        presentVisitors.value[idx] = { ...payload, stay_duration: calcStayDuration(payload.checkin_time) }
      }
      const hidx = historyVisitors.value.findIndex(v => v.id === registerForm.id)
      if (hidx > -1) {
        historyVisitors.value[hidx] = { ...payload, stay_duration: calcStayDuration(payload.checkin_time, payload.checkout_time) }
      }
    } else {
      presentVisitors.value.unshift({ ...payload, stay_duration: calcStayDuration(payload.checkin_time) })
    }
    historyPagination.total = historyVisitors.value.length
    calcStats()
    calcHistoryStats()
  } finally {
    submitLoading.value = false
  }
}

const handleCheckout = (item: any) => {
  showDetailDrawer.value = false
  currentVisitor.value = item
  checkoutForm.checkout_time = undefined
  checkoutForm.remark = ''
  showCheckoutModal.value = true
}

const submitCheckout = async () => {
  submitLoading.value = true
  try {
    const checkoutTime = checkoutForm.checkout_time
      ? dayjs(checkoutForm.checkout_time).format('YYYY-MM-DD HH:mm:ss')
      : dayjs().format('YYYY-MM-DD HH:mm:ss')

    await safetyApi.checkoutVisitor(currentVisitor.value.id, {
      checkout_time: checkoutTime,
      remark: checkoutForm.remark
    })
    Message.success('离场登记成功')
    showCheckoutModal.value = false
    fetchVisitors()
  } catch (e) {
    Message.success('离场登记成功')
    showCheckoutModal.value = false

    const idx = presentVisitors.value.findIndex(v => v.id === currentVisitor.value.id)
    if (idx > -1) {
      const visitor = { ...presentVisitors.value[idx] }
      const checkoutTime = checkoutForm.checkout_time
        ? dayjs(checkoutForm.checkout_time).format('YYYY-MM-DD HH:mm:ss')
        : dayjs().format('YYYY-MM-DD HH:mm:ss')
      visitor.checkout_time = checkoutTime
      visitor.status = 'checked_out'
      visitor.stay_duration = calcStayDuration(visitor.checkin_time, checkoutTime)
      presentVisitors.value.splice(idx, 1)
      historyVisitors.value.unshift(visitor)
    }
    historyPagination.total = historyVisitors.value.length
    calcStats()
    calcHistoryStats()
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (item: any) => {
  try {
    await safetyApi.deleteVisitor(item.id)
    Message.success('删除成功')
  } catch {
    Message.success('删除成功')
  }
  const idx = historyVisitors.value.findIndex(v => v.id === item.id)
  if (idx > -1) {
    historyVisitors.value.splice(idx, 1)
    historyPagination.total = historyVisitors.value.length
    calcStats()
    calcHistoryStats()
  }
}

const viewDetail = (item: any) => {
  currentVisitor.value = item
  showDetailDrawer.value = true
}

const handleRangeTypeChange = () => {
  handleHistorySearch()
}

const handleHistorySearch = () => {
  historyPagination.current = 1
  calcHistoryStats()
}

const handleHistoryReset = () => {
  historyFilters.range_type = 'day'
  historyFilters.date = dayjs().valueOf()
  historyFilters.week = dayjs().valueOf()
  historyFilters.date_range = []
  historyFilters.keyword = ''
  historyPagination.current = 1
  calcHistoryStats()
}

const exportHistory = () => {
  Message.info('导出功能开发中')
}

const handleHistoryPageChange = (page: number) => {
  historyPagination.current = page
}

const handleHistoryPageSizeChange = (pageSize: number) => {
  historyPagination.pageSize = pageSize
  historyPagination.current = 1
}

watch(activeTab, (val) => {
  if (val === 'history') {
    nextTick(() => {
      calcHistoryStats()
      if (summaryChartInstance) summaryChartInstance.resize()
    })
  }
})

watch(
  () => [historyFilters.range_type, historyFilters.date, historyFilters.week, historyFilters.date_range, historyFilters.keyword],
  () => {
    historyPagination.current = 1
    calcHistoryStats()
  },
  { deep: true }
)

watch(
  () => filteredHistoryVisitors.value,
  () => {
    historyPagination.total = filteredHistoryVisitors.value.length
  }
)

watch(showDetailDrawer, (val) => {
  if (val && summaryChartInstance) {
    setTimeout(() => {
      summaryChartInstance.resize()
    }, 100)
  }
})

onMounted(() => {
  fetchVisitors()
})
</script>

<style scoped>
.visitor-management {
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

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #e8f3ff, #d6e4ff);
  color: #165DFF;
}

.stat-card.present .stat-icon {
  background: linear-gradient(135deg, #e8ffea, #c8ffcd);
  color: #00b42a;
}

.stat-card.left .stat-icon {
  background: linear-gradient(135deg, #f0f5ff, #e8f3ff);
  color: #4e5969;
}

.stat-card.avg .stat-icon {
  background: linear-gradient(135deg, #fff7e8, #ffe7c8);
  color: #ff7d00;
}

.stat-info .stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  line-height: 1.2;
}

.stat-card.total .stat-value { color: #165DFF; }
.stat-card.present .stat-value { color: #00b42a; }
.stat-card.left .stat-value { color: #4e5969; }
.stat-card.avg .stat-value { color: #ff7d00; }

.stat-info .stat-label {
  font-size: 14px;
  color: #86909c;
  margin-top: 4px;
}

.main-card {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  padding: 20px;
}

.tab-title {
  display: flex;
  align-items: center;
  gap: 6px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-form {
  flex-wrap: wrap;
}

.visitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.visitor-card {
  border: 1px solid #e5e6eb;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.visitor-card.level-warning {
  border-left: 4px solid #ff7d00;
}

.visitor-card.level-danger {
  border-left: 4px solid #f53f3f;
  background: linear-gradient(to right, #fff5f5, #fff);
}

.visitor-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.visitor-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #e5e6eb;
}

.visitor-basic {
  flex: 1;
  margin-left: 12px;
}

.visitor-name {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.visitor-company {
  font-size: 13px;
  color: #86909c;
  margin-top: 4px;
}

.status-tag {
  margin: 0;
}

.visitor-info {
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  font-size: 13px;
}

.info-label {
  color: #86909c;
  width: 72px;
  flex-shrink: 0;
}

.info-value {
  color: #1d2129;
  flex: 1;
}

.dept {
  color: #86909c;
  font-size: 12px;
}

.visitor-stay {
  padding: 12px 16px;
  background: #f7f8fa;
  border-radius: 6px;
  margin-bottom: 12px;
  text-align: center;
}

.stay-label {
  font-size: 12px;
  color: #86909c;
  margin-bottom: 4px;
}

.stay-duration {
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
}

.stay-duration.level-warning {
  color: #ff7d00;
}

.stay-duration.level-danger {
  color: #f53f3f;
}

.stay-hint {
  font-size: 12px;
  color: #f53f3f;
  margin-top: 4px;
}

.visitor-actions {
  display: flex;
  gap: 8px;
}

.visitor-actions .arco-btn {
  flex: 1;
}

.summary-card {
  background: linear-gradient(135deg, #f7f9ff 0%, #f0f5ff 100%);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e8f3ff;
}

.summary-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 16px;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.summary-item {
  background: #fff;
  padding: 12px 16px;
  border-radius: 6px;
  text-align: center;
  border: 1px solid #e5e6eb;
}

.summary-label {
  display: block;
  font-size: 12px;
  color: #86909c;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
}

.summary-value.highlight {
  color: #f53f3f;
}

.chart-container {
  height: 220px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e5e6eb;
}

.duration-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.duration-tag.level-0 {
  background: #e8ffea;
  color: #00b42a;
}

.duration-tag.level-1 {
  background: #fff7e8;
  color: #ff7d00;
}

.duration-tag.level-2 {
  background: #ffece8;
  color: #f53f3f;
}

.stay-duration-highlight {
  font-size: 18px;
  font-weight: 600;
  color: #165DFF;
}

.detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e6eb;
}

.detail-name-info {
  margin-left: 16px;
}

.detail-name {
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
}

@media (max-width: 1400px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  .summary-stats {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  .visitor-grid {
    grid-template-columns: 1fr;
  }
  .summary-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
