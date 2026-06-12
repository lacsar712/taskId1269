<template>
  <div class="qc-management">
    <a-card title="质控管理">
      <template #extra>
        <a-button type="primary" @click="showQCModal = true">
          <template #icon><icon-plus /></template>
          新建质控记录
        </a-button>
      </template>

      <!-- 统计概览 -->
      <a-row :gutter="16" style="margin-bottom: 20px;">
        <a-col :span="6">
          <a-statistic title="本月质控次数" :value="stats.total">
            <template #prefix><icon-experiment /></template>
          </a-statistic>
        </a-col>
        <a-col :span="6">
          <a-statistic title="合格次数" :value="stats.passed">
            <template #prefix><icon-check-circle /></template>
          </a-statistic>
        </a-col>
        <a-col :span="6">
          <a-statistic title="合格率" :value="stats.passRate" suffix="%">
            <template #prefix><icon-bar-chart /></template>
          </a-statistic>
        </a-col>
        <a-col :span="6">
          <a-statistic title="待处理问题" :value="stats.pending">
            <template #prefix><icon-exclamation-circle /></template>
          </a-statistic>
        </a-col>
      </a-row>

      <!-- 搜索栏 -->
      <a-row :gutter="16" style="margin-bottom: 16px;">
        <a-col :span="6">
          <a-select v-model="searchForm.type" placeholder="质控类型" allow-clear>
            <a-option value="blank">空白样</a-option>
            <a-option value="parallel">平行样</a-option>
            <a-option value="standard">标准样</a-option>
            <a-option value="spike">加标样</a-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-select v-model="searchForm.result" placeholder="质控结果" allow-clear>
            <a-option value="passed">合格</a-option>
            <a-option value="failed">不合格</a-option>
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

      <!-- 质控记录列表 -->
      <a-table :columns="columns" :data="qcList" :pagination="pagination" :loading="loading">
        <template #result="{ record }">
          <a-tag :color="record.result === 'passed' ? 'green' : 'red'">
            {{ record.result === 'passed' ? '合格' : '不合格' }}
          </a-tag>
        </template>
      </a-table>
    </a-card>

    <!-- 新建质控记录弹窗 -->
    <a-modal v-model:visible="showQCModal" title="新建质控记录" width="600px" @ok="handleSaveQC">
      <a-form :model="qcForm" layout="vertical">
        <a-form-item label="质控类型" required>
          <a-select v-model="qcForm.type" placeholder="请选择质控类型">
            <a-option value="blank">空白样</a-option>
            <a-option value="parallel">平行样</a-option>
            <a-option value="standard">标准样</a-option>
            <a-option value="spike">加标样</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="检测项目" required>
          <a-select v-model="qcForm.item" placeholder="请选择检测项目">
            <a-option value="COD">COD</a-option>
            <a-option value="BOD">BOD</a-option>
            <a-option value="SS">SS</a-option>
            <a-option value="NH3-N">氨氮</a-option>
            <a-option value="TP">总磷</a-option>
            <a-option value="TN">总氮</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="检测值">
          <a-input-number v-model="qcForm.value" placeholder="请输入检测值" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="标准值">
          <a-input-number v-model="qcForm.standard" placeholder="请输入标准值" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="允许偏差(%)">
          <a-input-number v-model="qcForm.tolerance" placeholder="请输入允许偏差" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model="qcForm.remark" placeholder="请输入备注" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const showQCModal = ref(false)

const searchForm = reactive({
  type: '',
  result: '',
  dateRange: []
})

const qcForm = reactive({
  type: '',
  item: '',
  value: null,
  standard: null,
  tolerance: 10,
  remark: ''
})

const stats = reactive({
  total: 156,
  passed: 148,
  passRate: 94.9,
  pending: 3
})

const columns = [
  { title: '质控编号', dataIndex: 'qcNo' },
  { title: '质控类型', dataIndex: 'typeText' },
  { title: '检测项目', dataIndex: 'item' },
  { title: '检测值', dataIndex: 'value' },
  { title: '标准值', dataIndex: 'standard' },
  { title: '偏差', dataIndex: 'deviation' },
  { title: '结果', dataIndex: 'result', slotName: 'result' },
  { title: '检测人', dataIndex: 'tester' },
  { title: '检测时间', dataIndex: 'testTime' },
]

const qcList = ref([
  {
    id: 1,
    qcNo: 'QC-2024-001',
    typeText: '平行样',
    item: 'COD',
    value: '45.6',
    standard: '45.0',
    deviation: '1.3%',
    result: 'passed',
    tester: '张三',
    testTime: '2024-01-15 09:30'
  },
  {
    id: 2,
    qcNo: 'QC-2024-002',
    typeText: '标准样',
    item: 'BOD',
    value: '18.5',
    standard: '20.0',
    deviation: '7.5%',
    result: 'passed',
    tester: '李四',
    testTime: '2024-01-15 10:00'
  },
  {
    id: 3,
    qcNo: 'QC-2024-003',
    typeText: '加标样',
    item: '氨氮',
    value: '85.2',
    standard: '100.0',
    deviation: '14.8%',
    result: 'failed',
    tester: '王五',
    testTime: '2024-01-15 11:00'
  },
  {
    id: 4,
    qcNo: 'QC-2024-004',
    typeText: '空白样',
    item: 'COD',
    value: '0.5',
    standard: '0',
    deviation: '-',
    result: 'passed',
    tester: '赵六',
    testTime: '2024-01-15 14:00'
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
  searchForm.type = ''
  searchForm.result = ''
  searchForm.dateRange = []
}

const viewQC = (record: any) => {
  Message.info(`查看质控记录: ${record.qcNo}`)
}

const handleQC = (record: any) => {
  Message.info(`处理质控问题: ${record.qcNo}`)
}

const handleSaveQC = () => {
  Message.success('质控记录保存成功')
  showQCModal.value = false
}
</script>

<style scoped>
.qc-management {
  padding: 20px;
}
</style>
