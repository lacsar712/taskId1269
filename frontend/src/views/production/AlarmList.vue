<template>
  <div class="page-container">
    <div class="page-header">
      <h2>异常告警列表</h2>
      <p>水质超标(COD/氨氮) / 工艺参数异常(DO/pH/加药量) / 工况异常等报警 / 支持分级展示(一般/紧急)</p>
    </div>
    
    <!-- 告警统计 -->
    <div class="alarm-stats">
      <div class="stat-item urgent">
        <div class="count">{{ alarmStats.urgent }}</div>
        <div class="label">紧急告警</div>
      </div>
      <div class="stat-item warning">
        <div class="count">{{ alarmStats.warning }}</div>
        <div class="label">警告告警</div>
      </div>
      <div class="stat-item normal">
        <div class="count">{{ alarmStats.normal }}</div>
        <div class="label">一般告警</div>
      </div>
      <div class="stat-item pending">
        <div class="count">{{ alarmStats.pending }}</div>
        <div class="label">待处理</div>
      </div>
    </div>
    
    <!-- 筛选条件 -->
    <div class="filter-bar">
      <a-space>
        <a-select v-model="filters.alarm_level" placeholder="告警级别" style="width: 120px;" allow-clear>
          <a-option value="urgent">紧急</a-option>
          <a-option value="warning">警告</a-option>
          <a-option value="normal">一般</a-option>
        </a-select>
        <a-select v-model="filters.alarm_type" placeholder="告警类型" style="width: 160px;" allow-clear>
          <a-option value="water_quality">水质超标</a-option>
          <a-option value="process_param">工艺参数异常</a-option>
          <a-option value="operation">工况异常</a-option>
        </a-select>
        <a-select v-model="filters.status" placeholder="处理状态" style="width: 120px;" allow-clear>
          <a-option value="pending">待处理</a-option>
          <a-option value="processing">处理中</a-option>
          <a-option value="resolved">已处理</a-option>
        </a-select>
        <a-range-picker style="width: 240px;" />
        <a-button type="primary" @click="fetchAlarms">
          <template #icon><icon-search /></template>
          查询
        </a-button>
      </a-space>
    </div>
    
    <!-- 告警列表 -->
    <a-table :columns="columns" :data="alarms" :loading="loading" :pagination="pagination">
      <template #alarm_level="{ record }">
        <a-tag :color="getLevelColor(record.alarm_level)">
          <icon-exclamation-circle v-if="record.alarm_level === 'urgent'" />
          {{ getLevelText(record.alarm_level) }}
        </a-tag>
      </template>
      <template #status="{ record }">
        <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
      </template>
      <template #operations="{ record }">
        <a-space>
          <a-button type="primary" size="small" v-if="record.status === 'pending'" @click="handleAlarm(record)">处理</a-button>
        </a-space>
      </template>
    </a-table>
    
    <!-- 处理弹窗 -->
    <a-modal v-model:visible="showHandleModal" title="处理告警" @ok="submitHandle" :ok-loading="submitLoading">
      <a-descriptions :column="1" size="small" style="margin-bottom: 16px;">
        <a-descriptions-item label="告警编号">{{ currentAlarm?.alarm_no }}</a-descriptions-item>
        <a-descriptions-item label="告警类型">{{ currentAlarm?.alarm_type }}</a-descriptions-item>
        <a-descriptions-item label="告警级别">
          <a-tag :color="getLevelColor(currentAlarm?.alarm_level)">{{ getLevelText(currentAlarm?.alarm_level) }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="告警内容">{{ currentAlarm?.title }}</a-descriptions-item>
        <a-descriptions-item label="当前值">{{ currentAlarm?.current_value }}</a-descriptions-item>
        <a-descriptions-item label="阈值">{{ currentAlarm?.threshold_value }}</a-descriptions-item>
      </a-descriptions>
      <a-form :model="handleForm" layout="vertical">
        <a-form-item label="处理结果" required>
          <a-textarea v-model="handleForm.handle_result" placeholder="请详细描述处理措施和结果" :auto-size="{ minRows: 4 }" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 详情弹窗 -->
    <a-drawer v-model:visible="showDetailDrawer" title="告警详情" :width="500">
      <a-descriptions :column="1" bordered>
        <a-descriptions-item label="告警编号">{{ currentAlarm?.alarm_no }}</a-descriptions-item>
        <a-descriptions-item label="告警类型">{{ currentAlarm?.alarm_type }}</a-descriptions-item>
        <a-descriptions-item label="告警级别">
          <a-tag :color="getLevelColor(currentAlarm?.alarm_level)">{{ getLevelText(currentAlarm?.alarm_level) }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="告警内容">{{ currentAlarm?.title }}</a-descriptions-item>
        <a-descriptions-item label="告警来源">{{ currentAlarm?.source || '-' }}</a-descriptions-item>
        <a-descriptions-item label="当前值">{{ currentAlarm?.current_value || '-' }}</a-descriptions-item>
        <a-descriptions-item label="阈值">{{ currentAlarm?.threshold_value || '-' }}</a-descriptions-item>
        <a-descriptions-item label="告警时间">{{ currentAlarm?.alarm_time }}</a-descriptions-item>
        <a-descriptions-item label="处理状态">
          <a-tag :color="getStatusColor(currentAlarm?.status)">{{ getStatusText(currentAlarm?.status) }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="处理人" v-if="currentAlarm?.handler_name">{{ currentAlarm.handler_name }}</a-descriptions-item>
        <a-descriptions-item label="处理时间" v-if="currentAlarm?.handle_time">{{ currentAlarm.handle_time }}</a-descriptions-item>
        <a-descriptions-item label="处理结果" v-if="currentAlarm?.handle_result">{{ currentAlarm.handle_result }}</a-descriptions-item>
      </a-descriptions>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { productionApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const showHandleModal = ref(false)
const showDetailDrawer = ref(false)
const currentAlarm = ref<any>(null)
const alarms = ref<any[]>([])
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const filters = reactive({
  alarm_level: '',
  alarm_type: '',
  status: ''
})

const handleForm = reactive({
  handle_result: ''
})

const alarmStats = reactive({
  urgent: 2,
  warning: 5,
  normal: 8,
  pending: 3
})

const columns = [
  { title: '告警编号', dataIndex: 'alarm_no', width: 150 },
  { title: '告警类型', dataIndex: 'alarm_type', width: 120 },
  { title: '级别', slotName: 'alarm_level', width: 100 },
  { title: '告警内容', dataIndex: 'title', ellipsis: true },
  { title: '当前值', dataIndex: 'current_value', width: 80 },
  { title: '阈值', dataIndex: 'threshold_value', width: 80 },
  { title: '告警时间', dataIndex: 'alarm_time', width: 160 },
  { title: '状态', slotName: 'status', width: 90 },
  { title: '操作', slotName: 'operations', width: 120 }
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
  const map: Record<string, string> = { pending: 'blue', processing: 'orange', resolved: 'green' }
  return map[status] || 'gray'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = { pending: '待处理', processing: '处理中', resolved: '已处理' }
  return map[status] || '未知'
}

const fetchAlarms = async () => {
  loading.value = true
  try {
    const res: any = await productionApi.getAlarms({
      page: pagination.current,
      page_size: pagination.pageSize,
      alarm_level: filters.alarm_level || undefined,
      status: filters.status || undefined
    })
    alarms.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    alarms.value = [
      { alarm_no: 'ALM20240115001', alarm_type: '水质超标', alarm_level: 'urgent', title: '出水COD超标', current_value: 35, threshold_value: 30, alarm_time: '2024-01-15 10:30', status: 'pending' },
      { alarm_no: 'ALM20240115002', alarm_type: '工艺参数异常', alarm_level: 'warning', title: '生化池DO偏低', current_value: 1.2, threshold_value: 1.5, alarm_time: '2024-01-15 11:15', status: 'processing' },
      { alarm_no: 'ALM20240115003', alarm_type: '工况异常', alarm_level: 'normal', title: '进水流量波动', current_value: 750, threshold_value: 700, alarm_time: '2024-01-15 12:00', status: 'resolved' },
      { alarm_no: 'ALM20240115004', alarm_type: '水质超标', alarm_level: 'warning', title: '出水氨氮偏高', current_value: 4.8, threshold_value: 4, alarm_time: '2024-01-15 14:20', status: 'pending' }
    ]
  } finally {
    loading.value = false
  }
}

const viewAlarm = (record: any) => {
  currentAlarm.value = record
  showDetailDrawer.value = true
}

const handleAlarm = (record: any) => {
  currentAlarm.value = record
  handleForm.handle_result = ''
  showHandleModal.value = true
}

const submitHandle = async () => {
  if (!handleForm.handle_result) {
    Message.warning('请填写处理结果')
    return
  }
  submitLoading.value = true
  try {
    await productionApi.handleAlarm(currentAlarm.value.id, handleForm)
    Message.success('处理成功')
    showHandleModal.value = false
    fetchAlarms()
  } catch (e) {
    Message.error('处理失败')
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchAlarms()
})
</script>

<style scoped>
.alarm-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-item {
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.stat-item.urgent {
  background: linear-gradient(135deg, #ffece8, #fff);
  border: 1px solid #f53f3f;
}

.stat-item.warning {
  background: linear-gradient(135deg, #fff7e8, #fff);
  border: 1px solid #ff7d00;
}

.stat-item.normal {
  background: linear-gradient(135deg, #e8f3ff, #fff);
  border: 1px solid #165DFF;
}

.stat-item.pending {
  background: linear-gradient(135deg, #f7f8fa, #fff);
  border: 1px solid #86909c;
}

.stat-item .count {
  font-size: 32px;
  font-weight: 600;
}

.stat-item.urgent .count { color: #f53f3f; }
.stat-item.warning .count { color: #ff7d00; }
.stat-item.normal .count { color: #165DFF; }
.stat-item.pending .count { color: #4e5969; }

.stat-item .label {
  font-size: 14px;
  color: #86909c;
  margin-top: 4px;
}

.filter-bar {
  margin-bottom: 16px;
}
</style>
