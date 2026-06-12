<template>
  <div class="page-container">
    <div class="page-header">
      <h2>文档检索下载</h2>
      <p>精准检索 / 预览下载 / 收藏夹</p>
    </div>
    
    <div class="search-section">
      <a-card>
        <a-form layout="inline" :model="searchForm">
          <a-form-item label="关键词">
            <a-input v-model="searchForm.keyword" placeholder="请输入文档名称或内容关键词" style="width: 300px;" />
          </a-form-item>
          <a-form-item label="文档分类">
            <a-select v-model="searchForm.category_id" placeholder="全部" style="width: 150px;" allow-clear>
              <a-option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</a-option>
            </a-select>
          </a-form-item>
          <a-form-item label="文件类型">
            <a-select v-model="searchForm.file_type" placeholder="全部" style="width: 120px;" allow-clear>
              <a-option value="pdf">PDF</a-option>
              <a-option value="doc">Word</a-option>
              <a-option value="xls">Excel</a-option>
              <a-option value="ppt">PowerPoint</a-option>
            </a-select>
          </a-form-item>
          <a-form-item label="上传时间">
            <a-range-picker v-model="searchForm.date_range" style="width: 240px;" />
          </a-form-item>
          <a-form-item>
            <a-space>
              <a-button type="primary" @click="handleSearch">搜索</a-button>
              <a-button @click="handleReset">重置</a-button>
            </a-space>
          </a-form-item>
        </a-form>
      </a-card>
    </div>
    
    <a-tabs v-model:active-key="activeTab" class="content-tabs">
      <a-tab-pane key="search" title="搜索结果">
        <div class="table-operations">
          <a-space>
            <span>共找到 {{ pagination.total }} 条结果</span>
            <a-button type="text" @click="handleBatchDownload">批量下载</a-button>
          </a-space>
        </div>
        <a-table 
          :columns="columns" 
          :data="documents" 
          :loading="loading" 
          :pagination="pagination"
          :row-selection="rowSelection"
        >
          <template #preview="{ record }">
            <a-button type="text" size="small" @click="handlePreview(record)">预览</a-button>
          </template>
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" @click="handleAddToFavorites(record)">
                <template #icon><icon-star /></template>
                收藏
              </a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="favorites" title="我的收藏">
        <a-table :columns="favoriteColumns" :data="favorites" :loading="favoriteLoading">
          <template #operations="{ record }">
            <a-space>
              <a-button type="text" size="small" @click="handlePreview(record)">预览</a-button>
              <a-button type="text" size="small" status="danger" @click="handleRemoveFavorite(record)">取消收藏</a-button>
            </a-space>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 预览弹窗 -->
    <a-modal v-model:visible="showPreviewModal" title="文档预览" width="90%" :footer="false">
      <div class="preview-container">
        <iframe :src="previewUrl" style="width: 100%; height: 600px; border: none;"></iframe>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const favoriteLoading = ref(false)
const showPreviewModal = ref(false)
const activeTab = ref('search')
const keyword = ref('')
const categories = ref<any[]>([])
const documents = ref<any[]>([])
const favorites = ref<any[]>([])
const selectedRows = ref<any[]>([])
const previewUrl = ref('')
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const searchForm = reactive({
  keyword: '',
  category_id: null,
  file_type: '',
  date_range: []
})

const rowSelection = reactive({
  type: 'checkbox',
  showCheckedAll: true,
  selectedRowKeys: [],
  onSelect: (row: any, selected: boolean) => {
    if (selected) {
      selectedRows.value.push(row)
    } else {
      selectedRows.value = selectedRows.value.filter(r => r.id !== row.id)
    }
  },
  onSelectAll: (selected: boolean) => {
    if (selected) {
      selectedRows.value = [...documents.value]
    } else {
      selectedRows.value = []
    }
  }
})

const columns = [
  { title: '文档名称', dataIndex: 'name' },
  { title: '分类', dataIndex: 'category_name', width: 120 },
  { title: '文件类型', dataIndex: 'file_type', width: 100 },
  { title: '文件大小', dataIndex: 'file_size', width: 100 },
  { title: '版本', dataIndex: 'version', width: 80 },
  { title: '上传人', dataIndex: 'uploader', width: 100 },
  { title: '上传时间', dataIndex: 'upload_time', width: 160 },
  { title: '下载次数', dataIndex: 'download_count', width: 100 },
  { title: '预览', slotName: 'preview', width: 80 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const favoriteColumns = [
  { title: '文档名称', dataIndex: 'name' },
  { title: '分类', dataIndex: 'category_name', width: 120 },
  { title: '文件类型', dataIndex: 'file_type', width: 100 },
  { title: '收藏时间', dataIndex: 'favorite_time', width: 160 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const fetchData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    documents.value = [
      { id: 1, name: '设备操作手册.pdf', category_id: 3, category_name: '操作手册', file_type: 'PDF', file_size: '2.5MB', version: '2.1', uploader: '张三', upload_time: '2024-01-15 10:30', download_count: 45 },
      { id: 2, name: '安全管理制度.docx', category_id: 4, category_name: '安全规范', file_type: 'Word', file_size: '1.2MB', version: '1.0', uploader: '李四', upload_time: '2024-01-15 14:20', download_count: 32 },
      { id: 3, name: '生产流程优化方案.xlsx', category_id: 1, category_name: '技术文档', file_type: 'Excel', file_size: '3.8MB', version: '1.5', uploader: '王五', upload_time: '2024-01-16 09:15', download_count: 28 },
      { id: 4, name: '员工培训计划.pptx', category_id: 5, category_name: '培训资料', file_type: 'PowerPoint', file_size: '5.2MB', version: '1.0', uploader: '赵六', upload_time: '2024-01-16 11:45', download_count: 15 }
    ]
    pagination.total = documents.value.length
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  categories.value = [
    { id: 1, name: '技术文档' },
    { id: 2, name: '管理文档' },
    { id: 3, name: '操作手册' },
    { id: 4, name: '安全规范' },
    { id: 5, name: '培训资料' }
  ]
}

const fetchFavorites = async () => {
  favoriteLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 300))
    favorites.value = [
      { id: 1, name: '设备操作手册.pdf', category_name: '操作手册', file_type: 'PDF', favorite_time: '2024-01-15 11:00' },
      { id: 3, name: '生产流程优化方案.xlsx', category_name: '技术文档', file_type: 'Excel', favorite_time: '2024-01-16 10:00' }
    ]
  } finally {
    favoriteLoading.value = false
  }
}

const handleSearch = () => {
  fetchData()
}

const handleReset = () => {
  Object.assign(searchForm, {
    keyword: '',
    category_id: null,
    file_type: '',
    date_range: []
  })
  fetchData()
}

const handlePreview = (record: any) => {
  previewUrl.value = `/api/documents/${record.id}/preview`
  showPreviewModal.value = true
}

const handleDownload = (record: any) => {
  Message.success(`开始下载: ${record.name}`)
}

const handleBatchDownload = () => {
  if (selectedRows.value.length === 0) {
    Message.warning('请选择要下载的文档')
    return
  }
  Message.success(`开始批量下载 ${selectedRows.value.length} 个文档`)
}

const handleAddToFavorites = (record: any) => {
  Message.success(`已添加到收藏: ${record.name}`)
  fetchFavorites()
}

const handleRemoveFavorite = (record: any) => {
  Message.success(`已取消收藏: ${record.name}`)
  favorites.value = favorites.value.filter(f => f.id !== record.id)
}

onMounted(() => {
  fetchData()
  fetchCategories()
  fetchFavorites()
})
</script>

<style scoped>
.search-section {
  margin-bottom: 16px;
}

.content-tabs {
  margin-top: 16px;
}

.table-operations {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.preview-container {
  width: 100%;
  height: 600px;
}
</style>
