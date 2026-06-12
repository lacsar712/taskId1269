import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api'
import router from '@/router'

interface User {
  id: number
  username: string
  real_name: string | null
  email: string | null
  phone: string | null
  department: string | null
  position: string | null
  role_id: number | null
  role_name: string | null
  is_active: boolean
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)

  const login = async (username: string, password: string) => {
    const res: any = await authApi.login({ username, password })
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    await fetchUser()
    router.push('/')
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (e) {
      // ignore
    }
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  const fetchUser = async () => {
    if (!token.value) return
    try {
      const res: any = await authApi.getCurrentUser()
      user.value = res
    } catch (e) {
      logout()
    }
  }

  return {
    token,
    user,
    login,
    logout,
    fetchUser
  }
})
