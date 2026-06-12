<template>
  <div class="page-container">
    <div class="page-header">
      <h2>采购管理</h2>
      <p>采购申请 / 采购订单 / 采购跟踪</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="采购申请">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="keyword" placeholder="搜索申请单号" style="width: 240px;" @search="fetchApplicationData" />
            <a-select v-model="status" placeholder="状态" style="width: 120px;" allow-clear>
              <a-option value="pending">待审批</a-option>
              <a-option value="approved">已批准</a-option>
              <a-option value="rejected">已拒绝</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="showApplicationModal = true">
            <template #icon><icon-plus /></template>
            新建采购申请
          </a-button>
        </div>
        
        <a-table :columns="applicationColumns" :data="applications" :loading="loading" :pagination="pagination">
          <template #status="{ record }">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" v-if="record.status === 'pending'" @click="handleEditApplication(record)">编辑</a-button>
              <a-button type="text" size="small" v-if="record.status === 'approved'" @click="handleCreateOrder(record)">创建订单</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="采购订单">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="orderKeyword" placeholder="搜索订单号" style="width: 240px;" @search="fetchOrderData" />
            <a-select v-model="orderStatus" placeholder="状态" style="width: 120px;" allow-clear>
              <a-option value="pending">待采购</a-option>
              <a-option value="ordered">已下单</a-option>
              <a-option value="received">已收货</a-option>
              <a-option value="completed">已完成</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="showOrderModal = true">
            <template #icon><icon-plus /></template>
            新建采购订单
          </a-button>
        </div>
        
        <a-table :columns="orderColumns" :data="orders" :loading="orderLoading" :pagination="orderPagination">
          <template #status="{ record }">
            <a-tag :color="getOrderStatusColor(record.status)">
              {{ getOrderStatusText(record.status) }}
            </a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" v-if="record.status === 'pending'" @click="handleEditOrder(record)">编辑</a-button>
              <a-button type="text" size="small" v-if="record.status === 'ordered'" @click="handleReceive(record)">确认收货</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="采购跟踪">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="trackKeyword" placeholder="搜索订单号" style="width: 240px;" @search="fetchTrackData" />
            <a-select v-model="trackStatus" placeholder="状态" style="width: 120px;" allow-clear>
              <a-option value="all">全部</a-option>
              <a-option value="pending">进行中</a-option>
              <a-option value="completed">已完成</a-option>
            </a-select>
            <a-range-picker v-model="trackDateRange" style="width: 240px;" />
          </a-space>
        </div>
        
        <a-table :columns="trackColumns" :data="tracks" :loading="trackLoading" :pagination="trackPagination">
          <template #progress="{ record }">
            <a-progress :percent="record.progress" />
          </template>
          <template #status="{ record }">
            <a-tag :color="getOrderStatusColor(record.status)">
              {{ getOrderStatusText(record.status) }}
            </a-tag>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 采购申请弹窗 -->
    <a-modal 
      v-model:visible="showApplicationModal" 
      :title="editingApplication ? '编辑采购申请' : '新建采购申请'" 
      @ok="handleSubmitApplication" 
      :ok-loading="submitLoading"
      width="800px"
    >
      <a-form :model="applicationForm" layout="vertical" ref="applicationFormRef">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="申请部门" field="department" required>
              <a-input v-model="applicationForm.department" placeholder="请输入申请部门" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="申请人" field="applicant" required>
              <a-input v-model="applicationForm.applicant" placeholder="请输入申请人" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="申请物资" required>
          <a-table :columns="materialColumns" :data="applicationForm.materials" :pagination="false" size="small">
            <template #operations="{ rowIndex }">
              <a-button type="text" size="small" status="danger" @click="removeApplicationMaterial(rowIndex)">删除</a-button>
            </template>
          </a-table>
          <a-button type="dashed" @click="showMaterialSelectModal = true" style="width: 100%; margin-top: 8px;">
            <template #icon><icon-plus /></template>
            添加物资
          </a-button>
        </a-form-item>
        <a-form-item label="申请原因" field="reason" required>
          <a-textarea v-model="applicationForm.reason" :max-length="500" show-word-limit />
        </a-form-item>
        <a-form-item label="备注" field="remark">
          <a-textarea v-model="applicationForm.remark" :max-length="500" show-word-limit />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 采购订单弹窗 -->
    <a-modal 
      v-model:visible="showOrderModal" 
      :title="editingOrder ? '编辑采购订单' : '新建采购订单'" 
      @ok="handleSubmitOrder" 
      :ok-loading="submitLoading"
      width="800px"
    >
      <a-form :model="orderForm" layout="vertical" ref="orderFormRef">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="供应商" field="supplier_id" required>
              <a-select v-model="orderForm.supplier_id" placeholder="请选择供应商">
                <a-option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">{{ supplier.name }}</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="订单日期" field="order_date" required>
              <a-date-picker v-model="orderForm.order_date" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="预计到货日期" field="expected_date">
              <a-date-picker v-model="orderForm.expected_date" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="订单金额" field="total_amount">
              <a-input-number v-model="orderForm.total_amount" :min="0" :precision="2" style="width: 100%;" disabled />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="采购物资" required>
          <a-table :columns="materialColumns" :data="orderForm.materials" :pagination="false" size="small">
            <template #operations="{ rowIndex }">
              <a-button type="text" size="small" status="danger" @click="removeOrderMaterial(rowIndex)">删除</a-button>
            </template>
          </a-table>
          <a-button type="dashed" @click="showMaterialSelectModal = true" style="width: 100%; margin-top: 8px;">
            <template #icon><icon-plus /></template>
            添加物资
          </a-button>
        </a-form-item>
        <a-form-item label="备注" field="remark">
          <a-textarea v-model="orderForm.remark" :max-length="500" show-word-limit />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 物资选择弹窗 -->
    <a-modal v-model:visible="showMaterialSelectModal" title="选择物资" width="600px" @ok="handleAddMaterial">
      <a-table 
        :columns="selectMaterialColumns" 
        :data="materials" 
        :pagination="false"
        :row-selection="materialRowSelection"
      />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const orderLoading = ref(false)
const trackLoading = ref(false)
const submitLoading = ref(false)
const showApplicationModal = ref(false)
const showOrderModal = ref(false)
const showMaterialSelectModal = ref(false)
const editingApplication = ref<any>(null)
const editingOrder = ref<any>(null)
const keyword = ref('')
const orderKeyword = ref('')
const trackKeyword = ref('')
const status = ref('')
const orderStatus = ref('')
const trackStatus = ref('')
const trackDateRange = ref([])
const applications = ref<any[]>([])
const orders = ref<any[]>([])
const tracks = ref<any[]>([])
const materials = ref<any[]>([])
const suppliers = ref<any[]>([])
const selectedMaterials = ref<any[]>([])
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })
const orderPagination = reactive({ current: 1, pageSize: 10, total: 0 })
const trackPagination = reactive({ current: 1, pageSize: 10, total: 0 })

const applicationForm = reactive({
  department: '',
  applicant: '',
  materials: [] as any[],
  reason: '',
  remark: ''
})

const orderForm = reactive({
  supplier_id: null,
  order_date: '',
  expected_date: '',
  total_amount: 0,
  materials: [] as any[],
  remark: ''
})

const applicationFormRef = ref()
const orderFormRef = ref()

const applicationColumns = [
  { title: '申请单号', dataIndex: 'application_no', width: 140 },
  { title: '申请部门', dataIndex: 'department', width: 120 },
  { title: '申请人', dataIndex: 'applicant', width: 100 },
  { title: '申请日期', dataIndex: 'application_date', width: 120 },
  { title: '物资种类', dataIndex: 'material_count', width: 100 },
  { title: '预计金额', dataIndex: 'estimated_amount', width: 100 },
  { title: '状态', slotName: 'status', width: 90 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const orderColumns = [
  { title: '订单号', dataIndex: 'order_no', width: 140 },
  { title: '供应商', dataIndex: 'supplier_name', width: 150 },
  { title: '订单日期', dataIndex: 'order_date', width: 120 },
  { title: '预计到货日期', dataIndex: 'expected_date', width: 120 },
  { title: '订单金额', dataIndex: 'total_amount', width: 100 },
  { title: '物资种类', dataIndex: 'material_count', width: 100 },
  { title: '状态', slotName: 'status', width: 90 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const trackColumns = [
  { title: '订单号', dataIndex: 'order_no', width: 140 },
  { title: '供应商', dataIndex: 'supplier_name', width: 150 },
  { title: '订单日期', dataIndex: 'order_date', width: 120 },
  { title: '预计到货日期', dataIndex: 'expected_date', width: 120 },
  { title: '进度', slotName: 'progress', width: 200 },
  { title: '状态', slotName: 'status', width: 90 }
]

const materialColumns = [
  { title: '物资编码', dataIndex: 'code', width: 120 },
  { title: '物资名称', dataIndex: 'name' },
  { title: '单位', dataIndex: 'unit', width: 80 },
  { title: '数量', dataIndex: 'quantity', width: 100 },
  { title: '单价', dataIndex: 'price', width: 100 },
  { title: '金额', dataIndex: 'amount', width: 100 },
  { title: '操作', slotName: 'operations', width: 80 }
]

const selectMaterialColumns = [
  { title: '物资编码', dataIndex: 'code', width: 120 },
  { title: '物资名称', dataIndex: 'name' },
  { title: '单位', dataIndex: 'unit', width: 80 },
  { title: '当前库存', dataIndex: 'current_stock', width: 100 }
]

const materialRowSelection = reactive({
  type: 'checkbox',
  selectedRowKeys: [],
  onSelect: (row: any, selected: boolean) => {
    if (selected) {
      selectedMaterials.value.push(row)
    } else {
      selectedMaterials.value = selectedMaterials.value.filter(r => r.id !== row.id)
    }
  }
})

const getStatusColor = (status: string) => {
  const map: Record<string, string> = {
    pending: 'orange',
    approved: 'green',
    rejected: 'red'
  }
  return map[status] || 'gray'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝'
  }
  return map[status] || '未知'
}

const getOrderStatusColor = (status: string) => {
  const map: Record<string, string> = {
    pending: 'orange',
    ordered: 'blue',
    received: 'cyan',
    completed: 'green'
  }
  return map[status] || 'gray'
}

const getOrderStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待采购',
    ordered: '已下单',
    received: '已收货',
    completed: '已完成'
  }
  return map[status] || '未知'
}

const fetchApplicationData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    applications.value = [
      { id: 1, application_no: 'PA20240115001', department: '生产部', applicant: '张三', application_date: '2024-01-15', material_count: 3, estimated_amount: 15000.00, status: 'approved' },
      { id: 2, application_no: 'PA20240116001', department: '维修部', applicant: '李四', application_date: '2024-01-16', material_count: 2, estimated_amount: 8500.00, status: 'pending' }
    ]
    pagination.total = applications.value.length
  } finally {
    loading.value = false
  }
}

const fetchOrderData = async () => {
  orderLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    orders.value = [
      { id: 1, order_no: 'PO20240115001', supplier_id: 1, supplier_name: 'XX设备公司', order_date: '2024-01-15', expected_date: '2024-01-20', total_amount: 15000.00, material_count: 3, status: 'ordered' },
      { id: 2, order_no: 'PO20240116001', supplier_id: 2, supplier_name: 'YY配件公司', order_date: '2024-01-16', expected_date: '2024-01-22', total_amount: 8500.00, material_count: 2, status: 'pending' }
    ]
    orderPagination.total = orders.value.length
  } finally {
    orderLoading.value = false
  }
}

const fetchTrackData = async () => {
  trackLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    tracks.value = [
      { id: 1, order_no: 'PO20240115001', supplier_name: 'XX设备公司', order_date: '2024-01-15', expected_date: '2024-01-20', progress: 60, status: 'ordered' },
      { id: 2, order_no: 'PO20240114001', supplier_name: 'ZZ化工公司', order_date: '2024-01-14', expected_date: '2024-01-18', progress: 100, status: 'completed' }
    ]
    trackPagination.total = tracks.value.length
  } finally {
    trackLoading.value = false
  }
}

const fetchMaterials = async () => {
  materials.value = [
    { id: 1, code: 'MAT001', name: '潜水泵', unit: '台', current_stock: 5 },
    { id: 2, code: 'MAT002', name: '曝气头', unit: '个', current_stock: 1 },
    { id: 3, code: 'MAT003', name: '聚合氯化铝', unit: 'kg', current_stock: 0 }
  ]
}

const fetchSuppliers = async () => {
  suppliers.value = [
    { id: 1, name: 'XX设备公司' },
    { id: 2, name: 'YY配件公司' },
    { id: 3, name: 'ZZ化工公司' }
  ]
}

const handleSubmitApplication = async () => {
  const valid = await applicationFormRef.value?.validate()
  if (!valid) return
  
  submitLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    Message.success('创建成功')
    showApplicationModal.value = false
    fetchApplicationData()
  } catch (e) {
    Message.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleSubmitOrder = async () => {
  const valid = await orderFormRef.value?.validate()
  if (!valid) return
  
  submitLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    Message.success('创建成功')
    showOrderModal.value = false
    fetchOrderData()
  } catch (e) {
    Message.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleAddMaterial = () => {
  const targetForm = showApplicationModal.value ? applicationForm : orderForm
  selectedMaterials.value.forEach(material => {
    targetForm.materials.push({
      id: material.id,
      code: material.code,
      name: material.name,
      unit: material.unit,
      quantity: 1,
      price: 0,
      amount: 0
    })
  })
  selectedMaterials.value = []
  showMaterialSelectModal.value = false
}

const removeApplicationMaterial = (index: number) => {
  applicationForm.materials.splice(index, 1)
}

const removeOrderMaterial = (index: number) => {
  orderForm.materials.splice(index, 1)
}

const handleViewApplication = (record: any) => {
  Message.info(`查看申请: ${record.application_no}`)
}

const handleEditApplication = (record: any) => {
  editingApplication.value = record
  showApplicationModal.value = true
}

const handleCreateOrder = (record: any) => {
  Message.info(`创建订单: ${record.application_no}`)
  showOrderModal.value = true
}

const handleViewOrder = (record: any) => {
  Message.info(`查看订单: ${record.order_no}`)
}

const handleEditOrder = (record: any) => {
  editingOrder.value = record
  showOrderModal.value = true
}

const handleReceive = (record: any) => {
  Message.success(`确认收货: ${record.order_no}`)
  record.status = 'received'
}

onMounted(() => {
  fetchApplicationData()
  fetchOrderData()
  fetchTrackData()
  fetchMaterials()
  fetchSuppliers()
})
</script>

<style scoped>
.table-operations {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}
</style>
