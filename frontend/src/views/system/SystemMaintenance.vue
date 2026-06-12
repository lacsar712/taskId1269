<template>
  <div class="page-container">
    <div class="page-header">
      <h2>系统维护</h2>
      <p>数据备份恢复 / 版本更新 / 异常修复</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="数据备份恢复">
        <a-card>
          <a-row :gutter="16" style="margin-bottom: 20px;">
            <a-col :span="8">
              <a-card title="备份设置" size="small">
                <a-form :model="backupConfig" layout="vertical" size="small">
                  <a-form-item label="自动备份">
                    <a-switch v-model="backupConfig.autoBackup" />
                  </a-form-item>
                  <a-form-item v-if="backupConfig.autoBackup" label="备份时间">
                    <a-time-picker v-model="backupConfig.backupTime" format="HH:mm" style="width: 100%;" />
                  </a-form-item>
                  <a-form-item v-if="backupConfig.autoBackup" label="备份频率">
                    <a-select v-model="backupConfig.frequency" style="width: 100%;">
                      <a-option value="daily">每天</a-option>
                      <a-option value="weekly">每周</a-option>
                      <a-option value="monthly">每月</a-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item label="保留备份数">
                    <a-input-number v-model="backupConfig.retentionCount" :min="1" :max="30" style="width: 100%;" />
                  </a-form-item>
                  <a-form-item>
                    <a-button type="primary" block @click="saveBackupConfig">保存设置</a-button>
                  </a-form-item>
                </a-form>
              </a-card>
            </a-col>
            <a-col :span="16">
              <a-card title="备份记录" size="small">
                <template #extra>
                  <a-button type="primary" @click="createBackup">立即备份</a-button>
                </template>
                
                <a-table
                  :columns="backupColumns"
                  :data="backups"
                  :pagination="backupPagination"
                  size="small"
                >
                  <template #size="{ record }">
                    {{ formatFileSize(record.size) }}
                  </template>
                  <template #status="{ record }">
                    <a-tag :color="record.status === '成功' ? 'green' : 'red'">{{ record.status }}</a-tag>
                  </template>
                  <template #operations="{ record }">
                    <a-space>
                      <a-button type="text" size="small" @click="restoreBackup(record)">恢复</a-button>
                      <a-popconfirm content="确定要删除该备份吗？" @ok="deleteBackup(record)">
                        <a-button type="text" size="small" status="danger">删除</a-button>
                      </a-popconfirm>
                    </a-space>
                  </template>
                </a-table>
              </a-card>
            </a-col>
          </a-row>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="版本更新">
        <a-card>
          <a-alert message="当前版本：v1.2.0" type="info" style="margin-bottom: 20px;">
            <template #description>
              最后更新时间：2026-01-15 10:00:00
            </template>
          </a-alert>
          
          <a-card title="更新历史" style="margin-bottom: 20px;">
            <a-timeline>
              <a-timeline-item v-for="version in versions" :key="version.id">
                <template #dot>
                  <icon-check-circle v-if="version.installed" style="color: #00B42A;" />
                  <icon-clock-circle v-else style="color: #86909c;" />
                </template>
                <a-space direction="vertical" size="small">
                  <div>
                    <a-tag color="blue" style="margin-right: 8px;">{{ version.number }}</a-tag>
                    <span style="font-weight: 600;">{{ version.title }}</span>
                  </div>
                  <div style="color: #86909c; font-size: 13px;">{{ version.date }}</div>
                  <div>{{ version.description }}</div>
                  <a-button v-if="!version.installed" type="primary" size="small" @click="installVersion(version)">安装更新</a-button>
                </a-space>
              </a-timeline-item>
            </a-timeline>
          </a-card>
          
          <a-card title="手动更新">
            <a-upload
              :file-list="updateFileList"
              :limit="1"
              accept=".zip,.tar.gz"
              @change="handleUpdateFileChange"
            >
              <template #upload-button>
                <a-button>
                  <template #icon><icon-upload /></template>
                  选择更新包
                </a-button>
              </template>
            </a-upload>
            <a-button 
              type="primary" 
              style="margin-top: 16px;" 
              :disabled="updateFileList.length === 0"
              @click="uploadUpdate"
            >
              上传并安装
            </a-button>
          </a-card>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="异常修复">
        <a-card>
          <a-row :gutter="16" style="margin-bottom: 20px;">
            <a-col :span="8">
              <a-statistic title="系统健康度" :value="systemHealth" suffix="%">
                <template #prefix><icon-heart /></template>
              </a-statistic>
            </a-col>
            <a-col :span="8">
              <a-statistic title="待修复异常" :value="pendingIssues">
                <template #prefix><icon-exclamation-circle /></template>
              </a-statistic>
            </a-col>
            <a-col :span="8">
              <a-statistic title="已修复异常" :value="fixedIssues">
                <template #prefix><icon-check-circle /></template>
              </a-statistic>
            </a-col>
          </a-row>
          
          <a-card title="异常列表" size="small">
            <a-table
              :columns="issueColumns"
              :data="issues"
              :pagination="issuePagination"
              size="small"
            >
              <template #level="{ record }">
                <a-tag :color="getIssueLevelColor(record.level)">{{ record.level }}</a-tag>
              </template>
              <template #status="{ record }">
                <a-tag :color="getIssueStatusColor(record.status)">{{ record.status }}</a-tag>
              </template>
              <template #operations="{ record }">
                <a-space>
                  <a-button v-if="record.status === '待修复'" type="text" size="small" @click="fixIssue(record)">修复</a-button>
                </a-space>
              </template>
            </a-table>
          </a-card>
          
          <a-divider />
          
          <a-card title="系统诊断" size="small">
            <a-space direction="vertical" style="width: 100%;">
              <a-button type="primary" @click="runDiagnosis">运行系统诊断</a-button>
              <a-descriptions v-if="diagnosisResult" :column="1" bordered size="small">
                <a-descriptions-item label="数据库连接">{{ diagnosisResult.database }}</a-descriptions-item>
                <a-descriptions-item label="文件系统">{{ diagnosisResult.filesystem }}</a-descriptions-item>
                <a-descriptions-item label="网络连接">{{ diagnosisResult.network }}</a-descriptions-item>
                <a-descriptions-item label="内存使用">{{ diagnosisResult.memory }}</a-descriptions-item>
                <a-descriptions-item label="CPU使用">{{ diagnosisResult.cpu }}</a-descriptions-item>
              </a-descriptions>
            </a-space>
          </a-card>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const backupPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const issuePagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const backupConfig = reactive({
  autoBackup: true,
  backupTime: '02:00',
  frequency: 'daily',
  retentionCount: 7
})

const backups = ref([
  { id: 1, name: 'backup_20260204_020000.sql', size: 524288000, createTime: '2026-02-04 02:00:00', status: '成功' },
  { id: 2, name: 'backup_20260203_020000.sql', size: 521000000, createTime: '2026-02-03 02:00:00', status: '成功' },
  { id: 3, name: 'backup_20260202_020000.sql', size: 518000000, createTime: '2026-02-02 02:00:00', status: '成功' },
  { id: 4, name: 'backup_20260201_020000.sql', size: 515000000, createTime: '2026-02-01 02:00:00', status: '失败' }
])

const versions = ref([
  { id: 1, number: 'v1.2.0', title: '当前版本', date: '2026-01-15', description: '修复已知问题，优化性能', installed: true },
  { id: 2, number: 'v1.3.0', title: '新功能更新', date: '2026-02-01', description: '新增绩效管理模块，优化界面体验', installed: false },
  { id: 3, number: 'v1.1.0', title: '历史版本', date: '2025-12-01', description: '初始版本发布', installed: true }
])

const updateFileList = ref([])

const systemHealth = ref(95)
const pendingIssues = ref(3)
const fixedIssues = ref(12)

const issues = ref([
  { id: 1, title: '数据库连接超时', level: '高', status: '待修复', description: '数据库连接偶尔超时', createTime: '2026-02-04 10:00:00' },
  { id: 2, title: '文件系统空间不足', level: '中', status: '待修复', description: '日志文件占用空间过大', createTime: '2026-02-03 15:30:00' },
  { id: 3, title: '缓存清理异常', level: '低', status: '待修复', description: '缓存清理功能偶尔失败', createTime: '2026-02-02 09:20:00' },
  { id: 4, title: '接口响应慢', level: '中', status: '已修复', description: '第三方接口响应时间过长', createTime: '2026-01-30 14:00:00', fixTime: '2026-02-01 10:00:00' }
])

const diagnosisResult = ref<any>(null)

const backupColumns = [
  { title: '备份文件名', dataIndex: 'name', width: 250 },
  { title: '文件大小', slotName: 'size', width: 120 },
  { title: '备份时间', dataIndex: 'createTime', width: 180 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const issueColumns = [
  { title: '异常标题', dataIndex: 'title', width: 200 },
  { title: '级别', slotName: 'level', width: 100 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '描述', dataIndex: 'description', ellipsis: true },
  { title: '发现时间', dataIndex: 'createTime', width: 180 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

const getIssueLevelColor = (level: string) => {
  const colors: Record<string, string> = {
    '高': 'red',
    '中': 'orange',
    '低': 'blue'
  }
  return colors[level] || 'gray'
}

const getIssueStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    '待修复': 'red',
    '修复中': 'orange',
    '已修复': 'green'
  }
  return colors[status] || 'gray'
}

const saveBackupConfig = () => {
  Message.success('备份设置保存成功')
}

const createBackup = () => {
  Message.loading('备份中...', 2)
  setTimeout(() => {
    backups.value.unshift({
      id: Date.now(),
      name: `backup_${new Date().toISOString().replace(/[-:]/g, '').split('.')[0]}.sql`,
      size: Math.floor(Math.random() * 100000000) + 500000000,
      createTime: new Date().toLocaleString('zh-CN'),
      status: '成功'
    })
    Message.success('备份创建成功')
  }, 2000)
}

const restoreBackup = (record: any) => {
  Message.warning('恢复操作将覆盖当前数据，请确认！')
  // 实际应该弹出确认对话框
}

const downloadBackup = (record: any) => {
  Message.success(`下载备份：${record.name}`)
}

const deleteBackup = (record: any) => {
  const index = backups.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    backups.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const installVersion = (version: any) => {
  Message.loading('安装更新中...', 3)
  setTimeout(() => {
    version.installed = true
    Message.success(`版本${version.number}安装成功`)
  }, 3000)
}

const handleUpdateFileChange = (fileList: any[]) => {
  updateFileList.value = fileList
}

const uploadUpdate = () => {
  Message.loading('上传并安装更新中...', 3)
  setTimeout(() => {
    Message.success('更新安装成功，请重启系统')
    updateFileList.value = []
  }, 3000)
}

const viewIssueDetail = (record: any) => {
  Message.info(`查看异常详情：${record.title}`)
}

const fixIssue = (record: any) => {
  Message.loading('修复中...', 2)
  setTimeout(() => {
    record.status = '已修复'
    record.fixTime = new Date().toLocaleString('zh-CN')
    pendingIssues.value--
    fixedIssues.value++
    Message.success('异常修复成功')
  }, 2000)
}

const runDiagnosis = () => {
  Message.loading('诊断中...', 2)
  setTimeout(() => {
    diagnosisResult.value = {
      database: '正常',
      filesystem: '正常',
      network: '正常',
      memory: '使用率 65%',
      cpu: '使用率 45%'
    }
    Message.success('系统诊断完成')
  }, 2000)
}

// 初始化分页
backupPagination.total = backups.value.length
issuePagination.total = issues.value.length
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
