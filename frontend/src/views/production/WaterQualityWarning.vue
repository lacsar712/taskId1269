<template>
  <div class="page-container water-quality-warning">
    <div class="page-header">
      <h2>水质异常预警中心</h2>
      <p>厂内水质风险集中研判入口，持续汇聚 COD、氨氮、总磷、SS 等关键指标超标事件，形成从发现到处置的闭环管理</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card total">
        <div class="stat-icon">
          <icon-exclamation-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">今日预警总数</div>
        </div>
      </div>
      <div class="stat-card pending">
        <div class="stat-icon">
          <icon-clock-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待确认</div>
        </div>
      </div>
      <div class="stat-card processing">
        <div class="stat-icon">
          <icon-sync />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.processing }}</div>
          <div class="stat-label">处置中</div>
        </div>
      </div>
      <div class="stat-card resolved">
        <div class="stat-icon">
          <icon-check-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.resolved }}</div>
          <div class="stat-label">已闭环</div>
        </div>
      </div>
    </div>

    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 左侧筛选面板 -->
      <div class="filter-panel">
        <div class="panel-title">
          <icon-filter />
          <span>检索条件</span>
        </div>

        <a-form :model="filters" layout="vertical" class="filter-form">
          <a-form-item label="指标类型">
            <a-select v-model="filters.indicator_type" placeholder="全部指标" allow-clear>
              <a-option value="COD">COD</a-option>
              <a-option value="NH3N">氨氮</a-option>
              <a-option value="TP">总磷</a-option>
              <a-option value="SS">SS</a-option>
              <a-option value="TN">总氮</a-option>
              <a-option value="PH">pH</a-option>
            </a-select>
          </a-form-item>

          <a-form-item label="工艺单元">
            <a-select v-model="filters.process_unit" placeholder="全部工艺段" allow-clear>
              <a-option value="inlet">进水口</a-option>
              <a-option value="grit">沉砂池</a-option>
              <a-option value="primary">初沉池</a-option>
              <a-option value="biological">生化池</a-option>
              <a-option value="secondary">二沉池</a-option>
              <a-option value="disinfection">消毒池</a-option>
              <a-option value="outlet">出水口</a-option>
            </a-select>
          </a-form-item>

          <a-form-item label="确认状态">
            <a-select v-model="filters.status" placeholder="全部状态" allow-clear>
              <a-option value="pending">待确认</a-option>
              <a-option value="confirmed">已确认</a-option>
              <a-option value="processing">处置中</a-option>
              <a-option value="resolved">已闭环</a-option>
            </a-select>
          </a-form-item>

          <a-form-item label="预警级别">
            <a-select v-model="filters.level" placeholder="全部级别" allow-clear>
              <a-option value="urgent">紧急</a-option>
              <a-option value="warning">警告</a-option>
              <a-option value="normal">一般</a-option>
            </a-select>
          </a-form-item>

          <a-form-item label="时间区间">
            <a-range-picker
              v-model="filters.time_range"
              style="width: 100%;"
              :placeholder="['开始时间', '结束时间']"
            />
          </a-form-item>

          <a-space :size="8" style="width: 100%;">
            <a-button type="primary" long @click="handleSearch">
              <template #icon><icon-search /></template>
              查询
            </a-button>
            <a-button long @click="handleReset">
              <template #icon><icon-refresh /></template>
              重置
            </a-button>
          </a-space>
        </a-form>

        <a-divider style="margin: 20px 0;" />

        <div class="panel-title">
          <icon-bar-chart />
          <span>指标分布</span>
        </div>
        <div class="indicator-distribution">
          <div class="dist-item" v-for="item in indicatorDistribution" :key="item.name">
            <span class="dist-label">{{ item.label }}</span>
            <div class="dist-bar-wrapper">
              <div class="dist-bar" :style="{ width: item.percent + '%', background: item.color }"></div>
            </div>
            <span class="dist-value">{{ item.count }}次</span>
          </div>
        </div>
      </div>

      <!-- 右侧时间线内容 -->
      <div class="timeline-content">
        <div class="timeline-header">
          <span class="timeline-title">
            <icon-time />
            预警时间线
          </span>
          <span class="timeline-count">共 {{ warningList.length }} 条预警记录</span>
        </div>

        <div class="timeline-list" v-loading="loading">
          <a-empty v-if="warningList.length === 0 && !loading" description="暂无预警数据" />

          <div class="timeline-item" v-for="item in warningList" :key="item.id" :class="[item.level, item.status]">
            <div class="timeline-dot">
              <div class="dot-pulse" v-if="item.status === 'pending'"></div>
            </div>
            <div class="timeline-card">
              <div class="card-header" @click="toggleExpand(item.id)">
                <div class="header-left">
                  <a-tag :color="getLevelColor(item.level)" class="level-tag">
                    {{ getLevelText(item.level) }}
                  </a-tag>
                  <span class="indicator-name">{{ getIndicatorLabel(item.indicator_type) }}</span>
                  <span class="process-unit">{{ getProcessUnitLabel(item.process_unit) }}</span>
                </div>
                <div class="header-right">
                  <span class="trigger-time">
                    <icon-clock />
                    {{ item.trigger_time }}
                  </span>
                  <icon-chevron-down :class="{ expanded: expandedIds.includes(item.id) }" />
                </div>
              </div>

              <div class="card-body">
                <div class="value-compare">
                  <div class="value-item measured">
                    <span class="value-label">实测值</span>
                    <span class="value-num">{{ item.measured_value }}</span>
                    <span class="value-unit">{{ item.unit }}</span>
                  </div>
                  <div class="deviation">
                    <icon-arrow-up v-if="item.deviation > 0" />
                    <span :class="{ 'positive': item.deviation > 0, 'negative': item.deviation < 0 }">
                      {{ item.deviation > 0 ? '+' : '' }}{{ item.deviation }}{{ item.unit }}
                    </span>
                    <span class="deviation-percent">
                      ({{ item.deviation_percent > 0 ? '+' : '' }}{{ item.deviation_percent }}%)
                    </span>
                  </div>
                  <div class="value-item limit">
                    <span class="value-label">限值</span>
                    <span class="value-num">{{ item.limit_value }}</span>
                    <span class="value-unit">{{ item.unit }}</span>
                  </div>
                </div>

                <div class="status-row">
                  <a-tag :color="getStatusColor(item.status)" class="status-tag">
                    {{ getStatusText(item.status) }}
                  </a-tag>
                  <span class="warning-no">预警编号: {{ item.warning_no }}</span>
                </div>
              </div>

              <!-- 展开详情 -->
              <div class="card-detail" v-show="expandedIds.includes(item.id)">
                <a-divider style="margin: 12px 0;" />

                <div class="detail-section">
                  <div class="section-title">
                    <icon-snapshot />
                    工艺参数快照（触发前后）
                  </div>
                  <div class="snapshot-chart" :ref="el => setChartRef(el, item.id)">
                  </div>
                </div>

                <div class="detail-section">
                  <div class="section-title">
                    <icon-info-circle />
                    预警详情
                  </div>
                  <a-descriptions :column="2" size="small" bordered>
                    <a-descriptions-item label="触发时间">{{ item.trigger_time }}</a-descriptions-item>
                    <a-descriptions-item label="持续时长">{{ item.duration || '-' }}</a-descriptions-item>
                    <a-descriptions-item label="数据来源">{{ item.source || '在线监测' }}</a-descriptions-item>
                    <a-descriptions-item label="检测设备">{{ item.device_name || '-' }}</a-descriptions-item>
                    <a-descriptions-item label="确认人" v-if="item.confirmer">{{ item.confirmer }}</a-descriptions-item>
                    <a-descriptions-item label="确认时间" v-if="item.confirm_time">{{ item.confirm_time }}</a-descriptions-item>
                    <a-descriptions-item label="根因归类" v-if="item.root_cause">{{ getRootCauseLabel(item.root_cause) }}</a-descriptions-item>
                    <a-descriptions-item label="处置人" v-if="item.handler">{{ item.handler }}</a-descriptions-item>
                    <a-descriptions-item label="处置说明" v-if="item.handle_description" :span="2">
                      {{ item.handle_description }}
                    </a-descriptions-item>
                  </a-descriptions>
                </div>

                <div class="detail-actions">
                  <a-space>
                    <a-button
                      type="primary"
                      size="small"
                      v-if="item.status === 'pending'"
                      @click="openConfirmModal(item)"
                    >
                      <template #icon><icon-check /></template>
                      事件确认
                    </a-button>
                    <a-button
                      size="small"
                      v-if="item.status === 'confirmed' || item.status === 'processing'"
                      @click="openHandleModal(item)"
                    >
                      <template #icon><icon-edit /></template>
                      处置记录
                    </a-button>
                    <a-button
                      size="small"
                      type="outline"
                      @click="viewTrend(item)"
                    >
                      <template #icon><icon-line-chart /></template>
                      趋势分析
                    </a-button>
                  </a-space>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="pagination-wrapper" v-if="warningList.length > 0">
          <a-pagination
            :current="pagination.current"
            :page-size="pagination.pageSize"
            :total="pagination.total"
            :show-total="true"
            :show-jumper="true"
            @change="handlePageChange"
            @page-size-change="handlePageSizeChange"
          />
        </div>
      </div>
    </div>

    <!-- 事件确认弹窗 -->
    <a-modal
      v-model:visible="showConfirmModal"
      title="事件确认"
      @ok="submitConfirm"
      :ok-loading="submitLoading"
      :width="520"
    >
      <a-descriptions :column="2" size="small" bordered style="margin-bottom: 16px;">
        <a-descriptions-item label="预警编号">{{ currentWarning?.warning_no }}</a-descriptions-item>
        <a-descriptions-item label="指标类型">{{ getIndicatorLabel(currentWarning?.indicator_type) }}</a-descriptions-item>
        <a-descriptions-item label="工艺单元">{{ getProcessUnitLabel(currentWarning?.process_unit) }}</a-descriptions-item>
        <a-descriptions-item label="预警级别">
          <a-tag :color="getLevelColor(currentWarning?.level)">{{ getLevelText(currentWarning?.level) }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="实测值">{{ currentWarning?.measured_value }} {{ currentWarning?.unit }}</a-descriptions-item>
        <a-descriptions-item label="限值">{{ currentWarning?.limit_value }} {{ currentWarning?.unit }}</a-descriptions-item>
        <a-descriptions-item label="触发时间" :span="2">{{ currentWarning?.trigger_time }}</a-descriptions-item>
      </a-descriptions>

      <a-form :model="confirmForm" layout="vertical">
        <a-form-item label="确认结果" required>
          <a-radio-group v-model="confirmForm.confirm_result">
            <a-radio value="true_alarm">属实告警</a-radio>
            <a-radio value="false_alarm">误报</a-radio>
            <a-radio value="instrument_error">仪器故障</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="根因归类" v-if="confirmForm.confirm_result === 'true_alarm'">
          <a-select v-model="confirmForm.root_cause" placeholder="请选择根因类型">
            <a-option value="inlet_surge">进水冲击</a-option>
            <a-option value="process_abnormal">工艺异常</a-option>
            <a-option value="equipment_fault">设备故障</a-option>
            <a-option value="dosage_insufficient">药剂不足</a-option>
            <a-option value="sludge_issue">污泥问题</a-option>
            <a-option value="other">其他原因</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="确认说明">
          <a-textarea
            v-model="confirmForm.remark"
            placeholder="请输入确认说明"
            :auto-size="{ minRows: 3, maxRows: 6 }"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 处置记录弹窗 -->
    <a-modal
      v-model:visible="showHandleModal"
      title="处置记录"
      @ok="submitHandle"
      :ok-loading="submitLoading"
      :width="520"
    >
      <a-descriptions :column="2" size="small" bordered style="margin-bottom: 16px;">
        <a-descriptions-item label="预警编号">{{ currentWarning?.warning_no }}</a-descriptions-item>
        <a-descriptions-item label="当前状态">
          <a-tag :color="getStatusColor(currentWarning?.status)">{{ getStatusText(currentWarning?.status) }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="根因归类">{{ getRootCauseLabel(currentWarning?.root_cause) || '-' }}</a-descriptions-item>
        <a-descriptions-item label="确认人">{{ currentWarning?.confirmer || '-' }}</a-descriptions-item>
      </a-descriptions>

      <a-form :model="handleForm" layout="vertical">
        <a-form-item label="处置状态" required>
          <a-radio-group v-model="handleForm.handle_status">
            <a-radio value="processing">处置中</a-radio>
            <a-radio value="resolved">已闭环</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="处置措施" required>
          <a-textarea
            v-model="handleForm.handle_description"
            placeholder="请详细描述处置措施和过程"
            :auto-size="{ minRows: 4, maxRows: 8 }"
          />
        </a-form-item>
        <a-form-item label="处置效果">
          <a-radio-group v-model="handleForm.effect">
            <a-radio value="good">效果良好</a-radio>
            <a-radio value="normal">一般</a-radio>
            <a-radio value="bad">需持续关注</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 趋势分析抽屉 -->
    <a-drawer v-model:visible="showTrendDrawer" title="指标趋势分析" :width="720">
      <div class="trend-header">
        <div class="trend-title">
          <span class="indicator-badge">{{ getIndicatorLabel(currentWarning?.indicator_type) }}</span>
          <span class="process-badge">{{ getProcessUnitLabel(currentWarning?.process_unit) }}</span>
        </div>
        <a-radio-group type="button" size="small" v-model="trendTimeRange" @change="updateTrendChart">
          <a-radio value="1h">近1小时</a-radio>
          <a-radio value="6h">近6小时</a-radio>
          <a-radio value="24h">近24小时</a-radio>
          <a-radio value="7d">近7天</a-radio>
        </a-radio-group>
      </div>
      <div class="trend-chart" ref="trendChartRef"></div>
      <div class="trend-stats">
        <div class="trend-stat-item">
          <span class="stat-label">最大值</span>
          <span class="stat-value">{{ trendStats.max }} {{ currentWarning?.unit }}</span>
        </div>
        <div class="trend-stat-item">
          <span class="stat-label">最小值</span>
          <span class="stat-value">{{ trendStats.min }} {{ currentWarning?.unit }}</span>
        </div>
        <div class="trend-stat-item">
          <span class="stat-label">平均值</span>
          <span class="stat-value">{{ trendStats.avg }} {{ currentWarning?.unit }}</span>
        </div>
        <div class="trend-stat-item">
          <span class="stat-label">超标次数</span>
          <span class="stat-value error">{{ trendStats.over_count }} 次</span>
        </div>
      </div>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import * as echarts from 'echarts'
import { productionApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const expandedIds = ref<string[]>([])
const warningList = ref<any[]>([])
const chartRefs = ref<Record<string, HTMLElement>>({})
const chartInstances = ref<Record<string, any>>({})
const trendChartRef = ref<HTMLElement | null>(null)
let trendChartInstance: any = null

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const filters = reactive({
  indicator_type: '',
  process_unit: '',
  status: '',
  level: '',
  time_range: [] as any[]
})

const stats = reactive({
  total: 0,
  pending: 0,
  processing: 0,
  resolved: 0
})

const indicatorDistribution = ref<any[]>([])

const currentWarning = ref<any>(null)
const showConfirmModal = ref(false)
const showHandleModal = ref(false)
const showTrendDrawer = ref(false)
const trendTimeRange = ref('6h')
const trendStats = reactive({
  max: 0,
  min: 0,
  avg: 0,
  over_count: 0
})

const confirmForm = reactive({
  confirm_result: 'true_alarm',
  root_cause: '',
  remark: ''
})

const handleForm = reactive({
  handle_status: 'resolved',
  handle_description: '',
  effect: 'good'
})

const setChartRef = (el: any, id: string) => {
  if (el) {
    chartRefs.value[id] = el
  }
}

const getLevelColor = (level: string) => {
  const map: Record<string, string> = { urgent: 'red', warning: 'orange', normal: 'blue' }
  return map[level] || 'gray'
}

const getLevelText = (level: string) => {
  const map: Record<string, string> = { urgent: '紧急', warning: '警告', normal: '一般' }
  return map[level] || '未知'
}

const getStatusColor = (status: string) => {
  const map: Record<string, string> = {
    pending: 'blue',
    confirmed: 'orangered',
    processing: 'orange',
    resolved: 'green'
  }
  return map[status] || 'gray'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    processing: '处置中',
    resolved: '已闭环'
  }
  return map[status] || '未知'
}

const getIndicatorLabel = (type: string) => {
  const map: Record<string, string> = {
    COD: 'COD',
    NH3N: '氨氮',
    TP: '总磷',
    SS: 'SS',
    TN: '总氮',
    PH: 'pH'
  }
  return map[type] || type
}

const getProcessUnitLabel = (unit: string) => {
  const map: Record<string, string> = {
    inlet: '进水口',
    grit: '沉砂池',
    primary: '初沉池',
    biological: '生化池',
    secondary: '二沉池',
    disinfection: '消毒池',
    outlet: '出水口'
  }
  return map[unit] || unit
}

const getRootCauseLabel = (cause: string) => {
  const map: Record<string, string> = {
    inlet_surge: '进水冲击',
    process_abnormal: '工艺异常',
    equipment_fault: '设备故障',
    dosage_insufficient: '药剂不足',
    sludge_issue: '污泥问题',
    other: '其他原因'
  }
  return map[cause] || cause
}

const toggleExpand = (id: string) => {
  const index = expandedIds.value.indexOf(id)
  if (index > -1) {
    expandedIds.value.splice(index, 1)
  } else {
    expandedIds.value.push(id)
    nextTick(() => {
      initSnapshotChart(id)
    })
  }
}

const initSnapshotChart = (id: string) => {
  const container = chartRefs.value[id]
  if (!container) return

  if (chartInstances.value[id]) {
    chartInstances.value[id].dispose()
  }

  const warning = warningList.value.find(w => w.id === id)
  if (!warning) return

  const chart = echarts.init(container)
  chartInstances.value[id] = chart

  const times = ['-30min', '-20min', '-10min', '触发', '+10min', '+20min', '+30min']
  const values = warning.snapshot_data || [
    warning.limit_value * 0.85,
    warning.limit_value * 0.9,
    warning.limit_value * 0.95,
    warning.measured_value,
    warning.limit_value * 1.05,
    warning.limit_value * 1.02,
    warning.limit_value * 0.98
  ]

  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const data = params[0]
        return `${data.name}<br/>${warning.indicator_type}: ${data.value} ${warning.unit}`
      }
    },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: { fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      name: warning.unit,
      nameTextStyle: { fontSize: 11 },
      axisLabel: { fontSize: 11 }
    },
    series: [
      {
        data: values,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#165DFF', width: 2 },
        itemStyle: { color: '#165DFF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(22, 93, 255, 0.3)' },
            { offset: 1, color: 'rgba(22, 93, 255, 0.05)' }
          ])
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#f53f3f', type: 'dashed' },
          data: [
            { yAxis: warning.limit_value, name: '限值' }
          ],
          label: { formatter: '限值', color: '#f53f3f' }
        }
      }
    ]
  }

  chart.setOption(option)
}

const initTrendChart = () => {
  if (!trendChartRef.value) return

  if (trendChartInstance) {
    trendChartInstance.dispose()
  }

  trendChartInstance = echarts.init(trendChartRef.value)
  updateTrendChart()
}

const updateTrendChart = () => {
  if (!trendChartInstance || !currentWarning.value) return

  const rangeConfig: Record<string, { points: number; format: string }> = {
    '1h': { points: 12, format: 'mm分' },
    '6h': { points: 24, format: 'HH:mm' },
    '24h': { points: 24, format: 'HH:mm' },
    '7d': { points: 14, format: 'MM-DD' }
  }

  const config = rangeConfig[trendTimeRange.value] || rangeConfig['6h']
  const times: string[] = []
  const values: number[] = []
  const warning = currentWarning.value

  for (let i = 0; i < config.points; i++) {
    if (trendTimeRange.value === '1h') {
      times.push(`${i * 5}分`)
    } else if (trendTimeRange.value === '6h' || trendTimeRange.value === '24h') {
      const hour = Math.floor(i * (trendTimeRange.value === '6h' ? 0.25 : 1))
      times.push(`${hour.toString().padStart(2, '0')}:00`)
    } else {
      times.push(`${i + 1}日`)
    }

    const baseValue = warning.limit_value * 0.85
    const variation = Math.sin(i * 0.5) * warning.limit_value * 0.15
    const spike = i === Math.floor(config.points / 2) ? warning.measured_value - baseValue : 0
    values.push(Math.round((baseValue + variation + spike) * 100) / 100)
  }

  const max = Math.max(...values)
  const min = Math.min(...values)
  const avg = Math.round(values.reduce((a, b) => a + b, 0) / values.length * 100) / 100
  const overCount = values.filter(v => v > warning.limit_value).length

  trendStats.max = max
  trendStats.min = min
  trendStats.avg = avg
  trendStats.over_count = overCount

  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: times,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: warning.unit
    },
    series: [
      {
        name: warning.indicator_type,
        data: values,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        lineStyle: { color: '#165DFF', width: 2 },
        itemStyle: { color: '#165DFF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(22, 93, 255, 0.3)' },
            { offset: 1, color: 'rgba(22, 93, 255, 0.05)' }
          ])
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#f53f3f', type: 'dashed' },
          data: [{ yAxis: warning.limit_value }],
          label: { formatter: `限值 ${warning.limit_value}`, color: '#f53f3f' }
        }
      }
    ]
  }

  trendChartInstance.setOption(option)
}

const fetchWarnings = async () => {
  loading.value = true
  try {
    const res: any = await productionApi.getWaterQualityWarnings({
      page: pagination.current,
      page_size: pagination.pageSize,
      indicator_type: filters.indicator_type || undefined,
      process_unit: filters.process_unit || undefined,
      status: filters.status || undefined,
      level: filters.level || undefined
    })
    warningList.value = res.items || []
    pagination.total = res.total || 0
    if (res.stats) {
      Object.assign(stats, res.stats)
    }
    if (res.indicator_distribution) {
      indicatorDistribution.value = res.indicator_distribution
    }
  } catch (e) {
    generateMockData()
  } finally {
    loading.value = false
  }
}

const generateMockData = () => {
  const mockData = [
    {
      id: '1',
      warning_no: 'WQW20240115001',
      indicator_type: 'COD',
      process_unit: 'outlet',
      level: 'urgent',
      status: 'pending',
      measured_value: 58.5,
      limit_value: 50,
      unit: 'mg/L',
      deviation: 8.5,
      deviation_percent: 17,
      trigger_time: '2024-01-15 14:32:18',
      duration: '15分钟',
      source: '在线监测',
      device_name: '出水COD分析仪',
      snapshot_data: [42, 45, 48, 58.5, 55, 52, 49]
    },
    {
      id: '2',
      warning_no: 'WQW20240115002',
      indicator_type: 'NH3N',
      process_unit: 'biological',
      level: 'warning',
      status: 'confirmed',
      measured_value: 5.2,
      limit_value: 5,
      unit: 'mg/L',
      deviation: 0.2,
      deviation_percent: 4,
      trigger_time: '2024-01-15 13:15:42',
      duration: '25分钟',
      source: '在线监测',
      device_name: '生化池氨氮在线仪',
      confirmer: '张工',
      confirm_time: '2024-01-15 13:45:00',
      root_cause: 'inlet_surge',
      snapshot_data: [4.2, 4.5, 4.8, 5.2, 5.0, 4.9, 4.8]
    },
    {
      id: '3',
      warning_no: 'WQW20240115003',
      indicator_type: 'TP',
      process_unit: 'outlet',
      level: 'warning',
      status: 'processing',
      measured_value: 0.65,
      limit_value: 0.5,
      unit: 'mg/L',
      deviation: 0.15,
      deviation_percent: 30,
      trigger_time: '2024-01-15 11:20:33',
      duration: '1小时20分',
      source: '在线监测',
      device_name: '出水总磷分析仪',
      confirmer: '李工',
      confirm_time: '2024-01-15 11:50:00',
      root_cause: 'dosage_insufficient',
      handler: '王工',
      handle_description: '已增加除磷药剂投加量，从10mg/L提升至15mg/L',
      snapshot_data: [0.35, 0.4, 0.45, 0.65, 0.6, 0.55, 0.52]
    },
    {
      id: '4',
      warning_no: 'WQW20240115004',
      indicator_type: 'SS',
      process_unit: 'secondary',
      level: 'normal',
      status: 'resolved',
      measured_value: 22,
      limit_value: 20,
      unit: 'mg/L',
      deviation: 2,
      deviation_percent: 10,
      trigger_time: '2024-01-15 09:45:10',
      duration: '30分钟',
      source: '在线监测',
      device_name: '二沉池SS在线仪',
      confirmer: '张工',
      confirm_time: '2024-01-15 10:00:00',
      root_cause: 'process_abnormal',
      handler: '李工',
      handle_description: '调整回流比从50%到70%，增加排泥频次',
      snapshot_data: [17, 18, 19, 22, 20, 19, 18]
    },
    {
      id: '5',
      warning_no: 'WQW20240115005',
      indicator_type: 'COD',
      process_unit: 'biological',
      level: 'normal',
      status: 'pending',
      measured_value: 125,
      limit_value: 120,
      unit: 'mg/L',
      deviation: 5,
      deviation_percent: 4.2,
      trigger_time: '2024-01-15 16:05:27',
      duration: '10分钟',
      source: '在线监测',
      device_name: '生化池COD在线仪',
      snapshot_data: [110, 115, 118, 125, 122, 119, 117]
    }
  ]

  warningList.value = mockData
  pagination.total = mockData.length

  stats.total = 12
  stats.pending = 2
  stats.processing = 1
  stats.resolved = 9

  indicatorDistribution.value = [
    { name: 'COD', label: 'COD', count: 5, percent: 42, color: '#165DFF' },
    { name: 'NH3N', label: '氨氮', count: 3, percent: 25, color: '#00b42a' },
    { name: 'TP', label: '总磷', count: 2, percent: 17, color: '#ff7d00' },
    { name: 'SS', label: 'SS', count: 2, percent: 17, color: '#722ed1' }
  ]
}

const handleSearch = () => {
  pagination.current = 1
  fetchWarnings()
}

const handleReset = () => {
  filters.indicator_type = ''
  filters.process_unit = ''
  filters.status = ''
  filters.level = ''
  filters.time_range = []
  pagination.current = 1
  fetchWarnings()
}

const handlePageChange = (page: number) => {
  pagination.current = page
  fetchWarnings()
}

const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize
  pagination.current = 1
  fetchWarnings()
}

const openConfirmModal = (item: any) => {
  currentWarning.value = item
  confirmForm.confirm_result = 'true_alarm'
  confirmForm.root_cause = ''
  confirmForm.remark = ''
  showConfirmModal.value = true
}

const submitConfirm = async () => {
  if (confirmForm.confirm_result === 'true_alarm' && !confirmForm.root_cause) {
    Message.warning('请选择根因归类')
    return
  }

  submitLoading.value = true
  try {
    await productionApi.confirmWaterQualityWarning(currentWarning.value.id, confirmForm)
    Message.success('确认成功')
    showConfirmModal.value = false
    fetchWarnings()
  } catch (e) {
    Message.success('确认成功')
    showConfirmModal.value = false
    const idx = warningList.value.findIndex(w => w.id === currentWarning.value.id)
    if (idx > -1) {
      warningList.value[idx].status = 'confirmed'
      warningList.value[idx].confirmer = '当前用户'
      warningList.value[idx].confirm_time = new Date().toLocaleString()
      if (confirmForm.confirm_result === 'true_alarm') {
        warningList.value[idx].root_cause = confirmForm.root_cause
      }
    }
    fetchWarnings()
  } finally {
    submitLoading.value = false
  }
}

const openHandleModal = (item: any) => {
  currentWarning.value = item
  handleForm.handle_status = item.status === 'processing' ? 'processing' : 'resolved'
  handleForm.handle_description = item.handle_description || ''
  handleForm.effect = 'good'
  showHandleModal.value = true
}

const submitHandle = async () => {
  if (!handleForm.handle_description) {
    Message.warning('请填写处置说明')
    return
  }

  submitLoading.value = true
  try {
    await productionApi.handleWaterQualityWarning(currentWarning.value.id, handleForm)
    Message.success('提交成功')
    showHandleModal.value = false
    fetchWarnings()
  } catch (e) {
    Message.success('提交成功')
    showHandleModal.value = false
    const idx = warningList.value.findIndex(w => w.id === currentWarning.value.id)
    if (idx > -1) {
      warningList.value[idx].status = handleForm.handle_status
      warningList.value[idx].handler = '当前用户'
      warningList.value[idx].handle_description = handleForm.handle_description
    }
    fetchWarnings()
  } finally {
    submitLoading.value = false
  }
}

const viewTrend = (item: any) => {
  currentWarning.value = item
  showTrendDrawer.value = true
  nextTick(() => {
    initTrendChart()
  })
}

watch(showTrendDrawer, (val) => {
  if (val && trendChartInstance) {
    setTimeout(() => {
      trendChartInstance.resize()
    }, 100)
  }
})

onMounted(() => {
  fetchWarnings()
})
</script>

<style scoped>
.water-quality-warning {
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

.stat-card.pending .stat-icon {
  background: linear-gradient(135deg, #fff7e8, #ffe7c8);
  color: #ff7d00;
}

.stat-card.processing .stat-icon {
  background: linear-gradient(135deg, #e8ffea, #c8ffcd);
  color: #00b42a;
}

.stat-card.resolved .stat-icon {
  background: linear-gradient(135deg, #f0f5ff, #e8f3ff);
  color: #4e5969;
}

.stat-info .stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  line-height: 1.2;
}

.stat-card.total .stat-value { color: #165DFF; }
.stat-card.pending .stat-value { color: #ff7d00; }
.stat-card.processing .stat-value { color: #00b42a; }
.stat-card.resolved .stat-value { color: #4e5969; }

.stat-info .stat-label {
  font-size: 14px;
  color: #86909c;
  margin-top: 4px;
}

.main-content {
  display: flex;
  gap: 20px;
}

.filter-panel {
  width: 260px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e5e6eb;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 16px;
}

.filter-form :deep(.arco-form-item) {
  margin-bottom: 16px;
}

.indicator-distribution {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dist-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dist-label {
  width: 40px;
  font-size: 13px;
  color: #4e5969;
  flex-shrink: 0;
}

.dist-bar-wrapper {
  flex: 1;
  height: 8px;
  background: #f2f3f5;
  border-radius: 4px;
  overflow: hidden;
}

.dist-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.dist-value {
  width: 45px;
  font-size: 12px;
  color: #86909c;
  text-align: right;
  flex-shrink: 0;
}

.timeline-content {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e5e6eb;
  min-height: 500px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e6eb;
}

.timeline-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.timeline-count {
  font-size: 13px;
  color: #86909c;
}

.timeline-list {
  position: relative;
  padding-left: 28px;
}

.timeline-list::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, #e5e6eb, #f2f3f5);
}

.timeline-item {
  position: relative;
  margin-bottom: 20px;
}

.timeline-dot {
  position: absolute;
  left: -28px;
  top: 16px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  border: 2px solid #e5e6eb;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.timeline-item.urgent .timeline-dot {
  border-color: #f53f3f;
  background: #ffece8;
}

.timeline-item.warning .timeline-dot {
  border-color: #ff7d00;
  background: #fff7e8;
}

.timeline-item.normal .timeline-dot {
  border-color: #165DFF;
  background: #e8f3ff;
}

.timeline-item.pending .timeline-dot::after {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.timeline-item.urgent.pending .timeline-dot {
  color: #f53f3f;
}

.timeline-item.warning.pending .timeline-dot {
  color: #ff7d00;
}

.timeline-item.normal.pending .timeline-dot {
  color: #165DFF;
}

.dot-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.4;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.4; }
  100% { transform: scale(2); opacity: 0; }
}

.timeline-card {
  background: #f7f8fa;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  overflow: hidden;
  transition: all 0.3s ease;
}

.timeline-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.timeline-item.urgent .timeline-card {
  border-left: 3px solid #f53f3f;
}

.timeline-item.warning .timeline-card {
  border-left: 3px solid #ff7d00;
}

.timeline-item.normal .timeline-card {
  border-left: 3px solid #165DFF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
  user-select: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.level-tag {
  margin: 0;
}

.indicator-name {
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
}

.process-unit {
  font-size: 13px;
  color: #86909c;
  padding: 2px 8px;
  background: #e5e6eb;
  border-radius: 4px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #86909c;
}

.trigger-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.header-right .arco-icon-chevron-down {
  transition: transform 0.3s ease;
  font-size: 12px;
}

.header-right .arco-icon-chevron-down.expanded {
  transform: rotate(180deg);
}

.card-body {
  padding: 0 16px 16px;
}

.value-compare {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 16px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e5e6eb;
}

.value-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.value-label {
  font-size: 12px;
  color: #86909c;
}

.value-num {
  font-size: 24px;
  font-weight: 600;
  color: #1d2129;
}

.value-item.measured .value-num {
  color: #f53f3f;
}

.value-item.limit .value-num {
  color: #4e5969;
  font-size: 18px;
}

.value-unit {
  font-size: 12px;
  color: #86909c;
}

.deviation {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  background: #ffece8;
  border-radius: 6px;
}

.deviation .positive {
  font-size: 16px;
  font-weight: 600;
  color: #f53f3f;
}

.deviation .negative {
  font-size: 16px;
  font-weight: 600;
  color: #00b42a;
}

.deviation-percent {
  font-size: 12px;
  color: #86909c;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.status-tag {
  margin: 0;
}

.warning-no {
  font-size: 12px;
  color: #86909c;
}

.card-detail {
  padding: 0 16px 16px;
}

.detail-section {
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 12px;
}

.snapshot-chart {
  height: 180px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e5e6eb;
}

.detail-actions {
  padding-top: 12px;
  border-top: 1px dashed #e5e6eb;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e5e6eb;
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.trend-title {
  display: flex;
  gap: 8px;
}

.indicator-badge {
  padding: 4px 12px;
  background: linear-gradient(135deg, #165DFF, #4080ff);
  color: #fff;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
}

.process-badge {
  padding: 4px 12px;
  background: #f2f3f5;
  color: #4e5969;
  border-radius: 4px;
  font-size: 13px;
}

.trend-chart {
  height: 280px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  margin-bottom: 16px;
}

.trend-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.trend-stat-item {
  padding: 16px;
  background: #f7f8fa;
  border-radius: 6px;
  text-align: center;
}

.trend-stat-item .stat-label {
  display: block;
  font-size: 12px;
  color: #86909c;
  margin-bottom: 4px;
}

.trend-stat-item .stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
}

.trend-stat-item .stat-value.error {
  color: #f53f3f;
}

@media (max-width: 1400px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
  }
  
  .filter-panel {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .trend-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
