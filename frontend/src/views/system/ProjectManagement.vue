<template>
  <div class="page-container">
    <div class="page-header">
      <h2>项目管理</h2>
      <p>基础信息管理 / 设备点位配置</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="基础信息管理">
        <a-card>
          <template #title>
            <a-space>
              <span>项目列表</span>
              <a-button type="primary" @click="showProjectModal = true">
                <template #icon><icon-plus /></template>
                新增项目
              </a-button>
            </a-space>
          </template>
          
          <a-table
            :columns="projectColumns"
            :data="projects"
            :pagination="pagination"
            :loading="loading"
          >
            <template #status="{ record }">
              <a-tag :color="record.status === '运行中' ? 'green' : 'gray'">{{ record.status }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="editProject(record)">编辑</a-button>
                <a-button type="text" size="small" @click="viewProject(record)">详情</a-button>
                <a-popconfirm content="确定要删除该项目吗？" @ok="deleteProject(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="设备点位配置">
        <a-card>
          <template #title>
            <a-space>
              <span>设备点位列表</span>
              <a-button type="primary" @click="showPointModal = true">
                <template #icon><icon-plus /></template>
                新增点位
              </a-button>
            </a-space>
          </template>
          
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="项目">
              <a-select v-model="filterProject" placeholder="请选择项目" style="width: 200px;" allow-clear>
                <a-option value="项目A">项目A</a-option>
                <a-option value="项目B">项目B</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="设备类型">
              <a-select v-model="filterDeviceType" placeholder="请选择类型" style="width: 200px;" allow-clear>
                <a-option value="水泵">水泵</a-option>
                <a-option value="风机">风机</a-option>
                <a-option value="搅拌器">搅拌器</a-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="loadPoints">查询</a-button>
            </a-form-item>
          </a-form>
          
          <a-table
            :columns="pointColumns"
            :data="devicePoints"
            :pagination="pointPagination"
          >
            <template #status="{ record }">
              <a-tag :color="record.status === '在线' ? 'green' : 'red'">{{ record.status }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="editPoint(record)">编辑</a-button>
                <a-button type="text" size="small" @click="testPoint(record)">测试</a-button>
                <a-popconfirm content="确定要删除该点位吗？" @ok="deletePoint(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 新增/编辑项目弹窗 -->
    <a-modal
      v-model:visible="showProjectModal"
      :title="editingProject ? '编辑项目' : '新增项目'"
      @ok="saveProject"
      :ok-loading="saveLoading"
      width="600px"
    >
      <a-form :model="projectForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="项目名称" required>
              <a-input v-model="projectForm.name" placeholder="请输入项目名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="项目编码" required>
              <a-input v-model="projectForm.code" placeholder="请输入项目编码" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="项目类型">
              <a-select v-model="projectForm.type" placeholder="请选择类型">
                <a-option value="污水处理">污水处理</a-option>
                <a-option value="给水处理">给水处理</a-option>
                <a-option value="中水回用">中水回用</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="设计规模">
              <a-input-number v-model="projectForm.capacity" :min="0" :precision="2" style="width: 100%;" />
              <template #extra>m³/d</template>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="项目地址">
          <a-input v-model="projectForm.address" placeholder="请输入项目地址" />
        </a-form-item>
        <a-form-item label="项目描述">
          <a-textarea v-model="projectForm.description" :auto-size="{ minRows: 3 }" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 新增/编辑点位弹窗 -->
    <a-modal
      v-model:visible="showPointModal"
      :title="editingPoint ? '编辑点位' : '新增点位'"
      @ok="savePoint"
      :ok-loading="saveLoading"
      width="700px"
    >
      <a-form :model="pointForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="项目" required>
              <a-select v-model="pointForm.project" placeholder="请选择项目">
                <a-option value="项目A">项目A</a-option>
                <a-option value="项目B">项目B</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="设备类型" required>
              <a-select v-model="pointForm.deviceType" placeholder="请选择类型">
                <a-option value="水泵">水泵</a-option>
                <a-option value="风机">风机</a-option>
                <a-option value="搅拌器">搅拌器</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="点位名称" required>
              <a-input v-model="pointForm.name" placeholder="请输入点位名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="点位编码" required>
              <a-input v-model="pointForm.code" placeholder="请输入点位编码" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="通信协议">
              <a-select v-model="pointForm.protocol" placeholder="请选择协议">
                <a-option value="Modbus RTU">Modbus RTU</a-option>
                <a-option value="Modbus TCP">Modbus TCP</a-option>
                <a-option value="OPC UA">OPC UA</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="数据地址">
              <a-input v-model="pointForm.address" placeholder="请输入数据地址" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="点位描述">
          <a-textarea v-model="pointForm.description" :auto-size="{ minRows: 2 }" />
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
const showProjectModal = ref(false)
const showPointModal = ref(false)
const editingProject = ref<any>(null)
const editingPoint = ref<any>(null)
const filterProject = ref('')
const filterDeviceType = ref('')

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const pointPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const projects = ref([
  { id: 1, name: '项目A', code: 'PROJ001', type: '污水处理', capacity: 50000, address: 'XX市XX区XX路', status: '运行中', createTime: '2025-01-01' },
  { id: 2, name: '项目B', code: 'PROJ002', type: '给水处理', capacity: 30000, address: 'XX市XX区YY路', status: '运行中', createTime: '2025-02-01' }
])

const devicePoints = ref([
  { id: 1, project: '项目A', deviceType: '水泵', name: '进水泵1', code: 'PUMP001', protocol: 'Modbus RTU', address: '40001', status: '在线', updateTime: '2026-02-04 10:00:00' },
  { id: 2, project: '项目A', deviceType: '风机', name: '曝气风机1', code: 'BLOWER001', protocol: 'Modbus TCP', address: '192.168.1.100:502', status: '在线', updateTime: '2026-02-04 10:00:00' },
  { id: 3, project: '项目A', deviceType: '搅拌器', name: '搅拌器1', code: 'MIXER001', protocol: 'Modbus RTU', address: '40010', status: '离线', updateTime: '2026-02-04 09:30:00' },
  { id: 4, project: '项目B', deviceType: '水泵', name: '出水泵1', code: 'PUMP002', protocol: 'Modbus RTU', address: '40020', status: '在线', updateTime: '2026-02-04 10:00:00' }
])

const projectForm = reactive({
  name: '',
  code: '',
  type: '',
  capacity: 0,
  address: '',
  description: ''
})

const pointForm = reactive({
  project: '',
  deviceType: '',
  name: '',
  code: '',
  protocol: '',
  address: '',
  description: ''
})

const projectColumns = [
  { title: '项目名称', dataIndex: 'name', width: 150 },
  { title: '项目编码', dataIndex: 'code', width: 120 },
  { title: '项目类型', dataIndex: 'type', width: 120 },
  { title: '设计规模', dataIndex: 'capacity', width: 120, render: ({ record }: any) => `${record.capacity} m³/d` },
  { title: '项目地址', dataIndex: 'address', ellipsis: true },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '创建时间', dataIndex: 'createTime', width: 120 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const pointColumns = [
  { title: '项目', dataIndex: 'project', width: 120 },
  { title: '设备类型', dataIndex: 'deviceType', width: 120 },
  { title: '点位名称', dataIndex: 'name', width: 150 },
  { title: '点位编码', dataIndex: 'code', width: 150 },
  { title: '通信协议', dataIndex: 'protocol', width: 150 },
  { title: '数据地址', dataIndex: 'address', width: 200 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '更新时间', dataIndex: 'updateTime', width: 180 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const editProject = (record: any) => {
  editingProject.value = record
  Object.assign(projectForm, record)
  showProjectModal.value = true
}

const viewProject = (record: any) => {
  Message.info(`查看项目：${record.name}`)
}

const deleteProject = (record: any) => {
  const index = projects.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    projects.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const saveProject = async () => {
  if (!projectForm.name || !projectForm.code) {
    Message.warning('请填写完整信息')
    return
  }
  
  saveLoading.value = true
  setTimeout(() => {
    if (editingProject.value) {
      const index = projects.value.findIndex(item => item.id === editingProject.value.id)
      if (index > -1) {
        Object.assign(projects.value[index], projectForm)
      }
      Message.success('编辑成功')
    } else {
      projects.value.push({
        id: Date.now(),
        ...projectForm,
        status: '运行中',
        createTime: new Date().toLocaleDateString()
      })
      Message.success('新增成功')
    }
    saveLoading.value = false
    showProjectModal.value = false
    editingProject.value = null
    Object.assign(projectForm, { name: '', code: '', type: '', capacity: 0, address: '', description: '' })
  }, 500)
}

const loadPoints = () => {
  // 过滤逻辑
  Message.success('查询完成')
}

const editPoint = (record: any) => {
  editingPoint.value = record
  Object.assign(pointForm, record)
  showPointModal.value = true
}

const testPoint = (record: any) => {
  Message.loading('测试中...', 1)
  setTimeout(() => {
    Message.success(`点位"${record.name}"测试成功`)
  }, 1000)
}

const deletePoint = (record: any) => {
  const index = devicePoints.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    devicePoints.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const savePoint = async () => {
  if (!pointForm.project || !pointForm.deviceType || !pointForm.name || !pointForm.code) {
    Message.warning('请填写完整信息')
    return
  }
  
  saveLoading.value = true
  setTimeout(() => {
    if (editingPoint.value) {
      const index = devicePoints.value.findIndex(item => item.id === editingPoint.value.id)
      if (index > -1) {
        Object.assign(devicePoints.value[index], pointForm, { updateTime: new Date().toLocaleString('zh-CN') })
      }
      Message.success('编辑成功')
    } else {
      devicePoints.value.push({
        id: Date.now(),
        ...pointForm,
        status: '在线',
        updateTime: new Date().toLocaleString('zh-CN')
      })
      Message.success('新增成功')
    }
    saveLoading.value = false
    showPointModal.value = false
    editingPoint.value = null
    Object.assign(pointForm, { project: '', deviceType: '', name: '', code: '', protocol: '', address: '', description: '' })
  }, 500)
}

// 初始化分页
pagination.total = projects.value.length
pointPagination.total = devicePoints.value.length
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
