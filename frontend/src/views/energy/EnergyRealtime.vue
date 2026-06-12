<template>
  <div class="page-container">
    <div class="page-header">
      <h2>能耗实时监测</h2>
      <p>数据采集 / 实时看板 / 异常告警</p>
    </div>

    <!-- 实时指标卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #165DFF, #14C9C9);">
          <icon-thunderbolt />
        </div>
        <div class="stat-info">
          <div class="stat-label">当前总功率</div>
          <div class="stat-value">{{ realtimeStats.totalPower }}<span class="stat-unit">kW</span></div>
          <div class="stat-trend up">
            <icon-arrow-rise /> 较昨日 +2.5%
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #00B42A, #7BE188);">
          <icon-clock-circle />
        </div>
        <div class="stat-info">
          <div class="stat-label">今日累计能耗</div>
          <div class="stat-value">{{ realtimeStats.todayEnergy }}<span class="stat-unit">kWh</span></div>
          <div class="stat-sub">预计今日: {{ realtimeStats.estimatedEnergy }} kWh</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #FF7D00, #FFCF8B);">
          <icon-dollar />
        </div>
        <div class="stat-info">
          <div class="stat-label">今日成本</div>
          <div class="stat-value">{{ realtimeStats.todayCost }}<span class="stat-unit">元</span></div>
          <div class="stat-sub">单价: {{ realtimeStats.unitPrice }} 元/kWh</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #F53F3F, #FFCFC9);">
          <icon-notification />
        </div>
        <div class="stat-info">
          <div class="stat-label">异常告警</div>
          <div class="stat-value">{{ realtimeStats.alarms }}<span class="stat-unit">条</span></div>
          <div class="stat-sub">
            <a-tag color="red" size="small">紧急 {{ realtimeStats.urgent }}</a-tag>
            <a-tag color="orange" size="small">警告 {{ realtimeStats.warning }}</a-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 实时功率曲线 -->
    <a-card style="margin-bottom: 16px;">
      <template #title>
        <span>实时功率曲线</span>
      </template>
      <template #extra>
        <a-space>
          <a-button size="small" @click="refreshData">
            <template #icon><icon-refresh /></template>
            刷新
          </a-button>
          <a-switch v-model="autoRefresh" size="small">
            <template #checked>自动刷新</template>
            <template #unchecked>手动刷新</template>
          </a-switch>
        </a-space>
      </template>
      <div ref="powerChartRef" style="height: 350px;"></div>
    </a-card>

    <!-- 工艺段能耗分布 -->
    <div class="charts-row">
      <a-card>
        <template #title>工艺段能耗分布</template>
        <div ref="processChartRef" style="height: 300px;"></div>
      </a-card>
      <a-card>
        <template #title>设备能耗TOP5</template>
        <div ref="equipmentChartRef" style="height: 300px;"></div>
      </a-card>
    </div>

    <!-- 异常告警列表 -->
    <a-card style="margin-top: 16px;">
      <template #title>
        <span>异常告警</span>
      </template>
      <a-table :columns="alarmColumns" :data="alarmList" :pagination="false" size="small">
        <template #level="{ record }">
          <a-tag :color="record.level === 'urgent' ? 'red' : 'orange'">
            {{ record.level === 'urgent' ? '紧急' : '警告' }}
          </a-tag>
        </template>
        <template #status="{ record }">
          <a-tag :color="record.status === 'handled' ? 'green' : 'gray'">
            {{ record.status === 'handled' ? '已处理' : '待处理' }}
          </a-tag>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import * as echarts from 'echarts'

const autoRefresh = ref(true)
const refreshTimer = ref<any>(null)

const realtimeStats = reactive({
  totalPower: 1250,
  todayEnergy: 12500,
  estimatedEnergy: 15000,
  todayCost: 8750,
  unitPrice: 0.7,
  alarms: 3,
  urgent: 1,
  warning: 2
})

const powerChartRef = ref<HTMLElement>()
const processChartRef = ref<HTMLElement>()
const equipmentChartRef = ref<HTMLElement>()

let powerChart: echarts.ECharts
let processChart: echarts.ECharts
let equipmentChart: echarts.ECharts

const alarmColumns = [
  { title: '告警时间', dataIndex: 'alarm_time', width: 180 },
  { title: '告警级别', slotName: 'level', width: 100 },
  { title: '设备名称', dataIndex: 'equipment_name', width: 150 },
  { title: '告警内容', dataIndex: 'content', ellipsis: true },
  { title: '当前值', dataIndex: 'current_value', width: 120 },
  { title: '阈值', dataIndex: 'threshold', width: 120 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 100, fixed: 'right' }
]

const alarmList = ref([
  {
    id: 1,
    alarm_time: '2025-01-05 14:30:00',
    level: 'urgent',
    equipment_name: '提升泵-001',
    content: '功率异常，超过额定功率20%',
    current_value: '120%',
    threshold: '100%',
    status: 'pending'
  },
  {
    id: 2,
    alarm_time: '2025-01-05 14:25:00',
    level: 'warning',
    equipment_name: '曝气机-002',
    content: '能耗偏高，建议检查',
    current_value: '85 kW',
    threshold: '80 kW',
    status: 'pending'
  },
  {
    id: 3,
    alarm_time: '2025-01-05 14:20:00',
    level: 'warning',
    equipment_name: '搅拌器-003',
    content: '运行时间过长',
    current_value: '720 h',
    threshold: '700 h',
    status: 'handled'
  }
])

const initCharts = () => {
  // 实时功率曲线
  if (powerChartRef.value) {
    powerChart = echarts.init(powerChartRef.value)
    updatePowerChart()
  }

  // 工艺段能耗分布
  if (processChartRef.value) {
    processChart = echarts.init(processChartRef.value)
    processChart.setOption({
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

  // 设备能耗TOP5
  if (equipmentChartRef.value) {
    equipmentChart = echarts.init(equipmentChartRef.value)
    equipmentChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['提升泵-001', '曝气机-002', '搅拌器-003', '加药泵-004', '污泥泵-005']
      },
      yAxis: { type: 'value', name: '功率(kW)' },
      series: [
        {
          type: 'bar',
          data: [180, 150, 120, 100, 80],
          itemStyle: { color: '#165DFF', borderRadius: [4, 4, 0, 0] }
        }
      ]
    })
  }
}

const updatePowerChart = () => {
  if (powerChart && powerChartRef.value) {
    const now = new Date()
    const times: string[] = []
    const powers: number[] = []
    
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000)
      times.push(`${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')}`)
      powers.push(1200 + Math.random() * 100)
    }
    
    powerChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: times,
        boundaryGap: false
      },
      yAxis: { type: 'value', name: '功率(kW)' },
      series: [
        {
          type: 'line',
          smooth: true,
          data: powers,
          itemStyle: { color: '#165DFF' },
          areaStyle: { color: 'rgba(22, 93, 255, 0.1)' },
          markLine: {
            data: [
              { yAxis: 1300, name: '告警阈值', lineStyle: { color: '#F53F3F', type: 'dashed' } }
            ]
          }
        }
      ]
    })
  }
}

const refreshData = () => {
  updatePowerChart()
  Message.success('数据已刷新')
}

const handleAlarm = (record: any) => {
  Message.info(`处理告警: ${record.content}`)
}

const startAutoRefresh = () => {
  if (autoRefresh.value) {
    refreshTimer.value = setInterval(() => {
      updatePowerChart()
    }, 5000)
  } else {
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
      refreshTimer.value = null
    }
  }
}

const handleResize = () => {
  powerChart?.resize()
  processChart?.resize()
  equipmentChart?.resize()
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
  startAutoRefresh()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
  powerChart?.dispose()
  processChart?.dispose()
  equipmentChart?.dispose()
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
  margin-bottom: 4px;
}

.stat-unit {
  font-size: 14px;
  color: #86909c;
  margin-left: 4px;
  font-weight: normal;
}

.stat-trend {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-trend.up {
  color: #00b42a;
}

.stat-trend.down {
  color: #f53f3f;
}

.stat-sub {
  font-size: 13px;
  color: #86909c;
  margin-top: 4px;
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
