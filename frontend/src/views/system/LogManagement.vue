<template>
  <div class="page-container">
    <div class="page-header">
      <h2>日志管理</h2>
      <p>操作日志 / 告警日志 / 日志归档</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="操作日志">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="操作人">
              <a-input v-model="opLogSearch.username" placeholder="请输入操作人" allow-clear style="width: 200px;" />
            </a-form-item>
            <a-form-item label="操作类型">
              <a-select v-model="opLogSearch.type" placeholder="请选择类型" allow-clear style="width: 150px;">
                <a-option value="新增">新增</a-option>
                <a-option value="编辑">编辑</a-option>
                <a-option value="删除">删除</a-option>
                <a-option value="查询">查询</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="操作时间">
              <a-range-picker v-model="opLogSearch.dateRange" style="width: 300px;" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="loadOpLogs">查询</a-button>
              <a-button style="margin-left: 8px;" @click="exportOpLogs">导出</a-button>
            </a-form-item>
          </a-form>
          
          <a-table
            :columns="opLogColumns"
            :data="operationLogs"
            :pagination="opLogPagination"
            :loading="loading"
          >
            <template #type="{ record }">
              <a-tag :color="getOpTypeColor(record.type)">{{ record.type }}</a-tag>
            </template>
            <template #result="{ record }">
              <a-tag :color="record.result === '成功' ? 'green' : 'red'">{{ record.result }}</a-tag>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="告警日志">
        <a-card>
          <a-row :gutter="16" style="margin-bottom: 20px;">
            <a-col :span="6">
              <a-statistic title="今日告警" :value="alarmStats.today" />
            </a-col>
            <a-col :span="6">
              <a-statistic title="未处理" :value="alarmStats.unhandled">
                <template #prefix><icon-exclamation-circle /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="已处理" :value="alarmStats.handled">
                <template #prefix><icon-check-circle /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="处理率" :value="alarmStats.handleRate" suffix="%">
                <template #prefix><icon-trophy /></template>
              </a-statistic>
            </a-col>
          </a-row>
          
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="告警级别">
              <a-select v-model="alarmLogSearch.level" placeholder="请选择级别" allow-clear style="width: 150px;">
                <a-option value="紧急">紧急</a-option>
                <a-option value="警告">警告</a-option>
                <a-option value="提示">提示</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="告警状态">
              <a-select v-model="alarmLogSearch.status" placeholder="请选择状态" allow-clear style="width: 150px;">
                <a-option value="未处理">未处理</a-option>
                <a-option value="处理中">处理中</a-option>
                <a-option value="已处理">已处理</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="告警时间">
              <a-range-picker v-model="alarmLogSearch.dateRange" style="width: 300px;" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="loadAlarmLogs">查询</a-button>
            </a-form-item>
          </a-form>
          
          <a-table
            :columns="alarmLogColumns"
            :data="alarmLogs"
            :pagination="alarmLogPagination"
          >
            <template #level="{ record }">
              <a-tag :color="getAlarmLevelColor(record.level)">{{ record.level }}</a-tag>
            </template>
            <template #status="{ record }">
              <a-tag :color="getAlarmStatusColor(record.status)">{{ record.status }}</a-tag>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="日志归档">
        <a-card>
          <a-alert message="日志归档说明" type="info" style="margin-bottom: 20px;">
            <template #description>
              系统会自动归档超过保留期的日志，归档后的日志将被压缩存储，可通过下载功能获取归档文件。
            </template>
          </a-alert>
          
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="归档时间">
              <a-range-picker v-model="archiveSearch.dateRange" style="width: 300px;" />
            </a-form-item>
            <a-form-item label="日志类型">
              <a-select v-model="archiveSearch.type" placeholder="请选择类型" allow-clear style="width: 150px;">
                <a-option value="操作日志">操作日志</a-option>
                <a-option value="告警日志">告警日志</a-option>
                <a-option value="系统日志">系统日志</a-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="loadArchives">查询</a-button>
              <a-button style="margin-left: 8px;" @click="createArchive">创建归档</a-button>
            </a-form-item>
          </a-form>
          
          <a-table
            :columns="archiveColumns"
            :data="archives"
            :pagination="archivePagination"
          >
            <template #type="{ record }">
              <a-tag>{{ record.type }}</a-tag>
            </template>
            <template #size="{ record }">
              {{ formatFileSize(record.size) }}
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-popconfirm content="确定要删除该归档吗？" @ok="deleteArchive(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)

const opLogPagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

const alarmLogPagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

const archivePagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const opLogSearch = reactive({
  username: '',
  type: '',
  dateRange: []
})

const alarmLogSearch = reactive({
  level: '',
  status: '',
  dateRange: []
})

const archiveSearch = reactive({
  dateRange: [],
  type: ''
})

const alarmStats = reactive({
  today: 156,
  unhandled: 12,
  handled: 144,
  handleRate: 92.3
})

const operationLogs = ref([
  { id: 1, username: 'admin', type: '新增', module: '用户管理', content: '新增用户：operator1', ip: '192.168.1.100', result: '成功', time: '2026-02-04 10:30:00' },
  { id: 2, username: 'operator1', type: '编辑', module: '生产管理', content: '编辑生产计划：PLAN001', ip: '192.168.1.101', result: '成功', time: '2026-02-04 09:15:00' },
  { id: 3, username: 'admin', type: '删除', module: '设备管理', content: '删除设备：EQUIP001', ip: '192.168.1.100', result: '失败', time: '2026-02-04 08:45:00' },
  { id: 4, username: 'maintainer1', type: '查询', module: '维护管理', content: '查询维护记录', ip: '192.168.1.103', result: '成功', time: '2026-02-03 16:20:00' }
])

const alarmLogs = ref([
  { id: 1, level: '紧急', title: 'COD超标告警', content: 'COD值：65mg/L，超过标准值50mg/L', status: '未处理', time: '2026-02-04 10:30:00' },
  { id: 2, level: '警告', title: '设备故障告警', content: '水泵1运行异常', status: '处理中', handler: 'maintainer1', time: '2026-02-04 09:15:00' },
  { id: 3, level: '提示', title: '数据采集异常', content: '数据采集延迟超过5分钟', status: '已处理', handler: 'admin', time: '2026-02-04 08:45:00' },
  { id: 4, level: '紧急', title: '氨氮超标告警', content: '氨氮值：8.5mg/L，超过标准值5mg/L', status: '已处理', handler: 'operator1', time: '2026-02-03 16:20:00' }
])

const archives = ref([
  { id: 1, type: '操作日志', dateRange: '2026-01-01 ~ 2026-01-31', fileCount: 1250, size: 52428800, createTime: '2026-02-01 08:00:00' },
  { id: 2, type: '告警日志', dateRange: '2026-01-01 ~ 2026-01-31', fileCount: 856, size: 31457280, createTime: '2026-02-01 08:00:00' },
  { id: 3, type: '系统日志', dateRange: '2025-12-01 ~ 2025-12-31', fileCount: 2100, size: 104857600, createTime: '2026-01-01 08:00:00' }
])

const opLogColumns = [
  { title: '操作人', dataIndex: 'username', width: 120 },
  { title: '操作类型', slotName: 'type', width: 100 },
  { title: '操作模块', dataIndex: 'module', width: 120 },
  { title: '操作内容', dataIndex: 'content', ellipsis: true },
  { title: 'IP地址', dataIndex: 'ip', width: 150 },
  { title: '结果', slotName: 'result', width: 100 },
  { title: '操作时间', dataIndex: 'time', width: 180 }
]

const alarmLogColumns = [
  { title: '告警级别', slotName: 'level', width: 100 },
  { title: '告警标题', dataIndex: 'title', width: 200 },
  { title: '告警内容', dataIndex: 'content', ellipsis: true },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '处理人', dataIndex: 'handler', width: 120 },
  { title: '告警时间', dataIndex: 'time', width: 180 },
  { title: '操作', slotName: 'operations', width: 100 }
]

const archiveColumns = [
  { title: '日志类型', slotName: 'type', width: 120 },
  { title: '时间范围', dataIndex: 'dateRange', width: 200 },
  { title: '文件数量', dataIndex: 'fileCount', width: 100 },
  { title: '文件大小', slotName: 'size', width: 120 },
  { title: '创建时间', dataIndex: 'createTime', width: 180 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const getOpTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    '新增': 'green',
    '编辑': 'blue',
    '删除': 'red',
    '查询': 'gray'
  }
  return colors[type] || 'gray'
}

const getAlarmLevelColor = (level: string) => {
  const colors: Record<string, string> = {
    '紧急': 'red',
    '警告': 'orange',
    '提示': 'blue'
  }
  return colors[level] || 'gray'
}

const getAlarmStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    '未处理': 'red',
    '处理中': 'orange',
    '已处理': 'green'
  }
  return colors[status] || 'gray'
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

const loadOpLogs = () => {
  Message.success('查询完成')
}

const exportOpLogs = () => {
  Message.success('导出中...')
}

const loadAlarmLogs = () => {
  Message.success('查询完成')
}

const viewAlarmDetail = (record: any) => {
  Message.info(`查看告警详情：${record.title}`)
}

const loadArchives = () => {
  Message.success('查询完成')
}

const createArchive = () => {
  Message.loading('创建归档中...', 2)
  setTimeout(() => {
    archives.value.unshift({
      id: Date.now(),
      type: archiveSearch.type || '操作日志',
      dateRange: archiveSearch.dateRange.length > 0 
        ? `${archiveSearch.dateRange[0]} ~ ${archiveSearch.dateRange[1]}`
        : '2026-02-01 ~ 2026-02-28',
      fileCount: Math.floor(Math.random() * 1000) + 500,
      size: Math.floor(Math.random() * 100000000) + 10000000,
      createTime: new Date().toLocaleString('zh-CN')
    })
    Message.success('归档创建成功')
  }, 2000)
}

const downloadArchive = (record: any) => {
  Message.success(`下载归档：${record.type}`)
}

const deleteArchive = (record: any) => {
  const index = archives.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    archives.value.splice(index, 1)
    Message.success('删除成功')
  }
}

// 初始化分页
opLogPagination.total = operationLogs.value.length
alarmLogPagination.total = alarmLogs.value.length
archivePagination.total = archives.value.length
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
