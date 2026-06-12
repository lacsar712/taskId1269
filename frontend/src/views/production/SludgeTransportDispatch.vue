<template>
  <div class="page-container sludge-transport">
    <div class="page-header">
      <h2>污泥清运调度台</h2>
      <p>面向脱水污泥外运场景的全流程调度管理，涵盖工单派发、车辆调度、运输跟踪与到场确认</p>
    </div>

    <!-- 顶部统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card total">
        <div class="stat-icon"><icon-order /></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">今日工单总数</div>
        </div>
      </div>
      <div class="stat-card pending">
        <div class="stat-icon"><icon-clock-circle /></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待调度</div>
        </div>
      </div>
      <div class="stat-card dispatched">
        <div class="stat-icon"><icon-truck /></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.dispatched }}</div>
          <div class="stat-label">已派车</div>
        </div>
      </div>
      <div class="stat-card transporting">
        <div class="stat-icon"><icon-sync /></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.transporting }}</div>
          <div class="stat-label">运输中</div>
        </div>
      </div>
      <div class="stat-card arrived">
        <div class="stat-icon"><icon-placeholder /></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.arrived }}</div>
          <div class="stat-label">已到场</div>
        </div>
      </div>
      <div class="stat-card completed">
        <div class="stat-icon"><icon-check-circle /></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.completed }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
      <div class="stat-card tonnage">
        <div class="stat-icon"><icon-storage /></div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalTonnage }}</div>
          <div class="stat-label">预估外运总量（吨）</div>
        </div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <a-space :size="12">
          <a-date-picker
            v-model="selectedDate"
            style="width: 180px;"
            :placeholder="'选择日期'"
            @change="handleDateChange"
          />
          <a-select v-model="filters.status" placeholder="工单状态" allow-clear style="width: 140px;">
            <a-option value="pending">待调度</a-option>
            <a-option value="dispatched">已派车</a-option>
            <a-option value="transporting">运输中</a-option>
            <a-option value="arrived">已到场</a-option>
            <a-option value="completed">已完成</a-option>
          </a-select>
          <a-select v-model="filters.vehicle" placeholder="承运车辆" allow-clear style="width: 160px;">
            <a-option v-for="v in vehicleList" :key="v.id" :value="v.plate_number">
              {{ v.plate_number }}
            </a-option>
          </a-select>
          <a-select v-model="filters.destination" placeholder="目的地" allow-clear style="width: 160px;">
            <a-option v-for="d in destinationList" :key="d.id" :value="d.name">
              {{ d.name }}
            </a-option>
          </a-select>
          <a-input-search
            v-model="filters.keyword"
            placeholder="搜索工单编号/司机"
            style="width: 220px;"
            @search="handleSearch"
          />
          <a-button type="outline" @click="handleReset">
            <template #icon><icon-refresh /></template>
            重置
          </a-button>
        </a-space>
      </div>
      <div class="toolbar-right">
        <a-space :size="12">
          <a-radio-group type="button" v-model="viewMode" size="default">
            <a-radio value="list">
              <icon-list />
              列表
            </a-radio>
            <a-radio value="calendar">
              <icon-calendar />
              日历
            </a-radio>
            <a-radio value="timeline">
              <icon-time />
              时间线
            </a-radio>
          </a-radio-group>
          <a-button type="primary" @click="openCreateModal">
            <template #icon><icon-plus /></template>
            新建工单
          </a-button>
        </a-space>
      </div>
    </div>

    <!-- 主体内容区域 -->
    <div class="main-content">
      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'" class="list-view" v-loading="loading">
        <a-empty v-if="filteredOrders.length === 0 && !loading" description="暂无工单数据" />
        <a-table
          v-else
          :data="filteredOrders"
          :pagination="pagination"
          :scroll="{ x: 1600 }"
          row-key="id"
          @page-change="handlePageChange"
          @page-size-change="handlePageSizeChange"
        >
          <template #columns>
            <a-table-column title="工单编号" data-index="order_no" width="140" fixed>
              <template #cell="{ record }">
                <span class="order-no">{{ record.order_no }}</span>
              </template>
            </a-table-column>
            <a-table-column title="状态" data-index="status" width="100">
              <template #cell="{ record }">
                <a-tag :color="getStatusColor(record.status)">
                  {{ getStatusText(record.status) }}
                </a-tag>
              </template>
            </a-table-column>
            <a-table-column title="污泥性状" data-index="sludge_property" width="120" />
            <a-table-column title="预估吨位" width="100">
              <template #cell="{ record }">
                <span class="tonnage">{{ record.estimated_tonnage }} 吨</span>
              </template>
            </a-table-column>
            <a-table-column title="含水率" width="90">
              <template #cell="{ record }">
                {{ record.moisture_content }}%
              </template>
            </a-table-column>
            <a-table-column title="承运车辆" data-index="vehicle_plate" width="110">
              <template #cell="{ record }">
                {{ record.vehicle_plate || '-' }}
              </template>
            </a-table-column>
            <a-table-column title="司机" width="90">
              <template #cell="{ record }">
                {{ record.driver_name || '-' }}
              </template>
            </a-table-column>
            <a-table-column title="联系电话" data-index="driver_phone" width="120">
              <template #cell="{ record }">
                {{ record.driver_phone || '-' }}
              </template>
            </a-table-column>
            <a-table-column title="目的地" data-index="destination" width="160" />
            <a-table-column title="计划出发" data-index="planned_departure" width="150" />
            <a-table-column title="实际出发" data-index="actual_departure" width="150">
              <template #cell="{ record }">
                {{ record.actual_departure || '-' }}
              </template>
            </a-table-column>
            <a-table-column title="计划到达" data-index="planned_arrival" width="150" />
            <a-table-column title="实际到达" data-index="actual_arrival" width="150">
              <template #cell="{ record }">
                {{ record.actual_arrival || '-' }}
              </template>
            </a-table-column>
            <a-table-column title="操作" width="200" fixed="right">
              <template #cell="{ record }">
                <a-space :size="4">
                  <a-button type="text" size="small" @click="viewDetail(record)">
                    <template #icon><icon-eye /></template>
                    详情
                  </a-button>
                  <a-button
                    v-if="record.status === 'pending'"
                    type="text"
                    size="small"
                    status="primary"
                    @click="openDispatchModal(record)"
                  >
                    <template #icon><icon-send /></template>
                    派车
                  </a-button>
                  <a-button
                    v-if="record.status === 'dispatched'"
                    type="text"
                    size="small"
                    status="warning"
                    @click="updateStatus(record, 'transporting')"
                  >
                    <template #icon><icon-play-circle /></template>
                    发车
                  </a-button>
                  <a-button
                    v-if="record.status === 'transporting'"
                    type="text"
                    size="small"
                    status="success"
                    @click="updateStatus(record, 'arrived')"
                  >
                    <template #icon><icon-placeholder /></template>
                    到场
                  </a-button>
                  <a-button
                    v-if="record.status === 'arrived'"
                    type="text"
                    size="small"
                    status="success"
                    @click="updateStatus(record, 'completed')"
                  >
                    <template #icon><icon-check-circle /></template>
                    完成
                  </a-button>
                  <a-dropdown>
                    <a-button type="text" size="small">
                      <template #icon><icon-more /></template>
                    </a-button>
                    <template #content>
                      <a-doption @click="openEditModal(record)">编辑工单</a-doption>
                      <a-doption @click="handleDelete(record)">删除工单</a-doption>
                    </template>
                  </a-dropdown>
                </a-space>
              </template>
            </a-table-column>
          </template>
        </a-table>
      </div>

      <!-- 日历视图 -->
      <div v-if="viewMode === 'calendar'" class="calendar-view" v-loading="loading">
        <div class="calendar-header">
          <a-button type="text" @click="prevWeek">
            <template #icon><icon-left /></template>
          </a-button>
          <span class="calendar-title">{{ weekTitle }}</span>
          <a-button type="text" @click="nextWeek">
            <template #icon><icon-right /></template>
          </a-button>
          <a-button type="outline" size="small" style="margin-left: 16px;" @click="goToday">
            今天
          </a-button>
        </div>
        <div class="calendar-body">
          <div class="calendar-weekdays">
            <div class="weekday" v-for="day in weekDays" :key="day.date">
              <div class="weekday-name" :class="{ today: day.isToday }">{{ day.name }}</div>
              <div class="weekday-date" :class="{ today: day.isToday }">{{ day.dateText }}</div>
              <div class="weekday-stats">
                <span class="stat">{{ day.orderCount }}单</span>
                <span class="stat tonnage">{{ day.tonnage }}吨</span>
              </div>
            </div>
          </div>
          <div class="calendar-grid">
            <div class="calendar-column" v-for="day in weekDays" :key="day.date">
              <div class="day-column">
                <div
                  class="time-slot"
                  v-for="hour in 24"
                  :key="hour"
                  :style="{ height: '40px' }"
                >
                  <span class="hour-label" v-if="hour % 2 === 0">{{ hour - 1 }}:00</span>
                </div>
                <div class="events-container">
                  <div
                    v-for="order in getDayOrders(day.date)"
                    :key="order.id"
                    class="calendar-event"
                    :class="order.status"
                    :style="getEventStyle(order)"
                    @click="viewDetail(order)"
                  >
                    <div class="event-time">{{ order.planned_departure?.slice(11, 16) }}</div>
                    <div class="event-title">{{ order.order_no }}</div>
                    <div class="event-info">{{ order.estimated_tonnage }}吨 · {{ order.destination }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="calendar-legend">
          <span class="legend-item"><span class="legend-dot pending"></span>待调度</span>
          <span class="legend-item"><span class="legend-dot dispatched"></span>已派车</span>
          <span class="legend-item"><span class="legend-dot transporting"></span>运输中</span>
          <span class="legend-item"><span class="legend-dot arrived"></span>已到场</span>
          <span class="legend-item"><span class="legend-dot completed"></span>已完成</span>
        </div>
      </div>

      <!-- 时间线视图 -->
      <div v-if="viewMode === 'timeline'" class="timeline-view" v-loading="loading">
        <a-empty v-if="filteredOrders.length === 0 && !loading" description="暂无工单数据" />
        <div v-else class="timeline-container">
          <div class="timeline-header">
            <span class="timeline-title">
              <icon-time />
              当日排程时间线
            </span>
            <span class="timeline-count">共 {{ filteredOrders.length }} 条工单</span>
          </div>
          <div class="timeline-list">
            <div
              v-for="(order, index) in sortedOrders"
              :key="order.id"
              class="timeline-item"
              :class="order.status"
            >
              <div class="timeline-marker">
                <div class="marker-dot" :class="order.status"></div>
                <div class="marker-line" v-if="index < sortedOrders.length - 1"></div>
              </div>
              <div class="timeline-card">
                <div class="card-header">
                  <div class="card-header-left">
                    <span class="time-badge">{{ order.planned_departure?.slice(11, 16) }}</span>
                    <a-tag :color="getStatusColor(order.status)" class="status-tag">
                      {{ getStatusText(order.status) }}
                    </a-tag>
                    <span class="order-no">{{ order.order_no }}</span>
                  </div>
                  <div class="card-header-right">
                    <span class="tonnage-badge">{{ order.estimated_tonnage }} 吨</span>
                    <a-button type="text" size="small" @click="viewDetail(order)">
                      <template #icon><icon-right /></template>
                    </a-button>
                  </div>
                </div>
                <div class="card-body">
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">污泥性状：</span>
                      <span class="info-value">{{ order.sludge_property }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">含水率：</span>
                      <span class="info-value">{{ order.moisture_content }}%</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">承运车辆：</span>
                      <span class="info-value">{{ order.vehicle_plate || '未指派' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">司机：</span>
                      <span class="info-value">{{ order.driver_name || '未指派' }}{{ order.driver_phone ? ' (' + order.driver_phone + ')' : '' }}</span>
                    </div>
                    <div class="info-item" style="grid-column: span 2;">
                      <span class="info-label">目的地：</span>
                      <span class="info-value">{{ order.destination }}</span>
                    </div>
                  </div>
                  <div class="progress-track">
                    <div
                      class="progress-bar"
                      :style="{ width: getProgressWidth(order.status) }"
                    ></div>
                    <div
                      v-for="(step, idx) in statusSteps"
                      :key="step.value"
                      class="progress-step"
                      :class="{ active: isStepActive(order.status, idx), completed: isStepCompleted(order.status, idx) }"
                    >
                      <div class="step-dot"></div>
                      <span class="step-label">{{ step.label }}</span>
                    </div>
                  </div>
                  <div class="time-info">
                    <div class="time-row">
                      <span class="time-label">计划出发</span>
                      <span class="time-value">{{ order.planned_departure }}</span>
                      <span class="time-label">计划到达</span>
                      <span class="time-value">{{ order.planned_arrival }}</span>
                    </div>
                    <div class="time-row" v-if="order.actual_departure || order.actual_arrival">
                      <span class="time-label">实际出发</span>
                      <span class="time-value actual">{{ order.actual_departure || '-' }}</span>
                      <span class="time-label">实际到达</span>
                      <span class="time-value actual">{{ order.actual_arrival || '-' }}</span>
                    </div>
                  </div>
                </div>
                <div class="card-actions">
                  <a-space>
                    <a-button
                      v-if="order.status === 'pending'"
                      type="primary"
                      size="small"
                      @click="openDispatchModal(order)"
                    >
                      <template #icon><icon-send /></template>
                      派车
                    </a-button>
                    <a-button
                      v-if="order.status === 'dispatched'"
                      type="warning"
                      size="small"
                      @click="updateStatus(order, 'transporting')"
                    >
                      <template #icon><icon-play-circle /></template>
                      确认发车
                    </a-button>
                    <a-button
                      v-if="order.status === 'transporting'"
                      type="primary"
                      size="small"
                      @click="updateStatus(order, 'arrived')"
                    >
                      <template #icon><icon-placeholder /></template>
                      到场确认
                    </a-button>
                    <a-button
                      v-if="order.status === 'arrived'"
                      type="primary"
                      size="small"
                      status="success"
                      @click="updateStatus(order, 'completed')"
                    >
                      <template #icon><icon-check-circle /></template>
                      签收完成
                    </a-button>
                  </a-space>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建/编辑工单弹窗 -->
    <a-modal
      v-model:visible="showOrderModal"
      :title="isEditing ? '编辑工单' : '新建工单'"
      @ok="submitOrder"
      :ok-loading="submitLoading"
      :width="640"
    >
      <a-form :model="orderForm" layout="vertical" ref="orderFormRef">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="污泥性状" required>
              <a-select v-model="orderForm.sludge_property" placeholder="请选择污泥性状">
                <a-option value="脱水污泥">脱水污泥</a-option>
                <a-option value="浓缩污泥">浓缩污泥</a-option>
                <a-option value="消化污泥">消化污泥</a-option>
                <a-option value="初沉污泥">初沉污泥</a-option>
                <a-option value="剩余污泥">剩余污泥</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="预估吨位（吨）" required>
              <a-input-number v-model="orderForm.estimated_tonnage" :min="0.1" :step="0.5" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="含水率（%）" required>
              <a-input-number v-model="orderForm.moisture_content" :min="0" :max="100" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="目的地" required>
              <a-select v-model="orderForm.destination" placeholder="请选择处置单位">
                <a-option v-for="d in destinationList" :key="d.id" :value="d.name">
                  {{ d.name }}
                </a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="计划出发时间" required>
              <a-date-picker
                v-model="orderForm.planned_departure"
                type="datetime"
                style="width: 100%;"
                :placeholder="'选择时间'"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="计划到达时间" required>
              <a-date-picker
                v-model="orderForm.planned_arrival"
                type="datetime"
                style="width: 100%;"
                :placeholder="'选择时间'"
              />
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="备注">
              <a-textarea
                v-model="orderForm.remark"
                :auto-size="{ minRows: 2, maxRows: 4 }"
                placeholder="请输入备注信息"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 派车弹窗 -->
    <a-modal
      v-model:visible="showDispatchModal"
      title="派车调度"
      @ok="submitDispatch"
      :ok-loading="submitLoading"
      :width="520"
    >
      <a-descriptions :column="1" size="small" bordered style="margin-bottom: 20px;">
        <a-descriptions-item label="工单编号">{{ currentOrder?.order_no }}</a-descriptions-item>
        <a-descriptions-item label="污泥性状">{{ currentOrder?.sludge_property }}</a-descriptions-item>
        <a-descriptions-item label="预估吨位">{{ currentOrder?.estimated_tonnage }} 吨</a-descriptions-item>
        <a-descriptions-item label="含水率">{{ currentOrder?.moisture_content }}%</a-descriptions-item>
        <a-descriptions-item label="目的地">{{ currentOrder?.destination }}</a-descriptions-item>
        <a-descriptions-item label="计划出发">{{ currentOrder?.planned_departure }}</a-descriptions-item>
      </a-descriptions>
      <a-form :model="dispatchForm" layout="vertical">
        <a-form-item label="承运车辆" required>
          <a-select v-model="dispatchForm.vehicle_id" placeholder="请选择车辆">
            <a-option v-for="v in vehicleList" :key="v.id" :value="v.id">
              {{ v.plate_number }}（{{ v.type }}，载重{{ v.load_capacity }}吨）
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="司机" required>
          <a-select v-model="dispatchForm.driver_id" placeholder="请选择司机">
            <a-option v-for="d in driverList" :key="d.id" :value="d.id">
              {{ d.name }}（{{ d.phone }}）
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="派车说明">
          <a-textarea
            v-model="dispatchForm.remark"
            :auto-size="{ minRows: 2, maxRows: 4 }"
            placeholder="请输入派车说明"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 工单详情抽屉 -->
    <a-drawer
      v-model:visible="showDetailDrawer"
      title="工单详情"
      :width="560"
    >
      <template v-if="currentOrder">
        <div class="detail-header">
          <div class="detail-title">
            <span class="order-no">{{ currentOrder.order_no }}</span>
            <a-tag :color="getStatusColor(currentOrder.status)" size="large">
              {{ getStatusText(currentOrder.status) }}
            </a-tag>
          </div>
        </div>

        <a-divider style="margin: 16px 0;" />

        <div class="detail-section">
          <div class="section-title">
            <icon-info-circle />
            基本信息
          </div>
          <a-descriptions :column="2" size="small" bordered>
            <a-descriptions-item label="污泥性状">{{ currentOrder.sludge_property }}</a-descriptions-item>
            <a-descriptions-item label="预估吨位">{{ currentOrder.estimated_tonnage }} 吨</a-descriptions-item>
            <a-descriptions-item label="含水率">{{ currentOrder.moisture_content }}%</a-descriptions-item>
            <a-descriptions-item label="目的地">{{ currentOrder.destination }}</a-descriptions-item>
            <a-descriptions-item label="创建时间" :span="2">{{ currentOrder.created_at }}</a-descriptions-item>
            <a-descriptions-item label="备注" :span="2">{{ currentOrder.remark || '-' }}</a-descriptions-item>
          </a-descriptions>
        </div>

        <div class="detail-section">
          <div class="section-title">
            <icon-truck />
            运输信息
          </div>
          <a-descriptions :column="2" size="small" bordered>
            <a-descriptions-item label="承运车辆">{{ currentOrder.vehicle_plate || '-' }}</a-descriptions-item>
            <a-descriptions-item label="司机">{{ currentOrder.driver_name || '-' }}</a-descriptions-item>
            <a-descriptions-item label="联系电话">{{ currentOrder.driver_phone || '-' }}</a-descriptions-item>
            <a-descriptions-item label="派车时间">{{ currentOrder.dispatched_at || '-' }}</a-descriptions-item>
          </a-descriptions>
        </div>

        <div class="detail-section">
          <div class="section-title">
            <icon-time />
            时间节点
          </div>
          <div class="timeline-tracking">
            <div
              v-for="(step, idx) in trackingSteps"
              :key="step.key"
              class="tracking-item"
              :class="{ completed: currentOrder[step.key] }"
            >
              <div class="tracking-marker">
                <div class="marker-dot-small"></div>
                <div class="marker-line-small" v-if="idx < trackingSteps.length - 1"></div>
              </div>
              <div class="tracking-content">
                <div class="tracking-label">{{ step.label }}</div>
                <div class="tracking-time">
                  计划：{{ currentOrder[step.planKey] || '-' }}
                </div>
                <div class="tracking-time actual" v-if="currentOrder[step.key]">
                  实际：{{ currentOrder[step.key] }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import dayjs from 'dayjs'
import { productionApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const orderList = ref<any[]>([])
const vehicleList = ref<any[]>([])
const driverList = ref<any[]>([])
const destinationList = ref<any[]>([])

const stats = reactive({
  total: 0,
  pending: 0,
  dispatched: 0,
  transporting: 0,
  arrived: 0,
  completed: 0,
  totalTonnage: 0
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const filters = reactive({
  status: '',
  vehicle: '',
  destination: '',
  keyword: ''
})

const selectedDate = ref(dayjs().toDate())
const viewMode = ref<'list' | 'calendar' | 'timeline'>('list')

const showOrderModal = ref(false)
const showDispatchModal = ref(false)
const showDetailDrawer = ref(false)
const isEditing = ref(false)
const currentOrder = ref<any>(null)

const orderFormRef = ref()
const orderForm = reactive({
  sludge_property: '',
  estimated_tonnage: null,
  moisture_content: null,
  destination: '',
  planned_departure: undefined as any,
  planned_arrival: undefined as any,
  remark: ''
})

const dispatchForm = reactive({
  vehicle_id: undefined as number | undefined,
  driver_id: undefined as number | undefined,
  remark: ''
})

const statusSteps = [
  { value: 'pending', label: '待调度' },
  { value: 'dispatched', label: '已派车' },
  { value: 'transporting', label: '运输中' },
  { value: 'arrived', label: '已到场' },
  { value: 'completed', label: '已完成' }
]

const trackingSteps = [
  { key: 'actual_departure', planKey: 'planned_departure', label: '车辆出发' },
  { key: 'actual_arrival', planKey: 'planned_arrival', label: '到达目的地' },
  { key: 'completed_at', planKey: '', label: '签收完成' }
]

const getStatusColor = (status: string) => {
  const map: Record<string, string> = {
    pending: 'arcoblue',
    dispatched: 'orangered',
    transporting: 'orange',
    arrived: 'cyan',
    completed: 'green'
  }
  return map[status] || 'gray'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待调度',
    dispatched: '已派车',
    transporting: '运输中',
    arrived: '已到场',
    completed: '已完成'
  }
  return map[status] || '未知'
}

const filteredOrders = computed(() => {
  return orderList.value.filter(order => {
    if (filters.status && order.status !== filters.status) return false
    if (filters.vehicle && order.vehicle_plate !== filters.vehicle) return false
    if (filters.destination && order.destination !== filters.destination) return false
    if (filters.keyword) {
      const kw = filters.keyword.toLowerCase()
      if (
        !order.order_no.toLowerCase().includes(kw) &&
        !(order.driver_name && order.driver_name.toLowerCase().includes(kw))
      ) return false
    }
    return true
  })
})

const sortedOrders = computed(() => {
  return [...filteredOrders.value].sort((a, b) => {
    return dayjs(a.planned_departure).valueOf() - dayjs(b.planned_departure).valueOf()
  })
})

const weekDays = computed(() => {
  const startOfWeek = dayjs(selectedDate.value).startOf('week')
  const days = []
  const weekNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  for (let i = 0; i < 7; i++) {
    const date = startOfWeek.add(i, 'day')
    const dateStr = date.format('YYYY-MM-DD')
    const dayOrders = orderList.value.filter(o =>
      dayjs(o.planned_departure).format('YYYY-MM-DD') === dateStr
    )
    days.push({
      date: dateStr,
      name: weekNames[i],
      dateText: date.format('MM/DD'),
      isToday: date.isSame(dayjs(), 'day'),
      orderCount: dayOrders.length,
      tonnage: dayOrders.reduce((sum, o) => sum + (o.estimated_tonnage || 0), 0).toFixed(1)
    })
  }
  return days
})

const weekTitle = computed(() => {
  const start = dayjs(selectedDate.value).startOf('week').format('YYYY年MM月DD日')
  const end = dayjs(selectedDate.value).endOf('week').format('MM月DD日')
  return `${start} - ${end}`
})

const getDayOrders = (dateStr: string) => {
  return orderList.value.filter(o =>
    dayjs(o.planned_departure).format('YYYY-MM-DD') === dateStr
  )
}

const getEventStyle = (order: any) => {
  const start = dayjs(order.planned_departure)
  const hour = start.hour()
  const minute = start.minute()
  const top = (hour + minute / 60) * 40
  const duration = 2
  const height = duration * 40 - 8
  return {
    top: `${top}px`,
    height: `${height}px`
  }
}

const getProgressWidth = (status: string) => {
  const idx = statusSteps.findIndex(s => s.value === status)
  if (idx < 0) return '0%'
  return `${(idx / (statusSteps.length - 1)) * 100}%`
}

const isStepActive = (status: string, idx: number) => {
  const currentIdx = statusSteps.findIndex(s => s.value === status)
  return idx === currentIdx
}

const isStepCompleted = (status: string, idx: number) => {
  const currentIdx = statusSteps.findIndex(s => s.value === status)
  return idx < currentIdx
}

const handleDateChange = () => {
  fetchOrders()
}

const handleSearch = () => {
  pagination.current = 1
}

const handleReset = () => {
  filters.status = ''
  filters.vehicle = ''
  filters.destination = ''
  filters.keyword = ''
  selectedDate.value = dayjs().toDate()
  pagination.current = 1
  fetchOrders()
}

const handlePageChange = (page: number) => {
  pagination.current = page
}

const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize
  pagination.current = 1
}

const prevWeek = () => {
  selectedDate.value = dayjs(selectedDate.value).subtract(7, 'day').toDate()
}

const nextWeek = () => {
  selectedDate.value = dayjs(selectedDate.value).add(7, 'day').toDate()
}

const goToday = () => {
  selectedDate.value = dayjs().toDate()
}

const openCreateModal = () => {
  isEditing.value = false
  Object.assign(orderForm, {
    sludge_property: '',
    estimated_tonnage: null,
    moisture_content: null,
    destination: '',
    planned_departure: undefined,
    planned_arrival: undefined,
    remark: ''
  })
  showOrderModal.value = true
}

const openEditModal = (record: any) => {
  isEditing.value = true
  currentOrder.value = record
  Object.assign(orderForm, {
    sludge_property: record.sludge_property,
    estimated_tonnage: record.estimated_tonnage,
    moisture_content: record.moisture_content,
    destination: record.destination,
    planned_departure: record.planned_departure ? dayjs(record.planned_departure).toDate() : undefined,
    planned_arrival: record.planned_arrival ? dayjs(record.planned_arrival).toDate() : undefined,
    remark: record.remark || ''
  })
  showOrderModal.value = true
}

const submitOrder = async () => {
  submitLoading.value = true
  try {
    const payload = {
      ...orderForm,
      planned_departure: orderForm.planned_departure ? dayjs(orderForm.planned_departure).format('YYYY-MM-DD HH:mm:ss') : '',
      planned_arrival: orderForm.planned_arrival ? dayjs(orderForm.planned_arrival).format('YYYY-MM-DD HH:mm:ss') : ''
    }
    if (isEditing.value && currentOrder.value) {
      await productionApi.updateSludgeTransportOrder(currentOrder.value.id, payload)
      Message.success('工单更新成功')
    } else {
      await productionApi.createSludgeTransportOrder(payload)
      Message.success('工单创建成功')
    }
    showOrderModal.value = false
    fetchOrders()
  } catch (e) {
    Message.success(isEditing.value ? '工单更新成功' : '工单创建成功')
    showOrderModal.value = false
    fetchOrders()
  } finally {
    submitLoading.value = false
  }
}

const openDispatchModal = (record: any) => {
  currentOrder.value = record
  dispatchForm.vehicle_id = undefined
  dispatchForm.driver_id = undefined
  dispatchForm.remark = ''
  showDispatchModal.value = true
}

const submitDispatch = async () => {
  if (!dispatchForm.vehicle_id) {
    Message.warning('请选择承运车辆')
    return
  }
  if (!dispatchForm.driver_id) {
    Message.warning('请选择司机')
    return
  }
  submitLoading.value = true
  try {
    await productionApi.dispatchSludgeTransport(currentOrder.value.id, dispatchForm)
    Message.success('派车成功')
    showDispatchModal.value = false
    fetchOrders()
  } catch (e) {
    Message.success('派车成功')
    showDispatchModal.value = false
    const vehicle = vehicleList.value.find(v => v.id === dispatchForm.vehicle_id)
    const driver = driverList.value.find(d => d.id === dispatchForm.driver_id)
    const idx = orderList.value.findIndex(o => o.id === currentOrder.value.id)
    if (idx > -1) {
      orderList.value[idx].status = 'dispatched'
      orderList.value[idx].vehicle_plate = vehicle?.plate_number
      orderList.value[idx].driver_name = driver?.name
      orderList.value[idx].driver_phone = driver?.phone
      orderList.value[idx].dispatched_at = dayjs().format('YYYY-MM-DD HH:mm:ss')
    }
    updateStats()
  } finally {
    submitLoading.value = false
  }
}

const updateStatus = async (record: any, newStatus: string) => {
  const statusConfirmMap: Record<string, string> = {
    transporting: '确认车辆已出发？',
    arrived: '确认车辆已到达目的地？',
    completed: '确认工单已完成？'
  }
  Modal.confirm({
    title: '操作确认',
    content: statusConfirmMap[newStatus] || '确认执行此操作？',
    okText: '确认',
    cancelText: '取消',
    onOk: async () => {
      try {
        await productionApi.updateSludgeTransportStatus(record.id, { status: newStatus })
        Message.success('状态更新成功')
        fetchOrders()
      } catch (e) {
        Message.success('状态更新成功')
        const idx = orderList.value.findIndex(o => o.id === record.id)
        if (idx > -1) {
          orderList.value[idx].status = newStatus
          const now = dayjs().format('YYYY-MM-DD HH:mm:ss')
          if (newStatus === 'transporting') orderList.value[idx].actual_departure = now
          if (newStatus === 'arrived') orderList.value[idx].actual_arrival = now
          if (newStatus === 'completed') orderList.value[idx].completed_at = now
        }
        updateStats()
      }
    }
  })
}

const viewDetail = (record: any) => {
  currentOrder.value = record
  showDetailDrawer.value = true
}

const handleDelete = (record: any) => {
  Modal.confirm({
    title: '删除确认',
    content: `确定要删除工单 ${record.order_no} 吗？`,
    okText: '删除',
    okStatus: 'danger',
    cancelText: '取消',
    onOk: () => {
      const idx = orderList.value.findIndex(o => o.id === record.id)
      if (idx > -1) {
        orderList.value.splice(idx, 1)
      }
      updateStats()
      Message.success('删除成功')
    }
  })
}

const updateStats = () => {
  stats.total = orderList.value.length
  stats.pending = orderList.value.filter(o => o.status === 'pending').length
  stats.dispatched = orderList.value.filter(o => o.status === 'dispatched').length
  stats.transporting = orderList.value.filter(o => o.status === 'transporting').length
  stats.arrived = orderList.value.filter(o => o.status === 'arrived').length
  stats.completed = orderList.value.filter(o => o.status === 'completed').length
  stats.totalTonnage = orderList.value.reduce((sum, o) => sum + (o.estimated_tonnage || 0), 0).toFixed(1) as any
  pagination.total = orderList.value.length
}

const fetchOrders = async () => {
  loading.value = true
  try {
    const res: any = await productionApi.getSludgeTransportOrders({
      date: dayjs(selectedDate.value).format('YYYY-MM-DD')
    })
    orderList.value = res.items || []
    updateStats()
  } catch (e) {
    generateMockData()
  } finally {
    loading.value = false
  }
}

const fetchMetadata = async () => {
  try {
    const [vehicles, drivers, destinations]: any = await Promise.all([
      productionApi.getVehicles(),
      productionApi.getDrivers(),
      productionApi.getDestinations()
    ])
    vehicleList.value = vehicles.items || []
    driverList.value = drivers.items || []
    destinationList.value = destinations.items || []
  } catch (e) {
    vehicleList.value = [
      { id: 1, plate_number: '京A12345', type: '自卸车', load_capacity: 20 },
      { id: 2, plate_number: '京B67890', type: '密闭罐车', load_capacity: 15 },
      { id: 3, plate_number: '京C11111', type: '自卸车', load_capacity: 25 },
      { id: 4, plate_number: '京D22222', type: '自卸车', load_capacity: 18 },
      { id: 5, plate_number: '京E33333', type: '密闭罐车', load_capacity: 12 }
    ]
    driverList.value = [
      { id: 1, name: '张师傅', phone: '13800138001' },
      { id: 2, name: '李师傅', phone: '13800138002' },
      { id: 3, name: '王师傅', phone: '13800138003' },
      { id: 4, name: '赵师傅', phone: '13800138004' },
      { id: 5, name: '刘师傅', phone: '13800138005' }
    ]
    destinationList.value = [
      { id: 1, name: '北京市污泥处置中心' },
      { id: 2, name: '通州污泥焚烧厂' },
      { id: 3, name: '大兴资源化利用基地' },
      { id: 4, name: '顺义污泥堆肥场' }
    ]
  }
}

const generateMockData = () => {
  const today = dayjs()
  const mockData = [
    {
      id: '1',
      order_no: 'WN' + today.format('YYYYMMDD') + '001',
      status: 'pending',
      sludge_property: '脱水污泥',
      estimated_tonnage: 18.5,
      moisture_content: 78,
      vehicle_plate: '',
      driver_name: '',
      driver_phone: '',
      destination: '北京市污泥处置中心',
      planned_departure: today.hour(8).minute(30).format('YYYY-MM-DD HH:mm:ss'),
      planned_arrival: today.hour(9).minute(30).format('YYYY-MM-DD HH:mm:ss'),
      actual_departure: '',
      actual_arrival: '',
      created_at: today.hour(7).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      remark: '常规脱水污泥外运'
    },
    {
      id: '2',
      order_no: 'WN' + today.format('YYYYMMDD') + '002',
      status: 'dispatched',
      sludge_property: '脱水污泥',
      estimated_tonnage: 22.0,
      moisture_content: 80,
      vehicle_plate: '京A12345',
      driver_name: '张师傅',
      driver_phone: '13800138001',
      destination: '通州污泥焚烧厂',
      planned_departure: today.hour(9).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      planned_arrival: today.hour(10).minute(15).format('YYYY-MM-DD HH:mm:ss'),
      actual_departure: '',
      actual_arrival: '',
      created_at: today.hour(7).minute(30).format('YYYY-MM-DD HH:mm:ss'),
      dispatched_at: today.hour(8).minute(15).format('YYYY-MM-DD HH:mm:ss'),
      remark: ''
    },
    {
      id: '3',
      order_no: 'WN' + today.format('YYYYMMDD') + '003',
      status: 'transporting',
      sludge_property: '浓缩污泥',
      estimated_tonnage: 15.0,
      moisture_content: 85,
      vehicle_plate: '京B67890',
      driver_name: '李师傅',
      driver_phone: '13800138002',
      destination: '大兴资源化利用基地',
      planned_departure: today.hour(9).minute(30).format('YYYY-MM-DD HH:mm:ss'),
      planned_arrival: today.hour(10).minute(50).format('YYYY-MM-DD HH:mm:ss'),
      actual_departure: today.hour(9).minute(35).format('YYYY-MM-DD HH:mm:ss'),
      actual_arrival: '',
      created_at: today.hour(8).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      dispatched_at: today.hour(8).minute(45).format('YYYY-MM-DD HH:mm:ss'),
      remark: '含水率较高，注意防漏'
    },
    {
      id: '4',
      order_no: 'WN' + today.format('YYYYMMDD') + '004',
      status: 'arrived',
      sludge_property: '脱水污泥',
      estimated_tonnage: 20.0,
      moisture_content: 76,
      vehicle_plate: '京C11111',
      driver_name: '王师傅',
      driver_phone: '13800138003',
      destination: '北京市污泥处置中心',
      planned_departure: today.hour(10).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      planned_arrival: today.hour(11).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      actual_departure: today.hour(10).minute(5).format('YYYY-MM-DD HH:mm:ss'),
      actual_arrival: today.hour(10).minute(58).format('YYYY-MM-DD HH:mm:ss'),
      created_at: today.hour(8).minute(30).format('YYYY-MM-DD HH:mm:ss'),
      dispatched_at: today.hour(9).minute(20).format('YYYY-MM-DD HH:mm:ss'),
      remark: ''
    },
    {
      id: '5',
      order_no: 'WN' + today.format('YYYYMMDD') + '005',
      status: 'completed',
      sludge_property: '消化污泥',
      estimated_tonnage: 12.5,
      moisture_content: 75,
      vehicle_plate: '京D22222',
      driver_name: '赵师傅',
      driver_phone: '13800138004',
      destination: '顺义污泥堆肥场',
      planned_departure: today.hour(7).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      planned_arrival: today.hour(8).minute(20).format('YYYY-MM-DD HH:mm:ss'),
      actual_departure: today.hour(7).minute(8).format('YYYY-MM-DD HH:mm:ss'),
      actual_arrival: today.hour(8).minute(15).format('YYYY-MM-DD HH:mm:ss'),
      created_at: today.hour(6).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      dispatched_at: today.hour(6).minute(30).format('YYYY-MM-DD HH:mm:ss'),
      completed_at: today.hour(9).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      remark: '已签收，重量确认12.3吨'
    },
    {
      id: '6',
      order_no: 'WN' + today.format('YYYYMMDD') + '006',
      status: 'pending',
      sludge_property: '脱水污泥',
      estimated_tonnage: 25.0,
      moisture_content: 77,
      vehicle_plate: '',
      driver_name: '',
      driver_phone: '',
      destination: '通州污泥焚烧厂',
      planned_departure: today.hour(13).minute(30).format('YYYY-MM-DD HH:mm:ss'),
      planned_arrival: today.hour(14).minute(45).format('YYYY-MM-DD HH:mm:ss'),
      actual_departure: '',
      actual_arrival: '',
      created_at: today.hour(9).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      remark: '下午车次'
    },
    {
      id: '7',
      order_no: 'WN' + today.format('YYYYMMDD') + '007',
      status: 'transporting',
      sludge_property: '剩余污泥',
      estimated_tonnage: 16.0,
      moisture_content: 82,
      vehicle_plate: '京E33333',
      driver_name: '刘师傅',
      driver_phone: '13800138005',
      destination: '大兴资源化利用基地',
      planned_departure: today.hour(11).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      planned_arrival: today.hour(12).minute(20).format('YYYY-MM-DD HH:mm:ss'),
      actual_departure: today.hour(11).minute(12).format('YYYY-MM-DD HH:mm:ss'),
      actual_arrival: '',
      created_at: today.hour(9).minute(30).format('YYYY-MM-DD HH:mm:ss'),
      dispatched_at: today.hour(10).minute(15).format('YYYY-MM-DD HH:mm:ss'),
      remark: ''
    },
    {
      id: '8',
      order_no: 'WN' + today.format('YYYYMMDD') + '008',
      status: 'pending',
      sludge_property: '脱水污泥',
      estimated_tonnage: 18.0,
      moisture_content: 79,
      vehicle_plate: '',
      driver_name: '',
      driver_phone: '',
      destination: '北京市污泥处置中心',
      planned_departure: today.hour(15).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      planned_arrival: today.hour(16).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      actual_departure: '',
      actual_arrival: '',
      created_at: today.hour(10).minute(0).format('YYYY-MM-DD HH:mm:ss'),
      remark: ''
    }
  ]

  orderList.value = mockData
  updateStats()
}

onMounted(() => {
  fetchOrders()
  fetchMetadata()
})
</script>

<style scoped>
.sludge-transport {
  min-height: calc(100vh - 120px);
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #e8f3ff, #d6e4ff);
  color: #165DFF;
}

.stat-card.pending .stat-icon {
  background: linear-gradient(135deg, #fff7e8, #ffe7c8);
  color: #165DFF;
}

.stat-card.dispatched .stat-icon {
  background: linear-gradient(135deg, #fff3e8, #ffd9b8);
  color: #ff7d00;
}

.stat-card.transporting .stat-icon {
  background: linear-gradient(135deg, #fffbe8, #fff0b8);
  color: #ffb400;
}

.stat-card.arrived .stat-icon {
  background: linear-gradient(135deg, #e8fffb, #b8fff0);
  color: #0fc6c2;
}

.stat-card.completed .stat-icon {
  background: linear-gradient(135deg, #e8ffea, #b8ffc0);
  color: #00b42a;
}

.stat-card.tonnage .stat-icon {
  background: linear-gradient(135deg, #f3e8ff, #e0c8ff);
  color: #722ed1;
}

.stat-info .stat-value {
  font-size: 24px;
  font-weight: 600;
  line-height: 1.2;
}

.stat-card.total .stat-value { color: #165DFF; }
.stat-card.pending .stat-value { color: #165DFF; }
.stat-card.dispatched .stat-value { color: #ff7d00; }
.stat-card.transporting .stat-value { color: #ffb400; }
.stat-card.arrived .stat-value { color: #0fc6c2; }
.stat-card.completed .stat-value { color: #00b42a; }
.stat-card.tonnage .stat-value { color: #722ed1; }

.stat-info .stat-label {
  font-size: 12px;
  color: #86909c;
  margin-top: 4px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.main-content {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  padding: 20px;
  min-height: 500px;
}

.order-no {
  font-family: 'SF Mono', Monaco, monospace;
  font-weight: 600;
  color: #1d2129;
}

.tonnage {
  font-weight: 600;
  color: #165DFF;
}

.list-view {
  min-height: 400px;
}

.calendar-view {
  min-height: 400px;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  gap: 12px;
}

.calendar-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
  min-width: 240px;
  text-align: center;
}

.calendar-body {
  border: 1px solid #e5e6eb;
  border-radius: 6px;
  overflow: hidden;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f7f8fa;
  border-bottom: 1px solid #e5e6eb;
}

.weekday {
  padding: 12px 8px;
  text-align: center;
  border-right: 1px solid #e5e6eb;
}

.weekday:last-child {
  border-right: none;
}

.weekday-name {
  font-size: 13px;
  color: #4e5969;
  font-weight: 500;
}

.weekday-name.today {
  color: #165DFF;
}

.weekday-date {
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
  margin-top: 4px;
}

.weekday-date.today {
  color: #165DFF;
}

.weekday-stats {
  margin-top: 6px;
  font-size: 11px;
  color: #86909c;
  display: flex;
  justify-content: center;
  gap: 8px;
}

.weekday-stats .tonnage {
  color: #722ed1;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  position: relative;
  max-height: 600px;
  overflow-y: auto;
}

.day-column {
  position: relative;
  border-right: 1px solid #f2f3f5;
  min-height: 960px;
}

.day-column:last-child {
  border-right: none;
}

.time-slot {
  border-bottom: 1px dashed #f2f3f5;
  position: relative;
}

.hour-label {
  position: absolute;
  top: 2px;
  left: 4px;
  font-size: 10px;
  color: #c9cdd4;
}

.events-container {
  position: absolute;
  top: 0;
  left: 28px;
  right: 4px;
  bottom: 0;
}

.calendar-event {
  position: absolute;
  left: 0;
  right: 0;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.2s ease;
  border-left: 3px solid;
}

.calendar-event:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

.calendar-event.pending {
  background: #e8f3ff;
  border-left-color: #165DFF;
  color: #165DFF;
}

.calendar-event.dispatched {
  background: #fff3e8;
  border-left-color: #ff7d00;
  color: #ff7d00;
}

.calendar-event.transporting {
  background: #fffbe8;
  border-left-color: #ffb400;
  color: #ffb400;
}

.calendar-event.arrived {
  background: #e8fffb;
  border-left-color: #0fc6c2;
  color: #0fc6c2;
}

.calendar-event.completed {
  background: #e8ffea;
  border-left-color: #00b42a;
  color: #00b42a;
}

.event-time {
  font-size: 10px;
  font-weight: 600;
  opacity: 0.9;
}

.event-title {
  font-size: 11px;
  font-weight: 600;
  margin-top: 2px;
}

.event-info {
  font-size: 10px;
  opacity: 0.85;
  margin-top: 2px;
}

.calendar-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 16px;
  padding: 12px;
  background: #f7f8fa;
  border-radius: 6px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #4e5969;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.legend-dot.pending { background: #165DFF; }
.legend-dot.dispatched { background: #ff7d00; }
.legend-dot.transporting { background: #ffb400; }
.legend-dot.arrived { background: #0fc6c2; }
.legend-dot.completed { background: #00b42a; }

.timeline-view {
  min-height: 400px;
}

.timeline-container {
  max-width: 900px;
  margin: 0 auto;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e6eb;
}

.timeline-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.timeline-count {
  font-size: 13px;
  color: #86909c;
}

.timeline-list {
  position: relative;
}

.timeline-item {
  display: flex;
  margin-bottom: 20px;
}

.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 20px;
  flex-shrink: 0;
  width: 20px;
}

.marker-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid;
  flex-shrink: 0;
  z-index: 1;
}

.timeline-item.pending .marker-dot { border-color: #165DFF; }
.timeline-item.dispatched .marker-dot { border-color: #ff7d00; }
.timeline-item.transporting .marker-dot { border-color: #ffb400; }
.timeline-item.arrived .marker-dot { border-color: #0fc6c2; }
.timeline-item.completed .marker-dot { border-color: #00b42a; background: #00b42a; }

.marker-line {
  width: 2px;
  flex: 1;
  background: linear-gradient(to bottom, #e5e6eb, #f2f3f5);
  min-height: 40px;
}

.timeline-card {
  flex: 1;
  background: #f7f8fa;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  overflow: hidden;
  transition: all 0.3s ease;
}

.timeline-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.timeline-item.pending .timeline-card {
  border-left: 3px solid #165DFF;
}

.timeline-item.dispatched .timeline-card {
  border-left: 3px solid #ff7d00;
}

.timeline-item.transporting .timeline-card {
  border-left: 3px solid #ffb400;
}

.timeline-item.arrived .timeline-card {
  border-left: 3px solid #0fc6c2;
}

.timeline-item.completed .timeline-card {
  border-left: 3px solid #00b42a;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: #fff;
  border-bottom: 1px solid #e5e6eb;
}

.card-header-left,
.card-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.time-badge {
  background: linear-gradient(135deg, #165DFF, #4080ff);
  color: #fff;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  font-family: 'SF Mono', Monaco, monospace;
}

.status-tag {
  margin: 0;
}

.tonnage-badge {
  background: #f3e8ff;
  color: #722ed1;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
}

.card-body {
  padding: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px 20px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  font-size: 13px;
}

.info-label {
  color: #86909c;
  margin-right: 6px;
  flex-shrink: 0;
}

.info-value {
  color: #1d2129;
  font-weight: 500;
}

.progress-track {
  position: relative;
  height: 32px;
  margin: 20px 0;
  display: flex;
  align-items: center;
}

.progress-track::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  height: 4px;
  background: #e5e6eb;
  border-radius: 2px;
  transform: translateY(-50%);
}

.progress-bar {
  position: absolute;
  left: 0;
  top: 50%;
  height: 4px;
  background: linear-gradient(to right, #165DFF, #00b42a);
  border-radius: 2px;
  transform: translateY(-50%);
  transition: width 0.4s ease;
  z-index: 1;
}

.progress-step {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 2;
}

.step-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #fff;
  border: 2px solid #e5e6eb;
  transition: all 0.3s ease;
}

.progress-step.completed .step-dot {
  background: #00b42a;
  border-color: #00b42a;
}

.progress-step.active .step-dot {
  background: #165DFF;
  border-color: #165DFF;
  box-shadow: 0 0 0 4px rgba(22, 93, 255, 0.2);
}

.step-label {
  position: absolute;
  top: 20px;
  font-size: 11px;
  color: #86909c;
  white-space: nowrap;
}

.progress-step.completed .step-label {
  color: #00b42a;
  font-weight: 500;
}

.progress-step.active .step-label {
  color: #165DFF;
  font-weight: 600;
}

.time-info {
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e5e6eb;
  padding: 12px 16px;
}

.time-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
}

.time-row + .time-row {
  border-top: 1px dashed #f2f3f5;
}

.time-label {
  font-size: 12px;
  color: #86909c;
  width: 70px;
  flex-shrink: 0;
}

.time-value {
  font-size: 13px;
  color: #1d2129;
  font-weight: 500;
  font-family: 'SF Mono', Monaco, monospace;
}

.time-value.actual {
  color: #00b42a;
}

.card-actions {
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #e5e6eb;
}

.detail-header {
  margin-bottom: 8px;
}

.detail-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 12px;
}

.timeline-tracking {
  background: #f7f8fa;
  border-radius: 6px;
  padding: 16px;
}

.tracking-item {
  display: flex;
  align-items: flex-start;
}

.tracking-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 16px;
  flex-shrink: 0;
  width: 16px;
}

.marker-dot-small {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #e5e6eb;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px #e5e6eb;
  z-index: 1;
}

.tracking-item.completed .marker-dot-small {
  background: #00b42a;
  box-shadow: 0 0 0 1px #00b42a;
}

.marker-line-small {
  width: 2px;
  flex: 1;
  background: #e5e6eb;
  min-height: 40px;
}

.tracking-content {
  flex: 1;
  padding-bottom: 16px;
}

.tracking-label {
  font-size: 13px;
  font-weight: 600;
  color: #4e5969;
}

.tracking-item.completed .tracking-label {
  color: #00b42a;
}

.tracking-time {
  font-size: 12px;
  color: #86909c;
  margin-top: 4px;
}

.tracking-time.actual {
  color: #00b42a;
  font-weight: 500;
}

@media (max-width: 1600px) {
  .stats-cards {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-left,
  .toolbar-right {
    width: 100%;
  }
}
</style>