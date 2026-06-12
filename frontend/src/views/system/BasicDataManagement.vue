<template>
  <div class="page-container">
    <div class="page-header">
      <h2>基础数据管理</h2>
      <p>工艺段配置 / 设备类型 / 水质指标</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="工艺段配置">
        <a-card>
          <template #title>
            <a-space>
              <span>工艺段列表</span>
              <a-button type="primary" @click="showProcessModal = true">
                <template #icon><icon-plus /></template>
                新增工艺段
              </a-button>
            </a-space>
          </template>
          
          <a-table
            :columns="processColumns"
            :data="processSections"
            :pagination="pagination"
            :loading="loading"
          >
            <template #status="{ record }">
              <a-tag :color="record.status === '启用' ? 'green' : 'red'">{{ record.status }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="editProcess(record)">编辑</a-button>
                <a-button type="text" size="small" @click="viewProcess(record)">详情</a-button>
                <a-popconfirm content="确定要删除该工艺段吗？" @ok="deleteProcess(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="设备类型">
        <a-card>
          <template #title>
            <a-space>
              <span>设备类型列表</span>
              <a-button type="primary" @click="showDeviceTypeModal = true">
                <template #icon><icon-plus /></template>
                新增类型
              </a-button>
            </a-space>
          </template>
          
          <a-row :gutter="16" style="margin-bottom: 20px;">
            <a-col :span="6" v-for="type in deviceTypes" :key="type.id">
              <a-card :title="type.name" size="small">
                <a-descriptions :column="1" size="small">
                  <a-descriptions-item label="类型编码">{{ type.code }}</a-descriptions-item>
                  <a-descriptions-item label="设备数量">{{ type.deviceCount }}</a-descriptions-item>
                  <a-descriptions-item label="状态">
                    <a-tag :color="type.status === '启用' ? 'green' : 'red'" size="small">{{ type.status }}</a-tag>
                  </a-descriptions-item>
                </a-descriptions>
                <template #actions>
                  <a-space>
                    <a-button type="text" size="small" @click="editDeviceType(type)">编辑</a-button>
                    <a-popconfirm content="确定要删除该设备类型吗？" @ok="deleteDeviceType(type)">
                      <a-button type="text" size="small" status="danger">删除</a-button>
                    </a-popconfirm>
                  </a-space>
                </template>
              </a-card>
            </a-col>
          </a-row>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="水质指标">
        <a-card>
          <template #title>
            <a-space>
              <span>水质指标列表</span>
              <a-button type="primary" @click="showIndicatorModal = true">
                <template #icon><icon-plus /></template>
                新增指标
              </a-button>
            </a-space>
          </template>
          
          <a-table
            :columns="indicatorColumns"
            :data="waterQualityIndicators"
            :pagination="indicatorPagination"
          >
            <template #unit="{ record }">
              <a-tag>{{ record.unit }}</a-tag>
            </template>
            <template #standard="{ record }">
              <a-descriptions :column="1" size="small" bordered>
                <a-descriptions-item label="标准值">{{ record.standard }} {{ record.unit }}</a-descriptions-item>
                <a-descriptions-item label="上限">{{ record.max }} {{ record.unit }}</a-descriptions-item>
                <a-descriptions-item label="下限">{{ record.min }} {{ record.unit }}</a-descriptions-item>
              </a-descriptions>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="editIndicator(record)">编辑</a-button>
                <a-popconfirm content="确定要删除该指标吗？" @ok="deleteIndicator(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 新增/编辑工艺段弹窗 -->
    <a-modal
      v-model:visible="showProcessModal"
      :title="editingProcess ? '编辑工艺段' : '新增工艺段'"
      @ok="saveProcess"
      :ok-loading="saveLoading"
    >
      <a-form :model="processForm" layout="vertical">
        <a-form-item label="工艺段名称" required>
          <a-input v-model="processForm.name" placeholder="请输入工艺段名称" />
        </a-form-item>
        <a-form-item label="工艺段编码" required>
          <a-input v-model="processForm.code" placeholder="请输入工艺段编码" />
        </a-form-item>
        <a-form-item label="工艺描述">
          <a-textarea v-model="processForm.description" :auto-size="{ minRows: 3 }" />
        </a-form-item>
        <a-form-item label="状态">
          <a-radio-group v-model="processForm.status">
            <a-radio value="启用">启用</a-radio>
            <a-radio value="禁用">禁用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 新增/编辑设备类型弹窗 -->
    <a-modal
      v-model:visible="showDeviceTypeModal"
      :title="editingDeviceType ? '编辑设备类型' : '新增设备类型'"
      @ok="saveDeviceType"
      :ok-loading="saveLoading"
    >
      <a-form :model="deviceTypeForm" layout="vertical">
        <a-form-item label="类型名称" required>
          <a-input v-model="deviceTypeForm.name" placeholder="请输入类型名称" />
        </a-form-item>
        <a-form-item label="类型编码" required>
          <a-input v-model="deviceTypeForm.code" placeholder="请输入类型编码" />
        </a-form-item>
        <a-form-item label="类型描述">
          <a-textarea v-model="deviceTypeForm.description" :auto-size="{ minRows: 3 }" />
        </a-form-item>
        <a-form-item label="状态">
          <a-radio-group v-model="deviceTypeForm.status">
            <a-radio value="启用">启用</a-radio>
            <a-radio value="禁用">禁用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 新增/编辑水质指标弹窗 -->
    <a-modal
      v-model:visible="showIndicatorModal"
      :title="editingIndicator ? '编辑水质指标' : '新增水质指标'"
      @ok="saveIndicator"
      :ok-loading="saveLoading"
      width="600px"
    >
      <a-form :model="indicatorForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="指标名称" required>
              <a-input v-model="indicatorForm.name" placeholder="请输入指标名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="指标编码" required>
              <a-input v-model="indicatorForm.code" placeholder="请输入指标编码" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="单位" required>
              <a-input v-model="indicatorForm.unit" placeholder="请输入单位" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="标准值" required>
              <a-input-number v-model="indicatorForm.standard" :precision="2" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="上限" required>
              <a-input-number v-model="indicatorForm.max" :precision="2" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="下限" required>
              <a-input-number v-model="indicatorForm.min" :precision="2" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="指标说明">
          <a-textarea v-model="indicatorForm.description" :auto-size="{ minRows: 2 }" />
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
const showProcessModal = ref(false)
const showDeviceTypeModal = ref(false)
const showIndicatorModal = ref(false)
const editingProcess = ref<any>(null)
const editingDeviceType = ref<any>(null)
const editingIndicator = ref<any>(null)

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const indicatorPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const processSections = ref([
  { id: 1, name: '预处理', code: 'PRE', description: '格栅、沉砂等预处理工艺', status: '启用', deviceCount: 5 },
  { id: 2, name: '生化处理', code: 'BIO', description: 'A/O、A²/O等生化处理工艺', status: '启用', deviceCount: 12 },
  { id: 3, name: '深度处理', code: 'ADV', description: '过滤、消毒等深度处理工艺', status: '启用', deviceCount: 8 },
  { id: 4, name: '污泥处理', code: 'SLUDGE', description: '污泥浓缩、脱水等处理工艺', status: '启用', deviceCount: 6 }
])

const deviceTypes = ref([
  { id: 1, name: '水泵', code: 'PUMP', description: '各类水泵设备', deviceCount: 15, status: '启用' },
  { id: 2, name: '风机', code: 'BLOWER', description: '曝气风机设备', deviceCount: 8, status: '启用' },
  { id: 3, name: '搅拌器', code: 'MIXER', description: '搅拌器设备', deviceCount: 12, status: '启用' },
  { id: 4, name: '格栅', code: 'SCREEN', description: '格栅设备', deviceCount: 4, status: '启用' },
  { id: 5, name: '加药设备', code: 'DOSING', description: '加药泵、加药系统', deviceCount: 10, status: '启用' },
  { id: 6, name: '仪表', code: 'METER', description: '各类检测仪表', deviceCount: 25, status: '启用' }
])

const waterQualityIndicators = ref([
  { id: 1, name: 'COD', code: 'COD', unit: 'mg/L', standard: 50, max: 60, min: 0, description: '化学需氧量' },
  { id: 2, name: 'BOD5', code: 'BOD5', unit: 'mg/L', standard: 10, max: 15, min: 0, description: '五日生化需氧量' },
  { id: 3, name: 'NH3-N', code: 'NH3N', unit: 'mg/L', standard: 5, max: 8, min: 0, description: '氨氮' },
  { id: 4, name: 'TP', code: 'TP', unit: 'mg/L', standard: 0.5, max: 1.0, min: 0, description: '总磷' },
  { id: 5, name: 'TN', code: 'TN', unit: 'mg/L', standard: 15, max: 20, min: 0, description: '总氮' },
  { id: 6, name: 'SS', code: 'SS', unit: 'mg/L', standard: 10, max: 15, min: 0, description: '悬浮物' },
  { id: 7, name: 'pH', code: 'PH', unit: '', standard: 7.0, max: 8.5, min: 6.5, description: '酸碱度' }
])

const processForm = reactive({
  name: '',
  code: '',
  description: '',
  status: '启用'
})

const deviceTypeForm = reactive({
  name: '',
  code: '',
  description: '',
  status: '启用'
})

const indicatorForm = reactive({
  name: '',
  code: '',
  unit: '',
  standard: 0,
  max: 0,
  min: 0,
  description: ''
})

const processColumns = [
  { title: '工艺段名称', dataIndex: 'name', width: 150 },
  { title: '工艺段编码', dataIndex: 'code', width: 150 },
  { title: '工艺描述', dataIndex: 'description', ellipsis: true },
  { title: '设备数量', dataIndex: 'deviceCount', width: 100 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const indicatorColumns = [
  { title: '指标名称', dataIndex: 'name', width: 120 },
  { title: '指标编码', dataIndex: 'code', width: 120 },
  { title: '单位', slotName: 'unit', width: 100 },
  { title: '标准值', slotName: 'standard', width: 200 },
  { title: '指标说明', dataIndex: 'description', ellipsis: true },
  { title: '操作', slotName: 'operations', width: 150 }
]

const editProcess = (record: any) => {
  editingProcess.value = record
  Object.assign(processForm, record)
  showProcessModal.value = true
}

const viewProcess = (record: any) => {
  Message.info(`查看工艺段：${record.name}`)
}

const deleteProcess = (record: any) => {
  const index = processSections.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    processSections.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const saveProcess = async () => {
  if (!processForm.name || !processForm.code) {
    Message.warning('请填写完整信息')
    return
  }
  
  saveLoading.value = true
  setTimeout(() => {
    if (editingProcess.value) {
      const index = processSections.value.findIndex(item => item.id === editingProcess.value.id)
      if (index > -1) {
        Object.assign(processSections.value[index], processForm)
      }
      Message.success('编辑成功')
    } else {
      processSections.value.push({
        id: Date.now(),
        ...processForm,
        deviceCount: 0
      })
      Message.success('新增成功')
    }
    saveLoading.value = false
    showProcessModal.value = false
    editingProcess.value = null
    Object.assign(processForm, { name: '', code: '', description: '', status: '启用' })
  }, 500)
}

const editDeviceType = (record: any) => {
  editingDeviceType.value = record
  Object.assign(deviceTypeForm, record)
  showDeviceTypeModal.value = true
}

const deleteDeviceType = (record: any) => {
  const index = deviceTypes.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    deviceTypes.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const saveDeviceType = async () => {
  if (!deviceTypeForm.name || !deviceTypeForm.code) {
    Message.warning('请填写完整信息')
    return
  }
  
  saveLoading.value = true
  setTimeout(() => {
    if (editingDeviceType.value) {
      const index = deviceTypes.value.findIndex(item => item.id === editingDeviceType.value.id)
      if (index > -1) {
        Object.assign(deviceTypes.value[index], deviceTypeForm)
      }
      Message.success('编辑成功')
    } else {
      deviceTypes.value.push({
        id: Date.now(),
        ...deviceTypeForm,
        deviceCount: 0
      })
      Message.success('新增成功')
    }
    saveLoading.value = false
    showDeviceTypeModal.value = false
    editingDeviceType.value = null
    Object.assign(deviceTypeForm, { name: '', code: '', description: '', status: '启用' })
  }, 500)
}

const editIndicator = (record: any) => {
  editingIndicator.value = record
  Object.assign(indicatorForm, record)
  showIndicatorModal.value = true
}

const deleteIndicator = (record: any) => {
  const index = waterQualityIndicators.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    waterQualityIndicators.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const saveIndicator = async () => {
  if (!indicatorForm.name || !indicatorForm.code || !indicatorForm.unit) {
    Message.warning('请填写完整信息')
    return
  }
  
  saveLoading.value = true
  setTimeout(() => {
    if (editingIndicator.value) {
      const index = waterQualityIndicators.value.findIndex(item => item.id === editingIndicator.value.id)
      if (index > -1) {
        Object.assign(waterQualityIndicators.value[index], indicatorForm)
      }
      Message.success('编辑成功')
    } else {
      waterQualityIndicators.value.push({
        id: Date.now(),
        ...indicatorForm
      })
      Message.success('新增成功')
    }
    saveLoading.value = false
    showIndicatorModal.value = false
    editingIndicator.value = null
    Object.assign(indicatorForm, { name: '', code: '', unit: '', standard: 0, max: 0, min: 0, description: '' })
  }, 500)
}

// 初始化分页
pagination.total = processSections.value.length
indicatorPagination.total = waterQualityIndicators.value.length
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
