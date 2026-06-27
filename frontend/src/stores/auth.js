import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  // --- State ---
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // --- Getters ---
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const departmentId = computed(() => user.value?.department_id || null)

  // --- Actions ---
  async function login(username, password) {
    const res = await api.post('/auth/login', { username, password })
    const { access_token, user: userData } = res.data
    token.value = access_token
    user.value = userData
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))
    return userData
  }

  async function register(username, password, email, adminKey = null, departmentId = null) {
    const payload = { username, password, email }
    if (adminKey) payload.admin_key = adminKey
    if (departmentId) payload.department_id = departmentId
    const res = await api.post('/auth/register', payload)
    const { access_token, user: userData } = res.data
    token.value = access_token
    user.value = userData
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))
    return userData
  }

  async function refreshToken() {
    try {
      const res = await api.post('/auth/refresh')
      const { access_token, user: userData } = res.data
      token.value = access_token
      user.value = userData
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function restoreSession() {
    // Token 已在构造函数中从 localStorage 加载
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    departmentId,
    login,
    register,
    refreshToken,
    logout,
    restoreSession,
  }
})
