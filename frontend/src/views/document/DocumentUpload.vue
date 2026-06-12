<template>
  <div class="page-container">
    <div class="page-header">
      <h2>文档上传管理</h2>
      <p>文档上传 / 版本控制 / 文档审核</p>
    </div>
    
    <div class="table-operations">
      <a-space>
        <a-input-search v-model="keyword" placeholder="搜索文档名称" style="width: 240px;" @search="fetchData" />
        <a-select v-model="categoryId" placeholder="文档分类" style="width: 140px;" allow-clear>
          <a-option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</a-option>
        </a-select>
        <a-select v-model="status" placeholder="审核状态" style="width: 120px;" allow-clear>
          <a-option value="pending">待审核</a-option>
          <a-option value="approved">已通过</a-option>
          <a-option value="rejected">已拒绝</a-option>
        </a-select>
      </a-space>
      <a-button type="primary" @click="showUploadModal = true">
        <template #icon><icon-upload /></template>
        上传文档
      </a-button>
    </div>
    
    <a-table :columns="columns" :data="documents" :loading="loading" :pagination="pagination">
      <template #status="{ record }">
        <a-tag :color="getStatusColor(record.status)">
          {{ getStatusText(record.status) }}
        </a-tag>
      </template>
      <template #version="{ record }">
        <a-space>
          <span>v{{ record.version }}</span>
          <a-button type="text" size="mini" @click="handleViewVersions(record)">历史版本</a-button>
        </a-space>
      </template>
      <template #operations="{ record }">
        <a-space>
          <a-button type="text" size="small" @click="handleEdit(record)">编辑</a-button>
          <a-button type="text" size="small" @click="handleUploadNewVersion(record)">上传新版本</a-button>
          <a-button type="text" size="small" v-if="record.status === 'pending'" @click="handleReview(record)">审核</a-button>
        </a-space>
      </template>
    </a-table>
    
    <!-- 上传文档弹窗 -->
    <a-modal 
      v-model:visible="showUploadModal" 
      title="上传文档" 
      @ok="handleUpload" 
      :ok-loading="uploadLoading"
      width="600px"
    >
      <a-form :model="uploadForm" layout="vertical" ref="uploadFormRef">
        <a-form-item label="文档名称" field="name" required>
          <a-input v-model="uploadForm.name" placeholder="请输入文档名称" />
        </a-form-item>
        <a-form-item label="文档分类" field="category_id" required>
          <a-select v-model="uploadForm.category_id" placeholder="请选择分类">
            <a-option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="文件上传" field="file" required>
          <a-upload
            :auto-upload="false"
            :file-list="fileList"
            @change="handleFileChange"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx"
          >
            <template #upload-button>
              <a-button>
                <template #icon><icon-upload /></template>
                选择文件
              </a-button>
            </template>
          </a-upload>
        </a-form-item>
        <a-form-item label="版本号" field="version">
          <a-input v-model="uploadForm.version" placeholder="如：1.0.0" />
        </a-form-item>
        <a-form-item label="文档描述" field="description">
          <a-textarea v-model="uploadForm.description" :max-length="500" show-word-limit />
        </a-form-item>
        <a-form-item label="标签" field="tags">
          <a-input v-model="uploadForm.tags" placeholder="多个标签用逗号分隔" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 编辑文档弹窗 -->
    <a-modal 
      v-model:visible="showEditModal" 
      title="编辑文档" 
      @ok="handleUpdate" 
      :ok-loading="submitLoading"
      width="600px"
    >
      <a-form :model="editForm" layout="vertical" ref="editFormRef">
        <a-form-item label="文档名称" field="name" required>
          <a-input v-model="editForm.name" />
        </a-form-item>
        <a-form-item label="文档分类" field="category_id" required>
          <a-select v-model="editForm.category_id">
            <a-option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="文档描述" field="description">
          <a-textarea v-model="editForm.description" :max-length="500" show-word-limit />
        </a-form-item>
        <a-form-item label="标签" field="tags">
          <a-input v-model="editForm.tags" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 版本历史弹窗 -->
    <a-modal v-model:visible="showVersionModal" title="版本历史" width="700px">
      <a-table :columns="versionColumns" :data="versions" :pagination="false">
      </a-table>
    </a-modal>
    
    <!-- 审核弹窗 -->
    <a-modal v-model:visible="showReviewModal" title="文档审核" width="500px" @ok="handleReviewSubmit">
      <a-form :model="reviewForm" layout="vertical">
        <a-form-item label="审核结果" required>
          <a-radio-group v-model="reviewForm.result">
            <a-radio value="approved">通过</a-radio>
            <a-radio value="rejected">拒绝</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="审核意见">
          <a-textarea v-model="reviewForm.comment" :max-length="500" show-word-limit />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const uploadLoading = ref(false)
const submitLoading = ref(false)
const showUploadModal = ref(false)
const showEditModal = ref(false)
const showVersionModal = ref(false)
const showReviewModal = ref(false)
const keyword = ref('')
const categoryId = ref('')
const status = ref('')
const categories = ref<any[]>([])
const documents = ref<any[]>([])
const versions = ref<any[]>([])
const fileList = ref<any[]>([])
const editing = ref<any>(null)
const reviewing = ref<any>(null)
const uploadFormRef = ref()
const editFormRef = ref()
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const uploadForm = reactive({
  name: '',
  category_id: null,
  version: '1.0.0',
  description: '',
  tags: ''
})

const editForm = reactive({
  name: '',
  category_id: null,
  description: '',
  tags: ''
})

const reviewForm = reactive({
  result: 'approved',
  comment: ''
})

const columns = [
  { title: '文档编号', dataIndex: 'doc_no', width: 140 },
  { title: '文档名称', dataIndex: 'name' },
  { title: '分类', dataIndex: 'category_name', width: 120 },
  { title: '版本', slotName: 'version', width: 120 },
  { title: '文件大小', dataIndex: 'file_size', width: 100 },
  { title: '上传人', dataIndex: 'uploader', width: 100 },
  { title: '上传时间', dataIndex: 'upload_time', width: 160 },
  { title: '审核状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 280 }
]

const versionColumns = [
  { title: '版本号', dataIndex: 'version', width: 100 },
  { title: '文件大小', dataIndex: 'file_size', width: 100 },
  { title: '上传人', dataIndex: 'uploader', width: 100 },
  { title: '上传时间', dataIndex: 'upload_time', width: 160 },
  { title: '更新说明', dataIndex: 'description' },
  { title: '操作', slotName: 'operations', width: 120 }
]

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
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[status] || '未知'
}

const fetchData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    documents.value = [
      { id: 1, doc_no: 'DOC20240115001', name: '设备操作手册.pdf', category_id: 3, category_name: '操作手册', version: '2.1', file_size: '2.5MB', uploader: '张三', upload_time: '2024-01-15 10:30', status: 'approved' },
      { id: 2, doc_no: 'DOC20240115002', name: '安全管理制度.docx', category_id: 4, category_name: '安全规范', version: '1.0', file_size: '1.2MB', uploader: '李四', upload_time: '2024-01-15 14:20', status: 'pending' },
      { id: 3, doc_no: 'DOC20240116001', name: '生产流程优化方案.xlsx', category_id: 1, category_name: '技术文档', version: '1.5', file_size: '3.8MB', uploader: '王五', upload_time: '2024-01-16 09:15', status: 'approved' },
      { id: 4, doc_no: 'DOC20240116002', name: '员工培训计划.pptx', category_id: 5, category_name: '培训资料', version: '1.0', file_size: '5.2MB', uploader: '赵六', upload_time: '2024-01-16 11:45', status: 'pending' }
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

const handleFileChange = (fileList: any[]) => {
  // 处理文件选择
}

const handleUpload = async () => {
  const valid = await uploadFormRef.value?.validate()
  if (!valid) return
  
  uploadLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    Message.success('上传成功')
    showUploadModal.value = false
    fetchData()
  } catch (e) {
    Message.error('上传失败')
  } finally {
    uploadLoading.value = false
  }
}

const handleEdit = (record: any) => {
  editing.value = record
  Object.assign(editForm, {
    name: record.name,
    category_id: record.category_id,
    description: '',
    tags: ''
  })
  showEditModal.value = true
}

const handleUpdate = async () => {
  const valid = await editFormRef.value?.validate()
  if (!valid) return
  
  submitLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    Message.success('更新成功')
    showEditModal.value = false
    fetchData()
  } catch (e) {
    Message.error('更新失败')
  } finally {
    submitLoading.value = false
  }
}

const handleUploadNewVersion = (record: any) => {
  editing.value = record
  Object.assign(uploadForm, {
    name: record.name,
    category_id: record.category_id,
    version: '',
    description: '',
    tags: ''
  })
  showUploadModal.value = true
}

const handleViewVersions = (record: any) => {
  versions.value = [
    { version: '2.1', file_size: '2.5MB', uploader: '张三', upload_time: '2024-01-15 10:30', description: '更新设备参数' },
    { version: '2.0', file_size: '2.3MB', uploader: '张三', upload_time: '2024-01-10 15:20', description: '初始版本' }
  ]
  showVersionModal.value = true
}

const handleReview = (record: any) => {
  reviewing.value = record
  Object.assign(reviewForm, {
    result: 'approved',
    comment: ''
  })
  showReviewModal.value = true
}

const handleReviewSubmit = async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    Message.success('审核完成')
    showReviewModal.value = false
    fetchData()
  } catch (e) {
    Message.error('审核失败')
  }
}

const handleDelete = (record: any) => {
  Message.info(`删除文档: ${record.name}`)
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
