<template>
  <div class="page-container reagent-inventory">
    <div class="page-header">
      <h2>化验试剂库存</h2>
      <p>管理化验室常用试剂的名称、规格、生产厂家、库存量与有效期，库存低于预警线时集中提示</p>
    </div>

    <!-- 低库存预警汇总条 -->
    <div v-if="lowStockReagents.length > 0" class="warning-banner">
      <div class="warning-header">
        <icon-exclamation-circle class="warning-icon" />
        <span class="warning-title">库存预警提醒</span>
        <span class="warning-count">共 {{ lowStockReagents.length }} 种试剂库存低于安全线</span>
      </div>
      <div class="warning-items">
        <div 
          v-for="item in lowStockReagents.slice(0, 6)" 
          :key="item.id" 
          class="warning-item"
          @click="scrollToReagent(item)"
        >
          <span class="item-name">{{ item.name }}</span>
          <span class="item-spec">{{ item.specification || '-' }}</span>
          <span class="item-stock">
            当前: <strong>{{ item.current_stock }}</strong> / 安全: {{ item.min_safe_stock }} {{ item.unit }}
          </span>
          <a-button type="text" size="mini" class="apply-btn" @click.stop="openApplyModal(item)">
            立即补货
          </a-button>
        </div>
        <div v-if="lowStockReagents.length > 6" class="warning-more">
          还有 {{ lowStockReagents.length - 6 }} 种...
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card total">
        <div class="stat-icon">
          <icon-experiment />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">试剂总数</div>
        </div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon">
          <icon-exclamation-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.low_stock }}</div>
          <div class="stat-label">库存不足</div>
        </div>
      </div>
      <div class="stat-card expiry">
        <div class="stat-icon">
          <icon-calendar />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.near_expiry }}</div>
          <div class="stat-label">临近过期</div>
        </div>
      </div>
      <div class="stat-card category">
        <div class="stat-icon">
          <icon-folder />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.categories }}</div>
          <div class="stat-label">试剂分类</div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="table-operations">
      <a-space :size="12">
        <a-input-search 
          v-model="filters.keyword" 
          placeholder="搜索试剂名称/编号/厂家" 
          style="width: 260px;" 
        />
        <a-select 
          v-model="filters.category" 
          placeholder="试剂分类" 
          style="width: 140px;" 
          allow-clear
        >
          <a-option v-for="cat in categories" :key="cat.name" :value="cat.name">
            {{ cat.name }}
          </a-option>
        </a-select>
        <a-select 
          v-model="filters.status" 
          placeholder="状态" 
          style="width: 120px;" 
          allow-clear
        >
          <a-option value="active">在用</a-option>
          <a-option value="inactive">停用</a-option>
        </a-select>
        <a-checkbox v-model="filters.low_stock_only">
          仅显示低库存
        </a-checkbox>
      </a-space>
      <a-space :size="8">
        <a-button type="outline" @click="handleReset">
          <template #icon><icon-refresh /></template>
          重置
        </a-button>
        <a-button type="primary" @click="openAddModal">
          <template #icon><icon-plus /></template>
          新增试剂
        </a-button>
      </a-space>
    </div>

    <!-- 试剂列表 -->
    <div class="table-wrapper">
      <a-table 
        :columns="columns" 
        :data="reagentList" 
        :loading="false" 
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        :scroll="{ x: 1200 }"
      >
        <template #stock="{ record }">
          <div class="stock-cell">
            <div class="stock-bar">
              <div 
                class="stock-fill" 
                :class="{ 
                  low: record.current_stock <= record.min_safe_stock,
                  medium: record.current_stock > record.min_safe_stock && record.current_stock <= record.min_safe_stock * 2
                }"
                :style="{ width: getStockPercent(record) + '%' }"
              ></div>
            </div>
            <span 
              class="stock-text"
              :class="{ 'low-text': record.current_stock <= record.min_safe_stock }"
            >
              {{ record.current_stock }} / {{ record.min_safe_stock }}
            </span>
          </div>
        </template>

        <template #expiry="{ record }">
          <span v-if="record.expiry_date" :class="{ 'expiry-soon': isExpirySoon(record.expiry_date) }">
            {{ record.expiry_date }}
          </span>
          <span v-else>-</span>
        </template>

        <template #status="{ record }">
          <a-tag :color="record.status === 'active' ? 'green' : 'gray'">
            {{ record.status === 'active' ? '在用' : '停用' }}
          </a-tag>
        </template>

        <template #operations="{ record }">
          <a-space :size="4">
            <a-button type="text" size="small" @click="viewReagent(record)">详情</a-button>
            <a-button type="text" size="small" @click="openEditModal(record)">编辑</a-button>
            <a-button type="text" size="small" @click="openApplyModal(record)">补货</a-button>
            <a-popconfirm 
              content="确定停用该试剂吗？" 
              @ok="deleteReagent(record)"
              v-if="record.status === 'active'"
            >
              <a-button type="text" size="small" status="danger">停用</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </div>

    <!-- 新增/编辑试剂弹窗 -->
    <a-modal 
      v-model:visible="showReagentModal" 
      :title="isEdit ? '编辑试剂' : '新增试剂'" 
      @ok="submitReagent" 
      :ok-loading="submitLoading"
      width="720px"
    >
      <a-form :model="reagentForm" layout="vertical" ref="reagentFormRef">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="试剂名称" field="name" required>
              <a-input v-model="reagentForm.name" placeholder="请输入试剂名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="规格" field="specification">
              <a-input v-model="reagentForm.specification" placeholder="例如：500ml/瓶" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="生产厂家" field="manufacturer">
              <a-input v-model="reagentForm.manufacturer" placeholder="请输入生产厂家" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="试剂分类" field="category">
              <a-select v-model="reagentForm.category" placeholder="请选择或输入分类" allow-create allow-clear>
                <a-option v-for="cat in categories" :key="cat.name" :value="cat.name">
                  {{ cat.name }}
                </a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="当前库存" field="current_stock">
              <a-input-number v-model="reagentForm.current_stock" :min="0" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="最低安全库存" field="min_safe_stock">
              <a-input-number v-model="reagentForm.min_safe_stock" :min="0" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="单位" field="unit">
              <a-select v-model="reagentForm.unit" allow-create>
                <a-option value="瓶">瓶</a-option>
                <a-option value="盒">盒</a-option>
                <a-option value="支">支</a-option>
                <a-option value="g">g</a-option>
                <a-option value="kg">kg</a-option>
                <a-option value="ml">ml</a-option>
                <a-option value="L">L</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="存放位置" field="storage_location">
              <a-input v-model="reagentForm.storage_location" placeholder="例如：冷藏柜A区" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="有效期" field="expiry_date">
              <a-date-picker v-model="reagentForm.expiry_date" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="纯度等级" field="purity">
              <a-select v-model="reagentForm.purity" allow-clear allow-create>
                <a-option value="分析纯">分析纯(AR)</a-option>
                <a-option value="化学纯">化学纯(CP)</a-option>
                <a-option value="优级纯">优级纯(GR)</a-option>
                <a-option value="色谱纯">色谱纯</a-option>
                <a-option value="基准试剂">基准试剂</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="CAS号" field="cas_no">
              <a-input v-model="reagentForm.cas_no" placeholder="CAS编号" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="备注" field="remarks">
          <a-textarea v-model="reagentForm.remarks" :auto-size="{ minRows: 2, maxRows: 4 }" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 试剂详情抽屉 -->
    <a-drawer v-model:visible="showDetailDrawer" title="试剂详情" :width="560">
      <div v-if="currentReagent">
        <a-descriptions :column="2" bordered size="small">
          <a-descriptions-item label="试剂编号">{{ currentReagent.reagent_no }}</a-descriptions-item>
          <a-descriptions-item label="试剂名称">{{ currentReagent.name }}</a-descriptions-item>
          <a-descriptions-item label="规格">{{ currentReagent.specification || '-' }}</a-descriptions-item>
          <a-descriptions-item label="分类">{{ currentReagent.category || '-' }}</a-descriptions-item>
          <a-descriptions-item label="生产厂家">{{ currentReagent.manufacturer || '-' }}</a-descriptions-item>
          <a-descriptions-item label="纯度">{{ currentReagent.purity || '-' }}</a-descriptions-item>
          <a-descriptions-item label="CAS号">{{ currentReagent.cas_no || '-' }}</a-descriptions-item>
          <a-descriptions-item label="单位">{{ currentReagent.unit }}</a-descriptions-item>
          <a-descriptions-item label="当前库存">
            <span :class="{ 'low-text': currentReagent.current_stock <= currentReagent.min_safe_stock }">
              {{ currentReagent.current_stock }}
            </span>
          </a-descriptions-item>
          <a-descriptions-item label="最低安全库存">{{ currentReagent.min_safe_stock }}</a-descriptions-item>
          <a-descriptions-item label="存放位置">{{ currentReagent.storage_location || '-' }}</a-descriptions-item>
          <a-descriptions-item label="有效期">
            <span :class="{ 'expiry-soon': isExpirySoon(currentReagent.expiry_date) }">
              {{ currentReagent.expiry_date || '-' }}
            </span>
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="currentReagent.status === 'active' ? 'green' : 'gray'">
              {{ currentReagent.status === 'active' ? '在用' : '停用' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">{{ currentReagent.created_at }}</a-descriptions-item>
          <a-descriptions-item label="备注" :span="2">{{ currentReagent.remarks || '-' }}</a-descriptions-item>
        </a-descriptions>
        
        <div class="detail-actions">
          <a-space>
            <a-button type="primary" @click="openEditModal(currentReagent); showDetailDrawer = false;">
              <template #icon><icon-edit /></template>
              编辑
            </a-button>
            <a-button @click="openApplyModal(currentReagent); showDetailDrawer = false;">
              <template #icon><icon-plus /></template>
              申请补货
            </a-button>
          </a-space>
        </div>
      </div>
    </a-drawer>

    <!-- 补货申请弹窗 -->
    <a-modal 
      v-model:visible="showApplyModal" 
      title="补货申请" 
      @ok="submitApply" 
      :ok-loading="applyLoading"
      width="520px"
    >
      <div v-if="applyReagent" class="apply-info">
        <a-descriptions :column="2" size="small" bordered style="margin-bottom: 16px;">
          <a-descriptions-item label="试剂名称">{{ applyReagent.name }}</a-descriptions-item>
          <a-descriptions-item label="规格">{{ applyReagent.specification || '-' }}</a-descriptions-item>
          <a-descriptions-item label="当前库存">
            <span :class="{ 'low-text': applyReagent.current_stock <= applyReagent.min_safe_stock }">
              {{ applyReagent.current_stock }} {{ applyReagent.unit }}
            </span>
          </a-descriptions-item>
          <a-descriptions-item label="安全库存">
            {{ applyReagent.min_safe_stock }} {{ applyReagent.unit }}
          </a-descriptions-item>
        </a-descriptions>
      </div>
      
      <a-form :model="applyForm" layout="vertical">
        <a-form-item label="申请数量" required>
          <a-input-number 
            v-model="applyForm.apply_quantity" 
            :min="1" 
            :style="{ width: '100%' }"
            :addon-after="applyReagent?.unit || '瓶'"
          />
        </a-form-item>
        <a-form-item label="紧急程度" required>
          <a-radio-group v-model="applyForm.urgency">
            <a-radio value="urgent">紧急</a-radio>
            <a-radio value="normal">普通</a-radio>
            <a-radio value="low">低</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="用途说明">
          <a-textarea 
            v-model="applyForm.purpose" 
            placeholder="请简要说明试剂用途"
            :auto-size="{ minRows: 3, maxRows: 5 }"
            :max-length="200"
            show-word-limit
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useReagentStore } from '@/stores/reagent'

const store = useReagentStore()

const submitLoading = ref(false)
const applyLoading = ref(false)
const showReagentModal = ref(false)
const showDetailDrawer = ref(false)
const showApplyModal = ref(false)
const isEdit = ref(false)
const currentReagent = ref<any>(null)
const applyReagent = ref<any>(null)

const filters = reactive({
  keyword: '',
  category: '',
  status: '',
  low_stock_only: false
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const reagentForm = reactive({
  name: '',
  specification: '',
  manufacturer: '',
  current_stock: 0,
  min_safe_stock: 0,
  storage_location: '',
  expiry_date: '',
  unit: '瓶',
  category: '',
  purity: '',
  cas_no: '',
  remarks: ''
})

const applyForm = reactive({
  apply_quantity: 1,
  urgency: 'normal',
  purpose: ''
})

const lowStockReagents = computed(() => store.lowStockReagents)
const stats = computed(() => store.stats)
const categories = computed(() => store.categories)

const filteredReagents = computed(() => {
  let list = [...store.reagents]
  if (filters.keyword) {
    const kw = filters.keyword.toLowerCase()
    list = list.filter(item =>
      item.name.toLowerCase().includes(kw) ||
      item.reagent_no.toLowerCase().includes(kw) ||
      (item.manufacturer && item.manufacturer.toLowerCase().includes(kw))
    )
  }
  if (filters.category) {
    list = list.filter(item => item.category === filters.category)
  }
  if (filters.status) {
    list = list.filter(item => item.status === filters.status)
  }
  if (filters.low_stock_only) {
    list = list.filter(item => item.current_stock <= item.min_safe_stock)
  }
  return list
})

const reagentList = computed(() => {
  const start = (pagination.current - 1) * pagination.pageSize
  pagination.total = filteredReagents.value.length
  return filteredReagents.value.slice(start, start + pagination.pageSize)
})

const columns = [
  { title: '试剂编号', dataIndex: 'reagent_no', width: 130 },
  { title: '试剂名称', dataIndex: 'name', width: 140 },
  { title: '规格', dataIndex: 'specification', width: 120 },
  { title: '生产厂家', dataIndex: 'manufacturer', width: 140 },
  { 
    title: '库存/安全库存', 
    dataIndex: 'stock', 
    slotName: 'stock',
    width: 180
  },
  { title: '存放位置', dataIndex: 'storage_location', width: 120 },
  { 
    title: '有效期', 
    dataIndex: 'expiry_date',
    slotName: 'expiry',
    width: 110
  },
  { title: '状态', dataIndex: 'status', slotName: 'status', width: 80 },
  { title: '操作', dataIndex: 'operations', slotName: 'operations', width: 200, fixed: 'right' }
]

const getStockPercent = (record: any) => {
  if (!record.min_safe_stock) return 100
  const percent = (record.current_stock / (record.min_safe_stock * 3)) * 100
  return Math.min(percent, 100)
}

const isExpirySoon = (date: string) => {
  if (!date) return false
  const expiry = new Date(date)
  const now = new Date()
  const diffDays = Math.ceil((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  return diffDays <= 30 && diffDays > 0
}

const handleReset = () => {
  filters.keyword = ''
  filters.category = ''
  filters.status = ''
  filters.low_stock_only = false
  pagination.current = 1
}

const handlePageChange = (page: number) => {
  pagination.current = page
}

const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize
  pagination.current = 1
}

const openAddModal = () => {
  isEdit.value = false
  currentReagent.value = null
  Object.assign(reagentForm, {
    name: '',
    specification: '',
    manufacturer: '',
    current_stock: 0,
    min_safe_stock: 0,
    storage_location: '',
    expiry_date: '',
    unit: '瓶',
    category: '',
    purity: '',
    cas_no: '',
    remarks: ''
  })
  showReagentModal.value = true
}

const openEditModal = (record: any) => {
  isEdit.value = true
  currentReagent.value = record
  Object.assign(reagentForm, { ...record })
  showReagentModal.value = true
}

const submitReagent = async () => {
  if (!reagentForm.name) {
    Message.warning('请输入试剂名称')
    return
  }
  
  submitLoading.value = true
  try {
    if (isEdit.value && currentReagent.value) {
      store.updateReagent(currentReagent.value.id, { ...reagentForm })
      Message.success('更新成功')
    } else {
      store.addReagent({ ...reagentForm })
      Message.success('新增成功')
    }
    showReagentModal.value = false
  } finally {
    submitLoading.value = false
  }
}

const deleteReagent = async (record: any) => {
  store.deactivateReagent(record.id)
  Message.success('已停用')
}

const viewReagent = (record: any) => {
  currentReagent.value = record
  showDetailDrawer.value = true
}

const scrollToReagent = (item: any) => {
  filters.keyword = item.name
  filters.low_stock_only = false
  pagination.current = 1
}

const openApplyModal = (record: any) => {
  applyReagent.value = record
  applyForm.apply_quantity = Math.max(1, record.min_safe_stock - record.current_stock)
  applyForm.urgency = record.current_stock === 0 ? 'urgent' : 'normal'
  applyForm.purpose = ''
  showApplyModal.value = true
}

const submitApply = async () => {
  if (!applyForm.apply_quantity || applyForm.apply_quantity <= 0) {
    Message.warning('请输入申请数量')
    return
  }
  
  applyLoading.value = true
  try {
    const result = store.addReplenishment({
      reagent_id: applyReagent.value.id,
      apply_quantity: applyForm.apply_quantity,
      urgency: applyForm.urgency,
      purpose: applyForm.purpose
    })
    if (result) {
      Message.success('申请已提交，可在补货申请管理页查看审批进度')
      showApplyModal.value = false
    } else {
      Message.error('提交失败，未找到对应试剂')
    }
  } finally {
    applyLoading.value = false
  }
}

onMounted(() => {
  store.fetchReagents()
  store.fetchCategories()
})
</script>

<style scoped>
.reagent-inventory {
  min-height: calc(100vh - 120px);
}

.warning-banner {
  background: linear-gradient(135deg, #fff7e8 0%, #ffe7c8 100%);
  border: 1px solid #ffaa00;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 20px;
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.warning-icon {
  color: #ff7d00;
  font-size: 20px;
}

.warning-title {
  font-size: 16px;
  font-weight: 600;
  color: #b55c00;
}

.warning-count {
  font-size: 13px;
  color: #865000;
  margin-left: auto;
}

.warning-items {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.warning-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 14px;
  background: #fff;
  border: 1px solid #ffd28a;
  border-radius: 6px;
  min-width: 200px;
  cursor: pointer;
  transition: all 0.2s;
}

.warning-item:hover {
  box-shadow: 0 2px 8px rgba(255, 125, 0, 0.2);
  transform: translateY(-1px);
}

.item-name {
  font-size: 14px;
  font-weight: 600;
  color: #b55c00;
}

.item-spec {
  font-size: 12px;
  color: #86909c;
}

.item-stock {
  font-size: 12px;
  color: #4e5969;
}

.item-stock strong {
  color: #f53f3f;
  font-weight: 600;
}

.apply-btn {
  align-self: flex-end;
  margin-top: 4px;
  color: #ff7d00 !important;
}

.warning-more {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 14px;
  color: #865000;
  font-size: 13px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 16px;
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #e8f3ff, #d6e4ff);
  color: #165DFF;
}

.stat-card.warning .stat-icon {
  background: linear-gradient(135deg, #fff7e8, #ffe7c8);
  color: #ff7d00;
}

.stat-card.expiry .stat-icon {
  background: linear-gradient(135deg, #ffece8, #ffd2c8);
  color: #f53f3f;
}

.stat-card.category .stat-icon {
  background: linear-gradient(135deg, #e8ffea, #c8ffcd);
  color: #00b42a;
}

.stat-info .stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  line-height: 1.2;
}

.stat-card.total .stat-value { color: #165DFF; }
.stat-card.warning .stat-value { color: #ff7d00; }
.stat-card.expiry .stat-value { color: #f53f3f; }
.stat-card.category .stat-value { color: #00b42a; }

.stat-info .stat-label {
  font-size: 14px;
  color: #86909c;
  margin-top: 4px;
}

.table-operations {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
}

.table-wrapper {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  padding: 16px;
}

.stock-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stock-bar {
  flex: 1;
  height: 8px;
  background: #f2f3f5;
  border-radius: 4px;
  overflow: hidden;
  min-width: 80px;
}

.stock-fill {
  height: 100%;
  background: #00b42a;
  border-radius: 4px;
  transition: width 0.3s;
}

.stock-fill.low {
  background: #f53f3f;
}

.stock-fill.medium {
  background: #ff7d00;
}

.stock-text {
  font-size: 12px;
  color: #4e5969;
  white-space: nowrap;
}

.stock-text.low-text {
  color: #f53f3f;
  font-weight: 600;
}

.low-text {
  color: #f53f3f;
  font-weight: 600;
}

.expiry-soon {
  color: #f53f3f;
  font-weight: 500;
}

.apply-info {
  padding: 8px 0;
}

.detail-actions {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e6eb;
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .table-operations {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>
