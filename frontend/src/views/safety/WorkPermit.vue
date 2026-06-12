<template>
  <div class="page-container">
    <div class="page-header">
      <h2>作业许可</h2>
      <p>许可申请 / 许可审批 / 作业记录</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="许可申请">
        <div class="table-operations">
          <a-space>
            <a-select placeholder="作业类型" style="width: 140px;" allow-clear>
              <a-option value="fire">动火作业</a-option>
              <a-option value="confined">受限空间</a-option>
              <a-option value="height">高处作业</a-option>
            </a-select>
            <a-select placeholder="状态" style="width: 120px;" allow-clear>
              <a-option value="pending">待审批</a-option>
              <a-option value="approved">已批准</a-option>
              <a-option value="rejected">已驳回</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="showAddModal = true">
            <template #icon><icon-plus /></template>
            申请许可
          </a-button>
        </div>
        <a-table :columns="columns" :data="permits">
          <template #status="{ record }">
            <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="审批记录">
        <a-table :columns="approvalColumns" :data="approvals" />
      </a-tab-pane>
      
      <a-tab-pane key="3" title="作业记录">
        <a-table :columns="workColumns" :data="workRecords" />
      </a-tab-pane>
    </a-tabs>
    
    <a-modal v-model:visible="showAddModal" title="申请作业许可" @ok="handleAdd">
      <a-form :model="form" layout="vertical">
        <a-form-item label="作业类型" required>
          <a-select v-model="form.work_type">
            <a-option value="fire">动火作业</a-option>
            <a-option value="confined">受限空间作业</a-option>
            <a-option value="height">高处作业</a-option>
            <a-option value="electric">临时用电</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="作业地点">
          <a-input v-model="form.work_location" />
        </a-form-item>
        <a-form-item label="作业内容">
          <a-textarea v-model="form.work_content" />
        </a-form-item>
        <a-form-item label="作业时间">
          <a-range-picker v-model="form.work_time" show-time style="width: 100%;" />
        </a-form-item>
        <a-form-item label="安全措施">
          <a-textarea v-model="form.safety_measures" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const showAddModal = ref(false)
const form = reactive({ work_type: '', work_location: '', work_content: '', work_time: [], safety_measures: '' })

const columns = [
  { title: '许可编号', dataIndex: 'permit_no' },
  { title: '作业类型', dataIndex: 'work_type' },
  { title: '作业地点', dataIndex: 'work_location' },
  { title: '申请人', dataIndex: 'applicant_name' },
  { title: '申请时间', dataIndex: 'apply_time' },
  { title: '状态', slotName: 'status' },
  { title: '操作', slotName: 'operations' }
]

const approvalColumns = [
  { title: '许可编号', dataIndex: 'permit_no' },
  { title: '审批人', dataIndex: 'approver' },
  { title: '审批时间', dataIndex: 'approve_time' },
  { title: '审批结果', dataIndex: 'result' },
  { title: '审批意见', dataIndex: 'opinion' }
]

const workColumns = [
  { title: '许可编号', dataIndex: 'permit_no' },
  { title: '作业类型', dataIndex: 'work_type' },
  { title: '开始时间', dataIndex: 'start_time' },
  { title: '结束时间', dataIndex: 'end_time' },
  { title: '作业人员', dataIndex: 'workers' },
  { title: '完成情况', dataIndex: 'completion' }
]

const permits = ref([
  { permit_no: 'WP20240115001', work_type: '动火作业', work_location: '污泥脱水间', applicant_name: '张三', apply_time: '2024-01-15 09:00', status: 'pending' },
  { permit_no: 'WP20240114001', work_type: '高处作业', work_location: '进水泵房', applicant_name: '李四', apply_time: '2024-01-14 14:00', status: 'approved' }
])

const approvals = ref([
  { permit_no: 'WP20240114001', approver: '王主任', approve_time: '2024-01-14 15:00', result: '批准', opinion: '同意，注意安全' }
])

const workRecords = ref([
  { permit_no: 'WP20240114001', work_type: '高处作业', start_time: '2024-01-14 16:00', end_time: '2024-01-14 18:00', workers: '李四、赵五', completion: '已完成' }
])

const getStatusColor = (status: string) => ({ pending: 'blue', approved: 'green', rejected: 'red', completed: 'gray' }[status] || 'gray')
const getStatusText = (status: string) => ({ pending: '待审批', approved: '已批准', rejected: '已驳回', completed: '已完成' }[status] || '未知')
const handleAdd = () => { showAddModal.value = false }
</script>

<style scoped>
.table-operations { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
