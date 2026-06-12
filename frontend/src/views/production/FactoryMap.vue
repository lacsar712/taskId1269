<template>
  <div class="page-container factory-map">
    <div class="page-header">
      <h2>厂区电子地图</h2>
      <p>以空间视角总览全厂运行态势，点击各区域查看详细运行信息</p>
    </div>

    <div class="map-container">
      <div class="map-wrapper">
        <svg
          class="factory-svg"
          viewBox="0 0 1000 600"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.15" />
            </filter>
            <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#f0f5ff;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#e8f3ff;stop-opacity:1" />
            </linearGradient>
          </defs>

          <rect x="0" y="0" width="1000" height="600" fill="url(#bgGradient)" rx="8" />

          <g class="flow-lines" stroke="#c9cdd4" stroke-width="3" stroke-dasharray="8,4" fill="none">
            <path d="M 120 150 Q 200 150 200 200 Q 200 250 280 250" />
            <path d="M 360 250 Q 420 250 420 300 Q 420 350 500 350" />
            <path d="M 580 350 Q 640 350 640 400 Q 640 450 720 450" />
            <path d="M 800 450 Q 860 450 860 400 Q 860 300 880 250" />
          </g>

          <g
            v-for="zone in zones"
            :key="zone.id"
            class="zone-group"
            :class="{ active: selectedZone?.id === zone.id, [zone.status]: true }"
            @click="handleZoneClick(zone, $event)"
            @mouseenter="handleZoneHover(zone, $event)"
            @mouseleave="handleZoneLeave"
          >
            <rect
              :x="zone.x"
              :y="zone.y"
              :width="zone.width"
              :height="zone.height"
              :fill="zone.color"
              :rx="8"
              filter="url(#shadow)"
              class="zone-rect"
            />
            <rect
              :x="zone.x"
              :y="zone.y"
              :width="zone.width"
              :height="zone.height"
              fill="transparent"
              :rx="8"
              class="zone-hitarea"
            />

            <text
              :x="zone.x + zone.width / 2"
              :y="zone.y + 30"
              text-anchor="middle"
              class="zone-name"
            >
              {{ zone.name }}
            </text>

            <text
              :x="zone.x + zone.width / 2"
              :y="zone.y + 55"
              text-anchor="middle"
              class="zone-status"
            >
              <tspan :fill="getStatusColor(zone.status)">{{ getStatusText(zone.status) }}</tspan>
            </text>

            <g class="zone-stats">
              <rect
                :x="zone.x + 15"
                :y="zone.y + 70"
                :width="zone.width - 30"
                height="60"
                rx="6"
                fill="rgba(255,255,255,0.85)"
              />
              <g v-for="(stat, idx) in zone.stats" :key="stat.label">
                <text
                  :x="zone.x + 25"
                  :y="zone.y + 92 + idx * 18"
                  class="stat-label"
                >
                  {{ stat.label }}:
                </text>
                <text
                  :x="zone.x + zone.width - 25"
                  :y="zone.y + 92 + idx * 18"
                  text-anchor="end"
                  class="stat-value"
                  :class="{ warning: stat.isWarning }"
                >
                  {{ stat.value }}
                </text>
              </g>
            </g>

            <g v-if="zone.alarmCount > 0" class="alarm-badge">
              <circle
                :cx="zone.x + zone.width - 15"
                :cy="zone.y + 15"
                r="16"
                fill="#f53f3f"
              />
              <text
                :x="zone.x + zone.width - 15"
                :y="zone.y + 20"
                text-anchor="middle"
                class="alarm-count"
              >
                {{ zone.alarmCount }}
              </text>
            </g>

            <g class="equipment-icon">
              <circle
                :cx="zone.x + zone.width / 2"
                :cy="zone.y + zone.height - 25"
                r="18"
                fill="#fff"
                stroke="#e5e6eb"
                stroke-width="2"
              />
              <text
                :x="zone.x + zone.width / 2"
                :y="zone.y + zone.height - 20"
                text-anchor="middle"
                class="equipment-count"
              >
                {{ zone.equipmentRunning }}/{{ zone.equipmentTotal }}
              </text>
            </g>
          </g>

          <g class="direction-indicator">
            <path d="M 950 30 L 950 70 M 940 40 L 950 30 L 960 40" stroke="#4e5969" stroke-width="2" fill="none" />
            <text x="950" y="85" text-anchor="middle" class="direction-text">N</text>
          </g>
        </svg>

        <div
          v-if="hoverZone && !selectedZone"
          class="hover-tooltip"
          :style="tooltipStyle"
        >
          <div class="tooltip-header">
            <span class="tooltip-name">{{ hoverZone.name }}</span>
            <a-tag :color="getStatusColor(hoverZone.status)" size="small">
              {{ getStatusText(hoverZone.status) }}
            </a-tag>
          </div>
          <div class="tooltip-stats">
            <div v-for="stat in hoverZone.stats" :key="stat.label" class="tooltip-stat">
              <span class="stat-label">{{ stat.label }}</span>
              <span class="stat-value" :class="{ warning: stat.isWarning }">{{ stat.value }}</span>
            </div>
          </div>
          <div class="tooltip-footer">
            <icon-info-circle /> 点击查看详情
          </div>
        </div>
      </div>

      <div class="map-legend">
        <div class="legend-title">图例说明</div>
        <div class="legend-items">
          <div class="legend-item">
            <span class="legend-color normal"></span>
            <span>正常运行</span>
          </div>
          <div class="legend-item">
            <span class="legend-color warning"></span>
            <span>参数预警</span>
          </div>
          <div class="legend-item">
            <span class="legend-color error"></span>
            <span>异常告警</span>
          </div>
          <div class="legend-item">
            <span class="legend-icon">
              <icon-notification />
            </span>
            <span>当前告警数</span>
          </div>
          <div class="legend-item">
            <span class="legend-icon">
              <icon-computer />
            </span>
            <span>运行/总设备数</span>
          </div>
        </div>
      </div>
    </div>

    <a-modal
      v-model:visible="showDetailModal"
      :title="selectedZone?.name + ' - 运行详情'"
      :footer="null"
      :width="680"
      wrapClassName="zone-detail-modal"
    >
      <div v-if="selectedZone" class="zone-detail">
        <div class="detail-header">
          <div class="detail-status" :class="selectedZone.status">
            <icon-check-circle v-if="selectedZone.status === 'normal'" />
            <icon-exclamation-circle v-else-if="selectedZone.status === 'warning'" />
            <icon-close-circle v-else />
            {{ getStatusText(selectedZone.status) }}
          </div>
          <div class="detail-update-time">
            <icon-sync />
            数据更新于 {{ updateTime }}
          </div>
        </div>

        <a-tabs v-model:activeKey="activeTab">
          <a-tab-pane key="params" title="工艺参数">
            <div class="params-section">
              <div class="section-title">
                <icon-bar-chart />
                关键工艺参数实时读数
              </div>
              <div class="params-list">
                <div
                  v-for="param in selectedZone.parameters"
                  :key="param.code"
                  class="param-item"
                  :class="param.status"
                >
                  <div class="param-info">
                    <span class="param-name">{{ param.name }}</span>
                    <a-tag v-if="param.status !== 'normal'" :color="getStatusColor(param.status)" size="small">
                      {{ param.status === 'warning' ? '偏高' : '超标' }}
                    </a-tag>
                  </div>
                  <div class="param-value">
                    <span class="value-num">{{ param.value }}</span>
                    <span class="value-unit">{{ param.unit }}</span>
                  </div>
                  <div class="param-range">
                    标准值: {{ param.standard }} {{ param.unit }}
                    <span v-if="param.min"> | 范围: {{ param.min }} - {{ param.max }}</span>
                  </div>
                  <a-progress
                    :percent="getParamPercent(param)"
                    :status="param.status === 'normal' ? 'success' : param.status === 'warning' ? 'warning' : 'danger'"
                    size="small"
                  />
                </div>
              </div>
            </div>
          </a-tab-pane>

          <a-tab-pane key="alarms" title="最近告警">
            <div class="alarms-section">
              <div class="section-title">
                <icon-notification />
                最近告警记录
                <a-tag v-if="selectedZone.recentAlarms.length > 0" color="red" size="small">
                  {{ selectedZone.recentAlarms.length }} 条
                </a-tag>
              </div>
              <a-empty v-if="selectedZone.recentAlarms.length === 0" description="暂无告警记录" />
              <div v-else class="alarms-list">
                <div
                  v-for="alarm in selectedZone.recentAlarms"
                  :key="alarm.id"
                  class="alarm-item"
                  :class="alarm.level"
                >
                  <div class="alarm-level">
                    <a-tag :color="getAlarmColor(alarm.level)">
                      {{ getAlarmLevelText(alarm.level) }}
                    </a-tag>
                  </div>
                  <div class="alarm-content">
                    <div class="alarm-title">{{ alarm.title }}</div>
                    <div class="alarm-desc">{{ alarm.description }}</div>
                    <div class="alarm-time">
                      <icon-clock /> {{ alarm.time }}
                    </div>
                  </div>
                  <a-button size="small" type="outline" @click="viewAlarmDetail(alarm)">
                    查看
                  </a-button>
                </div>
              </div>
            </div>
          </a-tab-pane>

          <a-tab-pane key="equipment" title="设备状态">
            <div class="equipment-section">
              <div class="section-title">
                <icon-computer />
                在运设备概况
              </div>
              <div class="equipment-stats">
                <div class="equip-stat running">
                  <span class="stat-num">{{ selectedZone.equipmentRunning }}</span>
                  <span class="stat-label">运行中</span>
                </div>
                <div class="equip-stat standby">
                  <span class="stat-num">{{ selectedZone.equipmentStandby }}</span>
                  <span class="stat-label">备用</span>
                </div>
                <div class="equip-stat fault">
                  <span class="stat-num">{{ selectedZone.equipmentFault }}</span>
                  <span class="stat-label">故障</span>
                </div>
                <div class="equip-stat total">
                  <span class="stat-num">{{ selectedZone.equipmentTotal }}</span>
                  <span class="stat-label">总计</span>
                </div>
              </div>
              <div class="equipment-list">
                <div
                  v-for="equip in selectedZone.equipmentList"
                  :key="equip.id"
                  class="equip-item"
                  :class="equip.status"
                >
                  <div class="equip-status-dot"></div>
                  <div class="equip-info">
                    <span class="equip-name">{{ equip.name }}</span>
                    <span class="equip-type">{{ equip.type }}</span>
                  </div>
                  <a-tag :color="getEquipStatusColor(equip.status)" size="small">
                    {{ getEquipStatusText(equip.status) }}
                  </a-tag>
                </div>
              </div>
            </div>
          </a-tab-pane>
        </a-tabs>

        <div class="detail-actions">
          <a-button type="primary" @click="jumpToProcessMonitor">
            <template #icon><icon-dashboard /></template>
            跳转至工艺运行监控
          </a-button>
          <a-button @click="showDetailModal = false">
            关闭
          </a-button>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { productionApi } from '@/api'

const router = useRouter()

const loading = ref(false)
const showDetailModal = ref(false)
const selectedZone = ref<any>(null)
const hoverZone = ref<any>(null)
const activeTab = ref('params')
const updateTime = ref('')
const tooltipPosition = reactive({ x: 0, y: 0 })

const tooltipStyle = computed(() => ({
  left: tooltipPosition.x + 'px',
  top: tooltipPosition.y + 'px'
}))

const zones = ref<any[]>([])

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
    normal: '正常运行',
    warning: '参数预警',
    error: '异常告警'
  }
  return map[status] || '未知'
}

const getAlarmColor = (level: string) => {
  const map: Record<string, string> = {
    urgent: 'red',
    warning: 'orange',
    normal: 'blue'
  }
  return map[level] || 'gray'
}

const getAlarmLevelText = (level: string) => {
  const map: Record<string, string> = {
    urgent: '紧急',
    warning: '警告',
    normal: '一般'
  }
  return map[level] || '未知'
}

const getEquipStatusColor = (status: string) => {
  const map: Record<string, string> = {
    running: 'green',
    standby: 'blue',
    fault: 'red',
    maintenance: 'orange'
  }
  return map[status] || 'gray'
}

const getEquipStatusText = (status: string) => {
  const map: Record<string, string> = {
    running: '运行中',
    standby: '备用',
    fault: '故障',
    maintenance: '维护中'
  }
  return map[status] || '未知'
}

const getParamPercent = (param: any) => {
  if (!param.min || !param.max) return 50
  const range = param.max - param.min
  return Math.min(100, Math.max(0, ((param.value - param.min) / range) * 100))
}

const handleZoneClick = (zone: any, event: MouseEvent) => {
  selectedZone.value = zone
  showDetailModal.value = true
  activeTab.value = 'params'
}

const handleZoneHover = (zone: any, event: MouseEvent) => {
  hoverZone.value = zone
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const mapRect = document.querySelector('.map-wrapper')?.getBoundingClientRect()
  if (mapRect) {
    tooltipPosition.x = event.clientX - mapRect.left + 15
    tooltipPosition.y = event.clientY - mapRect.top + 15
  }
}

const handleZoneLeave = () => {
  hoverZone.value = null
}

const jumpToProcessMonitor = () => {
  if (selectedZone.value) {
    router.push({
      path: '/production/monitor',
      query: {
        section: selectedZone.value.id
      }
    })
    showDetailModal.value = false
    Message.success(`已跳转至工艺运行监控 - ${selectedZone.value.name}`)
  }
}

const viewAlarmDetail = (alarm: any) => {
  router.push({
    path: '/production/alarm',
    query: {
      id: alarm.id,
      zone: selectedZone.value?.id
    }
  })
  showDetailModal.value = false
}

const fetchZoneData = async () => {
  loading.value = true
  try {
    const res: any = await productionApi.getFactoryMapData()
    if (res && res.zones) {
      zones.value = res.zones
    } else {
      generateMockData()
    }
  } catch (e) {
    generateMockData()
  } finally {
    loading.value = false
    updateTime.value = new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }
}

const generateMockData = () => {
  zones.value = [
    {
      id: 'inlet',
      name: '进水区',
      x: 50,
      y: 100,
      width: 140,
      height: 180,
      color: '#e8f3ff',
      status: 'normal',
      alarmCount: 0,
      equipmentRunning: 3,
      equipmentStandby: 1,
      equipmentFault: 0,
      equipmentTotal: 4,
      stats: [
        { label: '进水流量', value: '650 m³/h', isWarning: false },
        { label: 'COD', value: '185 mg/L', isWarning: false },
        { label: 'pH', value: '7.2', isWarning: false }
      ],
      parameters: [
        { name: '进水流量', code: 'FLOW_IN', value: 650, unit: 'm³/h', standard: 600, min: 400, max: 800, status: 'normal' },
        { name: '进水COD', code: 'COD_IN', value: 185, unit: 'mg/L', standard: 200, min: 100, max: 300, status: 'normal' },
        { name: '进水氨氮', code: 'NH3N_IN', value: 38, unit: 'mg/L', standard: 40, min: 20, max: 60, status: 'normal' },
        { name: '进水pH', code: 'PH_IN', value: 7.2, unit: '', standard: 7.5, min: 6, max: 9, status: 'normal' },
        { name: '进水SS', code: 'SS_IN', value: 220, unit: 'mg/L', standard: 250, min: 100, max: 350, status: 'normal' },
        { name: '水温', code: 'TEMP', value: 22.5, unit: '℃', standard: 20, min: 10, max: 35, status: 'normal' }
      ],
      recentAlarms: [],
      equipmentList: [
        { id: 1, name: '进水提升泵1#', type: '离心泵', status: 'running' },
        { id: 2, name: '进水提升泵2#', type: '离心泵', status: 'running' },
        { id: 3, name: '进水提升泵3#', type: '离心泵', status: 'running' },
        { id: 4, name: '进水提升泵4#', type: '离心泵', status: 'standby' }
      ]
    },
    {
      id: 'grating',
      name: '格栅间',
      x: 240,
      y: 180,
      width: 140,
      height: 160,
      color: '#e8ffea',
      status: 'normal',
      alarmCount: 0,
      equipmentRunning: 4,
      equipmentStandby: 2,
      equipmentFault: 0,
      equipmentTotal: 6,
      stats: [
        { label: '格栅间隙', value: '10 mm', isWarning: false },
        { label: '运行模式', value: '自动', isWarning: false },
        { label: 'SS去除', value: '65%', isWarning: false }
      ],
      parameters: [
        { name: '细格栅间隙', code: 'GRATING_GAP', value: 10, unit: 'mm', standard: 10, min: 5, max: 20, status: 'normal' },
        { name: '栅渣量', code: 'GRATING_RESIDUE', value: 0.8, unit: 'm³/d', standard: 1, min: 0, max: 3, status: 'normal' },
        { name: '输送皮带转速', code: 'BELT_SPEED', value: 5, unit: 'm/min', standard: 5, min: 2, max: 10, status: 'normal' },
        { name: '压榨机压力', code: 'PRESSURE', value: 0.6, unit: 'MPa', standard: 0.5, min: 0.3, max: 0.8, status: 'normal' }
      ],
      recentAlarms: [],
      equipmentList: [
        { id: 1, name: '粗格栅1#', type: '回转式', status: 'running' },
        { id: 2, name: '粗格栅2#', type: '回转式', status: 'running' },
        { id: 3, name: '细格栅1#', type: '转鼓式', status: 'running' },
        { id: 4, name: '细格栅2#', type: '转鼓式', status: 'running' },
        { id: 5, name: '螺旋输送机', type: '无轴', status: 'standby' },
        { id: 6, name: '栅渣压榨机', type: '螺旋式', status: 'standby' }
      ]
    },
    {
      id: 'biological',
      name: '生化池',
      x: 460,
      y: 280,
      width: 160,
      height: 180,
      color: '#fff7e8',
      status: 'warning',
      alarmCount: 2,
      equipmentRunning: 8,
      equipmentStandby: 2,
      equipmentFault: 1,
      equipmentTotal: 11,
      stats: [
        { label: 'DO', value: '1.8 mg/L', isWarning: true },
        { label: 'MLSS', value: '4200 mg/L', isWarning: false },
        { label: 'SV30', value: '32%', isWarning: false }
      ],
      parameters: [
        { name: '溶解氧 DO', code: 'DO', value: 1.8, unit: 'mg/L', standard: 2.5, min: 1, max: 4, status: 'warning' },
        { name: 'MLSS', code: 'MLSS', value: 4200, unit: 'mg/L', standard: 4000, min: 3000, max: 5000, status: 'normal' },
        { name: '污泥沉降比 SV30', code: 'SV30', value: 32, unit: '%', standard: 30, min: 20, max: 40, status: 'normal' },
        { name: '污泥指数 SVI', code: 'SVI', value: 120, unit: 'mL/g', standard: 100, min: 70, max: 150, status: 'normal' },
        { name: '混合液温度', code: 'MIX_TEMP', value: 23, unit: '℃', standard: 20, min: 15, max: 30, status: 'normal' },
        { name: 'ORP', code: 'ORP', value: 80, unit: 'mV', standard: 100, min: 50, max: 150, status: 'warning' },
        { name: '内回流比', code: 'INTERNAL_RATIO', value: 200, unit: '%', standard: 200, min: 100, max: 300, status: 'normal' },
        { name: '外回流比', code: 'EXTERNAL_RATIO', value: 80, unit: '%', standard: 80, min: 50, max: 120, status: 'normal' }
      ],
      recentAlarms: [
        { id: 1, title: '生化池DO偏低', description: '好氧区溶解氧持续低于2.0mg/L，可能影响硝化效果', level: 'warning', time: '2024-01-15 14:25:00' },
        { id: 2, title: 'ORP值偏低', description: '厌氧区ORP值低于正常范围，需检查进水碳源', level: 'normal', time: '2024-01-15 13:10:00' }
      ],
      equipmentList: [
        { id: 1, name: '好氧区曝气盘1#', type: '微孔曝气', status: 'running' },
        { id: 2, name: '好氧区曝气盘2#', type: '微孔曝气', status: 'running' },
        { id: 3, name: '厌氧区搅拌器1#', type: '潜水搅拌', status: 'running' },
        { id: 4, name: '厌氧区搅拌器2#', type: '潜水搅拌', status: 'fault' },
        { id: 5, name: '缺氧区搅拌器1#', type: '潜水搅拌', status: 'running' },
        { id: 6, name: '内回流泵1#', type: '轴流泵', status: 'running' },
        { id: 7, name: '内回流泵2#', type: '轴流泵', status: 'running' },
        { id: 8, name: '外回流泵1#', type: '离心泵', status: 'running' },
        { id: 9, name: '外回流泵2#', type: '离心泵', status: 'running' },
        { id: 10, name: '排泥泵1#', type: '离心泵', status: 'standby' },
        { id: 11, name: '排泥泵2#', type: '离心泵', status: 'standby' }
      ]
    },
    {
      id: 'secondary',
      name: '二沉池',
      x: 680,
      y: 380,
      width: 140,
      height: 160,
      color: '#f0f5ff',
      status: 'normal',
      alarmCount: 0,
      equipmentRunning: 3,
      equipmentStandby: 1,
      equipmentFault: 0,
      equipmentTotal: 4,
      stats: [
        { label: '出水SS', value: '15 mg/L', isWarning: false },
        { label: '污泥回流', value: '80%', isWarning: false },
        { label: '表面负荷', value: '1.2 m/h', isWarning: false }
      ],
      parameters: [
        { name: '表面负荷', code: 'SURFACE_LOAD', value: 1.2, unit: 'm/h', standard: 1.0, min: 0.5, max: 1.5, status: 'normal' },
        { name: '溢流堰负荷', code: 'WEIR_LOAD', value: 6, unit: 'L/(s·m)', standard: 5, min: 2, max: 8, status: 'normal' },
        { name: '停留时间', code: 'HRT', value: 2.5, unit: 'h', standard: 2.0, min: 1.5, max: 3.0, status: 'normal' },
        { name: '出水SS', code: 'SS_SEC', value: 15, unit: 'mg/L', standard: 20, min: 5, max: 30, status: 'normal' },
        { name: '污泥界面', code: 'SLUDGE_LEVEL', value: 0.8, unit: 'm', standard: 1.0, min: 0.3, max: 1.5, status: 'normal' }
      ],
      recentAlarms: [],
      equipmentList: [
        { id: 1, name: '二沉池1#吸泥机', type: '周边传动', status: 'running' },
        { id: 2, name: '二沉池2#吸泥机', type: '周边传动', status: 'running' },
        { id: 3, name: '二沉池3#吸泥机', type: '周边传动', status: 'running' },
        { id: 4, name: '二沉池4#吸泥机', type: '周边传动', status: 'standby' }
      ]
    },
    {
      id: 'deep',
      name: '深度处理',
      x: 860,
      y: 300,
      width: 100,
      height: 180,
      color: '#ffe8e8',
      status: 'error',
      alarmCount: 1,
      equipmentRunning: 5,
      equipmentStandby: 1,
      equipmentFault: 1,
      equipmentTotal: 7,
      stats: [
        { label: '出水TP', value: '0.65 mg/L', isWarning: true },
        { label: '过滤周期', value: '24 h', isWarning: false },
        { label: '反洗频率', value: '2次/天', isWarning: false }
      ],
      parameters: [
        { name: '总磷 TP', code: 'TP_DEEP', value: 0.65, unit: 'mg/L', standard: 0.5, min: 0.1, max: 0.5, status: 'error' },
        { name: '过滤水头损失', code: 'FILTER_HEAD', value: 2.5, unit: 'm', standard: 2.0, min: 0.5, max: 3.0, status: 'warning' },
        { name: '过滤周期', code: 'FILTER_CYCLE', value: 24, unit: 'h', standard: 24, min: 12, max: 48, status: 'normal' },
        { name: '反洗强度', code: 'BACKWASH_INT', value: 15, unit: 'L/(m²·s)', standard: 15, min: 10, max: 20, status: 'normal' },
        { name: '除磷药剂投加量', code: 'DOSAGE_PAC', value: 15, unit: 'mg/L', standard: 10, min: 5, max: 20, status: 'warning' },
        { name: '出水浊度', code: 'TURBIDITY', value: 0.8, unit: 'NTU', standard: 1.0, min: 0.1, max: 2.0, status: 'normal' }
      ],
      recentAlarms: [
        { id: 1, title: '深度处理TP超标', description: '出水总磷0.65mg/L，超过排放标准0.5mg/L，需加大除磷药剂投加量', level: 'urgent', time: '2024-01-15 15:30:00' }
      ],
      equipmentList: [
        { id: 1, name: 'V型滤池1#', type: '深床过滤', status: 'running' },
        { id: 2, name: 'V型滤池2#', type: '深床过滤', status: 'running' },
        { id: 3, name: 'V型滤池3#', type: '深床过滤', status: 'running' },
        { id: 4, name: '反洗水泵1#', type: '离心泵', status: 'running' },
        { id: 5, name: '反洗风机1#', type: '罗茨风机', status: 'running' },
        { id: 6, name: '反洗风机2#', type: '罗茨风机', status: 'standby' },
        { id: 7, name: 'PAC投加泵', type: '计量泵', status: 'fault' }
      ]
    },
    {
      id: 'outlet',
      name: '出水区',
      x: 860,
      y: 100,
      width: 100,
      height: 160,
      color: '#e8fffc',
      status: 'warning',
      alarmCount: 1,
      equipmentRunning: 2,
      equipmentStandby: 1,
      equipmentFault: 0,
      equipmentTotal: 3,
      stats: [
        { label: '出水COD', value: '52 mg/L', isWarning: true },
        { label: '出水氨氮', value: '4.2 mg/L', isWarning: false },
        { label: '出水流量', value: '640 m³/h', isWarning: false }
      ],
      parameters: [
        { name: '出水COD', code: 'COD_OUT', value: 52, unit: 'mg/L', standard: 50, min: 0, max: 50, status: 'warning' },
        { name: '出水氨氮', code: 'NH3N_OUT', value: 4.2, unit: 'mg/L', standard: 5, min: 0, max: 5, status: 'normal' },
        { name: '出水总磷', code: 'TP_OUT', value: 0.48, unit: 'mg/L', standard: 0.5, min: 0, max: 0.5, status: 'normal' },
        { name: '出水TN', code: 'TN_OUT', value: 14.5, unit: 'mg/L', standard: 15, min: 0, max: 15, status: 'normal' },
        { name: '出水SS', code: 'SS_OUT', value: 12, unit: 'mg/L', standard: 10, min: 0, max: 10, status: 'warning' },
        { name: '出水pH', code: 'PH_OUT', value: 7.1, unit: '', standard: 7.5, min: 6, max: 9, status: 'normal' },
        { name: '出水流量', code: 'FLOW_OUT', value: 640, unit: 'm³/h', standard: 600, min: 400, max: 800, status: 'normal' }
      ],
      recentAlarms: [
        { id: 1, title: '出水COD接近限值', description: '出水COD为52mg/L，接近排放标准50mg/L，需关注处理效果', level: 'warning', time: '2024-01-15 15:00:00' }
      ],
      equipmentList: [
        { id: 1, name: '出水在线监测仪', type: 'COD/氨氮/TP', status: 'running' },
        { id: 2, name: '电磁流量计', type: '智能型', status: 'running' },
        { id: 3, name: '尾水消毒装置', type: '紫外线', status: 'standby' }
      ]
    }
  ]
}

let refreshTimer: any = null

onMounted(() => {
  fetchZoneData()
  refreshTimer = setInterval(() => {
    fetchZoneData()
  }, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.factory-map {
  min-height: calc(100vh - 120px);
}

.map-container {
  display: flex;
  gap: 20px;
}

.map-wrapper {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  padding: 20px;
  position: relative;
  min-height: 650px;
}

.factory-svg {
  width: 100%;
  height: auto;
  max-height: 600px;
}

.zone-group {
  cursor: pointer;
  transition: all 0.3s ease;
}

.zone-group:hover .zone-rect {
  filter: url(#shadow) brightness(1.05);
  stroke-width: 3px;
}

.zone-group.active .zone-rect {
  stroke: #165dff;
  stroke-width: 3px;
}

.zone-group.warning .zone-rect {
  stroke: #ff7d00;
  stroke-width: 2px;
}

.zone-group.error .zone-rect {
  stroke: #f53f3f;
  stroke-width: 2px;
}

.zone-hitarea {
  cursor: pointer;
}

.zone-name {
  font-size: 16px;
  font-weight: 600;
  fill: #1d2129;
}

.zone-status {
  font-size: 12px;
}

.stat-label {
  font-size: 11px;
  fill: #86909c;
}

.stat-value {
  font-size: 11px;
  font-weight: 600;
  fill: #1d2129;
}

.stat-value.warning {
  fill: #f53f3f;
}

.alarm-count {
  font-size: 12px;
  font-weight: 600;
  fill: #fff;
}

.equipment-count {
  font-size: 10px;
  font-weight: 600;
  fill: #4e5969;
}

.direction-text {
  font-size: 12px;
  fill: #4e5969;
  font-weight: 500;
}

.flow-lines path {
  animation: flowDash 2s linear infinite;
}

@keyframes flowDash {
  to {
    stroke-dashoffset: -24;
  }
}

.hover-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.85);
  color: #fff;
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 12px;
  pointer-events: none;
  z-index: 100;
  min-width: 180px;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.tooltip-name {
  font-weight: 600;
  font-size: 14px;
}

.tooltip-stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.tooltip-stat {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.tooltip-stat .stat-label {
  color: rgba(255, 255, 255, 0.7);
}

.tooltip-stat .stat-value {
  font-weight: 500;
}

.tooltip-stat .stat-value.warning {
  color: #ff7d00;
}

.tooltip-footer {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  gap: 4px;
}

.map-legend {
  width: 160px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  padding: 16px;
  height: fit-content;
}

.legend-title {
  font-size: 14px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e6eb;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #4e5969;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid #e5e6eb;
}

.legend-color.normal {
  background: #e8ffea;
  border-color: #00b42a;
}

.legend-color.warning {
  background: #fff7e8;
  border-color: #ff7d00;
}

.legend-color.error {
  background: #ffe8e8;
  border-color: #f53f3f;
}

.legend-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #165dff;
}

.zone-detail {
  padding: 8px 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e6eb;
}

.detail-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: 500;
  font-size: 14px;
}

.detail-status.normal {
  background: #e8ffea;
  color: #00b42a;
}

.detail-status.warning {
  background: #fff7e8;
  color: #ff7d00;
}

.detail-status.error {
  background: #ffece8;
  color: #f53f3f;
}

.detail-update-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #86909c;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 16px;
}

.params-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.param-item {
  background: #f7f8fa;
  border: 1px solid #e5e6eb;
  border-radius: 8px;
  padding: 12px;
  transition: all 0.3s;
}

.param-item.warning {
  border-color: #ff7d00;
  background: #fff7e8;
}

.param-item.error {
  border-color: #f53f3f;
  background: #ffece8;
}

.param-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.param-name {
  font-weight: 500;
  color: #1d2129;
  font-size: 13px;
}

.param-value {
  margin-bottom: 8px;
}

.value-num {
  font-size: 24px;
  font-weight: 600;
  color: #165dff;
}

.param-item.warning .value-num {
  color: #ff7d00;
}

.param-item.error .value-num {
  color: #f53f3f;
}

.value-unit {
  font-size: 12px;
  color: #86909c;
  margin-left: 4px;
}

.param-range {
  font-size: 11px;
  color: #86909c;
  margin-bottom: 8px;
}

.alarms-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alarm-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f7f8fa;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  border-left: 3px solid #e5e6eb;
}

.alarm-item.urgent {
  border-left-color: #f53f3f;
}

.alarm-item.warning {
  border-left-color: #ff7d00;
}

.alarm-item.normal {
  border-left-color: #165dff;
}

.alarm-content {
  flex: 1;
}

.alarm-title {
  font-weight: 500;
  color: #1d2129;
  margin-bottom: 4px;
}

.alarm-desc {
  font-size: 12px;
  color: #4e5969;
  margin-bottom: 4px;
}

.alarm-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #86909c;
}

.equipment-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.equip-stat {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  background: #f7f8fa;
}

.equip-stat.running {
  background: linear-gradient(135deg, #e8ffea, #c8ffcd);
}

.equip-stat.standby {
  background: linear-gradient(135deg, #e8f3ff, #d6e4ff);
}

.equip-stat.fault {
  background: linear-gradient(135deg, #ffece8, #ffd6cc);
}

.equip-stat.total {
  background: linear-gradient(135deg, #f0f5ff, #e8f3ff);
}

.equip-stat .stat-num {
  display: block;
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 4px;
}

.equip-stat.running .stat-num {
  color: #00b42a;
}

.equip-stat.standby .stat-num {
  color: #165dff;
}

.equip-stat.fault .stat-num {
  color: #f53f3f;
}

.equip-stat .stat-label {
  font-size: 12px;
  color: #4e5969;
}

.equipment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.equip-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #fff;
  border: 1px solid #e5e6eb;
  border-radius: 6px;
}

.equip-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #86909c;
}

.equip-item.running .equip-status-dot {
  background: #00b42a;
  box-shadow: 0 0 6px rgba(0, 180, 42, 0.6);
}

.equip-item.standby .equip-status-dot {
  background: #165dff;
}

.equip-item.fault .equip-status-dot {
  background: #f53f3f;
}

.equip-item.maintenance .equip-status-dot {
  background: #ff7d00;
}

.equip-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.equip-name {
  font-weight: 500;
  color: #1d2129;
  font-size: 13px;
}

.equip-type {
  font-size: 12px;
  color: #86909c;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e5e6eb;
}

@media (max-width: 1400px) {
  .map-container {
    flex-direction: column;
  }

  .map-legend {
    width: 100%;
  }

  .legend-items {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .legend-item {
    flex: 1;
    min-width: 120px;
  }
}

@media (max-width: 1024px) {
  .params-list {
    grid-template-columns: 1fr;
  }

  .equipment-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

<style>
.zone-detail-modal .arco-modal-body {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
