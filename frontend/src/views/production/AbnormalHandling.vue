<template>
  <div class="page-container">
    <div class="page-header">
      <h2>异常处理</h2>
      <p>异常告警列表 / 异常处理工单 / 异常溯源分析</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="待处理异常">
        <a-table :columns="columns" :data="pendingAlarms" :loading="loading">
          <template #alarm_level="{ record }">
            <a-tag :color="getLevelColor(record.alarm_level)">{{ getLevelText(record.alarm_level) }}</a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="primary" size="small" @click="handleProcess(record)">处理</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="处理工单">
        <a-table :columns="workOrderColumns" :data="workOrders">
          <template #status="{ record }">
            <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="异常溯源">
        <a-card title="异常关联分析">
          <div ref="traceChartRef" style="height: 400px;"></div>
        </a-card>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 处理弹窗 -->
    <a-modal v-model:visible="showProcessModal" title="异常处理" @ok="submitProcess" :ok-loading="submitLoading">
      <a-descriptions :column="1" size="small" style="margin-bottom: 16px;">
        <a-descriptions-item label="告警编号">{{ currentAlarm?.alarm_no }}</a-descriptions-item>
        <a-descriptions-item label="告警类型">{{ currentAlarm?.alarm_type }}</a-descriptions-item>
        <a-descriptions-item label="告警内容">{{ currentAlarm?.title }}</a-descriptions-item>
      </a-descriptions>
      <a-form :model="processForm" layout="vertical">
        <a-form-item label="处理结果" required>
          <a-textarea v-model="processForm.handle_result" placeholder="请输入处理结果" :auto-size="{ minRows: 4 }" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import * as echarts from 'echarts'
import { productionApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const showProcessModal = ref(false)
const currentAlarm = ref<any>(null)
const traceChartRef = ref<HTMLElement>()
let traceChart: echarts.ECharts

const pendingAlarms = ref<any[]>([])
const workOrders = ref<any[]>([])

const processForm = reactive({
  handle_result: ''
})

const columns = [
  { title: '告警编号', dataIndex: 'alarm_no', width: 150 },
  { title: '告警类型', dataIndex: 'alarm_type', width: 120 },
  { title: '级别', slotName: 'alarm_level', width: 80 },
  { title: '告警内容', dataIndex: 'title', ellipsis: true },
  { title: '告警时间', dataIndex: 'alarm_time', width: 180 },
  { title: '操作', slotName: 'operations', width: 140 }
]

const workOrderColumns = [
  { title: '工单编号', dataIndex: 'order_no' },
  { title: '关联告警', dataIndex: 'alarm_no' },
  { title: '处理人', dataIndex: 'handler' },
  { title: '处理时间', dataIndex: 'handle_time' },
  { title: '处理结果', dataIndex: 'result', ellipsis: true },
  { title: '状态', slotName: 'status' }
]

const getLevelColor = (level: string) => {
  const map: Record<string, string> = { normal: 'blue', warning: 'orange', urgent: 'red' }
  return map[level] || 'gray'
}

const getLevelText = (level: string) => {
  const map: Record<string, string> = { normal: '一般', warning: '警告', urgent: '紧急' }
  return map[level] || '未知'
}

const getStatusColor = (status: string) => {
  const map: Record<string, string> = { pending: 'blue', processing: 'orange', completed: 'green' }
  return map[status] || 'gray'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = { pending: '待处理', processing: '处理中', completed: '已完成' }
  return map[status] || '未知'
}

const fetchData = async () => {
  loading.value = true
  try {
    const res: any = await productionApi.getAlarms({ status: 'pending' })
    pendingAlarms.value = res.items || []
  } catch (e) {
    pendingAlarms.value = [
      { alarm_no: 'ALM20240115001', alarm_type: '水质超标', alarm_level: 'urgent', title: '出水COD超标，当前值35mg/L，标准值30mg/L', alarm_time: '2024-01-15 10:30' },
      { alarm_no: 'ALM20240115002', alarm_type: '工艺参数异常', alarm_level: 'warning', title: '生化池DO偏低，当前值1.2mg/L', alarm_time: '2024-01-15 11:15' },
      { alarm_no: 'ALM20240115003', alarm_type: '工况异常', alarm_level: 'normal', title: '进水流量波动较大', alarm_time: '2024-01-15 12:00' }
    ]
  } finally {
    loading.value = false
  }
  
  workOrders.value = [
    { order_no: 'WO20240115001', alarm_no: 'ALM20240114001', handler: '张三', handle_time: '2024-01-14 15:30', result: '增加曝气量，恢复正常', status: 'completed' },
    { order_no: 'WO20240115002', alarm_no: 'ALM20240114002', handler: '李四', handle_time: '2024-01-14 16:45', result: '调整回流比', status: 'completed' }
  ]
}

const handleProcess = (record: any) => {
  currentAlarm.value = record
  processForm.handle_result = ''
  showProcessModal.value = true
}

const submitProcess = async () => {
  if (!processForm.handle_result) {
    Message.warning('请输入处理结果')
    return
  }
  submitLoading.value = true
  try {
    await productionApi.handleAlarm(currentAlarm.value.id, processForm)
    Message.success('处理成功')
    showProcessModal.value = false
    fetchData()
  } catch (e) {
    Message.error('处理失败')
  } finally {
    submitLoading.value = false
  }
}

const initTraceChart = () => {
  if (!traceChartRef.value) return
  traceChart = echarts.init(traceChartRef.value)
  traceChart.setOption({
    tooltip: {},
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      label: { show: true, position: 'right' },
      force: { repulsion: 100 },
      data: [
        { name: 'COD超标', symbolSize: 50, category: 0 },
        { name: '曝气不足', symbolSize: 40, category: 1 },
        { name: '进水浓度高', symbolSize: 40, category: 1 },
        { name: '污泥活性低', symbolSize: 35, category: 1 },
        { name: '风机故障', symbolSize: 30, category: 2 },
        { name: '进水异常', symbolSize: 30, category: 2 }
      ],
      links: [
        { source: 'COD超标', target: '曝气不足' },
        { source: 'COD超标', target: '进水浓度高' },
        { source: 'COD超标', target: '污泥活性低' },
        { source: '曝气不足', target: '风机故障' },
        { source: '进水浓度高', target: '进水异常' }
      ],
      categories: [
        { name: '异常结果' },
        { name: '直接原因' },
        { name: '根本原因' }
      ]
    }],
    color: ['#f53f3f', '#ff7d00', '#165DFF']
  })
}

onMounted(() => {
  fetchData()
  setTimeout(initTraceChart, 100)
})

onUnmounted(() => {
  traceChart?.dispose()
})
</script>

<style scoped>
.table-operations {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}
</style>
