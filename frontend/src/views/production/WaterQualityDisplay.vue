<template>
  <div class="water-quality-display" :class="{ fullscreen: isFullscreen }">
    <div class="bg-decoration">
      <div class="grid-bg"></div>
      <div class="glow glow-1"></div>
      <div class="glow glow-2"></div>
    </div>

    <div class="display-container">
      <header class="display-header">
        <div class="header-left">
          <div class="logo-decor">
            <div class="logo-icon">
              <icon-sync />
            </div>
          </div>
          <div class="header-text">
            <h1 class="main-title">出水水质信息公示牌</h1>
            <p class="sub-title">EFFLUENT WATER QUALITY DISPLAY BOARD</p>
          </div>
        </div>

        <div class="header-center">
          <div class="factory-info">
            <span class="factory-name">XX污水处理厂</span>
            <span class="divider-line">|</span>
            <span class="standard-label">执行标准：GB 18918-2002 一级A标准</span>
          </div>
        </div>

        <div class="header-right">
          <div class="update-info">
            <div class="update-icon">
              <icon-clock-circle />
            </div>
            <div class="update-text">
              <span class="update-label">数据更新时间</span>
              <span class="update-time" :class="{ 'blink-animate': isUpdating }">{{ updateTime }}</span>
            </div>
          </div>
          <div class="action-btns">
            <a-button
              type="outline"
              shape="circle"
              size="large"
              @click="refreshData"
              :loading="loading"
              class="refresh-btn"
            >
              <template #icon><icon-refresh /></template>
            </a-button>
            <a-button
              type="outline"
              shape="circle"
              size="large"
              @click="toggleFullscreen"
              class="fullscreen-btn"
            >
              <template #icon>
                <icon-fullscreen v-if="!isFullscreen" />
                <icon-fullscreen-exit v-else />
              </template>
            </a-button>
          </div>
        </div>
      </header>

      <div class="date-strip">
        <div class="date-item">
          <span class="date-label">当前日期</span>
          <span class="date-value">{{ currentDate }}</span>
        </div>
        <div class="date-divider"></div>
        <div class="date-item">
          <span class="date-label">实时时钟</span>
          <span class="date-value time-value">{{ currentTime }}</span>
        </div>
        <div class="date-divider"></div>
        <div class="date-item">
          <span class="date-label">天气状况</span>
          <span class="date-value">
            <icon-sun /> 晴 25℃
          </span>
        </div>
        <div class="date-divider"></div>
        <div class="date-item">
          <span class="date-label">进出水量</span>
          <span class="date-value">进水: {{ waterVolume.inflow }} m³/d / 出水: {{ waterVolume.outflow }} m³/d</span>
        </div>
      </div>

      <section class="indicators-section">
        <div class="section-header">
          <div class="section-title">
            <span class="title-decor-left"></span>
            <h2>核心出水指标 · 实时监测</h2>
            <span class="title-decor-right"></span>
          </div>
          <div class="section-badge">
            <span class="badge-dot"></span>
            实时数据 ONLINE
          </div>
        </div>

        <div class="indicator-cards">
          <div
            v-for="item in indicatorData"
            :key="item.key"
            class="indicator-card"
            :class="[
              getStatusClass(item),
              { 'card-highlight': item.alert_level === 'danger' || item.alert_level === 'warning' }
            ]"
          >
            <div class="card-corner corner-tl"></div>
            <div class="card-corner corner-tr"></div>
            <div class="card-corner corner-bl"></div>
            <div class="card-corner corner-br"></div>

            <div class="card-header">
              <div class="indicator-icon" :style="{ background: item.icon_bg }">
                <component :is="item.icon" />
              </div>
              <div class="indicator-meta">
                <h3 class="indicator-name">{{ item.name }}</h3>
                <span class="indicator-en">{{ item.name_en }}</span>
              </div>
              <div class="alert-badge" v-if="item.alert_level !== 'normal'">
                <a-tag
                  :color="item.alert_level === 'danger' ? 'red' : 'orange'"
                  size="large"
                >
                  {{ item.alert_level === 'danger' ? '超标预警' : '接近限值' }}
                </a-tag>
              </div>
            </div>

            <div class="card-body">
              <div class="value-block measured-block">
                <span class="block-label">实测值</span>
                <div class="value-row">
                  <span class="value-num" :class="{ 'danger-text': item.alert_level === 'danger', 'warning-text': item.alert_level === 'warning' }">
                    {{ item.measured_value }}
                  </span>
                  <span class="value-unit">{{ item.unit }}</span>
                </div>
                <span class="value-source">来源: {{ item.source }}</span>
              </div>

              <div class="compare-arrow">
                <icon-arrow-right />
              </div>

              <div class="value-block limit-block">
                <span class="block-label">国标限值</span>
                <div class="value-row">
                  <span class="value-num limit-num">{{ item.limit_value }}</span>
                  <span class="value-unit">{{ item.unit }}</span>
                </div>
                <span class="value-source">标准: GB 18918-2002</span>
              </div>

              <div class="deviation-block" v-if="item.deviation_percent !== undefined">
                <div class="deviation-value" :class="getDeviationClass(item)">
                  <span class="deviation-arrow" v-if="item.deviation_percent !== 0">
                    <icon-arrow-up v-if="item.deviation_percent > 0" />
                    <icon-arrow-down v-else />
                  </span>
                  <span class="deviation-num">
                    {{ item.deviation_percent > 0 ? '+' : '' }}{{ item.deviation_percent }}%
                  </span>
                </div>
                <div class="deviation-bar-wrapper">
                  <div class="deviation-bar">
                    <div
                      class="bar-fill"
                      :class="getBarFillClass(item)"
                      :style="{ width: getBarWidth(item) + '%' }"
                    ></div>
                    <div class="limit-marker"></div>
                  </div>
                </div>
              </div>
            </div>

            <div class="card-footer">
              <div class="sample-info">
                <icon-snapshot />
                采样时间: {{ item.sample_time }}
              </div>
              <div class="trend-info" :class="item.trend">
                <icon-arrow-up v-if="item.trend === 'up'" />
                <icon-arrow-down v-else-if="item.trend === 'down'" />
                <icon-minus v-else />
                {{ item.trend === 'up' ? '上升趋势' : item.trend === 'down' ? '下降趋势' : '平稳' }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="charts-section">
        <div class="chart-panel trend-panel">
          <div class="panel-header">
            <h3 class="panel-title">
              <icon-line-chart />
              24小时出水水质趋势
            </h3>
            <div class="panel-legend">
              <span class="legend-item">
                <span class="legend-dot" style="background: #00d4ff;"></span>
                实测值
              </span>
              <span class="legend-item">
                <span class="legend-dot" style="background: #ff4d4f; border-style: dashed;"></span>
                排放限值
              </span>
            </div>
          </div>
          <div class="chart-container" ref="trendChartRef"></div>
        </div>

        <div class="chart-panel compliance-panel">
          <div class="panel-header">
            <h3 class="panel-title">
              <icon-pie-chart />
              本月达标统计
            </h3>
          </div>
          <div class="compliance-content">
            <div class="compliance-chart" ref="complianceChartRef"></div>
            <div class="compliance-stats">
              <div class="stat-item compliant">
                <span class="stat-num">{{ complianceStats.compliant_rate }}%</span>
                <span class="stat-label">达标率</span>
              </div>
              <div class="stat-item total">
                <span class="stat-num">{{ complianceStats.total_samples }}</span>
                <span class="stat-label">监测总次</span>
              </div>
              <div class="stat-item compliant-count">
                <span class="stat-num">{{ complianceStats.compliant_count }}</span>
                <span class="stat-label">达标次</span>
              </div>
              <div class="stat-item overproof">
                <span class="stat-num">{{ complianceStats.overproof_count }}</span>
                <span class="stat-label">超标次</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer class="display-footer">
        <div class="footer-content">
          <div class="footer-left">
            <icon-info-circle />
            本公示牌数据每5分钟自动刷新，与化验检测系统及在线监测仪实时同步
          </div>
          <div class="footer-right">
            <span class="contact-info">
              运维监督电话: 400-XXX-XXXX
            </span>
            <span class="footer-divider">|</span>
            <span class="copyright">
              © 2024 XX环保科技有限公司 版权所有
            </span>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { productionApi } from '@/api'

const loading = ref(false)
const isUpdating = ref(false)
const isFullscreen = ref(false)
const updateTime = ref('--:--:--')
const currentDate = ref('')
const currentTime = ref('')
const trendChartRef = ref<HTMLElement | null>(null)
const complianceChartRef = ref<HTMLElement | null>(null)
let trendChartInstance: echarts.ECharts | null = null
let complianceChartInstance: echarts.ECharts | null = null
let clockTimer: number | null = null
let refreshTimer: number | null = null
const REFRESH_INTERVAL = 5 * 60 * 1000

const waterVolume = reactive({
  inflow: '0',
  outflow: '0'
})

const complianceStats = reactive({
  compliant_rate: 0,
  total_samples: 0,
  compliant_count: 0,
  overproof_count: 0
})

interface IndicatorItem {
  key: string
  name: string
  name_en: string
  icon: string
  icon_bg: string
  unit: string
  measured_value: string | number
  limit_value: string | number
  source: string
  sample_time: string
  deviation_percent: number
  alert_level: 'normal' | 'warning' | 'danger'
  trend: 'up' | 'down' | 'stable'
}

const indicatorData = ref<IndicatorItem[]>([])

const mockIndicatorData = (): IndicatorItem[] => [
  {
    key: 'COD',
    name: '化学需氧量',
    name_en: 'COD',
    icon: 'icon-apps',
    icon_bg: 'linear-gradient(135deg, #1e3a5f, #2d5a87)',
    unit: 'mg/L',
    measured_value: 42.5,
    limit_value: 50,
    source: '在线监测',
    sample_time: dayjs().format('HH:mm:ss'),
    deviation_percent: -15,
    alert_level: 'normal',
    trend: 'down'
  },
  {
    key: 'NH3N',
    name: '氨氮',
    name_en: 'NH₃-N',
    icon: 'icon-cloud',
    icon_bg: 'linear-gradient(135deg, #1e4d3a, #2d7d5a)',
    unit: 'mg/L',
    measured_value: 4.85,
    limit_value: 5,
    source: '在线监测',
    sample_time: dayjs().format('HH:mm:ss'),
    deviation_percent: -3,
    alert_level: 'warning',
    trend: 'up'
  },
  {
    key: 'TP',
    name: '总磷',
    name_en: 'TP',
    icon: 'icon-fire',
    icon_bg: 'linear-gradient(135deg, #4d3a1e, #7d5a2d)',
    unit: 'mg/L',
    measured_value: 0.58,
    limit_value: 0.5,
    source: '化验检测',
    sample_time: dayjs().subtract(2, 'minute').format('HH:mm:ss'),
    deviation_percent: 16,
    alert_level: 'danger',
    trend: 'up'
  },
  {
    key: 'SS',
    name: '悬浮物',
    name_en: 'SS',
    icon: 'icon-storage',
    icon_bg: 'linear-gradient(135deg, #3a1e4d, #5a2d7d)',
    unit: 'mg/L',
    measured_value: 8.5,
    limit_value: 10,
    source: '在线监测',
    sample_time: dayjs().format('HH:mm:ss'),
    deviation_percent: -15,
    alert_level: 'normal',
    trend: 'stable'
  },
  {
    key: 'PH',
    name: '酸碱度',
    name_en: 'pH',
    icon: 'icon-experiment',
    icon_bg: 'linear-gradient(135deg, #4d4d1e, #7d7d2d)',
    unit: '',
    measured_value: 7.2,
    limit_value: '6-9',
    source: '在线监测',
    sample_time: dayjs().format('HH:mm:ss'),
    deviation_percent: 0,
    alert_level: 'normal',
    trend: 'stable'
  }
]

const getStatusClass = (item: IndicatorItem) => {
  return `status-${item.alert_level}`
}

const getDeviationClass = (item: IndicatorItem) => {
  if (item.deviation_percent > 10) return 'dev-danger'
  if (item.deviation_percent > 0) return 'dev-warning'
  if (item.deviation_percent < -20) return 'dev-excellent'
  return 'dev-normal'
}

const getBarFillClass = (item: IndicatorItem) => {
  if (item.alert_level === 'danger') return 'fill-danger'
  if (item.alert_level === 'warning') return 'fill-warning'
  return 'fill-normal'
}

const getBarWidth = (item: IndicatorItem) => {
  const measured = Number(item.measured_value)
  const limit = typeof item.limit_value === 'string' ? 7.5 : Number(item.limit_value)
  const percent = (measured / limit) * 80
  return Math.min(percent, 100)
}

const refreshData = async () => {
  loading.value = true
  isUpdating.value = true
  try {
    const res: any = await productionApi.getEffluentQualityDisplay()
    if (res && res.indicators) {
      indicatorData.value = res.indicators
      updateTime.value = res.update_time
      Object.assign(waterVolume, res.water_volume || {})
      Object.assign(complianceStats, res.compliance_stats || {})
    } else {
      generateMockData()
    }
  } catch (e) {
    generateMockData()
  } finally {
    loading.value = false
    nextTick(() => {
      if (trendChartInstance) initTrendChart()
      if (complianceChartInstance) initComplianceChart()
    })
    setTimeout(() => {
      isUpdating.value = false
    }, 800)
  }
}

const generateMockData = () => {
  const baseData = mockIndicatorData()
  baseData.forEach(item => {
    const fluctuation = (Math.random() - 0.5) * 0.1
    if (item.key !== 'PH' && typeof item.measured_value === 'number') {
      item.measured_value = Number((item.measured_value * (1 + fluctuation)).toFixed(2))
    }
    item.sample_time = dayjs().format('HH:mm:ss')
    if (item.key !== 'PH' && typeof item.limit_value === 'number') {
      const dev = ((Number(item.measured_value) - item.limit_value) / item.limit_value * 100)
      item.deviation_percent = Math.round(dev)
      if (dev > 0) {
        item.alert_level = dev > 10 ? 'danger' : 'warning'
      } else {
        item.alert_level = dev > -5 ? 'warning' : 'normal'
      }
    }
  })
  indicatorData.value = baseData
  updateTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss')
  waterVolume.inflow = (38000 + Math.floor(Math.random() * 4000)).toLocaleString()
  waterVolume.outflow = (36500 + Math.floor(Math.random() * 3500)).toLocaleString()
  complianceStats.total_samples = 720
  complianceStats.compliant_count = 712
  complianceStats.overproof_count = 8
  complianceStats.compliant_rate = 98.9
}

const updateDateTime = () => {
  currentDate.value = dayjs().format('YYYY年MM月DD日 dddd')
  currentTime.value = dayjs().format('HH:mm:ss')
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChartInstance) trendChartInstance.dispose()

  trendChartInstance = echarts.init(trendChartRef.value)

  const hours: string[] = []
  for (let i = 0; i < 24; i++) {
    hours.push(`${i.toString().padStart(2, '0')}:00`)
  }

  const generateSeriesData = (base: number, limit: number, variance: number) => {
    return hours.map((_, idx) => {
      const wave = Math.sin(idx * 0.4) * variance
      const noise = (Math.random() - 0.5) * variance * 0.6
      let val = base + wave + noise
      if (idx === 14) val = limit * 1.08
      if (idx === 3) val = limit * 0.6
      return Number(val.toFixed(2))
    })
  }

  const option = {
    backgroundColor: 'transparent',
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      top: '10%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10, 25, 47, 0.95)',
      borderColor: '#00d4ff',
      textStyle: { color: '#fff' },
      axisPointer: {
        type: 'cross',
        lineStyle: { color: '#00d4ff', type: 'dashed' }
      }
    },
    legend: {
      show: false
    },
    xAxis: {
      type: 'category',
      data: hours,
      axisLine: { lineStyle: { color: '#2a4a6a' } },
      axisLabel: { color: '#8ab4d6', fontSize: 11, margin: 12 },
      axisTick: { show: false }
    },
    yAxis: [
      {
        type: 'value',
        name: 'COD/SS (mg/L)',
        nameTextStyle: { color: '#8ab4d6', fontSize: 11, padding: [0, 0, 0, 20] },
        position: 'left',
        axisLine: { show: true, lineStyle: { color: '#2a4a6a' } },
        axisLabel: { color: '#8ab4d6', fontSize: 11 },
        splitLine: { lineStyle: { color: 'rgba(42, 74, 106, 0.5)', type: 'dashed' } }
      },
      {
        type: 'value',
        name: 'NH3N/TP (mg/L)',
        nameTextStyle: { color: '#8ab4d6', fontSize: 11, padding: [0, 20, 0, 0] },
        position: 'right',
        axisLine: { show: true, lineStyle: { color: '#2a4a6a' } },
        axisLabel: { color: '#8ab4d6', fontSize: 11 },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'COD',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        data: generateSeriesData(42, 50, 8),
        lineStyle: { color: '#00d4ff', width: 2.5 },
        itemStyle: { color: '#00d4ff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.35)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.02)' }
          ])
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#ff4d4f', type: 'dashed', width: 2 },
          data: [{ yAxis: 50, name: 'COD限值' }],
          label: {
            formatter: 'COD限值 50',
            color: '#ff4d4f',
            fontSize: 11,
            backgroundColor: 'rgba(255, 77, 79, 0.15)',
            padding: [3, 6],
            borderRadius: 3
          }
        }
      },
      {
        name: '氨氮',
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        symbol: 'diamond',
        symbolSize: 5,
        data: generateSeriesData(3.8, 5, 0.9),
        lineStyle: { color: '#00ff88', width: 2.5 },
        itemStyle: { color: '#00ff88' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 255, 136, 0.25)' },
            { offset: 1, color: 'rgba(0, 255, 136, 0.02)' }
          ])
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#ffaa00', type: 'dashed', width: 2 },
          data: [{ yAxis: 5, name: '氨氮限值' }],
          label: {
            formatter: '氨氮限值 5',
            color: '#ffaa00',
            fontSize: 11,
            backgroundColor: 'rgba(255, 170, 0, 0.15)',
            padding: [3, 6],
            borderRadius: 3
          }
        }
      },
      {
        name: 'SS',
        type: 'line',
        smooth: true,
        symbol: 'triangle',
        symbolSize: 5,
        data: generateSeriesData(8, 10, 2),
        lineStyle: { color: '#c77dff', width: 2 },
        itemStyle: { color: '#c77dff' }
      }
    ]
  }

  trendChartInstance.setOption(option)
}

const initComplianceChart = () => {
  if (!complianceChartRef.value) return
  if (complianceChartInstance) complianceChartInstance.dispose()

  complianceChartInstance = echarts.init(complianceChartRef.value)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10, 25, 47, 0.95)',
      borderColor: '#00d4ff',
      textStyle: { color: '#fff' },
      formatter: '{b}: {c}次 ({d}%)'
    },
    legend: {
      show: false
    },
    series: [
      {
        name: '达标统计',
        type: 'pie',
        radius: ['55%', '75%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#0a192f',
          borderWidth: 3
        },
        label: {
          show: true,
          position: 'center',
          formatter: () => {
            return `{rate|${complianceStats.compliant_rate}%}\n{label|达标率}`
          },
          rich: {
            rate: {
              fontSize: 36,
              fontWeight: 'bold',
              color: '#00ff88',
              lineHeight: 50
            },
            label: {
              fontSize: 13,
              color: '#8ab4d6',
              lineHeight: 20
            }
          }
        },
        labelLine: {
          show: false
        },
        data: [
          {
            value: complianceStats.compliant_count,
            name: '达标',
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                { offset: 0, color: '#00ff88' },
                { offset: 1, color: '#00d4ff' }
              ])
            }
          },
          {
            value: complianceStats.overproof_count,
            name: '超标',
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                { offset: 0, color: '#ff4d4f' },
                { offset: 1, color: '#ff7d00' }
              ])
            }
          }
        ]
      }
    ]
  }

  complianceChartInstance.setOption(option)
}

const handleResize = () => {
  trendChartInstance?.resize()
  complianceChartInstance?.resize()
}

onMounted(async () => {
  updateDateTime()
  clockTimer = window.setInterval(() => {
    updateDateTime()
  }, 1000)

  refreshTimer = window.setInterval(() => {
    refreshData()
  }, REFRESH_INTERVAL)

  await refreshData()

  nextTick(() => {
    initTrendChart()
    initComplianceChart()
  })

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement
  })
})

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer)
  if (refreshTimer) clearInterval(refreshTimer)
  window.removeEventListener('resize', handleResize)
  trendChartInstance?.dispose()
  complianceChartInstance?.dispose()
})

watch(isFullscreen, () => {
  setTimeout(() => {
    trendChartInstance?.resize()
    complianceChartInstance?.resize()
  }, 200)
})
</script>

<style scoped>
.water-quality-display {
  position: relative;
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(180deg, #061225 0%, #0a192f 35%, #0f2847 100%);
  color: #fff;
  overflow-x: hidden;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.water-quality-display.fullscreen {
  height: 100vh;
  overflow: hidden;
}

.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.grid-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
}

.glow-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.15), transparent 70%);
  top: -200px;
  left: -100px;
  animation: float 8s ease-in-out infinite;
}

.glow-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(0, 255, 136, 0.12), transparent 70%);
  bottom: -150px;
  right: -100px;
  animation: float 10s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 20px); }
}

.display-container {
  position: relative;
  z-index: 1;
  padding: 20px 32px;
  max-width: 1920px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.display-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0 20px;
  border-bottom: 1px solid rgba(0, 212, 255, 0.15);
  position: relative;
}

.display-header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.logo-decor {
  position: relative;
}

.logo-icon {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #00d4ff, #0066ff);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
  animation: rotate-slow 12s linear infinite;
}

@keyframes rotate-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.main-title {
  font-size: 30px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #ffffff 0%, #00d4ff 50%, #ffffff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 4px;
  white-space: nowrap;
}

.sub-title {
  font-size: 12px;
  color: #5a7a9a;
  letter-spacing: 3px;
  margin: 4px 0 0;
}

.header-center {
  flex: 1;
  text-align: center;
}

.factory-info {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  padding: 8px 24px;
  background: rgba(0, 212, 255, 0.06);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 24px;
}

.factory-name {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: 2px;
}

.divider-line {
  color: rgba(0, 212, 255, 0.4);
}

.standard-label {
  font-size: 13px;
  color: #8ab4d6;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
  justify-content: flex-end;
}

.update-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 18px;
  background: rgba(0, 255, 136, 0.06);
  border: 1px solid rgba(0, 255, 136, 0.2);
  border-radius: 10px;
}

.update-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 255, 136, 0.05));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00ff88;
  font-size: 18px;
}

.update-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.update-label {
  font-size: 11px;
  color: #5a7a9a;
}

.update-time {
  font-size: 15px;
  font-weight: 600;
  color: #00ff88;
  font-family: 'Courier New', monospace;
  transition: all 0.3s;
}

.update-time.blink-animate {
  animation: blink 0.8s ease-in-out 2;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; transform: scale(1.05); }
}

.action-btns {
  display: flex;
  gap: 10px;
}

.action-btns :deep(.arco-btn) {
  background: rgba(0, 212, 255, 0.08) !important;
  border-color: rgba(0, 212, 255, 0.3) !important;
  color: #00d4ff !important;
}

.action-btns :deep(.arco-btn:hover) {
  background: rgba(0, 212, 255, 0.2) !important;
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
}

.refresh-btn :deep(.arco-btn-icon) {
  animation: spin 3s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.date-strip {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 14px 32px;
  margin: 18px 0;
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.05), rgba(0, 212, 255, 0.12), rgba(0, 212, 255, 0.05));
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-radius: 10px;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-label {
  font-size: 12px;
  color: #5a7a9a;
  padding: 3px 10px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 4px;
}

.date-value {
  font-size: 15px;
  font-weight: 500;
  color: #c4e0f5;
}

.date-value.time-value {
  color: #00d4ff;
  font-family: 'Courier New', monospace;
  font-weight: 700;
  font-size: 18px;
}

.date-divider {
  width: 1px;
  height: 28px;
  background: linear-gradient(180deg, transparent, rgba(0, 212, 255, 0.3), transparent);
}

.indicators-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  margin-bottom: 18px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 14px;
}

.section-title h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #ffffff;
  letter-spacing: 3px;
}

.title-decor-left,
.title-decor-right {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff);
}

.title-decor-right {
  background: linear-gradient(90deg, #00d4ff, transparent);
}

.section-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: rgba(0, 255, 136, 0.08);
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 20px;
  font-size: 12px;
  color: #00ff88;
  font-weight: 600;
  letter-spacing: 1px;
}

.badge-dot {
  width: 8px;
  height: 8px;
  background: #00ff88;
  border-radius: 50%;
  animation: pulse-dot 1.5s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); }
  50% { box-shadow: 0 0 0 6px rgba(0, 255, 136, 0); }
}

.indicator-cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 18px;
  flex: 1;
  min-height: 0;
}

.indicator-card {
  position: relative;
  background: linear-gradient(180deg, rgba(22, 52, 88, 0.6), rgba(12, 32, 58, 0.8));
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  padding: 18px 16px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  display: flex;
  flex-direction: column;
}

.indicator-card:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 212, 255, 0.5);
  box-shadow: 0 10px 40px rgba(0, 212, 255, 0.15);
}

.indicator-card.card-highlight {
  animation: card-pulse 3s ease-in-out infinite;
}

@keyframes card-pulse {
  0%, 100% { box-shadow: 0 0 0 rgba(255, 77, 79, 0); }
  50% { box-shadow: 0 0 30px rgba(255, 77, 79, 0.25); }
}

.card-corner {
  position: absolute;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(0, 212, 255, 0.6);
}

.corner-tl {
  top: 0;
  left: 0;
  border-right: none;
  border-bottom: none;
}

.corner-tr {
  top: 0;
  right: 0;
  border-left: none;
  border-bottom: none;
}

.corner-bl {
  bottom: 0;
  left: 0;
  border-right: none;
  border-top: none;
}

.corner-br {
  bottom: 0;
  right: 0;
  border-left: none;
  border-top: none;
}

.indicator-card.status-danger {
  border-color: rgba(255, 77, 79, 0.5);
  background: linear-gradient(180deg, rgba(88, 22, 32, 0.5), rgba(58, 12, 22, 0.8));
}

.indicator-card.status-danger .card-corner {
  border-color: rgba(255, 77, 79, 0.7);
}

.indicator-card.status-warning {
  border-color: rgba(255, 170, 0, 0.5);
  background: linear-gradient(180deg, rgba(88, 60, 22, 0.5), rgba(58, 42, 12, 0.8));
}

.indicator-card.status-warning .card-corner {
  border-color: rgba(255, 170, 0, 0.7);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.indicator-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #00d4ff;
  flex-shrink: 0;
}

.indicator-meta {
  flex: 1;
  min-width: 0;
}

.indicator-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #ffffff;
}

.indicator-en {
  font-size: 11px;
  color: #5a7a9a;
  font-family: 'Courier New', monospace;
}

.alert-badge {
  flex-shrink: 0;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.value-block {
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.block-label {
  display: block;
  font-size: 11px;
  color: #5a7a9a;
  margin-bottom: 6px;
  letter-spacing: 1px;
}

.value-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.value-num {
  font-size: 32px;
  font-weight: 700;
  color: #00d4ff;
  font-family: 'Courier New', monospace;
  line-height: 1;
}

.value-unit {
  font-size: 12px;
  color: #8ab4d6;
  font-weight: 500;
}

.value-source {
  display: block;
  font-size: 10px;
  color: #4a6a8a;
  margin-top: 4px;
}

.measured-block {
  border-left: 3px solid #00d4ff;
}

.indicator-card.status-danger .measured-block {
  border-left-color: #ff4d4f;
}

.indicator-card.status-warning .measured-block {
  border-left-color: #ffaa00;
}

.danger-text {
  color: #ff4d4f !important;
  text-shadow: 0 0 15px rgba(255, 77, 79, 0.5);
  animation: danger-flicker 2s ease-in-out infinite;
}

@keyframes danger-flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.85; }
}

.warning-text {
  color: #ffaa00 !important;
  text-shadow: 0 0 15px rgba(255, 170, 0, 0.4);
}

.limit-block {
  border-left: 3px solid #5a7a9a;
  padding: 8px 12px;
}

.limit-num {
  font-size: 20px;
  color: #c4e0f5;
}

.compare-arrow {
  display: none;
  align-items: center;
  justify-content: center;
  color: #3a5a7a;
  font-size: 14px;
}

.deviation-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.deviation-value {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.dev-danger {
  background: rgba(255, 77, 79, 0.15);
  color: #ff4d4f;
  border: 1px solid rgba(255, 77, 79, 0.3);
}

.dev-warning {
  background: rgba(255, 170, 0, 0.15);
  color: #ffaa00;
  border: 1px solid rgba(255, 170, 0, 0.3);
}

.dev-normal {
  background: rgba(0, 255, 136, 0.1);
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.2);
}

.dev-excellent {
  background: rgba(0, 212, 255, 0.12);
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.25);
}

.deviation-num {
  font-size: 14px;
}

.deviation-bar-wrapper {
  padding: 0 4px;
}

.deviation-bar {
  position: relative;
  height: 6px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 3px;
  overflow: visible;
}

.bar-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.fill-normal {
  background: linear-gradient(90deg, #00ff88, #00d4ff);
  box-shadow: 0 0 8px rgba(0, 255, 136, 0.5);
}

.fill-warning {
  background: linear-gradient(90deg, #ffaa00, #ff7d00);
  box-shadow: 0 0 8px rgba(255, 170, 0, 0.5);
}

.fill-danger {
  background: linear-gradient(90deg, #ff7d00, #ff4d4f);
  box-shadow: 0 0 10px rgba(255, 77, 79, 0.6);
}

.limit-marker {
  position: absolute;
  right: 16%;
  top: -2px;
  width: 2px;
  height: 10px;
  background: #ff4d4f;
  border-radius: 1px;
}

.limit-marker::after {
  content: '限';
  position: absolute;
  right: -8px;
  top: -16px;
  font-size: 10px;
  color: #ff4d4f;
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed rgba(0, 212, 255, 0.15);
  font-size: 11px;
}

.sample-info {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #5a7a9a;
  font-family: 'Courier New', monospace;
}

.trend-info {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 4px;
}

.trend-info.up {
  background: rgba(255, 77, 79, 0.12);
  color: #ff7d7f;
}

.trend-info.down {
  background: rgba(0, 255, 136, 0.12);
  color: #5aff9d;
}

.trend-info.stable {
  background: rgba(0, 212, 255, 0.12);
  color: #5ad4ff;
}

.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 18px;
  height: 280px;
  margin-bottom: 18px;
  flex-shrink: 0;
}

.chart-panel {
  background: linear-gradient(180deg, rgba(22, 52, 88, 0.5), rgba(12, 32, 58, 0.7));
  border: 1px solid rgba(0, 212, 255, 0.18);
  border-radius: 12px;
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: #e0f0ff;
  letter-spacing: 2px;
}

.panel-title :deep(svg) {
  color: #00d4ff;
}

.panel-legend {
  display: flex;
  gap: 18px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #8ab4d6;
}

.legend-dot {
  width: 12px;
  height: 4px;
  border-radius: 2px;
  border: 2px solid transparent;
}

.chart-container {
  flex: 1;
  min-height: 0;
}

.compliance-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  min-height: 0;
}

.compliance-chart {
  min-height: 0;
}

.compliance-stats {
  display: grid;
  grid-template-rows: repeat(4, 1fr);
  gap: 8px;
  align-content: center;
}

.stat-item {
  padding: 6px 10px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
}

.stat-item .stat-num {
  font-size: 22px;
  font-weight: 700;
  font-family: 'Courier New', monospace;
  line-height: 1.2;
}

.stat-item .stat-label {
  font-size: 11px;
  color: #5a7a9a;
  margin-top: 3px;
}

.stat-item.compliant .stat-num { color: #00ff88; }
.stat-item.total .stat-num { color: #00d4ff; }
.stat-item.compliant-count .stat-num { color: #5aff9d; font-size: 18px; }
.stat-item.overproof .stat-num { color: #ff4d4f; font-size: 18px; }

.display-footer {
  padding: 10px 0 0;
  border-top: 1px solid rgba(0, 212, 255, 0.12);
  flex-shrink: 0;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #5a7a9a;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-divider {
  color: rgba(90, 122, 154, 0.4);
}

@media (max-width: 1680px) {
  .display-container {
    padding: 16px 24px;
  }
  .main-title { font-size: 26px; }
  .indicator-cards { gap: 14px; }
  .value-num { font-size: 28px; }
}

@media (max-width: 1440px) {
  .main-title { font-size: 22px; letter-spacing: 2px; }
  .sub-title { font-size: 10px; }
  .indicator-name { font-size: 14px; }
  .value-num { font-size: 24px; }
  .limit-num { font-size: 17px; }
  .charts-section { height: 240px; }
}

@media (max-width: 1280px) {
  .indicator-cards {
    grid-template-columns: repeat(3, 1fr);
  }
  .charts-section {
    grid-template-columns: 1fr;
    height: auto;
  }
  .chart-panel { min-height: 260px; }
}
</style>
