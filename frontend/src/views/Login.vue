<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo">
        <img src="/favicon.svg" alt="logo" />
        <h1>污水处理厂智能管理系统</h1>
        <p>Water Treatment Plant Intelligent Management System</p>
      </div>
      <a-form :model="form" @submit="handleLogin" layout="vertical">
        <a-form-item field="username" label="用户名">
          <a-input v-model="form.username" placeholder="请输入用户名" size="large">
            <template #prefix>
              <icon-user />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item field="password" label="密码">
          <a-input-password v-model="form.password" placeholder="请输入密码" size="large">
            <template #prefix>
              <icon-lock />
            </template>
          </a-input-password>
        </a-form-item>
        <a-form-item>
          <a-checkbox v-model="form.remember">记住密码</a-checkbox>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading" long size="large">
            登 录
          </a-button>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  username: 'admin',
  password: '123456',
  remember: true
})

const handleLogin = async () => {
  if (!form.username || !form.password) {
    Message.warning('请输入用户名和密码')
    return
  }
  
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    Message.success('登录成功')
  } catch (error: any) {
    Message.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #165DFF 0%, #0E42D2 50%, #722ED1 100%);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.login-box {
  width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 48px 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.logo {
  text-align: center;
  margin-bottom: 36px;
}

.logo img {
  width: 72px;
  height: 72px;
}

.logo h1 {
  font-size: 22px;
  color: #1d2129;
  margin-top: 16px;
  font-weight: 600;
}

.logo p {
  font-size: 13px;
  color: #86909c;
  margin-top: 8px;
}

.login-tips {
  margin-top: 16px;
}

:deep(.arco-form-item-label) {
  font-weight: 500;
}

:deep(.arco-btn-primary) {
  background: linear-gradient(135deg, #165DFF 0%, #0E42D2 100%);
}

:deep(.arco-btn-primary:hover) {
  background: linear-gradient(135deg, #4080FF 0%, #165DFF 100%);
}
</style>
