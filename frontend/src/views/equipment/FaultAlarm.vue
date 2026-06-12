<template>
  <div class="page-container">
    <div class="page-header">
      <h2>故障告警</h2>
      <p>设备故障(泵/风机停机) / 参数超限(温度/振动) / 维保到期提醒等报警</p>
    </div>
    
    <div class="alarm-stats">
      <div class="stat-item" style="background: linear-gradient(135deg, #ffece8, #fff); border-color: #f53f3f;">
        <div class="count" style="color: #f53f3f;">{{ stats.equipment }}</div>
        <div class="label">设备故障</div>
      </div>
      <div class="stat-item" style="background: linear-gradient(135deg, #fff7e8, #fff); border-color: #ff7d00;">
        <div class="count" style="color: #ff7d00;">{{ stats.param }}</div>
        <div class="label">参数超限</div>
      </div>
      <div class="stat-item" style="background: linear-gradient(135deg, #e8f3ff, #fff); border-color: #165DFF;">
        <div class="count" style="color: #165DFF;">{{ stats.maintenance }}</div>
        <div class="label">维保到期</div>
      </div>
    </div>
    
    <a-table :columns="columns" :data="alarms">
      <template #alarm_type="{ record }">
        <a-tag :color="getTypeColor(record.alarm_type)">{{ getTypeText(record.alarm_type) }}</a-tag>
      </template>
      <template #status="{ record }">
        <a-tag :color="record.status === 'pending' ? 'red' : 'green'">{{ record.status === 'pending' ? '待处理' : '已处理' }}</a-tag>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const stats = reactive({ equipment: 2, param: 3, maintenance: 5 })

const columns = [
  { title: '告警时间', dataIndex: 'alarm_time' },
  { title: '设备名称', dataIndex: 'equipment_name' },
  { title: '告警类型', slotName: 'alarm_type' },
  { title: '告警内容', dataIndex: 'content' },
  { title: '状态', slotName: 'status' }
]

const alarms = ref([
  { alarm_time: '2024-01-15 10:30', equipment_name: '曝气风机#3', alarm_type: 'equipment', content: '设备停机', status: 'pending' },
  { alarm_time: '2024-01-15 09:15', equipment_name: '提升泵#1', alarm_type: 'param', content: '振动超限 (当前: 8.5mm/s, 阈值: 7mm/s)', status: 'pending' },
  { alarm_time: '2024-01-15 08:00', equipment_name: '回流泵#1', alarm_type: 'maintenance', content: '维保到期提醒', status: 'resolved' }
])

const getTypeColor = (t: string) => ({ equipment: 'red', param: 'orange', maintenance: 'blue' }[t] || 'gray')
const getTypeText = (t: string) => ({ equipment: '设备故障', param: '参数超限', maintenance: '维保到期' }[t] || '未知')
</script>

<style scoped>
.alarm-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-item { padding: 20px; border-radius: 8px; text-align: center; border: 1px solid; }
.stat-item .count { font-size: 32px; font-weight: 600; }
.stat-item .label { font-size: 14px; color: #86909c; margin-top: 4px; }
</style>
