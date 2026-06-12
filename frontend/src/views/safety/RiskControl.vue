<template>
  <div class="page-container">
    <div class="page-header">
      <h2>风险管控</h2>
      <p>风险点台账 / 风险评估 / 隐患整改</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="风险点台账">
        <div class="table-operations">
          <a-space>
            <a-select v-model="riskLevel" placeholder="风险等级" style="width: 120px;" allow-clear>
              <a-option value="high">高风险</a-option>
              <a-option value="medium">中风险</a-option>
              <a-option value="low">低风险</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="showAddModal = true">
            <template #icon><icon-plus /></template>
            新增风险点
          </a-button>
        </div>
        <a-table :columns="columns" :data="risks" :loading="loading">
          <template #risk_level="{ record }">
            <a-tag :color="getLevelColor(record.risk_level)">{{ getLevelText(record.risk_level) }}</a-tag>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="风险评估">
        <a-card title="风险矩阵">
          <div class="risk-matrix">
            <div class="matrix-row" v-for="i in 5" :key="i">
              <div class="matrix-cell" v-for="j in 5" :key="j" :class="getCellClass(i, j)">
                {{ getCellCount(i, j) }}
              </div>
            </div>
          </div>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="隐患整改">
        <a-table :columns="hazardColumns" :data="hazards">
          <template #status="{ record }">
            <a-tag :color="record.status === 'completed' ? 'green' : 'orange'">
              {{ record.status === 'completed' ? '已整改' : '整改中' }}
            </a-tag>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>
    
    <a-modal v-model:visible="showAddModal" title="新增风险点" @ok="handleAdd">
      <a-form :model="form" layout="vertical">
        <a-form-item label="风险点名称" required>
          <a-input v-model="form.name" />
        </a-form-item>
        <a-form-item label="位置">
          <a-input v-model="form.location" />
        </a-form-item>
        <a-form-item label="风险等级">
          <a-select v-model="form.risk_level">
            <a-option value="high">高风险</a-option>
            <a-option value="medium">中风险</a-option>
            <a-option value="low">低风险</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="管控措施">
          <a-textarea v-model="form.control_measures" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const loading = ref(false)
const showAddModal = ref(false)
const riskLevel = ref('')
const form = reactive({ name: '', location: '', risk_level: 'medium', control_measures: '' })

const columns = [
  { title: '风险点编号', dataIndex: 'code' },
  { title: '风险点名称', dataIndex: 'name' },
  { title: '位置', dataIndex: 'location' },
  { title: '风险类型', dataIndex: 'risk_type' },
  { title: '风险等级', slotName: 'risk_level' },
  { title: '责任人', dataIndex: 'responsible_person' }
]

const hazardColumns = [
  { title: '隐患编号', dataIndex: 'code' },
  { title: '隐患描述', dataIndex: 'description' },
  { title: '整改措施', dataIndex: 'measures' },
  { title: '责任人', dataIndex: 'responsible' },
  { title: '截止日期', dataIndex: 'deadline' },
  { title: '状态', slotName: 'status' }
]

const risks = ref([
  { code: 'RP001', name: '高压配电室', location: '动力车间', risk_type: '设备风险', risk_level: 'high', responsible_person: '张三' },
  { code: 'RP002', name: '污泥脱水间', location: '污泥车间', risk_type: '环境风险', risk_level: 'medium', responsible_person: '李四' },
  { code: 'RP003', name: '加药间', location: '化学车间', risk_type: '操作风险', risk_level: 'medium', responsible_person: '王五' }
])

const hazards = ref([
  { code: 'HZ001', description: '灭火器过期', measures: '更换新灭火器', responsible: '张三', deadline: '2024-01-20', status: 'pending' },
  { code: 'HZ002', description: '安全标识缺失', measures: '补充安全标识', responsible: '李四', deadline: '2024-01-18', status: 'completed' }
])

const getLevelColor = (level: string) => ({ high: 'red', medium: 'orange', low: 'green' }[level] || 'gray')
const getLevelText = (level: string) => ({ high: '高风险', medium: '中风险', low: '低风险' }[level] || '未知')
const getCellClass = (i: number, j: number) => {
  const score = i * j
  if (score >= 15) return 'high'
  if (score >= 8) return 'medium'
  return 'low'
}
const getCellCount = (i: number, j: number) => Math.floor(Math.random() * 3)
const handleAdd = () => { showAddModal.value = false }
</script>

<style scoped>
.table-operations { display: flex; justify-content: space-between; margin-bottom: 16px; }
.risk-matrix { display: flex; flex-direction: column; gap: 4px; width: fit-content; margin: 0 auto; }
.matrix-row { display: flex; gap: 4px; }
.matrix-cell { width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-weight: 600; color: #fff; }
.matrix-cell.high { background: #f53f3f; }
.matrix-cell.medium { background: #ff7d00; }
.matrix-cell.low { background: #00b42a; }
</style>
