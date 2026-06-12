<template>
  <div class="page-container">
    <div class="page-header">
      <h2>安全培训</h2>
      <p>培训计划 / 培训记录 / 持证管理</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="培训计划">
        <div class="table-operations">
          <a-input-search placeholder="搜索培训" style="width: 240px;" />
          <a-button type="primary">
            <template #icon><icon-plus /></template>
            新建培训
          </a-button>
        </div>
        <a-table :columns="planColumns" :data="trainingPlans">
          <template #status="{ record }">
            <a-tag :color="record.status === 'completed' ? 'green' : record.status === 'ongoing' ? 'blue' : 'gray'">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="培训记录">
        <a-table :columns="recordColumns" :data="trainingRecords" />
      </a-tab-pane>
      
      <a-tab-pane key="3" title="持证管理">
        <a-table :columns="certColumns" :data="certificates">
          <template #status="{ record }">
            <a-tag :color="record.status === 'valid' ? 'green' : 'red'">
              {{ record.status === 'valid' ? '有效' : '即将到期' }}
            </a-tag>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const planColumns = [
  { title: '培训编号', dataIndex: 'training_no' },
  { title: '培训主题', dataIndex: 'title' },
  { title: '培训类型', dataIndex: 'training_type' },
  { title: '培训时间', dataIndex: 'training_date' },
  { title: '培训讲师', dataIndex: 'trainer' },
  { title: '状态', slotName: 'status' }
]

const recordColumns = [
  { title: '培训主题', dataIndex: 'title' },
  { title: '参训人员', dataIndex: 'participant' },
  { title: '培训时间', dataIndex: 'date' },
  { title: '培训时长', dataIndex: 'duration' },
  { title: '考核成绩', dataIndex: 'score' }
]

const certColumns = [
  { title: '姓名', dataIndex: 'name' },
  { title: '证书名称', dataIndex: 'cert_name' },
  { title: '证书编号', dataIndex: 'cert_no' },
  { title: '有效期至', dataIndex: 'expiry_date' },
  { title: '状态', slotName: 'status' }
]

const trainingPlans = ref([
  { training_no: 'TR001', title: '新员工安全教育', training_type: '入职培训', training_date: '2024-01-20', trainer: '安全部', status: 'planned' },
  { training_no: 'TR002', title: '消防安全培训', training_type: '专项培训', training_date: '2024-01-15', trainer: '消防队', status: 'completed' },
  { training_no: 'TR003', title: '化学品安全操作', training_type: '专项培训', training_date: '2024-01-18', trainer: '技术部', status: 'ongoing' }
])

const trainingRecords = ref([
  { title: '消防安全培训', participant: '张三', date: '2024-01-15', duration: '4小时', score: '92分' },
  { title: '消防安全培训', participant: '李四', date: '2024-01-15', duration: '4小时', score: '88分' }
])

const certificates = ref([
  { name: '张三', cert_name: '特种作业操作证', cert_no: 'TZ2024001', expiry_date: '2025-06-30', status: 'valid' },
  { name: '李四', cert_name: '电工证', cert_no: 'DG2024001', expiry_date: '2024-03-15', status: 'expiring' }
])

const getStatusText = (status: string) => ({ planned: '计划中', ongoing: '进行中', completed: '已完成' }[status] || '未知')
</script>

<style scoped>
.table-operations { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
