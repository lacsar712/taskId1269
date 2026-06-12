<template>
  <div class="page-container">
    <div class="page-header">
      <h2>绩效统计分析</h2>
      <p>个人统计 / 班组统计 / 趋势分析</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="个人统计">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="选择人员">
              <a-select v-model="selectedUser" placeholder="请选择人员" style="width: 200px;">
                <a-option value="张三">张三</a-option>
                <a-option value="李四">李四</a-option>
                <a-option value="王五">王五</a-option>
                <a-option value="赵六">赵六</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="时间范围">
              <a-range-picker v-model="dateRange" style="width: 300px;" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="loadUserData">查询</a-button>
            </a-form-item>
          </a-form>
          
          <a-row :gutter="16" style="margin-bottom: 20px;">
            <a-col :span="6">
              <a-statistic title="综合得分" :value="userStats.totalScore" :precision="2">
                <template #prefix><icon-trophy /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="排名" :value="userStats.rank" suffix="/ 50">
                <template #prefix><icon-fire /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="完成指标数" :value="userStats.completedIndicators" suffix="/ 7">
                <template #prefix><icon-check-circle /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="达标率" :value="userStats.passRate" suffix="%">
                <template #prefix><icon-star /></template>
              </a-statistic>
            </a-col>
          </a-row>
          
          <a-row :gutter="16">
            <a-col :span="16">
              <a-card title="指标得分明细">
                <div ref="userScoreChartRef" style="height: 350px;"></div>
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card title="指标完成情况">
                <div ref="userCompletionChartRef" style="height: 350px;"></div>
              </a-card>
            </a-col>
          </a-row>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="班组统计">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="选择班组">
              <a-select v-model="selectedTeam" placeholder="请选择班组" style="width: 200px;">
                <a-option value="运行一班">运行一班</a-option>
                <a-option value="运行二班">运行二班</a-option>
                <a-option value="运行三班">运行三班</a-option>
                <a-option value="维修班">维修班</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="统计月份">
              <a-month-picker v-model="teamMonth" style="width: 200px;" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="loadTeamData">查询</a-button>
            </a-form-item>
          </a-form>
          
          <a-row :gutter="16" style="margin-bottom: 20px;">
            <a-col :span="6">
              <a-statistic title="班组平均分" :value="teamStats.avgScore" :precision="2">
                <template #prefix><icon-trophy /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="班组排名" :value="teamStats.rank" suffix="/ 4">
                <template #prefix><icon-fire /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="成员人数" :value="teamStats.memberCount">
                <template #prefix><icon-user-group /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="优秀成员" :value="teamStats.excellentCount">
                <template #prefix><icon-star /></template>
              </a-statistic>
            </a-col>
          </a-row>
          
          <a-row :gutter="16">
            <a-col :span="12">
              <a-card title="班组指标对比">
                <div ref="teamComparisonChartRef" style="height: 350px;"></div>
              </a-card>
            </a-col>
            <a-col :span="12">
              <a-card title="成员得分排名">
                <a-table
                  :columns="memberColumns"
                  :data="teamMembers"
                  :pagination="false"
                  size="small"
                >
                  <template #rank="{ record, rowIndex }">
                    <a-tag :color="getRankColor(rowIndex + 1)">{{ rowIndex + 1 }}</a-tag>
                  </template>
                </a-table>
              </a-card>
            </a-col>
          </a-row>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="趋势分析">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="分析指标">
              <a-select v-model="trendIndicator" placeholder="请选择指标" style="width: 200px;">
                <a-option value="综合得分">综合得分</a-option>
                <a-option value="COD去除率">COD去除率</a-option>
                <a-option value="氨氮去除率">氨氮去除率</a-option>
                <a-option value="设备运行率">设备运行率</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="时间范围">
              <a-select v-model="trendRange" placeholder="请选择范围" style="width: 150px;">
                <a-option value="week">近一周</a-option>
                <a-option value="month">近一月</a-option>
                <a-option value="quarter">近一季度</a-option>
                <a-option value="year">近一年</a-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="loadTrendData">查询</a-button>
            </a-form-item>
          </a-form>
          
          <a-row :gutter="16">
            <a-col :span="24">
              <a-card title="趋势分析图">
                <div ref="trendChartRef" style="height: 400px;"></div>
              </a-card>
            </a-col>
          </a-row>
          
          <a-row :gutter="16" style="margin-top: 16px;">
            <a-col :span="8">
              <a-card title="平均值">
                <a-statistic :value="trendStats.avg" :precision="2" />
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card title="最高值">
                <a-statistic :value="trendStats.max" :precision="2" />
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card title="最低值">
                <a-statistic :value="trendStats.min" :precision="2" />
              </a-card>
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

const selectedUser = ref('张三')
const selectedTeam = ref('运行一班')
const teamMonth = ref('')
const dateRange = ref([])
const trendIndicator = ref('综合得分')
const trendRange = ref('month')

const userScoreChartRef = ref<HTMLElement>()
const userCompletionChartRef = ref<HTMLElement>()
const teamComparisonChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

let userScoreChart: echarts.ECharts
let userCompletionChart: echarts.ECharts
let teamComparisonChart: echarts.ECharts
let trendChart: echarts.ECharts

const userStats = reactive({
  totalScore: 85.6,
  rank: 12,
  completedIndicators: 6,
  passRate: 85.7
})

const teamStats = reactive({
  avgScore: 82.3,
  rank: 2,
  memberCount: 12,
  excellentCount: 3
})

const trendStats = reactive({
  avg: 83.5,
  max: 92.3,
  min: 75.8
})

const teamMembers = ref([
  { name: '张三', score: 88.5, indicators: 7 },
  { name: '李四', score: 85.2, indicators: 6 },
  { name: '王五', score: 82.8, indicators: 6 },
  { name: '赵六', score: 80.1, indicators: 5 },
  { name: '孙七', score: 78.5, indicators: 5 }
])

const memberColumns = [
  { title: '排名', slotName: 'rank', width: 80 },
  { title: '姓名', dataIndex: 'name', width: 120 },
  { title: '得分', dataIndex: 'score', width: 100 },
  { title: '完成指标', dataIndex: 'indicators', width: 100 }
]

const getRankColor = (rank: number) => {
  if (rank === 1) return 'red'
  if (rank === 2) return 'orange'
  if (rank === 3) return 'blue'
  return 'gray'
}

const loadUserData = () => {
  initUserCharts()
}

const loadTeamData = () => {
  initTeamChart()
}

const loadTrendData = () => {
  initTrendChart()
}

const initUserCharts = () => {
  if (userScoreChartRef.value) {
    userScoreChart = echarts.init(userScoreChartRef.value)
    userScoreChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['得分', '满分'], top: 0 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['COD去除率', '氨氮去除率', '日处理水量', '设备运行率', '安全事故数', '吨水电耗', '吨水药耗']
      },
      yAxis: { type: 'value', name: '得分', max: 100 },
      series: [
        {
          name: '得分',
          type: 'bar',
          data: [90, 88, 85, 82, 95, 80, 75],
          itemStyle: { color: '#165DFF', borderRadius: [4, 4, 0, 0] }
        },
        {
          name: '满分',
          type: 'line',
          data: [100, 100, 100, 100, 100, 100, 100],
          itemStyle: { color: '#86909c' },
          lineStyle: { type: 'dashed' }
        }
      ]
    })
  }
  
  if (userCompletionChartRef.value) {
    userCompletionChart = echarts.init(userCompletionChartRef.value)
    userCompletionChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0, left: 'center' },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}\n{c}'
          },
          data: [
            { value: 6, name: '已完成', itemStyle: { color: '#00B42A' } },
            { value: 1, name: '未完成', itemStyle: { color: '#F53F3F' } }
          ]
        }
      ]
    })
  }
}

const initTeamChart = () => {
  if (teamComparisonChartRef.value) {
    teamComparisonChart = echarts.init(teamComparisonChartRef.value)
    teamComparisonChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['运行一班', '运行二班', '运行三班', '维修班'], top: 0 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['COD去除率', '氨氮去除率', '日处理水量', '设备运行率', '安全事故数']
      },
      yAxis: { type: 'value', name: '得分' },
      series: [
        {
          name: '运行一班',
          type: 'bar',
          data: [88, 85, 82, 80, 95],
          itemStyle: { color: '#165DFF' }
        },
        {
          name: '运行二班',
          type: 'bar',
          data: [85, 83, 80, 78, 90],
          itemStyle: { color: '#00B42A' }
        },
        {
          name: '运行三班',
          type: 'bar',
          data: [82, 80, 78, 75, 88],
          itemStyle: { color: '#FF7D00' }
        },
        {
          name: '维修班',
          type: 'bar',
          data: [75, 72, 70, 85, 92],
          itemStyle: { color: '#722ED1' }
        }
      ]
    })
  }
}

const initTrendChart = () => {
  if (trendChartRef.value) {
    const labels = trendRange.value === 'week' 
      ? ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      : trendRange.value === 'month'
      ? ['第1周', '第2周', '第3周', '第4周']
      : trendRange.value === 'quarter'
      ? ['1月', '2月', '3月']
      : ['Q1', 'Q2', 'Q3', 'Q4']
    
    const data = trendRange.value === 'week'
      ? [82, 84, 83, 85, 86, 84, 85]
      : trendRange.value === 'month'
      ? [80, 82, 84, 85]
      : trendRange.value === 'quarter'
      ? [78, 82, 85]
      : [75, 80, 85, 88]
    
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels
      },
      yAxis: { type: 'value', name: '得分' },
      series: [
        {
          name: trendIndicator.value,
          type: 'line',
          smooth: true,
          data: data,
          itemStyle: { color: '#165DFF' },
          areaStyle: { color: 'rgba(22, 93, 255, 0.1)' },
          markLine: {
            data: [
              { type: 'average', name: '平均值' }
            ]
          }
        }
      ]
    })
  }
}

onMounted(() => {
  setTimeout(() => {
    initUserCharts()
    initTeamChart()
    initTrendChart()
  }, 100)
})

onUnmounted(() => {
  userScoreChart?.dispose()
  userCompletionChart?.dispose()
  teamComparisonChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 8px;
}

.page-header p {
  font-size: 14px;
  color: #86909c;
}
</style>
