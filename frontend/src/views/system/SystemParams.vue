<template>
  <div class="page-container">
    <div class="page-header">
      <h2>系统参数设置</h2>
      <p>告警参数 / 报表参数 / 界面配置</p>
    </div>
    
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" title="告警参数">
        <a-card>
          <a-form :model="alarmParams" layout="vertical" style="max-width: 800px;">
            <a-form-item label="告警级别设置">
              <a-alert message="告警级别说明" type="info" style="margin-bottom: 16px;">
                <template #description>
                  紧急：立即处理，系统自动通知；警告：需要关注，24小时内处理；提示：一般信息，记录即可
                </template>
              </a-alert>
              <a-table
                :columns="alarmLevelColumns"
                :data="alarmLevels"
                :pagination="false"
                size="small"
              >
                <template #color="{ record }">
                  <a-tag :color="record.color">{{ record.name }}</a-tag>
                </template>
              </a-table>
            </a-form-item>
            
            <a-divider />
            
            <a-form-item label="告警通知设置">
              <a-space direction="vertical" style="width: 100%;">
                <a-checkbox v-model="alarmParams.emailNotify">启用邮件通知</a-checkbox>
                <a-checkbox v-model="alarmParams.smsNotify">启用短信通知</a-checkbox>
                <a-checkbox v-model="alarmParams.wechatNotify">启用微信通知</a-checkbox>
              </a-space>
            </a-form-item>
            
            <a-form-item label="告警延迟时间（秒）">
              <a-input-number v-model="alarmParams.delayTime" :min="0" :max="3600" style="width: 200px;" />
              <template #extra>告警触发后延迟多少秒才发送通知，避免频繁告警</template>
            </a-form-item>
            
            <a-form-item label="告警恢复通知">
              <a-radio-group v-model="alarmParams.recoverNotify">
                <a-radio value="always">总是通知</a-radio>
                <a-radio value="important">仅重要告警</a-radio>
                <a-radio value="never">不通知</a-radio>
              </a-radio-group>
            </a-form-item>
          </a-form>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="2" title="报表参数">
        <a-card>
          <a-form :model="reportParams" layout="vertical" style="max-width: 800px;">
            <a-form-item label="报表生成时间">
              <a-time-picker v-model="reportParams.generateTime" format="HH:mm" style="width: 200px;" />
              <template #extra>每日自动生成报表的时间</template>
            </a-form-item>
            
            <a-form-item label="报表保留天数">
              <a-input-number v-model="reportParams.retentionDays" :min="30" :max="3650" style="width: 200px;" />
              <template #extra>超过此天数的报表将被自动删除</template>
            </a-form-item>
            
            <a-form-item label="报表格式">
              <a-checkbox-group v-model="reportParams.formats">
                <a-checkbox value="pdf">PDF</a-checkbox>
                <a-checkbox value="excel">Excel</a-checkbox>
                <a-checkbox value="word">Word</a-checkbox>
              </a-checkbox-group>
            </a-form-item>
            
            <a-form-item label="报表模板">
              <a-select v-model="reportParams.template" placeholder="请选择模板" style="width: 300px;">
                <a-option value="default">默认模板</a-option>
                <a-option value="custom1">自定义模板1</a-option>
                <a-option value="custom2">自定义模板2</a-option>
              </a-select>
            </a-form-item>
            
            <a-form-item label="自动发送报表">
              <a-space direction="vertical">
                <a-checkbox v-model="reportParams.autoSend">启用自动发送</a-checkbox>
                <a-form-item v-if="reportParams.autoSend" label="接收人邮箱" style="margin-top: 8px;">
                  <a-textarea 
                    v-model="reportParams.recipients" 
                    placeholder="多个邮箱用逗号分隔"
                    :auto-size="{ minRows: 2 }"
                  />
                </a-form-item>
              </a-space>
            </a-form-item>
          </a-form>
        </a-card>
      </a-tab-pane>
      
      <a-tab-pane key="3" title="界面配置">
        <a-card>
          <a-form :model="uiParams" layout="vertical" style="max-width: 800px;">
            <a-form-item label="系统名称">
              <a-input v-model="uiParams.systemName" placeholder="请输入系统名称" style="width: 300px;" />
            </a-form-item>
            
            <a-form-item label="系统Logo">
              <a-upload
                :file-list="logoFileList"
                :limit="1"
                accept="image/*"
                @change="handleLogoChange"
              >
                <template #upload-button>
                  <a-button>
                    <template #icon><icon-upload /></template>
                    上传Logo
                  </a-button>
                </template>
              </a-upload>
              <template #extra>建议尺寸：200x60px，支持PNG、JPG格式</template>
            </a-form-item>
            
            <a-form-item label="主题颜色">
              <a-color-picker v-model="uiParams.primaryColor" />
              <template #extra>系统主色调</template>
            </a-form-item>
            
            <a-form-item label="页面刷新间隔（秒）">
              <a-input-number v-model="uiParams.refreshInterval" :min="5" :max="300" style="width: 200px;" />
              <template #extra>数据自动刷新间隔，0表示不自动刷新</template>
            </a-form-item>
            
            <a-form-item label="每页显示条数">
              <a-input-number v-model="uiParams.pageSize" :min="10" :max="100" :step="10" style="width: 200px;" />
            </a-form-item>
            
            <a-form-item label="默认时间范围">
              <a-select v-model="uiParams.defaultTimeRange" style="width: 200px;">
                <a-option value="today">今天</a-option>
                <a-option value="yesterday">昨天</a-option>
                <a-option value="week">近一周</a-option>
                <a-option value="month">近一月</a-option>
              </a-select>
            </a-form-item>
            
            <a-form-item label="功能设置">
              <a-space direction="vertical">
                <a-checkbox v-model="uiParams.enableWatermark">启用水印</a-checkbox>
                <a-checkbox v-model="uiParams.enableAnimation">启用动画效果</a-checkbox>
                <a-checkbox v-model="uiParams.enableSound">启用声音提示</a-checkbox>
              </a-space>
            </a-form-item>
            
            <a-form-item>
              <a-button type="primary" @click="saveUIParams">保存界面配置</a-button>
              <a-button style="margin-left: 8px;" @click="resetUIParams">重置为默认</a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'

const alarmLevels = ref([
  { id: 1, name: '紧急', level: 1, color: 'red', threshold: 90, description: '立即处理' },
  { id: 2, name: '警告', level: 2, color: 'orange', threshold: 70, description: '24小时内处理' },
  { id: 3, name: '提示', level: 3, color: 'blue', threshold: 50, description: '一般信息' }
])

const alarmParams = reactive({
  emailNotify: true,
  smsNotify: false,
  wechatNotify: true,
  delayTime: 60,
  recoverNotify: 'important'
})

const reportParams = reactive({
  generateTime: '08:00',
  retentionDays: 365,
  formats: ['pdf', 'excel'],
  template: 'default',
  autoSend: false,
  recipients: ''
})

const uiParams = reactive({
  systemName: '水处理管理系统',
  primaryColor: '#165DFF',
  refreshInterval: 30,
  pageSize: 20,
  defaultTimeRange: 'today',
  enableWatermark: false,
  enableAnimation: true,
  enableSound: true
})

const logoFileList = ref([])

const alarmLevelColumns = [
  { title: '级别名称', slotName: 'color', width: 120 },
  { title: '级别值', dataIndex: 'level', width: 100 },
  { title: '阈值', dataIndex: 'threshold', width: 100 },
  { title: '说明', dataIndex: 'description', width: 150 },
  { title: '操作', slotName: 'operations', width: 100 }
]

const editAlarmLevel = (record: any) => {
  Message.info(`编辑告警级别：${record.name}`)
}

const saveAlarmParams = () => {
  Message.success('告警参数保存成功')
}

const saveReportParams = () => {
  Message.success('报表参数保存成功')
}

const saveUIParams = () => {
  Message.success('界面配置保存成功')
}

const resetUIParams = () => {
  Object.assign(uiParams, {
    systemName: '水处理管理系统',
    primaryColor: '#165DFF',
    refreshInterval: 30,
    pageSize: 20,
    defaultTimeRange: 'today',
    enableWatermark: false,
    enableAnimation: true,
    enableSound: true
  })
  Message.success('已重置为默认配置')
}

const handleLogoChange = (fileList: any[]) => {
  logoFileList.value = fileList
  if (fileList.length > 0) {
    Message.success('Logo上传成功')
  }
}
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
