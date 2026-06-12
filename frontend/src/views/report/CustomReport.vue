<template>
  <div class="page-container">
    <div class="page-header">
      <h2>自定义报表</h2>
      <p>报表模板配置 / 自定义查询 / 权限管理</p>
    </div>

    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="报表模板">
        <a-card>
          <template #title>
            <span>报表模板列表</span>
          </template>
          <template #extra>
            <a-button type="primary" @click="createTemplate">
              <template #icon><icon-plus /></template>
              新建模板
            </a-button>
          </template>
          <a-table :columns="templateColumns" :data="templateList" :loading="loading">
            <template #category="{ record }">
              <a-tag>{{ record.category }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="editTemplate(record)">编辑</a-button>
                <a-button type="text" size="small" @click="copyTemplate(record)">复制</a-button>
                <a-popconfirm content="确定要删除该模板吗？" @ok="deleteTemplate(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>

      <a-tab-pane key="2" title="自定义查询">
        <a-card>
          <a-form :model="queryForm" layout="vertical" style="max-width: 800px;">
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="数据源">
                  <a-select v-model="queryForm.dataSource" placeholder="请选择数据源">
                    <a-option value="production">生产数据</a-option>
                    <a-option value="quality">水质数据</a-option>
                    <a-option value="energy">能耗数据</a-option>
                    <a-option value="equipment">设备数据</a-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="时间范围">
                  <a-range-picker v-model="queryForm.dateRange" style="width: 100%;" />
                </a-form-item>
              </a-col>
            </a-row>
            <a-form-item label="查询字段">
              <a-checkbox-group v-model="queryForm.fields">
                <a-checkbox value="water_volume">处理水量</a-checkbox>
                <a-checkbox value="cod">COD</a-checkbox>
                <a-checkbox value="nh3n">氨氮</a-checkbox>
                <a-checkbox value="energy">能耗</a-checkbox>
                <a-checkbox value="cost">成本</a-checkbox>
              </a-checkbox-group>
            </a-form-item>
            <a-form-item label="分组方式">
              <a-radio-group v-model="queryForm.groupBy">
                <a-radio value="day">按日</a-radio>
                <a-radio value="week">按周</a-radio>
                <a-radio value="month">按月</a-radio>
              </a-radio-group>
            </a-form-item>
            <a-form-item>
              <a-space>
                <a-button type="primary" @click="executeQuery">
                  <template #icon><icon-search /></template>
                  执行查询
                </a-button>
                <a-button @click="saveQuery">保存查询</a-button>
                <a-button @click="exportQuery">导出数据</a-button>
              </a-space>
            </a-form-item>
          </a-form>

          <a-divider />

          <div v-if="queryResult.length > 0">
            <a-table :columns="resultColumns" :data="queryResult" :pagination="false" />
          </div>
          <a-empty v-else description="暂无查询结果" />
        </a-card>
      </a-tab-pane>

      <a-tab-pane key="3" title="权限管理">
        <a-card>
          <template #title>
            <span>报表权限配置</span>
          </template>
          <a-table :columns="permissionColumns" :data="permissionList">
            <template #reportName="{ record }">
              <a-link>{{ record.report_name }}</a-link>
            </template>
            <template #users="{ record }">
              <a-tag v-for="user in record.users" :key="user" style="margin-right: 4px;">{{ user }}</a-tag>
            </template>
            <template #roles="{ record }">
              <a-tag v-for="role in record.roles" :key="role" style="margin-right: 4px;">{{ role }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-button type="text" size="small" @click="editPermission(record)">编辑权限</a-button>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)

const templateColumns = [
  { title: '模板名称', dataIndex: 'name', width: 200 },
  { title: '分类', slotName: 'category', width: 120 },
  { title: '数据源', dataIndex: 'dataSource', width: 150 },
  { title: '创建时间', dataIndex: 'create_time', width: 180 },
  { title: '创建人', dataIndex: 'creator', width: 120 },
  { title: '操作', slotName: 'operations', width: 200, fixed: 'right' }
]

const templateList = ref([
  {
    id: 1,
    name: '生产日报模板',
    category: '生产报表',
    dataSource: '生产数据',
    create_time: '2025-01-01 10:00:00',
    creator: '张三'
  },
  {
    id: 2,
    name: '水质分析模板',
    category: '水质报表',
    dataSource: '水质数据',
    create_time: '2025-01-02 14:30:00',
    creator: '李四'
  },
  {
    id: 3,
    name: '能耗统计模板',
    category: '能耗报表',
    dataSource: '能耗数据',
    create_time: '2025-01-03 09:15:00',
    creator: '王五'
  }
])

const queryForm = reactive({
  dataSource: '',
  dateRange: [],
  fields: [],
  groupBy: 'day'
})

const resultColumns = [
  { title: '日期', dataIndex: 'date', width: 120 },
  { title: '处理水量(m³)', dataIndex: 'water_volume', width: 120 },
  { title: 'COD(mg/L)', dataIndex: 'cod', width: 100 },
  { title: '氨氮(mg/L)', dataIndex: 'nh3n', width: 100 },
  { title: '能耗(kWh)', dataIndex: 'energy', width: 120 },
  { title: '成本(元)', dataIndex: 'cost', width: 100 }
]

const queryResult = ref<any[]>([])

const permissionColumns = [
  { title: '报表名称', slotName: 'reportName', width: 200 },
  { title: '授权用户', slotName: 'users', width: 200 },
  { title: '授权角色', slotName: 'roles', width: 200 },
  { title: '权限类型', dataIndex: 'permission_type', width: 120 },
  { title: '更新时间', dataIndex: 'update_time', width: 180 },
  { title: '操作', slotName: 'operations', width: 120, fixed: 'right' }
]

const permissionList = ref([
  {
    id: 1,
    report_name: '生产日报',
    users: ['张三', '李四'],
    roles: ['生产管理员', '操作员'],
    permission_type: '查看+导出',
    update_time: '2025-01-01 10:00:00'
  },
  {
    id: 2,
    report_name: '水质分析报表',
    users: ['王五'],
    roles: ['水质管理员'],
    permission_type: '查看+编辑',
    update_time: '2025-01-02 14:30:00'
  },
  {
    id: 3,
    report_name: '能耗统计报表',
    users: ['赵六', '张三'],
    roles: ['能耗管理员'],
    permission_type: '查看',
    update_time: '2025-01-03 09:15:00'
  }
])

const createTemplate = () => {
  Message.info('打开新建模板对话框')
}

const editTemplate = (record: any) => {
  Message.info(`编辑模板: ${record.name}`)
}

const copyTemplate = (record: any) => {
  Message.success(`复制模板: ${record.name}`)
}

const deleteTemplate = (record: any) => {
  Message.warning(`删除模板: ${record.name}`)
}

const executeQuery = () => {
  loading.value = true
  setTimeout(() => {
    queryResult.value = [
      { date: '2025-01-01', water_volume: 15600, cod: 28, nh3n: 3.5, energy: 12500, cost: 8750 },
      { date: '2025-01-02', water_volume: 15800, cod: 26, nh3n: 3.2, energy: 12800, cost: 8960 },
      { date: '2025-01-03', water_volume: 16200, cod: 30, nh3n: 3.8, energy: 13200, cost: 9240 },
      { date: '2025-01-04', water_volume: 15500, cod: 25, nh3n: 3.1, energy: 12400, cost: 8680 },
      { date: '2025-01-05', water_volume: 16000, cod: 27, nh3n: 3.4, energy: 13000, cost: 9100 }
    ]
    loading.value = false
    Message.success('查询成功')
  }, 500)
}

const saveQuery = () => {
  Message.success('查询已保存')
}

const exportQuery = () => {
  Message.success('数据导出成功')
}

const editPermission = (record: any) => {
  Message.info(`编辑权限: ${record.report_name}`)
}
</script>

<style scoped>
.page-container {
  padding: 16px;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
}

.page-header p {
  margin: 0;
  font-size: 14px;
  color: #86909c;
}
</style>
