<template>
  <div class="data-management">
    <a-card title="数据管理">
      <template #extra>
        <a-space>
          <a-button @click="handleExport">
            <template #icon><icon-download /></template>
            导出数据
          </a-button>
        </a-space>
      </template>

      <!-- 搜索栏 -->
      <a-row :gutter="16" style="margin-bottom: 16px;">
        <a-col :span="6">
          <a-input v-model="searchForm.keyword" placeholder="关键词搜索" allow-clear />
        </a-col>
        <a-col :span="6">
          <a-select v-model="searchForm.type" placeholder="数据类型" allow-clear>
            <a-option value="water">水质数据</a-option>
            <a-option value="sludge">污泥数据</a-option>
            <a-option value="air">气体数据</a-option>
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

      <!-- 数据统计 -->
      <a-row :gutter="16" style="margin-bottom: 20px;">
        <a-col :span="6">
          <a-statistic title="总数据量" :value="stats.total">
            <template #prefix><icon-database /></template>
          </a-statistic>
        </a-col>
        <a-col :span="6">
          <a-statistic title="本月新增" :value="stats.monthly">
            <template #prefix><icon-plus-circle /></template>
          </a-statistic>
        </a-col>
        <a-col :span="6">
          <a-statistic title="合格率" :value="stats.passRate" suffix="%">
            <template #prefix><icon-check-circle /></template>
          </a-statistic>
        </a-col>
        <a-col :span="6">
          <a-statistic title="异常数据" :value="stats.abnormal">
            <template #prefix><icon-exclamation-circle /></template>
          </a-statistic>
        </a-col>
      </a-row>

      <!-- 数据列表 -->
      <a-table :columns="columns" :data="dataList" :pagination="pagination" :loading="loading">
        <template #status="{ record }">
          <a-tag :color="record.isNormal ? 'green' : 'red'">
            {{ record.isNormal ? '正常' : '异常' }}
          </a-tag>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)

const searchForm = reactive({
  keyword: '',
  type: '',
  dateRange: []
})

const stats = reactive({
  total: 12580,
  monthly: 856,
  passRate: 98.5,
  abnormal: 12
})

const columns = [
  { title: '数据编号', dataIndex: 'dataNo' },
  { title: '数据类型', dataIndex: 'typeText' },
  { title: '检测项目', dataIndex: 'item' },
  { title: '检测值', dataIndex: 'value' },
  { title: '单位', dataIndex: 'unit' },
  { title: '标准值', dataIndex: 'standard' },
  { title: '状态', dataIndex: 'status', slotName: 'status' },
  { title: '检测时间', dataIndex: 'testTime' },
]

const dataList = ref([
  {
    id: 1,
    dataNo: 'DATA-2024-001',
    typeText: '水质数据',
    item: 'COD',
    value: '45.6',
    unit: 'mg/L',
    standard: '≤50',
    isNormal: true,
    testTime: '2024-01-15 09:30'
  },
  {
    id: 2,
    dataNo: 'DATA-2024-002',
    typeText: '水质数据',
    item: 'BOD',
    value: '12.3',
    unit: 'mg/L',
    standard: '≤10',
    isNormal: false,
    testTime: '2024-01-15 09:35'
  },
  {
    id: 3,
    dataNo: 'DATA-2024-003',
    typeText: '水质数据',
    item: '氨氮',
    value: '3.2',
    unit: 'mg/L',
    standard: '≤5',
    isNormal: true,
    testTime: '2024-01-15 09:40'
  },
  {
    id: 4,
    dataNo: 'DATA-2024-004',
    typeText: '污泥数据',
    item: '含水率',
    value: '78.5',
    unit: '%',
    standard: '≤80',
    isNormal: true,
    testTime: '2024-01-15 10:00'
  }
])

const pagination = reactive({
  total: 4,
  current: 1,
  pageSize: 10
})

const handleSearch = () => {
  Message.success('查询成功')
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.type = ''
  searchForm.dateRange = []
}

const handleExport = () => {
  Message.success('导出数据成功')
}

const viewData = (record: any) => {
  Message.info(`查看数据: ${record.dataNo}`)
}

const editData = (record: any) => {
  Message.info(`编辑数据: ${record.dataNo}`)
}
</script>

<style scoped>
.data-management {
  padding: 20px;
}
</style>
