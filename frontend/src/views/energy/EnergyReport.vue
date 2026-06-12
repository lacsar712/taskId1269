<template>
  <div class="page-container">
    <div class="page-header">
      <h2>能耗报表</h2>
      <p>日报月报 / 节能效果 / 对标报表</p>
    </div>

    <a-card class="filter-card">
      <a-form :model="filterForm" layout="inline">
        <a-form-item label="报表类型">
          <a-select v-model="filterForm.reportType" placeholder="请选择" style="width: 200px;">
            <a-option value="daily">日报</a-option>
            <a-option value="monthly">月报</a-option>
            <a-option value="quarterly">季报</a-option>
            <a-option value="yearly">年报</a-option>
            <a-option value="saving">节能效果报表</a-option>
            <a-option value="benchmark">对标报表</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="日期范围">
          <a-range-picker v-model="filterForm.dateRange" style="width: 300px;" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="fetchReports">
            <template #icon><icon-search /></template>
            查询
          </a-button>
          <a-button @click="resetFilter" style="margin-left: 8px;">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #165DFF, #14C9C9);">
          <icon-file />
        </div>
        <div class="stat-info">
          <div class="stat-label">报表总数</div>
          <div class="stat-value">{{ stats.total }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #00B42A, #7BE188);">
          <icon-thunderbolt />
        </div>
        <div class="stat-info">
          <div class="stat-label">累计能耗</div>
          <div class="stat-value">{{ stats.totalEnergy }}<span class="stat-unit">kWh</span></div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #FF7D00, #FFCF8B);">
          <icon-dollar />
        </div>
        <div class="stat-info">
          <div class="stat-label">累计成本</div>
          <div class="stat-value">{{ stats.totalCost }}<span class="stat-unit">元</span></div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #722ED1, #D3ADF7);">
          <icon-check-circle />
        </div>
        <div class="stat-info">
          <div class="stat-label">节能率</div>
          <div class="stat-value">{{ stats.savingRate }}<span class="stat-unit">%</span></div>
        </div>
      </div>
    </div>

    <!-- 报表列表 -->
    <a-card>
      <template #title>
        <span>报表列表</span>
      </template>
      <a-table :columns="columns" :data="reportList" :loading="loading" :pagination="pagination">
        <template #reportType="{ record }">
          <a-tag :color="getTypeColor(record.report_type)">
            {{ getTypeText(record.report_type) }}
          </a-tag>
        </template>
        <template #totalEnergy="{ record }">
          {{ record.total_energy }} kWh
        </template>
        <template #totalCost="{ record }">
          {{ record.total_cost }} 元
        </template>
        <template #savingRate="{ record }">
          <span style="color: #00b42a;">{{ record.saving_rate }}%</span>
        </template>
        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </a-tag>
        </template>
      </a-table>
    </a-card>

    <!-- 报表趋势图 -->
    <a-card style="margin-top: 16px;">
      <template #title>
        <span>报表生成趋势</span>
      </template>
      <div ref="trendChartRef" style="height: 300px;"></div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import * as echarts from 'echarts'

const loading = ref(false)
const filterForm = reactive({
  reportType: '',
  dateRange: []
})

const stats = ref({
  total: 89,
  totalEnergy: 3375000,
  totalCost: 2362500,
  savingRate: 8.5
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const columns = [
  { title: '报表编号', dataIndex: 'report_no', width: 150 },
  { title: '报表名称', dataIndex: 'report_name', ellipsis: true },
  { title: '报表类型', slotName: 'reportType', width: 120 },
  { title: '统计周期', dataIndex: 'period', width: 150 },
  { title: '总能耗', slotName: 'totalEnergy', width: 150 },
  { title: '总成本', slotName: 'totalCost', width: 150 },
  { title: '节能率', slotName: 'savingRate', width: 100 },
  { title: '生成时间', dataIndex: 'create_time', width: 180 },
  { title: '状态', slotName: 'status', width: 100 },
]

const reportList = ref([
  {
    id: 1,
    report_no: 'ENR20250101001',
    report_name: '2025年1月能耗月报',
    report_type: 'monthly',
    period: '2025-01',
    total_energy: 375000,
    total_cost: 262500,
    saving_rate: 8.5,
    create_time: '2025-01-31 18:00:00',
    status: 'approved'
  },
  {
    id: 2,
    report_no: 'ENR20250102001',
    report_name: '2025年1月2日能耗日报',
    report_type: 'daily',
    period: '2025-01-02',
    total_energy: 12500,
    total_cost: 8750,
    saving_rate: 5.2,
    create_time: '2025-01-02 23:00:00',
    status: 'approved'
  },
  {
    id: 3,
    report_no: 'ENR20250103001',
    report_name: '2025年第一季度节能效果报表',
    report_type: 'saving',
    period: '2025-Q1',
    total_energy: 1125000,
    total_cost: 787500,
    saving_rate: 10.5,
    create_time: '2025-01-03 10:00:00',
    status: 'pending'
  },
  {
    id: 4,
    report_no: 'ENR20250104001',
    report_name: '2024年度能耗年报',
    report_type: 'yearly',
    period: '2024',
    total_energy: 4500000,
    total_cost: 3150000,
    saving_rate: 8.2,
    create_time: '2025-01-04 14:30:00',
    status: 'approved'
  },
  {
    id: 5,
    report_no: 'ENR20250105001',
    report_name: '2025年1月对标报表',
    report_type: 'benchmark',
    period: '2025-01',
    total_energy: 375000,
    total_cost: 262500,
    saving_rate: 8.5,
    create_time: '2025-01-05 09:00:00',
    status: 'approved'
  }
])

const trendChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts

const getTypeColor = (type: string) => {
  const map: Record<string, string> = {
    daily: 'blue',
    monthly: 'green',
    quarterly: 'orange',
    yearly: 'purple',
    saving: 'cyan',
    benchmark: 'red'
  }
  return map[type] || 'gray'
}

const getTypeText = (type: string) => {
  const map: Record<string, string> = {
    daily: '日报',
    monthly: '月报',
    quarterly: '季报',
    yearly: '年报',
    saving: '节能效果',
    benchmark: '对标报表'
  }
  return map[type] || type
}

const getStatusColor = (status: string) => {
  const map: Record<string, string> = {
    approved: 'green',
    pending: 'orange',
    rejected: 'red'
  }
  return map[status] || 'gray'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    approved: '已审核',
    pending: '待审核',
    rejected: '已驳回'
  }
  return map[status] || status
}

const initChart = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['日报', '月报', '季报', '年报'], top: 0 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月']
      },
      yAxis: { type: 'value', name: '数量' },
      series: [
        {
          name: '日报',
          type: 'bar',
          data: [28, 30, 31, 30, 31, 30],
          itemStyle: { color: '#165DFF', borderRadius: [4, 4, 0, 0] }
        },
        {
          name: '月报',
          type: 'bar',
          data: [1, 1, 1, 1, 1, 1],
          itemStyle: { color: '#00B42A', borderRadius: [4, 4, 0, 0] }
        },
        {
          name: '季报',
          type: 'bar',
          data: [0, 0, 1, 0, 0, 0],
          itemStyle: { color: '#FF7D00', borderRadius: [4, 4, 0, 0] }
        },
        {
          name: '年报',
          type: 'bar',
          data: [0, 0, 0, 0, 0, 0],
          itemStyle: { color: '#722ED1', borderRadius: [4, 4, 0, 0] }
        }
      ]
    })
  }
}

const fetchReports = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    Message.success('查询成功')
  }, 500)
}

const resetFilter = () => {
  filterForm.reportType = ''
  filterForm.dateRange = []
  fetchReports()
}

const createReport = () => {
  Message.info('打开新建报表对话框')
}

const exportReports = () => {
  Message.success('导出成功')
}

const viewReport = (record: any) => {
  Message.info(`查看报表: ${record.report_name}`)
}

const editReport = (record: any) => {
  Message.info(`编辑报表: ${record.report_name}`)
}

const downloadReport = (record: any) => {
  Message.success(`下载报表: ${record.report_name}`)
}

const handleResize = () => {
  trendChart?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
})
</script>

<style scoped>
.page-container {
  padding: 16px;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
}

.page-header p {
  margin: 0;
  font-size: 14px;
  color: #86909c;
}

.filter-card {
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #86909c;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
}

.stat-unit {
  font-size: 14px;
  color: #86909c;
  margin-left: 4px;
  font-weight: normal;
}
</style>
