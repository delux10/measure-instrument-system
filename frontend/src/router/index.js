import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/',
    component: () => import('../views/layout/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表盘' },
      },
      {
        path: 'instruments',
        name: 'InstrumentList',
        component: () => import('../views/instruments/InstrumentList.vue'),
        meta: { title: '仪器台账' },
      },
      {
        path: 'calibration',
        name: 'CalibrationPlan',
        component: () => import('../views/calibration/CalibrationPlan.vue'),
        meta: { title: '检定计划' },
      },
      {
        path: 'contract',
        name: 'ContractList',
        component: () => import('../views/contract/ContractList.vue'),
        meta: { title: '合同管理' },
      },
      {
        path: 'supervision',
        name: 'SupervisionList',
        component: () => import('../views/supervision/SupervisionList.vue'),
        meta: { title: '监督管理' },
      },
      {
        path: 'system/users',
        name: 'UserManagement',
        component: () => import('../views/system/UserManagement.vue'),
        meta: { title: '用户管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：未登录跳转到登录页
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
