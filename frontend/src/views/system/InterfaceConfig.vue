<template>
  <div class="page-container">
    <div class="page-header">
      <h2>接口配置</h2>
      <p>第三方接口管理 / 调试监控 / 权限控制</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="第三方接口管理">
        <a-card>
          <template #title>
            <a-space>
              <span>接口列表</span>
              <a-button type="primary" @click="showInterfaceModal = true">
                <template #icon><icon-plus /></template>
                新增接口
              </a-button>
            </a-space>
          </template>
          
          <a-table
            :columns="interfaceColumns"
            :data="interfaces"
            :pagination="pagination"
            :loading="loading"
          >
            <template #type="{ record }">
              <a-tag :color="getInterfaceTypeColor(record.type)">{{ record.type }}</a-tag>
            </template>
            <template #status="{ record }">
              <a-tag :color="record.status === '启用' ? 'green' : 'red'">{{ record.status }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="testInterface(record)">测试</a-button>
                <a-button type="text" size="small" @click="editInterface(record)">编辑</a-button>
                <a-button type="text" size="small" @click="viewInterfaceLog(record)">日志</a-button>
                <a-popconfirm content="确定要删除该接口吗？" @ok="deleteInterface(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="调试监控">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="选择接口">
              <a-select v-model="debugInterface" placeholder="请选择接口" style="width: 200px;">
                <a-option v-for="item in interfaces" :key="item.id" :value="item.id">{{ item.name }}</a-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="startDebug">开始调试</a-button>
              <a-button style="margin-left: 8px;" @click="stopDebug">停止调试</a-button>
            </a-form-item>
          </a-form>
          
          <a-row :gutter="16">
            <a-col :span="12">
              <a-card title="请求信息" size="small">
                <a-form :model="requestForm" layout="vertical" size="small">
                  <a-form-item label="请求URL">
                    <a-input v-model="requestForm.url" placeholder="请输入URL" />
                  </a-form-item>
                  <a-form-item label="请求方法">
                    <a-select v-model="requestForm.method">
                      <a-option value="GET">GET</a-option>
                      <a-option value="POST">POST</a-option>
                      <a-option value="PUT">PUT</a-option>
                      <a-option value="DELETE">DELETE</a-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item label="请求头">
                    <a-textarea v-model="requestForm.headers" :auto-size="{ minRows: 3 }" />
                  </a-form-item>
                  <a-form-item label="请求体">
                    <a-textarea v-model="requestForm.body" :auto-size="{ minRows: 5 }" />
                  </a-form-item>
                  <a-form-item>
                    <a-button type="primary" @click="sendRequest">发送请求</a-button>
                  </a-form-item>
                </a-form>
              </a-card>
            </a-col>
            <a-col :span="12">
              <a-card title="响应信息" size="small">
                <a-descriptions :column="1" size="small" bordered>
                  <a-descriptions-item label="状态码">
                    <a-tag :color="response.statusCode >= 200 && response.statusCode < 300 ? 'green' : 'red'">
                      {{ response.statusCode }}
                    </a-tag>
                  </a-descriptions-item>
                  <a-descriptions-item label="响应时间">{{ response.responseTime }}ms</a-descriptions-item>
                  <a-descriptions-item label="响应头">
                    <a-textarea v-model="response.headers" :auto-size="{ minRows: 3 }" readonly />
                  </a-descriptions-item>
                  <a-descriptions-item label="响应体">
                    <a-textarea v-model="response.body" :auto-size="{ minRows: 8 }" readonly />
                  </a-descriptions-item>
                </a-descriptions>
              </a-card>
            </a-col>
          </a-row>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="权限控制">
        <a-card>
          <a-alert message="接口权限控制说明" type="info" style="margin-bottom: 20px;">
            <template #description>
              可以为每个接口配置访问权限，只有拥有相应权限的角色才能调用该接口。
            </template>
          </a-alert>
          
          <a-table
            :columns="permissionColumns"
            :data="interfacePermissions"
            :pagination="permissionPagination"
          >
            <template #interface="{ record }">
              <a-link @click="viewInterfaceDetail(record)">{{ record.interfaceName }}</a-link>
            </template>
            <template #roles="{ record }">
              <a-tag v-for="role in record.roles" :key="role" style="margin-right: 4px;">{{ role }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="editPermission(record)">编辑权限</a-button>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 新增/编辑接口弹窗 -->
    <a-modal
      v-model:visible="showInterfaceModal"
      :title="editingInterface ? '编辑接口' : '新增接口'"
      @ok="saveInterface"
      :ok-loading="saveLoading"
      width="700px"
    >
      <a-form :model="interfaceForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="接口名称" required>
              <a-input v-model="interfaceForm.name" placeholder="请输入接口名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="接口类型" required>
              <a-select v-model="interfaceForm.type" placeholder="请选择类型">
                <a-option value="REST API">REST API</a-option>
                <a-option value="WebSocket">WebSocket</a-option>
                <a-option value="MQTT">MQTT</a-option>
                <a-option value="OPC UA">OPC UA</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="接口地址" required>
          <a-input v-model="interfaceForm.url" placeholder="请输入接口地址" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="认证方式">
              <a-select v-model="interfaceForm.authType" placeholder="请选择认证方式">
                <a-option value="None">无认证</a-option>
                <a-option value="Basic">Basic认证</a-option>
                <a-option value="Token">Token认证</a-option>
                <a-option value="API Key">API Key</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="状态">
              <a-radio-group v-model="interfaceForm.status">
                <a-radio value="启用">启用</a-radio>
                <a-radio value="禁用">禁用</a-radio>
              </a-radio-group>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="接口描述">
          <a-textarea v-model="interfaceForm.description" :auto-size="{ minRows: 3 }" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 编辑权限弹窗 -->
    <a-modal
      v-model:visible="showPermissionModal"
      title="编辑接口权限"
      @ok="savePermission"
    >
      <a-form :model="permissionForm" layout="vertical">
        <a-form-item label="接口名称">
          <a-input v-model="permissionForm.interfaceName" readonly />
        </a-form-item>
        <a-form-item label="允许访问的角色" required>
          <a-select v-model="permissionForm.roles" multiple placeholder="请选择角色">
            <a-option value="管理员">管理员</a-option>
            <a-option value="操作员">操作员</a-option>
            <a-option value="维护员">维护员</a-option>
            <a-option value="查看者">查看者</a-option>
          </a-select>
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
const showInterfaceModal = ref(false)
const showPermissionModal = ref(false)
const editingInterface = ref<any>(null)
const debugInterface = ref('')
const isDebugging = ref(false)

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const permissionPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const interfaces = ref([
  { id: 1, name: 'SCADA数据接口', type: 'REST API', url: 'http://192.168.1.100:8080/api/scada', authType: 'Token', status: '启用', description: 'SCADA系统数据采集接口' },
  { id: 2, name: '设备监控接口', type: 'WebSocket', url: 'ws://192.168.1.101:8081/ws', authType: 'API Key', status: '启用', description: '实时设备监控WebSocket接口' },
  { id: 3, name: '数据上报接口', type: 'REST API', url: 'http://192.168.1.102:8080/api/report', authType: 'Basic', status: '禁用', description: '数据上报到上级平台接口' }
])

const interfacePermissions = ref([
  { id: 1, interfaceName: 'SCADA数据接口', roles: ['管理员', '操作员'], updateTime: '2026-02-01' },
  { id: 2, interfaceName: '设备监控接口', roles: ['管理员', '操作员', '维护员'], updateTime: '2026-02-01' },
  { id: 3, interfaceName: '数据上报接口', roles: ['管理员'], updateTime: '2026-02-01' }
])

const requestForm = reactive({
  url: '',
  method: 'GET',
  headers: 'Content-Type: application/json',
  body: ''
})

const response = reactive({
  statusCode: 200,
  responseTime: 0,
  headers: '',
  body: ''
})

const interfaceForm = reactive({
  name: '',
  type: '',
  url: '',
  authType: 'None',
  status: '启用',
  description: ''
})

const permissionForm = reactive({
  interfaceName: '',
  roles: []
})

const interfaceColumns = [
  { title: '接口名称', dataIndex: 'name', width: 200 },
  { title: '接口类型', slotName: 'type', width: 120 },
  { title: '接口地址', dataIndex: 'url', ellipsis: true },
  { title: '认证方式', dataIndex: 'authType', width: 120 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 250 }
]

const permissionColumns = [
  { title: '接口名称', slotName: 'interface', width: 200 },
  { title: '允许访问的角色', slotName: 'roles', width: 300 },
  { title: '更新时间', dataIndex: 'updateTime', width: 120 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const getInterfaceTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    'REST API': 'blue',
    'WebSocket': 'green',
    'MQTT': 'orange',
    'OPC UA': 'purple'
  }
  return colors[type] || 'gray'
}

const testInterface = (record: any) => {
  Message.loading('测试中...', 1)
  setTimeout(() => {
    Message.success(`接口"${record.name}"测试成功`)
  }, 1000)
}

const editInterface = (record: any) => {
  editingInterface.value = record
  Object.assign(interfaceForm, record)
  showInterfaceModal.value = true
}

const viewInterfaceLog = (record: any) => {
  Message.info(`查看接口日志：${record.name}`)
}

const deleteInterface = (record: any) => {
  const index = interfaces.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    interfaces.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const saveInterface = async () => {
  if (!interfaceForm.name || !interfaceForm.type || !interfaceForm.url) {
    Message.warning('请填写完整信息')
    return
  }
  
  saveLoading.value = true
  setTimeout(() => {
    if (editingInterface.value) {
      const index = interfaces.value.findIndex(item => item.id === editingInterface.value.id)
      if (index > -1) {
        Object.assign(interfaces.value[index], interfaceForm)
      }
      Message.success('编辑成功')
    } else {
      interfaces.value.push({
        id: Date.now(),
        ...interfaceForm
      })
      Message.success('新增成功')
    }
    saveLoading.value = false
    showInterfaceModal.value = false
    editingInterface.value = null
    Object.assign(interfaceForm, { name: '', type: '', url: '', authType: 'None', status: '启用', description: '' })
  }, 500)
}

const startDebug = () => {
  if (!debugInterface.value) {
    Message.warning('请先选择接口')
    return
  }
  isDebugging.value = true
  const selected = interfaces.value.find(item => item.id === debugInterface.value)
  if (selected) {
    requestForm.url = selected.url
  }
  Message.success('调试模式已启动')
}

const stopDebug = () => {
  isDebugging.value = false
  Message.success('调试模式已停止')
}

const sendRequest = () => {
  if (!requestForm.url) {
    Message.warning('请输入请求URL')
    return
  }
  
  Message.loading('发送请求中...', 1)
  setTimeout(() => {
    response.statusCode = 200
    response.responseTime = Math.floor(Math.random() * 100) + 50
    response.headers = 'Content-Type: application/json\nX-Request-ID: 123456789'
    response.body = JSON.stringify({ code: 200, message: 'success', data: { result: '请求成功' } }, null, 2)
    Message.success('请求发送成功')
  }, 1000)
}

const viewInterfaceDetail = (record: any) => {
  Message.info(`查看接口详情：${record.interfaceName}`)
}

const editPermission = (record: any) => {
  Object.assign(permissionForm, record)
  showPermissionModal.value = true
}

const savePermission = () => {
  if (!permissionForm.roles || permissionForm.roles.length === 0) {
    Message.warning('请至少选择一个角色')
    return
  }
  
  const index = interfacePermissions.value.findIndex(item => item.interfaceName === permissionForm.interfaceName)
  if (index > -1) {
    interfacePermissions.value[index].roles = permissionForm.roles
    interfacePermissions.value[index].updateTime = new Date().toLocaleDateString()
  }
  Message.success('权限保存成功')
  showPermissionModal.value = false
  Object.assign(permissionForm, { interfaceName: '', roles: [] })
}

// 初始化分页
pagination.total = interfaces.value.length
permissionPagination.total = interfacePermissions.value.length
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
