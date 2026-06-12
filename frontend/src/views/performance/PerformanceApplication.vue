<template>
  <div class="page-container">
    <div class="page-header">
      <h2>绩效应用</h2>
      <p>绩效报表 / 奖惩管理 / 改进计划</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="绩效报表">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 20px;">
            <a-form-item label="报表类型">
              <a-select v-model="reportType" placeholder="请选择类型" style="width: 150px;">
                <a-option value="个人报表">个人报表</a-option>
                <a-option value="班组报表">班组报表</a-option>
                <a-option value="综合报表">综合报表</a-option>
              </a-select>
            </a-form-item>
            <a-form-item label="时间范围">
              <a-range-picker v-model="reportDateRange" style="width: 300px;" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="generateReport">生成报表</a-button>
              <a-button style="margin-left: 8px;" @click="exportReport">导出Excel</a-button>
            </a-form-item>
          </a-form>
          
          <a-row :gutter="16" style="margin-bottom: 20px;">
            <a-col :span="6">
              <a-statistic title="报表总数" :value="reportStats.total">
                <template #prefix><icon-file /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="本月生成" :value="reportStats.month">
                <template #prefix><icon-calendar /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="待审核" :value="reportStats.pending">
                <template #prefix><icon-clock-circle /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="已发布" :value="reportStats.published">
                <template #prefix><icon-check-circle /></template>
              </a-statistic>
            </a-col>
          </a-row>
          
          <a-table
            :columns="reportColumns"
            :data="reports"
            :pagination="reportPagination"
          >
            <template #type="{ record }">
              <a-tag :color="getReportTypeColor(record.type)">{{ record.type }}</a-tag>
            </template>
            <template #status="{ record }">
              <a-tag :color="getReportStatusColor(record.status)">{{ record.status }}</a-tag>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-popconfirm content="确定要删除该报告吗？" @ok="deleteReport(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="奖惩管理">
        <a-card>
          <template #title>
            <a-space>
              <span>奖惩记录</span>
              <a-button type="primary" @click="showRewardModal = true">
                <template #icon><icon-plus /></template>
                新增奖惩
              </a-button>
            </a-space>
          </template>
          
          <a-row :gutter="16" style="margin-bottom: 20px;">
            <a-col :span="8">
              <a-card>
                <a-statistic title="奖励总额" :value="rewardStats.totalReward" :precision="2" prefix="¥">
                  <template #prefix><icon-gift /></template>
                </a-statistic>
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card>
                <a-statistic title="惩罚总额" :value="rewardStats.totalPunish" :precision="2" prefix="¥">
                  <template #prefix><icon-exclamation-circle /></template>
                </a-statistic>
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card>
                <a-statistic title="净奖励" :value="rewardStats.netReward" :precision="2" prefix="¥">
                  <template #prefix><icon-wallet /></template>
                </a-statistic>
              </a-card>
            </a-col>
          </a-row>
          
          <a-table
            :columns="rewardColumns"
            :data="rewards"
            :pagination="rewardPagination"
          >
            <template #type="{ record }">
              <a-tag :color="record.type === '奖励' ? 'green' : 'red'">{{ record.type }}</a-tag>
            </template>
            <template #amount="{ record }">
              <span :style="{ color: record.type === '奖励' ? '#00B42A' : '#F53F3F' }">
                {{ record.type === '奖励' ? '+' : '-' }}¥{{ record.amount }}
              </span>
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="editReward(record)">编辑</a-button>
                <a-popconfirm content="确定要删除该奖惩记录吗？" @ok="deleteReward(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="改进计划">
        <a-card>
          <template #title>
            <a-space>
              <span>改进计划列表</span>
              <a-button type="primary" @click="showPlanModal = true">
                <template #icon><icon-plus /></template>
                新建计划
              </a-button>
            </a-space>
          </template>
          
          <a-row :gutter="16" style="margin-bottom: 20px;">
            <a-col :span="6">
              <a-statistic title="进行中" :value="planStats.inProgress">
                <template #prefix><icon-play-circle /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="已完成" :value="planStats.completed">
                <template #prefix><icon-check-circle /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="已延期" :value="planStats.delayed">
                <template #prefix><icon-clock-circle /></template>
              </a-statistic>
            </a-col>
            <a-col :span="6">
              <a-statistic title="完成率" :value="planStats.completionRate" suffix="%">
                <template #prefix><icon-trophy /></template>
              </a-statistic>
            </a-col>
          </a-row>
          
          <a-table
            :columns="planColumns"
            :data="plans"
            :pagination="planPagination"
          >
            <template #priority="{ record }">
              <a-tag :color="getPriorityColor(record.priority)">{{ record.priority }}</a-tag>
            </template>
            <template #status="{ record }">
              <a-tag :color="getPlanStatusColor(record.status)">{{ record.status }}</a-tag>
            </template>
            <template #progress="{ record }">
              <a-progress :percent="record.progress" :show-text="true" />
            </template>
            <template #operations="{ record }">
              <a-space>
                <a-button type="text" size="small" @click="editPlan(record)">编辑</a-button>
                <a-popconfirm content="确定要删除该计划吗？" @ok="deletePlan(record)">
                  <a-button type="text" size="small" status="danger">删除</a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </a-table>
        </a-card>
      </a-tab-pane>
    </a-tabs>
    
    <!-- 新增奖惩弹窗 -->
    <a-modal
      v-model:visible="showRewardModal"
      :title="editingReward ? '编辑奖惩' : '新增奖惩'"
      @ok="saveReward"
    >
      <a-form :model="rewardForm" layout="vertical">
        <a-form-item label="类型" required>
          <a-radio-group v-model="rewardForm.type">
            <a-radio value="奖励">奖励</a-radio>
            <a-radio value="惩罚">惩罚</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="人员" required>
          <a-input v-model="rewardForm.person" placeholder="请输入人员姓名" />
        </a-form-item>
        <a-form-item label="金额" required>
          <a-input-number v-model="rewardForm.amount" :min="0" :precision="2" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="原因" required>
          <a-textarea v-model="rewardForm.reason" :auto-size="{ minRows: 3 }" />
        </a-form-item>
      </a-form>
    </a-modal>
    
    <!-- 新建计划弹窗 -->
    <a-modal
      v-model:visible="showPlanModal"
      :title="editingPlan ? '编辑计划' : '新建计划'"
      @ok="savePlan"
    >
      <a-form :model="planForm" layout="vertical">
        <a-form-item label="计划名称" required>
          <a-input v-model="planForm.name" placeholder="请输入计划名称" />
        </a-form-item>
        <a-form-item label="优先级" required>
          <a-select v-model="planForm.priority">
            <a-option value="高">高</a-option>
            <a-option value="中">中</a-option>
            <a-option value="低">低</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="负责人" required>
          <a-input v-model="planForm.owner" placeholder="请输入负责人" />
        </a-form-item>
        <a-form-item label="计划内容" required>
          <a-textarea v-model="planForm.content" :auto-size="{ minRows: 4 }" />
        </a-form-item>
        <a-form-item label="截止日期" required>
          <a-date-picker v-model="planForm.deadline" style="width: 100%;" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const reportType = ref('个人报表')
const reportDateRange = ref([])
const showRewardModal = ref(false)
const showPlanModal = ref(false)
const editingReward = ref<any>(null)
const editingPlan = ref<any>(null)

const reportPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const rewardPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const planPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const reportStats = reactive({
  total: 156,
  month: 12,
  pending: 3,
  published: 145
})

const rewardStats = reactive({
  totalReward: 125000,
  totalPunish: 15000,
  netReward: 110000
})

const planStats = reactive({
  inProgress: 8,
  completed: 15,
  delayed: 2,
  completionRate: 75
})

const reports = ref([
  { id: 1, name: '2026年1月个人绩效报表', type: '个人报表', dateRange: '2026-01-01 ~ 2026-01-31', creator: '系统', createTime: '2026-02-01 08:00:00', status: '已发布' },
  { id: 2, name: '2026年1月班组绩效报表', type: '班组报表', dateRange: '2026-01-01 ~ 2026-01-31', creator: '系统', createTime: '2026-02-01 08:00:00', status: '已发布' },
  { id: 3, name: '2026年1月综合绩效报表', type: '综合报表', dateRange: '2026-01-01 ~ 2026-01-31', creator: '管理员', createTime: '2026-02-01 10:00:00', status: '待审核' }
])

const rewards = ref([
  { id: 1, type: '奖励', person: '张三', amount: 500, reason: '月度绩效优秀', date: '2026-02-01' },
  { id: 2, type: '奖励', person: '李四', amount: 300, reason: '设备维护及时', date: '2026-02-02' },
  { id: 3, type: '惩罚', person: '王五', amount: 200, reason: '操作不规范', date: '2026-02-03' }
])

const plans = ref([
  { id: 1, name: '提高COD去除率', priority: '高', owner: '张三', content: '优化曝气系统，提高COD去除率至90%以上', deadline: '2026-03-01', progress: 60, status: '进行中' },
  { id: 2, name: '降低吨水电耗', priority: '中', owner: '李四', content: '优化设备运行策略，降低吨水电耗5%', deadline: '2026-03-15', progress: 100, status: '已完成' },
  { id: 3, name: '完善安全制度', priority: '高', owner: '王五', content: '完善安全管理制度，减少安全事故', deadline: '2026-02-28', progress: 80, status: '进行中' }
])

const rewardForm = reactive({
  type: '奖励',
  person: '',
  amount: 0,
  reason: ''
})

const planForm = reactive({
  name: '',
  priority: '中',
  owner: '',
  content: '',
  deadline: ''
})

const reportColumns = [
  { title: '报表名称', dataIndex: 'name', ellipsis: true },
  { title: '报表类型', slotName: 'type', width: 120 },
  { title: '时间范围', dataIndex: 'dateRange', width: 200 },
  { title: '创建人', dataIndex: 'creator', width: 100 },
  { title: '创建时间', dataIndex: 'createTime', width: 180 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const rewardColumns = [
  { title: '类型', slotName: 'type', width: 100 },
  { title: '人员', dataIndex: 'person', width: 100 },
  { title: '金额', slotName: 'amount', width: 120 },
  { title: '原因', dataIndex: 'reason', ellipsis: true },
  { title: '日期', dataIndex: 'date', width: 120 },
  { title: '操作', slotName: 'operations', width: 150 }
]

const planColumns = [
  { title: '计划名称', dataIndex: 'name', ellipsis: true },
  { title: '优先级', slotName: 'priority', width: 100 },
  { title: '负责人', dataIndex: 'owner', width: 100 },
  { title: '截止日期', dataIndex: 'deadline', width: 120 },
  { title: '进度', slotName: 'progress', width: 150 },
  { title: '状态', slotName: 'status', width: 100 },
  { title: '操作', slotName: 'operations', width: 200 }
]

const getReportTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    '个人报表': 'blue',
    '班组报表': 'green',
    '综合报表': 'orange'
  }
  return colors[type] || 'gray'
}

const getReportStatusColor = (status: string) => {
  return status === '已发布' ? 'green' : 'orange'
}

const getPriorityColor = (priority: string) => {
  const colors: Record<string, string> = {
    '高': 'red',
    '中': 'orange',
    '低': 'blue'
  }
  return colors[priority] || 'gray'
}

const getPlanStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    '进行中': 'blue',
    '已完成': 'green',
    '已延期': 'red'
  }
  return colors[status] || 'gray'
}

const generateReport = () => {
  Message.success('报表生成中，请稍候...')
  setTimeout(() => {
    reports.value.unshift({
      id: Date.now(),
      name: `${reportType.value}-${new Date().toLocaleDateString()}`,
      type: reportType.value,
      dateRange: '2026-02-01 ~ 2026-02-28',
      creator: '当前用户',
      createTime: new Date().toLocaleString('zh-CN'),
      status: '待审核'
    })
    Message.success('报表生成成功')
  }, 1000)
}

const exportReport = () => {
  Message.success('报表导出中...')
}

const viewReport = (record: any) => {
  Message.info(`查看报表：${record.name}`)
}

const downloadReport = (record: any) => {
  Message.success(`下载报表：${record.name}`)
}

const deleteReport = (record: any) => {
  const index = reports.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    reports.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const editReward = (record: any) => {
  editingReward.value = record
  Object.assign(rewardForm, record)
  showRewardModal.value = true
}

const deleteReward = (record: any) => {
  const index = rewards.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    rewards.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const saveReward = () => {
  if (!rewardForm.person || !rewardForm.amount || !rewardForm.reason) {
    Message.warning('请填写完整信息')
    return
  }
  
  if (editingReward.value) {
    const index = rewards.value.findIndex(item => item.id === editingReward.value.id)
    if (index > -1) {
      Object.assign(rewards.value[index], rewardForm, { date: new Date().toLocaleDateString() })
    }
    Message.success('编辑成功')
  } else {
    rewards.value.push({
      id: Date.now(),
      ...rewardForm,
      date: new Date().toLocaleDateString()
    })
    Message.success('新增成功')
  }
  showRewardModal.value = false
  editingReward.value = null
  Object.assign(rewardForm, { type: '奖励', person: '', amount: 0, reason: '' })
}

const viewPlan = (record: any) => {
  Message.info(`查看计划：${record.name}`)
}

const editPlan = (record: any) => {
  editingPlan.value = record
  Object.assign(planForm, record)
  showPlanModal.value = true
}

const deletePlan = (record: any) => {
  const index = plans.value.findIndex(item => item.id === record.id)
  if (index > -1) {
    plans.value.splice(index, 1)
    Message.success('删除成功')
  }
}

const savePlan = () => {
  if (!planForm.name || !planForm.owner || !planForm.content || !planForm.deadline) {
    Message.warning('请填写完整信息')
    return
  }
  
  if (editingPlan.value) {
    const index = plans.value.findIndex(item => item.id === editingPlan.value.id)
    if (index > -1) {
      Object.assign(plans.value[index], planForm, { progress: 0, status: '进行中' })
    }
    Message.success('编辑成功')
  } else {
    plans.value.push({
      id: Date.now(),
      ...planForm,
      deadline: typeof planForm.deadline === 'string' ? planForm.deadline : planForm.deadline.format('YYYY-MM-DD'),
      progress: 0,
      status: '进行中'
    })
    Message.success('新建成功')
  }
  showPlanModal.value = false
  editingPlan.value = null
  Object.assign(planForm, { name: '', priority: '中', owner: '', content: '', deadline: '' })
}

// 初始化分页
reportPagination.total = reports.value.length
rewardPagination.total = rewards.value.length
planPagination.total = plans.value.length
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
