<template>
  <div style="max-width: 1200px; margin: 0 auto">
    <div style="margin-bottom: 24px">
      <h2 style="margin: 0 0 4px; font-size: 22px; font-weight: 700; color: #1a1a2e">
        Welcome, {{ userStore.userName }}
      </h2>
      <p style="margin: 0; color: #909399; font-size: 14px">{{ currentDate }}</p>
    </div>

    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px">
      <div v-for="(card, idx) in statsCards" :key="idx"
        style="background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.04); cursor: default; transition: all 0.25s ease;"
        class="stat-card"
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
      <div style="background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.04);">
        <h3 style="margin: 0 0 16px; font-size: 15px; font-weight: 600; color: #303133">Quick Actions</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px">
          <div v-for="(action, idx) in quickActions" :key="idx"
            style="display: flex; align-items: center; gap: 12px; padding: 14px; border-radius: 10px; cursor: pointer; transition: all 0.2s; background: #f5f7fa;"
            class="quick-action-item"
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

      <div style="background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.04);">
        <h3 style="margin: 0 0 16px; font-size: 15px; font-weight: 600; color: #303133">Recent Activity</h3>
        <div v-if="recentActivities.length === 0" style="text-align: center; padding: 32px 0; color: #c0c4cc">
          <el-icon :size="40" style="margin-bottom: 8px"><Document /></el-icon>
          <p style="margin: 0; font-size: 13px">No recent activity</p>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { DataBoard, List, Calendar, Document, WarningFilled, Plus, Edit, Setting } from '@element-plus/icons-vue'
import request from '../api/index'

const router = useRouter()
const userStore = useUserStore()

const currentDate = new Date().toLocaleDateString('en-US', {
  year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
})

const statsCards = ref([])
const recentActivities = ref([])

async function fetchDashboardData() {
  try {
    const [instRes, calRes, expiringRes] = await Promise.all([
      request({ url: '/instruments/', method: 'get', params: { page_size: 9999 } }),
      request({ url: '/calibration/records', method: 'get', params: { page_size: 9999 } }),
      request({ url: '/calibration/expiring', method: 'get', params: { days: 30 } })
    ])

    const instruments = instRes.data?.data || []
    const records = calRes.data?.data || []
    const expiring = expiringRes.data?.data || []

    const totalInstruments = instruments.length
    const pendingCal = records.filter(r => !r.actual_date).length
    const now = new Date()
    const overdueCount = records.filter(r => r.plan_date && !r.actual_date && new Date(r.plan_date) < now).length

    statsCards.value = [
      { label: 'Instruments', value: String(totalInstruments), icon: DataBoard, bg: 'rgba(64,158,255,0.1)', color: '#409EFF', subtext: 'Total instruments' },
      { label: 'Pending Cal', value: String(pendingCal), icon: Calendar, bg: 'rgba(230,162,60,0.1)', color: '#E6A23C', subtext: 'Awaiting calibration' },
      { label: 'Expiring Soon', value: String(expiring.length), icon: WarningFilled, bg: 'rgba(245,108,108,0.1)', color: '#F56C6C', subtext: 'Within 30 days' },
      { label: 'Overdue', value: String(overdueCount), icon: List, bg: 'rgba(144,147,153,0.1)', color: '#909399', subtext: 'Past due date' },
    ]

    const recent = records.slice(-5).reverse()
    recentActivities.value = recent.map(r => ({
      text: `Record #${r.id} ${r.actual_date ? 'completed' : 'scheduled'}`,
      time: r.plan_date || r.created_at || '',
      color: r.actual_date ? '#67C23A' : '#E6A23C',
    }))
  } catch {
    statsCards.value = [
      { label: 'Instruments', value: '0', icon: DataBoard, bg: 'rgba(64,158,255,0.1)', color: '#409EFF', subtext: 'Total instruments' },
      { label: 'Pending Cal', value: '0', icon: Calendar, bg: 'rgba(230,162,60,0.1)', color: '#E6A23C', subtext: 'Awaiting calibration' },
      { label: 'Expiring', value: '0', icon: WarningFilled, bg: 'rgba(245,108,108,0.1)', color: '#F56C6C', subtext: 'Within 30 days' },
      { label: 'Overdue', value: '0', icon: List, bg: 'rgba(144,147,153,0.1)', color: '#909399', subtext: 'Past due date' },
    ]
    recentActivities.value = []
  }
}

const quickActions = computed(() => {
  const actions = []
  if (userStore.canAccessModule('instruments')) {
    actions.push({ name: 'Add Instrument', desc: 'Register new device', icon: Plus, bg: 'rgba(64,158,255,0.1)', color: '#409EFF', handler: () => router.push('/instruments') })
  }
  if (userStore.canAccessModule('calibration')) {
    actions.push({ name: 'Calibration', desc: 'Record calibration results', icon: Edit, bg: 'rgba(103,194,58,0.1)', color: '#67C23A', handler: () => router.push('/calibration') })
  }
  if (userStore.canAccessModule('contracts')) {
    actions.push({ name: 'Contracts', desc: 'Contract management', icon: Document, bg: 'rgba(230,162,60,0.1)', color: '#E6A23C', handler: () => router.push('/contract') })
  }
  if (userStore.isAdmin) {
    actions.push({ name: 'System', desc: 'User & permission mgmt', icon: Setting, bg: 'rgba(144,147,153,0.1)', color: '#909399', handler: () => router.push('/system/users') })
  }
  return actions
})

onMounted(() => { fetchDashboardData() })
</script>

<style scoped>
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.06) !important; }
.quick-action-item:hover { background: rgba(64,158,255,0.06) !important; transform: translateX(2px); }
</style>
