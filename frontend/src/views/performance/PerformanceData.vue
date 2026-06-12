<template>
  <div class="page-container">
    <div class="page-header">
      <h2>绩效数据管理</h2>
      <p>自动采集 / 手动补录 / 数据审核</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="自动采集">
        <a-card>
          <template #title>
            <a-space>
              <span>采集任务列表</span>
              <a-button type="primary" @click="showTaskModal = true">
                <template #icon><icon-plus /></template>
                新建采集任务
              </a-button>
            </a-space>
          </template>
          
          <a-table
            :columns="taskColumns"
            :data="collectTasks"
            :pagination="pagination"
            :loading="loading"
          >
            <template #status="{ record }">
              <a-tag :color="getStatusColor(record.status)">{{ record.status }}</a-tag>
            </template>
            <template #frequency="{ record }">
              <a-tag>{{ record.frequency }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="runTask(record)">立即执行</a-button>
                <a-button type="text" size="small" @click="editTask(record)">编辑</a-button>
                <a-popconfirm content="确定要删除该任务吗？" @ok="deleteTask(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="手动补录">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="选择指标">
              <a-select v-model="manualForm.indicator" placeholder="请选择指标" style="width: 200px;">
                <a-option value="COD去除率">COD去除率</a-option>
                <a-option value="氨氮去除率">氨氮去除率</a-option>
                <a-option value="日处理水量">日处理水量</a-option>
                <a-option value="设备运行率">设备运行率</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="数据日期">
              <a-date-picker v-model="manualForm.date" style="width: 200px;" />
            </a-form-item>
            <a-form-item label="数据值">
              <a-input-number v-model="manualForm.value" :precision="2" style="width: 150px;" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="submitManualData">提交</a-button>
            </a-form-item>
          </a-form>
          
          <a-table
            :columns="manualColumns"
            :data="manualData"
            :pagination="manualPagination"
          >
            <template #status="{ record }">
              <a-tag :color="record.status === '已审核' ? 'green' : 'orange'">{{ record.status }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" v-if="record.status === '待审核'" @click="auditData(record, true)">通过</a-button>
                <a-button type="text" size="small" status="danger" v-if="record.status === '待审核'" @click="auditData(record, false)">驳回</a-button>
                <a-popconfirm content="确定要删除该数据吗？" @ok="deleteManualData(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="数据审核">
        <a-row :gutter="16">
          <a-col :span="16">
            <a-card title="待审核数据">
              <a-table
                :columns="auditColumns"
                :data="pendingAuditData"
                :pagination="auditPagination"
              >
                <template #operations="{ record }">
                  <a-space>
                    <a-button type="primary" size="small" @click="auditData(record, true)">通过</a-button>
                    <a-button size="small" @click="auditData(record, false)">驳回</a-button>
                  </a-space>
                </template>
              </a-table>
            </a-card>
          </a-col>
          <a-col :span="8">
            <a-card title="审核统计">
              <div ref="auditChartRef" style="height: 300px;"></div>
            </a-card>
          </a-col>
        </a-row>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 新建采集任务弹窗 -->
    <a-modal
      v-model:visible="showTaskModal"
      title="新建采集任务"
      @ok="saveTask"
      :ok-loading="saveLoading"
    >
      <a-form :model="taskForm" layout="vertical">
        <a-form-item label="任务名称" required>
          <a-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </a-form-item>
        <a-form-item label="采集指标" required>
          <a-select v-model="taskForm.indicator" placeholder="请选择指标">
            <a-option value="COD去除率">COD去除率</a-option>
            <a-option value="氨氮去除率">氨氮去除率</a-option>
            <a-option value="日处理水量">日处理水量</a-option>
            <a-option value="设备运行率">设备运行率</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="采集频率" required>
          <a-select v-model="taskForm.frequency" placeholder="请选择频率">
            <a-option value="每小时">每小时</a-option>
            <a-option value="每天">每天</a-option>
            <a-option value="每周">每周</a-option>
            <a-option value="每月">每月</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="数据源">
          <a-input v-model="taskForm.source" placeholder="请输入数据源" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import * as echarts from 'echarts'

const loading = ref(false)
const saveLoading = ref(false)
const showTaskModal = ref(false)
const editingTask = ref<any>(null)
const auditChartRef = ref<HTMLElement>()
let auditChart: echarts.ECharts

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const manualPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const auditPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const collectTasks = ref([
  { id: 1, name: 'COD去除率采集', indicator: 'COD去除率', frequency: '每天', source: 'SCADA系统', status: '运行中', lastRun: '2026-02-04 08:00:00' },
  { id: 2, name: '氨氮去除率采集', indicator: '氨氮去除率', frequency: '每天', source: 'SCADA系统', status: '运行中', lastRun: '2026-02-04 08:00:00' },
  { id: 3, name: '日处理水量采集', indicator: '日处理水量', frequency: '每天', source: '流量计', status: '运行中', lastRun: '2026-02-04 08:00:00' },
  { id: 4, name: '设备运行率采集', indicator: '设备运行率', frequency: '每小时', source: '设备管理系统', status: '已停止', lastRun: '2026-02-03 23:00:00' }
])

const manualData = ref([
  { id: 1, indicator: 'COD去除率', date: '2026-02-03', value: 88.5, submitter: '张三', submitTime: '2026-02-03 10:30:00', status: '已审核' },
  { id: 2, indicator: '氨氮去除率', date: '2026-02-03', value: 92.3, submitter: '李四', submitTime: '2026-02-03 11:20:00', status: '待审核' },
  { id: 3, indicator: '日处理水量', date: '2026-02-02', value: 12500, submitter: '王五', submitTime: '2026-02-02 15:45:00', status: '已审核' }
])

const pendingAuditData = ref([
  { id: 2, indicator: '氨氮去除率', date: '2026-02-03', value: 92.3, submitter: '李四', submitTime: '2026-02-03 11:20:00' },
  { id: 4, indicator: '设备运行率', date: '2026-02-04', value: 95.8, submitter: '赵六', submitTime: '2026-02-04 09:15:00' }
])

const taskForm = reactive({
  name: '',
  indicator: '',
  frequency: '',
  source: ''
})

const manualForm = reactive({
  indicator: '',
  date: '',
  value: 0
})

const taskColumns = [
  { title: '任务名称', dataIndex: 'name', width: 200 },
  { title: '采集指标', dataIndex: 'indicator', width: 150 },
  { title: '采集频率', slotName: 'frequency', width: 120 },
  { title: '数据源', dataIndex: 'source', width: 150 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '最后执行时间', dataIndex: 'lastRun', width: 180 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const manualColumns = [
  { title: '指标名称', dataIndex: 'indicator', width: 150 },
  { title: '数据日期', dataIndex: 'date', width: 120 },
  { title: '数据值', dataIndex: 'value', width: 120 },
  { title: '提交人', dataIndex: 'submitter', width: 100 },
  { title: '提交时间', dataIndex: 'submitTime', width: 180 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const auditColumns = [
  { title: '指标名称', dataIndex: 'indicator', width: 150 },
  { title: '数据日期', dataIndex: 'date', width: 120 },
  { title: '数据值', dataIndex: 'value', width: 120 },
  { title: '提交人', dataIndex: 'submitter', width: 100 },
  { title: '提交时间', dataIndex: 'submitTime', width: 180 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    '运行中': 'green',
    '已停止': 'red',
    '已暂停': 'orange'
  }
  return colors[status] || 'gray'
}

const runTask = (record: any) => {
  Message.success(`任务"${record.name}"已执行`)
  record.lastRun = new Date().toLocaleString('zh-CN')
}

const editTask = (record: any) => {
  editingTask.value = record
  Object.assign(taskForm, record)
  showTaskModal.value = true
}

const deleteTask = (record: any) => {
  const index = collectTasks.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    collectTasks.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const saveTask = async () => {
  if (!taskForm.name || !taskForm.indicator || !taskForm.frequency) {
    Message.warning('请填写完整信息')
    return
  }
  
  saveLoading.value = true
  setTimeout(() => {
    if (editingTask.value) {
      const index = collectTasks.value.findIndex(item => item.id === editingTask.value.id)
      if (index > -1) {
        Object.assign(collectTasks.value[index], taskForm)
      }
      Message.success('编辑成功')
    } else {
      collectTasks.value.push({
        id: Date.now(),
        ...taskForm,
        status: '运行中',
        lastRun: new Date().toLocaleString('zh-CN')
      })
      Message.success('新增成功')
    }
    saveLoading.value = false
    showTaskModal.value = false
    editingTask.value = null
    Object.assign(taskForm, { name: '', indicator: '', frequency: '', source: '' })
  }, 500)
}

const submitManualData = () => {
  if (!manualForm.indicator || !manualForm.date || !manualForm.value) {
    Message.warning('请填写完整信息')
    return
  }
  
  manualData.value.push({
    id: Date.now(),
    indicator: manualForm.indicator,
    date: typeof manualForm.date === 'string' ? manualForm.date : manualForm.date.format('YYYY-MM-DD'),
    value: manualForm.value,
    submitter: '当前用户',
    submitTime: new Date().toLocaleString('zh-CN'),
    status: '待审核'
  })
  
  pendingAuditData.value.push({
    id: Date.now(),
    indicator: manualForm.indicator,
    date: typeof manualForm.date === 'string' ? manualForm.date : manualForm.date.format('YYYY-MM-DD'),
    value: manualForm.value,
    submitter: '当前用户',
    submitTime: new Date().toLocaleString('zh-CN')
  })
  
  Message.success('提交成功，等待审核')
  Object.assign(manualForm, { indicator: '', date: '', value: 0 })
}

const auditData = (record: any, approved: boolean) => {
  const manualIndex = manualData.value.findIndex(item => item.id === record.id)
  if (manualIndex > -1) {
    manualData.value[manualIndex].status = approved ? '已审核' : '已驳回'
  }
  
  const auditIndex = pendingAuditData.value.findIndex(item => item.id === record.id)
  if (auditIndex > -1) {
    pendingAuditData.value.splice(auditIndex, 1)
  }
  
  Message.success(approved ? '审核通过' : '已驳回')
  initAuditChart()
}

const deleteManualData = (record: any) => {
  const index = manualData.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    manualData.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const initAuditChart = () => {
  if (auditChartRef.value) {
    const total = manualData.value.length
    const approved = manualData.value.filter(item => item.status === '已审核').length
    const pending = manualData.value.filter(item => item.status === '待审核').length
    const rejected = total - approved - pending
    
    auditChart = echarts.init(auditChartRef.value)
    auditChart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        bottom: 0,
        left: 'center'
      },
      series: [
        {
          type: 'pie',
          radius: '60%',
          data: [
            { value: approved, name: '已审核', itemStyle: { color: '#00B42A' } },
            { value: pending, name: '待审核', itemStyle: { color: '#FF7D00' } },
            { value: rejected, name: '已驳回', itemStyle: { color: '#F53F3F' } }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    })
  }
}

onMounted(() => {
  pagination.total = collectTasks.value.length
  manualPagination.total = manualData.value.length
  auditPagination.total = pendingAuditData.value.length
  setTimeout(initAuditChart, 100)
})

onUnmounted(() => {
  auditChart?.dispose()
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
