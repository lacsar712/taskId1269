<template>
  <div class="detection-task">
    <a-card title="检测任务管理">
      <template #extra>
        <a-button type="primary" @click="showTaskModal = true">
          <template #icon><icon-plus /></template>
          新建任务
        </a-button>
      </template>

      <!-- 搜索栏 -->
      <a-row :gutter="16" style="margin-bottom: 16px;">
        <a-col :span="6">
          <a-input v-model="searchForm.taskNo" placeholder="任务编号" allow-clear />
        </a-col>
        <a-col :span="6">
          <a-select v-model="searchForm.status" placeholder="任务状态" allow-clear>
            <a-option value="pending">待检测</a-option>
            <a-option value="testing">检测中</a-option>
            <a-option value="completed">已完成</a-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-range-picker v-model="searchForm.dateRange" style="width: 100%;" />
        </a-col>
        <a-col :span="6">
          <a-space>
            <a-button type="primary" @click="handleSearch">查询</a-button>
            <a-button @click="handleReset">重置</a-button>
          </a-space>
        </a-col>
      </a-row>

      <!-- 任务列表 -->
      <a-table :columns="columns" :data="taskList" :pagination="pagination" :loading="loading">
        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">{{ record.statusText }}</a-tag>
        </template>
        <template #priority="{ record }">
          <a-tag :color="getPriorityColor(record.priority)">{{ record.priorityText }}</a-tag>
        </template>
        <template #operations="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="editTask(record)">编辑</a-button>
          </a-space>
        </template>
      </a-table>
    </a-card>

    <!-- 新建/编辑任务弹窗 -->
    <a-modal v-model:visible="showTaskModal" :title="isEdit ? '编辑任务' : '新建任务'" width="600px" @ok="handleSaveTask">
      <a-form :model="taskForm" layout="vertical">
        <a-form-item label="任务名称" required>
          <a-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </a-form-item>
        <a-form-item label="关联样品" required>
          <a-select v-model="taskForm.sampleId" placeholder="请选择样品">
            <a-option v-for="sample in sampleList" :key="sample.id" :value="sample.id">
              {{ sample.name }}
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="检测项目">
          <a-select v-model="taskForm.items" placeholder="请选择检测项目" multiple>
            <a-option value="COD">COD</a-option>
            <a-option value="BOD">BOD</a-option>
            <a-option value="SS">SS</a-option>
            <a-option value="NH3-N">氨氮</a-option>
            <a-option value="TP">总磷</a-option>
            <a-option value="TN">总氮</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="优先级">
          <a-select v-model="taskForm.priority" placeholder="请选择优先级">
            <a-option value="high">高</a-option>
            <a-option value="medium">中</a-option>
            <a-option value="low">低</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="截止时间">
          <a-date-picker v-model="taskForm.deadline" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model="taskForm.remark" placeholder="请输入备注" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const showTaskModal = ref(false)
const isEdit = ref(false)

const searchForm = reactive({
  taskNo: '',
  status: '',
  dateRange: []
})

const taskForm = reactive({
  name: '',
  sampleId: '',
  items: [],
  priority: 'medium',
  deadline: '',
  remark: ''
})

const columns = [
  { title: '任务编号', dataIndex: 'taskNo' },
  { title: '任务名称', dataIndex: 'name' },
  { title: '关联样品', dataIndex: 'sampleName' },
  { title: '检测项目', dataIndex: 'itemsText' },
  { title: '状态', dataIndex: 'status', slotName: 'status' },
  { title: '优先级', dataIndex: 'priority', slotName: 'priority' },
  { title: '创建时间', dataIndex: 'createTime' },
  { title: '截止时间', dataIndex: 'deadline' },
  { title: '操作', slotName: 'operations', width: 180 }
]

const taskList = ref([
  {
    id: 1,
    taskNo: 'TASK-2024-001',
    name: '进水水质检测',
    sampleName: '进水样品-001',
    itemsText: 'COD, BOD, SS',
    status: 'testing',
    statusText: '检测中',
    priority: 'high',
    priorityText: '高',
    createTime: '2024-01-15 09:00',
    deadline: '2024-01-16'
  },
  {
    id: 2,
    taskNo: 'TASK-2024-002',
    name: '出水水质检测',
    sampleName: '出水样品-001',
    itemsText: 'NH3-N, TP, TN',
    status: 'pending',
    statusText: '待检测',
    priority: 'medium',
    priorityText: '中',
    createTime: '2024-01-15 10:00',
    deadline: '2024-01-17'
  },
  {
    id: 3,
    taskNo: 'TASK-2024-003',
    name: '污泥检测',
    sampleName: '污泥样品-001',
    itemsText: 'COD, BOD',
    status: 'completed',
    statusText: '已完成',
    priority: 'low',
    priorityText: '低',
    createTime: '2024-01-14 14:00',
    deadline: '2024-01-15'
  }
])

const sampleList = ref([
  { id: 1, name: '进水样品-001' },
  { id: 2, name: '出水样品-001' },
  { id: 3, name: '污泥样品-001' }
])

const pagination = reactive({
  total: 3,
  current: 1,
  pageSize: 10
})

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    pending: 'orange',
    testing: 'blue',
    completed: 'green'
  }
  return colors[status] || 'gray'
}

const getPriorityColor = (priority: string) => {
  const colors: Record<string, string> = {
    high: 'red',
    medium: 'orange',
    low: 'green'
  }
  return colors[priority] || 'gray'
}

const handleSearch = () => {
  Message.success('查询成功')
}

const handleReset = () => {
  searchForm.taskNo = ''
  searchForm.status = ''
  searchForm.dateRange = []
}

const viewTask = (record: any) => {
  Message.info(`查看任务: ${record.name}`)
}

const editTask = (record: any) => {
  isEdit.value = true
  taskForm.name = record.name
  showTaskModal.value = true
}

const deleteTask = (record: any) => {
  Message.success(`删除任务: ${record.name}`)
}

const handleSaveTask = () => {
  Message.success(isEdit.value ? '编辑成功' : '新建成功')
  showTaskModal.value = false
  isEdit.value = false
}
</script>

<style scoped>
.detection-task {
  padding: 20px;
}
</style>
