import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, getUserInfoApi, logoutApi } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => userInfo.value?.name || '')
  const modulePermissions = computed(() => userInfo.value?.module_permissions ?? null)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

  function canAccessModule(moduleName) {
    if (!isLoggedIn.value) return false
    const perms = modulePermissions.value
    if (perms === null || perms === undefined) return true
    return Array.isArray(perms) && perms.includes(moduleName)
  }

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function removeToken() {
    token.value = ''
    localStorage.removeItem('token')
  }

  async function login(credentials) {
    const res = await loginApi(credentials)
    setToken(res.data.access_token)
    userInfo.value = res.data.user
    return res
  }

  async function fetchUserInfo() {
    const res = await getUserInfoApi()
    userInfo.value = res.data.data || res.data
  }

  async function logout() {
    try {
      await logoutApi()
    } finally {
      removeToken()
      userInfo.value = null
    }
  }

  return { token, userInfo, isLoggedIn, userName, modulePermissions, isAdmin, canAccessModule, login, logout, setToken, removeToken, fetchUserInfo }
})
