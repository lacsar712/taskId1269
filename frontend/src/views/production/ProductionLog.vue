<template>
  <div class="page-container">
    <div class="page-header">
      <h2>生产日志管理</h2>
      <p>自动日志生成 / 人工操作记录 / 交接班记录</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="生产日志列表">
        <div class="table-operations">
          <a-space>
            <a-range-picker style="width: 240px;" />
            <a-select v-model="logType" placeholder="日志类型" style="width: 120px;" allow-clear>
              <a-option value="auto">自动生成</a-option>
              <a-option value="manual">人工记录</a-option>
              <a-option value="handover">交接班</a-option>
            </a-select>
            <a-select v-model="shift" placeholder="班次" style="width: 100px;" allow-clear>
              <a-option value="morning">早班</a-option>
              <a-option value="afternoon">中班</a-option>
              <a-option value="night">晚班</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="showAddModal = true">
            <template #icon><icon-plus /></template>
            添加日志
          </a-button>
        </div>
        
        <a-table :columns="columns" :data="logs" :loading="loading" :pagination="pagination">
          <template #log_type="{ record }">
            <a-tag :color="getTypeColor(record.log_type)">{{ getTypeText(record.log_type) }}</a-tag>
          </template>
          <template #shift="{ record }">
            <span>{{ getShiftText(record.shift) }}</span>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" @click="viewLog(record)">查看</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="交接班记录">
        <a-timeline>
          <a-timeline-item v-for="item in handoverRecords" :key="item.id" :dot-color="item.status === 'completed' ? 'green' : 'blue'">
            <div class="timeline-item">
              <div class="timeline-header">
                <span class="time">{{ item.time }}</span>
                <a-tag :color="item.status === 'completed' ? 'green' : 'blue'" size="small">
                  {{ item.status === 'completed' ? '已完成' : '进行中' }}
                </a-tag>
              </div>
              <div class="timeline-title">{{ item.from }} → {{ item.to }}</div>
              <div class="timeline-content">{{ item.content }}</div>
            </div>
          </a-timeline-item>
        </a-timeline>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 添加日志弹窗 -->
    <a-modal v-model:visible="showAddModal" title="添加生产日志" @ok="handleAddLog" :ok-loading="submitLoading">
      <a-form :model="logForm" layout="vertical">
        <a-form-item label="日志日期" required>
          <a-date-picker v-model="logForm.log_date" show-time style="width: 100%;" />
        </a-form-item>
        <a-form-item label="日志类型" required>
          <a-select v-model="logForm.log_type">
            <a-option value="manual">人工记录</a-option>
            <a-option value="handover">交接班记录</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="班次">
          <a-select v-model="logForm.shift">
            <a-option value="morning">早班</a-option>
            <a-option value="afternoon">中班</a-option>
            <a-option value="night">晚班</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="日志内容" required>
          <a-textarea v-model="logForm.content" :max-length="2000" show-word-limit :auto-size="{ minRows: 4 }" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 查看日志弹窗 -->
    <a-modal v-model:visible="showViewModal" title="日志详情" :footer="false">
      <a-descriptions :column="1" bordered>
        <a-descriptions-item label="日志时间">{{ currentLog?.log_date }}</a-descriptions-item>
        <a-descriptions-item label="日志类型">{{ getTypeText(currentLog?.log_type) }}</a-descriptions-item>
        <a-descriptions-item label="班次">{{ getShiftText(currentLog?.shift) }}</a-descriptions-item>
        <a-descriptions-item label="记录人">{{ currentLog?.operator_name }}</a-descriptions-item>
        <a-descriptions-item label="日志内容">{{ currentLog?.content }}</a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { productionApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const showAddModal = ref(false)
const showViewModal = ref(false)
const logType = ref('')
const shift = ref('')
const logs = ref<any[]>([])
const currentLog = ref<any>(null)
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const logForm = reactive({
  log_date: '',
  log_type: 'manual',
  shift: 'morning',
  content: ''
})

const columns = [
  { title: '日志时间', dataIndex: 'log_date', width: 180 },
  { title: '类型', slotName: 'log_type', width: 100 },
  { title: '班次', slotName: 'shift', width: 80 },
  { title: '内容摘要', dataIndex: 'content', ellipsis: true },
  { title: '记录人', dataIndex: 'operator_name', width: 100 },
  { title: '操作', slotName: 'operations', width: 80 }
]

const handoverRecords = ref([
  { id: 1, time: '2024-01-15 08:00', from: '丙班(夜班)', to: '甲班(早班)', content: '夜间运行正常，曝气风机#3已切换至#4，待检修。进水COD较高，建议关注。', status: 'completed' },
  { id: 2, time: '2024-01-15 16:00', from: '甲班(早班)', to: '乙班(中班)', content: '白天运行平稳，处理量14500m³。二沉池刮泥机已完成保养。', status: 'completed' },
  { id: 3, time: '2024-01-16 00:00', from: '乙班(中班)', to: '丙班(夜班)', content: '进水量正常，出水水质达标。注意关注污泥回流比。', status: 'in_progress' }
])

const getTypeColor = (type: string) => {
  const map: Record<string, string> = { auto: 'blue', manual: 'green', handover: 'orange' }
  return map[type] || 'gray'
}

const getTypeText = (type: string) => {
  const map: Record<string, string> = { auto: '自动生成', manual: '人工记录', handover: '交接班' }
  return map[type] || '未知'
}

const getShiftText = (shift: string) => {
  const map: Record<string, string> = { morning: '早班', afternoon: '中班', night: '晚班' }
  return map[shift] || '-'
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const res: any = await productionApi.getLogs({ page: pagination.current, page_size: pagination.pageSize, log_type: logType.value || undefined, shift: shift.value || undefined })
    logs.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    logs.value = [
      { id: 1, log_date: '2024-01-15 08:30:00', log_type: 'auto', shift: 'morning', content: '系统自动记录：进水流量650m³/h，COD 185mg/L，氨氮38mg/L...', operator_name: '系统' },
      { id: 2, log_date: '2024-01-15 10:15:00', log_type: 'manual', shift: 'morning', content: '曝气风机#3出现异响，已切换至备用风机#4运行...', operator_name: '张三' },
      { id: 3, log_date: '2024-01-15 16:00:00', log_type: 'handover', shift: 'afternoon', content: '早班-中班交接：白天运行平稳，处理量14500m³...', operator_name: '李四' }
    ]
  } finally {
    loading.value = false
  }
}

const viewLog = (record: any) => {
  currentLog.value = record
  showViewModal.value = true
}

const handleAddLog = async () => {
  if (!logForm.content) {
    Message.warning('请填写日志内容')
    return
  }
  submitLoading.value = true
  try {
    await productionApi.createLog(logForm)
    Message.success('添加成功')
    showAddModal.value = false
    fetchLogs()
  } catch (e) {
    Message.error('添加失败')
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.table-operations {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.timeline-item {
  padding: 12px 16px;
  background: #f7f8fa;
  border-radius: 8px;
  margin-bottom: 8px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.timeline-header .time {
  font-size: 13px;
  color: #86909c;
}

.timeline-title {
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 8px;
}

.timeline-content {
  font-size: 14px;
  color: #4e5969;
  line-height: 1.6;
}
</style>
