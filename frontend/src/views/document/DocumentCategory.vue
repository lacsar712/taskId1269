<template>
  <div class="page-container">
    <div class="page-header">
      <h2>文档分类管理</h2>
      <p>分类体系配置 / 权限控制 / 标签管理</p>
    </div>
    
    <div class="table-operations">
      <a-space>
        <a-input-search v-model="keyword" placeholder="搜索分类名称" style="width: 240px;" @search="fetchData" />
        <a-select v-model="status" placeholder="状态筛选" style="width: 120px;" allow-clear>
          <a-option value="active">启用</a-option>
          <a-option value="inactive">停用</a-option>
        </a-select>
      </a-space>
      <a-button type="primary" @click="handleAdd">
        <template #icon><icon-plus /></template>
        新增分类
      </a-button>
    </div>
    
    <a-table :columns="columns" :data="categories" :loading="loading" :pagination="pagination">
      <template #status="{ record }">
        <a-tag :color="record.status === 'active' ? 'green' : 'gray'">
          {{ record.status === 'active' ? '启用' : '停用' }}
        </a-tag>
      </template>
      <template #operations="{ record }">
        <a-space>
          <a-button type="text" size="small" @click="handleEdit(record)">编辑</a-button>
          <a-button type="text" size="small" @click="handleManageTags(record)">标签管理</a-button>
          <a-button type="text" size="small" @click="handleManagePermission(record)">权限设置</a-button>
          
        </a-space>
      </template>
    </a-table>
    
    <!-- 新增/编辑弹窗 -->
    <a-modal 
      v-model:visible="showModal" 
      :title="editing ? '编辑分类' : '新增分类'" 
      @ok="handleSubmit" 
      :ok-loading="submitLoading"
      width="600px"
    >
      <a-form :model="form" layout="vertical" ref="formRef">
        <a-form-item label="分类名称" field="name" required>
          <a-input v-model="form.name" placeholder="请输入分类名称" />
        </a-form-item>
        <a-form-item label="父级分类" field="parent_id">
          <a-tree-select 
            v-model="form.parent_id" 
            :data="categoryTree" 
            placeholder="请选择父级分类"
            allow-clear
          />
        </a-form-item>
        <a-form-item label="分类编码" field="code" required>
          <a-input v-model="form.code" placeholder="请输入分类编码" />
        </a-form-item>
        <a-form-item label="排序" field="sort">
          <a-input-number v-model="form.sort" :min="0" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="状态" field="status">
          <a-radio-group v-model="form.status">
            <a-radio value="active">启用</a-radio>
            <a-radio value="inactive">停用</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="描述" field="description">
          <a-textarea v-model="form.description" :max-length="500" show-word-limit />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 标签管理弹窗 -->
    <a-modal v-model:visible="showTagModal" title="标签管理" width="500px">
      <a-form layout="vertical">
        <a-form-item label="标签列表">
          <a-space wrap>
            <a-tag v-for="tag in currentTags" :key="tag" closable @close="removeTag(tag)">
              {{ tag }}
            </a-tag>
            <a-input 
              v-if="tagInputVisible" 
              v-model="tagInputValue" 
              size="small" 
              style="width: 100px;"
              @blur="handleTagInputConfirm"
              @keyup.enter="handleTagInputConfirm"
            />
            <a-tag v-else @click="showTagInput" style="cursor: pointer;">
              <template #icon><icon-plus /></template>
              新增标签
            </a-tag>
          </a-space>
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 权限设置弹窗 -->
    <a-modal v-model:visible="showPermissionModal" title="权限设置" width="600px">
      <a-form layout="vertical">
        <a-form-item label="可见范围">
          <a-checkbox-group v-model="permissionForm.visible_scope">
            <a-checkbox value="all">全部用户</a-checkbox>
            <a-checkbox value="department">本部门</a-checkbox>
            <a-checkbox value="role">指定角色</a-checkbox>
            <a-checkbox value="user">指定用户</a-checkbox>
          </a-checkbox-group>
        </a-form-item>
        <a-form-item label="操作权限">
          <a-checkbox-group v-model="permissionForm.operations">
            <a-checkbox value="view">查看</a-checkbox>
            <a-checkbox value="download">下载</a-checkbox>
            <a-checkbox value="upload">上传</a-checkbox>
            <a-checkbox value="edit">编辑</a-checkbox>
            <a-checkbox value="delete">删除</a-checkbox>
          </a-checkbox-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const submitLoading = ref(false)
const showModal = ref(false)
const showTagModal = ref(false)
const showPermissionModal = ref(false)
const editing = ref<any>(null)
const keyword = ref('')
const status = ref('')
const categories = ref<any[]>([])
const categoryTree = ref<any[]>([])
const currentTags = ref<string[]>([])
const tagInputVisible = ref(false)
const tagInputValue = ref('')
const formRef = ref()
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const form = reactive({
  name: '',
  parent_id: null,
  code: '',
  sort: 0,
  status: 'active',
  description: ''
})

const permissionForm = reactive({
  visible_scope: ['all'],
  operations: ['view', 'download']
})

const columns = [
  { title: '分类编码', dataIndex: 'code', width: 120 },
  { title: '分类名称', dataIndex: 'name' },
  { title: '父级分类', dataIndex: 'parent_name', width: 120 },
  { title: '排序', dataIndex: 'sort', width: 80 },
  { title: '文档数量', dataIndex: 'document_count', width: 100 },
  { title: '状态', slotName: 'status', width: 90 },
  { title: '操作', slotName: 'operations', width: 280 }
]

const fetchData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    categories.value = [
      { id: 1, code: 'CAT001', name: '技术文档', parent_id: null, parent_name: '-', sort: 1, document_count: 45, status: 'active' },
      { id: 2, code: 'CAT002', name: '管理文档', parent_id: null, parent_name: '-', sort: 2, document_count: 32, status: 'active' },
      { id: 3, code: 'CAT003', name: '操作手册', parent_id: 1, parent_name: '技术文档', sort: 1, document_count: 18, status: 'active' },
      { id: 4, code: 'CAT004', name: '安全规范', parent_id: 2, parent_name: '管理文档', sort: 1, document_count: 12, status: 'active' },
      { id: 5, code: 'CAT005', name: '培训资料', parent_id: null, parent_name: '-', sort: 3, document_count: 28, status: 'active' }
    ]
    pagination.total = categories.value.length
  } finally {
    loading.value = false
  }
}

const buildCategoryTree = () => {
  categoryTree.value = [
    { key: null, title: '根分类', value: null },
    { key: 1, title: '技术文档', value: 1 },
    { key: 2, title: '管理文档', value: 2 },
    { key: 3, title: '培训资料', value: 5 }
  ]
}

const handleAdd = () => {
  editing.value = null
  Object.assign(form, {
    name: '',
    parent_id: null,
    code: '',
    sort: 0,
    status: 'active',
    description: ''
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

const handleDelete = (record: any) => {
  Message.info(`删除分类: ${record.name}`)
}

const handleManageTags = (record: any) => {
  currentTags.value = ['重要', '常用', '技术']
  showTagModal.value = true
}

const handleManagePermission = (record: any) => {
  showPermissionModal.value = true
}

const showTagInput = () => {
  tagInputVisible.value = true
}

const handleTagInputConfirm = () => {
  if (tagInputValue.value && !currentTags.value.includes(tagInputValue.value)) {
    currentTags.value.push(tagInputValue.value)
  }
  tagInputVisible.value = false
  tagInputValue.value = ''
}

const removeTag = (tag: string) => {
  currentTags.value = currentTags.value.filter(t => t !== tag)
}

onMounted(() => {
  fetchData()
  buildCategoryTree()
})
</script>

<style scoped>
.table-operations {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}
</style>
