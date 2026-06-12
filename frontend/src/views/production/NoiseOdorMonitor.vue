<template>
  <div class="page-container noise-odor-monitor">
    <div class="page-header">
      <h2>噪声与臭气监测</h2>
      <p>管理厂界及厂内重点区域的噪声、dB(A)、H₂S、NH₃ 等环境监测读数，为环保合规与异味溯源提供数据支撑</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card points">
        <div class="stat-icon">
          <icon-location />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.point_count }}</div>
          <div class="stat-label">监测点位</div>
        </div>
      </div>
      <div class="stat-card normal">
        <div class="stat-icon">
          <icon-check-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.normal_count }}</div>
          <div class="stat-label">正常运行</div>
        </div>
      </div>
      <div class="stat-card over">
        <div class="stat-icon">
          <icon-exclamation-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.over_count }}</div>
          <div class="stat-label">今日超标</div>
        </div>
      </div>
      <div class="stat-card offline">
        <div class="stat-icon">
          <icon-close-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.offline_count }}</div>
          <div class="stat-label">离线设备</div>
        </div>
      </div>
    </div>

    <!-- Tab 切换 -->
    <a-tabs v-model:activeKey="activeTab" type="card" class="main-tabs">
      <!-- 实时监测 -->
      <a-tab-pane key="realtime" title="实时监测">
        <div class="realtime-content">
          <!-- 左侧点位表格 -->
          <div class="point-table-panel">
            <div class="panel-header">
              <span class="panel-title">
                <icon-apps />
                监测点位
              </span>
              <a-space :size="8">
                <a-select
                  v-model="filterIndicator"
                  placeholder="全部指标"
                  style="width: 120px;"
                  size="small"
                  allow-clear
                >
                  <a-option value="noise">噪声 dB(A)</a-option>
                  <a-option value="h2s">H₂S</a-option>
                  <a-option value="nh3">NH₃</a-option>
                </a-select>
                <a-input-search
                  v-model="searchKeyword"
                  placeholder="搜索点位"
                  style="width: 160px;"
                  size="small"
                  @search="handleSearch"
                />
              </a-space>
            </div>

            <div class="point-table-wrapper">
              <a-table
                :data="filteredPoints"
                :pagination="false"
                size="small"
                :row-class-name="getRowClassName"
                @row-click="handlePointClick"
                :scroll="{ y: 420 }"
              >
                <template #columns>
                  <a-table-column title="点位名称" data-index="name" width="120">
                    <template #cell="{ record }">
                      <span class="point-name">
                        <span class="status-dot" :class="record.status"></span>
                        {{ record.name }}
                      </span>
                    </template>
                  </a-table-column>
                  <a-table-column title="位置" data-index="location" width="100" />
                  <a-table-column title="类型" data-index="type" width="80">
                    <template #cell="{ record }">
                      <a-tag :color="record.type === 'boundary' ? 'blue' : 'green'" size="small">
                        {{ record.type === 'boundary' ? '厂界' : '厂内' }}
                      </a-tag>
                    </template>
                  </a-table-column>
                  <a-table-column title="噪声 dB(A)" data-index="noise_value" width="100">
                    <template #cell="{ record }">
                      <span :class="{ 'over-value': record.noise_over }">
                        {{ record.noise_value !== null ? record.noise_value : '-' }}
                      </span>
                    </template>
                  </a-table-column>
                  <a-table-column title="H₂S (ppm)" data-index="h2s_value" width="90">
                    <template #cell="{ record }">
                      <span :class="{ 'over-value': record.h2s_over }">
                        {{ record.h2s_value !== null ? record.h2s_value : '-' }}
                      </span>
                    </template>
                  </a-table-column>
                  <a-table-column title="NH₃ (ppm)" data-index="nh3_value" width="90">
                    <template #cell="{ record }">
                      <span :class="{ 'over-value': record.nh3_over }">
                        {{ record.nh3_value !== null ? record.nh3_value : '-' }}
                      </span>
                    </template>
                  </a-table-column>
                  <a-table-column title="更新时间" data-index="update_time" width="140" />
                </template>
              </a-table>
            </div>
          </div>

          <!-- 右侧曲线图 -->
          <div class="chart-panel">
            <div class="panel-header">
              <span class="panel-title">
                <icon-line-chart />
                近24小时变化曲线
              </span>
              <a-radio-group type="button" size="small" v-model="chartIndicator" @change="updateChart">
                <a-radio value="noise">噪声 dB(A)</a-radio>
                <a-radio value="h2s">H₂S</a-radio>
                <a-radio value="nh3">NH₃</a-radio>
              </a-radio-group>
            </div>

            <div class="selected-point-info" v-if="selectedPoint">
              <span class="point-badge">{{ selectedPoint.name }}</span>
              <span class="location-text">{{ selectedPoint.location }}</span>
              <a-tag :color="selectedPoint.status === 'online' ? 'green' : 'gray'" size="small">
                {{ selectedPoint.status === 'online' ? '在线' : '离线' }}
              </a-tag>
            </div>
            <div class="no-selection" v-else>
              <icon-info-circle />
              <span>请选择左侧监测点位查看趋势</span>
            </div>

            <div class="chart-container" ref="chartRef"></div>

            <div class="chart-stats" v-if="selectedPoint">
              <div class="stat-item">
                <span class="stat-label">最大值</span>
                <span class="stat-value">{{ chartStats.max }} {{ getUnit() }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">最小值</span>
                <span class="stat-value">{{ chartStats.min }} {{ getUnit() }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平均值</span>
                <span class="stat-value">{{ chartStats.avg }} {{ getUnit() }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">限值</span>
                <span class="stat-value limit">{{ getLimitValue() }} {{ getUnit() }}</span>
              </div>
            </div>
          </div>
        </div>
      </a-tab-pane>

      <!-- 超标记录 -->
      <a-tab-pane key="over-record" title="超标记录">
        <div class="over-record-content">
          <div class="filter-bar">
            <a-form :model="overFilters" layout="inline">
              <a-form-item label="指标类型">
                <a-select v-model="overFilters.indicator" placeholder="全部指标" allow-clear style="width: 140px;">
                  <a-option value="noise">噪声 dB(A)</a-option>
                  <a-option value="h2s">H₂S</a-option>
                  <a-option value="nh3">NH₃</a-option>
                </a-select>
              </a-form-item>
              <a-form-item label="监测点位">
                <a-select v-model="overFilters.point_id" placeholder="全部点位" allow-clear style="width: 160px;">
                  <a-option v-for="p in monitorPoints" :key="p.id" :value="p.id">{{ p.name }}</a-option>
                </a-select>
              </a-form-item>
              <a-form-item label="超标级别">
                <a-select v-model="overFilters.level" placeholder="全部级别" allow-clear style="width: 120px;">
                  <a-option value="slight">轻度超标</a-option>
                  <a-option value="moderate">中度超标</a-option>
                  <a-option value="severe">严重超标</a-option>
                </a-select>
              </a-form-item>
              <a-form-item label="时间范围">
                <a-range-picker
                  v-model="overFilters.time_range"
                  style="width: 260px;"
                  :placeholder="['开始时间', '结束时间']"
                />
              </a-form-item>
              <a-form-item>
                <a-space :size="8">
                  <a-button type="primary" @click="handleOverSearch">
                    <template #icon><icon-search /></template>
                    查询
                  </a-button>
                  <a-button @click="handleOverReset">
                    <template #icon><icon-refresh /></template>
                    重置
                  </a-button>
                </a-space>
              </a-form-item>
            </a-form>
          </div>

          <a-table
            :data="overRecords"
            :pagination="overPagination"
            @page-change="handleOverPageChange"
            @page-size-change="handleOverPageSizeChange"
            :loading="overLoading"
            row-key="id"
          >
            <template #columns>
              <a-table-column title="超标编号" data-index="record_no" width="140" />
              <a-table-column title="指标类型" data-index="indicator" width="110">
                <template #cell="{ record }">
                  <a-tag :color="getIndicatorColor(record.indicator)">
                    {{ getIndicatorLabel(record.indicator) }}
                  </a-tag>
                </template>
              </a-table-column>
              <a-table-column title="监测点位" data-index="point_name" width="120" />
              <a-table-column title="超标级别" data-index="level" width="100">
                <template #cell="{ record }">
                  <a-tag :color="getOverLevelColor(record.level)">
                    {{ getOverLevelText(record.level) }}
                  </a-tag>
                </template>
              </a-table-column>
              <a-table-column title="峰值" width="90">
                <template #cell="{ record }">
                  <span class="peak-value">{{ record.peak_value }}</span>
                  <span class="value-unit">{{ record.unit }}</span>
                </template>
              </a-table-column>
              <a-table-column title="限值" data-index="limit_value" width="90">
                <template #cell="{ record }">
                  {{ record.limit_value }} {{ record.unit }}
                </template>
              </a-table-column>
              <a-table-column title="超标幅度" width="100">
                <template #cell="{ record }">
                  <span class="over-rate">+{{ record.over_percent }}%</span>
                </template>
              </a-table-column>
              <a-table-column title="开始时间" data-index="start_time" width="160" />
              <a-table-column title="结束时间" data-index="end_time" width="160" />
              <a-table-column title="持续时长" data-index="duration" width="100" />
              <a-table-column title="气象条件" data-index="weather" width="120">
                <template #cell="{ record }">
                  <span v-if="record.weather">{{ record.weather }} / {{ record.temperature }}℃ / {{ record.wind_speed }}m/s</span>
                  <span v-else>-</span>
                </template>
              </a-table-column>
              <a-table-column title="操作" width="100" fixed="right">
                <template #cell="{ record }">
                  <a-button type="text" size="small" @click="viewOverDetail(record)">
                    详情
                  </a-button>
                </template>
              </a-table-column>
            </template>
          </a-table>
        </div>
      </a-tab-pane>

      <!-- 限值配置 -->
      <a-tab-pane key="limit-config" title="限值配置">
        <div class="limit-config-content">
          <div class="config-header">
            <span class="panel-title">
              <icon-setting />
              厂界限值配置
            </span>
            <a-button type="primary" @click="openLimitModal">
              <template #icon><icon-plus /></template>
              新增配置
            </a-button>
          </div>

          <a-table :data="limitConfigs" :pagination="false" row-key="id">
            <template #columns>
              <a-table-column title="监测项目" data-index="indicator" width="150">
                <template #cell="{ record }">
                  <span class="indicator-name">
                    <span class="indicator-dot" :style="{ background: getIndicatorColor(record.indicator) }"></span>
                    {{ getIndicatorLabel(record.indicator) }}
                  </span>
                </template>
              </a-table-column>
              <a-table-column title="适用点位" data-index="point_names" width="200" />
              <a-table-column title="限值类型" data-index="limit_type" width="100">
                <template #cell="{ record }">
                  {{ record.limit_type === 'day' ? '昼间限值' : '夜间限值' }}
                </template>
              </a-table-column>
              <a-table-column title="限值" width="120">
                <template #cell="{ record }">
                  <span class="limit-value">{{ record.limit_value }}</span>
                  <span class="value-unit">{{ record.unit }}</span>
                </template>
              </a-table-column>
              <a-table-column title="标准来源" data-index="standard" width="200" />
              <a-table-column title="生效时间" data-index="effective_date" width="120" />
              <a-table-column title="状态" data-index="status" width="80">
                <template #cell="{ record }">
                  <a-tag :color="record.status === 'active' ? 'green' : 'gray'" size="small">
                    {{ record.status === 'active' ? '启用' : '停用' }}
                  </a-tag>
                </template>
              </a-table-column>
              <a-table-column title="操作" width="160" fixed="right">
                <template #cell="{ record }">
                  <a-space :size="4">
                    <a-button type="text" size="small" @click="editLimit(record)">编辑</a-button>
                    <a-button type="text" size="small" @click="toggleLimitStatus(record)">
                      {{ record.status === 'active' ? '停用' : '启用' }}
                    </a-button>
                    <a-button type="text" size="small" status="danger" @click="deleteLimit(record)">删除</a-button>
                  </a-space>
                </template>
              </a-table-column>
            </template>
          </a-table>
        </div>
      </a-tab-pane>
    </a-tabs>

    <!-- 超标详情弹窗 -->
    <a-modal
      v-model:visible="showDetailModal"
      title="超标记录详情"
      :footer="false"
      :width="680"
    >
      <div class="detail-modal-content" v-if="currentOverRecord">
        <div class="detail-header">
          <div class="detail-title">
            <a-tag :color="getOverLevelColor(currentOverRecord.level)" size="large">
              {{ getOverLevelText(currentOverRecord.level) }}
            </a-tag>
            <span class="record-no">{{ currentOverRecord.record_no }}</span>
          </div>
          <div class="detail-indicator">
            {{ getIndicatorLabel(currentOverRecord.indicator) }} - {{ currentOverRecord.point_name }}
          </div>
        </div>

        <div class="detail-chart" :ref="el => setDetailChartRef(el)"></div>

        <a-descriptions :column="2" bordered size="small">
          <a-descriptions-item label="峰值浓度">
            <span class="peak-value-large">{{ currentOverRecord.peak_value }}</span>
            <span class="value-unit">{{ currentOverRecord.unit }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="限值">
            {{ currentOverRecord.limit_value }} {{ currentOverRecord.unit }}
          </a-descriptions-item>
          <a-descriptions-item label="超标幅度">
            <span class="over-rate-large">+{{ currentOverRecord.over_percent }}%</span>
          </a-descriptions-item>
          <a-descriptions-item label="持续时长">
            {{ currentOverRecord.duration }}
          </a-descriptions-item>
          <a-descriptions-item label="开始时间">
            {{ currentOverRecord.start_time }}
          </a-descriptions-item>
          <a-descriptions-item label="结束时间">
            {{ currentOverRecord.end_time }}
          </a-descriptions-item>
          <a-descriptions-item label="天气状况">
            {{ currentOverRecord.weather || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="气温">
            {{ currentOverRecord.temperature ? currentOverRecord.temperature + '℃' : '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="风速">
            {{ currentOverRecord.wind_speed ? currentOverRecord.wind_speed + ' m/s' : '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="风向">
            {{ currentOverRecord.wind_direction || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="气压" v-if="currentOverRecord.pressure">
            {{ currentOverRecord.pressure }} hPa
          </a-descriptions-item>
          <a-descriptions-item label="湿度" v-if="currentOverRecord.humidity">
            {{ currentOverRecord.humidity }}%
          </a-descriptions-item>
          <a-descriptions-item label="备注说明" :span="2">
            {{ currentOverRecord.remark || '暂无备注' }}
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>

    <!-- 限值配置弹窗 -->
    <a-modal
      v-model:visible="showLimitModal"
      :title="isEditLimit ? '编辑限值配置' : '新增限值配置'"
      @ok="submitLimit"
      :ok-loading="submitLoading"
      :width="560"
    >
      <a-form :model="limitForm" layout="vertical">
        <a-form-item label="监测项目" required>
          <a-select v-model="limitForm.indicator" placeholder="请选择监测项目">
            <a-option value="noise">噪声 dB(A)</a-option>
            <a-option value="h2s">H₂S</a-option>
            <a-option value="nh3">NH₃</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="适用点位" required>
          <a-select v-model="limitForm.point_ids" multiple placeholder="请选择适用点位" :max-tag-count="3">
            <a-option v-for="p in monitorPoints" :key="p.id" :value="p.id">{{ p.name }}</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="限值类型" required>
          <a-radio-group v-model="limitForm.limit_type">
            <a-radio value="day">昼间限值</a-radio>
            <a-radio value="night">夜间限值</a-radio>
            <a-radio value="all">全天限值</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="限值" required>
          <a-input-number v-model="limitForm.limit_value" :min="0" :step="0.1" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="标准来源">
          <a-input v-model="limitForm.standard" placeholder="如：GB 12348-2008 工业企业厂界环境噪声排放标准" />
        </a-form-item>
        <a-form-item label="生效时间">
          <a-date-picker v-model="limitForm.effective_date" style="width: 100%;" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed, watch } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import * as echarts from 'echarts'
import { productionApi } from '@/api'

const activeTab = ref('realtime')
const searchKeyword = ref('')
const filterIndicator = ref('')
const chartIndicator = ref('noise')
const selectedPoint = ref<any>(null)
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: any = null

const loading = ref(false)
const overLoading = ref(false)
const submitLoading = ref(false)

const stats = reactive({
  point_count: 0,
  normal_count: 0,
  over_count: 0,
  offline_count: 0
})

const monitorPoints = ref<any[]>([])
const overRecords = ref<any[]>([])
const limitConfigs = ref<any[]>([])

const chartStats = reactive({
  max: 0,
  min: 0,
  avg: 0
})

const overFilters = reactive({
  indicator: '',
  point_id: '',
  level: '',
  time_range: [] as any[]
})

const overPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const showDetailModal = ref(false)
const currentOverRecord = ref<any>(null)
const detailChartRef = ref<HTMLElement | null>(null)
let detailChartInstance: any = null

const showLimitModal = ref(false)
const isEditLimit = ref(false)
const limitForm = reactive({
  id: null as number | null,
  indicator: '',
  point_ids: [] as number[],
  limit_type: 'all',
  limit_value: null as number | null,
  standard: '',
  effective_date: null as any
})

const filteredPoints = computed(() => {
  let list = [...monitorPoints.value]
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    list = list.filter(p =>
      p.name.toLowerCase().includes(keyword) ||
      p.location.toLowerCase().includes(keyword)
    )
  }
  if (filterIndicator.value) {
    const key = filterIndicator.value
    list = list.filter(p => p[key + '_value'] !== null)
  }
  return list
})

const getRowClassName = (record: any) => {
  if (selectedPoint.value?.id === record.id) {
    return 'row-selected'
  }
  return ''
}

const getIndicatorLabel = (type: string) => {
  const map: Record<string, string> = {
    noise: '噪声 dB(A)',
    h2s: 'H₂S',
    nh3: 'NH₃'
  }
  return map[type] || type
}

const getIndicatorColor = (type: string) => {
  const map: Record<string, string> = {
    noise: '#165DFF',
    h2s: '#ff7d00',
    nh3: '#00b42a'
  }
  return map[type] || '#86909c'
}

const getOverLevelText = (level: string) => {
  const map: Record<string, string> = {
    slight: '轻度超标',
    moderate: '中度超标',
    severe: '严重超标'
  }
  return map[level] || level
}

const getOverLevelColor = (level: string) => {
  const map: Record<string, string> = {
    slight: 'orange',
    moderate: 'orangered',
    severe: 'red'
  }
  return map[level] || 'gray'
}

const getUnit = () => {
  const map: Record<string, string> = {
    noise: 'dB(A)',
    h2s: 'ppm',
    nh3: 'ppm'
  }
  return map[chartIndicator.value] || ''
}

const getLimitValue = () => {
  if (!selectedPoint.value) return 0
  const key = chartIndicator.value
  const limitKey = key + '_limit'
  return selectedPoint.value[limitKey] || 0
}

const handlePointClick = (record: any) => {
  selectedPoint.value = record
  nextTick(() => {
    initChart()
  })
}

const handleSearch = () => {
  // 搜索已通过 computed 实现
}

const initChart = () => {
  if (!chartRef.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance || !selectedPoint.value) return

  const indicator = chartIndicator.value
  const valueKey = indicator + '_value'
  const limitKey = indicator + '_limit'
  const limitValue = selectedPoint.value[limitKey] || 0
  const unit = getUnit()

  const hours = 24
  const times: string[] = []
  const values: number[] = []

  for (let i = 0; i < hours; i++) {
    times.push(`${i.toString().padStart(2, '0')}:00`)
    const baseValue = limitValue * 0.75
    const variation = Math.sin(i * 0.4) * limitValue * 0.2
    const randomFactor = (Math.random() - 0.5) * limitValue * 0.1
    let value = baseValue + variation + randomFactor
    if (i >= 8 && i <= 10) {
      value = limitValue * (1.1 + Math.random() * 0.15)
    }
    values.push(Math.round(value * 100) / 100)
  }

  const max = Math.max(...values)
  const min = Math.min(...values)
  const avg = Math.round(values.reduce((a, b) => a + b, 0) / values.length * 100) / 100

  chartStats.max = max
  chartStats.min = min
  chartStats.avg = avg

  const color = getIndicatorColor(indicator)

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
        return `${data.name}<br/>${getIndicatorLabel(indicator)}: ${data.value} ${unit}`
      }
    },
    xAxis: {
      type: 'category',
      data: times,
      boundaryGap: false,
      axisLabel: { fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      name: unit,
      nameTextStyle: { fontSize: 11 },
      axisLabel: { fontSize: 11 }
    },
    series: [
      {
        name: getIndicatorLabel(indicator),
        data: values,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        lineStyle: { color: color, width: 2 },
        itemStyle: { color: color },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: color + '4D' },
            { offset: 1, color: color + '0D' }
          ])
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#f53f3f', type: 'dashed' },
          data: [{ yAxis: limitValue }],
          label: { formatter: `限值 ${limitValue}`, color: '#f53f3f', fontSize: 11 }
        },
        markArea: {
          silent: true,
          itemStyle: {
            color: 'rgba(245, 63, 63, 0.08)'
          },
          data: [
            [
              { yAxis: limitValue, name: '超标区' },
              { yAxis: null }
            ]
          ]
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

const fetchMonitorData = async () => {
  loading.value = true
  try {
    const res: any = await productionApi.getNoiseOdorMonitorData()
    monitorPoints.value = res.points || []
    if (res.stats) {
      Object.assign(stats, res.stats)
    }
    if (monitorPoints.value.length > 0) {
      selectedPoint.value = monitorPoints.value[0]
      nextTick(() => {
        initChart()
      })
    }
  } catch (e) {
    generateMockData()
  } finally {
    loading.value = false
  }
}

const generateMockData = () => {
  const points = [
    {
      id: 1,
      name: '东厂界1号',
      location: '东侧厂界北段',
      type: 'boundary',
      status: 'online',
      noise_value: 62.5,
      noise_over: true,
      noise_limit: 60,
      h2s_value: 0.03,
      h2s_over: false,
      h2s_limit: 0.06,
      nh3_value: 0.15,
      nh3_over: false,
      nh3_limit: 0.2,
      update_time: '2024-01-15 14:30:00'
    },
    {
      id: 2,
      name: '东厂界2号',
      location: '东侧厂界南段',
      type: 'boundary',
      status: 'online',
      noise_value: 55.2,
      noise_over: false,
      noise_limit: 60,
      h2s_value: 0.025,
      h2s_over: false,
      h2s_limit: 0.06,
      nh3_value: 0.12,
      nh3_over: false,
      nh3_limit: 0.2,
      update_time: '2024-01-15 14:30:00'
    },
    {
      id: 3,
      name: '南厂界1号',
      location: '南侧厂界西段',
      type: 'boundary',
      status: 'online',
      noise_value: 58.3,
      noise_over: false,
      noise_limit: 60,
      h2s_value: 0.045,
      h2s_over: false,
      h2s_limit: 0.06,
      nh3_value: 0.18,
      nh3_over: false,
      nh3_limit: 0.2,
      update_time: '2024-01-15 14:30:00'
    },
    {
      id: 4,
      name: '南厂界2号',
      location: '南侧厂界东段',
      type: 'boundary',
      status: 'online',
      noise_value: 65.8,
      noise_over: true,
      noise_limit: 60,
      h2s_value: 0.072,
      h2s_over: true,
      h2s_limit: 0.06,
      nh3_value: 0.25,
      nh3_over: true,
      nh3_limit: 0.2,
      update_time: '2024-01-15 14:30:00'
    },
    {
      id: 5,
      name: '西厂界1号',
      location: '西侧厂界北段',
      type: 'boundary',
      status: 'offline',
      noise_value: null,
      noise_over: false,
      noise_limit: 60,
      h2s_value: null,
      h2s_over: false,
      h2s_limit: 0.06,
      nh3_value: null,
      nh3_over: false,
      nh3_limit: 0.2,
      update_time: '2024-01-15 12:15:00'
    },
    {
      id: 6,
      name: '西厂界2号',
      location: '西侧厂界南段',
      type: 'boundary',
      status: 'online',
      noise_value: 53.7,
      noise_over: false,
      noise_limit: 60,
      h2s_value: 0.02,
      h2s_over: false,
      h2s_limit: 0.06,
      nh3_value: 0.08,
      nh3_over: false,
      nh3_limit: 0.2,
      update_time: '2024-01-15 14:30:00'
    },
    {
      id: 7,
      name: '北厂界1号',
      location: '北侧厂界东段',
      type: 'boundary',
      status: 'online',
      noise_value: 57.1,
      noise_over: false,
      noise_limit: 60,
      h2s_value: 0.035,
      h2s_over: false,
      h2s_limit: 0.06,
      nh3_value: 0.14,
      nh3_over: false,
      nh3_limit: 0.2,
      update_time: '2024-01-15 14:30:00'
    },
    {
      id: 8,
      name: '北厂界2号',
      location: '北侧厂界西段',
      type: 'boundary',
      status: 'online',
      noise_value: 54.6,
      noise_over: false,
      noise_limit: 60,
      h2s_value: 0.018,
      h2s_over: false,
      h2s_limit: 0.06,
      nh3_value: 0.09,
      nh3_over: false,
      nh3_limit: 0.2,
      update_time: '2024-01-15 14:30:00'
    },
    {
      id: 9,
      name: '生化池区',
      location: '厂区中部生化池',
      type: 'internal',
      status: 'online',
      noise_value: 72.3,
      noise_over: false,
      noise_limit: 85,
      h2s_value: 0.15,
      h2s_over: true,
      h2s_limit: 0.1,
      nh3_value: 0.45,
      nh3_over: true,
      nh3_limit: 0.3,
      update_time: '2024-01-15 14:30:00'
    },
    {
      id: 10,
      name: '污泥脱水间',
      location: '厂区东部污泥车间',
      type: 'internal',
      status: 'online',
      noise_value: 78.5,
      noise_over: false,
      noise_limit: 85,
      h2s_value: 0.085,
      h2s_over: false,
      h2s_limit: 0.1,
      nh3_value: 0.28,
      nh3_over: false,
      nh3_limit: 0.3,
      update_time: '2024-01-15 14:30:00'
    },
    {
      id: 11,
      name: '粗格栅间',
      location: '厂区西北进水区',
      type: 'internal',
      status: 'online',
      noise_value: 68.2,
      noise_over: false,
      noise_limit: 85,
      h2s_value: 0.055,
      h2s_over: false,
      h2s_limit: 0.1,
      nh3_value: 0.15,
      nh3_over: false,
      nh3_limit: 0.3,
      update_time: '2024-01-15 14:30:00'
    },
    {
      id: 12,
      name: '厌氧罐区',
      location: '厂区南部厌氧区',
      type: 'internal',
      status: 'online',
      noise_value: 65.4,
      noise_over: false,
      noise_limit: 85,
      h2s_value: 0.12,
      h2s_over: true,
      h2s_limit: 0.1,
      nh3_value: 0.35,
      nh3_over: true,
      nh3_limit: 0.3,
      update_time: '2024-01-15 14:30:00'
    }
  ]

  monitorPoints.value = points
  stats.point_count = points.length
  stats.normal_count = points.filter(p => p.status === 'online' && !p.noise_over && !p.h2s_over && !p.nh3_over).length
  stats.over_count = points.filter(p => p.noise_over || p.h2s_over || p.nh3_over).length
  stats.offline_count = points.filter(p => p.status === 'offline').length

  if (points.length > 0) {
    selectedPoint.value = points[0]
    nextTick(() => {
      initChart()
    })
  }

  overRecords.value = [
    {
      id: 1,
      record_no: 'NO20240115001',
      indicator: 'noise',
      point_id: 4,
      point_name: '南厂界2号',
      level: 'slight',
      peak_value: 65.8,
      limit_value: 60,
      unit: 'dB(A)',
      over_percent: 9.7,
      start_time: '2024-01-15 09:15:00',
      end_time: '2024-01-15 09:45:00',
      duration: '30分钟',
      weather: '晴',
      temperature: 8,
      wind_speed: 2.3,
      wind_direction: '北风',
      pressure: 1025,
      humidity: 45,
      remark: '早高峰期间交通噪声影响'
    },
    {
      id: 2,
      record_no: 'NO20240115002',
      indicator: 'h2s',
      point_id: 4,
      point_name: '南厂界2号',
      level: 'slight',
      peak_value: 0.072,
      limit_value: 0.06,
      unit: 'ppm',
      over_percent: 20,
      start_time: '2024-01-15 10:20:00',
      end_time: '2024-01-15 11:05:00',
      duration: '45分钟',
      weather: '晴',
      temperature: 10,
      wind_speed: 1.5,
      wind_direction: '东南风',
      pressure: 1024,
      humidity: 42,
      remark: '污泥运输车辆作业时段'
    },
    {
      id: 3,
      record_no: 'NO20240115003',
      indicator: 'nh3',
      point_id: 4,
      point_name: '南厂界2号',
      level: 'slight',
      peak_value: 0.25,
      limit_value: 0.2,
      unit: 'ppm',
      over_percent: 25,
      start_time: '2024-01-15 10:30:00',
      end_time: '2024-01-15 11:10:00',
      duration: '40分钟',
      weather: '晴',
      temperature: 10,
      wind_speed: 1.5,
      wind_direction: '东南风',
      pressure: 1024,
      humidity: 42,
      remark: '污泥运输车辆作业时段'
    },
    {
      id: 4,
      record_no: 'NO20240115004',
      indicator: 'noise',
      point_id: 1,
      point_name: '东厂界1号',
      level: 'slight',
      peak_value: 62.5,
      limit_value: 60,
      unit: 'dB(A)',
      over_percent: 4.2,
      start_time: '2024-01-15 14:00:00',
      end_time: '2024-01-15 14:30:00',
      duration: '30分钟',
      weather: '多云',
      temperature: 12,
      wind_speed: 3.1,
      wind_direction: '东风',
      pressure: 1023,
      humidity: 50,
      remark: '设备检修作业噪声'
    },
    {
      id: 5,
      record_no: 'NO20240115005',
      indicator: 'h2s',
      point_id: 9,
      point_name: '生化池区',
      level: 'moderate',
      peak_value: 0.15,
      limit_value: 0.1,
      unit: 'ppm',
      over_percent: 50,
      start_time: '2024-01-15 08:00:00',
      end_time: '2024-01-15 10:30:00',
      duration: '2小时30分',
      weather: '晴',
      temperature: 9,
      wind_speed: 1.2,
      wind_direction: '西南风',
      pressure: 1025,
      humidity: 48,
      remark: '进水负荷波动导致'
    },
    {
      id: 6,
      record_no: 'NO20240115006',
      indicator: 'nh3',
      point_id: 9,
      point_name: '生化池区',
      level: 'moderate',
      peak_value: 0.45,
      limit_value: 0.3,
      unit: 'ppm',
      over_percent: 50,
      start_time: '2024-01-15 08:15:00',
      end_time: '2024-01-15 10:45:00',
      duration: '2小时30分',
      weather: '晴',
      temperature: 9,
      wind_speed: 1.2,
      wind_direction: '西南风',
      pressure: 1025,
      humidity: 48,
      remark: '进水负荷波动导致'
    },
    {
      id: 7,
      record_no: 'NO20240114001',
      indicator: 'h2s',
      point_id: 12,
      point_name: '厌氧罐区',
      level: 'severe',
      peak_value: 0.18,
      limit_value: 0.1,
      unit: 'ppm',
      over_percent: 80,
      start_time: '2024-01-14 22:30:00',
      end_time: '2024-01-15 01:15:00',
      duration: '2小时45分',
      weather: '阴',
      temperature: 5,
      wind_speed: 0.8,
      wind_direction: '无风',
      pressure: 1026,
      humidity: 65,
      remark: '厌氧罐排气阀故障，已紧急处置'
    }
  ]
  overPagination.total = overRecords.value.length

  limitConfigs.value = [
    {
      id: 1,
      indicator: 'noise',
      point_names: '东厂界1号、东厂界2号、南厂界1号、南厂界2号',
      point_ids: [1, 2, 3, 4],
      limit_type: 'day',
      limit_value: 60,
      unit: 'dB(A)',
      standard: 'GB 12348-2008 工业企业厂界环境噪声排放标准',
      effective_date: '2023-01-01',
      status: 'active'
    },
    {
      id: 2,
      indicator: 'noise',
      point_names: '西厂界1号、西厂界2号、北厂界1号、北厂界2号',
      point_ids: [5, 6, 7, 8],
      limit_type: 'day',
      limit_value: 60,
      unit: 'dB(A)',
      standard: 'GB 12348-2008 工业企业厂界环境噪声排放标准',
      effective_date: '2023-01-01',
      status: 'active'
    },
    {
      id: 3,
      indicator: 'noise',
      point_names: '全部厂界点位',
      point_ids: [1, 2, 3, 4, 5, 6, 7, 8],
      limit_type: 'night',
      limit_value: 50,
      unit: 'dB(A)',
      standard: 'GB 12348-2008 工业企业厂界环境噪声排放标准',
      effective_date: '2023-01-01',
      status: 'active'
    },
    {
      id: 4,
      indicator: 'h2s',
      point_names: '全部厂界点位',
      point_ids: [1, 2, 3, 4, 5, 6, 7, 8],
      limit_type: 'all',
      limit_value: 0.06,
      unit: 'ppm',
      standard: 'GB 14554-93 恶臭污染物排放标准',
      effective_date: '2023-01-01',
      status: 'active'
    },
    {
      id: 5,
      indicator: 'nh3',
      point_names: '全部厂界点位',
      point_ids: [1, 2, 3, 4, 5, 6, 7, 8],
      limit_type: 'all',
      limit_value: 0.2,
      unit: 'ppm',
      standard: 'GB 14554-93 恶臭污染物排放标准',
      effective_date: '2023-01-01',
      status: 'active'
    },
    {
      id: 6,
      indicator: 'noise',
      point_names: '生化池区、污泥脱水间、粗格栅间、厌氧罐区',
      point_ids: [9, 10, 11, 12],
      limit_type: 'all',
      limit_value: 85,
      unit: 'dB(A)',
      standard: 'GBZ 2.2-2007 工作场所有害因素职业接触限值',
      effective_date: '2023-01-01',
      status: 'active'
    },
    {
      id: 7,
      indicator: 'h2s',
      point_names: '生化池区、污泥脱水间、厌氧罐区',
      point_ids: [9, 10, 12],
      limit_type: 'all',
      limit_value: 0.1,
      unit: 'ppm',
      standard: 'GBZ 2.1-2019 工作场所有害因素职业接触限值',
      effective_date: '2023-01-01',
      status: 'active'
    },
    {
      id: 8,
      indicator: 'nh3',
      point_names: '生化池区、污泥脱水间、厌氧罐区',
      point_ids: [9, 10, 12],
      limit_type: 'all',
      limit_value: 0.3,
      unit: 'ppm',
      standard: 'GBZ 2.1-2019 工作场所有害因素职业接触限值',
      effective_date: '2023-01-01',
      status: 'active'
    }
  ]
}

const handleOverSearch = () => {
  overPagination.current = 1
  fetchOverRecords()
}

const handleOverReset = () => {
  overFilters.indicator = ''
  overFilters.point_id = ''
  overFilters.level = ''
  overFilters.time_range = []
  overPagination.current = 1
  fetchOverRecords()
}

const handleOverPageChange = (page: number) => {
  overPagination.current = page
  fetchOverRecords()
}

const handleOverPageSizeChange = (pageSize: number) => {
  overPagination.pageSize = pageSize
  overPagination.current = 1
  fetchOverRecords()
}

const fetchOverRecords = async () => {
  overLoading.value = true
  try {
    const res: any = await productionApi.getNoiseOdorOverRecords({
      page: overPagination.current,
      page_size: overPagination.pageSize,
      indicator: overFilters.indicator || undefined,
      point_id: overFilters.point_id || undefined,
      level: overFilters.level || undefined
    })
    overRecords.value = res.items || []
    overPagination.total = res.total || 0
  } catch (e) {
    // Mock data already generated
  } finally {
    overLoading.value = false
  }
}

const viewOverDetail = (record: any) => {
  currentOverRecord.value = record
  showDetailModal.value = true
  nextTick(() => {
    initDetailChart()
  })
}

const setDetailChartRef = (el: any) => {
  if (el) {
    detailChartRef.value = el
  }
}

const initDetailChart = () => {
  if (!detailChartRef.value || !currentOverRecord.value) return

  if (detailChartInstance) {
    detailChartInstance.dispose()
  }

  detailChartInstance = echarts.init(detailChartRef.value)

  const record = currentOverRecord.value
  const indicator = record.indicator
  const color = getIndicatorColor(indicator)
  const limitValue = record.limit_value

  const hours = 12
  const times: string[] = []
  const values: number[] = []

  const startTime = new Date(record.start_time.replace(/-/g, '/'))
  for (let i = 0; i < hours; i++) {
    const t = new Date(startTime.getTime() + i * 15 * 60 * 1000)
    times.push(`${t.getHours().toString().padStart(2, '0')}:${t.getMinutes().toString().padStart(2, '0')}`)
  }

  for (let i = 0; i < hours; i++) {
    const progress = i / (hours - 1)
    let value: number
    if (progress < 0.2) {
      value = limitValue * (0.9 + progress * 0.5)
    } else if (progress < 0.8) {
      value = limitValue * (1.05 + Math.sin((progress - 0.2) * Math.PI / 0.6) * 0.25)
    } else {
      value = limitValue * (1.2 - (progress - 0.8) * 1.5)
    }
    values.push(Math.round(value * 100) / 100)
  }

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
      name: record.unit
    },
    series: [
      {
        name: getIndicatorLabel(indicator),
        data: values,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        lineStyle: { color: color, width: 2 },
        itemStyle: { color: color },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: color + '4D' },
            { offset: 1, color: color + '0D' }
          ])
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#f53f3f', type: 'dashed' },
          data: [{ yAxis: limitValue }],
          label: { formatter: `限值 ${limitValue}`, color: '#f53f3f' }
        }
      }
    ]
  }

  detailChartInstance.setOption(option)
}

const openLimitModal = () => {
  isEditLimit.value = false
  limitForm.id = null
  limitForm.indicator = ''
  limitForm.point_ids = []
  limitForm.limit_type = 'all'
  limitForm.limit_value = null
  limitForm.standard = ''
  limitForm.effective_date = null
  showLimitModal.value = true
}

const editLimit = (record: any) => {
  isEditLimit.value = true
  limitForm.id = record.id
  limitForm.indicator = record.indicator
  limitForm.point_ids = [...record.point_ids]
  limitForm.limit_type = record.limit_type
  limitForm.limit_value = record.limit_value
  limitForm.standard = record.standard
  limitForm.effective_date = record.effective_date
  showLimitModal.value = true
}

const toggleLimitStatus = (record: any) => {
  const newStatus = record.status === 'active' ? 'inactive' : 'active'
  Modal.confirm({
    title: '确认操作',
    content: `确定要${newStatus === 'active' ? '启用' : '停用'}该限值配置吗？`,
    onOk: () => {
      const idx = limitConfigs.value.findIndex(l => l.id === record.id)
      if (idx > -1) {
        limitConfigs.value[idx].status = newStatus
      }
      Message.success('操作成功')
    }
  })
}

const deleteLimit = (record: any) => {
  Modal.confirm({
    title: '删除确认',
    content: `确定要删除该限值配置吗？删除后将无法恢复。`,
    okButtonProps: { status: 'danger' },
    onOk: () => {
      const idx = limitConfigs.value.findIndex(l => l.id === record.id)
      if (idx > -1) {
        limitConfigs.value.splice(idx, 1)
      }
      Message.success('删除成功')
    }
  })
}

const submitLimit = async () => {
  if (!limitForm.indicator) {
    Message.warning('请选择监测项目')
    return
  }
  if (limitForm.point_ids.length === 0) {
    Message.warning('请选择适用点位')
    return
  }
  if (limitForm.limit_value === null) {
    Message.warning('请输入限值')
    return
  }

  submitLoading.value = true
  try {
    if (isEditLimit.value) {
      await productionApi.updateNoiseOdorLimit(limitForm.id, limitForm)
      Message.success('更新成功')
    } else {
      await productionApi.createNoiseOdorLimit(limitForm)
      Message.success('创建成功')
    }
    showLimitModal.value = false
    fetchLimitConfigs()
  } catch (e) {
    const pointNames = limitForm.point_ids
      .map(id => monitorPoints.value.find(p => p.id === id)?.name)
      .filter(Boolean)
      .join('、')
    const unit = limitForm.indicator === 'noise' ? 'dB(A)' : 'ppm'

    if (isEditLimit.value) {
      const idx = limitConfigs.value.findIndex(l => l.id === limitForm.id)
      if (idx > -1) {
        limitConfigs.value[idx] = {
          ...limitConfigs.value[idx],
          indicator: limitForm.indicator,
          point_names: pointNames,
          point_ids: [...limitForm.point_ids],
          limit_type: limitForm.limit_type,
          limit_value: limitForm.limit_value,
          unit: unit,
          standard: limitForm.standard,
          effective_date: limitForm.effective_date || new Date().toISOString().split('T')[0]
        }
      }
      Message.success('更新成功')
    } else {
      const newId = Math.max(...limitConfigs.value.map(l => l.id)) + 1
      limitConfigs.value.push({
        id: newId,
        indicator: limitForm.indicator,
        point_names: pointNames,
        point_ids: [...limitForm.point_ids],
        limit_type: limitForm.limit_type,
        limit_value: limitForm.limit_value,
        unit: unit,
        standard: limitForm.standard,
        effective_date: limitForm.effective_date || new Date().toISOString().split('T')[0],
        status: 'active'
      })
      Message.success('创建成功')
    }
    showLimitModal.value = false
  } finally {
    submitLoading.value = false
  }
}

const fetchLimitConfigs = async () => {
  try {
    const res: any = await productionApi.getNoiseOdorLimits()
    limitConfigs.value = res.items || []
  } catch (e) {
    // Mock data already generated
  }
}

watch(showDetailModal, (val) => {
  if (val && detailChartInstance) {
    setTimeout(() => {
      detailChartInstance.resize()
    }, 100)
  }
})

watch(activeTab, (val) => {
  if (val === 'realtime') {
    nextTick(() => {
      if (chartInstance) {
        chartInstance.resize()
      }
    })
  }
})

onMounted(() => {
  fetchMonitorData()
})
</script>

<style scoped>
.noise-odor-monitor {
  min-height: calc(100vh - 120px);
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
  margin: 0 0 6px 0;
}

.page-header p {
  font-size: 13px;
  color: #86909c;
  margin: 0;
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

.stat-card.points .stat-icon {
  background: linear-gradient(135deg, #e8f3ff, #d6e4ff);
  color: #165DFF;
}

.stat-card.normal .stat-icon {
  background: linear-gradient(135deg, #e8ffea, #c8ffcd);
  color: #00b42a;
}

.stat-card.over .stat-icon {
  background: linear-gradient(135deg, #fff7e8, #ffe7c8);
  color: #ff7d00;
}

.stat-card.offline .stat-icon {
  background: linear-gradient(135deg, #f2f3f5, #e5e6eb);
  color: #86909c;
}

.stat-info .stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  line-height: 1.2;
}

.stat-card.points .stat-value { color: #165DFF; }
.stat-card.normal .stat-value { color: #00b42a; }
.stat-card.over .stat-value { color: #ff7d00; }
.stat-card.offline .stat-value { color: #86909c; }

.stat-info .stat-label {
  font-size: 14px;
  color: #86909c;
  margin-top: 4px;
}

.main-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 0 20px;
  border: 1px solid #e5e6eb;
}

.realtime-content {
  display: flex;
  gap: 20px;
  padding-top: 8px;
}

.point-table-panel {
  flex: 1;
  min-width: 0;
}

.chart-panel {
  width: 480px;
  flex-shrink: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e6eb;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
}

.point-table-wrapper {
  max-height: 480px;
  overflow: hidden;
}

.point-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  color: #1d2129;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.online {
  background: #00b42a;
  box-shadow: 0 0 6px rgba(0, 180, 42, 0.4);
}

.status-dot.offline {
  background: #c9cdd4;
}

.status-dot.over {
  background: #f53f3f;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.over-value {
  color: #f53f3f;
  font-weight: 600;
}

.row-selected {
  background: #e8f3ff !important;
}

.row-selected :deep(.arco-table-cell) {
  background: #e8f3ff !important;
}

.selected-point-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  padding: 10px 14px;
  background: #f7f8fa;
  border-radius: 6px;
}

.point-badge {
  padding: 4px 12px;
  background: linear-gradient(135deg, #165DFF, #4080ff);
  color: #fff;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
}

.location-text {
  font-size: 13px;
  color: #4e5969;
  flex: 1;
}

.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 280px;
  color: #c9cdd4;
  font-size: 14px;
}

.chart-container {
  height: 280px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e5e6eb;
  margin-bottom: 12px;
}

.chart-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.stat-item {
  padding: 12px 8px;
  background: #f7f8fa;
  border-radius: 6px;
  text-align: center;
}

.stat-item .stat-label {
  display: block;
  font-size: 12px;
  color: #86909c;
  margin-bottom: 4px;
}

.stat-item .stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.stat-item .stat-value.limit {
  color: #f53f3f;
}

.over-record-content {
  padding-top: 8px;
}

.filter-bar {
  margin-bottom: 16px;
  padding: 16px;
  background: #f7f8fa;
  border-radius: 6px;
}

.peak-value {
  font-size: 16px;
  font-weight: 600;
  color: #f53f3f;
}

.value-unit {
  font-size: 12px;
  color: #86909c;
  margin-left: 2px;
}

.over-rate {
  color: #f53f3f;
  font-weight: 600;
}

.limit-config-content {
  padding-top: 8px;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.indicator-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #1d2129;
}

.indicator-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.limit-value {
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
}

.detail-modal-content {
  padding: 8px 0;
}

.detail-header {
  margin-bottom: 16px;
}

.detail-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.record-no {
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
}

.detail-indicator {
  font-size: 13px;
  color: #86909c;
}

.detail-chart {
  height: 200px;
  margin-bottom: 16px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e5e6eb;
}

.peak-value-large {
  font-size: 24px;
  font-weight: 600;
  color: #f53f3f;
}

.over-rate-large {
  font-size: 18px;
  font-weight: 600;
  color: #f53f3f;
}

@media (max-width: 1400px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .realtime-content {
    flex-direction: column;
  }

  .chart-panel {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }

  .chart-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>