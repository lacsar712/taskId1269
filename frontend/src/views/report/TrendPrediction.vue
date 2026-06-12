<template>
  <div class="page-container">
    <div class="page-header">
      <h2>趋势预测</h2>
      <p>水质趋势预测 / 能耗趋势预测 / 设备故障预测</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="水质趋势预测">
        <a-row :gutter="16">
          <a-col :span="16">
            <a-card title="出水水质预测 (未来7天)">
              <div ref="waterQualityChartRef" style="height: 350px;"></div>
            </a-card>
          </a-col>
          <a-col :span="8">
            <a-card title="预警信息">
              <a-list :data="waterAlerts" :bordered="false">
                <template #item="{ item }">
                  <a-list-item>
                    <a-list-item-meta :title="item.title" :description="item.desc">
                      <template #avatar>
                        <a-avatar :style="{ background: item.color }">
                          <icon-exclamation-circle />
                        </a-avatar>
                      </template>
                    </a-list-item-meta>
                  </a-list-item>
                </template>
              </a-list>
            </a-card>
          </a-col>
        </a-row>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="能耗趋势预测">
        <a-card title="能耗预测 (未来30天)">
          <div ref="energyChartRef" style="height: 400px;"></div>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="设备故障预测">
        <a-table :columns="faultColumns" :data="faultPredictions">
          <template #risk="{ record }">
            <a-tag :color="getRiskColor(record.risk_level)">{{ record.risk_level }}</a-tag>
          </template>
          <template #probability="{ record }">
            <a-progress :percent="record.probability" :status="record.probability > 70 ? 'danger' : record.probability > 40 ? 'warning' : 'success'" size="small" />
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const waterQualityChartRef = ref<HTMLElement>()
const energyChartRef = ref<HTMLElement>()

const waterAlerts = ref([
  { title: 'COD可能超标', desc: '预计1月20日COD达32mg/L', color: '#f53f3f' },
  { title: '氨氮上升趋势', desc: '未来3天氨氮呈上升趋势', color: '#ff7d00' },
  { title: 'SS稳定', desc: 'SS指标预计保持稳定', color: '#00b42a' }
])

const faultColumns = [
  { title: '设备名称', dataIndex: 'equipment' },
  { title: '预测故障类型', dataIndex: 'fault_type' },
  { title: '风险等级', slotName: 'risk' },
  { title: '故障概率', slotName: 'probability' },
  { title: '建议措施', dataIndex: 'suggestion' }
]

const faultPredictions = ref([
  { equipment: '曝气风机#1', fault_type: '轴承磨损', risk_level: '高', probability: 75, suggestion: '建议提前更换轴承' },
  { equipment: '提升泵#2', fault_type: '密封老化', risk_level: '中', probability: 45, suggestion: '下次保养时检查密封' },
  { equipment: '刮泥机', fault_type: '链条松动', risk_level: '低', probability: 25, suggestion: '定期检查调整' }
])

const getRiskColor = (level: string) => ({ '高': 'red', '中': 'orange', '低': 'green' }[level] || 'gray')

onMounted(() => {
  if (waterQualityChartRef.value) {
    const chart = echarts.init(waterQualityChartRef.value)
    const dates = ['1/15', '1/16', '1/17', '1/18', '1/19', '1/20', '1/21']
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['COD实际', 'COD预测', '氨氮实际', '氨氮预测'] },
      xAxis: { type: 'category', data: dates },
      yAxis: [{ type: 'value', name: 'COD(mg/L)' }, { type: 'value', name: '氨氮(mg/L)' }],
      series: [
        { name: 'COD实际', type: 'line', data: [28, 27, 29, null, null, null, null] },
        { name: 'COD预测', type: 'line', lineStyle: { type: 'dashed' }, data: [28, 27, 29, 30, 31, 32, 30] },
        { name: '氨氮实际', type: 'line', yAxisIndex: 1, data: [3.5, 3.4, 3.6, null, null, null, null] },
        { name: '氨氮预测', type: 'line', yAxisIndex: 1, lineStyle: { type: 'dashed' }, data: [3.5, 3.4, 3.6, 3.7, 3.8, 3.9, 3.8] }
      ]
    })
  }
  if (energyChartRef.value) {
    const chart = echarts.init(energyChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['实际能耗', '预测能耗', '历史同期'] },
      xAxis: { type: 'category', data: Array.from({ length: 30 }, (_, i) => `${i + 1}日`) },
      yAxis: { type: 'value', name: 'kWh' },
      series: [
        { name: '实际能耗', type: 'line', data: Array.from({ length: 15 }, () => Math.floor(11000 + Math.random() * 2000)) },
        { name: '预测能耗', type: 'line', lineStyle: { type: 'dashed' }, data: Array.from({ length: 30 }, () => Math.floor(11500 + Math.random() * 1500)) },
        { name: '历史同期', type: 'line', lineStyle: { type: 'dotted' }, data: Array.from({ length: 30 }, () => Math.floor(12000 + Math.random() * 1000)) }
      ]
    })
  }
})
</script>
