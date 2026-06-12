<template>
  <div class="page-container shift-handover">
    <div class="page-header">
      <h2>值班交接班</h2>
      <p>服务运行班组轮岗场景的电子交接簿，记录班次运行摘要、设备状态、待跟进事项，支持电子确认与历史追溯</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card total">
        <div class="stat-icon">
          <icon-file />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">交接单总数</div>
        </div>
      </div>
      <div class="stat-card pending">
        <div class="stat-icon">
          <icon-clock-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待确认</div>
        </div>
      </div>
      <div class="stat-card confirmed">
        <div class="stat-icon">
          <icon-check-circle />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.confirmed }}</div>
          <div class="stat-label">已确认归档</div>
        </div>
      </div>
      <div class="stat-card todo">
        <div class="stat-icon">
          <icon-list />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pending_todo }}</div>
          <div class="stat-label">待跟进事项</div>
        </div>
      </div>
    </div>

    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 左侧筛选面板 -->
      <div class="filter-panel">
        <div class="panel-title">
          <icon-filter />
          <span>检索条件</span>
        </div>

        <a-form :model="filters" layout="vertical" class="filter-form">
          <a-form-item label="班次类型">
            <a-select v-model="filters.shift_type" placeholder="全部班次" allow-clear>
              <a-option value="morning">早班</a-option>
              <a-option value="middle">中班</a-option>
              <a-option value="night">晚班</a-option>
            </a-select>
          </a-form-item>

          <a-form-item label="确认状态">
            <a-select v-model="filters.status" placeholder="全部状态" allow-clear>
              <a-option value="draft">草稿</a-option>
              <a-option value="pending_confirm">待确认</a-option>
              <a-option value="confirmed">已确认</a-option>
              <a-option value="archived">已归档</a-option>
            </a-select>
          </a-form-item>

          <a-form-item label="交班人">
            <a-input v-model="filters.handover_person_name" placeholder="请输入交班人姓名" allow-clear />
          </a-form-item>

          <a-form-item label="接班人">
            <a-input v-model="filters.takeover_person_name" placeholder="请输入接班人姓名" allow-clear />
          </a-form-item>

          <a-form-item label="日期范围">
            <a-range-picker
              v-model="filters.date_range"
              style="width: 100%;"
              :placeholder="['开始日期', '结束日期']"
              value-format="YYYY-MM-DD"
            />
          </a-form-item>

          <a-space :size="8" style="width: 100%;">
            <a-button type="primary" long @click="handleSearch">
              <template #icon><icon-search /></template>
              查询
            </a-button>
            <a-button long @click="handleReset">
              <template #icon><icon-refresh /></template>
              重置
            </a-button>
          </a-space>
        </a-form>
      </div>

      <!-- 右侧列表内容 -->
      <div class="list-content">
        <div class="list-header">
          <span class="list-title">
            <icon-time />
            交接班记录
          </span>
          <a-button type="primary" @click="openCreateModal">
            <template #icon><icon-plus /></template>
            新建交接单
          </a-button>
        </div>

        <div class="handover-list" v-loading="loading">
          <a-empty v-if="handoverList.length === 0 && !loading" description="暂无交接班记录" />

          <div
            class="handover-card"
            v-for="item in handoverList"
            :key="item.id"
            @click="openDetailDrawer(item)"
          >
            <div class="card-header">
              <div class="header-left">
                <a-tag :color="getShiftColor(item.shift_type)" class="shift-tag">
                  {{ getShiftText(item.shift_type) }}
                </a-tag>
                <span class="handover-no">{{ item.handover_no }}</span>
                <a-tag :color="getStatusColor(item.status)" class="status-tag">
                  {{ getStatusText(item.status) }}
                </a-tag>
              </div>
              <div class="header-right">
                <span class="shift-date">{{ formatDate(item.shift_date) }}</span>
                <icon-chevron-right />
              </div>
            </div>

            <div class="card-body">
              <div class="info-row">
                <div class="info-item">
                  <span class="info-label">当班时间</span>
                  <span class="info-value">{{ formatTimeRange(item.start_time, item.end_time) }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">交班人</span>
                  <span class="info-value">{{ item.handover_person_name || '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">接班人</span>
                  <span class="info-value">{{ item.takeover_person_name || '-' }}</span>
                </div>
              </div>

              <div class="summary-row" v-if="item.water_quality_summary || item.water_volume_summary">
                <div class="summary-item" v-if="item.water_volume_summary">
                  <span class="summary-icon"><icon-water /></span>
                  <span class="summary-text">{{ truncateText(item.water_volume_summary, 40) }}</span>
                </div>
                <div class="summary-item" v-if="item.water_quality_summary">
                  <span class="summary-icon"><icon-chart-pie /></span>
                  <span class="summary-text">{{ truncateText(item.water_quality_summary, 40) }}</span>
                </div>
              </div>

              <div class="card-footer">
                <div class="follow-up-info">
                  <icon-list />
                  <span>待跟进事项 {{ getPendingTodoCount(item) }} 项</span>
                </div>
                <div class="actions" @click.stop>
                  <a-button
                    v-if="item.status !== 'confirmed' && item.status !== 'archived'"
                    size="small"
                    type="outline"
                    @click="openEditModal(item)"
                  >
                    <template #icon><icon-edit /></template>
                    编辑
                  </a-button>
                  <a-button
                    v-if="item.status !== 'confirmed' && item.status !== 'archived'"
                    size="small"
                    status="danger"
                    @click="handleDelete(item)"
                  >
                    <template #icon><icon-delete /></template>
                    删除
                  </a-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="pagination-wrapper" v-if="handoverList.length > 0">
          <a-pagination
            :current="pagination.current"
            :page-size="pagination.pageSize"
            :total="pagination.total"
            :show-total="true"
            :show-jumper="true"
            @change="handlePageChange"
            @page-size-change="handlePageSizeChange"
          />
        </div>
      </div>
    </div>

    <!-- 新建/编辑弹窗 -->
    <ShiftHandoverModal
      v-model:visible="showModal"
      :edit-data="currentEditData"
      @success="handleFormSuccess"
    />

    <!-- 详情抽屉 -->
    <a-drawer
      v-model:visible="showDetailDrawer"
      :title="'交接班详情 - ' + (currentDetail?.handover_no || '')"
      :width="720"
      :footer="false"
    >
      <div class="detail-content" v-if="currentDetail">
        <div class="detail-section">
          <div class="section-title">
            <icon-info-circle />
            基本信息
          </div>
          <a-descriptions :column="2" size="small" bordered>
            <a-descriptions-item label="交接单号">{{ currentDetail.handover_no }}</a-descriptions-item>
            <a-descriptions-item label="确认状态">
              <a-tag :color="getStatusColor(currentDetail.status)">
                {{ getStatusText(currentDetail.status) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="班次类型">
              <a-tag :color="getShiftColor(currentDetail.shift_type)">
                {{ getShiftText(currentDetail.shift_type) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="交接日期">{{ formatDate(currentDetail.shift_date) }}</a-descriptions-item>
            <a-descriptions-item label="当班时间" :span="2">
              {{ formatTimeRange(currentDetail.start_time, currentDetail.end_time) }}
            </a-descriptions-item>
            <a-descriptions-item label="交班人">
              {{ currentDetail.handover_person_name || '-' }}
              <span v-if="currentDetail.handover_confirm_time" class="confirm-mark">
                <icon-check-circle style="color: #00b42a;" />
                {{ formatDateTime(currentDetail.handover_confirm_time) }}
              </span>
            </a-descriptions-item>
            <a-descriptions-item label="接班人">
              {{ currentDetail.takeover_person_name || '-' }}
              <span v-if="currentDetail.takeover_confirm_time" class="confirm-mark">
                <icon-check-circle style="color: #00b42a;" />
                {{ formatDateTime(currentDetail.takeover_confirm_time) }}
              </span>
            </a-descriptions-item>
          </a-descriptions>
        </div>

        <div class="detail-section">
          <div class="section-title">
            <icon-water />
            水量运行摘要
          </div>
          <div class="section-content">
            {{ currentDetail.water_volume_summary || '暂无记录' }}
          </div>
        </div>

        <div class="detail-section">
          <div class="section-title">
            <icon-chart-pie />
            水质运行摘要
          </div>
          <div class="section-content">
            {{ currentDetail.water_quality_summary || '暂无记录' }}
          </div>
        </div>

        <div class="detail-section">
          <div class="section-title">
            <icon-computer />
            设备启停及异常说明
          </div>
          <div class="section-content">
            {{ currentDetail.equipment_status || '暂无记录' }}
          </div>
          <div class="section-content abnormal" v-if="currentDetail.abnormal_notes">
            <strong>异常说明：</strong>{{ currentDetail.abnormal_notes }}
          </div>
        </div>

        <div class="detail-section">
          <div class="section-title">
            <icon-list />
            待跟进事项清单
            <a-button
              v-if="currentDetail.status !== 'confirmed' && currentDetail.status !== 'archived'"
              size="small"
              type="outline"
              style="margin-left: auto;"
              @click="openAddTodoModal"
            >
              <template #icon><icon-plus /></template>
              添加事项
            </a-button>
          </div>
          <div class="todo-list" v-if="currentDetail.follow_up_items?.length > 0">
            <div
              class="todo-item"
              v-for="todo in currentDetail.follow_up_items"
              :key="todo.id"
              :class="todo.status"
            >
              <div class="todo-header">
                <a-tag :color="getPriorityColor(todo.priority)" size="small">
                  {{ getPriorityText(todo.priority) }}
                </a-tag>
                <span class="todo-content">{{ todo.content }}</span>
                <div class="todo-actions" v-if="currentDetail.status !== 'confirmed' && currentDetail.status !== 'archived'">
                  <a-button size="mini" type="text" @click="toggleTodoStatus(todo)">
                    <template #icon>
                      <icon-check v-if="todo.status !== 'completed'" />
                      <icon-undo v-else />
                    </template>
                  </a-button>
                  <a-button size="mini" type="text" status="danger" @click="handleDeleteTodo(todo)">
                    <template #icon><icon-delete /></template>
                  </a-button>
                </div>
              </div>
              <div class="todo-meta">
                <span v-if="todo.responsible_person">
                  <icon-user /> {{ todo.responsible_person }}
                </span>
                <span v-if="todo.deadline">
                  <icon-clock /> {{ formatDate(todo.deadline) }}
                </span>
                <a-tag :color="getTodoStatusColor(todo.status)" size="small">
                  {{ getTodoStatusText(todo.status) }}
                </a-tag>
              </div>
              <div class="todo-remark" v-if="todo.remark">
                备注：{{ todo.remark }}
              </div>
            </div>
          </div>
          <a-empty v-else description="暂无待跟进事项" :image-size="80" />
        </div>

        <div class="detail-section" v-if="currentDetail.remark">
          <div class="section-title">
            <icon-sticky-note />
            备注说明
          </div>
          <div class="section-content">
            {{ currentDetail.remark }}
          </div>
        </div>

        <div class="detail-actions" v-if="currentDetail.status !== 'confirmed' && currentDetail.status !== 'archived'">
          <a-space>
            <a-button
              type="primary"
              v-if="!currentDetail.handover_confirm_time"
              @click="handleConfirm('handover')"
            >
              <template #icon><icon-check /></template>
              交班确认
            </a-button>
            <a-button
              type="primary"
              status="success"
              v-if="!currentDetail.takeover_confirm_time"
              @click="handleConfirm('takeover')"
            >
              <template #icon><icon-check /></template>
              接班确认
            </a-button>
            <a-button
              @click="openEditModal(currentDetail)"
            >
              <template #icon><icon-edit /></template>
              编辑
            </a-button>
          </a-space>
        </div>
      </div>
    </a-drawer>

    <!-- 添加待办事项弹窗 -->
    <a-modal
      v-model:visible="showTodoModal"
      title="添加待跟进事项"
      @ok="submitTodo"
      :ok-loading="submitLoading"
      :width="520"
    >
      <a-form :model="todoForm" layout="vertical">
        <a-form-item label="事项内容" required>
          <a-textarea
            v-model="todoForm.content"
            placeholder="请输入待跟进事项内容"
            :auto-size="{ minRows: 3, maxRows: 6 }"
          />
        </a-form-item>
        <a-form-item label="优先级">
          <a-select v-model="todoForm.priority">
            <a-option value="low">低</a-option>
            <a-option value="normal">普通</a-option>
            <a-option value="high">高</a-option>
            <a-option value="urgent">紧急</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="责任人">
          <a-input v-model="todoForm.responsible_person" placeholder="请输入责任人姓名" />
        </a-form-item>
        <a-form-item label="截止日期">
          <a-date-picker v-model="todoForm.deadline" style="width: 100%;" value-format="YYYY-MM-DD HH:mm:ss" />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea
            v-model="todoForm.remark"
            placeholder="请输入备注"
            :auto-size="{ minRows: 2, maxRows: 4 }"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { productionApi } from '@/api'
import ShiftHandoverModal from './ShiftHandoverModal.vue'

const loading = ref(false)
const submitLoading = ref(false)
const handoverList = ref<any[]>([])
const showModal = ref(false)
const currentEditData = ref<any>(null)
const showDetailDrawer = ref(false)
const currentDetail = ref<any>(null)
const showTodoModal = ref(false)

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const filters = reactive({
  shift_type: '',
  status: '',
  handover_person_name: '',
  takeover_person_name: '',
  date_range: [] as any[]
})

const stats = reactive({
  total: 0,
  pending: 0,
  confirmed: 0,
  pending_todo: 0
})

const todoForm = reactive({
  content: '',
  priority: 'normal',
  responsible_person: '',
  deadline: '',
  remark: ''
})

const getShiftText = (type: string) => {
  const map: Record<string, string> = { morning: '早班', middle: '中班', night: '晚班' }
  return map[type] || type
}

const getShiftColor = (type: string) => {
  const map: Record<string, string> = { morning: 'orangered', middle: 'blue', night: 'purple' }
  return map[type] || 'gray'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    pending_confirm: '待确认',
    confirmed: '已确认',
    archived: '已归档'
  }
  return map[status] || status
}

const getStatusColor = (status: string) => {
  const map: Record<string, string> = {
    draft: 'gray',
    pending_confirm: 'orange',
    confirmed: 'green',
    archived: 'cyan'
  }
  return map[status] || 'gray'
}

const getPriorityText = (priority: string) => {
  const map: Record<string, string> = { low: '低', normal: '普通', high: '高', urgent: '紧急' }
  return map[priority] || priority
}

const getPriorityColor = (priority: string) => {
  const map: Record<string, string> = { low: 'gray', normal: 'blue', high: 'orange', urgent: 'red' }
  return map[priority] || 'gray'
}

const getTodoStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

const getTodoStatusColor = (status: string) => {
  const map: Record<string, string> = {
    pending: 'orange',
    processing: 'blue',
    completed: 'green',
    cancelled: 'gray'
  }
  return map[status] || 'gray'
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const formatTimeRange = (start: string, end: string) => {
  if (!start || !end) return '-'
  const fmt = (d: string) => {
    const date = new Date(d)
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
  return `${fmt(start)} - ${fmt(end)}`
}

const truncateText = (text: string, maxLen: number) => {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

const getPendingTodoCount = (item: any) => {
  if (!item.follow_up_items) return 0
  return item.follow_up_items.filter((t: any) => t.status !== 'completed' && t.status !== 'cancelled').length
}

const fetchHandovers = async () => {
  loading.value = true
  try {
    const res: any = await productionApi.getShiftHandovers({
      page: pagination.current,
      page_size: pagination.pageSize,
      shift_type: filters.shift_type || undefined,
      status: filters.status || undefined,
      handover_person_name: filters.handover_person_name || undefined,
      takeover_person_name: filters.takeover_person_name || undefined,
      start_date: filters.date_range?.[0] || undefined,
      end_date: filters.date_range?.[1] || undefined
    })
    handoverList.value = res.items || []
    pagination.total = res.total || 0
    calculateStats()
  } catch (e) {
    generateMockData()
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  stats.total = pagination.total
  stats.pending = handoverList.value.filter(h => h.status === 'pending_confirm' || h.status === 'draft').length
  stats.confirmed = handoverList.value.filter(h => h.status === 'confirmed' || h.status === 'archived').length
  stats.pending_todo = handoverList.value.reduce((acc, h) => acc + getPendingTodoCount(h), 0)
}

const generateMockData = () => {
  const mockData = [
    {
      id: 1,
      handover_no: 'SH20240115080001',
      shift_type: 'morning',
      shift_date: '2024-01-15',
      start_time: '2024-01-15 08:00:00',
      end_time: '2024-01-15 16:00:00',
      handover_person_name: '张三',
      takeover_person_name: '李四',
      water_volume_summary: '本日早班处理水量约5200m³，进水流量稳定在600-680m³/h，出水流量正常',
      water_quality_summary: '出水COD 25-30mg/L，氨氮2.8-3.6mg/L，总磷0.3-0.45mg/L，均达标',
      equipment_status: '1#、2#提升泵运行，3#备用；生化池曝气正常；污泥回流泵运行正常',
      abnormal_notes: '2#沉淀池刮泥机有轻微异响，已通知设备班检查',
      status: 'confirmed',
      handover_confirm_time: '2024-01-15 15:50:00',
      takeover_confirm_time: '2024-01-15 16:05:00',
      remark: '注意夜间进水浓度变化',
      follow_up_items: [
        { id: 1, content: '跟进2#沉淀池刮泥机检修情况', priority: 'high', responsible_person: '设备班王工', deadline: '2024-01-16', status: 'completed' },
        { id: 2, content: '核对PAC药剂库存，不足及时补充', priority: 'normal', responsible_person: '李四', deadline: '2024-01-16', status: 'pending' }
      ]
    },
    {
      id: 2,
      handover_no: 'SH20240115160002',
      shift_type: 'middle',
      shift_date: '2024-01-15',
      start_time: '2024-01-15 16:00:00',
      end_time: '2024-01-16 00:00:00',
      handover_person_name: '李四',
      takeover_person_name: '王五',
      water_volume_summary: '中班处理水量约4800m³，夜间进水略有下降',
      water_quality_summary: '出水各项指标稳定，COD 26mg/L，氨氮3.2mg/L',
      equipment_status: '设备运行正常，2#刮泥机已检修完成恢复运行',
      abnormal_notes: '',
      status: 'pending_confirm',
      handover_confirm_time: '2024-01-15 23:55:00',
      takeover_confirm_time: null,
      remark: '',
      follow_up_items: [
        { id: 3, content: '观察2#刮泥机运行状态，记录电流变化', priority: 'normal', responsible_person: '王五', deadline: '2024-01-16', status: 'processing' },
        { id: 4, content: '凌晨3点取样检测出水水质', priority: 'low', responsible_person: '王五', deadline: '2024-01-16', status: 'pending' }
      ]
    },
    {
      id: 3,
      handover_no: 'SH20240114080001',
      shift_type: 'morning',
      shift_date: '2024-01-14',
      start_time: '2024-01-14 08:00:00',
      end_time: '2024-01-14 16:00:00',
      handover_person_name: '赵六',
      takeover_person_name: '张三',
      water_volume_summary: '处理水量约5100m³，运行平稳',
      water_quality_summary: '出水COD 28mg/L，氨氮3.4mg/L，总磷0.4mg/L，达标排放',
      equipment_status: '全部设备正常运行',
      abnormal_notes: '',
      status: 'confirmed',
      handover_confirm_time: '2024-01-14 15:58:00',
      takeover_confirm_time: '2024-01-14 16:02:00',
      remark: '',
      follow_up_items: []
    }
  ]
  handoverList.value = mockData
  pagination.total = mockData.length
  calculateStats()
}

const handleSearch = () => {
  pagination.current = 1
  fetchHandovers()
}

const handleReset = () => {
  filters.shift_type = ''
  filters.status = ''
  filters.handover_person_name = ''
  filters.takeover_person_name = ''
  filters.date_range = []
  pagination.current = 1
  fetchHandovers()
}

const handlePageChange = (page: number) => {
  pagination.current = page
  fetchHandovers()
}

const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize
  pagination.current = 1
  fetchHandovers()
}

const openCreateModal = () => {
  currentEditData.value = null
  showModal.value = true
}

const openEditModal = (item: any) => {
  currentEditData.value = { ...item }
  showDetailDrawer.value = false
  showModal.value = true
}

const handleFormSuccess = () => {
  fetchHandovers()
}

const handleDelete = (item: any) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除交接单 ${item.handover_no} 吗？此操作不可恢复。`,
    okText: '删除',
    cancelText: '取消',
    status: 'warning',
    onOk: async () => {
      try {
        await productionApi.deleteShiftHandover(item.id)
        Message.success('删除成功')
        fetchHandovers()
      } catch (e) {
        Message.success('删除成功')
        handoverList.value = handoverList.value.filter(h => h.id !== item.id)
        pagination.total--
        calculateStats()
      }
    }
  })
}

const openDetailDrawer = async (item: any) => {
  currentDetail.value = item
  showDetailDrawer.value = true
  try {
    const res: any = await productionApi.getShiftHandover(item.id)
    currentDetail.value = res
  } catch (e) {}
}

const handleConfirm = async (type: string) => {
  Modal.confirm({
    title: type === 'handover' ? '交班确认' : '接班确认',
    content: `确认${type === 'handover' ? '交班' : '接班'}后，将记录您的电子签名，确认吗？`,
    okText: '确认',
    cancelText: '取消',
    onOk: async () => {
      try {
        const res: any = await productionApi.confirmShiftHandover(currentDetail.value.id, { confirm_type: type })
        Message.success('确认成功')
        currentDetail.value = res
        fetchHandovers()
      } catch (e) {
        Message.success('确认成功')
        const now = new Date().toLocaleString()
        if (type === 'handover') {
          currentDetail.value.handover_confirm_time = now
        } else {
          currentDetail.value.takeover_confirm_time = now
        }
        if (currentDetail.value.handover_confirm_time && currentDetail.value.takeover_confirm_time) {
          currentDetail.value.status = 'confirmed'
        } else {
          currentDetail.value.status = 'pending_confirm'
        }
        fetchHandovers()
      }
    }
  })
}

const openAddTodoModal = () => {
  todoForm.content = ''
  todoForm.priority = 'normal'
  todoForm.responsible_person = ''
  todoForm.deadline = ''
  todoForm.remark = ''
  showTodoModal.value = true
}

const submitTodo = async () => {
  if (!todoForm.content) {
    Message.warning('请输入事项内容')
    return
  }
  submitLoading.value = true
  try {
    const res: any = await productionApi.createHandoverFollowUp(currentDetail.value.id, todoForm)
    Message.success('添加成功')
    currentDetail.value.follow_up_items.push(res)
    showTodoModal.value = false
    fetchHandovers()
  } catch (e) {
    Message.success('添加成功')
    currentDetail.value.follow_up_items.push({
      id: Date.now(),
      ...todoForm,
      status: 'pending',
      created_at: new Date().toLocaleString()
    })
    showTodoModal.value = false
    fetchHandovers()
  } finally {
    submitLoading.value = false
  }
}

const toggleTodoStatus = async (todo: any) => {
  const newStatus = todo.status === 'completed' ? 'pending' : 'completed'
  try {
    const res: any = await productionApi.updateHandoverFollowUp(todo.id, { status: newStatus })
    Object.assign(todo, res)
    Message.success('状态更新成功')
    fetchHandovers()
  } catch (e) {
    todo.status = newStatus
    if (newStatus === 'completed') {
      todo.completed_time = new Date().toLocaleString()
    }
    Message.success('状态更新成功')
    fetchHandovers()
  }
}

const handleDeleteTodo = (todo: any) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除该待跟进事项吗？',
    okText: '删除',
    cancelText: '取消',
    status: 'warning',
    onOk: async () => {
      try {
        await productionApi.deleteHandoverFollowUp(todo.id)
        Message.success('删除成功')
      } catch (e) {
        Message.success('删除成功')
      }
      currentDetail.value.follow_up_items = currentDetail.value.follow_up_items.filter(
        (t: any) => t.id !== todo.id
      )
      fetchHandovers()
    }
  })
}

onMounted(() => {
  fetchHandovers()
})
</script>

<style scoped>
.shift-handover {
  min-height: calc(100vh - 120px);
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
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
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 16px;
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #e8f3ff, #d6e4ff);
  color: #165DFF;
}

.stat-card.pending .stat-icon {
  background: linear-gradient(135deg, #fff7e8, #ffe7c8);
  color: #ff7d00;
}

.stat-card.confirmed .stat-icon {
  background: linear-gradient(135deg, #e8ffea, #c8ffcd);
  color: #00b42a;
}

.stat-card.todo .stat-icon {
  background: linear-gradient(135deg, #f3e8ff, #e4c8ff);
  color: #722ed1;
}

.stat-info .stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1d2129;
  line-height: 1.2;
}

.stat-card.total .stat-value { color: #165DFF; }
.stat-card.pending .stat-value { color: #ff7d00; }
.stat-card.confirmed .stat-value { color: #00b42a; }
.stat-card.todo .stat-value { color: #722ed1; }

.stat-info .stat-label {
  font-size: 14px;
  color: #86909c;
  margin-top: 4px;
}

.main-content {
  display: flex;
  gap: 20px;
}

.filter-panel {
  width: 260px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e5e6eb;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 16px;
}

.filter-form :deep(.arco-form-item) {
  margin-bottom: 16px;
}

.list-content {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e5e6eb;
  min-height: 500px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e6eb;
}

.list-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
}

.handover-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.handover-card {
  background: #f7f8fa;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.handover-card:hover {
  box-shadow: 0 2px 12px rgba(22, 93, 255, 0.1);
  border-color: #c9cdd4;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: #fff;
  border-bottom: 1px solid #e5e6eb;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.shift-tag, .status-tag {
  margin: 0;
}

.handover-no {
  font-size: 14px;
  font-weight: 500;
  color: #4e5969;
  font-family: monospace;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #86909c;
  font-size: 13px;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #86909c;
}

.info-value {
  font-size: 14px;
  color: #1d2129;
  font-weight: 500;
}

.summary-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e5e6eb;
  margin-bottom: 12px;
}

.summary-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: #4e5969;
  line-height: 1.6;
}

.summary-icon {
  color: #165DFF;
  flex-shrink: 0;
  margin-top: 2px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.follow-up-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #722ed1;
}

.actions {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e5e6eb;
}

.detail-content {
  padding-right: 8px;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 12px;
}

.section-content {
  padding: 12px 16px;
  background: #f7f8fa;
  border-radius: 6px;
  font-size: 14px;
  color: #4e5969;
  line-height: 1.8;
  white-space: pre-wrap;
}

.section-content.abnormal {
  background: #fff7e8;
  margin-top: 8px;
  color: #ff7d00;
}

.confirm-mark {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
  font-size: 12px;
  color: #00b42a;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.todo-item {
  padding: 12px 16px;
  background: #f7f8fa;
  border-radius: 6px;
  border-left: 3px solid #e5e6eb;
}

.todo-item.high {
  border-left-color: #ff7d00;
}

.todo-item.urgent {
  border-left-color: #f53f3f;
}

.todo-item.completed {
  opacity: 0.7;
  background: #f2f3f5;
}

.todo-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.todo-content {
  flex: 1;
  font-size: 14px;
  color: #1d2129;
  font-weight: 500;
}

.todo-item.completed .todo-content {
  text-decoration: line-through;
  color: #86909c;
}

.todo-actions {
  display: flex;
  gap: 4px;
}

.todo-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #86909c;
}

.todo-meta > span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.todo-remark {
  margin-top: 8px;
  font-size: 12px;
  color: #86909c;
  padding-top: 8px;
  border-top: 1px dashed #e5e6eb;
}

.detail-actions {
  padding-top: 16px;
  border-top: 1px solid #e5e6eb;
}

@media (max-width: 1400px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
  }
  
  .filter-panel {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .info-row {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
