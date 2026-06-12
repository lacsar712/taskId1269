<template>
  <div class="page-container">
    <div class="page-header">
      <h2>常规报表</h2>
      <p>生产日报 / 月报季报年报 / 环保监管报表</p>
    </div>

    <a-card class="filter-card">
      <a-form :model="filterForm" layout="inline">
        <a-form-item label="报表类型">
          <a-select v-model="filterForm.reportType" placeholder="请选择" style="width: 200px;">
            <a-option value="daily">生产日报</a-option>
            <a-option value="monthly">月报</a-option>
            <a-option value="quarterly">季报</a-option>
            <a-option value="yearly">年报</a-option>
            <a-option value="environmental">环保监管报表</a-option>
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
          <icon-check-circle />
        </div>
        <div class="stat-info">
          <div class="stat-label">已审核</div>
          <div class="stat-value">{{ stats.approved }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #FF7D00, #FFCF8B);">
          <icon-clock-circle />
        </div>
        <div class="stat-info">
          <div class="stat-label">待审核</div>
          <div class="stat-value">{{ stats.pending }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #722ED1, #D3ADF7);">
          <icon-download />
        </div>
        <div class="stat-info">
          <div class="stat-label">本月导出</div>
          <div class="stat-value">{{ stats.exported }}</div>
        </div>
      </div>
    </div>

    <!-- 报表列表 -->
    <a-card>
      <template #title>
        <span>报表列表</span>
      </template>
      <template #extra>
        <a-space>
          <a-button type="primary" @click="createReport">
            <template #icon><icon-plus /></template>
            新建报表
          </a-button>
          <a-button @click="exportReports">
            <template #icon><icon-download /></template>
            批量导出
          </a-button>
        </a-space>
      </template>
      <a-table :columns="columns" :data="reportList" :loading="loading" :pagination="pagination">
        <template #reportType="{ record }">
          <a-tag :color="getTypeColor(record.report_type)">
            {{ getTypeText(record.report_type) }}
          </a-tag>
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
  total: 156,
  approved: 128,
  pending: 18,
  exported: 45
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
  { title: '生成时间', dataIndex: 'create_time', width: 180 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作人', dataIndex: 'operator', width: 120 },
]

const reportList = ref([
  {
    id: 1,
    report_no: 'RPT20250101001',
    report_name: '2025年1月生产月报',
    report_type: 'monthly',
    period: '2025-01',
    create_time: '2025-01-31 18:00:00',
    status: 'approved',
    operator: '张三'
  },
  {
    id: 2,
    report_no: 'RPT20250102001',
    report_name: '2025年1月2日生产日报',
    report_type: 'daily',
    period: '2025-01-02',
    create_time: '2025-01-02 23:00:00',
    status: 'approved',
    operator: '李四'
  },
  {
    id: 3,
    report_no: 'RPT20250103001',
    report_name: '2025年第一季度环保监管报表',
    report_type: 'environmental',
    period: '2025-Q1',
    create_time: '2025-01-03 10:00:00',
    status: 'pending',
    operator: '王五'
  },
  {
    id: 4,
    report_no: 'RPT20250104001',
    report_name: '2024年度生产年报',
    report_type: 'yearly',
    period: '2024',
    create_time: '2025-01-04 14:30:00',
    status: 'approved',
    operator: '赵六'
  },
  {
    id: 5,
    report_no: 'RPT20250105001',
    report_name: '2025年1月5日生产日报',
    report_type: 'daily',
    period: '2025-01-05',
    create_time: '2025-01-05 23:00:00',
    status: 'pending',
    operator: '张三'
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
    environmental: 'red'
  }
  return map[type] || 'gray'
}

const getTypeText = (type: string) => {
  const map: Record<string, string> = {
    daily: '生产日报',
    monthly: '月报',
    quarterly: '季报',
    yearly: '年报',
    environmental: '环保监管'
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
</style>
