<template>
  <div class="page-container">
    <div class="page-header">
      <h2>节能策略管理</h2>
      <p>节能建议生成 / 节能方案执行 / 节能效果评估</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="节能建议">
        <div class="suggestion-list">
          <div class="suggestion-card" v-for="item in suggestions" :key="item.id">
            <div class="suggestion-header">
              <a-tag :color="item.priority === 'high' ? 'red' : item.priority === 'medium' ? 'orange' : 'blue'">
                {{ item.priority === 'high' ? '高优先级' : item.priority === 'medium' ? '中优先级' : '低优先级' }}
              </a-tag>
              <span class="saving">预计节省: ¥{{ item.expected_saving }}/月</span>
            </div>
            <div class="suggestion-title">{{ item.title }}</div>
            <div class="suggestion-desc">{{ item.description }}</div>
          </div>
        </div>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="方案执行">
        <a-table :columns="planColumns" :data="plans">
          <template #status="{ record }">
            <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
          </template>
          <template #progress="{ record }">
            <a-progress :percent="record.progress" size="small" />
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="效果评估">
        <a-row :gutter="16" style="margin-bottom: 16px;">
          <a-col :span="8">
            <a-statistic title="本月节能量" :value="12580" suffix="kWh" />
          </a-col>
          <a-col :span="8">
            <a-statistic title="节能率" :value="8.5" suffix="%" />
          </a-col>
          <a-col :span="8">
            <a-statistic title="节省成本" :value="8806" prefix="¥" />
          </a-col>
        </a-row>
        <a-card title="节能效果趋势">
          <div ref="effectChartRef" style="height: 350px;"></div>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const effectChartRef = ref<HTMLElement>()

const suggestions = ref([
  { id: 1, priority: 'high', title: '优化曝气量自动控制', description: '根据实时DO值自动调节曝气量', expected_saving: 1500 },
  { id: 2, priority: 'medium', title: '调整泵组运行策略', description: '采用变频调速，优化泵组运行组合', expected_saving: 800 },
  { id: 3, priority: 'low', title: '错峰用电优化', description: '将非紧急操作调整至低谷电价时段', expected_saving: 500 }
])

const planColumns = [
  { title: '方案名称', dataIndex: 'name' },
  { title: '目标节能', dataIndex: 'target' },
  { title: '实际节能', dataIndex: 'actual' },
  { title: '执行进度', slotName: 'progress' },
  { title: '状态', slotName: 'status' }
]

const plans = ref([
  { name: '曝气优化方案', target: '15%', actual: '12%', progress: 80, status: 'executing' },
  { name: '变频调速改造', target: '10%', actual: '10%', progress: 100, status: 'completed' }
])

const getStatusColor = (s: string) => ({ planned: 'blue', executing: 'orange', completed: 'green' }[s] || 'gray')
const getStatusText = (s: string) => ({ planned: '计划中', executing: '执行中', completed: '已完成' }[s] || '未知')

onMounted(() => {
  if (effectChartRef.value) {
    const chart = echarts.init(effectChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['节能量', '节能率'] },
      xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
      yAxis: [{ type: 'value', name: 'kWh' }, { type: 'value', name: '%', max: 15 }],
      series: [
        { name: '节能量', type: 'bar', data: [8000, 9500, 10200, 11000, 11800, 12580] },
        { name: '节能率', type: 'line', yAxisIndex: 1, data: [5.2, 6.1, 6.8, 7.5, 8.0, 8.5] }
      ]
    })
  }
})
</script>

<style scoped>
.suggestion-list { display: flex; flex-direction: column; gap: 16px; }
.suggestion-card { background: #fff; border: 1px solid #e5e6eb; border-radius: 8px; padding: 16px; }
.suggestion-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.suggestion-header .saving { color: #00b42a; font-weight: 500; }
.suggestion-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
.suggestion-desc { color: #86909c; margin-bottom: 12px; }
.suggestion-footer { display: flex; gap: 8px; }
</style>
