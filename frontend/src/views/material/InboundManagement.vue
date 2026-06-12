<template>
  <div class="inbound-management">
    <a-card title="入库管理">
      <template #extra>
        <a-button type="primary" @click="showInboundModal = true">
          <template #icon><icon-plus /></template>
          新建入库单
        </a-button>
      </template>

      <!-- 搜索栏 -->
      <a-row :gutter="16" style="margin-bottom: 16px;">
        <a-col :span="6">
          <a-input v-model="searchForm.orderNo" placeholder="入库单号" allow-clear />
        </a-col>
        <a-col :span="6">
          <a-select v-model="searchForm.status" placeholder="入库状态" allow-clear>
            <a-option value="pending">待入库</a-option>
            <a-option value="completed">已入库</a-option>
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

      <!-- 入库单列表 -->
      <a-table :columns="columns" :data="inboundList" :pagination="pagination" :loading="loading">
        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">{{ record.statusText }}</a-tag>
        </template>
        <template #operations="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="viewInbound(record)">查看</a-button>
            <a-button v-if="record.status === 'pending'" type="text" size="small" status="success" @click="confirmInbound(record)">确认入库</a-button>
            <a-button v-if="record.status === 'pending'" type="text" size="small" status="danger" @click="cancelInbound(record)">取消</a-button>
          </a-space>
        </template>
      </a-table>
    </a-card>

    <!-- 新建入库单弹窗 -->
    <a-modal v-model:visible="showInboundModal" title="新建入库单" width="700px" @ok="handleSaveInbound">
      <a-form :model="inboundForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="供应商" required>
              <a-select v-model="inboundForm.supplierId" placeholder="请选择供应商">
                <a-option v-for="s in supplierList" :key="s.id" :value="s.id">{{ s.name }}</a-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="仓库" required>
              <a-select v-model="inboundForm.warehouseId" placeholder="请选择仓库">
                <a-option value="1">主仓库</a-option>
                <a-option value="2">备件库</a-option>
                <a-option value="3">化学品库</a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="入库明细">
          <a-table :columns="detailColumns" :data="inboundForm.details" :pagination="false" size="small">
            <template #quantity="{ record }">
              <a-input-number v-model="record.quantity" :min="1" size="small" />
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
          <a-textarea v-model="inboundForm.remark" placeholder="请输入备注" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)
const showInboundModal = ref(false)

const searchForm = reactive({
  orderNo: '',
  status: '',
  dateRange: []
})

const inboundForm = reactive({
  supplierId: '',
  warehouseId: '',
  details: [] as any[],
  remark: ''
})

const columns = [
  { title: '入库单号', dataIndex: 'orderNo' },
  { title: '供应商', dataIndex: 'supplierName' },
  { title: '仓库', dataIndex: 'warehouseName' },
  { title: '物资数量', dataIndex: 'itemCount' },
  { title: '总金额', dataIndex: 'totalAmount' },
  { title: '状态', dataIndex: 'status', slotName: 'status' },
  { title: '入库时间', dataIndex: 'inboundTime' },
  { title: '操作人', dataIndex: 'operator' },
  { title: '操作', slotName: 'operations', width: 180 }
]

const detailColumns = [
  { title: '物资名称', dataIndex: 'materialName' },
  { title: '规格型号', dataIndex: 'spec' },
  { title: '单位', dataIndex: 'unit' },
  { title: '数量', dataIndex: 'quantity', slotName: 'quantity' },
  { title: '单价', dataIndex: 'price' },
  { title: '操作', slotName: 'action', width: 80 }
]

const inboundList = ref([
  {
    id: 1,
    orderNo: 'IN-2024-001',
    supplierName: '华东化工有限公司',
    warehouseName: '化学品库',
    itemCount: 5,
    totalAmount: '¥12,500.00',
    status: 'completed',
    statusText: '已入库',
    inboundTime: '2024-01-15 10:30',
    operator: '张三'
  },
  {
    id: 2,
    orderNo: 'IN-2024-002',
    supplierName: '通用机械厂',
    warehouseName: '备件库',
    itemCount: 8,
    totalAmount: '¥35,600.00',
    status: 'pending',
    statusText: '待入库',
    inboundTime: '-',
    operator: '李四'
  }
])

const supplierList = ref([
  { id: 1, name: '华东化工有限公司' },
  { id: 2, name: '通用机械厂' },
  { id: 3, name: '环保设备公司' }
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

const viewInbound = (record: any) => {
  Message.info(`查看入库单: ${record.orderNo}`)
}

const confirmInbound = (record: any) => {
  Message.success(`确认入库: ${record.orderNo}`)
}

const cancelInbound = (record: any) => {
  Message.warning(`取消入库单: ${record.orderNo}`)
}

const addDetail = () => {
  inboundForm.details.push({
    materialName: '物资' + (inboundForm.details.length + 1),
    spec: '标准规格',
    unit: '件',
    quantity: 1,
    price: 100
  })
}

const removeDetail = (index: number) => {
  inboundForm.details.splice(index, 1)
}

const handleSaveInbound = () => {
  Message.success('入库单保存成功')
  showInboundModal.value = false
}
</script>

<style scoped>
.inbound-management {
  padding: 20px;
}
</style>
