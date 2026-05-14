<template>
  <div style="max-width: 1200px; margin: 0 auto">
    <div style="margin-bottom: 24px">
      <h2 style="margin: 0 0 4px; font-size: 22px; font-weight: 700; color: #1a1a2e">
        👋 欢迎回来，{{ userStore.userName }}
      </h2>
      <p style="margin: 0; color: #909399; font-size: 14px">{{ currentDate }} · 系统运行正常</p>
    </div>

    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px">
      <div v-for="(card, idx) in statsCards" :key="idx"
        style="background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.04); cursor: default; transition: all 0.25s ease;"
        class="stat-card dark-card"
      >
        <div style="display: flex; align-items: flex-start; justify-content: space-between">
          <div>
            <div style="font-size: 28px; font-weight: 700; color: #1a1a2e; line-height: 1.2">{{ card.value }}</div>
            <div style="font-size: 13px; color: #909399; margin-top: 6px">{{ card.label }}</div>
          </div>
          <div :style="{
            width: '44px', height: '44px', borderRadius: '10px',
            background: card.bg, display: 'flex', alignItems: 'center',
            justifyContent: 'center', flexShrink: '0'
          }">
            <el-icon :size="22" :color="card.color">
              <component :is="card.icon" />
            </el-icon>
          </div>
        </div>
        <div style="margin-top: 12px; font-size: 12px; color: #c0c4cc">{{ card.subtext }}</div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px">
      <div style="background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.04);" class="dark-card">
        <h3 style="margin: 0 0 16px; font-size: 15px; font-weight: 600; color: #303133">快捷操作</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px">
          <div v-for="(action, idx) in quickActions" :key="idx"
            style="display: flex; align-items: center; gap: 12px; padding: 14px; border-radius: 10px; cursor: pointer; transition: all 0.2s; background: #f5f7fa;"
            class="quick-action-item dark-action"
            @click="action.handler"
          >
            <div :style="{
              width: '36px', height: '36px', borderRadius: '8px',
              background: action.bg, display: 'flex', alignItems: 'center',
              justifyContent: 'center', flexShrink: '0'
            }">
              <el-icon :size="18" :color="action.color"><component :is="action.icon" /></el-icon>
            </div>
            <div>
              <div style="font-size: 14px; font-weight: 500; color: #303133">{{ action.name }}</div>
              <div style="font-size: 12px; color: #909399">{{ action.desc }}</div>
            </div>
          </div>
        </div>
      </div>

      <div style="background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.04);" class="dark-card">
        <h3 style="margin: 0 0 16px; font-size: 15px; font-weight: 600; color: #303133">最近动态</h3>
        <div v-if="recentActivities.length === 0" style="text-align: center; padding: 32px 0; color: #c0c4cc">
          <el-icon :size="40" style="margin-bottom: 8px"><Document /></el-icon>
          <p style="margin: 0; font-size: 13px">暂无动态</p>
        </div>
        <div v-for="(act, idx) in recentActivities" :key="idx" style="display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid rgba(0,0,0,0.04);">
          <div :style="{ width: '8px', height: '8px', borderRadius: '50%', background: act.color, flexShrink: '0' }"></div>
          <div style="flex: 1">
            <div style="font-size: 13px; color: #303133">{{ act.text }}</div>
            <div style="font-size: 12px; color: #c0c4cc">{{ act.time }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import {
  DataBoard, List, Calendar, Document, WarningFilled,
  Plus, Edit, Setting
} from '@element-plus/icons-vue'
import request from '../api/index'

const router = useRouter()
const userStore = useUserStore()

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
})

const statsCards = ref([])
const recentActivities = ref([])

async function fetchDashboardData() {
  try {
    const now = new Date()

    // 获取仪器列表 → 总数 & 过期数
    const instRes = await request({ url: '/instruments/', method: 'get', params: { page_size: 9999 } })
    const instruments = Array.isArray(instRes.data) ? instRes.data :
                        instRes.data?.results || instRes.data?.items || []
    const totalInstruments = instruments.length
    const overdueCount = instruments.filter(i => {
      if (!i.next_cal_date) return false
      return new Date(i.next_cal_date) < now
    }).length

    // 获取到期预警 (30天内)
    const expiringRes = await request({ url: '/instruments/expiring', method: 'get', params: { days: 30 } })
    const expiring = Array.isArray(expiringRes.data) ? expiringRes.data : []

    // 获取检定记录 → 待检定数
    const calRes = await request({ url: '/calibration-records/', method: 'get', params: { page_size: 9999 } })
    const records = Array.isArray(calRes.data) ? calRes.data :
                    calRes.data?.results || calRes.data?.items || []
    const pendingCal = records.filter(r => !r.actual_date).length

    statsCards.value = [
      { label: '仪器总数', value: String(totalInstruments), icon: DataBoard,
        bg: 'rgba(64,158,255,0.1)', color: '#409EFF', subtext: '全厂设备' },
      { label: '待检定', value: String(pendingCal), icon: Calendar,
        bg: 'rgba(230,162,60,0.1)', color: '#E6A23C', subtext: '计划待执行' },
      { label: '即将到期', value: String(expiring.length), icon: WarningFilled,
        bg: 'rgba(245,108,108,0.1)', color: '#F56C6C', subtext: '30天内到期' },
      { label: '已过期', value: String(overdueCount), icon: List,
        bg: 'rgba(144,147,153,0.1)', color: '#909399', subtext: '请及时处理' },
    ]

    // 最近动态：取最近5条检定记录
    const recent = records.slice(-5).reverse()
    recentActivities.value = recent.map(r => ({
      text: r.instrument?.name
        ? `仪器「${r.instrument.name}」${r.actual_date ? '完成检定' : '计划检定'}`
        : `检定记录 #${r.id} ${r.actual_date ? '已完成' : '待执行'}`,
      time: r.plan_date || r.created_at || '',
      color: r.actual_date ? '#67C23A' : '#E6A23C',
    }))
  } catch (e) {
    // 如果后端未启动，使用空数据
    statsCards.value = [
      { label: '仪器总数', value: '0', icon: DataBoard, bg: 'rgba(64,158,255,0.1)', color: '#409EFF', subtext: '全厂设备' },
      { label: '待检定', value: '0', icon: Calendar, bg: 'rgba(230,162,60,0.1)', color: '#E6A23C', subtext: '计划待执行' },
      { label: '即将到期', value: '0', icon: WarningFilled, bg: 'rgba(245,108,108,0.1)', color: '#F56C6C', subtext: '30天内到期' },
      { label: '已过期', value: '0', icon: List, bg: 'rgba(144,147,153,0.1)', color: '#909399', subtext: '请及时处理' },
    ]
    recentActivities.value = []
  }
}

const quickActions = [
  { name: '新增仪器', desc: '录入新设备信息', icon: Plus, bg: 'rgba(64,158,255,0.1)', color: '#409EFF', handler: () => router.push('/instruments') },
  { name: '检定记录', desc: '登记检定结果', icon: Edit, bg: 'rgba(103,194,58,0.1)', color: '#67C23A', handler: () => router.push('/calibration') },
  { name: '合同对账', desc: '比对合同与执行', icon: Document, bg: 'rgba(230,162,60,0.1)', color: '#E6A23C', handler: () => router.push('/contract') },
  { name: '系统设置', desc: '用户与权限管理', icon: Setting, bg: 'rgba(144,147,153,0.1)', color: '#909399', handler: () => router.push('/system/users') },
]

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.06) !important;
}
.quick-action-item:hover {
  background: rgba(64,158,255,0.06) !important;
  transform: translateX(2px);
}
</style>
