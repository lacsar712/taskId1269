<template>
  <div class="page-container">
    <div class="page-header">
      <h2>维护保养</h2>
      <p>保养计划 / 保养工单 / 保养提醒</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="保养计划">
        <a-table :columns="planColumns" :data="maintenancePlans">
          <template #status="{ record }">
            <a-tag :color="record.status === 'active' ? 'green' : 'gray'">{{ record.status === 'active' ? '启用' : '停用' }}</a-tag>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="保养工单">
        <a-table :columns="recordColumns" :data="maintenanceRecords">
          <template #result="{ record }">
            <a-tag :color="record.result === 'completed' ? 'green' : 'blue'">{{ record.result === 'completed' ? '已完成' : '进行中' }}</a-tag>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="保养提醒">
        <a-list :data="reminders" :bordered="false">
          <template #item="{ item }">
            <a-list-item>
              <a-list-item-meta :title="item.equipment_name" :description="item.content">
                <template #avatar>
                  <a-avatar :style="{ background: item.urgent ? '#f53f3f' : '#ff7d00' }">
                    <icon-notification />
                  </a-avatar>
                </template>
              </a-list-item-meta>
              <template #actions>
                <a-tag :color="item.urgent ? 'red' : 'orange'">{{ item.urgent ? '紧急' : '即将到期' }}</a-tag>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const planColumns = [
  { title: '计划编号', dataIndex: 'plan_no' },
  { title: '设备名称', dataIndex: 'equipment_name' },
  { title: '保养类型', dataIndex: 'maintenance_type' },
  { title: '保养频次', dataIndex: 'frequency' },
  { title: '下次保养', dataIndex: 'next_date' },
  { title: '状态', slotName: 'status' }
]

const recordColumns = [
  { title: '工单编号', dataIndex: 'record_no' },
  { title: '设备名称', dataIndex: 'equipment_name' },
  { title: '保养类型', dataIndex: 'maintenance_type' },
  { title: '保养日期', dataIndex: 'maintenance_date' },
  { title: '执行人', dataIndex: 'executor_name' },
  { title: '状态', slotName: 'result' }
]

const maintenancePlans = ref([
  { plan_no: 'MP001', equipment_name: '曝气风机#1', maintenance_type: '日常保养', frequency: '每周', next_date: '2024-01-20', status: 'active' },
  { plan_no: 'MP002', equipment_name: '提升泵#1', maintenance_type: '定期保养', frequency: '每月', next_date: '2024-02-01', status: 'active' }
])

const maintenanceRecords = ref([
  { record_no: 'MR20240115001', equipment_name: '曝气风机#1', maintenance_type: '日常保养', maintenance_date: '2024-01-15', executor_name: '张三', result: 'completed' },
  { record_no: 'MR20240114001', equipment_name: '提升泵#2', maintenance_type: '定期保养', maintenance_date: '2024-01-14', executor_name: '李四', result: 'completed' }
])

const reminders = ref([
  { id: 1, equipment_name: '曝气风机#3', content: '已超期3天未保养', urgent: true },
  { id: 2, equipment_name: '回流泵#1', content: '距下次保养还有2天', urgent: false },
  { id: 3, equipment_name: '刮泥机', content: '距下次保养还有5天', urgent: false }
])
</script>
