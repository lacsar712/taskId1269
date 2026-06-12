<template>
  <div class="page-container">
    <div class="page-header">
      <h2>考核指标体系</h2>
      <p>指标配置 / 权重设置 / 评分标准</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="指标配置">
        <a-card>
          <template #title>
            <a-space>
              <span>指标列表</span>
              <a-button type="primary" @click="showAddModal = true">
                <template #icon><icon-plus /></template>
                新增指标
              </a-button>
            </a-space>
          </template>
          
          <a-table
            :columns="indicatorColumns"
            :data="indicators"
            :pagination="pagination"
            :loading="loading"
            @page-change="handlePageChange"
            @page-size-change="handlePageSizeChange"
          >
            <template #category="{ record }">
              <a-tag :color="getCategoryColor(record.category)">{{ record.category }}</a-tag>
            </template>
            <template #weight="{ record }">
              <a-progress :percent="record.weight" :show-text="true" />
            </template>
            <template #status="{ record }">
              <a-switch v-model="record.status" checked-text="启用" unchecked-text="禁用" />
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
      
      <a-tab-pane key="2" title="权重设置">
        <a-row :gutter="16">
          <a-col :span="16">
            <a-card title="权重分配">
              <div ref="weightChartRef" style="height: 400px;"></div>
            </a-card>
          </a-col>
          <a-col :span="8">
            <a-card title="权重统计">
              <a-list :data="weightStats" size="small">
                <template #item="{ item }">
                  <a-list-item>
                    <a-list-item-meta>
                      <template #title>
                        <a-space>
                          <span>{{ item.category }}</span>
                          <a-tag :color="getCategoryColor(item.category)">{{ item.weight }}%</a-tag>
                        </a-space>
                      </template>
                      <template #description>
                        <a-progress :percent="item.weight" :show-text="false" />
                      </template>
                    </a-list-item-meta>
                  </a-list-item>
                </template>
              </a-list>
            </a-card>
          </a-col>
        </a-row>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="评分标准">
        <a-card>
          <a-table
            :columns="scoreColumns"
            :data="scoreStandards"
            :pagination="false"
          >
            <template #level="{ record }">
              <a-tag :color="getLevelColor(record.level)">{{ record.level }}</a-tag>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 新增/编辑指标弹窗 -->
    <a-modal
      v-model:visible="showAddModal"
      :title="editingIndicator ? '编辑指标' : '新增指标'"
      @ok="saveIndicator"
      :ok-loading="saveLoading"
    >
      <a-form :model="indicatorForm" layout="vertical">
        <a-form-item label="指标名称" required>
          <a-input v-model="indicatorForm.name" placeholder="请输入指标名称" />
        </a-form-item>
        <a-form-item label="指标分类" required>
          <a-select v-model="indicatorForm.category" placeholder="请选择分类">
            <a-option value="生产指标">生产指标</a-option>
            <a-option value="质量指标">质量指标</a-option>
            <a-option value="安全指标">安全指标</a-option>
            <a-option value="能耗指标">能耗指标</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="权重(%)" required>
          <a-input-number v-model="indicatorForm.weight" :min="0" :max="100" :precision="2" />
        </a-form-item>
        <a-form-item label="指标说明">
          <a-textarea v-model="indicatorForm.description" :auto-size="{ minRows: 3 }" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import * as echarts from 'echarts'

const loading = ref(false)
const saveLoading = ref(false)
const showAddModal = ref(false)
const editingIndicator = ref<any>(null)
const weightChartRef = ref<HTMLElement>()
let weightChart: echarts.ECharts

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const indicators = ref([
  { id: 1, name: 'COD去除率', category: '质量指标', weight: 25, description: '化学需氧量去除率', status: true },
  { id: 2, name: '氨氮去除率', category: '质量指标', weight: 20, description: '氨氮去除率', status: true },
  { id: 3, name: '日处理水量', category: '生产指标', weight: 15, description: '每日处理水量达标率', status: true },
  { id: 4, name: '设备运行率', category: '生产指标', weight: 15, description: '设备正常运行时间占比', status: true },
  { id: 5, name: '安全事故数', category: '安全指标', weight: 10, description: '安全事故发生次数', status: true },
  { id: 6, name: '吨水电耗', category: '能耗指标', weight: 10, description: '每吨水处理电耗', status: true },
  { id: 7, name: '吨水药耗', category: '能耗指标', weight: 5, description: '每吨水处理药耗', status: true }
])

const weightStats = ref([
  { category: '质量指标', weight: 45 },
  { category: '生产指标', weight: 30 },
  { category: '安全指标', weight: 10 },
  { category: '能耗指标', weight: 15 }
])

const scoreStandards = ref([
  { id: 1, indicator: 'COD去除率', level: '优秀', min: 90, max: 100, score: 100 },
  { id: 2, indicator: 'COD去除率', level: '良好', min: 85, max: 90, score: 80 },
  { id: 3, indicator: 'COD去除率', level: '合格', min: 80, max: 85, score: 60 },
  { id: 4, indicator: 'COD去除率', level: '不合格', min: 0, max: 80, score: 0 },
  { id: 5, indicator: '氨氮去除率', level: '优秀', min: 95, max: 100, score: 100 },
  { id: 6, indicator: '氨氮去除率', level: '良好', min: 90, max: 95, score: 80 },
  { id: 7, indicator: '氨氮去除率', level: '合格', min: 85, max: 90, score: 60 },
  { id: 8, indicator: '氨氮去除率', level: '不合格', min: 0, max: 85, score: 0 }
])

const indicatorForm = reactive({
  name: '',
  category: '',
  weight: 0,
  description: ''
})

const indicatorColumns = [
  { title: '指标名称', dataIndex: 'name', width: 150 },
  { title: '指标分类', slotName: 'category', width: 120 },
  { title: '权重', slotName: 'weight', width: 200 },
  { title: '指标说明', dataIndex: 'description', ellipsis: true },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const scoreColumns = [
  { title: '指标名称', dataIndex: 'indicator', width: 150 },
  { title: '等级', slotName: 'level', width: 100 },
  { title: '最小值', dataIndex: 'min', width: 100 },
  { title: '最大值', dataIndex: 'max', width: 100 },
  { title: '得分', dataIndex: 'score', width: 100 }
]

const getCategoryColor = (category: string) => {
  const colors: Record<string, string> = {
    '生产指标': 'blue',
    '质量指标': 'green',
    '安全指标': 'red',
    '能耗指标': 'orange'
  }
  return colors[category] || 'gray'
}

const getLevelColor = (level: string) => {
  const colors: Record<string, string> = {
    '优秀': 'green',
    '良好': 'blue',
    '合格': 'orange',
    '不合格': 'red'
  }
  return colors[level] || 'gray'
}

const handlePageChange = (page: number) => {
  pagination.current = page
}

const handlePageSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.current = 1
}

const editIndicator = (record: any) => {
  editingIndicator.value = record
  Object.assign(indicatorForm, record)
  showAddModal.value = true
}

const deleteIndicator = (record: any) => {
  const index = indicators.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    indicators.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const saveIndicator = async () => {
  if (!indicatorForm.name || !indicatorForm.category || !indicatorForm.weight) {
    Message.warning('请填写完整信息')
    return
  }
  
  saveLoading.value = true
  setTimeout(() => {
    if (editingIndicator.value) {
      const index = indicators.value.findIndex(item => item.id === editingIndicator.value.id)
      if (index > -1) {
        Object.assign(indicators.value[index], indicatorForm)
      }
      Message.success('编辑成功')
    } else {
      indicators.value.push({
        id: Date.now(),
        ...indicatorForm,
        status: true
      })
      Message.success('新增成功')
    }
    saveLoading.value = false
    showAddModal.value = false
    editingIndicator.value = null
    Object.assign(indicatorForm, { name: '', category: '', weight: 0, description: '' })
  }, 500)
}

const initWeightChart = () => {
  if (weightChartRef.value) {
    weightChart = echarts.init(weightChartRef.value)
    weightChart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c}% ({d}%)'
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center'
      },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}\n{c}%'
          },
          data: weightStats.value.map(item => ({
            value: item.weight,
            name: item.category
          }))
        }
      ]
    })
  }
}

onMounted(() => {
  pagination.total = indicators.value.length
  setTimeout(initWeightChart, 100)
})

onUnmounted(() => {
  weightChart?.dispose()
})
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
