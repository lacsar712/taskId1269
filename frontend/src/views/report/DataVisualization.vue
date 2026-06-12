<template>
  <div class="page-container">
    <div class="page-header">
      <h2>数据可视化</h2>
      <p>运营驾驶舱 / 趋势图表 / 对比分析</p>
    </div>

    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="运营驾驶舱">
        <!-- 核心指标卡片 -->
        <div class="kpi-grid">
          <div class="kpi-card" v-for="kpi in kpiList" :key="kpi.id">
            <div class="kpi-icon" :style="{ background: kpi.color }">
              <component :is="kpi.icon" />
            </div>
            <div class="kpi-content">
              <div class="kpi-label">{{ kpi.label }}</div>
              <div class="kpi-value">{{ kpi.value }}<span class="kpi-unit">{{ kpi.unit }}</span></div>
              <div class="kpi-trend" :class="kpi.trend > 0 ? 'up' : 'down'">
                <icon-arrow-rise v-if="kpi.trend > 0" />
                <icon-arrow-fall v-else />
                {{ Math.abs(kpi.trend) }}%
              </div>
            </div>
          </div>
        </div>

        <!-- 图表区域 -->
        <div class="charts-grid">
          <a-card>
            <template #title>水量趋势</template>
            <div ref="waterChartRef" style="height: 300px;"></div>
          </a-card>
          <a-card>
            <template #title>水质指标</template>
            <div ref="qualityChartRef" style="height: 300px;"></div>
          </a-card>
          <a-card>
            <template #title>能耗分析</template>
            <div ref="energyChartRef" style="height: 300px;"></div>
          </a-card>
          <a-card>
            <template #title>设备运行状态</template>
            <div ref="equipmentChartRef" style="height: 300px;"></div>
          </a-card>
        </div>
      </a-tab-pane>

      <a-tab-pane key="2" title="趋势图表">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 16px;">
            <a-form-item label="指标类型">
              <a-select v-model="trendForm.indicator" placeholder="请选择" style="width: 200px;">
                <a-option value="water">处理水量</a-option>
                <a-option value="cod">COD</a-option>
                <a-option value="nh3n">氨氮</a-option>
                <a-option value="energy">能耗</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="时间范围">
              <a-range-picker v-model="trendForm.dateRange" style="width: 300px;" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="updateTrendChart">查询</a-button>
            </a-form-item>
          </a-form>
          <div ref="trendChartRef" style="height: 400px;"></div>
        </a-card>
      </a-tab-pane>

      <a-tab-pane key="3" title="对比分析">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 16px;">
            <a-form-item label="对比维度">
              <a-select v-model="compareForm.dimension" placeholder="请选择" style="width: 200px;">
                <a-option value="period">时间段对比</a-option>
                <a-option value="process">工艺段对比</a-option>
                <a-option value="equipment">设备对比</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="指标">
              <a-select v-model="compareForm.indicator" placeholder="请选择" style="width: 200px;">
                <a-option value="water">处理水量</a-option>
                <a-option value="cod">COD去除率</a-option>
                <a-option value="energy">能耗</a-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="updateCompareChart">查询</a-button>
            </a-form-item>
          </a-form>
          <div ref="compareChartRef" style="height: 400px;"></div>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const kpiList = ref([
  {
    id: 1,
    label: '今日处理水量',
    value: '15600',
    unit: 'm³',
    trend: 2.5,
    color: 'linear-gradient(135deg, #165DFF, #14C9C9)',
    icon: 'icon-common'
  },
  {
    id: 2,
    label: 'COD去除率',
    value: '94.5',
    unit: '%',
    trend: 1.2,
    color: 'linear-gradient(135deg, #00B42A, #7BE188)',
    icon: 'icon-check-circle'
  },
  {
    id: 3,
    label: '日均能耗',
    value: '12500',
    unit: 'kWh',
    trend: -3.2,
    color: 'linear-gradient(135deg, #FF7D00, #FFCF8B)',
    icon: 'icon-thunderbolt'
  },
  {
    id: 4,
    label: '设备运行率',
    value: '96.8',
    unit: '%',
    trend: 0.5,
    color: 'linear-gradient(135deg, #722ED1, #D3ADF7)',
    icon: 'icon-computer'
  }
])

const trendForm = reactive({
  indicator: 'water',
  dateRange: []
})

const compareForm = reactive({
  dimension: 'period',
  indicator: 'water'
})

const waterChartRef = ref<HTMLElement>()
const qualityChartRef = ref<HTMLElement>()
const energyChartRef = ref<HTMLElement>()
const equipmentChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const compareChartRef = ref<HTMLElement>()

let waterChart: echarts.ECharts
let qualityChart: echarts.ECharts
let energyChart: echarts.ECharts
let equipmentChart: echarts.ECharts
let trendChart: echarts.ECharts
let compareChart: echarts.ECharts

const initCharts = () => {
  // 水量趋势图
  if (waterChartRef.value) {
    waterChart = echarts.init(waterChartRef.value)
    waterChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['进水量', '出水量'], top: 0 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
      },
      yAxis: { type: 'value', name: 'm³' },
      series: [
        {
          name: '进水量',
          type: 'line',
          smooth: true,
          data: [580, 520, 680, 720, 700, 650],
          itemStyle: { color: '#165DFF' },
          areaStyle: { color: 'rgba(22, 93, 255, 0.1)' }
        },
        {
          name: '出水量',
          type: 'line',
          smooth: true,
          data: [560, 500, 660, 700, 680, 630],
          itemStyle: { color: '#14C9C9' },
          areaStyle: { color: 'rgba(20, 201, 201, 0.1)' }
        }
      ]
    })
  }

  // 水质指标图
  if (qualityChartRef.value) {
    qualityChart = echarts.init(qualityChartRef.value)
    qualityChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['COD', '氨氮'], top: 0 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: [
        { type: 'value', name: 'COD(mg/L)', position: 'left' },
        { type: 'value', name: '氨氮(mg/L)', position: 'right' }
      ],
      series: [
        {
          name: 'COD',
          type: 'bar',
          data: [28, 26, 30, 25, 27, 29, 28],
          itemStyle: { color: '#165DFF', borderRadius: [4, 4, 0, 0] }
        },
        {
          name: '氨氮',
          type: 'line',
          yAxisIndex: 1,
          smooth: true,
          data: [3.5, 3.2, 3.8, 3.1, 3.4, 3.6, 3.5],
          itemStyle: { color: '#00B42A' }
        }
      ]
    })
  }

  // 能耗分析图
  if (energyChartRef.value) {
    energyChart = echarts.init(energyChartRef.value)
    energyChart.setOption({
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

  // 设备运行状态图
  if (equipmentChartRef.value) {
    equipmentChart = echarts.init(equipmentChartRef.value)
    equipmentChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['格栅机', '提升泵', '曝气机', '搅拌器', '加药泵', '污泥泵']
      },
      yAxis: { type: 'value', name: '运行率(%)' },
      series: [
        {
          type: 'bar',
          data: [98, 96, 95, 97, 99, 94],
          itemStyle: { color: '#00B42A', borderRadius: [4, 4, 0, 0] }
        }
      ]
    })
  }

  // 趋势图表
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    updateTrendChart()
  }

  // 对比分析图
  if (compareChartRef.value) {
    compareChart = echarts.init(compareChartRef.value)
    updateCompareChart()
  }
}

const updateTrendChart = () => {
  if (trendChart && trendChartRef.value) {
    const data = {
      water: {
        labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
        values: [450000, 465000, 480000, 475000, 490000, 485000]
      },
      cod: {
        labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
        values: [28, 26, 30, 25, 27, 29]
      },
      nh3n: {
        labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
        values: [3.5, 3.2, 3.8, 3.1, 3.4, 3.6]
      },
      energy: {
        labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
        values: [380000, 350000, 365000, 375000, 390000, 385000]
      }
    }
    const selected = data[trendForm.indicator as keyof typeof data] || data.water
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: selected.labels
      },
      yAxis: { type: 'value' },
      series: [
        {
          type: 'line',
          smooth: true,
          data: selected.values,
          itemStyle: { color: '#165DFF' },
          areaStyle: { color: 'rgba(22, 93, 255, 0.1)' }
        }
      ]
    })
  }
}

const updateCompareChart = () => {
  if (compareChart && compareChartRef.value) {
    const data = {
      period: {
        labels: ['1月', '2月', '3月'],
        series: [
          { name: '本期', data: [15600, 15800, 16200] },
          { name: '上期', data: [15200, 15400, 15800] }
        ]
      },
      process: {
        labels: ['预处理', '生化处理', '深度处理', '污泥处理'],
        series: [
          { name: '处理水量', data: [15600, 15600, 15600, 3200] }
        ]
      },
      equipment: {
        labels: ['设备A', '设备B', '设备C', '设备D'],
        series: [
          { name: '能耗', data: [3500, 4200, 3800, 1000] }
        ]
      }
    }
    const selected = data[compareForm.dimension as keyof typeof data] || data.period
    compareChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: selected.series.map(s => s.name), top: 0 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: selected.labels
      },
      yAxis: { type: 'value' },
      series: selected.series.map((s, idx) => ({
        name: s.name,
        type: 'bar',
        data: s.data,
        itemStyle: { color: ['#165DFF', '#00B42A', '#FF7D00', '#722ED1'][idx], borderRadius: [4, 4, 0, 0] }
      }))
    })
  }
}

const handleResize = () => {
  waterChart?.resize()
  qualityChart?.resize()
  energyChart?.resize()
  equipmentChart?.resize()
  trendChart?.resize()
  compareChart?.resize()
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  waterChart?.dispose()
  qualityChart?.dispose()
  energyChart?.dispose()
  equipmentChart?.dispose()
  trendChart?.dispose()
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

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

@media (max-width: 1400px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}

.kpi-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.kpi-content {
  flex: 1;
}

.kpi-label {
  font-size: 14px;
  color: #86909c;
  margin-bottom: 4px;
}

.kpi-value {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 4px;
}

.kpi-unit {
  font-size: 14px;
  color: #86909c;
  margin-left: 4px;
  font-weight: normal;
}

.kpi-trend {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.kpi-trend.up {
  color: #00b42a;
}

.kpi-trend.down {
  color: #f53f3f;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
