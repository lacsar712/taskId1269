<template>
  <div class="page-container">
    <div class="page-header">
      <h2>角色权限管理</h2>
      <p>角色配置 / 权限分配 / 权限继承</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="角色配置">
        <a-card>
          <template #title>
            <a-space>
              <span>角色列表</span>
              <a-button type="primary" @click="showRoleModal = true">
                <template #icon><icon-plus /></template>
                新增角色
              </a-button>
            </a-space>
          </template>
          
          <a-table
            :columns="roleColumns"
            :data="roles"
            :pagination="pagination"
            :loading="loading"
          >
            <template #status="{ record }">
              <a-tag :color="record.status === '启用' ? 'green' : 'red'">{{ record.status }}</a-tag>
            </template>
            <template #userCount="{ record }">
              <a-link @click="viewRoleUsers(record)">{{ record.userCount }}人</a-link>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="editRole(record)">编辑</a-button>
                <a-button type="text" size="small" @click="configPermissions(record)">权限配置</a-button>
                <a-popconfirm content="确定要删除该角色吗？" @ok="deleteRole(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="权限分配">
        <a-card>
          <a-row :gutter="16">
            <a-col :span="6">
              <a-card title="角色列表" size="small">
                <a-list :data="roles" size="small">
                  <template #item="{ item }">
                    <a-list-item 
                      :class="{ 'selected': selectedRole?.id === item.id }"
                      @click="selectRole(item)"
                      style="cursor: pointer;"
                    >
                      <a-list-item-meta>
                        <template #title>
                          <a-space>
                            <span>{{ item.name }}</span>
                            <a-tag :color="item.status === '启用' ? 'green' : 'red'" size="small">{{ item.status }}</a-tag>
                          </a-space>
                        </template>
                      </a-list-item-meta>
                    </a-list-item>
                  </template>
                </a-list>
              </a-card>
            </a-col>
            <a-col :span="18">
              <a-card :title="selectedRole ? `权限配置 - ${selectedRole.name}` : '请选择角色'">
                <a-tree
                  v-if="selectedRole"
                  v-model:checked-keys="checkedKeys"
                  :tree-data="permissionTree"
                  checkable
                  :check-strictly="false"
                  @check="handlePermissionCheck"
                >
                  <template #title="{ data }">
                    <a-space>
                      <span>{{ data.title }}</span>
                      <a-tag v-if="data.type" size="small">{{ data.type }}</a-tag>
                    </a-space>
                  </template>
                </a-tree>
                <a-empty v-else description="请从左侧选择一个角色" />
                
                <template v-if="selectedRole" #extra>
                  <a-button type="primary" @click="savePermissions">保存权限</a-button>
                </template>
              </a-card>
            </a-col>
          </a-row>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="权限继承">
        <a-card>
          <a-alert message="权限继承说明" type="info" style="margin-bottom: 20px;">
            <template #description>
              子角色可以继承父角色的权限，当父角色权限变更时，子角色会自动继承新的权限。
            </template>
          </a-alert>
          
          <a-table
            :columns="inheritColumns"
            :data="inheritRelations"
            :pagination="false"
          >
            <template #parentRole="{ record }">
              <a-tag color="blue">{{ record.parentRole }}</a-tag>
            </template>
            <template #childRole="{ record }">
              <a-tag color="green">{{ record.childRole }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="viewInheritPermissions(record)">查看继承权限</a-button>
                <a-button type="text" size="small" status="danger" @click="removeInherit(record)">取消继承</a-button>
              </a-space>
            </template>
          </a-table>
          
          <a-divider />
          
          <a-form layout="inline">
            <a-form-item label="父角色" required>
              <a-select v-model="inheritForm.parentRole" placeholder="请选择父角色" style="width: 200px;">
                <a-option v-for="role in roles" :key="role.name" :value="role.name">{{ role.name }}</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="子角色" required>
              <a-select v-model="inheritForm.childRole" placeholder="请选择子角色" style="width: 200px;">
                <a-option v-for="role in roles" :key="role.name" :value="role.name">{{ role.name }}</a-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="addInherit">建立继承关系</a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 新增/编辑角色弹窗 -->
    <a-modal
      v-model:visible="showRoleModal"
      :title="editingRole ? '编辑角色' : '新增角色'"
      @ok="saveRole"
      :ok-loading="saveLoading"
    >
      <a-form :model="roleForm" layout="vertical">
        <a-form-item label="角色名称" required>
          <a-input v-model="roleForm.name" placeholder="请输入角色名称" />
        </a-form-item>
        <a-form-item label="角色编码" required>
          <a-input v-model="roleForm.code" placeholder="请输入角色编码" />
        </a-form-item>
        <a-form-item label="角色描述">
          <a-textarea v-model="roleForm.description" :auto-size="{ minRows: 3 }" />
        </a-form-item>
        <a-form-item label="状态">
          <a-radio-group v-model="roleForm.status">
            <a-radio value="启用">启用</a-radio>
            <a-radio value="禁用">禁用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 角色用户弹窗 -->
    <a-modal
      v-model:visible="showUsersModal"
      :title="`角色用户 - ${selectedRole?.name}`"
      :footer="false"
    >
      <a-table
        :columns="userColumns"
        :data="roleUsers"
        :pagination="false"
        size="small"
      />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const saveLoading = ref(false)
const showRoleModal = ref(false)
const showUsersModal = ref(false)
const editingRole = ref<any>(null)
const selectedRole = ref<any>(null)
const checkedKeys = ref<string[]>([])

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const roles = ref([
  { id: 1, name: '管理员', code: 'ADMIN', description: '系统管理员，拥有所有权限', status: '启用', userCount: 2 },
  { id: 2, name: '操作员', code: 'OPERATOR', description: '生产操作员，负责日常运行操作', status: '启用', userCount: 8 },
  { id: 3, name: '维护员', code: 'MAINTAINER', description: '设备维护员，负责设备维护保养', status: '启用', userCount: 5 },
  { id: 4, name: '查看者', code: 'VIEWER', description: '只读用户，只能查看数据', status: '启用', userCount: 3 }
])

const inheritRelations = ref([
  { id: 1, parentRole: '管理员', childRole: '操作员', createTime: '2025-01-01' },
  { id: 2, parentRole: '操作员', childRole: '查看者', createTime: '2025-01-15' }
])

const roleUsers = ref([
  { id: 1, username: 'admin', realName: '管理员', department: '信息部' },
  { id: 2, username: 'admin2', realName: '管理员2', department: '信息部' }
])

const permissionTree = ref([
  {
    key: 'dashboard',
    title: '仪表盘',
    type: '菜单',
    children: [
      { key: 'dashboard:view', title: '查看', type: '权限' }
    ]
  },
  {
    key: 'production',
    title: '生产管理',
    type: '菜单',
    children: [
      { key: 'production:view', title: '查看', type: '权限' },
      { key: 'production:edit', title: '编辑', type: '权限' },
      { key: 'production:delete', title: '删除', type: '权限' }
    ]
  },
  {
    key: 'equipment',
    title: '设备管理',
    type: '菜单',
    children: [
      { key: 'equipment:view', title: '查看', type: '权限' },
      { key: 'equipment:edit', title: '编辑', type: '权限' },
      { key: 'equipment:maintain', title: '维护', type: '权限' }
    ]
  },
  {
    key: 'safety',
    title: '安全管理',
    type: '菜单',
    children: [
      { key: 'safety:view', title: '查看', type: '权限' },
      { key: 'safety:edit', title: '编辑', type: '权限' }
    ]
  },
  {
    key: 'system',
    title: '系统管理',
    type: '菜单',
    children: [
      { key: 'system:view', title: '查看', type: '权限' },
      { key: 'system:user', title: '用户管理', type: '权限' },
      { key: 'system:role', title: '角色管理', type: '权限' },
      { key: 'system:config', title: '系统配置', type: '权限' }
    ]
  }
])

const roleForm = reactive({
  name: '',
  code: '',
  description: '',
  status: '启用'
})

const inheritForm = reactive({
  parentRole: '',
  childRole: ''
})

const roleColumns = [
  { title: '角色名称', dataIndex: 'name', width: 150 },
  { title: '角色编码', dataIndex: 'code', width: 150 },
  { title: '角色描述', dataIndex: 'description', ellipsis: true },
  { title: '用户数', slotName: 'userCount', width: 100 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 250 }
]

const inheritColumns = [
  { title: '父角色', slotName: 'parentRole', width: 150 },
  { title: '子角色', slotName: 'childRole', width: 150 },
  { title: '建立时间', dataIndex: 'createTime', width: 120 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const userColumns = [
  { title: '用户名', dataIndex: 'username', width: 120 },
  { title: '真实姓名', dataIndex: 'realName', width: 120 },
  { title: '部门', dataIndex: 'department', width: 120 }
]

const editRole = (record: any) => {
  editingRole.value = record
  Object.assign(roleForm, record)
  showRoleModal.value = true
}

const deleteRole = (record: any) => {
  const index = roles.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    roles.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const saveRole = async () => {
  if (!roleForm.name || !roleForm.code) {
    Message.warning('请填写完整信息')
    return
  }
  
  saveLoading.value = true
  setTimeout(() => {
    if (editingRole.value) {
      const index = roles.value.findIndex(item => item.id === editingRole.value.id)
      if (index > -1) {
        Object.assign(roles.value[index], roleForm)
      }
      Message.success('编辑成功')
    } else {
      roles.value.push({
        id: Date.now(),
        ...roleForm,
        userCount: 0
      })
      Message.success('新增成功')
    }
    saveLoading.value = false
    showRoleModal.value = false
    editingRole.value = null
    Object.assign(roleForm, { name: '', code: '', description: '', status: '启用' })
  }, 500)
}

const selectRole = (role: any) => {
  selectedRole.value = role
  // 加载角色的权限
  checkedKeys.value = ['dashboard:view', 'production:view', 'equipment:view']
}

const handlePermissionCheck = (checked: string[]) => {
  checkedKeys.value = checked
}

const savePermissions = () => {
  Message.success(`角色"${selectedRole.value.name}"的权限已保存`)
}

const viewRoleUsers = (record: any) => {
  selectedRole.value = record
  showUsersModal.value = true
}

const viewInheritPermissions = (record: any) => {
  Message.info(`查看继承权限：${record.parentRole} -> ${record.childRole}`)
}

const removeInherit = (record: any) => {
  const index = inheritRelations.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    inheritRelations.value.splice(index, 1)
    Message.success('取消继承成功')
  }
}

const addInherit = () => {
  if (!inheritForm.parentRole || !inheritForm.childRole) {
    Message.warning('请选择父角色和子角色')
    return
  }
  
  if (inheritForm.parentRole === inheritForm.childRole) {
    Message.warning('父角色和子角色不能相同')
    return
  }
  
  inheritRelations.value.push({
    id: Date.now(),
    ...inheritForm,
    createTime: new Date().toLocaleDateString()
  })
  Message.success('建立继承关系成功')
  Object.assign(inheritForm, { parentRole: '', childRole: '' })
}

// 初始化分页
pagination.total = roles.value.length
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 8px;
}

.page-header p {
  font-size: 14px;
  color: #86909c;
}

.selected {
  background-color: #e8f3ff;
}
</style>
