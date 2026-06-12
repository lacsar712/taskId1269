<template>
  <div class="page-container">
    <div class="page-header">
      <h2>用户管理</h2>
      <p>账号管理 / 信息维护 / 登录日志</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="账号管理">
        <a-card>
          <template #title>
            <a-space>
              <span>用户列表</span>
              <a-button type="primary" @click="showUserModal = true">
                <template #icon><icon-plus /></template>
                新增用户
              </a-button>
            </a-space>
          </template>
          
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="用户名">
              <a-input v-model="searchForm.username" placeholder="请输入用户名" allow-clear style="width: 200px;" />
            </a-form-item>
            <a-form-item label="状态">
              <a-select v-model="searchForm.status" placeholder="请选择状态" allow-clear style="width: 150px;">
                <a-option value="启用">启用</a-option>
                <a-option value="禁用">禁用</a-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="loadUsers">查询</a-button>
              <a-button style="margin-left: 8px;" @click="resetSearch">重置</a-button>
            </a-form-item>
          </a-form>
          
          <a-table
            :columns="userColumns"
            :data="users"
            :pagination="pagination"
            :loading="loading"
          >
            <template #avatar="{ record }">
              <a-avatar :size="32">{{ record.username.charAt(0) }}</a-avatar>
            </template>
            <template #status="{ record }">
              <a-tag :color="record.status === '启用' ? 'green' : 'red'">{{ record.status }}</a-tag>
            </template>
            <template #role="{ record }">
              <a-tag v-for="role in record.roles" :key="role" style="margin-right: 4px;">{{ role }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="editUser(record)">编辑</a-button>
                <a-button type="text" size="small" @click="resetPassword(record)">重置密码</a-button>
                <a-button type="text" size="small" @click="toggleStatus(record)">
                  {{ record.status === '启用' ? '禁用' : '启用' }}
                </a-button>
                <a-popconfirm content="确定要删除该用户吗？" @ok="deleteUser(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="信息维护">
        <a-card>
          <a-descriptions title="个人信息" :column="2" bordered>
            <a-descriptions-item label="用户名">admin</a-descriptions-item>
            <a-descriptions-item label="真实姓名">管理员</a-descriptions-item>
            <a-descriptions-item label="手机号">138****8888</a-descriptions-item>
            <a-descriptions-item label="邮箱">admin@example.com</a-descriptions-item>
            <a-descriptions-item label="部门">信息部</a-descriptions-item>
            <a-descriptions-item label="职位">系统管理员</a-descriptions-item>
            <a-descriptions-item label="创建时间">2025-01-01 08:00:00</a-descriptions-item>
            <a-descriptions-item label="最后登录">2026-02-04 10:30:00</a-descriptions-item>
          </a-descriptions>
          
          <a-divider />
          
          <a-form :model="infoForm" layout="vertical" style="max-width: 600px;">
            <a-form-item label="真实姓名">
              <a-input v-model="infoForm.realName" />
            </a-form-item>
            <a-form-item label="手机号">
              <a-input v-model="infoForm.phone" />
            </a-form-item>
            <a-form-item label="邮箱">
              <a-input v-model="infoForm.email" />
            </a-form-item>
            <a-form-item label="部门">
              <a-input v-model="infoForm.department" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="updateInfo">保存</a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="登录日志">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="用户名">
              <a-input v-model="logSearchForm.username" placeholder="请输入用户名" allow-clear style="width: 200px;" />
            </a-form-item>
            <a-form-item label="登录时间">
              <a-range-picker v-model="logSearchForm.dateRange" style="width: 300px;" />
            </a-form-item>
            <a-form-item label="登录状态">
              <a-select v-model="logSearchForm.status" placeholder="请选择状态" allow-clear style="width: 150px;">
                <a-option value="成功">成功</a-option>
                <a-option value="失败">失败</a-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="loadLogs">查询</a-button>
            </a-form-item>
          </a-form>
          
          <a-table
            :columns="logColumns"
            :data="loginLogs"
            :pagination="logPagination"
          >
            <template #status="{ record }">
              <a-tag :color="record.status === '成功' ? 'green' : 'red'">{{ record.status }}</a-tag>
            </template>
            <template #ip="{ record }">
              <a-tag>{{ record.ip }}</a-tag>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 新增/编辑用户弹窗 -->
    <a-modal
      v-model:visible="showUserModal"
      :title="editingUser ? '编辑用户' : '新增用户'"
      @ok="saveUser"
      :ok-loading="saveLoading"
      width="600px"
    >
      <a-form :model="userForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="用户名" required>
              <a-input v-model="userForm.username" placeholder="请输入用户名" :disabled="!!editingUser" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="真实姓名" required>
              <a-input v-model="userForm.realName" placeholder="请输入真实姓名" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="密码" :required="!editingUser">
              <a-input-password v-model="userForm.password" placeholder="请输入密码" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="手机号">
              <a-input v-model="userForm.phone" placeholder="请输入手机号" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="邮箱">
              <a-input v-model="userForm.email" placeholder="请输入邮箱" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="部门">
              <a-input v-model="userForm.department" placeholder="请输入部门" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="角色" required>
          <a-select v-model="userForm.roles" multiple placeholder="请选择角色">
            <a-option value="管理员">管理员</a-option>
            <a-option value="操作员">操作员</a-option>
            <a-option value="维护员">维护员</a-option>
            <a-option value="查看者">查看者</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-radio-group v-model="userForm.status">
            <a-radio value="启用">启用</a-radio>
            <a-radio value="禁用">禁用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const saveLoading = ref(false)
const showUserModal = ref(false)
const editingUser = ref<any>(null)

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const logPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const searchForm = reactive({
  username: '',
  status: ''
})

const logSearchForm = reactive({
  username: '',
  dateRange: [],
  status: ''
})

const users = ref([
  { id: 1, username: 'admin', realName: '管理员', phone: '138****8888', email: 'admin@example.com', department: '信息部', roles: ['管理员'], status: '启用', createTime: '2025-01-01 08:00:00' },
  { id: 2, username: 'operator1', realName: '操作员1', phone: '139****9999', email: 'op1@example.com', department: '运行部', roles: ['操作员'], status: '启用', createTime: '2025-01-15 09:00:00' },
  { id: 3, username: 'maintainer1', realName: '维护员1', phone: '137****7777', email: 'm1@example.com', department: '维修部', roles: ['维护员'], status: '启用', createTime: '2025-02-01 10:00:00' },
  { id: 4, username: 'viewer1', realName: '查看者1', phone: '136****6666', email: 'v1@example.com', department: '管理部', roles: ['查看者'], status: '禁用', createTime: '2025-02-10 11:00:00' }
])

const loginLogs = ref([
  { id: 1, username: 'admin', ip: '192.168.1.100', location: 'XX市', status: '成功', loginTime: '2026-02-04 10:30:00' },
  { id: 2, username: 'operator1', ip: '192.168.1.101', location: 'XX市', status: '成功', loginTime: '2026-02-04 09:15:00' },
  { id: 3, username: 'viewer1', ip: '192.168.1.102', location: 'XX市', status: '失败', loginTime: '2026-02-04 08:45:00', reason: '密码错误' },
  { id: 4, username: 'maintainer1', ip: '192.168.1.103', location: 'XX市', status: '成功', loginTime: '2026-02-03 16:20:00' }
])

const infoForm = reactive({
  realName: '管理员',
  phone: '138****8888',
  email: 'admin@example.com',
  department: '信息部'
})

const userForm = reactive({
  username: '',
  realName: '',
  password: '',
  phone: '',
  email: '',
  department: '',
  roles: [],
  status: '启用'
})

const userColumns = [
  { title: '头像', slotName: 'avatar', width: 80 },
  { title: '用户名', dataIndex: 'username', width: 120 },
  { title: '真实姓名', dataIndex: 'realName', width: 120 },
  { title: '手机号', dataIndex: 'phone', width: 120 },
  { title: '邮箱', dataIndex: 'email', width: 180 },
  { title: '部门', dataIndex: 'department', width: 120 },
  { title: '角色', slotName: 'role', width: 150 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '创建时间', dataIndex: 'createTime', width: 180 },
  { title: '操作', slotName: 'operations', width: 280 }
]

const logColumns = [
  { title: '用户名', dataIndex: 'username', width: 120 },
  { title: 'IP地址', slotName: 'ip', width: 150 },
  { title: '登录地点', dataIndex: 'location', width: 120 },
  { title: '登录状态', slotName: 'status', width: 100 },
  { title: '登录时间', dataIndex: 'loginTime', width: 180 },
  { title: '失败原因', dataIndex: 'reason', width: 150 }
]

const loadUsers = () => {
  Message.success('查询完成')
}

const resetSearch = () => {
  Object.assign(searchForm, { username: '', status: '' })
  loadUsers()
}

const editUser = (record: any) => {
  editingUser.value = record
  Object.assign(userForm, { ...record, password: '' })
  showUserModal.value = true
}

const resetPassword = (record: any) => {
  Message.success(`用户"${record.username}"密码已重置为：123456`)
}

const toggleStatus = (record: any) => {
  record.status = record.status === '启用' ? '禁用' : '启用'
  Message.success(`用户状态已${record.status}`)
}

const deleteUser = (record: any) => {
  const index = users.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    users.value.splice(index, 1)
    pagination.total = users.value.length
    Message.success('删除成功')
  }
}

const saveUser = async () => {
  if (!userForm.username || !userForm.realName || (!editingUser.value && !userForm.password)) {
    Message.warning('请填写完整信息')
    return
  }
  
  if (!userForm.roles || userForm.roles.length === 0) {
    Message.warning('请至少选择一个角色')
    return
  }
  
  saveLoading.value = true
  setTimeout(() => {
    if (editingUser.value) {
      const index = users.value.findIndex(item => item.id === editingUser.value.id)
      if (index > -1) {
        const { password, ...rest } = userForm
        Object.assign(users.value[index], rest)
      }
      Message.success('编辑成功')
    } else {
      users.value.push({
        id: Date.now(),
        ...userForm,
        createTime: new Date().toLocaleString('zh-CN')
      })
      Message.success('新增成功')
    }
    saveLoading.value = false
    showUserModal.value = false
    editingUser.value = null
    Object.assign(userForm, { username: '', realName: '', password: '', phone: '', email: '', department: '', roles: [], status: '启用' })
  }, 500)
}

const updateInfo = () => {
  Message.success('信息更新成功')
}

const loadLogs = () => {
  Message.success('查询完成')
}

// 初始化分页
pagination.total = users.value.length
logPagination.total = loginLogs.value.length
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
</style>
