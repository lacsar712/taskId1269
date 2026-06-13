<template>
  <div class="page-container">
    <div class="page-header">
      <h2>工艺运行监控</h2>
      <p>实时参数监控 / 工艺流程可视化 / 断面水质数据</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="实时参数监控">
        <div class="filter-bar">
          <a-tag v-if="selectedZone" color="blue" :closable="true" @close="clearZoneFilter">
            <icon-location /> {{ sectionNameMapping[selectedZone] }}
          </a-tag>
          <a-select v-model="selectedSection" placeholder="选择工艺段" style="width: 200px;" allow-clear>
            <a-option value="pretreatment">预处理</a-option>
            <a-option value="bio">生化处理</a-option>
            <a-option value="deep">深度处理</a-option>
            <a-option value="sludge">污泥处理</a-option>
          </a-select>
          <a-button @click="navigateToFactoryMap">
            <template #icon><icon-location /></template>
            {{ mapButtonText }}
          </a-button>
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
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productionApi } from '@/api'

const route = useRoute()
const router = useRouter()

const sectionMapping: Record<string, string> = {
  'inlet': 'pretreatment',
  'grating': 'pretreatment',
  'biological': 'bio',
  'secondary': 'bio',
  'deep': 'deep',
  'outlet': 'deep'
}

const sectionNameMapping: Record<string, string> = {
  'inlet': '进水区',
  'grating': '格栅间',
  'biological': '生化池',
  'secondary': '二沉池',
  'deep': '深度处理',
  'outlet': '出水区'
}

const selectedSection = ref('')
const selectedZone = ref('')
const parameters = ref<any[]>([])

const isFromMap = computed(() => !!route.query.section)

const mapButtonText = computed(() => isFromMap.value ? '返回厂区电子地图' : '打开厂区电子地图')

const navigateToFactoryMap = () => {
  router.push('/production/factory-map')
}

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

const clearZoneFilter = () => {
  selectedZone.value = ''
  selectedSection.value = ''
  fetchParameters()
}

const fetchParameters = async () => {
  try {
    const res: any = await productionApi.getParameters({ 
      process_section: selectedSection.value || undefined,
      zone: selectedZone.value || undefined
    })
    parameters.value = res
  } catch (e) {
    const mockDataByZone: Record<string, any[]> = {
      'inlet': [
        { id: 1, name: '进水流量', code: 'FLOW_IN', unit: 'm³/h', current_value: 650, min_value: 400, max_value: 800, standard_value: 600, status: 'normal' },
        { id: 2, name: '进水COD', code: 'COD_IN', unit: 'mg/L', current_value: 185, min_value: 100, max_value: 300, standard_value: 200, status: 'normal' },
        { id: 3, name: '进水氨氮', code: 'NH3N_IN', unit: 'mg/L', current_value: 38, min_value: 20, max_value: 60, standard_value: 40, status: 'normal' },
        { id: 4, name: '进水pH', code: 'PH_IN', unit: '', current_value: 7.2, min_value: 6, max_value: 9, standard_value: 7.5, status: 'normal' },
        { id: 5, name: '进水SS', code: 'SS_IN', unit: 'mg/L', current_value: 220, min_value: 100, max_value: 350, standard_value: 250, status: 'normal' },
        { id: 6, name: '水温', code: 'TEMP', unit: '℃', current_value: 22.5, min_value: 10, max_value: 35, standard_value: 20, status: 'normal' }
      ],
      'grating': [
        { id: 1, name: '细格栅间隙', code: 'GRATING_GAP', unit: 'mm', current_value: 10, min_value: 5, max_value: 20, standard_value: 10, status: 'normal' },
        { id: 2, name: '栅渣量', code: 'GRATING_RESIDUE', unit: 'm³/d', current_value: 0.8, min_value: 0, max_value: 3, standard_value: 1, status: 'normal' },
        { id: 3, name: '输送皮带转速', code: 'BELT_SPEED', unit: 'm/min', current_value: 5, min_value: 2, max_value: 10, standard_value: 5, status: 'normal' },
        { id: 4, name: '压榨机压力', code: 'PRESSURE', unit: 'MPa', current_value: 0.6, min_value: 0.3, max_value: 0.8, standard_value: 0.5, status: 'normal' }
      ],
      'biological': [
        { id: 1, name: '溶解氧 DO', code: 'DO', unit: 'mg/L', current_value: 1.8, min_value: 1, max_value: 4, standard_value: 2.5, status: 'warning' },
        { id: 2, name: 'MLSS', code: 'MLSS', unit: 'mg/L', current_value: 4200, min_value: 3000, max_value: 5000, standard_value: 4000, status: 'normal' },
        { id: 3, name: '污泥沉降比 SV30', code: 'SV30', unit: '%', current_value: 32, min_value: 20, max_value: 40, standard_value: 30, status: 'normal' },
        { id: 4, name: '污泥指数 SVI', code: 'SVI', unit: 'mL/g', current_value: 120, min_value: 70, max_value: 150, standard_value: 100, status: 'normal' },
        { id: 5, name: '混合液温度', code: 'MIX_TEMP', unit: '℃', current_value: 23, min_value: 15, max_value: 30, standard_value: 20, status: 'normal' },
        { id: 6, name: 'ORP', code: 'ORP', unit: 'mV', current_value: 80, min_value: 50, max_value: 150, standard_value: 100, status: 'warning' },
        { id: 7, name: '内回流比', code: 'INTERNAL_RATIO', unit: '%', current_value: 200, min_value: 100, max_value: 300, standard_value: 200, status: 'normal' },
        { id: 8, name: '外回流比', code: 'EXTERNAL_RATIO', unit: '%', current_value: 80, min_value: 50, max_value: 120, standard_value: 80, status: 'normal' }
      ],
      'secondary': [
        { id: 1, name: '表面负荷', code: 'SURFACE_LOAD', unit: 'm/h', current_value: 1.2, min_value: 0.5, max_value: 1.5, standard_value: 1.0, status: 'normal' },
        { id: 2, name: '溢流堰负荷', code: 'WEIR_LOAD', unit: 'L/(s·m)', current_value: 6, min_value: 2, max_value: 8, standard_value: 5, status: 'normal' },
        { id: 3, name: '停留时间', code: 'HRT', unit: 'h', current_value: 2.5, min_value: 1.5, max_value: 3.0, standard_value: 2.0, status: 'normal' },
        { id: 4, name: '出水SS', code: 'SS_SEC', unit: 'mg/L', current_value: 15, min_value: 5, max_value: 30, standard_value: 20, status: 'normal' },
        { id: 5, name: '污泥界面', code: 'SLUDGE_LEVEL', unit: 'm', current_value: 0.8, min_value: 0.3, max_value: 1.5, standard_value: 1.0, status: 'normal' }
      ],
      'deep': [
        { id: 1, name: '总磷 TP', code: 'TP_DEEP', unit: 'mg/L', current_value: 0.65, min_value: 0.1, max_value: 0.5, standard_value: 0.5, status: 'error' },
        { id: 2, name: '过滤水头损失', code: 'FILTER_HEAD', unit: 'm', current_value: 2.5, min_value: 0.5, max_value: 3.0, standard_value: 2.0, status: 'warning' },
        { id: 3, name: '过滤周期', code: 'FILTER_CYCLE', unit: 'h', current_value: 24, min_value: 12, max_value: 48, standard_value: 24, status: 'normal' },
        { id: 4, name: '反洗强度', code: 'BACKWASH_INT', unit: 'L/(m²·s)', current_value: 15, min_value: 10, max_value: 20, standard_value: 15, status: 'normal' },
        { id: 5, name: '除磷药剂投加量', code: 'DOSAGE_PAC', unit: 'mg/L', current_value: 15, min_value: 5, max_value: 20, standard_value: 10, status: 'warning' },
        { id: 6, name: '出水浊度', code: 'TURBIDITY', unit: 'NTU', current_value: 0.8, min_value: 0.1, max_value: 2.0, standard_value: 1.0, status: 'normal' }
      ],
      'outlet': [
        { id: 1, name: '出水COD', code: 'COD_OUT', unit: 'mg/L', current_value: 52, min_value: 0, max_value: 50, standard_value: 50, status: 'warning' },
        { id: 2, name: '出水氨氮', code: 'NH3N_OUT', unit: 'mg/L', current_value: 4.2, min_value: 0, max_value: 5, standard_value: 5, status: 'normal' },
        { id: 3, name: '出水总磷', code: 'TP_OUT', unit: 'mg/L', current_value: 0.48, min_value: 0, max_value: 0.5, standard_value: 0.5, status: 'normal' },
        { id: 4, name: '出水TN', code: 'TN_OUT', unit: 'mg/L', current_value: 14.5, min_value: 0, max_value: 15, standard_value: 15, status: 'normal' },
        { id: 5, name: '出水SS', code: 'SS_OUT', unit: 'mg/L', current_value: 12, min_value: 0, max_value: 10, standard_value: 10, status: 'warning' },
        { id: 6, name: '出水pH', code: 'PH_OUT', unit: '', current_value: 7.1, min_value: 6, max_value: 9, standard_value: 7.5, status: 'normal' },
        { id: 7, name: '出水流量', code: 'FLOW_OUT', unit: 'm³/h', current_value: 640, min_value: 400, max_value: 800, standard_value: 600, status: 'normal' }
      ]
    }

    if (selectedZone.value && mockDataByZone[selectedZone.value]) {
      parameters.value = mockDataByZone[selectedZone.value]
    } else if (selectedSection.value === 'pretreatment') {
      parameters.value = [
        ...mockDataByZone['inlet'],
        ...mockDataByZone['grating']
      ]
    } else if (selectedSection.value === 'bio') {
      parameters.value = [
        ...mockDataByZone['biological'],
        ...mockDataByZone['secondary']
      ]
    } else if (selectedSection.value === 'deep') {
      parameters.value = [
        ...mockDataByZone['deep'],
        ...mockDataByZone['outlet']
      ]
    } else {
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
}

const initFromRoute = () => {
  const sectionParam = route.query.section as string
  if (sectionParam) {
    selectedZone.value = sectionParam
    if (sectionMapping[sectionParam]) {
      selectedSection.value = sectionMapping[sectionParam]
    }
    fetchParameters()
  }
}

onMounted(() => {
  initFromRoute()
})

watch(() => route.query, (newQuery) => {
  if (newQuery.section) {
    initFromRoute()
  }
}, { deep: true })
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
