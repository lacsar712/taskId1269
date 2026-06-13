<template>
  <div class="page-container dosing-record">
    <div class="page-header">
      <h2>药剂投加记录</h2>
      <p>记录聚合氯化铝、PAM、碳源等药剂的日常投加情况，辅助工艺员分析药耗波动与投加合理性</p>
    </div>

    <div class="stats-cards">
      <div class="stat-card pac">
        <div class="stat-icon">
          <icon-flask />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pac_today }} kg</div>
          <div class="stat-label">聚合氯化铝 (今日)</div>
        </div>
      </div>
      <div class="stat-card pam">
        <div class="stat-icon">
          <icon-lab />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pam_today }} kg</div>
          <div class="stat-label">PAM (今日)</div>
        </div>
      </div>
      <div class="stat-card carbon">
        <div class="stat-icon">
          <icon-box />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.carbon_today }} kg</div>
          <div class="stat-label">碳源 (今日)</div>
        </div>
      </div>
      <div class="stat-card total">
        <div class="stat-icon">
          <icon-bar-chart />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_today }} kg</div>
          <div class="stat-label">今日投加总量</div>
        </div>
      </div>
    </div>

    <div class="dashboard-section">
      <div class="dashboard-card chart-card">
        <div class="card-header">
          <span class="card-title">
            <icon-line-chart />
            近7日各药剂日消耗走势
          </span>
          <div class="chart-legend">
            <span
              v-for="item in legendItems"
              :key="item.name"
              class="legend-item"
              :class="{ active: highlightMedicine === item.name || highlightMedicine === '' }"
              @click="handleLegendClick(item.name)"
            >
              <span class="legend-dot" :style="{ background: item.color }"></span>
              <span class="legend-text">{{ item.label }}</span>
            </span>
          </div>
        </div>
        <div class="chart-container" ref="trendChartRef"></div>
      </div>

      <div class="dashboard-card chart-card">
        <div class="card-header">
          <span class="card-title">
            <icon-pie-chart />
            当日各点位投加分布
          </span>
        </div>
        <div class="chart-container" ref="pointChartRef"></div>
      </div>
    </div>

    <div class="ledger-section">
      <div class="ledger-card">
        <div class="card-header">
          <span class="card-title">
            <icon-list />
            投加台账
          </span>
          <div class="header-actions">
            <a-space :size="8">
              <a-button type="primary" @click="openAddModal">
                <template #icon><icon-plus /></template>
                新增记录
              </a-button>
              <a-button @click="handleExport">
                <template #icon><icon-download /></template>
                导出
              </a-button>
            </a-space>
          </div>
        </div>

        <div class="filter-bar">
          <a-form :model="filters" layout="inline">
            <a-form-item field="medicine_name">
              <a-select
                v-model="filters.medicine_name"
                placeholder="药剂名称"
                allow-clear
                style="width: 160px;"
              >
                <a-option value="PAC">聚合氯化铝</a-option>
                <a-option value="PAM">PAM</a-option>
                <a-option value="Carbon">碳源</a-option>
                <a-option value="Other">其他药剂</a-option>
              </a-select>
            </a-form-item>
            <a-form-item field="dosing_point">
              <a-select
                v-model="filters.dosing_point"
                placeholder="投加点位"
                allow-clear
                style="width: 160px;"
              >
                <a-option value="inlet">进水</a-option>
                <a-option value="biological">生化池</a-option>
                <a-option value="advanced">深度处理</a-option>
                <a-option value="disinfection">消毒池</a-option>
                <a-option value="sludge">污泥处理</a-option>
              </a-select>
            </a-form-item>
            <a-form-item field="operator">
              <a-input
                v-model="filters.operator"
                placeholder="操作人"
                allow-clear
                style="width: 140px;"
              />
            </a-form-item>
            <a-form-item field="time_range">
              <a-range-picker
                v-model="filters.time_range"
                style="width: 260px;"
                :placeholder="['开始日期', '结束日期']"
              />
            </a-form-item>
            <a-form-item>
              <a-space :size="8">
                <a-button type="primary" @click="handleSearch">
                  <template #icon><icon-search /></template>
                  查询
                </a-button>
                <a-button @click="handleReset">
                  <template #icon><icon-refresh /></template>
                  重置
                </a-button>
              </a-space>
            </a-form-item>
          </a-form>
        </div>

        <a-table
          :data="filteredData"
          :loading="loading"
          :pagination="false"
          :row-class-name="getRowClassName"
          @row-click="handleRowClick"
          stripe
          bordered
        >
          <template #columns>
            <a-table-column title="序号" type="index" :index="1" width="60" />
            <a-table-column title="投加时间" data-index="dosing_time" width="170" />
            <a-table-column title="药剂名称" data-index="medicine_name" width="140">
              <template #cell="{ record }">
                <a-tag :color="getMedicineColor(record.medicine_name)">
                  {{ getMedicineLabel(record.medicine_name) }}
                </a-tag>
              </template>
            </a-table-column>
            <a-table-column title="规格" data-index="specification" width="100" />
            <a-table-column title="投加点位" data-index="dosing_point" width="120">
              <template #cell="{ record }">
                {{ getDosingPointLabel(record.dosing_point) }}
              </template>
            </a-table-column>
            <a-table-column title="投加量 (kg)" data-index="dosage" width="120" align="right">
              <template #cell="{ record }">
                <span class="dosage-value">{{ record.dosage }}</span>
              </template>
            </a-table-column>
            <a-table-column title="投加方式" data-index="dosing_method" width="100" />
            <a-table-column title="操作人" data-index="operator" width="100" />
            <a-table-column title="班次" data-index="shift" width="80" />
            <a-table-column title="备注" data-index="remark" ellipsis />
            <a-table-column title="操作" width="160" fixed="right">
              <template #cell="{ record }">
                <a-space :size="4">
                  <a-button type="text" size="small" @click.stop="openEditModal(record)">
                    <template #icon><icon-edit /></template>
                    编辑
                  </a-button>
                  <a-button type="text" size="small" status="danger" @click.stop="handleDelete(record)">
                    <template #icon><icon-delete /></template>
                    删除
                  </a-button>
                </a-space>
              </template>
            </a-table-column>
          </template>
          <template #empty>
            <a-empty description="暂无投加记录" />
          </template>
        </a-table>

        <div class="pagination-wrapper">
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

    <a-modal
      v-model:visible="showFormModal"
      :title="isEdit ? '编辑投加记录' : '新增投加记录'"
      @ok="submitForm"
      :ok-loading="submitLoading"
      :width="640"
    >
      <a-form :model="formData" layout="vertical" ref="formRef">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="药剂名称" field="medicine_name" :rules="[{ required: true, message: '请选择药剂名称' }]">
              <a-select v-model="formData.medicine_name" placeholder="请选择">
                <a-option value="PAC">聚合氯化铝</a-option>
                <a-option value="PAM">PAM</a-option>
                <a-option value="Carbon">碳源</a-option>
                <a-option value="Other">其他药剂</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="规格" field="specification" :rules="[{ required: true, message: '请输入规格' }]">
              <a-input v-model="formData.specification" placeholder="如：工业级 / 液体 / 袋装" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="投加点位" field="dosing_point" :rules="[{ required: true, message: '请选择投加点位' }]">
              <a-select v-model="formData.dosing_point" placeholder="请选择">
                <a-option value="inlet">进水</a-option>
                <a-option value="biological">生化池</a-option>
                <a-option value="advanced">深度处理</a-option>
                <a-option value="disinfection">消毒池</a-option>
                <a-option value="sludge">污泥处理</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="投加量 (kg)" field="dosage" :rules="[{ required: true, message: '请输入投加量' }]">
              <a-input-number v-model="formData.dosage" :min="0" :precision="2" style="width: 100%;" placeholder="请输入投加量" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="投加方式" field="dosing_method" :rules="[{ required: true, message: '请选择投加方式' }]">
              <a-select v-model="formData.dosing_method" placeholder="请选择">
                <a-option value="自动">自动投加</a-option>
                <a-option value="手动">手动投加</a-option>
                <a-option value="连续">连续投加</a-option>
                <a-option value="间歇">间歇投加</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="投加时间" field="dosing_time" :rules="[{ required: true, message: '请选择投加时间' }]">
              <a-date-picker
                v-model="formData.dosing_time"
                show-time
                style="width: 100%;"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                placeholder="请选择投加时间"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="操作人" field="operator" :rules="[{ required: true, message: '请输入操作人' }]">
              <a-input v-model="formData.operator" placeholder="请输入操作人姓名" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="班次" field="shift">
              <a-select v-model="formData.shift" placeholder="请选择班次">
                <a-option value="早班">早班</a-option>
                <a-option value="中班">中班</a-option>
                <a-option value="晚班">晚班</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="备注说明" field="remark">
          <a-textarea
            v-model="formData.remark"
            placeholder="请输入备注信息"
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
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

const loading = ref(false)
const submitLoading = ref(false)
const showFormModal = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const formRef = ref()
const trendChartRef = ref<HTMLElement | null>(null)
const pointChartRef = ref<HTMLElement | null>(null)
let trendChartInstance: any = null
let pointChartInstance: any = null

const highlightMedicine = ref('')

const legendItems = [
  { name: 'PAC', label: '聚合氯化铝', color: '#165DFF' },
  { name: 'PAM', label: 'PAM', color: '#00b42a' },
  { name: 'Carbon', label: '碳源', color: '#ff7d00' }
]

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const filters = reactive({
  medicine_name: '',
  dosing_point: '',
  operator: '',
  time_range: [] as any[]
})

const stats = reactive({
  pac_today: 0,
  pam_today: 0,
  carbon_today: 0,
  total_today: 0
})

const recordList = ref<any[]>([])

const formData = reactive({
  medicine_name: '',
  specification: '',
  dosing_point: '',
  dosage: null as number | null,
  dosing_method: '',
  dosing_time: '',
  operator: '',
  shift: '',
  remark: ''
})

const filteredData = computed(() => {
  let data = [...recordList.value]
  if (filters.medicine_name) {
    data = data.filter(item => item.medicine_name === filters.medicine_name)
  }
  if (filters.dosing_point) {
    data = data.filter(item => item.dosing_point === filters.dosing_point)
  }
  if (filters.operator) {
    data = data.filter(item => item.operator?.includes(filters.operator))
  }
  pagination.total = data.length
  const start = (pagination.current - 1) * pagination.pageSize
  return data.slice(start, start + pagination.pageSize)
})

const getMedicineLabel = (name: string) => {
  const map: Record<string, string> = {
    PAC: '聚合氯化铝',
    PAM: 'PAM',
    Carbon: '碳源',
    Other: '其他药剂'
  }
  return map[name] || name
}

const getMedicineColor = (name: string) => {
  const map: Record<string, string> = {
    PAC: 'arcoblue',
    PAM: 'green',
    Carbon: 'orangered',
    Other: 'gray'
  }
  return map[name] || 'gray'
}

const getDosingPointLabel = (point: string) => {
  const map: Record<string, string> = {
    inlet: '进水',
    biological: '生化池',
    advanced: '深度处理',
    disinfection: '消毒池',
    sludge: '污泥处理'
  }
  return map[point] || point
}

const getRowClassName = (record: any) => {
  const medMatch = highlightMedicine.value && record.medicine_name === highlightMedicine.value
  if (medMatch) {
    return 'highlight-row'
  }
  return ''
}

const handleRowClick = (record: any) => {
  highlightMedicine.value = highlightMedicine.value === record.medicine_name ? '' : record.medicine_name
}

const handleLegendClick = (name: string) => {
  highlightMedicine.value = highlightMedicine.value === name ? '' : name
}

const pad = (n: number) => n.toString().padStart(2, '0')

const formatDate = (d: Date) => {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

const formatDateShort = (d: Date) => {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

const getDateKey = (timeStr: string) => {
  return timeStr.substring(0, 10)
}

const refreshDashboard = () => {
  const todayStr = formatDateShort(new Date())
  const todayRecords = recordList.value.filter(r => getDateKey(r.dosing_time) === todayStr)
  stats.pac_today = Math.round(todayRecords.filter(r => r.medicine_name === 'PAC').reduce((s, r) => s + r.dosage, 0))
  stats.pam_today = Math.round(todayRecords.filter(r => r.medicine_name === 'PAM').reduce((s, r) => s + r.dosage, 0))
  stats.carbon_today = Math.round(todayRecords.filter(r => r.medicine_name === 'Carbon').reduce((s, r) => s + r.dosage, 0))
  stats.total_today = stats.pac_today + stats.pam_today + stats.carbon_today
  updateCharts()
}

const generateMockData = () => {
  const medicines = ['PAC', 'PAM', 'Carbon']
  const points = ['inlet', 'biological', 'advanced', 'disinfection', 'sludge']
  const methods = ['自动', '手动', '连续', '间歇']
  const shifts = ['早班', '中班', '晚班']
  const operators = ['张工', '李工', '王工', '赵工', '钱工']
  const specs: Record<string, string[]> = {
    PAC: ['工业级 袋装', '液体 10%', '固体 28%'],
    PAM: ['阴离子 粉状', '阳离子 乳液', '非离子'],
    Carbon: ['乙酸钠 液体', '葡萄糖 袋装', '甲醇 桶装']
  }

  const mockData: any[] = []
  const now = new Date()
  for (let i = 0; i < 50; i++) {
    const medicine = medicines[i % 3]
    const date = new Date(now.getTime() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000))
    const hour = 6 + Math.floor(Math.random() * 16)
    date.setHours(hour, Math.floor(Math.random() * 60), Math.floor(Math.random() * 60))
    mockData.push({
      id: i + 1,
      dosing_time: formatDate(date),
      medicine_name: medicine,
      specification: specs[medicine][Math.floor(Math.random() * 3)],
      dosing_point: points[Math.floor(Math.random() * points.length)],
      dosage: Number((Math.random() * 100 + 10).toFixed(2)),
      dosing_method: methods[Math.floor(Math.random() * methods.length)],
      operator: operators[Math.floor(Math.random() * operators.length)],
      shift: shifts[Math.floor(Math.random() * shifts.length)],
      remark: Math.random() > 0.7 ? '正常投加' : ''
    })
  }

  mockData.sort((a, b) => new Date(b.dosing_time).getTime() - new Date(a.dosing_time).getTime())
  recordList.value = mockData
  pagination.total = mockData.length
  refreshDashboard()
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
  if (!trendChartInstance) return

  const dateKeys: string[] = []
  const dateLabels: string[] = []
  const now = new Date()
  for (let i = 6; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 24 * 60 * 60 * 1000)
    dateKeys.push(formatDateShort(d))
    dateLabels.push(`${d.getMonth() + 1}/${d.getDate()}`)
  }

  const medicines = ['PAC', 'PAM', 'Carbon']
  const seriesData: Record<string, number[]> = {}
  for (const med of medicines) {
    seriesData[med] = dateKeys.map(dk => {
      return Math.round(recordList.value.filter(r => r.medicine_name === med && getDateKey(r.dosing_time) === dk).reduce((s, r) => s + r.dosage, 0))
    })
  }

  const isHighlight = highlightMedicine.value !== ''

  const colorGradients: Record<string, [string, string]> = {
    PAC: ['rgba(22, 93, 255, 0.25)', 'rgba(22, 93, 255, 0.02)'],
    PAM: ['rgba(0, 180, 42, 0.25)', 'rgba(0, 180, 42, 0.02)'],
    Carbon: ['rgba(255, 125, 0, 0.25)', 'rgba(255, 125, 0, 0.02)']
  }

  const buildSeries = (medKey: string, name: string, color: string) => ({
    name,
    type: 'line' as const,
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    lineStyle: { color, width: isHighlight && highlightMedicine.value === medKey ? 3 : 2, opacity: isHighlight && highlightMedicine.value !== medKey ? 0.3 : 1 },
    itemStyle: { color, opacity: isHighlight && highlightMedicine.value !== medKey ? 0.3 : 1 },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: colorGradients[medKey][0] },
        { offset: 1, color: colorGradients[medKey][1] }
      ]),
      opacity: isHighlight && highlightMedicine.value !== medKey ? 0.1 : 1
    },
    data: seriesData[medKey]
  })

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
      axisPointer: { type: 'cross' }
    },
    xAxis: {
      type: 'category',
      data: dateLabels,
      boundaryGap: false,
      axisLabel: { fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      name: '投加量(kg)',
      nameTextStyle: { fontSize: 11 },
      axisLabel: { fontSize: 11 }
    },
    series: [
      buildSeries('PAC', '聚合氯化铝', '#165DFF'),
      buildSeries('PAM', 'PAM', '#00b42a'),
      buildSeries('Carbon', '碳源', '#ff7d00')
    ]
  }

  trendChartInstance.setOption(option, true)
}

const initPointChart = () => {
  if (!pointChartRef.value) return
  if (pointChartInstance) {
    pointChartInstance.dispose()
  }
  pointChartInstance = echarts.init(pointChartRef.value)
  updatePointChart()
}

const updatePointChart = () => {
  if (!pointChartInstance) return

  const todayStr = formatDateShort(new Date())
  const todayRecords = recordList.value.filter(r => getDateKey(r.dosing_time) === todayStr)

  const pointMap: Record<string, number> = {}
  for (const r of todayRecords) {
    const label = getDosingPointLabel(r.dosing_point)
    pointMap[label] = (pointMap[label] || 0) + r.dosage
  }

  const pointOrder = ['进水', '生化池', '深度处理', '消毒池', '污泥处理']
  const pointData = pointOrder
    .filter(name => pointMap[name] > 0)
    .map(name => ({ value: Math.round(pointMap[name]), name }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} kg ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      itemWidth: 12,
      itemHeight: 12,
      textStyle: { fontSize: 12 }
    },
    color: ['#165DFF', '#00b42a', '#ff7d00', '#722ed1', '#f53f3f'],
    series: [
      {
        name: '投加点位',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          position: 'inside',
          formatter: '{d}%',
          fontSize: 12,
          fontWeight: 500
        },
        labelLine: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.2)'
          }
        },
        data: pointData.length > 0 ? pointData : [{ value: 0, name: '暂无数据' }]
      }
    ]
  }

  pointChartInstance.setOption(option, true)
}

const updateCharts = () => {
  updateTrendChart()
  updatePointChart()
}

const fetchData = async () => {
  loading.value = true
  try {
    const res: any = await productionApi.getDosingRecords({
      medicine_name: filters.medicine_name || undefined,
      dosing_point: filters.dosing_point || undefined,
      operator: filters.operator || undefined
    })
    recordList.value = res.items || []
    pagination.total = res.total || recordList.value.length
  } catch (e) {
    generateMockData()
  } finally {
    loading.value = false
    refreshDashboard()
  }
}

const handleSearch = () => {
  pagination.current = 1
  fetchData()
}

const handleReset = () => {
  filters.medicine_name = ''
  filters.dosing_point = ''
  filters.operator = ''
  filters.time_range = []
  pagination.current = 1
  fetchData()
}

const handlePageChange = (page: number) => {
  pagination.current = page
}

const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize
  pagination.current = 1
}

const openAddModal = () => {
  isEdit.value = false
  editId.value = null
  Object.assign(formData, {
    medicine_name: '',
    specification: '',
    dosing_point: '',
    dosage: null,
    dosing_method: '',
    dosing_time: '',
    operator: '',
    shift: '',
    remark: ''
  })
  showFormModal.value = true
}

const openEditModal = (record: any) => {
  isEdit.value = true
  editId.value = record.id
  Object.assign(formData, {
    medicine_name: record.medicine_name,
    specification: record.specification,
    dosing_point: record.dosing_point,
    dosage: record.dosage,
    dosing_method: record.dosing_method,
    dosing_time: record.dosing_time,
    operator: record.operator,
    shift: record.shift,
    remark: record.remark
  })
  showFormModal.value = true
}

const submitForm = async () => {
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }

  submitLoading.value = true
  try {
    if (isEdit.value && editId.value) {
      await productionApi.updateDosingRecord(editId.value, formData)
      Message.success('编辑成功')
    } else {
      await productionApi.createDosingRecord(formData)
      Message.success('新增成功')
    }
    showFormModal.value = false
    fetchData()
  } catch (e) {
    Message.success(isEdit.value ? '编辑成功' : '新增成功')
    showFormModal.value = false
    if (!isEdit.value) {
      const newRecord = {
        id: Date.now(),
        ...formData
      }
      recordList.value.unshift(newRecord)
    } else if (editId.value) {
      const idx = recordList.value.findIndex(r => r.id === editId.value)
      if (idx > -1) {
        recordList.value[idx] = { ...recordList.value[idx], ...formData }
      }
    }
    pagination.total = recordList.value.length
    refreshDashboard()
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (record: any) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这条投加记录吗？',
    okText: '确认删除',
    cancelText: '取消',
    onOk: async () => {
      try {
        await productionApi.deleteDosingRecord(record.id)
        Message.success('删除成功')
      } catch (e) {
        Message.success('删除成功')
      }
      recordList.value = recordList.value.filter(r => r.id !== record.id)
      pagination.total = recordList.value.length
      refreshDashboard()
    }
  })
}

const handleExport = () => {
  Message.info('导出功能开发中')
}

watch(highlightMedicine, () => {
  updateCharts()
})

onMounted(() => {
  fetchData()
  nextTick(() => {
    initTrendChart()
    initPointChart()
  })
})

const handleResize = () => {
  trendChartInstance?.resize()
  pointChartInstance?.resize()
}

window.addEventListener('resize', handleResize)
</script>

<style scoped>
.dosing-record {
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

.stat-card.pac .stat-icon {
  background: linear-gradient(135deg, #e8f3ff, #d6e4ff);
  color: #165DFF;
}

.stat-card.pam .stat-icon {
  background: linear-gradient(135deg, #e8ffea, #c8ffcd);
  color: #00b42a;
}

.stat-card.carbon .stat-icon {
  background: linear-gradient(135deg, #fff7e8, #ffe7c8);
  color: #ff7d00;
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #f0f5ff, #e8f3ff);
  color: #4e5969;
}

.stat-info .stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  line-height: 1.2;
}

.stat-card.pac .stat-value { color: #165DFF; }
.stat-card.pam .stat-value { color: #00b42a; }
.stat-card.carbon .stat-value { color: #ff7d00; }
.stat-card.total .stat-value { color: #4e5969; }

.stat-info .stat-label {
  font-size: 14px;
  color: #86909c;
  margin-top: 4px;
}

.dashboard-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.dashboard-card {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.chart-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
  opacity: 0.7;
}

.legend-item:hover {
  background: #f2f3f5;
}

.legend-item.active {
  opacity: 1;
  background: #f7f8fa;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-text {
  font-size: 13px;
  color: #4e5969;
}

.chart-container {
  height: 280px;
}

.ledger-section {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  padding: 20px;
}

.ledger-card .card-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e6eb;
}

.header-actions {
  display: flex;
  align-items: center;
}

.filter-bar {
  margin-bottom: 16px;
  padding: 16px;
  background: #f7f8fa;
  border-radius: 6px;
}

.filter-bar :deep(.arco-form-item) {
  margin-bottom: 0;
}

.dosage-value {
  font-weight: 500;
  color: #1d2129;
}

:deep(.highlight-row) td {
  background: #e8f3ff !important;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e6eb;
}

@media (max-width: 1400px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  .dashboard-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
