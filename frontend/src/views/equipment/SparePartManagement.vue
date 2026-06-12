<template>
  <div class="page-container">
    <div class="page-header">
      <h2>备件管理</h2>
      <p>备件台账 / 出入库管理 / 库存预警</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="备件台账">
        <div class="table-operations">
          <a-input-search placeholder="搜索备件" style="width: 240px;" />
          <a-button type="primary">
            <template #icon><icon-plus /></template>
            新增备件
          </a-button>
        </div>
        <a-table :columns="columns" :data="spareParts">
          <template #status="{ record }">
            <a-tag :color="record.status === 'normal' ? 'green' : record.status === 'low' ? 'orange' : 'red'">
              {{ record.status === 'normal' ? '正常' : record.status === 'low' ? '库存低' : '缺货' }}
            </a-tag>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="出入库记录">
        <a-table :columns="recordColumns" :data="records">
          <template #type="{ record }">
            <a-tag :color="record.type === 'in' ? 'green' : 'blue'">{{ record.type === 'in' ? '入库' : '出库' }}</a-tag>
          </template>
        </a-table>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="库存预警">
        <a-alert type="warning" style="margin-bottom: 16px;">
          当前有 {{ lowStockCount }} 种备件库存低于安全库存，请及时补充！
        </a-alert>
        <a-table :columns="alertColumns" :data="lowStockItems" />
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const lowStockCount = ref(3)

const columns = [
  { title: '备件编号', dataIndex: 'code' },
  { title: '备件名称', dataIndex: 'name' },
  { title: '规格型号', dataIndex: 'model' },
  { title: '库存数量', dataIndex: 'stock_quantity' },
  { title: '最小库存', dataIndex: 'min_stock' },
  { title: '单价', dataIndex: 'unit_price' },
  { title: '状态', slotName: 'status' }
]

const recordColumns = [
  { title: '单号', dataIndex: 'no' },
  { title: '备件名称', dataIndex: 'name' },
  { title: '类型', slotName: 'type' },
  { title: '数量', dataIndex: 'quantity' },
  { title: '操作人', dataIndex: 'operator' },
  { title: '时间', dataIndex: 'time' }
]

const alertColumns = [
  { title: '备件名称', dataIndex: 'name' },
  { title: '当前库存', dataIndex: 'stock_quantity' },
  { title: '最小库存', dataIndex: 'min_stock' },
  { title: '缺口数量', dataIndex: 'gap' }
]

const spareParts = ref([
  { code: 'SP001', name: '风机轴承', model: '6312', stock_quantity: 15, min_stock: 10, unit_price: 350, status: 'normal' },
  { code: 'SP002', name: '水泵密封圈', model: 'DN150', stock_quantity: 5, min_stock: 10, unit_price: 80, status: 'low' },
  { code: 'SP003', name: '变频器', model: 'VFD-15KW', stock_quantity: 2, min_stock: 3, unit_price: 5800, status: 'low' }
])

const records = ref([
  { no: 'IO20240115001', name: '风机轴承', type: 'in', quantity: 10, operator: '张三', time: '2024-01-15 09:00' },
  { no: 'IO20240114001', name: '水泵密封圈', type: 'out', quantity: 2, operator: '李四', time: '2024-01-14 14:30' }
])

const lowStockItems = ref([
  { name: '水泵密封圈', stock_quantity: 5, min_stock: 10, gap: 5 },
  { name: '变频器', stock_quantity: 2, min_stock: 3, gap: 1 },
  { name: '电机', stock_quantity: 0, min_stock: 2, gap: 2 }
])
</script>

<style scoped>
.table-operations { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
