<template>
  <div class="page-container">
    <div class="page-header">
      <h2>设备分析</h2>
      <p>运行效率分析 / 维保成本分析</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="运行效率分析">
        <a-row :gutter="16" style="margin-bottom: 16px;">
          <a-col :span="6">
            <a-statistic title="设备综合效率(OEE)" :value="85.6" suffix="%">
              <template #suffix><icon-arrow-rise style="color: #00b42a;" /></template>
            </a-statistic>
          </a-col>
          <a-col :span="6">
            <a-statistic title="时间开动率" :value="92.3" suffix="%" />
          </a-col>
          <a-col :span="6">
            <a-statistic title="性能开动率" :value="95.1" suffix="%" />
          </a-col>
          <a-col :span="6">
            <a-statistic title="合格品率" :value="97.5" suffix="%" />
          </a-col>
        </a-row>
        <a-card title="设备效率对比">
          <div ref="efficiencyChartRef" style="height: 350px;"></div>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="维保成本分析">
        <a-row :gutter="16" style="margin-bottom: 16px;">
          <a-col :span="8">
            <a-statistic title="本月维保成本" :value="35680" prefix="¥" />
          </a-col>
          <a-col :span="8">
            <a-statistic title="备件成本" :value="18500" prefix="¥" />
          </a-col>
          <a-col :span="8">
            <a-statistic title="人工成本" :value="17180" prefix="¥" />
          </a-col>
        </a-row>
        <a-card title="维保成本趋势">
          <div ref="costChartRef" style="height: 350px;"></div>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const efficiencyChartRef = ref<HTMLElement>()
const costChartRef = ref<HTMLElement>()

onMounted(() => {
  if (efficiencyChartRef.value) {
    const chart = echarts.init(efficiencyChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['曝气风机', '提升泵', '回流泵'] },
      xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
      yAxis: { type: 'value', name: '%', max: 100 },
      series: [
        { name: '曝气风机', type: 'line', smooth: true, data: [88, 86, 89, 87, 90, 88] },
        { name: '提升泵', type: 'line', smooth: true, data: [92, 90, 91, 93, 92, 94] },
        { name: '回流泵', type: 'line', smooth: true, data: [85, 83, 86, 84, 87, 85] }
      ]
    })
  }
  if (costChartRef.value) {
    const chart = echarts.init(costChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['备件成本', '人工成本'] },
      xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
      yAxis: { type: 'value', name: '元' },
      series: [
        { name: '备件成本', type: 'bar', stack: 'total', data: [15000, 18000, 12000, 22000, 16000, 18500] },
        { name: '人工成本', type: 'bar', stack: 'total', data: [12000, 14000, 11000, 16000, 13000, 17180] }
      ]
    })
  }
})
</script>
