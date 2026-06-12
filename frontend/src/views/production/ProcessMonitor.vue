<template>
  <div class="page-container">
    <div class="page-header">
      <h2>工艺运行监控</h2>
      <p>实时参数监控 / 工艺流程可视化 / 断面水质数据</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="实时参数监控">
        <div class="filter-bar">
          <a-select v-model="selectedSection" placeholder="选择工艺段" style="width: 200px;" allow-clear>
            <a-option value="pretreatment">预处理</a-option>
            <a-option value="bio">生化处理</a-option>
            <a-option value="deep">深度处理</a-option>
            <a-option value="sludge">污泥处理</a-option>
          </a-select>
          <a-button type="primary" @click="fetchParameters">
            <template #icon><icon-refresh /></template>
            刷新数据
          </a-button>
        </div>
        
        <div class="params-grid">
          <div class="param-card" v-for="param in parameters" :key="param.id" :class="param.status">
            <div class="param-header">
              <span class="param-name">{{ param.name }}</span>
              <a-tag :color="getStatusColor(param.status)" size="small">
                {{ getStatusText(param.status) }}
              </a-tag>
            </div>
            <div class="param-value">
              {{ param.current_value?.toFixed(2) }}
              <span class="unit">{{ param.unit }}</span>
            </div>
            <div class="param-range">
              标准值: {{ param.standard_value }} | 范围: {{ param.min_value }} - {{ param.max_value }}
            </div>
            <a-progress 
              :percent="getPercent(param)" 
              :status="param.status === 'normal' ? 'success' : 'warning'"
              size="small"
            />
          </div>
        </div>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="工艺流程可视化">
        <div class="process-flow">
          <div class="flow-stage" v-for="(stage, index) in processStages" :key="index">
            <div class="stage-icon" :style="{ background: stage.color }">
              <component :is="stage.icon" />
            </div>
            <div class="stage-info">
              <div class="stage-name">{{ stage.name }}</div>
              <div class="stage-status">{{ stage.status }}</div>
            </div>
            <div class="stage-data">
              <div v-for="item in stage.data" :key="item.label">
                <span class="label">{{ item.label }}:</span>
                <span class="value">{{ item.value }}</span>
              </div>
            </div>
            <icon-arrow-right v-if="index < processStages.length - 1" class="arrow" />
          </div>
        </div>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="断面水质数据">
        <a-table :columns="qualityColumns" :data="qualityData" :pagination="false">
          <template #status="{ record }">
            <a-tag :color="record.is_qualified ? 'green' : 'red'">
              {{ record.is_qualified ? '达标' : '超标' }}
            </a-tag>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { productionApi } from '@/api'

const selectedSection = ref('')
const parameters = ref<any[]>([])

const processStages = ref([
  { 
    name: '进水', 
    icon: 'icon-import', 
    color: '#165DFF', 
    status: '正常运行',
    data: [{ label: '流量', value: '650 m³/h' }, { label: 'COD', value: '185 mg/L' }]
  },
  { 
    name: '格栅池', 
    icon: 'icon-filter', 
    color: '#0FC6C2', 
    status: '正常运行',
    data: [{ label: '格栅间隙', value: '10 mm' }, { label: '运行状态', value: '自动' }]
  },
  { 
    name: '沉砂池', 
    icon: 'icon-layers', 
    color: '#722ED1', 
    status: '正常运行',
    data: [{ label: '停留时间', value: '30 min' }, { label: 'SS去除', value: '65%' }]
  },
  { 
    name: '生化池', 
    icon: 'icon-experiment', 
    color: '#F77234', 
    status: '正常运行',
    data: [{ label: 'DO', value: '2.5 mg/L' }, { label: 'MLSS', value: '4000 mg/L' }]
  },
  { 
    name: '二沉池', 
    icon: 'icon-common', 
    color: '#00B42A', 
    status: '正常运行',
    data: [{ label: '出水SS', value: '15 mg/L' }, { label: '污泥回流', value: '80%' }]
  },
  { 
    name: '出水', 
    icon: 'icon-export', 
    color: '#14C9C9', 
    status: '达标排放',
    data: [{ label: 'COD', value: '28 mg/L' }, { label: '氨氮', value: '3.5 mg/L' }]
  }
])

const qualityColumns = [
  { title: '监测断面', dataIndex: 'section' },
  { title: 'COD (mg/L)', dataIndex: 'cod' },
  { title: '氨氮 (mg/L)', dataIndex: 'nh3n' },
  { title: 'SS (mg/L)', dataIndex: 'ss' },
  { title: 'pH', dataIndex: 'ph' },
  { title: '状态', slotName: 'status' }
]

const qualityData = ref([
  { section: '进水口', cod: 185, nh3n: 38, ss: 220, ph: 7.2, is_qualified: true },
  { section: '生化池出口', cod: 45, nh3n: 8, ss: 35, ph: 7.1, is_qualified: true },
  { section: '二沉池出口', cod: 32, nh3n: 4.5, ss: 18, ph: 7.0, is_qualified: true },
  { section: '总出水口', cod: 28, nh3n: 3.5, ss: 12, ph: 7.1, is_qualified: true }
])

const getStatusColor = (status: string) => {
  const map: Record<string, string> = {
    normal: 'green',
    warning: 'orange',
    error: 'red'
  }
  return map[status] || 'gray'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    normal: '正常',
    warning: '警告',
    error: '异常'
  }
  return map[status] || '未知'
}

const getPercent = (param: any) => {
  if (!param.min_value || !param.max_value) return 50
  const range = param.max_value - param.min_value
  return Math.min(100, Math.max(0, ((param.current_value - param.min_value) / range) * 100))
}

const fetchParameters = async () => {
  try {
    const res: any = await productionApi.getParameters({ process_section: selectedSection.value || undefined })
    parameters.value = res
  } catch (e) {
    // 使用模拟数据
    parameters.value = [
      { id: 1, name: '溶解氧 DO', code: 'DO', unit: 'mg/L', current_value: 2.5, min_value: 1, max_value: 4, standard_value: 2, status: 'normal' },
      { id: 2, name: 'pH值', code: 'PH', unit: '', current_value: 7.2, min_value: 6, max_value: 9, standard_value: 7, status: 'normal' },
      { id: 3, name: '水温', code: 'TEMP', unit: '℃', current_value: 22.5, min_value: 10, max_value: 35, standard_value: 20, status: 'normal' },
      { id: 4, name: 'MLSS', code: 'MLSS', unit: 'mg/L', current_value: 4200, min_value: 3000, max_value: 5000, standard_value: 4000, status: 'normal' },
      { id: 5, name: '污泥沉降比', code: 'SV30', unit: '%', current_value: 32, min_value: 20, max_value: 40, standard_value: 30, status: 'normal' },
      { id: 6, name: '进水流量', code: 'FLOW_IN', unit: 'm³/h', current_value: 650, min_value: 400, max_value: 800, standard_value: 600, status: 'normal' }
    ]
  }
}

onMounted(() => {
  fetchParameters()
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

@media (max-width: 1200px) {
  .params-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .params-grid {
    grid-template-columns: 1fr;
  }
}

.param-card {
  background: #fff;
  border: 1px solid #e5e6eb;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
}

.param-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.param-card.warning {
  border-color: #ff7d00;
  background: #fff7e8;
}

.param-card.error {
  border-color: #f53f3f;
  background: #ffece8;
}

.param-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.param-name {
  font-weight: 500;
  color: #1d2129;
}

.param-value {
  font-size: 32px;
  font-weight: 600;
  color: #165DFF;
  margin-bottom: 8px;
}

.param-value .unit {
  font-size: 14px;
  color: #86909c;
  margin-left: 4px;
}

.param-range {
  font-size: 12px;
  color: #86909c;
  margin-bottom: 8px;
}

.process-flow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f3ff 100%);
  border-radius: 12px;
  overflow-x: auto;
}

.flow-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  min-width: 140px;
}

.stage-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 28px;
  margin-bottom: 12px;
}

.stage-info {
  text-align: center;
  margin-bottom: 8px;
}

.stage-name {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.stage-status {
  font-size: 12px;
  color: #00b42a;
}

.stage-data {
  background: #fff;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
}

.stage-data .label {
  color: #86909c;
}

.stage-data .value {
  color: #1d2129;
  font-weight: 500;
  margin-left: 4px;
}

.arrow {
  font-size: 24px;
  color: #165DFF;
  margin: 0 10px;
}
</style>
