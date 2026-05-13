import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, getUserInfoApi, logoutApi } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => userInfo.value?.name || '')

  // 操作
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
    await fetchUserInfo()
    return res
  }

  async function fetchUserInfo() {
    const res = await getUserInfoApi()
    userInfo.value = res.data
  }

  async function logout() {
    try {
      await logoutApi()
    } finally {
      removeToken()
      userInfo.value = null
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    userName,
    login,
    logout,
    setToken,
    removeToken,
    fetchUserInfo,
  }
})
