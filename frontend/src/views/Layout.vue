<template>
  <a-layout class="layout">
    <!-- 顶部导航 -->
    <a-layout-header class="layout-header">
      <div class="logo">
        <img src="/favicon.svg" alt="logo" />
        <span>污水处理厂智能管理系统</span>
      </div>
      <div class="header-right">
        <a-space :size="16">
          <a-dropdown trigger="click">
            <a-space style="cursor: pointer; color: #fff;">
              <a-avatar :size="32" style="background-color: #14C9C9;">
                {{ userStore.user?.real_name?.charAt(0) || userStore.user?.username?.charAt(0) || 'U' }}
              </a-avatar>
              <span>{{ userStore.user?.real_name || userStore.user?.username || '用户' }}</span>
              <icon-down />
            </a-space>
            <template #content>
              <a-doption>
                <template #icon><icon-user /></template>
                个人信息
              </a-doption>
              <a-doption>
                <template #icon><icon-settings /></template>
                账号设置
              </a-doption>
              <a-divider style="margin: 4px 0;" />
              <a-doption @click="handleLogout">
                <template #icon><icon-export /></template>
                退出登录
              </a-doption>
            </template>
          </a-dropdown>
        </a-space>
      </div>
    </a-layout-header>
    
    <a-layout>
      <!-- 侧边栏菜单 -->
      <a-layout-sider
        class="layout-sider"
        :width="220"
        :collapsed-width="64"
        collapsible
        breakpoint="xl"
        v-model:collapsed="collapsed"
      >
        <a-menu
          :selected-keys="selectedKeys"
          :open-keys="openKeys"
          :auto-open-selected="true"
          @menu-item-click="handleMenuClick"
          @sub-menu-click="handleSubMenuClick"
        >
          <a-menu-item key="dashboard">
            <template #icon><icon-dashboard /></template>
            首页
          </a-menu-item>
          
          <a-sub-menu key="production">
            <template #icon><icon-settings /></template>
            <template #title>生产管理</template>
            <a-menu-item key="production/monitor">工艺运行监控</a-menu-item>
            <a-menu-item key="production/plan">生产计划调度</a-menu-item>
            <a-menu-item key="production/log">生产日志管理</a-menu-item>
            <a-menu-item key="production/abnormal">异常处理</a-menu-item>
            <a-menu-item key="production/optimization">工艺优化</a-menu-item>
            <a-menu-item key="production/alarm">异常告警列表</a-menu-item>
          </a-sub-menu>
          
          <a-sub-menu key="safety">
            <template #icon><icon-safe /></template>
            <template #title>安全管理</template>
            <a-menu-item key="safety/inspection">安全巡检</a-menu-item>
            <a-menu-item key="safety/risk">风险管控</a-menu-item>
            <a-menu-item key="safety/emergency">应急管理</a-menu-item>
            <a-menu-item key="safety/training">安全培训</a-menu-item>
            <a-menu-item key="safety/permit">作业许可</a-menu-item>
          </a-sub-menu>
          
          <a-sub-menu key="equipment">
            <template #icon><icon-computer /></template>
            <template #title>设备管理</template>
            <a-menu-item key="equipment/ledger">设备台账</a-menu-item>
            <a-menu-item key="equipment/monitor">运行监控</a-menu-item>
            <a-menu-item key="equipment/maintenance">维护保养</a-menu-item>
            <a-menu-item key="equipment/fault">故障管理</a-menu-item>
            <a-menu-item key="equipment/spare">备件管理</a-menu-item>
            <a-menu-item key="equipment/fault-alarm">故障告警</a-menu-item>
            <a-menu-item key="equipment/analysis">设备分析</a-menu-item>
          </a-sub-menu>
          
          <a-sub-menu key="laboratory">
            <template #icon><icon-experiment /></template>
            <template #title>化验管理</template>
            <a-menu-item key="laboratory/sample">样品管理</a-menu-item>
            <a-menu-item key="laboratory/task">检测任务</a-menu-item>
            <a-menu-item key="laboratory/data">数据管理</a-menu-item>
            <a-menu-item key="laboratory/report">报告管理</a-menu-item>
            <a-menu-item key="laboratory/qc">质控管理</a-menu-item>
            <a-menu-item key="laboratory/standard">标准库</a-menu-item>
          </a-sub-menu>
          
          <a-sub-menu key="report">
            <template #icon><icon-file /></template>
            <template #title>生产报表</template>
            <a-menu-item key="report/regular">常规报表</a-menu-item>
            <a-menu-item key="report/custom">自定义报表</a-menu-item>
            <a-menu-item key="report/visualization">数据可视化</a-menu-item>
            <a-menu-item key="report/trace">数据溯源</a-menu-item>
            <a-menu-item key="report/prediction">趋势预测</a-menu-item>
          </a-sub-menu>
          
          <a-sub-menu key="energy">
            <template #icon><icon-thunderbolt /></template>
            <template #title>能耗管理</template>
            <a-menu-item key="energy/realtime">能耗实时监测</a-menu-item>
            <a-menu-item key="energy/analysis">能耗多维度分析</a-menu-item>
            <a-menu-item key="energy/saving">节能策略管理</a-menu-item>
            <a-menu-item key="energy/cost">能耗成本核算</a-menu-item>
            <a-menu-item key="energy/report">能耗报表</a-menu-item>
          </a-sub-menu>
          
          <a-sub-menu key="document">
            <template #icon><icon-folder /></template>
            <template #title>资料管理</template>
            <a-menu-item key="document/category">文档分类管理</a-menu-item>
            <a-menu-item key="document/upload">文档上传管理</a-menu-item>
            <a-menu-item key="document/search">文档检索下载</a-menu-item>
            <a-menu-item key="document/archive">归档备份</a-menu-item>
            <a-menu-item key="document/recommend">常用文档推荐</a-menu-item>
          </a-sub-menu>
          
          <a-sub-menu key="material">
            <template #icon><icon-storage /></template>
            <template #title>物资管理</template>
            <a-menu-item key="material/ledger">物资台账</a-menu-item>
            <a-menu-item key="material/inbound">入库管理</a-menu-item>
            <a-menu-item key="material/outbound">出库管理</a-menu-item>
            <a-menu-item key="material/inventory">库存管理</a-menu-item>
            <a-menu-item key="material/purchase">采购管理</a-menu-item>
            <a-menu-item key="material/supplier">供应商管理</a-menu-item>
          </a-sub-menu>
          
          <a-sub-menu key="performance">
            <template #icon><icon-trophy /></template>
            <template #title>绩效管理</template>
            <a-menu-item key="performance/indicator">考核指标体系</a-menu-item>
            <a-menu-item key="performance/data">绩效数据管理</a-menu-item>
            <a-menu-item key="performance/analysis">绩效统计分析</a-menu-item>
            <a-menu-item key="performance/application">绩效应用</a-menu-item>
          </a-sub-menu>
          
          <a-sub-menu key="system">
            <template #icon><icon-settings /></template>
            <template #title>系统设置</template>
            <a-menu-item key="system/project">项目管理</a-menu-item>
            <a-menu-item key="system/user">用户管理</a-menu-item>
            <a-menu-item key="system/role">角色权限管理</a-menu-item>
            <a-menu-item key="system/basic">基础数据管理</a-menu-item>
            <a-menu-item key="system/params">系统参数设置</a-menu-item>
            <a-menu-item key="system/log">日志管理</a-menu-item>
            <a-menu-item key="system/interface">接口配置</a-menu-item>
            <a-menu-item key="system/maintenance">系统维护</a-menu-item>
          </a-sub-menu>
        </a-menu>
      </a-layout-sider>
      
      <!-- 主内容区 -->
      <a-layout-content class="layout-content">
        <a-breadcrumb class="breadcrumb-container">
          <a-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
            {{ item.title }}
          </a-breadcrumb-item>
        </a-breadcrumb>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const collapsed = ref(false)
const selectedKeys = ref<string[]>(['dashboard'])
const openKeys = ref<string[]>([])

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(r => r.meta?.title)
  return matched.map(r => ({
    path: r.path,
    title: r.meta?.title as string
  }))
})

const handleMenuClick = (key: string) => {
  router.push('/' + key)
}

const handleSubMenuClick = (key: string) => {
  const index = openKeys.value.indexOf(key)
  if (index > -1) {
    openKeys.value.splice(index, 1)
  } else {
    openKeys.value.push(key)
  }
}

const handleLogout = () => {
  userStore.logout()
}

watch(
  () => route.path,
  (path) => {
    const key = path.replace(/^\//, '')
    selectedKeys.value = [key]
    const parts = key.split('/')
    if (parts.length > 1) {
      openKeys.value = [parts[0]]
    }
  },
  { immediate: true }
)

onMounted(() => {
  userStore.fetchUser()
})
</script>

<style scoped>
.layout {
  height: 100vh;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: linear-gradient(135deg, #165DFF 0%, #0E42D2 100%);
  height: 56px;
}

.logo {
  display: flex;
  align-items: center;
  color: #fff;
}

.logo img {
  width: 32px;
  height: 32px;
  margin-right: 12px;
}

.logo span {
  font-size: 18px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.layout-sider {
  background: #fff;
  border-right: 1px solid #e5e6eb;
}

.layout-content {
  padding: 16px;
  overflow: auto;
  background: #f0f2f5;
}

.breadcrumb-container {
  margin-bottom: 12px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

:deep(.arco-layout-sider-children) {
  overflow-y: auto;
}

:deep(.arco-menu) {
  width: 100%;
}

:deep(.arco-menu-selected) {
  background: linear-gradient(90deg, #e8f3ff 0%, #f0f5ff 100%) !important;
}

:deep(.arco-menu-selected .arco-menu-item-inner) {
  color: #165DFF;
}
</style>
