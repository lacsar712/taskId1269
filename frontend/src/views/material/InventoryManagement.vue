<template>
  <div class="inventory-management">
    <a-card title="库存管理">
      <template #extra>
        <a-space>
          <a-button @click="handleInventoryCheck">
            <template #icon><icon-sync /></template>
            库存盘点
          </a-button>
          <a-button @click="handleExport">
            <template #icon><icon-download /></template>
            导出库存
          </a-button>
        </a-space>
      </template>

      <!-- 统计概览 -->
      <a-row :gutter="16" style="margin-bottom: 20px;">
        <a-col :span="6">
          <a-statistic title="物资总数" :value="stats.totalItems">
            <template #prefix><icon-apps /></template>
          </a-statistic>
        </a-col>
        <a-col :span="6">
          <a-statistic title="库存总量" :value="stats.totalStock">
            <template #prefix><icon-storage /></template>
          </a-statistic>
        </a-col>
        <a-col :span="6">
          <a-statistic title="库存总值" :value="stats.totalValue" :value-style="{ color: '#165DFF' }">
            <template #prefix>¥</template>
          </a-statistic>
        </a-col>
        <a-col :span="6">
          <a-statistic title="预警物资" :value="stats.warningCount" :value-style="{ color: '#F53F3F' }">
            <template #prefix><icon-exclamation-circle /></template>
          </a-statistic>
        </a-col>
      </a-row>

      <!-- 搜索栏 -->
      <a-row :gutter="16" style="margin-bottom: 16px;">
        <a-col :span="6">
          <a-input v-model="searchForm.keyword" placeholder="物资名称/编号" allow-clear />
        </a-col>
        <a-col :span="6">
          <a-select v-model="searchForm.warehouseId" placeholder="仓库" allow-clear>
            <a-option value="1">主仓库</a-option>
            <a-option value="2">备件库</a-option>
            <a-option value="3">化学品库</a-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-select v-model="searchForm.category" placeholder="物资分类" allow-clear>
            <a-option value="chemical">化学药剂</a-option>
            <a-option value="spare">备品备件</a-option>
            <a-option value="consumable">办公耗材</a-option>
            <a-option value="tool">工具设备</a-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-space>
            <a-button type="primary" @click="handleSearch">查询</a-button>
            <a-button @click="handleReset">重置</a-button>
          </a-space>
        </a-col>
      </a-row>

      <!-- 库存列表 -->
      <a-table :columns="columns" :data="inventoryList" :pagination="pagination" :loading="loading">
        <template #stockStatus="{ record }">
          <a-tag :color="getStockStatusColor(record.stockStatus)">{{ record.stockStatusText }}</a-tag>
        </template>
        <template #operations="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="viewDetail(record)">详情</a-button>
            <a-button type="text" size="small" @click="viewHistory(record)">流水</a-button>
            <a-button type="text" size="small" @click="adjustStock(record)">调整</a-button>
          </a-space>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const loading = ref(false)

const searchForm = reactive({
  keyword: '',
  warehouseId: '',
  category: ''
})

const stats = reactive({
  totalItems: 256,
  totalStock: 15680,
  totalValue: 856000,
  warningCount: 8
})

const columns = [
  { title: '物资编号', dataIndex: 'materialNo' },
  { title: '物资名称', dataIndex: 'name' },
  { title: '规格型号', dataIndex: 'spec' },
  { title: '分类', dataIndex: 'category' },
  { title: '仓库', dataIndex: 'warehouseName' },
  { title: '单位', dataIndex: 'unit' },
  { title: '当前库存', dataIndex: 'currentStock' },
  { title: '安全库存', dataIndex: 'safeStock' },
  { title: '单价', dataIndex: 'price' },
  { title: '库存状态', dataIndex: 'stockStatus', slotName: 'stockStatus' },
  { title: '操作', slotName: 'operations', width: 150 }
]

const inventoryList = ref([
  {
    id: 1,
    materialNo: 'MAT-001',
    name: '聚合氯化铝',
    spec: '工业级/25kg/袋',
    category: '化学药剂',
    warehouseName: '化学品库',
    unit: '袋',
    currentStock: 500,
    safeStock: 200,
    price: '¥85.00',
    stockStatus: 'normal',
    stockStatusText: '正常'
  },
  {
    id: 2,
    materialNo: 'MAT-002',
    name: '污泥泵叶轮',
    spec: 'DN150',
    category: '备品备件',
    warehouseName: '备件库',
    unit: '个',
    currentStock: 8,
    safeStock: 10,
    price: '¥2,500.00',
    stockStatus: 'warning',
    stockStatusText: '库存预警'
  },
  {
    id: 3,
    materialNo: 'MAT-003',
    name: '次氯酸钠',
    spec: '工业级/50kg/桶',
    category: '化学药剂',
    warehouseName: '化学品库',
    unit: '桶',
    currentStock: 150,
    safeStock: 100,
    price: '¥120.00',
    stockStatus: 'normal',
    stockStatusText: '正常'
  },
  {
    id: 4,
    materialNo: 'MAT-004',
    name: '密封圈',
    spec: 'DN100',
    category: '备品备件',
    warehouseName: '备件库',
    unit: '个',
    currentStock: 2,
    safeStock: 20,
    price: '¥35.00',
    stockStatus: 'danger',
    stockStatusText: '库存不足'
  }
])

const pagination = reactive({
  total: 4,
  current: 1,
  pageSize: 10
})

const getStockStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    normal: 'green',
    warning: 'orange',
    danger: 'red'
  }
  return colors[status] || 'gray'
}

const handleSearch = () => {
  Message.success('查询成功')
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.warehouseId = ''
  searchForm.category = ''
}

const handleInventoryCheck = () => {
  Message.info('开始库存盘点')
}

const handleExport = () => {
  Message.success('导出库存成功')
}

const viewDetail = (record: any) => {
  Message.info(`查看详情: ${record.name}`)
}

const viewHistory = (record: any) => {
  Message.info(`查看流水: ${record.name}`)
}

const adjustStock = (record: any) => {
  Message.info(`调整库存: ${record.name}`)
}
</script>

<style scoped>
.inventory-management {
  padding: 20px;
}
</style>
