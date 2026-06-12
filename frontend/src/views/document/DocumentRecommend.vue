<template>
  <div class="page-container">
    <div class="page-header">
      <h2>常用文档推荐</h2>
      <p>热门文档 / 个性化推荐</p>
    </div>
    
    <a-row :gutter="16">
      <a-col :span="16">
        <a-card title="热门文档" style="margin-bottom: 16px;">
          <a-tabs v-model:active-key="hotTab">
            <a-tab-pane key="today" title="今日热门">
              <a-list :data="todayHotDocs">
                <template #item="{ item }">
                  <a-list-item>
                    <a-list-item-meta>
                      <template #title>
                        <a-space>
                          <span>{{ item.name }}</span>
                          <a-tag color="red">热门</a-tag>
                        </a-space>
                      </template>
                      <template #description>
                        <a-space>
                          <span>{{ item.category_name }}</span>
                          <span>下载次数: {{ item.download_count }}</span>
                          <span>浏览次数: {{ item.view_count }}</span>
                        </a-space>
                      </template>
                    </a-list-item-meta>
                    <template #actions>
                      <a-space>
                        <a-button type="text" size="small" @click="handleDownload(item)">下载</a-button>
                        <a-button type="text" size="small" @click="handlePreview(item)">预览</a-button>
                      </a-space>
                    </template>
                  </a-list-item>
                </template>
              </a-list>
            </a-tab-pane>
            
            <a-tab-pane key="week" title="本周热门">
              <a-list :data="weekHotDocs">
                <template #item="{ item }">
                  <a-list-item>
                    <a-list-item-meta>
                      <template #title>
                        <a-space>
                          <span>{{ item.name }}</span>
                          <a-tag color="orange">热门</a-tag>
                        </a-space>
                      </template>
                      <template #description>
                        <a-space>
                          <span>{{ item.category_name }}</span>
                          <span>下载次数: {{ item.download_count }}</span>
                        </a-space>
                      </template>
                    </a-list-item-meta>
                    <template #actions>
                      <a-space>
                        <a-button type="text" size="small" @click="handleDownload(item)">下载</a-button>
                        <a-button type="text" size="small" @click="handlePreview(item)">预览</a-button>
                      </a-space>
                    </template>
                  </a-list-item>
                </template>
              </a-list>
            </a-tab-pane>
            
            <a-tab-pane key="month" title="本月热门">
              <a-list :data="monthHotDocs">
                <template #item="{ item }">
                  <a-list-item>
                    <a-list-item-meta>
                      <template #title>
                        <a-space>
                          <span>{{ item.name }}</span>
                          <a-tag color="blue">热门</a-tag>
                        </a-space>
                      </template>
                      <template #description>
                        <a-space>
                          <span>{{ item.category_name }}</span>
                          <span>下载次数: {{ item.download_count }}</span>
                        </a-space>
                      </template>
                    </a-list-item-meta>
                    <template #actions>
                      <a-space>
                        <a-button type="text" size="small" @click="handleDownload(item)">下载</a-button>
                        <a-button type="text" size="small" @click="handlePreview(item)">预览</a-button>
                      </a-space>
                    </template>
                  </a-list-item>
                </template>
              </a-list>
            </a-tab-pane>
          </a-tabs>
        </a-card>
        
        <a-card title="个性化推荐">
          <div class="recommend-section">
            <a-space direction="vertical" style="width: 100%;">
              <div v-for="doc in recommendedDocs" :key="doc.id" class="recommend-item">
                <a-space style="width: 100%; justify-content: space-between;">
                  <div>
                    <a-space>
                      <span class="doc-name">{{ doc.name }}</span>
                      <a-tag v-if="doc.reason" color="green">{{ doc.reason }}</a-tag>
                    </a-space>
                    <div class="doc-meta">
                      <span>{{ doc.category_name }}</span>
                      <span>·</span>
                      <span>{{ doc.upload_time }}</span>
                    </div>
                  </div>
                  <a-space>
                    <a-button type="text" size="small" @click="handleDownload(doc)">下载</a-button>
                    <a-button type="text" size="small" @click="handlePreview(doc)">预览</a-button>
                    <a-button type="text" size="small" @click="handleNotInterested(doc)">不感兴趣</a-button>
                  </a-space>
                </a-space>
              </div>
            </a-space>
          </div>
        </a-card>
      </a-col>
      
      <a-col :span="8">
        <a-card title="推荐统计" style="margin-bottom: 16px;">
          <a-statistic title="今日推荐" :value="stats.today" />
          <a-statistic title="本周推荐" :value="stats.week" style="margin-top: 16px;" />
          <a-statistic title="本月推荐" :value="stats.month" style="margin-top: 16px;" />
        </a-card>
        
        <a-card title="推荐设置">
          <a-form :model="recommendConfig" layout="vertical">
            <a-form-item label="推荐数量">
              <a-input-number v-model="recommendConfig.count" :min="1" :max="50" style="width: 100%;" />
            </a-form-item>
            <a-form-item label="推荐依据">
              <a-checkbox-group v-model="recommendConfig.basis">
                <a-checkbox value="download">下载历史</a-checkbox>
                <a-checkbox value="view">浏览历史</a-checkbox>
                <a-checkbox value="category">分类偏好</a-checkbox>
                <a-checkbox value="tag">标签偏好</a-checkbox>
              </a-checkbox-group>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="handleSaveConfig" block>保存设置</a-button>
            </a-form-item>
          </a-form>
        </a-card>
        
        <a-card title="最近浏览" style="margin-top: 16px;">
          <a-list :data="recentViews" size="small">
            <template #item="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    <a @click="handlePreview(item)">{{ item.name }}</a>
                  </template>
                  <template #description>
                    <span>{{ item.view_time }}</span>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
    </a-row>
    
    <!-- 预览弹窗 -->
    <a-modal v-model:visible="showPreviewModal" title="文档预览" width="90%" :footer="false">
      <div class="preview-container">
        <iframe :src="previewUrl" style="width: 100%; height: 600px; border: none;"></iframe>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'

const hotTab = ref('today')
const showPreviewModal = ref(false)
const previewUrl = ref('')

const todayHotDocs = ref<any[]>([])
const weekHotDocs = ref<any[]>([])
const monthHotDocs = ref<any[]>([])
const recommendedDocs = ref<any[]>([])
const recentViews = ref<any[]>([])

const stats = reactive({
  today: 12,
  week: 85,
  month: 320
})

const recommendConfig = reactive({
  count: 10,
  basis: ['download', 'view', 'category']
})

const fetchTodayHotDocs = async () => {
  await new Promise(resolve => setTimeout(resolve, 300))
  todayHotDocs.value = [
    { id: 1, name: '设备操作手册.pdf', category_name: '操作手册', download_count: 45, view_count: 120 },
    { id: 2, name: '安全管理制度.docx', category_name: '安全规范', download_count: 32, view_count: 98 },
    { id: 3, name: '生产流程优化方案.xlsx', category_name: '技术文档', download_count: 28, view_count: 76 },
    { id: 4, name: '员工培训计划.pptx', category_name: '培训资料', download_count: 25, view_count: 65 }
  ]
}

const fetchWeekHotDocs = async () => {
  await new Promise(resolve => setTimeout(resolve, 300))
  weekHotDocs.value = [
    { id: 1, name: '设备操作手册.pdf', category_name: '操作手册', download_count: 320 },
    { id: 2, name: '安全管理制度.docx', category_name: '安全规范', download_count: 245 },
    { id: 3, name: '生产流程优化方案.xlsx', category_name: '技术文档', download_count: 198 }
  ]
}

const fetchMonthHotDocs = async () => {
  await new Promise(resolve => setTimeout(resolve, 300))
  monthHotDocs.value = [
    { id: 1, name: '设备操作手册.pdf', category_name: '操作手册', download_count: 1250 },
    { id: 2, name: '安全管理制度.docx', category_name: '安全规范', download_count: 980 },
    { id: 3, name: '生产流程优化方案.xlsx', category_name: '技术文档', download_count: 756 }
  ]
}

const fetchRecommendedDocs = async () => {
  await new Promise(resolve => setTimeout(resolve, 300))
  recommendedDocs.value = [
    { id: 1, name: '设备维护保养手册.pdf', category_name: '操作手册', upload_time: '2024-01-10', reason: '基于您的浏览历史' },
    { id: 2, name: '应急预案.docx', category_name: '安全规范', upload_time: '2024-01-12', reason: '基于您的分类偏好' },
    { id: 3, name: '工艺优化报告.xlsx', category_name: '技术文档', upload_time: '2024-01-14', reason: '基于您的下载历史' },
    { id: 4, name: '新员工培训材料.pptx', category_name: '培训资料', upload_time: '2024-01-15', reason: '热门推荐' }
  ]
}

const fetchRecentViews = async () => {
  await new Promise(resolve => setTimeout(resolve, 300))
  recentViews.value = [
    { id: 1, name: '设备操作手册.pdf', view_time: '2024-01-15 10:30' },
    { id: 2, name: '安全管理制度.docx', view_time: '2024-01-14 15:20' },
    { id: 3, name: '生产流程优化方案.xlsx', view_time: '2024-01-13 09:15' }
  ]
}

const handleDownload = (item: any) => {
  Message.success(`开始下载: ${item.name}`)
}

const handlePreview = (item: any) => {
  previewUrl.value = `/api/documents/${item.id}/preview`
  showPreviewModal.value = true
}

const handleNotInterested = (item: any) => {
  Message.success(`已标记为不感兴趣: ${item.name}`)
  recommendedDocs.value = recommendedDocs.value.filter(d => d.id !== item.id)
}

const handleSaveConfig = () => {
  Message.success('推荐设置已保存')
}

onMounted(() => {
  fetchTodayHotDocs()
  fetchWeekHotDocs()
  fetchMonthHotDocs()
  fetchRecommendedDocs()
  fetchRecentViews()
})
</script>

<style scoped>
.recommend-section {
  min-height: 400px;
}

.recommend-item {
  padding: 12px;
  border-bottom: 1px solid #e5e6eb;
}

.recommend-item:last-child {
  border-bottom: none;
}

.doc-name {
  font-weight: 500;
  font-size: 14px;
}

.doc-meta {
  font-size: 12px;
  color: #86909c;
  margin-top: 4px;
}

.preview-container {
  width: 100%;
  height: 600px;
}
</style>
