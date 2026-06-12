<template>
  <div class="report-management">
    <a-card title="报告管理">
      <template #extra>
        <a-button type="primary" @click="showReportModal = true">
          <template #icon><icon-plus /></template>
          生成报告
        </a-button>
      </template>

      <!-- 搜索栏 -->
      <a-row :gutter="16" style="margin-bottom: 16px;">
        <a-col :span="6">
          <a-input v-model="searchForm.reportNo" placeholder="报告编号" allow-clear />
        </a-col>
        <a-col :span="6">
          <a-select v-model="searchForm.status" placeholder="报告状态" allow-clear>
            <a-option value="draft">草稿</a-option>
            <a-option value="reviewing">审核中</a-option>
            <a-option value="approved">已批准</a-option>
            <a-option value="published">已发布</a-option>
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

      <!-- 报告列表 -->
      <a-table :columns="columns" :data="reportList" :pagination="pagination" :loading="loading">
        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">{{ record.statusText }}</a-tag>
        </template>
      </a-table>
    </a-card>

    <!-- 生成报告弹窗 -->
    <a-modal v-model:visible="showReportModal" title="生成报告" width="600px" @ok="handleGenerateReport">
      <a-form :model="reportForm" layout="vertical">
        <a-form-item label="报告名称" required>
          <a-input v-model="reportForm.name" placeholder="请输入报告名称" />
        </a-form-item>
        <a-form-item label="报告类型" required>
          <a-select v-model="reportForm.type" placeholder="请选择报告类型">
            <a-option value="daily">日报</a-option>
            <a-option value="weekly">周报</a-option>
            <a-option value="monthly">月报</a-option>
            <a-option value="special">专项报告</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="报告周期">
          <a-range-picker v-model="reportForm.dateRange" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="包含数据">
          <a-checkbox-group v-model="reportForm.includeData">
            <a-checkbox value="water">水质数据</a-checkbox>
            <a-checkbox value="sludge">污泥数据</a-checkbox>
            <a-checkbox value="statistics">统计分析</a-checkbox>
            <a-checkbox value="trend">趋势图表</a-checkbox>
          </a-checkbox-group>
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model="reportForm.remark" placeholder="请输入备注" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const showReportModal = ref(false)

const searchForm = reactive({
  reportNo: '',
  status: '',
  dateRange: []
})

const reportForm = reactive({
  name: '',
  type: '',
  dateRange: [],
  includeData: [],
  remark: ''
})

const columns = [
  { title: '报告编号', dataIndex: 'reportNo' },
  { title: '报告名称', dataIndex: 'name' },
  { title: '报告类型', dataIndex: 'typeText' },
  { title: '报告周期', dataIndex: 'period' },
  { title: '状态', dataIndex: 'status', slotName: 'status' },
  { title: '创建人', dataIndex: 'creator' },
  { title: '创建时间', dataIndex: 'createTime' },
]

const reportList = ref([
  {
    id: 1,
    reportNo: 'RPT-2024-001',
    name: '2024年1月水质检测月报',
    typeText: '月报',
    period: '2024-01-01 ~ 2024-01-31',
    status: 'published',
    statusText: '已发布',
    creator: '张三',
    createTime: '2024-02-01 09:00'
  },
  {
    id: 2,
    reportNo: 'RPT-2024-002',
    name: '第3周水质检测周报',
    typeText: '周报',
    period: '2024-01-15 ~ 2024-01-21',
    status: 'approved',
    statusText: '已批准',
    creator: '李四',
    createTime: '2024-01-22 10:00'
  },
  {
    id: 3,
    reportNo: 'RPT-2024-003',
    name: '出水超标专项分析报告',
    typeText: '专项报告',
    period: '2024-01-10',
    status: 'reviewing',
    statusText: '审核中',
    creator: '王五',
    createTime: '2024-01-11 14:00'
  },
  {
    id: 4,
    reportNo: 'RPT-2024-004',
    name: '2024年1月15日日报',
    typeText: '日报',
    period: '2024-01-15',
    status: 'draft',
    statusText: '草稿',
    creator: '赵六',
    createTime: '2024-01-15 18:00'
  }
])

const pagination = reactive({
  total: 4,
  current: 1,
  pageSize: 10
})

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    draft: 'gray',
    reviewing: 'orange',
    approved: 'blue',
    published: 'green'
  }
  return colors[status] || 'gray'
}

const handleSearch = () => {
  Message.success('查询成功')
}

const handleReset = () => {
  searchForm.reportNo = ''
  searchForm.status = ''
  searchForm.dateRange = []
}

const viewReport = (record: any) => {
  Message.info(`查看报告: ${record.name}`)
}

const downloadReport = (record: any) => {
  Message.success(`下载报告: ${record.name}`)
}

const submitReport = (record: any) => {
  Message.success(`提交审核: ${record.name}`)
}

const approveReport = (record: any) => {
  Message.success(`批准报告: ${record.name}`)
}

const handleGenerateReport = () => {
  Message.success('报告生成成功')
  showReportModal.value = false
}
</script>

<style scoped>
.report-management {
  padding: 20px;
}
</style>
