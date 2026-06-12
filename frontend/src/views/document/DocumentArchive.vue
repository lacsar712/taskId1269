<template>
  <div class="page-container">
    <div class="page-header">
      <h2>归档备份</h2>
      <p>文档归档 / 自动备份 / 过期处置</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="文档归档">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="keyword" placeholder="搜索文档名称" style="width: 240px;" @search="fetchArchiveData" />
            <a-select v-model="archiveStatus" placeholder="归档状态" style="width: 120px;" allow-clear>
              <a-option value="archived">已归档</a-option>
              <a-option value="unarchived">未归档</a-option>
            </a-select>
          </a-space>
          <a-space>
            <a-button @click="handleBatchArchive">批量归档</a-button>
            <a-button type="primary" @click="showArchiveModal = true">新建归档</a-button>
          </a-space>
        </div>
        
        <a-table 
          :columns="archiveColumns" 
          :data="archiveDocuments" 
          :loading="loading" 
          :pagination="archivePagination"
          :row-selection="rowSelection"
        >
          <template #archive_status="{ record }">
            <a-tag :color="record.archive_status === 'archived' ? 'green' : 'gray'">
              {{ record.archive_status === 'archived' ? '已归档' : '未归档' }}
            </a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" v-if="record.archive_status !== 'archived'" @click="handleArchive(record)">归档</a-button>
              <a-button type="text" size="small" v-if="record.archive_status === 'archived'" @click="handleUnarchive(record)">取消归档</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="自动备份">
        <div class="backup-config">
          <a-card title="备份配置">
            <a-form :model="backupConfig" layout="vertical">
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="备份频率">
                    <a-select v-model="backupConfig.frequency">
                      <a-option value="daily">每日</a-option>
                      <a-option value="weekly">每周</a-option>
                      <a-option value="monthly">每月</a-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="备份时间">
                    <a-time-picker v-model="backupConfig.time" format="HH:mm" style="width: 100%;" />
                  </a-form-item>
                </a-col>
              </a-row>
              <a-form-item label="备份路径">
                <a-input v-model="backupConfig.path" placeholder="请输入备份路径" />
              </a-form-item>
              <a-form-item label="保留天数">
                <a-input-number v-model="backupConfig.retention_days" :min="1" style="width: 100%;" />
              </a-form-item>
              <a-form-item>
                <a-space>
                  <a-button type="primary" @click="handleSaveBackupConfig">保存配置</a-button>
                  <a-button @click="handleTestBackup">测试备份</a-button>
                </a-space>
              </a-form-item>
            </a-form>
          </a-card>
        </div>
        
        <div class="backup-history" style="margin-top: 16px;">
          <a-card title="备份历史">
            <a-table :columns="backupColumns" :data="backupHistory" :loading="backupLoading">
              <template #status="{ record }">
                <a-tag :color="record.status === 'success' ? 'green' : 'red'">
                  {{ record.status === 'success' ? '成功' : '失败' }}
                </a-tag>
              </template>
            </a-table>
          </a-card>
        </div>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="过期处置">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="expiredKeyword" placeholder="搜索文档名称" style="width: 240px;" @search="fetchExpiredData" />
            <a-select v-model="expiredStatus" placeholder="处置状态" style="width: 120px;" allow-clear>
              <a-option value="pending">待处置</a-option>
              <a-option value="deleted">已删除</a-option>
              <a-option value="archived">已归档</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="showExpiredConfigModal = true">过期规则配置</a-button>
        </div>
        
        <a-table :columns="expiredColumns" :data="expiredDocuments" :loading="expiredLoading" :pagination="expiredPagination">
          <template #expired_status="{ record }">
            <a-tag :color="getExpiredStatusColor(record.expired_status)">
              {{ getExpiredStatusText(record.expired_status) }}
            </a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-popconfirm content="确定要删除该文档吗？" @ok="handleDeleteExpired(record)" v-if="record.expired_status === 'pending'">
                <a-button type="text" size="small" status="danger">删除</a-button>
              </a-popconfirm>
              <a-button type="text" size="small" v-if="record.expired_status === 'pending'" @click="handleArchiveExpired(record)">归档</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 新建归档弹窗 -->
    <a-modal v-model:visible="showArchiveModal" title="新建归档" @ok="handleCreateArchive" width="600px">
      <a-form :model="archiveForm" layout="vertical">
        <a-form-item label="归档名称" required>
          <a-input v-model="archiveForm.name" />
        </a-form-item>
        <a-form-item label="归档说明">
          <a-textarea v-model="archiveForm.description" :max-length="500" show-word-limit />
        </a-form-item>
        <a-form-item label="选择文档">
          <a-select v-model="archiveForm.document_ids" multiple placeholder="请选择要归档的文档">
            <a-option v-for="doc in archiveDocuments" :key="doc.id" :value="doc.id">{{ doc.name }}</a-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 过期规则配置弹窗 -->
    <a-modal v-model:visible="showExpiredConfigModal" title="过期规则配置" @ok="handleSaveExpiredConfig" width="600px">
      <a-form :model="expiredConfig" layout="vertical">
        <a-form-item label="过期天数">
          <a-input-number v-model="expiredConfig.days" :min="1" style="width: 100%;" />
          <template #extra>文档超过指定天数未访问将被标记为过期</template>
        </a-form-item>
        <a-form-item label="自动处置方式">
          <a-radio-group v-model="expiredConfig.action">
            <a-radio value="delete">自动删除</a-radio>
            <a-radio value="archive">自动归档</a-radio>
            <a-radio value="none">仅标记</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="通知提醒">
          <a-checkbox-group v-model="expiredConfig.notifications">
            <a-checkbox value="before">过期前提醒</a-checkbox>
            <a-checkbox value="after">过期后提醒</a-checkbox>
          </a-checkbox-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const backupLoading = ref(false)
const expiredLoading = ref(false)
const showArchiveModal = ref(false)
const showExpiredConfigModal = ref(false)
const keyword = ref('')
const expiredKeyword = ref('')
const archiveStatus = ref('')
const expiredStatus = ref('')
const archiveDocuments = ref<any[]>([])
const backupHistory = ref<any[]>([])
const expiredDocuments = ref<any[]>([])
const selectedRows = ref<any[]>([])
const archivePagination = reactive({ current: 1, pageSize: 10, total: 0 })
const expiredPagination = reactive({ current: 1, pageSize: 10, total: 0 })

const archiveForm = reactive({
  name: '',
  description: '',
  document_ids: []
})

const backupConfig = reactive({
  frequency: 'daily',
  time: '02:00',
  path: '/backup/documents',
  retention_days: 30
})

const expiredConfig = reactive({
  days: 365,
  action: 'archive',
  notifications: ['before']
})

const rowSelection = reactive({
  type: 'checkbox',
  showCheckedAll: true,
  selectedRowKeys: [],
  onSelect: (row: any, selected: boolean) => {
    if (selected) {
      selectedRows.value.push(row)
    } else {
      selectedRows.value = selectedRows.value.filter(r => r.id !== row.id)
    }
  }
})

const archiveColumns = [
  { title: '文档编号', dataIndex: 'doc_no', width: 140 },
  { title: '文档名称', dataIndex: 'name' },
  { title: '分类', dataIndex: 'category_name', width: 120 },
  { title: '归档时间', dataIndex: 'archive_time', width: 160 },
  { title: '归档人', dataIndex: 'archiver', width: 100 },
  { title: '归档状态', slotName: 'archive_status', width: 100 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const backupColumns = [
  { title: '备份时间', dataIndex: 'backup_time', width: 160 },
  { title: '备份文件', dataIndex: 'backup_file', width: 200 },
  { title: '文件大小', dataIndex: 'file_size', width: 100 },
  { title: '状态', slotName: 'status', width: 80 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const expiredColumns = [
  { title: '文档编号', dataIndex: 'doc_no', width: 140 },
  { title: '文档名称', dataIndex: 'name' },
  { title: '最后访问时间', dataIndex: 'last_access_time', width: 160 },
  { title: '过期时间', dataIndex: 'expired_time', width: 160 },
  { title: '处置状态', slotName: 'expired_status', width: 100 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const getExpiredStatusColor = (status: string) => {
  const map: Record<string, string> = {
    pending: 'orange',
    deleted: 'red',
    archived: 'green'
  }
  return map[status] || 'gray'
}

const getExpiredStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处置',
    deleted: '已删除',
    archived: '已归档'
  }
  return map[status] || '未知'
}

const fetchArchiveData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    archiveDocuments.value = [
      { id: 1, doc_no: 'DOC20240115001', name: '设备操作手册.pdf', category_name: '操作手册', archive_time: '2024-01-15 10:30', archiver: '张三', archive_status: 'archived' },
      { id: 2, doc_no: 'DOC20240115002', name: '安全管理制度.docx', category_name: '安全规范', archive_time: '', archiver: '', archive_status: 'unarchived' },
      { id: 3, doc_no: 'DOC20240116001', name: '生产流程优化方案.xlsx', category_name: '技术文档', archive_time: '2024-01-16 09:15', archiver: '王五', archive_status: 'archived' }
    ]
    archivePagination.total = archiveDocuments.value.length
  } finally {
    loading.value = false
  }
}

const fetchBackupHistory = async () => {
  backupLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 300))
    backupHistory.value = [
      { id: 1, backup_time: '2024-01-15 02:00', backup_file: 'backup_20240115.zip', file_size: '1.2GB', status: 'success' },
      { id: 2, backup_time: '2024-01-14 02:00', backup_file: 'backup_20240114.zip', file_size: '1.1GB', status: 'success' },
      { id: 3, backup_time: '2024-01-13 02:00', backup_file: 'backup_20240113.zip', file_size: '1.0GB', status: 'success' }
    ]
  } finally {
    backupLoading.value = false
  }
}

const fetchExpiredData = async () => {
  expiredLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    expiredDocuments.value = [
      { id: 1, doc_no: 'DOC20230115001', name: '旧版操作手册.pdf', last_access_time: '2023-01-15', expired_time: '2024-01-15', expired_status: 'pending' },
      { id: 2, doc_no: 'DOC20230120001', name: '历史数据报表.xlsx', last_access_time: '2023-01-20', expired_time: '2024-01-20', expired_status: 'deleted' },
      { id: 3, doc_no: 'DOC20230201001', name: '培训资料.pptx', last_access_time: '2023-02-01', expired_time: '2024-02-01', expired_status: 'archived' }
    ]
    expiredPagination.total = expiredDocuments.value.length
  } finally {
    expiredLoading.value = false
  }
}

const handleArchive = (record: any) => {
  Message.success(`已归档: ${record.name}`)
  record.archive_status = 'archived'
}

const handleUnarchive = (record: any) => {
  Message.success(`已取消归档: ${record.name}`)
  record.archive_status = 'unarchived'
}

const handleBatchArchive = () => {
  if (selectedRows.value.length === 0) {
    Message.warning('请选择要归档的文档')
    return
  }
  Message.success(`已批量归档 ${selectedRows.value.length} 个文档`)
}

const handleCreateArchive = () => {
  Message.success('归档创建成功')
  showArchiveModal.value = false
}

const handleViewArchive = (record: any) => {
  Message.info(`查看归档: ${record.name}`)
}

const handleSaveBackupConfig = () => {
  Message.success('备份配置已保存')
}

const handleTestBackup = () => {
  Message.success('备份测试成功')
}

const handleRestore = (record: any) => {
  Message.info(`恢复备份: ${record.backup_file}`)
}

const handleDownloadBackup = (record: any) => {
  Message.info(`下载备份: ${record.backup_file}`)
}

const handleDeleteExpired = (record: any) => {
  Message.success(`已删除过期文档: ${record.name}`)
  record.expired_status = 'deleted'
}

const handleArchiveExpired = (record: any) => {
  Message.success(`已归档过期文档: ${record.name}`)
  record.expired_status = 'archived'
}

const handleExtendExpired = (record: any) => {
  Message.success(`已延期: ${record.name}`)
}

const handleSaveExpiredConfig = () => {
  Message.success('过期规则配置已保存')
  showExpiredConfigModal.value = false
}

onMounted(() => {
  fetchArchiveData()
  fetchBackupHistory()
  fetchExpiredData()
})
</script>

<style scoped>
.table-operations {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.backup-config {
  margin-bottom: 16px;
}
</style>
