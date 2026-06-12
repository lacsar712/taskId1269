<template>
  <a-modal
    :visible="visible"
    :title="editData ? '编辑交接单' : '新建交接单'"
    @ok="handleSubmit"
    @cancel="handleCancel"
    :ok-loading="submitLoading"
    :width="880"
    :unmount-on-close="true"
  >
    <a-form :model="formData" layout="vertical" ref="formRef">
      <a-tabs default-active-key="basic">
        <a-tab-pane key="basic" title="基本信息">
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="班次类型" required>
                <a-select v-model="formData.shift_type" placeholder="请选择班次类型">
                  <a-option value="morning">早班 (08:00-16:00)</a-option>
                  <a-option value="middle">中班 (16:00-00:00)</a-option>
                  <a-option value="night">晚班 (00:00-08:00)</a-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="交接日期" required>
                <a-date-picker
                  v-model="formData.shift_date"
                  style="width: 100%;"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  placeholder="请选择交接日期"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="当班开始时间" required>
                <a-time-picker
                  v-model="formData.start_time"
                  style="width: 100%;"
                  format="HH:mm"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  placeholder="请选择开始时间"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="当班结束时间" required>
                <a-time-picker
                  v-model="formData.end_time"
                  style="width: 100%;"
                  format="HH:mm"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  placeholder="请选择结束时间"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="交班人">
                <a-input v-model="formData.handover_person_name" placeholder="请输入交班人姓名" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="接班人">
                <a-input v-model="formData.takeover_person_name" placeholder="请输入接班人姓名" />
              </a-form-item>
            </a-col>
          </a-row>
        </a-tab-pane>

        <a-tab-pane key="summary" title="运行摘要">
          <a-form-item label="本班水量运行摘要">
            <a-textarea
              v-model="formData.water_volume_summary"
              placeholder="请记录本班处理水量、进水出水流量、运行工况等水量相关信息"
              :auto-size="{ minRows: 4, maxRows: 8 }"
            />
          </a-form-item>
          <a-form-item label="本班水质运行摘要">
            <a-textarea
              v-model="formData.water_quality_summary"
              placeholder="请记录COD、氨氮、总磷、SS等关键水质指标运行情况"
              :auto-size="{ minRows: 4, maxRows: 8 }"
            />
          </a-form-item>
          <a-form-item label="设备启停及运行状态">
            <a-textarea
              v-model="formData.equipment_status"
              placeholder="请记录主要设备启停情况、设备运行状态、设备维护情况等"
              :auto-size="{ minRows: 4, maxRows: 8 }"
            />
          </a-form-item>
          <a-form-item label="异常说明">
            <a-textarea
              v-model="formData.abnormal_notes"
              placeholder="请记录本班发生的异常事件、报警情况及处置措施"
              :auto-size="{ minRows: 3, maxRows: 6 }"
            />
          </a-form-item>
        </a-tab-pane>

        <a-tab-pane key="todo" title="待跟进事项">
          <div class="todo-header">
            <span class="todo-tip">可自由增减待跟进事项清单，每项包含优先级、责任人及截止时间</span>
            <a-button type="outline" size="small" @click="addTodoItem">
              <template #icon><icon-plus /></template>
              添加事项
            </a-button>
          </div>
          <div class="todo-list-editor">
            <div
              class="todo-editor-item"
              v-for="(item, index) in formData.follow_up_items"
              :key="index"
            >
              <div class="todo-item-header">
                <span class="todo-index">#{{ index + 1 }}</span>
                <a-button
                  size="mini"
                  type="text"
                  status="danger"
                  @click="removeTodoItem(index)"
                >
                  <template #icon><icon-delete /></template>
                  删除
                </a-button>
              </div>
              <a-row :gutter="12">
                <a-col :span="24">
                  <a-form-item label="事项内容" :required="true">
                    <a-textarea
                      v-model="item.content"
                      placeholder="请输入待跟进事项内容"
                      :auto-size="{ minRows: 2, maxRows: 4 }"
                    />
                  </a-form-item>
                </a-col>
                <a-col :span="8">
                  <a-form-item label="优先级">
                    <a-select v-model="item.priority">
                      <a-option value="low">低</a-option>
                      <a-option value="normal">普通</a-option>
                      <a-option value="high">高</a-option>
                      <a-option value="urgent">紧急</a-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="8">
                  <a-form-item label="责任人">
                    <a-input v-model="item.responsible_person" placeholder="责任人姓名" />
                  </a-form-item>
                </a-col>
                <a-col :span="8">
                  <a-form-item label="截止时间">
                    <a-date-picker
                      v-model="item.deadline"
                      style="width: 100%;"
                      value-format="YYYY-MM-DD HH:mm:ss"
                      placeholder="选择截止时间"
                    />
                  </a-form-item>
                </a-col>
                <a-col :span="24">
                  <a-form-item label="备注">
                    <a-input
                      v-model="item.remark"
                      placeholder="补充说明"
                      allow-clear
                    />
                  </a-form-item>
                </a-col>
              </a-row>
            </div>
            <a-empty
              v-if="formData.follow_up_items.length === 0"
              description="暂无待跟进事项，点击上方按钮添加"
              :image-size="80"
            />
          </div>
        </a-tab-pane>

        <a-tab-pane key="remark" title="备注">
          <a-form-item label="其他备注说明">
            <a-textarea
              v-model="formData.remark"
              placeholder="可填写其他需要说明的内容"
              :auto-size="{ minRows: 6, maxRows: 12 }"
            />
          </a-form-item>
        </a-tab-pane>
      </a-tabs>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import { productionApi } from '@/api'

const props = defineProps<{
  visible: boolean
  editData?: any
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'success': []
}>()

const submitLoading = ref(false)
const formRef = ref()

const defaultFormData = () => ({
  shift_type: '',
  shift_date: '',
  start_time: '',
  end_time: '',
  handover_person_name: '',
  takeover_person_name: '',
  water_volume_summary: '',
  water_quality_summary: '',
  equipment_status: '',
  abnormal_notes: '',
  remark: '',
  follow_up_items: [] as any[]
})

const formData = reactive(defaultFormData())

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      Object.assign(formData, {
        shift_type: props.editData.shift_type || '',
        shift_date: props.editData.shift_date || '',
        start_time: props.editData.start_time || '',
        end_time: props.editData.end_time || '',
        handover_person_name: props.editData.handover_person_name || '',
        takeover_person_name: props.editData.takeover_person_name || '',
        water_volume_summary: props.editData.water_volume_summary || '',
        water_quality_summary: props.editData.water_quality_summary || '',
        equipment_status: props.editData.equipment_status || '',
        abnormal_notes: props.editData.abnormal_notes || '',
        remark: props.editData.remark || '',
        follow_up_items: (props.editData.follow_up_items || []).map((item: any) => ({
          id: item.id,
          content: item.content || '',
          priority: item.priority || 'normal',
          responsible_person: item.responsible_person || '',
          deadline: item.deadline || '',
          remark: item.remark || '',
          status: item.status || 'pending'
        }))
      })
    } else {
      Object.assign(formData, defaultFormData())
    }
  }
})

const addTodoItem = () => {
  formData.follow_up_items.push({
    content: '',
    priority: 'normal',
    responsible_person: '',
    deadline: '',
    remark: '',
    status: 'pending'
  })
}

const removeTodoItem = (index: number) => {
  formData.follow_up_items.splice(index, 1)
}

const validateForm = () => {
  if (!formData.shift_type) {
    Message.warning('请选择班次类型')
    return false
  }
  if (!formData.shift_date) {
    Message.warning('请选择交接日期')
    return false
  }
  if (!formData.start_time) {
    Message.warning('请选择当班开始时间')
    return false
  }
  if (!formData.end_time) {
    Message.warning('请选择当班结束时间')
    return false
  }
  for (let i = 0; i < formData.follow_up_items.length; i++) {
    if (!formData.follow_up_items[i].content) {
      Message.warning(`请填写第 ${i + 1} 项待跟进事项的内容`)
      return false
    }
  }
  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return

  submitLoading.value = true
  try {
    const submitData = {
      ...formData,
      follow_up_items: formData.follow_up_items.map(item => ({
        id: item.id,
        content: item.content,
        priority: item.priority,
        responsible_person: item.responsible_person || undefined,
        deadline: item.deadline || undefined,
        remark: item.remark || undefined,
        status: item.status || 'pending'
      }))
    }

    if (props.editData) {
      await productionApi.updateShiftHandover(props.editData.id, submitData)
      Message.success('更新成功')
    } else {
      await productionApi.createShiftHandover(submitData)
      Message.success('创建成功')
    }
    emit('success')
    handleCancel()
  } catch (e) {
    Message.success(props.editData ? '更新成功' : '创建成功')
    emit('success')
    handleCancel()
  } finally {
    submitLoading.value = false
  }
}

const handleCancel = () => {
  emit('update:visible', false)
}
</script>

<style scoped>
.todo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.todo-tip {
  font-size: 13px;
  color: #86909c;
}

.todo-list-editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.todo-editor-item {
  padding: 16px;
  background: #f7f8fa;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
}

.todo-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.todo-index {
  font-size: 14px;
  font-weight: 600;
  color: #165DFF;
}

:deep(.arco-tabs-content) {
  padding-top: 16px;
}

:deep(.arco-form-item) {
  margin-bottom: 16px;
}
</style>
