<template>
  <div class="page-container">
    <div class="page-header">
      <h2>安全巡检</h2>
      <p>巡检计划管理 / 电子巡检执行 / 巡检统计分析</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="巡检计划">
        <div class="table-operations">
          <a-input-search placeholder="搜索计划名称" style="width: 240px;" />
          <a-button type="primary" @click="showAddModal = true">
            <template #icon><icon-plus /></template>
            新建计划
          </a-button>
        </div>
        <a-table :columns="planColumns" :data="plans" :loading="loading">
          <template #status="{ record }">
            <a-tag :color="record.status === 'active' ? 'green' : 'gray'">
              {{ record.status === 'active' ? '启用' : '停用' }}
            </a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" @click="editPlan(record)">编辑</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="巡检执行">
        <a-table :columns="recordColumns" :data="records">
          <template #status="{ record }">
            <a-tag :color="record.status === 'normal' ? 'green' : 'red'">
              {{ record.status === 'normal' ? '正常' : '异常' }}
            </a-tag>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="统计分析">
        <a-row :gutter="16">
          <a-col :span="8">
            <a-statistic title="本月巡检次数" :value="stats.total" />
          </a-col>
          <a-col :span="8">
            <a-statistic title="发现问题数" :value="stats.issues" />
          </a-col>
          <a-col :span="8">
            <a-statistic title="巡检完成率" :value="stats.rate" suffix="%" />
          </a-col>
        </a-row>
        <div ref="chartRef" style="height: 300px; margin-top: 20px;"></div>
      </a-tab-pane>
    </a-tabs>
    
    <a-modal v-model:visible="showAddModal" :title="editingPlan ? '编辑巡检计划' : '新建巡检计划'" @ok="handleAdd">
      <a-form :model="form" layout="vertical">
        <a-form-item label="计划名称" required>
          <a-input v-model="form.plan_name" />
        </a-form-item>
        <a-form-item label="巡检类型">
          <a-select v-model="form.inspection_type">
            <a-option value="daily">日常巡检</a-option>
            <a-option value="special">专项巡检</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="巡检频次">
          <a-select v-model="form.frequency">
            <a-option value="daily">每日</a-option>
            <a-option value="weekly">每周</a-option>
            <a-option value="monthly">每月</a-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import * as echarts from 'echarts'

import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const showAddModal = ref(false)
const showDetailDrawer = ref(false)
const editingPlan = ref<any>(null)
const currentPlan = ref<any>(null)
const chartRef = ref<HTMLElement>()
const form = reactive({ plan_name: '', inspection_type: 'daily', frequency: 'daily' })
const stats = reactive({ total: 45, issues: 8, rate: 95 })

const planColumns = [
  { title: '计划编号', dataIndex: 'plan_no' },
  { title: '计划名称', dataIndex: 'plan_name' },
  { title: '巡检类型', dataIndex: 'inspection_type' },
  { title: '巡检频次', dataIndex: 'frequency' },
  { title: '状态', slotName: 'status' },
  { title: '操作', slotName: 'operations' }
]

const recordColumns = [
  { title: '记录编号', dataIndex: 'record_no' },
  { title: '巡检人', dataIndex: 'inspector_name' },
  { title: '巡检时间', dataIndex: 'inspection_date' },
  { title: '发现问题', dataIndex: 'findings' },
  { title: '状态', slotName: 'status' }
]

const plans = ref([
  { plan_no: 'IP001', plan_name: '日常安全巡检', inspection_type: '日常巡检', frequency: '每日', status: 'active' },
  { plan_no: 'IP002', plan_name: '消防设施巡检', inspection_type: '专项巡检', frequency: '每周', status: 'active' },
  { plan_no: 'IP003', plan_name: '特种设备巡检', inspection_type: '专项巡检', frequency: '每月', status: 'active' }
])

const records = ref([
  { record_no: 'IR20240115001', inspector_name: '张三', inspection_date: '2024-01-15 09:00', findings: '无异常', status: 'normal' },
  { record_no: 'IR20240115002', inspector_name: '李四', inspection_date: '2024-01-15 14:00', findings: '灭火器压力不足', status: 'abnormal' }
])

const handleAdd = () => {
  if (editingPlan.value) {
    const index = plans.value.findIndex(p => p.plan_no === editingPlan.value.plan_no)
    if (index > -1) {
      Object.assign(plans.value[index], form)
      Message.success('编辑成功')
    }
  } else {
    plans.value.push({
      plan_no: 'IP' + String(Date.now()).slice(-3),
      plan_name: form.plan_name,
      inspection_type: form.inspection_type === 'daily' ? '日常巡检' : '专项巡检',
      frequency: form.frequency === 'daily' ? '每日' : form.frequency === 'weekly' ? '每周' : '每月',
      status: 'active'
    })
    Message.success('新建成功')
  }
  showAddModal.value = false
  editingPlan.value = null
}

const editPlan = (record: any) => {
  editingPlan.value = record
  Object.assign(form, {
    plan_name: record.plan_name,
    inspection_type: record.inspection_type === '日常巡检' ? 'daily' : 'special',
    frequency: record.frequency === '每日' ? 'daily' : record.frequency === '每周' ? 'weekly' : 'monthly'
  })
  showAddModal.value = true
}

const viewPlan = (record: any) => {
  currentPlan.value = record
  Message.info(`查看计划: ${record.plan_name}`)
}

onMounted(() => {
  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
      yAxis: { type: 'value' },
      series: [{ name: '巡检次数', type: 'bar', data: [6, 7, 6, 8, 7, 5, 6], itemStyle: { color: '#165DFF' } }]
    })
  }
})
</script>

<style scoped>
.table-operations { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
