<template>
  <div class="page-container">
    <div class="page-header">
      <h2>数据溯源</h2>
      <p>报表数据溯源 / 修改日志 / 数据导出归档</p>
    </div>

    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="数据溯源">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 16px;">
            <a-form-item label="报表编号">
              <a-input v-model="traceForm.reportNo" placeholder="请输入报表编号" style="width: 200px;" />
            </a-form-item>
            <a-form-item label="数据项">
              <a-input v-model="traceForm.dataItem" placeholder="请输入数据项" style="width: 200px;" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="searchTrace">
                <template #icon><icon-search /></template>
                查询
              </a-button>
            </a-form-item>
          </a-form>

          <a-table :columns="traceColumns" :data="traceList" :loading="loading">
            <template #dataSource="{ record }">
              <a-tag>{{ record.data_source }}</a-tag>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>

      <a-tab-pane key="2" title="修改日志">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 16px;">
            <a-form-item label="操作类型">
              <a-select v-model="logForm.operationType" placeholder="请选择" style="width: 200px;" allow-clear>
                <a-option value="create">创建</a-option>
                <a-option value="edit">编辑</a-option>
                <a-option value="delete">删除</a-option>
                <a-option value="approve">审核</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="操作人">
              <a-input v-model="logForm.operator" placeholder="请输入操作人" style="width: 200px;" />
            </a-form-item>
            <a-form-item label="时间范围">
              <a-range-picker v-model="logForm.dateRange" style="width: 300px;" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="searchLogs">查询</a-button>
            </a-form-item>
          </a-form>

          <a-table :columns="logColumns" :data="logList" :loading="loading">
            <template #operationType="{ record }">
              <a-tag :color="getOperationColor(record.operation_type)">
                {{ getOperationText(record.operation_type) }}
              </a-tag>
            </template>
            <template #changes="{ record }">
              <a-popover>
                <template #content>
                  <div v-for="change in record.changes" :key="change.field" style="margin-bottom: 8px;">
                    <strong>{{ change.field }}:</strong> {{ change.old_value }} → {{ change.new_value }}
                  </div>
                </template>
                <a-link>查看变更</a-link>
              </a-popover>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>

      <a-tab-pane key="3" title="数据导出归档">
        <a-card>
          <template #title>
            <span>导出记录</span>
          </template>
          <template #extra>
            <a-button type="primary" @click="exportData">
              <template #icon><icon-download /></template>
              导出数据
            </a-button>
          </template>

          <a-table :columns="exportColumns" :data="exportList" :loading="loading">
            <template #status="{ record }">
              <a-tag :color="record.status === 'success' ? 'green' : record.status === 'failed' ? 'red' : 'orange'">
                {{ record.status === 'success' ? '成功' : record.status === 'failed' ? '失败' : '进行中' }}
              </a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" v-if="record.status === 'success'">
                  下载
                </a-button>
              </a-space>
            </template>
          </a-table>
        </a-card>

        <a-card style="margin-top: 16px;">
          <template #title>
            <span>归档管理</span>
          </template>
          <a-table :columns="archiveColumns" :data="archiveList">
            <template #fileSize="{ record }">
              {{ formatFileSize(record.file_size) }}
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

const traceForm = reactive({
  reportNo: '',
  dataItem: ''
})

const logForm = reactive({
  operationType: '',
  operator: '',
  dateRange: []
})

const traceColumns = [
  { title: '报表编号', dataIndex: 'report_no', width: 150 },
  { title: '数据项', dataIndex: 'data_item', width: 150 },
  { title: '数据值', dataIndex: 'data_value', width: 120 },
  { title: '数据来源', slotName: 'dataSource', width: 120 },
  { title: '采集时间', dataIndex: 'collect_time', width: 180 },
  { title: '采集设备', dataIndex: 'device', width: 150 },
  { title: '操作', slotName: 'operations', width: 120, fixed: 'right' }
]

const traceList = ref([
  {
    id: 1,
    report_no: 'RPT20250101001',
    data_item: '处理水量',
    data_value: '15600',
    data_source: '生产数据',
    collect_time: '2025-01-01 23:00:00',
    device: '流量计-001'
  },
  {
    id: 2,
    report_no: 'RPT20250101001',
    data_item: 'COD',
    data_value: '28',
    data_source: '水质数据',
    collect_time: '2025-01-01 23:00:00',
    device: '在线监测-002'
  },
  {
    id: 3,
    report_no: 'RPT20250101001',
    data_item: '能耗',
    data_value: '12500',
    data_source: '能耗数据',
    collect_time: '2025-01-01 23:00:00',
    device: '电表-003'
  }
])

const logColumns = [
  { title: '操作时间', dataIndex: 'operation_time', width: 180 },
  { title: '操作类型', slotName: 'operationType', width: 120 },
  { title: '报表编号', dataIndex: 'report_no', width: 150 },
  { title: '操作人', dataIndex: 'operator', width: 120 },
  { title: '变更内容', slotName: 'changes', width: 120 },
  { title: '操作IP', dataIndex: 'ip', width: 150 },
  { title: '备注', dataIndex: 'remark', ellipsis: true }
]

const logList = ref([
  {
    id: 1,
    operation_time: '2025-01-01 10:00:00',
    operation_type: 'create',
    report_no: 'RPT20250101001',
    operator: '张三',
    changes: [
      { field: '处理水量', old_value: '-', new_value: '15600' },
      { field: 'COD', old_value: '-', new_value: '28' }
    ],
    ip: '192.168.1.100',
    remark: '创建生产日报'
  },
  {
    id: 2,
    operation_time: '2025-01-01 11:00:00',
    operation_type: 'edit',
    report_no: 'RPT20250101001',
    operator: '李四',
    changes: [
      { field: '处理水量', old_value: '15600', new_value: '15650' }
    ],
    ip: '192.168.1.101',
    remark: '修正数据'
  },
  {
    id: 3,
    operation_time: '2025-01-01 12:00:00',
    operation_type: 'approve',
    report_no: 'RPT20250101001',
    operator: '王五',
    changes: [],
    ip: '192.168.1.102',
    remark: '审核通过'
  }
])

const exportColumns = [
  { title: '导出时间', dataIndex: 'export_time', width: 180 },
  { title: '报表名称', dataIndex: 'report_name', ellipsis: true },
  { title: '文件名称', dataIndex: 'file_name', width: 200 },
  { title: '文件大小', dataIndex: 'file_size', width: 120 },
  { title: '导出人', dataIndex: 'exporter', width: 120 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 150, fixed: 'right' }
]

const exportList = ref([
  {
    id: 1,
    export_time: '2025-01-01 18:00:00',
    report_name: '2025年1月生产月报',
    file_name: 'RPT20250101001.xlsx',
    file_size: 245760,
    exporter: '张三',
    status: 'success'
  },
  {
    id: 2,
    export_time: '2025-01-02 10:00:00',
    report_name: '2025年1月2日生产日报',
    file_name: 'RPT20250102001.xlsx',
    file_size: 189440,
    exporter: '李四',
    status: 'success'
  },
  {
    id: 3,
    export_time: '2025-01-03 14:00:00',
    report_name: '2025年第一季度环保监管报表',
    file_name: 'RPT20250103001.xlsx',
    file_size: 0,
    exporter: '王五',
    status: 'processing'
  }
])

const archiveColumns = [
  { title: '归档时间', dataIndex: 'archive_time', width: 180 },
  { title: '报表名称', dataIndex: 'report_name', ellipsis: true },
  { title: '文件名称', dataIndex: 'file_name', width: 200 },
  { title: '文件大小', slotName: 'fileSize', width: 120 },
  { title: '归档人', dataIndex: 'archiver', width: 120 },
  { title: '操作', slotName: 'operations', width: 150, fixed: 'right' }
]

const archiveList = ref([
  {
    id: 1,
    archive_time: '2025-01-01 20:00:00',
    report_name: '2025年1月生产月报',
    file_name: 'RPT20250101001.xlsx',
    file_size: 245760,
    archiver: '张三'
  },
  {
    id: 2,
    archive_time: '2025-01-02 12:00:00',
    report_name: '2025年1月2日生产日报',
    file_name: 'RPT20250102001.xlsx',
    file_size: 189440,
    archiver: '李四'
  }
])

const getOperationColor = (type: string) => {
  const map: Record<string, string> = {
    create: 'green',
    edit: 'blue',
    delete: 'red',
    approve: 'orange'
  }
  return map[type] || 'gray'
}

const getOperationText = (type: string) => {
  const map: Record<string, string> = {
    create: '创建',
    edit: '编辑',
    delete: '删除',
    approve: '审核'
  }
  return map[type] || type
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const searchTrace = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    Message.success('查询成功')
  }, 500)
}

const searchLogs = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    Message.success('查询成功')
  }, 500)
}

const viewDetail = (record: any) => {
  Message.info(`查看详情: ${record.data_item}`)
}

const exportData = () => {
  Message.success('导出任务已提交')
}

const downloadFile = (record: any) => {
  Message.success(`下载文件: ${record.file_name}`)
}

const viewArchive = (record: any) => {
  Message.info(`查看归档: ${record.file_name}`)
}

const downloadArchive = (record: any) => {
  Message.success(`下载归档: ${record.file_name}`)
}

const deleteArchive = (record: any) => {
  Message.warning(`删除归档: ${record.file_name}`)
}
</script>

<style scoped>
.page-container {
  padding: 16px;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
}

.page-header p {
  margin: 0;
  font-size: 14px;
  color: #86909c;
}
</style>
