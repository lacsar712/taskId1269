<template>
  <div class="page-container">
    <div class="page-header">
      <h2>供应商管理</h2>
      <p>供应商台账 / 评价 / 合格名录</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="供应商台账">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="keyword" placeholder="搜索供应商名称/编码" style="width: 240px;" @search="fetchData" />
            <a-select v-model="status" placeholder="状态" style="width: 120px;" allow-clear>
              <a-option value="active">启用</a-option>
              <a-option value="inactive">停用</a-option>
            </a-select>
            <a-select v-model="qualification" placeholder="资质状态" style="width: 120px;" allow-clear>
              <a-option value="qualified">合格</a-option>
              <a-option value="unqualified">不合格</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="handleAdd">
            <template #icon><icon-plus /></template>
            新增供应商
          </a-button>
        </div>
        
        <a-table :columns="columns" :data="suppliers" :loading="loading" :pagination="pagination">
          <template #status="{ record }">
            <a-tag :color="record.status === 'active' ? 'green' : 'gray'">
              {{ record.status === 'active' ? '启用' : '停用' }}
            </a-tag>
          </template>
          <template #qualification_status="{ record }">
            <a-tag :color="record.qualification_status === 'qualified' ? 'green' : 'red'">
              {{ record.qualification_status === 'qualified' ? '合格' : '不合格' }}
            </a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" @click="handleEdit(record)">编辑</a-button>
              <a-button type="text" size="small" @click="handleViewDetail(record)">详情</a-button>
              <a-button type="text" size="small" @click="handleEvaluate(record)">评价</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="供应商评价">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="evaluateKeyword" placeholder="搜索供应商名称" style="width: 240px;" @search="fetchEvaluateData" />
            <a-select v-model="evaluateStatus" placeholder="评价等级" style="width: 120px;" allow-clear>
              <a-option value="excellent">优秀</a-option>
              <a-option value="good">良好</a-option>
              <a-option value="average">一般</a-option>
              <a-option value="poor">较差</a-option>
            </a-select>
          </a-space>
        </div>
        
        <a-table :columns="evaluateColumns" :data="evaluates" :loading="evaluateLoading" :pagination="evaluatePagination">
          <template #rating="{ record }">
            <a-rate :model-value="record.rating" readonly />
          </template>
          <template #level="{ record }">
            <a-tag :color="getLevelColor(record.level)">
              {{ getLevelText(record.level) }}
            </a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" @click="handleEditEvaluate(record)">编辑评价</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="合格名录">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="qualifiedKeyword" placeholder="搜索供应商名称" style="width: 240px;" @search="fetchQualifiedData" />
            <a-select v-model="qualifiedCategory" placeholder="供应类别" style="width: 140px;" allow-clear>
              <a-option value="equipment">设备</a-option>
              <a-option value="parts">配件</a-option>
              <a-option value="chemical">药剂</a-option>
            </a-select>
          </a-space>
        </div>
        
        <a-table :columns="qualifiedColumns" :data="qualifiedSuppliers" :loading="qualifiedLoading" :pagination="qualifiedPagination">
          <template #rating="{ record }">
            <a-rate :model-value="record.rating" readonly />
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" @click="handleViewDetail(record)">查看详情</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 新增/编辑供应商弹窗 -->
    <a-modal 
      v-model:visible="showModal" 
      :title="editing ? '编辑供应商' : '新增供应商'" 
      @ok="handleSubmit" 
      :ok-loading="submitLoading"
      width="700px"
    >
      <a-form :model="form" layout="vertical" ref="formRef">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="供应商编码" field="code" required>
              <a-input v-model="form.code" placeholder="请输入供应商编码" :disabled="!!editing" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="供应商名称" field="name" required>
              <a-input v-model="form.name" placeholder="请输入供应商名称" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="联系人" field="contact_person" required>
              <a-input v-model="form.contact_person" placeholder="请输入联系人" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="联系电话" field="contact_phone" required>
              <a-input v-model="form.contact_phone" placeholder="请输入联系电话" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="联系地址" field="address">
          <a-input v-model="form.address" placeholder="请输入联系地址" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="供应类别" field="category">
              <a-select v-model="form.category" placeholder="请选择供应类别" multiple>
                <a-option value="equipment">设备</a-option>
                <a-option value="parts">配件</a-option>
                <a-option value="chemical">药剂</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="资质状态" field="qualification_status">
              <a-select v-model="form.qualification_status">
                <a-option value="qualified">合格</a-option>
                <a-option value="unqualified">不合格</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="备注" field="remark">
          <a-textarea v-model="form.remark" :max-length="500" show-word-limit />
        </a-form-item>
        <a-form-item label="状态" field="status">
          <a-radio-group v-model="form.status">
            <a-radio value="active">启用</a-radio>
            <a-radio value="inactive">停用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 评价弹窗 -->
    <a-modal 
      v-model:visible="showEvaluateModal" 
      :title="editingEvaluate ? '编辑评价' : '新增评价'" 
      @ok="handleSubmitEvaluate" 
      :ok-loading="submitLoading"
      width="600px"
    >
      <a-form :model="evaluateForm" layout="vertical" ref="evaluateFormRef">
        <a-form-item label="供应商" required>
          <a-input v-model="evaluateForm.supplier_name" disabled />
        </a-form-item>
        <a-form-item label="评价等级" field="level" required>
          <a-select v-model="evaluateForm.level">
            <a-option value="excellent">优秀</a-option>
            <a-option value="good">良好</a-option>
            <a-option value="average">一般</a-option>
            <a-option value="poor">较差</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="评分" field="rating" required>
          <a-rate v-model="evaluateForm.rating" />
        </a-form-item>
        <a-form-item label="评价内容" field="content" required>
          <a-textarea v-model="evaluateForm.content" :max-length="500" show-word-limit />
        </a-form-item>
        <a-form-item label="评价日期" field="evaluate_date" required>
          <a-date-picker v-model="evaluateForm.evaluate_date" style="width: 100%;" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 详情抽屉 -->
    <a-drawer v-model:visible="showDetailDrawer" title="供应商详情" :width="600">
      <a-descriptions :column="2" bordered v-if="currentSupplier">
        <a-descriptions-item label="供应商编码">{{ currentSupplier.code }}</a-descriptions-item>
        <a-descriptions-item label="供应商名称">{{ currentSupplier.name }}</a-descriptions-item>
        <a-descriptions-item label="联系人">{{ currentSupplier.contact_person }}</a-descriptions-item>
        <a-descriptions-item label="联系电话">{{ currentSupplier.contact_phone }}</a-descriptions-item>
        <a-descriptions-item label="联系地址" :span="2">{{ currentSupplier.address || '-' }}</a-descriptions-item>
        <a-descriptions-item label="供应类别">{{ currentSupplier.category || '-' }}</a-descriptions-item>
        <a-descriptions-item label="资质状态">
          <a-tag :color="currentSupplier.qualification_status === 'qualified' ? 'green' : 'red'">
            {{ currentSupplier.qualification_status === 'qualified' ? '合格' : '不合格' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="currentSupplier.status === 'active' ? 'green' : 'gray'">
            {{ currentSupplier.status === 'active' ? '启用' : '停用' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="备注" :span="2">{{ currentSupplier.remark || '-' }}</a-descriptions-item>
      </a-descriptions>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const evaluateLoading = ref(false)
const qualifiedLoading = ref(false)
const submitLoading = ref(false)
const showModal = ref(false)
const showEvaluateModal = ref(false)
const showDetailDrawer = ref(false)
const editing = ref<any>(null)
const editingEvaluate = ref<any>(null)
const keyword = ref('')
const evaluateKeyword = ref('')
const qualifiedKeyword = ref('')
const status = ref('')
const evaluateStatus = ref('')
const qualification = ref('')
const qualifiedCategory = ref('')
const suppliers = ref<any[]>([])
const evaluates = ref<any[]>([])
const qualifiedSuppliers = ref<any[]>([])
const currentSupplier = ref<any>(null)
const formRef = ref()
const evaluateFormRef = ref()
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })
const evaluatePagination = reactive({ current: 1, pageSize: 10, total: 0 })
const qualifiedPagination = reactive({ current: 1, pageSize: 10, total: 0 })

const form = reactive({
  code: '',
  name: '',
  contact_person: '',
  contact_phone: '',
  address: '',
  category: [],
  qualification_status: 'qualified',
  remark: '',
  status: 'active'
})

const evaluateForm = reactive({
  supplier_id: null,
  supplier_name: '',
  level: 'good',
  rating: 4,
  content: '',
  evaluate_date: ''
})

const columns = [
  { title: '供应商编码', dataIndex: 'code', width: 120 },
  { title: '供应商名称', dataIndex: 'name' },
  { title: '联系人', dataIndex: 'contact_person', width: 100 },
  { title: '联系电话', dataIndex: 'contact_phone', width: 120 },
  { title: '供应类别', dataIndex: 'category', width: 120 },
  { title: '资质状态', slotName: 'qualification_status', width: 100 },
  { title: '状态', slotName: 'status', width: 90 },
  { title: '操作', slotName: 'operations', width: 280 }
]

const evaluateColumns = [
  { title: '供应商名称', dataIndex: 'supplier_name' },
  { title: '评价等级', slotName: 'level', width: 100 },
  { title: '评分', slotName: 'rating', width: 150 },
  { title: '评价日期', dataIndex: 'evaluate_date', width: 120 },
  { title: '评价人', dataIndex: 'evaluator', width: 100 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const qualifiedColumns = [
  { title: '供应商编码', dataIndex: 'code', width: 120 },
  { title: '供应商名称', dataIndex: 'name' },
  { title: '供应类别', dataIndex: 'category', width: 120 },
  { title: '评分', slotName: 'rating', width: 150 },
  { title: '加入时间', dataIndex: 'join_date', width: 120 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const getLevelColor = (level: string) => {
  const map: Record<string, string> = {
    excellent: 'green',
    good: 'blue',
    average: 'orange',
    poor: 'red'
  }
  return map[level] || 'gray'
}

const getLevelText = (level: string) => {
  const map: Record<string, string> = {
    excellent: '优秀',
    good: '良好',
    average: '一般',
    poor: '较差'
  }
  return map[level] || '未知'
}

const fetchData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    suppliers.value = [
      { id: 1, code: 'SUP001', name: 'XX设备公司', contact_person: '张经理', contact_phone: '13800138001', address: 'XX市XX区XX路', category: '设备,配件', qualification_status: 'qualified', status: 'active' },
      { id: 2, code: 'SUP002', name: 'YY配件公司', contact_person: '李经理', contact_phone: '13800138002', address: 'YY市YY区YY路', category: '配件', qualification_status: 'qualified', status: 'active' },
      { id: 3, code: 'SUP003', name: 'ZZ化工公司', contact_person: '王经理', contact_phone: '13800138003', address: 'ZZ市ZZ区ZZ路', category: '药剂', qualification_status: 'qualified', status: 'active' }
    ]
    pagination.total = suppliers.value.length
  } finally {
    loading.value = false
  }
}

const fetchEvaluateData = async () => {
  evaluateLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    evaluates.value = [
      { id: 1, supplier_id: 1, supplier_name: 'XX设备公司', level: 'excellent', rating: 5, evaluate_date: '2024-01-15', evaluator: '张三' },
      { id: 2, supplier_id: 2, supplier_name: 'YY配件公司', level: 'good', rating: 4, evaluate_date: '2024-01-14', evaluator: '李四' },
      { id: 3, supplier_id: 3, supplier_name: 'ZZ化工公司', level: 'average', rating: 3, evaluate_date: '2024-01-13', evaluator: '王五' }
    ]
    evaluatePagination.total = evaluates.value.length
  } finally {
    evaluateLoading.value = false
  }
}

const fetchQualifiedData = async () => {
  qualifiedLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    qualifiedSuppliers.value = [
      { id: 1, code: 'SUP001', name: 'XX设备公司', category: '设备,配件', rating: 5, join_date: '2023-01-15' },
      { id: 2, code: 'SUP002', name: 'YY配件公司', category: '配件', rating: 4, join_date: '2023-02-20' },
      { id: 3, code: 'SUP003', name: 'ZZ化工公司', category: '药剂', rating: 3, join_date: '2023-03-10' }
    ]
    qualifiedPagination.total = qualifiedSuppliers.value.length
  } finally {
    qualifiedLoading.value = false
  }
}

const handleAdd = () => {
  editing.value = null
  Object.assign(form, {
    code: '',
    name: '',
    contact_person: '',
    contact_phone: '',
    address: '',
    category: [],
    qualification_status: 'qualified',
    remark: '',
    status: 'active'
  })
  showModal.value = true
}

const handleEdit = (record: any) => {
  editing.value = record
  Object.assign(form, record)
  showModal.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate()
  if (!valid) return
  
  submitLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    Message.success(editing.value ? '更新成功' : '创建成功')
    showModal.value = false
    fetchData()
  } catch (e) {
    Message.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleViewDetail = (record: any) => {
  currentSupplier.value = record
  showDetailDrawer.value = true
}

const handleDelete = (record: any) => {
  Message.info(`删除供应商: ${record.name}`)
}

const handleEvaluate = (record: any) => {
  editingEvaluate.value = null
  Object.assign(evaluateForm, {
    supplier_id: record.id,
    supplier_name: record.name,
    level: 'good',
    rating: 4,
    content: '',
    evaluate_date: ''
  })
  showEvaluateModal.value = true
}

const handleSubmitEvaluate = async () => {
  const valid = await evaluateFormRef.value?.validate()
  if (!valid) return
  
  submitLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    Message.success('评价成功')
    showEvaluateModal.value = false
    fetchEvaluateData()
  } catch (e) {
    Message.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleViewEvaluate = (record: any) => {
  Message.info(`查看评价: ${record.supplier_name}`)
}

const handleEditEvaluate = (record: any) => {
  editingEvaluate.value = record
  Object.assign(evaluateForm, record)
  showEvaluateModal.value = true
}

const handleRemoveQualified = (record: any) => {
  Message.info(`移出名录: ${record.name}`)
}

onMounted(() => {
  fetchData()
  fetchEvaluateData()
  fetchQualifiedData()
})
</script>

<style scoped>
.table-operations {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}
</style>
