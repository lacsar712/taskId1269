<template>
  <div class="page-container">
    <div class="page-header">
      <h2>应急管理</h2>
      <p>应急预案管理 / 应急演练 / 应急处置</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="应急预案">
        <a-table :columns="planColumns" :data="plans">
          <template #plan_level="{ record }">
            <a-tag :color="record.plan_level === '一级' ? 'red' : record.plan_level === '二级' ? 'orange' : 'blue'">
              {{ record.plan_level }}
            </a-tag>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="应急演练">
        <a-timeline>
          <a-timeline-item v-for="drill in drills" :key="drill.id" :dot-color="drill.status === 'completed' ? 'green' : 'blue'">
            <div class="drill-item">
              <div class="drill-title">{{ drill.title }}</div>
              <div class="drill-info">
                <span>{{ drill.date }}</span>
                <a-tag :color="drill.status === 'completed' ? 'green' : 'blue'" size="small">
                  {{ drill.status === 'completed' ? '已完成' : '计划中' }}
                </a-tag>
              </div>
              <div class="drill-desc">{{ drill.description }}</div>
            </div>
          </a-timeline-item>
        </a-timeline>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="应急处置">
        <a-empty description="暂无应急事件" />
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const planColumns = [
  { title: '预案编号', dataIndex: 'plan_no' },
  { title: '预案名称', dataIndex: 'plan_name' },
  { title: '应急类型', dataIndex: 'emergency_type' },
  { title: '预案级别', slotName: 'plan_level' },
  { title: '最近演练', dataIndex: 'drill_date' },
  { title: '操作', slotName: 'operations' }
]

const plans = ref([
  { plan_no: 'EP001', plan_name: '环境污染应急预案', emergency_type: '环境事故', plan_level: '一级', drill_date: '2024-01-10' },
  { plan_no: 'EP002', plan_name: '火灾事故应急预案', emergency_type: '安全事故', plan_level: '一级', drill_date: '2023-12-15' },
  { plan_no: 'EP003', plan_name: '设备故障应急预案', emergency_type: '设备故障', plan_level: '二级', drill_date: '2024-01-05' }
])

const drills = ref([
  { id: 1, title: '2024年度消防演练', date: '2024-01-20', status: 'planned', description: '全厂消防疏散演练' },
  { id: 2, title: '污水溢流应急演练', date: '2024-01-10', status: 'completed', description: '模拟污水溢流情况下的应急处置' },
  { id: 3, title: '化学品泄漏演练', date: '2023-12-25', status: 'completed', description: '加药间化学品泄漏应急处置演练' }
])
</script>

<style scoped>
.drill-item { padding: 12px 0; }
.drill-title { font-size: 16px; font-weight: 600; color: #1d2129; }
.drill-info { display: flex; gap: 12px; align-items: center; margin: 8px 0; font-size: 13px; color: #86909c; }
.drill-desc { font-size: 14px; color: #4e5969; }
</style>
