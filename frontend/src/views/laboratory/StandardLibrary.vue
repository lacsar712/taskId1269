<template>
  <div class="page-container">
    <div class="page-header">
      <h2>标准库</h2>
      <p>检测方法标准 / 限值标准管理</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="检测方法标准">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="methodKeyword" placeholder="搜索标准编号/名称" style="width: 240px;" @search="fetchMethods" />
            <a-select v-model="methodCategory" placeholder="标准类别" style="width: 140px;" allow-clear @change="fetchMethods">
              <a-option value="national">国家标准</a-option>
              <a-option value="industry">行业标准</a-option>
              <a-option value="local">地方标准</a-option>
              <a-option value="enterprise">企业标准</a-option>
            </a-select>
            <a-select v-model="methodStatus" placeholder="状态" style="width: 120px;" allow-clear @change="fetchMethods">
              <a-option value="active">有效</a-option>
              <a-option value="obsolete">已废止</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="showMethodModal = true">
            <template #icon><icon-plus /></template>
            新增标准
          </a-button>
        </div>
        
        <a-table :columns="methodColumns" :data="methods" :loading="methodLoading" :pagination="methodPagination" @page-change="handleMethodPageChange">
          <template #category="{ record }">
            <a-tag :color="getCategoryColor(record.category)">{{ getCategoryText(record.category) }}</a-tag>
          </template>
          <template #status="{ record }">
            <a-tag :color="record.status === 'active' ? 'green' : 'gray'">{{ record.status === 'active' ? '有效' : '已废止' }}</a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" @click="viewMethod(record)">查看</a-button>
              <a-button type="text" size="small" @click="editMethod(record)">编辑</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="限值标准管理">
        <div class="table-operations">
          <a-space>
            <a-input-search v-model="limitKeyword" placeholder="搜索检测项目" style="width: 240px;" @search="fetchLimits" />
            <a-select v-model="limitType" placeholder="标准类型" style="width: 140px;" allow-clear>
              <a-option value="discharge">排放标准</a-option>
              <a-option value="environmental">环境标准</a-option>
              <a-option value="reuse">回用标准</a-option>
            </a-select>
            <a-select v-model="limitCategory" placeholder="标准类别" style="width: 140px;" allow-clear>
              <a-option value="national">国家标准</a-option>
              <a-option value="industry">行业标准</a-option>
              <a-option value="local">地方标准</a-option>
            </a-select>
          </a-space>
          <a-button type="primary" @click="showLimitModal = true">
            <template #icon><icon-plus /></template>
            新增限值
          </a-button>
        </div>
        
        <a-table :columns="limitColumns" :data="limits" :loading="limitLoading" :pagination="limitPagination">
          <template #type="{ record }">
            <a-tag :color="getLimitTypeColor(record.type)">{{ getLimitTypeText(record.type) }}</a-tag>
          </template>
          <template #category="{ record }">
            <a-tag :color="getCategoryColor(record.category)">{{ getCategoryText(record.category) }}</a-tag>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" @click="viewLimit(record)">查看</a-button>
              <a-button type="text" size="small" @click="editLimit(record)">编辑</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 检测方法标准弹窗 -->
    <a-modal v-model:visible="showMethodModal" title="检测方法标准" @ok="handleMethodSave" :ok-loading="methodSubmitLoading" width="800px">
      <a-form :model="methodForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="标准编号" field="standard_no" required>
              <a-input v-model="methodForm.standard_no" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="标准名称" field="name" required>
              <a-input v-model="methodForm.name" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="标准类别" field="category" required>
              <a-select v-model="methodForm.category">
                <a-option value="national">国家标准</a-option>
                <a-option value="industry">行业标准</a-option>
                <a-option value="local">地方标准</a-option>
                <a-option value="enterprise">企业标准</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="检测项目" field="test_item" required>
              <a-select v-model="methodForm.test_item">
                <a-option value="cod">COD</a-option>
                <a-option value="bod">BOD</a-option>
                <a-option value="nh3_n">氨氮</a-option>
                <a-option value="tp">总磷</a-option>
                <a-option value="tn">总氮</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="发布日期" field="publish_date" required>
              <a-date-picker v-model="methodForm.publish_date" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="实施日期" field="implement_date" required>
              <a-date-picker v-model="methodForm.implement_date" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="状态" field="status" required>
              <a-select v-model="methodForm.status">
                <a-option value="active">有效</a-option>
                <a-option value="obsolete">已废止</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="标准文件" field="file_url">
              <a-upload :auto-upload="false">
                <template #upload-button>
                  <a-button>选择文件</a-button>
                </template>
              </a-upload>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="标准摘要" field="summary">
          <a-textarea v-model="methodForm.summary" :max-length="1000" show-word-limit />
        </a-form-item>
        <a-form-item label="备注" field="remark">
          <a-textarea v-model="methodForm.remark" :max-length="500" show-word-limit />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 限值标准弹窗 -->
    <a-modal v-model:visible="showLimitModal" title="限值标准管理" @ok="handleLimitSave" :ok-loading="limitSubmitLoading" width="800px">
      <a-form :model="limitForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="标准编号" field="standard_no" required>
              <a-input v-model="limitForm.standard_no" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="标准名称" field="name" required>
              <a-input v-model="limitForm.name" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="标准类型" field="type" required>
              <a-select v-model="limitForm.type">
                <a-option value="discharge">排放标准</a-option>
                <a-option value="environmental">环境标准</a-option>
                <a-option value="reuse">回用标准</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="标准类别" field="category" required>
              <a-select v-model="limitForm.category">
                <a-option value="national">国家标准</a-option>
                <a-option value="industry">行业标准</a-option>
                <a-option value="local">地方标准</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="限值项目" required>
          <a-table :columns="limitItemColumns" :data="limitForm.limit_items" :pagination="false" size="small">
            <template #test_item="{ record, rowIndex }">
              <a-select v-model="record.test_item" style="width: 100%;">
                <a-option value="cod">COD</a-option>
                <a-option value="bod">BOD</a-option>
                <a-option value="nh3_n">氨氮</a-option>
                <a-option value="tp">总磷</a-option>
                <a-option value="tn">总氮</a-option>
              </a-select>
            </template>
            <template #limit_value="{ record, rowIndex }">
              <a-input-number v-model="record.limit_value" :precision="2" style="width: 100%;" />
            </template>
            <template #unit="{ record, rowIndex }">
              <a-input v-model="record.unit" style="width: 100%;" />
            </template>
            <template #operations="{ record, rowIndex }">
              <a-button type="text" size="small" status="danger" @click="removeLimitItem(rowIndex)">删除</a-button>
            </template>
          </a-table>
          <a-button type="dashed" style="width: 100%; margin-top: 8px;" @click="addLimitItem">
            <template #icon><icon-plus /></template>
            添加限值项
          </a-button>
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="发布日期" field="publish_date" required>
              <a-date-picker v-model="limitForm.publish_date" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="实施日期" field="implement_date" required>
              <a-date-picker v-model="limitForm.implement_date" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="备注" field="remark">
          <a-textarea v-model="limitForm.remark" :max-length="500" show-word-limit />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 详情抽屉 -->
    <a-drawer v-model:visible="showDetailDrawer" title="标准详情" :width="700">
      <a-descriptions :column="2" bordered v-if="currentRecord">
        <template v-for="(value, key) in currentRecord" :key="key">
          <a-descriptions-item :label="key">{{ value }}</a-descriptions-item>
        </template>
      </a-descriptions>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'

const methodLoading = ref(false)
const limitLoading = ref(false)
const methodSubmitLoading = ref(false)
const limitSubmitLoading = ref(false)

const showMethodModal = ref(false)
const showLimitModal = ref(false)
const showDetailDrawer = ref(false)

const methodKeyword = ref('')
const methodCategory = ref('')
const methodStatus = ref('')
const limitKeyword = ref('')
const limitType = ref('')
const limitCategory = ref('')

const methods = ref<any[]>([])
const limits = ref<any[]>([])
const currentRecord = ref<any>(null)

const methodPagination = reactive({ current: 1, pageSize: 10, total: 0 })
const limitPagination = reactive({ current: 1, pageSize: 10, total: 0 })

const methodForm = reactive({
  standard_no: '',
  name: '',
  category: '',
  test_item: '',
  publish_date: '',
  implement_date: '',
  status: 'active',
  file_url: '',
  summary: '',
  remark: ''
})

const limitForm = reactive({
  standard_no: '',
  name: '',
  type: '',
  category: '',
  limit_items: [] as any[],
  publish_date: '',
  implement_date: '',
  remark: ''
})

const methodColumns = [
  { title: '标准编号', dataIndex: 'standard_no', width: 160 },
  { title: '标准名称', dataIndex: 'name' },
  { title: '标准类别', slotName: 'category', width: 120 },
  { title: '检测项目', dataIndex: 'test_item', width: 120 },
  { title: '发布日期', dataIndex: 'publish_date', width: 120 },
  { title: '实施日期', dataIndex: 'implement_date', width: 120 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const limitColumns = [
  { title: '标准编号', dataIndex: 'standard_no', width: 160 },
  { title: '标准名称', dataIndex: 'name' },
  { title: '标准类型', slotName: 'type', width: 120 },
  { title: '标准类别', slotName: 'category', width: 120 },
  { title: '限值项目数', dataIndex: 'item_count', width: 100 },
  { title: '发布日期', dataIndex: 'publish_date', width: 120 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const limitItemColumns = [
  { title: '检测项目', slotName: 'test_item', width: 150 },
  { title: '限值', slotName: 'limit_value', width: 150 },
  { title: '单位', slotName: 'unit', width: 100 },
  { title: '操作', slotName: 'operations', width: 100 }
]

const getCategoryColor = (category: string) => {
  const map: Record<string, string> = {
    national: 'red',
    industry: 'blue',
    local: 'green',
    enterprise: 'orange'
  }
  return map[category] || 'gray'
}

const getCategoryText = (category: string) => {
  const map: Record<string, string> = {
    national: '国家标准',
    industry: '行业标准',
    local: '地方标准',
    enterprise: '企业标准'
  }
  return map[category] || category
}

const getLimitTypeColor = (type: string) => {
  const map: Record<string, string> = {
    discharge: 'red',
    environmental: 'blue',
    reuse: 'green'
  }
  return map[type] || 'gray'
}

const getLimitTypeText = (type: string) => {
  const map: Record<string, string> = {
    discharge: '排放标准',
    environmental: '环境标准',
    reuse: '回用标准'
  }
  return map[type] || type
}

const fetchMethods = async () => {
  methodLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    methods.value = [
      { id: 1, standard_no: 'GB 11914-1989', name: '水质 化学需氧量的测定 重铬酸盐法', category: 'national', test_item: 'COD', publish_date: '1989-12-25', implement_date: '1990-07-01', status: 'active', summary: '本标准规定了水中化学需氧量的测定方法' },
      { id: 2, standard_no: 'HJ 505-2009', name: '水质 五日生化需氧量(BOD5)的测定 稀释与接种法', category: 'industry', test_item: 'BOD', publish_date: '2009-09-27', implement_date: '2009-12-01', status: 'active', summary: '本标准规定了水中五日生化需氧量的测定方法' },
      { id: 3, standard_no: 'HJ 535-2009', name: '水质 氨氮的测定 纳氏试剂分光光度法', category: 'industry', test_item: '氨氮', publish_date: '2009-12-31', implement_date: '2010-04-01', status: 'active', summary: '本标准规定了水中氨氮的测定方法' }
    ]
    methodPagination.total = methods.value.length
  } finally {
    methodLoading.value = false
  }
}

const fetchLimits = async () => {
  limitLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    limits.value = [
      { id: 1, standard_no: 'GB 18918-2002', name: '城镇污水处理厂污染物排放标准', type: 'discharge', category: 'national', item_count: 19, publish_date: '2002-12-24', implement_date: '2003-07-01' },
      { id: 2, standard_no: 'GB 3838-2002', name: '地表水环境质量标准', type: 'environmental', category: 'national', item_count: 24, publish_date: '2002-04-28', implement_date: '2002-06-01' },
      { id: 3, standard_no: 'GB/T 18921-2019', name: '城市污水再生利用 景观环境用水水质', type: 'reuse', category: 'national', item_count: 14, publish_date: '2019-06-04', implement_date: '2020-01-01' }
    ]
    limitPagination.total = limits.value.length
  } finally {
    limitLoading.value = false
  }
}

const handleMethodPageChange = (page: number) => {
  methodPagination.current = page
  fetchMethods()
}

const viewMethod = (record: any) => {
  currentRecord.value = record
  showDetailDrawer.value = true
}

const editMethod = (record: any) => {
  Object.assign(methodForm, record)
  showMethodModal.value = true
}

const downloadMethod = (record: any) => {
  Message.success('标准文件下载中...')
}

const viewLimit = (record: any) => {
  currentRecord.value = record
  showDetailDrawer.value = true
}

const editLimit = (record: any) => {
  Object.assign(limitForm, record)
  if (!limitForm.limit_items || limitForm.limit_items.length === 0) {
    limitForm.limit_items = [
      { test_item: '', limit_value: null, unit: '' }
    ]
  }
  showLimitModal.value = true
}

const addLimitItem = () => {
  limitForm.limit_items.push({ test_item: '', limit_value: null, unit: '' })
}

const removeLimitItem = (index: number) => {
  limitForm.limit_items.splice(index, 1)
}

const handleMethodSave = async () => {
  methodSubmitLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    Message.success('保存成功')
    showMethodModal.value = false
    Object.assign(methodForm, {
      standard_no: '',
      name: '',
      category: '',
      test_item: '',
      publish_date: '',
      implement_date: '',
      status: 'active',
      file_url: '',
      summary: '',
      remark: ''
    })
    fetchMethods()
  } finally {
    methodSubmitLoading.value = false
  }
}

const handleLimitSave = async () => {
  limitSubmitLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    Message.success('保存成功')
    showLimitModal.value = false
    Object.assign(limitForm, {
      standard_no: '',
      name: '',
      type: '',
      category: '',
      limit_items: [],
      publish_date: '',
      implement_date: '',
      remark: ''
    })
    fetchLimits()
  } finally {
    limitSubmitLoading.value = false
  }
}

onMounted(() => {
  fetchMethods()
  fetchLimits()
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
