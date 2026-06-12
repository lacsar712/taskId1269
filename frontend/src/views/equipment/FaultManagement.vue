<template>
  <div class="page-container">
    <div class="page-header">
      <h2>故障管理</h2>
      <p>故障告警 / 故障维修 / 故障分析</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="故障列表">
        <div class="table-operations">
          <a-space>
            <a-select placeholder="故障级别" style="width: 120px;" allow-clear>
              <a-option value="critical">严重</a-option>
              <a-option value="major">一般</a-option>
              <a-option value="minor">轻微</a-option>
            </a-select>
            <a-select placeholder="状态" style="width: 120px;" allow-clear>
              <a-option value="pending">待维修</a-option>
              <a-option value="repairing">维修中</a-option>
              <a-option value="completed">已完成</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="showAddModal = true">
            <template #icon><icon-plus /></template>
            报修
          </a-button>
        </div>
        <a-table :columns="columns" :data="faults">
          <template #fault_level="{ record }">
            <a-tag :color="getLevelColor(record.fault_level)">{{ getLevelText(record.fault_level) }}</a-tag>
          </template>
          <template #status="{ record }">
            <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="故障分析">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-card title="故障类型分布">
              <div ref="typeChartRef" style="height: 300px;"></div>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card title="故障趋势">
              <div ref="trendChartRef" style="height: 300px;"></div>
            </a-card>
          </a-col>
        </a-row>
      </a-tab-pane>
    </a-tabs>
    
    <a-modal v-model:visible="showAddModal" title="设备报修" @ok="handleAdd">
      <a-form :model="form" layout="vertical">
        <a-form-item label="设备" required>
          <a-select v-model="form.equipment_id">
            <a-option :value="1">曝气风机#1</a-option>
            <a-option :value="2">曝气风机#2</a-option>
            <a-option :value="3">提升泵#1</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="故障类型">
          <a-select v-model="form.fault_type">
            <a-option value="equipment">设备故障</a-option>
            <a-option value="param">参数超限</a-option>
            <a-option value="maintenance">维保到期</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="故障描述" required>
          <a-textarea v-model="form.description" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import * as echarts from 'echarts'

const showAddModal = ref(false)
const typeChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const form = reactive({ equipment_id: null, fault_type: '', description: '' })

const columns = [
  { title: '故障编号', dataIndex: 'fault_no' },
  { title: '设备名称', dataIndex: 'equipment_name' },
  { title: '故障类型', dataIndex: 'fault_type' },
  { title: '故障级别', slotName: 'fault_level' },
  { title: '故障描述', dataIndex: 'description', ellipsis: true },
  { title: '故障时间', dataIndex: 'fault_time' },
  { title: '状态', slotName: 'status' }
]

const faults = ref([
  { fault_no: 'FT20240115001', equipment_name: '曝气风机#3', fault_type: '设备故障', fault_level: 'major', description: '轴承异响', fault_time: '2024-01-15 10:30', status: 'repairing' },
  { fault_no: 'FT20240114001', equipment_name: '提升泵#2', fault_type: '参数超限', fault_level: 'minor', description: '流量偏低', fault_time: '2024-01-14 15:00', status: 'completed' }
])

const getLevelColor = (l: string) => ({ critical: 'red', major: 'orange', minor: 'blue' }[l] || 'gray')
const getLevelText = (l: string) => ({ critical: '严重', major: '一般', minor: '轻微' }[l] || '未知')
const getStatusColor = (s: string) => ({ pending: 'blue', repairing: 'orange', completed: 'green' }[s] || 'gray')
const getStatusText = (s: string) => ({ pending: '待维修', repairing: '维修中', completed: '已完成' }[s] || '未知')
const handleAdd = () => { showAddModal.value = false }

onMounted(() => {
  if (typeChartRef.value) {
    const chart = echarts.init(typeChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{ type: 'pie', radius: '60%', data: [{ value: 35, name: '设备故障' }, { value: 25, name: '参数超限' }, { value: 15, name: '维保到期' }, { value: 10, name: '其他' }] }]
    })
  }
  if (trendChartRef.value) {
    const chart = echarts.init(trendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
      yAxis: { type: 'value' },
      series: [{ name: '故障数', type: 'line', smooth: true, data: [5, 8, 6, 10, 7, 6] }]
    })
  }
})
</script>

<style scoped>
.table-operations { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
