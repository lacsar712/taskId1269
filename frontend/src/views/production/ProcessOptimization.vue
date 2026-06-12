<template>
  <div class="page-container">
    <div class="page-header">
      <h2>工艺优化</h2>
      <p>智能调节建议 / 工艺效率分析 / 模拟仿真</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="智能调节建议">
        <div class="suggestion-list">
          <div class="suggestion-card" v-for="item in suggestions" :key="item.id">
            <div class="suggestion-header">
              <div class="priority" :class="item.priority">{{ getPriorityText(item.priority) }}</div>
              <span class="type">{{ item.optimization_type }}</span>
            </div>
            <div class="suggestion-title">{{ item.title }}</div>
            <div class="suggestion-content">
              <div class="current">
                <span class="label">当前状况：</span>
                {{ item.current_situation }}
              </div>
              <div class="suggest">
                <span class="label">优化建议：</span>
                {{ item.suggestion }}
              </div>
              <div class="effect">
                <span class="label">预期效果：</span>
                {{ item.expected_effect }}
              </div>
            </div>
          </div>
        </div>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="工艺效率分析">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-card title="处理效率分析">
              <div ref="efficiencyChartRef" style="height: 300px;"></div>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card title="能耗效率分析">
              <div ref="energyEfficiencyChartRef" style="height: 300px;"></div>
            </a-card>
          </a-col>
        </a-row>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="模拟仿真">
        <a-card title="参数调整模拟">
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="曝气量">
              <a-slider v-model="simParams.aeration" :min="50" :max="100" style="width: 150px;" />
              <span style="margin-left: 8px;">{{ simParams.aeration }}%</span>
            </a-form-item>
            <a-form-item label="回流比">
              <a-slider v-model="simParams.reflux" :min="50" :max="150" style="width: 150px;" />
              <span style="margin-left: 8px;">{{ simParams.reflux }}%</span>
            </a-form-item>
            <a-form-item label="污泥龄">
              <a-slider v-model="simParams.srt" :min="10" :max="30" style="width: 150px;" />
              <span style="margin-left: 8px;">{{ simParams.srt }}天</span>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="runSimulation">运行模拟</a-button>
            </a-form-item>
          </a-form>
          
          <a-row :gutter="16">
            <a-col :span="8">
              <a-statistic title="预测出水COD" :value="simResult.cod" suffix="mg/L">
                <template #prefix><icon-experiment /></template>
              </a-statistic>
            </a-col>
            <a-col :span="8">
              <a-statistic title="预测出水氨氮" :value="simResult.nh3n" suffix="mg/L">
                <template #prefix><icon-experiment /></template>
              </a-statistic>
            </a-col>
            <a-col :span="8">
              <a-statistic title="预测电耗" :value="simResult.power" suffix="kWh/m³">
                <template #prefix><icon-thunderbolt /></template>
              </a-statistic>
            </a-col>
          </a-row>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { productionApi } from '@/api'

const efficiencyChartRef = ref<HTMLElement>()
const energyEfficiencyChartRef = ref<HTMLElement>()
let efficiencyChart: echarts.ECharts
let energyEfficiencyChart: echarts.ECharts

const suggestions = ref([
  {
    id: 1,
    priority: 'high',
    optimization_type: '智能调节',
    title: '优化曝气量自动控制',
    current_situation: '当前曝气量恒定运行，DO波动范围1.8-3.2mg/L',
    suggestion: '建议采用DO反馈控制，根据实时DO值自动调节曝气量',
    expected_effect: '预计可节能15%，DO稳定在2.0-2.5mg/L'
  },
  {
    id: 2,
    priority: 'medium',
    optimization_type: '效率分析',
    title: '调整污泥回流比',
    current_situation: '当前回流比100%，二沉池污泥浓度偏低',
    suggestion: '建议将回流比提高至120%，提高生化池MLSS浓度',
    expected_effect: '预计提高COD去除率3-5%'
  },
  {
    id: 3,
    priority: 'low',
    optimization_type: '模拟仿真',
    title: '优化进水调节池运行',
    current_situation: '进水量波动较大，影响后续处理稳定性',
    suggestion: '利用调节池均化进水，设置水位联动控制',
    expected_effect: '预计稳定进水流量波动在±10%以内'
  }
])

const simParams = reactive({
  aeration: 80,
  reflux: 100,
  srt: 20
})

const simResult = reactive({
  cod: 28,
  nh3n: 3.5,
  power: 0.35
})

const getPriorityText = (priority: string) => {
  const map: Record<string, string> = { high: '高优先级', medium: '中优先级', low: '低优先级' }
  return map[priority] || '未知'
}

const runSimulation = () => {
  // 简单模拟计算
  simResult.cod = Math.max(15, 35 - simParams.aeration * 0.1 - simParams.reflux * 0.05)
  simResult.nh3n = Math.max(1, 5 - simParams.aeration * 0.02 - simParams.srt * 0.05)
  simResult.power = 0.25 + simParams.aeration * 0.002 + simParams.reflux * 0.001
}

const initCharts = () => {
  if (efficiencyChartRef.value) {
    efficiencyChart = echarts.init(efficiencyChartRef.value)
    efficiencyChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['COD去除率', '氨氮去除率', 'SS去除率'] },
      xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
      yAxis: { type: 'value', name: '%', max: 100 },
      series: [
        { name: 'COD去除率', type: 'line', smooth: true, data: [85, 86, 84, 87, 88, 85] },
        { name: '氨氮去除率', type: 'line', smooth: true, data: [90, 91, 89, 92, 91, 90] },
        { name: 'SS去除率', type: 'line', smooth: true, data: [95, 94, 96, 95, 94, 95] }
      ]
    })
  }
  
  if (energyEfficiencyChartRef.value) {
    energyEfficiencyChart = echarts.init(energyEfficiencyChartRef.value)
    energyEfficiencyChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['吨水电耗', '吨水药耗'] },
      xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
      yAxis: [
        { type: 'value', name: 'kWh/m³' },
        { type: 'value', name: 'kg/m³' }
      ],
      series: [
        { name: '吨水电耗', type: 'bar', data: [0.35, 0.33, 0.34, 0.32, 0.33, 0.34] },
        { name: '吨水药耗', type: 'line', yAxisIndex: 1, data: [0.025, 0.023, 0.024, 0.022, 0.024, 0.023] }
      ]
    })
  }
}

onMounted(() => {
  setTimeout(initCharts, 100)
})

onUnmounted(() => {
  efficiencyChart?.dispose()
  energyEfficiencyChart?.dispose()
})
</script>

<style scoped>
.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.suggestion-card {
  background: #fff;
  border: 1px solid #e5e6eb;
  border-radius: 8px;
  padding: 20px;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.priority {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.priority.high {
  background: #ffece8;
  color: #f53f3f;
}

.priority.medium {
  background: #fff7e8;
  color: #ff7d00;
}

.priority.low {
  background: #e8f3ff;
  color: #165DFF;
}

.type {
  font-size: 13px;
  color: #86909c;
}

.suggestion-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 12px;
}

.suggestion-content {
  background: #f7f8fa;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 16px;
}

.suggestion-content > div {
  margin-bottom: 8px;
  line-height: 1.6;
}

.suggestion-content > div:last-child {
  margin-bottom: 0;
}

.suggestion-content .label {
  color: #86909c;
}

.suggestion-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
