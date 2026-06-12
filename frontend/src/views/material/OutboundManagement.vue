<template>
  <div class="outbound-management">
    <a-card title="出库管理">
      <template #extra>
        <a-button type="primary" @click="showOutboundModal = true">
          <template #icon><icon-plus /></template>
          新建出库单
        </a-button>
      </template>

      <!-- 搜索栏 -->
      <a-row :gutter="16" style="margin-bottom: 16px;">
        <a-col :span="6">
          <a-input v-model="searchForm.orderNo" placeholder="出库单号" allow-clear />
        </a-col>
        <a-col :span="6">
          <a-select v-model="searchForm.status" placeholder="出库状态" allow-clear>
            <a-option value="pending">待出库</a-option>
            <a-option value="completed">已出库</a-option>
            <a-option value="cancelled">已取消</a-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-range-picker v-model="searchForm.dateRange" style="width: 100%;" />
        </a-col>
        <a-col :span="6">
          <a-space>
            <a-button type="primary" @click="handleSearch">查询</a-button>
            <a-button @click="handleReset">重置</a-button>
          </a-space>
        </a-col>
      </a-row>

      <!-- 出库单列表 -->
      <a-table :columns="columns" :data="outboundList" :pagination="pagination" :loading="loading">
        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">{{ record.statusText }}</a-tag>
        </template>
        <template #operations="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="viewOutbound(record)">查看</a-button>
            <a-button v-if="record.status === 'pending'" type="text" size="small" status="success" @click="confirmOutbound(record)">确认出库</a-button>
            <a-button v-if="record.status === 'pending'" type="text" size="small" status="danger" @click="cancelOutbound(record)">取消</a-button>
          </a-space>
        </template>
      </a-table>
    </a-card>

    <!-- 新建出库单弹窗 -->
    <a-modal v-model:visible="showOutboundModal" title="新建出库单" width="700px" @ok="handleSaveOutbound">
      <a-form :model="outboundForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="领用部门" required>
              <a-select v-model="outboundForm.department" placeholder="请选择领用部门">
                <a-option value="production">生产部</a-option>
                <a-option value="maintenance">设备维护部</a-option>
                <a-option value="laboratory">化验室</a-option>
                <a-option value="safety">安全部</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="仓库" required>
              <a-select v-model="outboundForm.warehouseId" placeholder="请选择仓库">
                <a-option value="1">主仓库</a-option>
                <a-option value="2">备件库</a-option>
                <a-option value="3">化学品库</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="领用人">
              <a-input v-model="outboundForm.receiver" placeholder="请输入领用人" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="用途">
              <a-input v-model="outboundForm.purpose" placeholder="请输入用途" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="出库明细">
          <a-table :columns="detailColumns" :data="outboundForm.details" :pagination="false" size="small">
            <template #quantity="{ record }">
              <a-input-number v-model="record.quantity" :min="1" :max="record.stock" size="small" />
            </template>
            <template #action="{ rowIndex }">
              <a-button type="text" size="small" status="danger" @click="removeDetail(rowIndex)">删除</a-button>
            </template>
          </a-table>
          <a-button type="dashed" long style="margin-top: 8px;" @click="addDetail">
            <template #icon><icon-plus /></template>
            添加物资
          </a-button>
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model="outboundForm.remark" placeholder="请输入备注" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const showOutboundModal = ref(false)

const searchForm = reactive({
  orderNo: '',
  status: '',
  dateRange: []
})

const outboundForm = reactive({
  department: '',
  warehouseId: '',
  receiver: '',
  purpose: '',
  details: [] as any[],
  remark: ''
})

const columns = [
  { title: '出库单号', dataIndex: 'orderNo' },
  { title: '领用部门', dataIndex: 'department' },
  { title: '领用人', dataIndex: 'receiver' },
  { title: '仓库', dataIndex: 'warehouseName' },
  { title: '物资数量', dataIndex: 'itemCount' },
  { title: '状态', dataIndex: 'status', slotName: 'status' },
  { title: '出库时间', dataIndex: 'outboundTime' },
  { title: '操作人', dataIndex: 'operator' },
  { title: '操作', slotName: 'operations', width: 180 }
]

const detailColumns = [
  { title: '物资名称', dataIndex: 'materialName' },
  { title: '规格型号', dataIndex: 'spec' },
  { title: '单位', dataIndex: 'unit' },
  { title: '库存', dataIndex: 'stock' },
  { title: '出库数量', dataIndex: 'quantity', slotName: 'quantity' },
  { title: '操作', slotName: 'action', width: 80 }
]

const outboundList = ref([
  {
    id: 1,
    orderNo: 'OUT-2024-001',
    department: '设备维护部',
    receiver: '王工',
    warehouseName: '备件库',
    itemCount: 3,
    status: 'completed',
    statusText: '已出库',
    outboundTime: '2024-01-15 14:30',
    operator: '张三'
  },
  {
    id: 2,
    orderNo: 'OUT-2024-002',
    department: '化验室',
    receiver: '李技师',
    warehouseName: '化学品库',
    itemCount: 5,
    status: 'pending',
    statusText: '待出库',
    outboundTime: '-',
    operator: '李四'
  }
])

const pagination = reactive({
  total: 2,
  current: 1,
  pageSize: 10
})

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    pending: 'orange',
    completed: 'green',
    cancelled: 'gray'
  }
  return colors[status] || 'gray'
}

const handleSearch = () => {
  Message.success('查询成功')
}

const handleReset = () => {
  searchForm.orderNo = ''
  searchForm.status = ''
  searchForm.dateRange = []
}

const viewOutbound = (record: any) => {
  Message.info(`查看出库单: ${record.orderNo}`)
}

const confirmOutbound = (record: any) => {
  Message.success(`确认出库: ${record.orderNo}`)
}

const cancelOutbound = (record: any) => {
  Message.warning(`取消出库单: ${record.orderNo}`)
}

const addDetail = () => {
  outboundForm.details.push({
    materialName: '物资' + (outboundForm.details.length + 1),
    spec: '标准规格',
    unit: '件',
    stock: 100,
    quantity: 1
  })
}

const removeDetail = (index: number) => {
  outboundForm.details.splice(index, 1)
}

const handleSaveOutbound = () => {
  Message.success('出库单保存成功')
  showOutboundModal.value = false
}
</script>

<style scoped>
.outbound-management {
  padding: 20px;
}
</style>
