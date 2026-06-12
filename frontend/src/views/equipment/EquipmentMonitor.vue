<template>
  <div class="page-container">
    <div class="page-header">
      <h2>运行监控</h2>
      <p>实时状态监控 / 运行时长统计 / 远程控制</p>
    </div>
    
    <a-row :gutter="16" style="margin-bottom: 16px;">
      <a-col :span="6">
        <a-statistic title="运行设备" :value="runningCount" suffix="台">
          <template #prefix><icon-check-circle style="color: #00b42a;" /></template>
        </a-statistic>
      </a-col>
      <a-col :span="6">
        <a-statistic title="停止设备" :value="stoppedCount" suffix="台">
          <template #prefix><icon-minus-circle style="color: #86909c;" /></template>
        </a-statistic>
      </a-col>
      <a-col :span="6">
        <a-statistic title="维护中" :value="maintenanceCount" suffix="台">
          <template #prefix><icon-tool style="color: #ff7d00;" /></template>
        </a-statistic>
      </a-col>
      <a-col :span="6">
        <a-statistic title="故障设备" :value="faultCount" suffix="台">
          <template #prefix><icon-close-circle style="color: #f53f3f;" /></template>
        </a-statistic>
      </a-col>
    </a-row>
    
    <div class="equipment-grid">
      <div class="equipment-card" v-for="eq in equipmentList" :key="eq.id" :class="eq.status">
        <div class="eq-header">
          <span class="eq-name">{{ eq.name }}</span>
          <a-tag :color="getStatusColor(eq.status)" size="small">{{ getStatusText(eq.status) }}</a-tag>
        </div>
        <div class="eq-body">
          <div class="eq-param" v-for="param in eq.params" :key="param.name">
            <span class="param-name">{{ param.name }}</span>
            <span class="param-value">{{ param.value }}{{ param.unit }}</span>
          </div>
        </div>
        <div class="eq-footer">
          <span class="run-time">运行: {{ eq.running_hours }}h</span>
          <a-space>
            <a-button size="mini" v-if="eq.status === 'running'" @click="stopEquipment(eq)">停止</a-button>
            <a-button size="mini" type="primary" v-if="eq.status === 'stopped'" @click="startEquipment(eq)">启动</a-button>
          </a-space>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Message } from '@arco-design/web-vue'

const runningCount = ref(12)
const stoppedCount = ref(3)
const maintenanceCount = ref(2)
const faultCount = ref(1)

const equipmentList = ref([
  { id: 1, name: '曝气风机#1', status: 'running', running_hours: 12500, params: [{ name: '电流', value: 45, unit: 'A' }, { name: '风压', value: 0.5, unit: 'MPa' }] },
  { id: 2, name: '曝气风机#2', status: 'running', running_hours: 11800, params: [{ name: '电流', value: 43, unit: 'A' }, { name: '风压', value: 0.48, unit: 'MPa' }] },
  { id: 3, name: '曝气风机#3', status: 'stopped', running_hours: 10200, params: [{ name: '电流', value: 0, unit: 'A' }, { name: '风压', value: 0, unit: 'MPa' }] },
  { id: 4, name: '提升泵#1', status: 'running', running_hours: 8500, params: [{ name: '流量', value: 650, unit: 'm³/h' }, { name: '扬程', value: 12, unit: 'm' }] },
  { id: 5, name: '提升泵#2', status: 'running', running_hours: 7800, params: [{ name: '流量', value: 620, unit: 'm³/h' }, { name: '扬程', value: 11.5, unit: 'm' }] },
  { id: 6, name: '回流泵#1', status: 'maintenance', running_hours: 6500, params: [{ name: '流量', value: 0, unit: 'm³/h' }, { name: '扬程', value: 0, unit: 'm' }] }
])

const getStatusColor = (s: string) => ({ running: 'green', stopped: 'gray', maintenance: 'orange', fault: 'red' }[s] || 'gray')
const getStatusText = (s: string) => ({ running: '运行中', stopped: '已停止', maintenance: '维护中', fault: '故障' }[s] || '未知')

const startEquipment = (eq: any) => { Message.success(`${eq.name} 启动指令已发送`) }
const stopEquipment = (eq: any) => { Message.warning(`${eq.name} 停止指令已发送`) }
</script>

<style scoped>
.equipment-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
@media (max-width: 1200px) { .equipment-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .equipment-grid { grid-template-columns: 1fr; } }

.equipment-card { background: #fff; border: 1px solid #e5e6eb; border-radius: 8px; padding: 16px; transition: all 0.3s; }
.equipment-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.equipment-card.running { border-left: 3px solid #00b42a; }
.equipment-card.stopped { border-left: 3px solid #86909c; }
.equipment-card.maintenance { border-left: 3px solid #ff7d00; }
.equipment-card.fault { border-left: 3px solid #f53f3f; }

.eq-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.eq-name { font-size: 16px; font-weight: 600; color: #1d2129; }

.eq-body { background: #f7f8fa; padding: 12px; border-radius: 6px; margin-bottom: 12px; }
.eq-param { display: flex; justify-content: space-between; margin-bottom: 4px; }
.eq-param:last-child { margin-bottom: 0; }
.param-name { color: #86909c; font-size: 13px; }
.param-value { color: #1d2129; font-weight: 500; }

.eq-footer { display: flex; justify-content: space-between; align-items: center; }
.run-time { font-size: 12px; color: #86909c; }
</style>
