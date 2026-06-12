<template>
  <div class="page-container">
    <div class="page-header">
      <h2>生产计划调度</h2>
      <p>生产计划制定 / 工况模式管理 / 资源调度</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="生产计划制定">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="searchKeyword" placeholder="搜索计划" style="width: 240px;" />
            <a-select v-model="searchStatus" placeholder="状态筛选" style="width: 120px;" allow-clear>
              <a-option value="pending">待执行</a-option>
              <a-option value="executing">执行中</a-option>
              <a-option value="completed">已完成</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="showAddModal = true">
            <template #icon><icon-plus /></template>
            新建计划
          </a-button>
        </div>
        
        <a-table :columns="planColumns" :data="plans" :loading="loading" :pagination="pagination">
          <template #status="{ record }">
            <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" v-if="record.status === 'pending'" @click="editPlan(record)">编辑</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="工况模式管理">
        <div class="mode-cards">
          <div class="mode-card" v-for="mode in operationModes" :key="mode.id" :class="{ active: mode.active }">
            <div class="mode-header">
              <span class="mode-name">{{ mode.name }}</span>
              <a-switch v-model="mode.active" />
            </div>
            <div class="mode-desc">{{ mode.description }}</div>
            <div class="mode-params">
              <div v-for="param in mode.params" :key="param.name">
                <span class="param-label">{{ param.name }}:</span>
                <span class="param-value">{{ param.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="资源调度">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-card title="人员调度">
              <a-table :columns="staffColumns" :data="staffData" :pagination="false" size="small" />
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card title="设备调度">
              <a-table :columns="equipmentColumns" :data="equipmentData" :pagination="false" size="small" />
            </a-card>
          </a-col>
        </a-row>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 新建计划弹窗 -->
    <a-modal v-model:visible="showAddModal" :title="editingPlan ? '编辑生产计划' : '新建生产计划'" @ok="handleAddPlan" :ok-loading="submitLoading">
      <a-form :model="planForm" layout="vertical">
        <a-form-item label="计划日期" required>
          <a-date-picker v-model="planForm.plan_date" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="目标处理量 (m³)">
          <a-input-number v-model="planForm.target_volume" :min="0" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="工况模式">
          <a-select v-model="planForm.operation_mode">
            <a-option value="normal">正常模式</a-option>
            <a-option value="peak">高峰模式</a-option>
            <a-option value="low">低负荷模式</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="备注说明">
          <a-textarea v-model="planForm.description" :max-length="500" show-word-limit />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { productionApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const showAddModal = ref(false)
const editingPlan = ref<any>(null)
const searchKeyword = ref('')
const searchStatus = ref('')
const plans = ref<any[]>([])
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const planForm = reactive({
  plan_date: '',
  target_volume: 15000,
  operation_mode: 'normal',
  description: ''
})

const planColumns = [
  { title: '计划编号', dataIndex: 'plan_no' },
  { title: '计划日期', dataIndex: 'plan_date' },
  { title: '目标处理量', dataIndex: 'target_volume' },
  { title: '实际处理量', dataIndex: 'actual_volume' },
  { title: '工况模式', dataIndex: 'operation_mode' },
  { title: '状态', slotName: 'status' },
  { title: '操作', slotName: 'operations', width: 120 }
]

const operationModes = ref([
  { 
    id: 1, 
    name: '正常模式', 
    active: true, 
    description: '适用于日常运行，各工艺段按标准参数运行',
    params: [{ name: '曝气量', value: '80%' }, { name: '回流比', value: '100%' }]
  },
  { 
    id: 2, 
    name: '高峰模式', 
    active: false, 
    description: '适用于进水量高峰期，提高处理能力',
    params: [{ name: '曝气量', value: '100%' }, { name: '回流比', value: '120%' }]
  },
  { 
    id: 3, 
    name: '低负荷模式', 
    active: false, 
    description: '适用于进水量较低时，节能运行',
    params: [{ name: '曝气量', value: '60%' }, { name: '回流比', value: '80%' }]
  },
  { 
    id: 4, 
    name: '雨季模式', 
    active: false, 
    description: '适用于雨季进水稀释时的运行',
    params: [{ name: '曝气量', value: '70%' }, { name: '回流比', value: '90%' }]
  }
])

const staffColumns = [
  { title: '班组', dataIndex: 'team' },
  { title: '班次', dataIndex: 'shift' },
  { title: '人员', dataIndex: 'staff' },
  { title: '状态', dataIndex: 'status' }
]

const staffData = ref([
  { team: '甲班', shift: '早班 (08:00-16:00)', staff: '张三、李四、王五', status: '在岗' },
  { team: '乙班', shift: '中班 (16:00-00:00)', staff: '赵六、钱七、孙八', status: '待班' },
  { team: '丙班', shift: '夜班 (00:00-08:00)', staff: '周九、吴十、郑十一', status: '休息' }
])

const equipmentColumns = [
  { title: '设备', dataIndex: 'name' },
  { title: '数量', dataIndex: 'count' },
  { title: '在用', dataIndex: 'inUse' },
  { title: '备用', dataIndex: 'backup' }
]

const equipmentData = ref([
  { name: '曝气风机', count: 6, inUse: 4, backup: 2 },
  { name: '提升泵', count: 4, inUse: 3, backup: 1 },
  { name: '回流泵', count: 3, inUse: 2, backup: 1 },
  { name: '污泥泵', count: 2, inUse: 1, backup: 1 }
])

const getStatusColor = (status: string) => {
  const map: Record<string, string> = { pending: 'blue', executing: 'orange', completed: 'green' }
  return map[status] || 'gray'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = { pending: '待执行', executing: '执行中', completed: '已完成' }
  return map[status] || '未知'
}

const fetchPlans = async () => {
  loading.value = true
  try {
    const res: any = await productionApi.getPlans({ page: pagination.current, page_size: pagination.pageSize, status: searchStatus.value || undefined })
    plans.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    plans.value = [
      { plan_no: 'PP20240115001', plan_date: '2024-01-15', target_volume: 15000, actual_volume: 14800, operation_mode: '正常模式', status: 'completed' },
      { plan_no: 'PP20240116001', plan_date: '2024-01-16', target_volume: 15000, actual_volume: 12500, operation_mode: '正常模式', status: 'executing' },
      { plan_no: 'PP20240117001', plan_date: '2024-01-17', target_volume: 16000, actual_volume: null, operation_mode: '高峰模式', status: 'pending' }
    ]
  } finally {
    loading.value = false
  }
}

const handleAddPlan = async () => {
  submitLoading.value = true
  try {
    if (editingPlan.value) {
      const index = plans.value.findIndex(p => p.plan_no === editingPlan.value.plan_no)
      if (index > -1) {
        Object.assign(plans.value[index], {
          plan_date: planForm.plan_date,
          target_volume: planForm.target_volume,
          operation_mode: planForm.operation_mode === 'normal' ? '正常模式' : planForm.operation_mode === 'peak' ? '高峰模式' : '低负荷模式',
          description: planForm.description
        })
      }
      Message.success('编辑成功')
    } else {
      await productionApi.createPlan(planForm)
      Message.success('创建成功')
      fetchPlans()
    }
    showAddModal.value = false
    editingPlan.value = null
  } catch (e) {
    if (!editingPlan.value) {
      Message.error('创建失败')
    }
  } finally {
    submitLoading.value = false
  }
}

const editPlan = (record: any) => {
  editingPlan.value = record
  Object.assign(planForm, {
    plan_date: record.plan_date,
    target_volume: record.target_volume,
    operation_mode: record.operation_mode === '正常模式' ? 'normal' : record.operation_mode === '高峰模式' ? 'peak' : 'low',
    description: record.description || ''
  })
  showAddModal.value = true
}

const viewPlan = (record: any) => {
  Message.info(`查看计划: ${record.plan_no}`)
}

onMounted(() => {
  fetchPlans()
})
</script>

<style scoped>
.table-operations {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.mode-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 768px) {
  .mode-cards {
    grid-template-columns: 1fr;
  }
}

.mode-card {
  background: #fff;
  border: 2px solid #e5e6eb;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s;
}

.mode-card.active {
  border-color: #165DFF;
  background: #f0f5ff;
}

.mode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.mode-name {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.mode-desc {
  font-size: 14px;
  color: #86909c;
  margin-bottom: 12px;
}

.mode-params {
  background: #f7f8fa;
  padding: 12px;
  border-radius: 6px;
}

.mode-params .param-label {
  color: #86909c;
}

.mode-params .param-value {
  color: #1d2129;
  font-weight: 500;
  margin-left: 4px;
}
</style>
