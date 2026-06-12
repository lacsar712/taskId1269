<template>
  <div class="page-container">
    <div class="page-header">
      <h2>设备台账</h2>
      <p>基础档案 / 设备分类管理 / 设备关联信息</p>
    </div>
    
    <div class="table-operations">
      <a-space>
        <a-input-search v-model="keyword" placeholder="搜索设备名称/编号" style="width: 240px;" @search="fetchData" />
        <a-select v-model="categoryId" placeholder="设备分类" style="width: 140px;" allow-clear>
          <a-option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</a-option>
        </a-select>
        <a-select v-model="status" placeholder="状态" style="width: 120px;" allow-clear>
          <a-option value="running">运行中</a-option>
          <a-option value="stopped">已停止</a-option>
          <a-option value="maintenance">维护中</a-option>
          <a-option value="fault">故障</a-option>
        </a-select>
      </a-space>
      <a-button type="primary" @click="handleOpenAddModal">
        <template #icon><icon-plus /></template>
        新增设备
      </a-button>
    </div>
    
    <a-table :columns="columns" :data="equipments" :loading="loading" :pagination="pagination">
      <template #status="{ record }">
        <a-tag :color="getStatusColor(record.status)">{{ getStatusText(record.status) }}</a-tag>
      </template>
      <template #operations="{ record }">
        <a-space>
          <a-button type="text" size="small" @click="viewEquipment(record)">详情</a-button>
          <a-button type="text" size="small" @click="editEquipment(record)">编辑</a-button>
        </a-space>
      </template>
    </a-table>
    
    <a-modal v-model:visible="showAddModal" :title="editingEquipment ? '编辑设备' : '新增设备'" @ok="handleSave" :ok-loading="submitLoading" width="600px">
      <a-form :model="form" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="设备名称" required>
              <a-input v-model="form.name" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="设备分类">
              <a-select v-model="form.category_id">
                <a-option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="型号规格">
              <a-input v-model="form.model" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="生产厂家">
              <a-input v-model="form.manufacturer" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="安装位置">
              <a-input v-model="form.location" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="所属工艺段">
              <a-select v-model="form.process_section">
                <a-option value="pretreatment">预处理</a-option>
                <a-option value="bio">生化处理</a-option>
                <a-option value="deep">深度处理</a-option>
                <a-option value="sludge">污泥处理</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="责任人">
          <a-input v-model="form.responsible_person" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <a-drawer v-model:visible="showDetailDrawer" title="设备详情" :width="600">
      <a-descriptions :column="2" bordered v-if="currentEquipment">
        <a-descriptions-item label="设备编号">{{ currentEquipment.code }}</a-descriptions-item>
        <a-descriptions-item label="设备名称">{{ currentEquipment.name }}</a-descriptions-item>
        <a-descriptions-item label="型号规格">{{ currentEquipment.model }}</a-descriptions-item>
        <a-descriptions-item label="生产厂家">{{ currentEquipment.manufacturer }}</a-descriptions-item>
        <a-descriptions-item label="安装位置">{{ currentEquipment.location }}</a-descriptions-item>
        <a-descriptions-item label="工艺段">{{ currentEquipment.process_section }}</a-descriptions-item>
        <a-descriptions-item label="运行时长">{{ currentEquipment.running_hours }} 小时</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="getStatusColor(currentEquipment.status)">{{ getStatusText(currentEquipment.status) }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="责任人">{{ currentEquipment.responsible_person }}</a-descriptions-item>
        <a-descriptions-item label="上次维护">{{ currentEquipment.last_maintenance_date }}</a-descriptions-item>
      </a-descriptions>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { equipmentApi } from '@/api'

import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const submitLoading = ref(false)
const showAddModal = ref(false)
const showDetailDrawer = ref(false)
const keyword = ref('')
const categoryId = ref('')
const status = ref('')
const categories = ref<any[]>([])
const equipments = ref<any[]>([])
const currentEquipment = ref<any>(null)
const editingEquipment = ref<any>(null)
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const form = reactive({
  name: '', category_id: null, model: '', manufacturer: '',
  location: '', process_section: '', responsible_person: ''
})

const columns = [
  { title: '设备编号', dataIndex: 'code', width: 120 },
  { title: '设备名称', dataIndex: 'name' },
  { title: '型号', dataIndex: 'model', width: 120 },
  { title: '安装位置', dataIndex: 'location', width: 120 },
  { title: '工艺段', dataIndex: 'process_section', width: 100 },
  { title: '运行时长(h)', dataIndex: 'running_hours', width: 100 },
  { title: '状态', slotName: 'status', width: 90 },
  { title: '操作', slotName: 'operations', width: 120 }
]

const getStatusColor = (s: string) => ({ running: 'green', stopped: 'gray', maintenance: 'orange', fault: 'red' }[s] || 'gray')
const getStatusText = (s: string) => ({ running: '运行中', stopped: '已停止', maintenance: '维护中', fault: '故障' }[s] || '未知')

const fetchData = async () => {
  loading.value = true
  try {
    const res: any = await equipmentApi.getList({ page: pagination.current, page_size: pagination.pageSize, keyword: keyword.value || undefined, category_id: categoryId.value || undefined, status: status.value || undefined })
    equipments.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    equipments.value = [
      { code: 'EQ001', name: '曝气风机#1', model: 'DL-200', location: '风机房', process_section: '生化处理', running_hours: 12500, status: 'running', responsible_person: '张三', manufacturer: 'XX公司' },
      { code: 'EQ002', name: '曝气风机#2', model: 'DL-200', location: '风机房', process_section: '生化处理', running_hours: 11800, status: 'running', responsible_person: '张三', manufacturer: 'XX公司' },
      { code: 'EQ003', name: '提升泵#1', model: 'QW-150', location: '进水泵房', process_section: '预处理', running_hours: 8500, status: 'running', responsible_person: '李四', manufacturer: 'YY公司' },
      { code: 'EQ004', name: '刮泥机', model: 'ZGN-30', location: '二沉池', process_section: '生化处理', running_hours: 6200, status: 'maintenance', responsible_person: '王五', manufacturer: 'ZZ公司' }
    ]
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res: any = await equipmentApi.getCategories()
    categories.value = res || []
  } catch (e) {
    categories.value = [
      { id: 1, name: '风机' }, { id: 2, name: '水泵' }, { id: 3, name: '阀门' }, { id: 4, name: '仪表' }
    ]
  }
}

const viewEquipment = (record: any) => {
  currentEquipment.value = record
  showDetailDrawer.value = true
}

const handleOpenAddModal = () => {
  resetForm()
  showAddModal.value = true
}

const editEquipment = (record: any) => {
  editingEquipment.value = record
  Object.assign(form, {
    name: record.name,
    category_id: record.category_id || null,
    model: record.model,
    manufacturer: record.manufacturer,
    location: record.location,
    process_section: record.process_section,
    responsible_person: record.responsible_person
  })
  showAddModal.value = true
}

const resetForm = () => {
  Object.assign(form, {
    name: '', category_id: null, model: '', manufacturer: '',
    location: '', process_section: '', responsible_person: ''
  })
  editingEquipment.value = null
}

const handleSave = () => {
  if (editingEquipment.value) {
    // 编辑模式
    const index = equipments.value.findIndex(item => item.code === editingEquipment.value.code)
    if (index > -1) {
      Object.assign(equipments.value[index], form)
      Message.success('编辑成功')
    }
  } else {
    // 新增模式
    equipments.value.push({
      code: 'EQ' + String(Date.now()).slice(-3),
      ...form,
      running_hours: 0,
      status: 'stopped'
    })
    Message.success('新增成功')
  }
  showAddModal.value = false
  resetForm()
}

onMounted(() => {
  fetchData()
  fetchCategories()
})
</script>

<style scoped>
.table-operations { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
