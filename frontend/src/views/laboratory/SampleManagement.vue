<template>
  <div class="page-container">
    <div class="page-header">
      <h2>样品管理</h2>
      <p>样品登记 / 样品流转 / 样品留存管理</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="样品登记">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="searchKeyword" placeholder="搜索样品编号/名称" style="width: 240px;" @search="fetchData" />
            <a-select v-model="searchStatus" placeholder="状态筛选" style="width: 120px;" allow-clear @change="fetchData">
              <a-option value="registered">已登记</a-option>
              <a-option value="testing">检测中</a-option>
              <a-option value="completed">已完成</a-option>
              <a-option value="archived">已归档</a-option>
            </a-select>
            <a-date-picker v-model="searchDate" placeholder="登记日期" style="width: 180px;" @change="fetchData" />
          </a-space>
          <a-button type="primary" @click="showAddModal = true">
            <template #icon><icon-plus /></template>
            登记样品
          </a-button>
        </div>
        
        <a-table :columns="columns" :data="samples" :loading="loading" :pagination="pagination" @page-change="handlePageChange" @page-size-change="handlePageSizeChange">
          <template #status="{ record }">
            <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" @click="viewSample(record)">详情</a-button>
              <a-button type="text" size="small" @click="editSample(record)" v-if="record.status === 'registered'">编辑</a-button>
              <a-popconfirm content="确定要删除该样品吗？" @ok="deleteSample(record)" v-if="record.status === 'registered'">
                <a-button type="text" size="small" status="danger">删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="样品流转">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="transferKeyword" placeholder="搜索样品编号" style="width: 240px;" />
            <a-select v-model="transferStatus" placeholder="流转状态" style="width: 120px;" allow-clear>
              <a-option value="pending">待流转</a-option>
              <a-option value="in_transit">流转中</a-option>
              <a-option value="received">已接收</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="showTransferModal = true">
            <template #icon><icon-sync /></template>
            发起流转
          </a-button>
        </div>
        
        <a-table :columns="transferColumns" :data="transfers" :loading="transferLoading" :pagination="transferPagination">
          <template #status="{ record }">
            <a-tag :color="getTransferStatusColor(record.status)">{{ getTransferStatusText(record.status) }}</a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" v-if="record.status === 'pending'">确认接收</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="样品留存管理">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="storageKeyword" placeholder="搜索样品编号" style="width: 240px;" />
            <a-select v-model="storageLocation" placeholder="存储位置" style="width: 140px;" allow-clear>
              <a-option value="cold_storage">冷藏库</a-option>
              <a-option value="freezer">冷冻库</a-option>
              <a-option value="room_temp">常温库</a-option>
            </a-select>
          </a-space>
        </div>
        
        <a-table :columns="storageColumns" :data="storages" :loading="storageLoading" :pagination="storagePagination">
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" status="danger" @click="handleDispose(record)">处置</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 登记样品弹窗 -->
    <a-modal v-model:visible="showAddModal" title="登记样品" @ok="handleAdd" :ok-loading="submitLoading" width="700px">
      <a-form :model="form" layout="vertical" ref="formRef">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="样品编号" field="sample_no" required>
              <a-input v-model="form.sample_no" placeholder="自动生成" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="样品名称" field="sample_name" required>
              <a-input v-model="form.sample_name" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="样品类型" field="sample_type" required>
              <a-select v-model="form.sample_type">
                <a-option value="water">水样</a-option>
                <a-option value="sludge">污泥</a-option>
                <a-option value="gas">气体</a-option>
                <a-option value="solid">固体</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="采样日期" field="sampling_date" required>
              <a-date-picker v-model="form.sampling_date" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="采样位置" field="sampling_location">
              <a-input v-model="form.sampling_location" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="采样人" field="sampler">
              <a-input v-model="form.sampler" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="样品描述" field="description">
          <a-textarea v-model="form.description" :max-length="500" show-word-limit />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 样品详情抽屉 -->
    <a-drawer v-model:visible="showDetailDrawer" title="样品详情" :width="600">
      <a-descriptions :column="2" bordered v-if="currentSample">
        <a-descriptions-item label="样品编号">{{ currentSample.sample_no }}</a-descriptions-item>
        <a-descriptions-item label="样品名称">{{ currentSample.sample_name }}</a-descriptions-item>
        <a-descriptions-item label="样品类型">{{ getSampleTypeText(currentSample.sample_type) }}</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="getStatusColor(currentSample.status)">{{ getStatusText(currentSample.status) }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="采样日期">{{ currentSample.sampling_date }}</a-descriptions-item>
        <a-descriptions-item label="登记日期">{{ currentSample.register_date }}</a-descriptions-item>
        <a-descriptions-item label="采样位置">{{ currentSample.sampling_location }}</a-descriptions-item>
        <a-descriptions-item label="采样人">{{ currentSample.sampler }}</a-descriptions-item>
        <a-descriptions-item label="样品描述" :span="2">{{ currentSample.description || '-' }}</a-descriptions-item>
      </a-descriptions>
    </a-drawer>
    
    <!-- 流转弹窗 -->
    <a-modal v-model:visible="showTransferModal" title="发起样品流转" @ok="handleTransfer" :ok-loading="transferSubmitLoading" width="600px">
      <a-form :model="transferForm" layout="vertical">
        <a-form-item label="选择样品" required>
          <a-select v-model="transferForm.sample_id" placeholder="请选择样品">
            <a-option v-for="sample in availableSamples" :key="sample.id" :value="sample.id">
              {{ sample.sample_no }} - {{ sample.sample_name }}
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="流转目标" required>
          <a-select v-model="transferForm.target_department">
            <a-option value="lab_a">实验室A</a-option>
            <a-option value="lab_b">实验室B</a-option>
            <a-option value="external">外部机构</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="流转原因">
          <a-textarea v-model="transferForm.reason" :max-length="200" show-word-limit />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const transferLoading = ref(false)
const storageLoading = ref(false)
const submitLoading = ref(false)
const transferSubmitLoading = ref(false)
const showAddModal = ref(false)
const showDetailDrawer = ref(false)
const showTransferModal = ref(false)
const searchKeyword = ref('')
const searchStatus = ref('')
const searchDate = ref('')
const transferKeyword = ref('')
const transferStatus = ref('')
const storageKeyword = ref('')
const storageLocation = ref('')

const samples = ref<any[]>([])
const transfers = ref<any[]>([])
const storages = ref<any[]>([])
const currentSample = ref<any>(null)
const availableSamples = ref<any[]>([])

const pagination = reactive({ current: 1, pageSize: 10, total: 0 })
const transferPagination = reactive({ current: 1, pageSize: 10, total: 0 })
const storagePagination = reactive({ current: 1, pageSize: 10, total: 0 })

const form = reactive({
  sample_no: '',
  sample_name: '',
  sample_type: '',
  sampling_date: '',
  sampling_location: '',
  sampler: '',
  description: ''
})

const transferForm = reactive({
  sample_id: null,
  target_department: '',
  reason: ''
})

const formRef = ref()

const columns = [
  { title: '样品编号', dataIndex: 'sample_no', width: 140 },
  { title: '样品名称', dataIndex: 'sample_name' },
  { title: '样品类型', dataIndex: 'sample_type', width: 100 },
  { title: '采样日期', dataIndex: 'sampling_date', width: 120 },
  { title: '登记日期', dataIndex: 'register_date', width: 120 },
  { title: '采样位置', dataIndex: 'sampling_location', width: 120 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 180, fixed: 'right' }
]

const transferColumns = [
  { title: '流转单号', dataIndex: 'transfer_no', width: 140 },
  { title: '样品编号', dataIndex: 'sample_no', width: 140 },
  { title: '样品名称', dataIndex: 'sample_name' },
  { title: '流转目标', dataIndex: 'target_department', width: 120 },
  { title: '发起时间', dataIndex: 'transfer_date', width: 160 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const storageColumns = [
  { title: '样品编号', dataIndex: 'sample_no', width: 140 },
  { title: '样品名称', dataIndex: 'sample_name' },
  { title: '存储位置', dataIndex: 'storage_location', width: 120 },
  { title: '存储日期', dataIndex: 'storage_date', width: 120 },
  { title: '预计保存期', dataIndex: 'expiry_date', width: 120 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const getStatusColor = (status: string) => {
  const map: Record<string, string> = {
    registered: 'blue',
    testing: 'orange',
    completed: 'green',
    archived: 'gray'
  }
  return map[status] || 'gray'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    registered: '已登记',
    testing: '检测中',
    completed: '已完成',
    archived: '已归档'
  }
  return map[status] || '未知'
}

const getSampleTypeText = (type: string) => {
  const map: Record<string, string> = {
    water: '水样',
    sludge: '污泥',
    gas: '气体',
    solid: '固体'
  }
  return map[type] || type
}

const getTransferStatusColor = (status: string) => {
  const map: Record<string, string> = {
    pending: 'blue',
    in_transit: 'orange',
    received: 'green'
  }
  return map[status] || 'gray'
}

const getTransferStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待流转',
    in_transit: '流转中',
    received: '已接收'
  }
  return map[status] || '未知'
}

const fetchData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    samples.value = [
      { id: 1, sample_no: 'SP20240204001', sample_name: '进水水样', sample_type: 'water', sampling_date: '2024-02-04', register_date: '2024-02-04', sampling_location: '进水口', sampler: '张三', status: 'registered', description: '日常采样' },
      { id: 2, sample_no: 'SP20240204002', sample_name: '出水水样', sample_type: 'water', sampling_date: '2024-02-04', register_date: '2024-02-04', sampling_location: '出水口', sampler: '李四', status: 'testing', description: '日常采样' },
      { id: 3, sample_no: 'SP20240203001', sample_name: '活性污泥', sample_type: 'sludge', sampling_date: '2024-02-03', register_date: '2024-02-03', sampling_location: '曝气池', sampler: '王五', status: 'completed', description: '定期检测' },
      { id: 4, sample_no: 'SP20240202001', sample_name: '废气样品', sample_type: 'gas', sampling_date: '2024-02-02', register_date: '2024-02-02', sampling_location: '排气口', sampler: '赵六', status: 'archived', description: '环境监测' }
    ]
    pagination.total = samples.value.length
  } finally {
    loading.value = false
  }
}

const fetchTransfers = async () => {
  transferLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    transfers.value = [
      { id: 1, transfer_no: 'TF20240204001', sample_no: 'SP20240203001', sample_name: '活性污泥', target_department: '实验室B', transfer_date: '2024-02-04 10:30', status: 'pending' },
      { id: 2, transfer_no: 'TF20240203001', sample_no: 'SP20240202001', sample_name: '废气样品', target_department: '外部机构', transfer_date: '2024-02-03 14:20', status: 'in_transit' },
      { id: 3, transfer_no: 'TF20240202001', sample_no: 'SP20240201001', sample_name: '进水水样', target_department: '实验室A', transfer_date: '2024-02-02 09:15', status: 'received' }
    ]
    transferPagination.total = transfers.value.length
  } finally {
    transferLoading.value = false
  }
}

const fetchStorages = async () => {
  storageLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    storages.value = [
      { id: 1, sample_no: 'SP20240201001', sample_name: '进水水样', storage_location: 'cold_storage', storage_date: '2024-02-01', expiry_date: '2024-02-08' },
      { id: 2, sample_no: 'SP20240130001', sample_name: '出水水样', storage_location: 'cold_storage', storage_date: '2024-01-30', expiry_date: '2024-02-06' },
      { id: 3, sample_no: 'SP20240125001', sample_name: '活性污泥', storage_location: 'freezer', storage_date: '2024-01-25', expiry_date: '2024-02-24' }
    ]
    storagePagination.total = storages.value.length
  } finally {
    storageLoading.value = false
  }
}

const handlePageChange = (page: number) => {
  pagination.current = page
  fetchData()
}

const handlePageSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.current = 1
  fetchData()
}

const viewSample = (record: any) => {
  currentSample.value = record
  showDetailDrawer.value = true
}

const editSample = (record: any) => {
  Object.assign(form, record)
  showAddModal.value = true
}

const deleteSample = async (record: any) => {
  Message.success('删除成功')
  fetchData()
}

const viewTransfer = (record: any) => {
  Message.info('查看流转详情')
}

const viewStorage = (record: any) => {
  Message.info('查看存储详情')
}

const handleDispose = async (record: any) => {
  Message.success('样品已处置')
  fetchStorages()
}

const handleAdd = async () => {
  if (!form.sample_no) {
    form.sample_no = `SP${new Date().toISOString().slice(0, 10).replace(/-/g, '')}${String(Math.floor(Math.random() * 1000)).padStart(3, '0')}`
  }
  submitLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    Message.success('登记成功')
    showAddModal.value = false
    Object.assign(form, {
      sample_no: '',
      sample_name: '',
      sample_type: '',
      sampling_date: '',
      sampling_location: '',
      sampler: '',
      description: ''
    })
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

const handleTransfer = async () => {
  transferSubmitLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    Message.success('流转发起成功')
    showTransferModal.value = false
    Object.assign(transferForm, {
      sample_id: null,
      target_department: '',
      reason: ''
    })
    fetchTransfers()
  } finally {
    transferSubmitLoading.value = false
  }
}

onMounted(() => {
  fetchData()
  fetchTransfers()
  fetchStorages()
  availableSamples.value = samples.value.filter(s => s.status === 'registered')
})
</script>

<style scoped>
.table-operations {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

@media (max-width: 768px) {
  .table-operations {
    flex-direction: column;
  }
  
  .table-operations > * {
    width: 100%;
  }
}
</style>
