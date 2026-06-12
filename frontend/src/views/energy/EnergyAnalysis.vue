<template>
  <div class="page-container">
    <div class="page-header">
      <h2>能耗多维度分析</h2>
      <p>工艺段能耗分析 / 设备能耗分析 / 时段能耗分析</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="工艺段分析">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-card title="工艺段能耗占比">
              <div ref="sectionPieRef" style="height: 350px;"></div>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card title="工艺段能耗对比">
              <div ref="sectionBarRef" style="height: 350px;"></div>
            </a-card>
          </a-col>
        </a-row>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="设备分析">
        <a-table :columns="equipmentColumns" :data="equipmentData">
          <template #efficiency="{ record }">
            <a-progress :percent="record.efficiency" size="small" />
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="时段分析">
        <a-card title="24小时能耗分布">
          <div ref="hourlyChartRef" style="height: 400px;"></div>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const sectionPieRef = ref<HTMLElement>()
const sectionBarRef = ref<HTMLElement>()
const hourlyChartRef = ref<HTMLElement>()

const equipmentColumns = [
  { title: '设备名称', dataIndex: 'name' },
  { title: '能耗(kWh)', dataIndex: 'consumption' },
  { title: '运行时间(h)', dataIndex: 'running_hours' },
  { title: '单位能耗', dataIndex: 'unit_consumption' },
  { title: '效率', slotName: 'efficiency' }
]

const equipmentData = ref([
  { name: '曝气风机#1', consumption: 3500, running_hours: 720, unit_consumption: '4.86 kWh/h', efficiency: 85 },
  { name: '曝气风机#2', consumption: 3200, running_hours: 680, unit_consumption: '4.71 kWh/h', efficiency: 82 },
  { name: '提升泵#1', consumption: 1200, running_hours: 700, unit_consumption: '1.71 kWh/h', efficiency: 78 },
  { name: '提升泵#2', consumption: 1100, running_hours: 650, unit_consumption: '1.69 kWh/h', efficiency: 75 }
])

onMounted(() => {
  if (sectionPieRef.value) {
    const chart = echarts.init(sectionPieRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        data: [
          { value: 45, name: '生化处理' },
          { value: 20, name: '预处理' },
          { value: 15, name: '深度处理' },
          { value: 12, name: '污泥处理' },
          { value: 8, name: '辅助系统' }
        ]
      }]
    })
  }
  if (sectionBarRef.value) {
    const chart = echarts.init(sectionBarRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['预处理', '生化处理', '深度处理', '污泥处理', '辅助系统'] },
      yAxis: { type: 'value', name: 'kWh' },
      series: [{ type: 'bar', data: [2500, 8500, 3200, 1800, 1500], itemStyle: { color: '#165DFF' } }]
    })
  }
  if (hourlyChartRef.value) {
    const chart = echarts.init(hourlyChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: Array.from({ length: 24 }, (_, i) => `${i}:00`) },
      yAxis: { type: 'value', name: 'kWh' },
      series: [{ type: 'line', smooth: true, areaStyle: {}, data: [450, 420, 400, 380, 390, 420, 550, 680, 720, 700, 680, 650, 620, 640, 660, 700, 750, 720, 680, 620, 580, 520, 480, 460] }]
    })
  }
})
</script>
