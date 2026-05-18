import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { title: '登录' } },
  {
    path: '/', component: () => import('../views/layout/Layout.vue'), redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '仪表盘', module: 'dashboard' } },
      { path: 'instruments', name: 'Instruments', component: () => import('../views/instruments/InstrumentList.vue'), meta: { title: '仪器台账', module: 'instruments' } },
      { path: 'calibration', name: 'Calibration', component: () => import('../views/calibration/CalibrationList.vue'), meta: { title: '检定管理', module: 'calibration' } },
      { path: 'contract', name: 'Contracts', component: () => import('../views/contract/ContractList.vue'), meta: { title: '合同管理', module: 'contracts' } },
      { path: 'supervision', name: 'Supervision', component: () => import('../views/supervision/SupervisionList.vue'), meta: { title: '监督管理', module: 'supervision' } },
      { path: 'system/users', name: 'Users', component: () => import('../views/system/UserManagement.vue'), meta: { title: '用户管理', module: 'user_management' } },
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) { next('/login'); return }
  if (to.meta.module) {
    const userStore = useUserStore()
    if (userStore.userInfo && !userStore.canAccessModule(to.meta.module)) { next('/dashboard'); return }
  }
  next()
})

export default router
