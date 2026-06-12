<template>
  <div class="page-container">
    <div class="page-header">
      <h2>物资台账</h2>
      <p>基础档案 / 分类管理 / 库存上下限</p>
    </div>
    
    <div class="table-operations">
      <a-space>
        <a-input-search v-model="keyword" placeholder="搜索物资名称/编码" style="width: 240px;" @search="fetchData" />
        <a-select v-model="categoryId" placeholder="物资分类" style="width: 140px;" allow-clear>
          <a-option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</a-option>
        </a-select>
        <a-select v-model="status" placeholder="状态" style="width: 120px;" allow-clear>
          <a-option value="active">启用</a-option>
          <a-option value="inactive">停用</a-option>
        </a-select>
      </a-space>
      <a-button type="primary" @click="handleAdd">
        <template #icon><icon-plus /></template>
        新增物资
      </a-button>
    </div>
    
    <a-table :columns="columns" :data="materials" :loading="loading" :pagination="pagination">
      <template #status="{ record }">
        <a-tag :color="record.status === 'active' ? 'green' : 'gray'">
          {{ record.status === 'active' ? '启用' : '停用' }}
        </a-tag>
      </template>
      <template #stock_status="{ record }">
        <a-tag :color="getStockStatusColor(record.stock_status)">
          {{ getStockStatusText(record.stock_status) }}
        </a-tag>
      </template>
      <template #operations="{ record }">
        <a-space>
          <a-button type="text" size="small" @click="handleEdit(record)">编辑</a-button>
          <a-button type="text" size="small" @click="handleViewDetail(record)">详情</a-button>
          <a-popconfirm content="确定要删除该物资吗？" @ok="handleDelete(record)">
            <a-button type="text" size="small" status="danger">删除</a-button>
          </a-popconfirm>
        </a-space>
      </template>
    </a-table>
    
    <!-- 新增/编辑弹窗 -->
    <a-modal 
      v-model:visible="showModal" 
      :title="editing ? '编辑物资' : '新增物资'" 
      @ok="handleSubmit" 
      :ok-loading="submitLoading"
      width="700px"
    >
      <a-form :model="form" layout="vertical" ref="formRef">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="物资编码" field="code" required>
              <a-input v-model="form.code" placeholder="请输入物资编码" :disabled="!!editing" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="物资名称" field="name" required>
              <a-input v-model="form.name" placeholder="请输入物资名称" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="物资分类" field="category_id" required>
              <a-select v-model="form.category_id" placeholder="请选择分类">
                <a-option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="规格型号" field="specification">
              <a-input v-model="form.specification" placeholder="请输入规格型号" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="单位" field="unit" required>
              <a-select v-model="form.unit" placeholder="请选择单位">
                <a-option value="个">个</a-option>
                <a-option value="台">台</a-option>
                <a-option value="套">套</a-option>
                <a-option value="件">件</a-option>
                <a-option value="kg">kg</a-option>
                <a-option value="m">m</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="单价" field="price">
              <a-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="库存上限" field="max_stock">
              <a-input-number v-model="form.max_stock" :min="0" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="库存下限" field="min_stock">
              <a-input-number v-model="form.min_stock" :min="0" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="供应商" field="supplier">
          <a-input v-model="form.supplier" placeholder="请输入供应商" />
        </a-form-item>
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
    
    <!-- 详情抽屉 -->
    <a-drawer v-model:visible="showDetailDrawer" title="物资详情" :width="600">
      <a-descriptions :column="2" bordered v-if="currentMaterial">
        <a-descriptions-item label="物资编码">{{ currentMaterial.code }}</a-descriptions-item>
        <a-descriptions-item label="物资名称">{{ currentMaterial.name }}</a-descriptions-item>
        <a-descriptions-item label="分类">{{ currentMaterial.category_name }}</a-descriptions-item>
        <a-descriptions-item label="规格型号">{{ currentMaterial.specification || '-' }}</a-descriptions-item>
        <a-descriptions-item label="单位">{{ currentMaterial.unit }}</a-descriptions-item>
        <a-descriptions-item label="单价">{{ currentMaterial.price ? `¥${currentMaterial.price}` : '-' }}</a-descriptions-item>
        <a-descriptions-item label="当前库存">{{ currentMaterial.current_stock }}</a-descriptions-item>
        <a-descriptions-item label="库存上限">{{ currentMaterial.max_stock || '-' }}</a-descriptions-item>
        <a-descriptions-item label="库存下限">{{ currentMaterial.min_stock || '-' }}</a-descriptions-item>
        <a-descriptions-item label="供应商">{{ currentMaterial.supplier || '-' }}</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="currentMaterial.status === 'active' ? 'green' : 'gray'">
            {{ currentMaterial.status === 'active' ? '启用' : '停用' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="备注" :span="2">{{ currentMaterial.remark || '-' }}</a-descriptions-item>
      </a-descriptions>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const submitLoading = ref(false)
const showModal = ref(false)
const showDetailDrawer = ref(false)
const editing = ref<any>(null)
const keyword = ref('')
const categoryId = ref('')
const status = ref('')
const categories = ref<any[]>([])
const materials = ref<any[]>([])
const currentMaterial = ref<any>(null)
const formRef = ref()
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const form = reactive({
  code: '',
  name: '',
  category_id: null,
  specification: '',
  unit: '',
  price: null,
  max_stock: null,
  min_stock: null,
  supplier: '',
  remark: '',
  status: 'active'
})

const columns = [
  { title: '物资编码', dataIndex: 'code', width: 120 },
  { title: '物资名称', dataIndex: 'name' },
  { title: '分类', dataIndex: 'category_name', width: 120 },
  { title: '规格型号', dataIndex: 'specification', width: 120 },
  { title: '单位', dataIndex: 'unit', width: 80 },
  { title: '单价', dataIndex: 'price', width: 100 },
  { title: '当前库存', dataIndex: 'current_stock', width: 100 },
  { title: '库存状态', slotName: 'stock_status', width: 100 },
  { title: '状态', slotName: 'status', width: 90 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const getStockStatusColor = (status: string) => {
  const map: Record<string, string> = {
    normal: 'green',
    low: 'orange',
    high: 'blue',
    out: 'red'
  }
  return map[status] || 'gray'
}

const getStockStatusText = (status: string) => {
  const map: Record<string, string> = {
    normal: '正常',
    low: '库存不足',
    high: '库存过高',
    out: '缺货'
  }
  return map[status] || '未知'
}

const fetchData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    materials.value = [
      { id: 1, code: 'MAT001', name: '潜水泵', category_id: 1, category_name: '设备', specification: 'QW100-80-15', unit: '台', price: 3500.00, current_stock: 5, max_stock: 10, min_stock: 2, stock_status: 'normal', supplier: 'XX设备公司', status: 'active' },
      { id: 2, code: 'MAT002', name: '曝气头', category_id: 2, category_name: '配件', specification: 'Φ215mm', unit: '个', price: 85.00, current_stock: 1, max_stock: 50, min_stock: 20, stock_status: 'low', supplier: 'YY配件公司', status: 'active' },
      { id: 3, code: 'MAT003', name: '聚合氯化铝', category_id: 3, category_name: '药剂', specification: '工业级', unit: 'kg', price: 2.50, current_stock: 0, max_stock: 5000, min_stock: 1000, stock_status: 'out', supplier: 'ZZ化工公司', status: 'active' },
      { id: 4, code: 'MAT004', name: '管道阀门', category_id: 2, category_name: '配件', specification: 'DN100', unit: '个', price: 450.00, current_stock: 25, max_stock: 30, min_stock: 10, stock_status: 'normal', supplier: 'XX设备公司', status: 'active' }
    ]
    pagination.total = materials.value.length
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  categories.value = [
    { id: 1, name: '设备' },
    { id: 2, name: '配件' },
    { id: 3, name: '药剂' },
    { id: 4, name: '工具' },
    { id: 5, name: '其他' }
  ]
}

const handleAdd = () => {
  editing.value = null
  Object.assign(form, {
    code: '',
    name: '',
    category_id: null,
    specification: '',
    unit: '',
    price: null,
    max_stock: null,
    min_stock: null,
    supplier: '',
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
  currentMaterial.value = record
  showDetailDrawer.value = true
}

const handleDelete = (record: any) => {
  const index = materials.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    materials.value.splice(index, 1)
    pagination.total = materials.value.length
    Message.success('删除成功')
  }
}

onMounted(() => {
  fetchData()
  fetchCategories()
})
</script>

<style scoped>
.table-operations {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}
</style>
