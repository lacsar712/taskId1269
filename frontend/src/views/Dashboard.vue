<template>
  <div class="dashboard">
    <!-- 概览卡片 -->
    <div class="dashboard-grid">
      <div class="stat-card">
        <div class="card-header">
          <div class="icon" style="background: linear-gradient(135deg, #165DFF, #14C9C9);">
            <icon-common />
          </div>
          <div class="info">
            <div class="title">今日处理水量</div>
            <div class="value">{{ overview.water_treatment?.today_output?.toLocaleString() }}<span class="unit">m³</span></div>
          </div>
        </div>
        <div class="trend up">
          <icon-arrow-rise /> 较昨日 +2.5%
        </div>
      </div>
      
      <div class="stat-card">
        <div class="card-header">
          <div class="icon" style="background: linear-gradient(135deg, #00B42A, #7BE188);">
            <icon-check-circle />
          </div>
          <div class="info">
            <div class="title">COD去除率</div>
            <div class="value">{{ overview.water_quality?.cod_removal_rate }}<span class="unit">%</span></div>
          </div>
        </div>
        <div class="trend up">
          <icon-arrow-rise /> 达标运行
        </div>
      </div>
      
      <div class="stat-card">
        <div class="card-header">
          <div class="icon" style="background: linear-gradient(135deg, #FF7D00, #FFCF8B);">
            <icon-computer />
          </div>
          <div class="info">
            <div class="title">设备运行率</div>
            <div class="value">{{ overview.equipment?.running_rate }}<span class="unit">%</span></div>
          </div>
        </div>
        <div class="sub-info">
          运行 {{ overview.equipment?.running }} / 总计 {{ overview.equipment?.total }} 台
        </div>
      </div>
      
      <div class="stat-card">
        <div class="card-header">
          <div class="icon" style="background: linear-gradient(135deg, #F53F3F, #FFCFC9);">
            <icon-notification />
          </div>
          <div class="info">
            <div class="title">待处理告警</div>
            <div class="value">{{ overview.alarms?.unhandled }}<span class="unit">条</span></div>
          </div>
        </div>
        <div class="sub-info">
          <a-space>
            <a-tag color="red" size="small">紧急 {{ overview.alarms?.urgent }}</a-tag>
            <a-tag color="orange" size="small">警告 {{ overview.alarms?.warning }}</a-tag>
          </a-space>
        </div>
      </div>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-row">
      <div class="chart-container">
        <div class="chart-title">
          <span>水量趋势</span>
          <a-radio-group v-model="waterTimeRange" type="button" size="small">
            <a-radio value="day">今日</a-radio>
            <a-radio value="week">本周</a-radio>
          </a-radio-group>
        </div>
        <div ref="waterChartRef" style="height: 280px;"></div>
      </div>
      
      <div class="chart-container">
        <div class="chart-title">
          <span>水质指标</span>
          <a-radio-group v-model="qualityTimeRange" type="button" size="small">
            <a-radio value="week">本周</a-radio>
            <a-radio value="month">本月</a-radio>
          </a-radio-group>
        </div>
        <div ref="qualityChartRef" style="height: 280px;"></div>
      </div>
    </div>
    
    <div class="charts-row">
      <div class="chart-container">
        <div class="chart-title">能耗分析</div>
        <div ref="energyChartRef" style="height: 280px;"></div>
      </div>
      
      <div class="chart-container">
        <div class="chart-title">快捷操作</div>
        <div class="quick-actions">
          <div class="quick-action-item" @click="$router.push('/production/monitor')">
            <icon-dashboard class="icon" />
            <span class="label">工艺监控</span>
          </div>
          <div class="quick-action-item" @click="$router.push('/production/alarm')">
            <icon-notification class="icon" />
            <span class="label">告警处理</span>
          </div>
          <div class="quick-action-item" @click="$router.push('/equipment/ledger')">
            <icon-computer class="icon" />
            <span class="label">设备管理</span>
          </div>
          <div class="quick-action-item" @click="$router.push('/laboratory/task')">
            <icon-experiment class="icon" />
            <span class="label">检测任务</span>
          </div>
          <div class="quick-action-item" @click="$router.push('/report/regular')">
            <icon-file class="icon" />
            <span class="label">生产报表</span>
          </div>
          <div class="quick-action-item" @click="$router.push('/energy/realtime')">
            <icon-thunderbolt class="icon" />
            <span class="label">能耗监测</span>
          </div>
          <div class="quick-action-item" @click="$router.push('/safety/inspection')">
            <icon-safe class="icon" />
            <span class="label">安全巡检</span>
          </div>
          <div class="quick-action-item" @click="$router.push('/system/user')">
            <icon-user-group class="icon" />
            <span class="label">用户管理</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { dashboardApi } from '@/api'

const overview = ref<any>({
  water_treatment: {},
  water_quality: {},
  equipment: {},
  alarms: {}
})
const trends = ref<any>({})

const waterTimeRange = ref('day')
const qualityTimeRange = ref('week')

const waterChartRef = ref<HTMLElement>()
const qualityChartRef = ref<HTMLElement>()
const energyChartRef = ref<HTMLElement>()

let waterChart: echarts.ECharts
let qualityChart: echarts.ECharts
let energyChart: echarts.ECharts

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
        data: trends.value.water_volume?.labels || ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
      },
      yAxis: { type: 'value', name: 'm³' },
      series: [
        {
          name: '进水量',
          type: 'line',
          smooth: true,
          data: trends.value.water_volume?.intake || [580, 520, 680, 720, 700, 650],
          itemStyle: { color: '#165DFF' },
          areaStyle: { color: 'rgba(22, 93, 255, 0.1)' }
        },
        {
          name: '出水量',
          type: 'line',
          smooth: true,
          data: trends.value.water_volume?.output || [560, 500, 660, 700, 680, 630],
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
        data: trends.value.water_quality?.labels || ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: [
        { type: 'value', name: 'COD(mg/L)', position: 'left' },
        { type: 'value', name: '氨氮(mg/L)', position: 'right' }
      ],
      series: [
        {
          name: 'COD',
          type: 'bar',
          data: trends.value.water_quality?.cod || [28, 26, 30, 25, 27, 29, 28],
          itemStyle: { color: '#165DFF', borderRadius: [4, 4, 0, 0] }
        },
        {
          name: '氨氮',
          type: 'line',
          yAxisIndex: 1,
          smooth: true,
          data: trends.value.water_quality?.nh3n || [3.5, 3.2, 3.8, 3.1, 3.4, 3.6, 3.5],
          itemStyle: { color: '#00B42A' }
        }
      ]
    })
  }
  
  // 能耗分析图
  if (energyChartRef.value) {
    energyChart = echarts.init(energyChartRef.value)
    energyChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['能耗', '成本'], top: 0 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: trends.value.energy?.labels || ['1月', '2月', '3月', '4月', '5月', '6月']
      },
      yAxis: [
        { type: 'value', name: '能耗(kWh)', position: 'left' },
        { type: 'value', name: '成本(元)', position: 'right' }
      ],
      series: [
        {
          name: '能耗',
          type: 'bar',
          data: trends.value.energy?.consumption || [380000, 350000, 365000, 375000, 390000, 385000],
          itemStyle: { color: '#722ED1', borderRadius: [4, 4, 0, 0] }
        },
        {
          name: '成本',
          type: 'line',
          yAxisIndex: 1,
          smooth: true,
          data: trends.value.energy?.cost || [266000, 245000, 255500, 262500, 273000, 269500],
          itemStyle: { color: '#F77234' }
        }
      ]
    })
  }
}

const fetchData = async () => {
  try {
    const [overviewData, trendsData] = await Promise.all([
      dashboardApi.getOverview(),
      dashboardApi.getTrends()
    ])
    overview.value = overviewData
    trends.value = trendsData
    initCharts()
  } catch (e) {
    // 使用默认数据
    initCharts()
  }
}

const handleResize = () => {
  waterChart?.resize()
  qualityChart?.resize()
  energyChart?.resize()
}

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  waterChart?.dispose()
  qualityChart?.dispose()
  energyChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 4px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

@media (max-width: 1400px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-card .card-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.stat-card .icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}

.stat-card .info {
  flex: 1;
}

.stat-card .title {
  font-size: 14px;
  color: #86909c;
  margin-bottom: 4px;
}

.stat-card .value {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
}

.stat-card .unit {
  font-size: 14px;
  color: #86909c;
  margin-left: 4px;
  font-weight: normal;
}

.stat-card .trend {
  margin-top: 12px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-card .trend.up {
  color: #00b42a;
}

.stat-card .trend.down {
  color: #f53f3f;
}

.stat-card .sub-info {
  margin-top: 12px;
  font-size: 13px;
  color: #86909c;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

@media (max-width: 1200px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}

.chart-container {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.chart-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.quick-action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 12px;
  background: #f7f8fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-action-item:hover {
  background: #e8f3ff;
  transform: translateY(-2px);
}

.quick-action-item .icon {
  font-size: 28px;
  color: #165DFF;
  margin-bottom: 8px;
}

.quick-action-item .label {
  font-size: 13px;
  color: #4e5969;
}
</style>
