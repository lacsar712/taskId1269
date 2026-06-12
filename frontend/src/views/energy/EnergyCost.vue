<template>
  <div class="page-container">
    <div class="page-header">
      <h2>能耗成本核算</h2>
      <p>成本统计 / 分摊分析 / 趋势分析</p>
    </div>

    <a-card class="filter-card">
      <a-form :model="filterForm" layout="inline">
        <a-form-item label="统计周期">
          <a-select v-model="filterForm.period" placeholder="请选择" style="width: 200px;">
            <a-option value="day">日</a-option>
            <a-option value="week">周</a-option>
            <a-option value="month">月</a-option>
            <a-option value="year">年</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="时间范围">
          <a-range-picker v-model="filterForm.dateRange" style="width: 300px;" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="fetchCostData">
            <template #icon><icon-search /></template>
            查询
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 成本汇总 -->
    <div class="cost-summary">
      <div class="cost-card">
        <div class="cost-icon" style="background: linear-gradient(135deg, #165DFF, #14C9C9);">
          <icon-dollar />
        </div>
        <div class="cost-info">
          <div class="cost-label">总成本</div>
          <div class="cost-value">{{ costSummary.total }}<span class="cost-unit">元</span></div>
          <div class="cost-trend up">较上期 +5.2%</div>
        </div>
      </div>
      <div class="cost-card">
        <div class="cost-icon" style="background: linear-gradient(135deg, #00B42A, #7BE188);">
          <icon-thunderbolt />
        </div>
        <div class="cost-info">
          <div class="cost-label">总能耗</div>
          <div class="cost-value">{{ costSummary.totalEnergy }}<span class="cost-unit">kWh</span></div>
          <div class="cost-trend up">较上期 +5.2%</div>
        </div>
      </div>
      <div class="cost-card">
        <div class="cost-icon" style="background: linear-gradient(135deg, #FF7D00, #FFCF8B);">
          <icon-calculator />
        </div>
        <div class="cost-info">
          <div class="cost-label">平均单价</div>
          <div class="cost-value">{{ costSummary.avgPrice }}<span class="cost-unit">元/kWh</span></div>
          <div class="cost-trend down">较上期 -0.5%</div>
        </div>
      </div>
      <div class="cost-card">
        <div class="cost-icon" style="background: linear-gradient(135deg, #722ED1, #D3ADF7);">
          <icon-chart />
        </div>
        <div class="cost-info">
          <div class="cost-label">单位水成本</div>
          <div class="cost-value">{{ costSummary.unitWaterCost }}<span class="cost-unit">元/m³</span></div>
          <div class="cost-trend down">较上期 -2.3%</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <a-card>
        <template #title>成本趋势</template>
        <div ref="trendChartRef" style="height: 400px;"></div>
      </a-card>

      <div class="charts-row" style="margin-top: 16px;">
        <a-card>
          <template #title>成本分布</template>
          <div ref="distributionChartRef" style="height: 300px;"></div>
        </a-card>
        <a-card>
          <template #title>单价趋势</template>
          <div ref="priceChartRef" style="height: 300px;"></div>
        </a-card>
      </div>
    </div>

    <!-- 成本分摊分析 -->
    <a-card style="margin-top: 16px;">
      <template #title>
        <span>成本分摊分析</span>
      </template>
      <a-table :columns="allocationColumns" :data="allocationList" :loading="loading">
        <template #cost="{ record }">
          {{ record.cost }} 元
        </template>
        <template #percentage="{ record }">
          {{ record.percentage }}%
        </template>
        <template #unitCost="{ record }">
          {{ record.unit_cost }} 元/kWh
        </template>
      </a-table>
    </a-card>

    <!-- 成本对比 -->
    <a-card style="margin-top: 16px;">
      <template #title>
        <span>成本对比分析</span>
      </template>
      <div ref="compareChartRef" style="height: 400px;"></div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import * as echarts from 'echarts'

const loading = ref(false)

const filterForm = reactive({
  period: 'month',
  dateRange: []
})

const costSummary = reactive({
  total: 262500,
  totalEnergy: 375000,
  avgPrice: 0.7,
  unitWaterCost: 0.56
})

const trendChartRef = ref<HTMLElement>()
const distributionChartRef = ref<HTMLElement>()
const priceChartRef = ref<HTMLElement>()
const compareChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts
let distributionChart: echarts.ECharts
let priceChart: echarts.ECharts
let compareChart: echarts.ECharts

const allocationColumns = [
  { title: '分摊对象', dataIndex: 'object', width: 150 },
  { title: '能耗(kWh)', dataIndex: 'energy', width: 150 },
  { title: '成本(元)', slotName: 'cost', width: 150 },
  { title: '占比', slotName: 'percentage', width: 120 },
  { title: '单位成本', slotName: 'unitCost', width: 150 },
  { title: '说明', dataIndex: 'remark', ellipsis: true }
]

const allocationList = ref([
  {
    id: 1,
    object: '生化处理',
    energy: 131250,
    cost: 91875,
    percentage: '35%',
    unit_cost: 0.7,
    remark: '按实际用电量分摊'
  },
  {
    id: 2,
    object: '深度处理',
    energy: 93750,
    cost: 65625,
    percentage: '25%',
    unit_cost: 0.7,
    remark: '按实际用电量分摊'
  },
  {
    id: 3,
    object: '预处理',
    energy: 75000,
    cost: 52500,
    percentage: '20%',
    unit_cost: 0.7,
    remark: '按实际用电量分摊'
  },
  {
    id: 4,
    object: '污泥处理',
    energy: 56250,
    cost: 39375,
    percentage: '15%',
    unit_cost: 0.7,
    remark: '按实际用电量分摊'
  },
  {
    id: 5,
    object: '其他',
    energy: 18750,
    cost: 13125,
    percentage: '5%',
    unit_cost: 0.7,
    remark: '公共设施等'
  }
])

const initCharts = () => {
  // 成本趋势图
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['成本', '能耗'], top: 0 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月']
      },
      yAxis: [
        { type: 'value', name: '成本(元)', position: 'left' },
        { type: 'value', name: '能耗(kWh)', position: 'right' }
      ],
      series: [
        {
          name: '成本',
          type: 'bar',
          data: [266000, 245000, 255500, 262500, 273000, 269500],
          itemStyle: { color: '#165DFF', borderRadius: [4, 4, 0, 0] }
        },
        {
          name: '能耗',
          type: 'line',
          yAxisIndex: 1,
          smooth: true,
          data: [380000, 350000, 365000, 375000, 390000, 385000],
          itemStyle: { color: '#00B42A' }
        }
      ]
    })
  }

  // 成本分布图
  if (distributionChartRef.value) {
    distributionChart = echarts.init(distributionChartRef.value)
    distributionChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          data: [
            { value: 35, name: '生化处理' },
            { value: 25, name: '深度处理' },
            { value: 20, name: '预处理' },
            { value: 15, name: '污泥处理' },
            { value: 5, name: '其他' }
          ],
          itemStyle: {
            borderRadius: 8
          }
        }
      ]
    })
  }

  // 单价趋势图
  if (priceChartRef.value) {
    priceChart = echarts.init(priceChartRef.value)
    priceChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['1月', '2月', '3月', '4月', '5月', '6月']
      },
      yAxis: { type: 'value', name: '单价(元/kWh)' },
      series: [
        {
          type: 'line',
          smooth: true,
          data: [0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
          itemStyle: { color: '#F77234' },
          areaStyle: { color: 'rgba(247, 114, 52, 0.1)' }
        }
      ]
    })
  }

  // 成本对比图
  if (compareChartRef.value) {
    compareChart = echarts.init(compareChartRef.value)
    compareChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['本期', '上期'], top: 0 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['预处理', '生化处理', '深度处理', '污泥处理']
      },
      yAxis: { type: 'value', name: '成本(元)' },
      series: [
        {
          name: '本期',
          type: 'bar',
          data: [52500, 91875, 65625, 39375],
          itemStyle: { color: '#165DFF', borderRadius: [4, 4, 0, 0] }
        },
        {
          name: '上期',
          type: 'bar',
          data: [50000, 87500, 62500, 37500],
          itemStyle: { color: '#86909c', borderRadius: [4, 4, 0, 0] }
        }
      ]
    })
  }
}

const fetchCostData = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    Message.success('查询成功')
  }, 500)
}

const handleResize = () => {
  trendChart?.resize()
  distributionChart?.resize()
  priceChart?.resize()
  compareChart?.resize()
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  distributionChart?.dispose()
  priceChart?.dispose()
  compareChart?.dispose()
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

.cost-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

@media (max-width: 1400px) {
  .cost-summary {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .cost-summary {
    grid-template-columns: 1fr;
  }
}

.cost-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 16px;
}

.cost-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.cost-info {
  flex: 1;
}

.cost-label {
  font-size: 14px;
  color: #86909c;
  margin-bottom: 4px;
}

.cost-value {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 4px;
}

.cost-unit {
  font-size: 14px;
  color: #86909c;
  margin-left: 4px;
  font-weight: normal;
}

.cost-trend {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.cost-trend.up {
  color: #f53f3f;
}

.cost-trend.down {
  color: #00b42a;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 1200px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
