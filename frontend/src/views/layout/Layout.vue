<template>
  <el-container style="min-height: 100vh; background: #f5f7fa">
    <!-- 顶部导航 -->
    <header style="
      position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
      height: 60px; background: rgba(255,255,255,0.92);
      backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(0,0,0,0.06);
      display: flex; align-items: center;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      transition: box-shadow 0.3s;
    ">
      <!-- Logo -->
      <div style="
        width: 200px; height: 60px; display: flex; align-items: center;
        justify-content: center; gap: 10px; flex-shrink: 0;
        border-right: 1px solid rgba(0,0,0,0.04);
      ">
        <div style="
          width: 32px; height: 32px; border-radius: 8px;
          background: linear-gradient(135deg, #409EFF, #337ecc);
          display: flex; align-items: center; justify-content: center;
        ">
          <el-icon :size="18" color="#fff"><Monitor /></el-icon>
        </div>
        <span style="font-size: 15px; font-weight: 700; color: #1a1a2e; letter-spacing: 0.5px">计量仪器系统</span>
      </div>

      <!-- 导航菜单 -->
      <el-menu
        :default-active="activeMenu"
        mode="horizontal"
        router
        :ellipsis="false"
        style="flex: 1; border-bottom: none; height: 60px; background: transparent; margin-left: 8px"
      >
        <el-menu-item v-if="userStore.canAccessModule('dashboard')" index="/dashboard" style="border-bottom: none; height: 60px; line-height: 60px; margin: 0 2px; border-radius: 8px; transition: all 0.2s">
          <el-icon style="margin-right: 6px; font-size: 16px"><DataBoard /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.canAccessModule('instruments')" index="/instruments" style="border-bottom: none; height: 60px; line-height: 60px; margin: 0 2px; border-radius: 8px; transition: all 0.2s">
          <el-icon style="margin-right: 6px; font-size: 16px"><List /></el-icon>
          <span>仪器台账</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.canAccessModule('calibration')" index="/calibration" style="border-bottom: none; height: 60px; line-height: 60px; margin: 0 2px; border-radius: 8px; transition: all 0.2s">
          <el-icon style="margin-right: 6px; font-size: 16px"><Calendar /></el-icon>
          <span>检定计划</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.canAccessModule('contracts')" index="/contract" style="border-bottom: none; height: 60px; line-height: 60px; margin: 0 2px; border-radius: 8px; transition: all 0.2s">
          <el-icon style="margin-right: 6px; font-size: 16px"><Document /></el-icon>
          <span>合同管理</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.canAccessModule('supervision')" index="/supervision" style="border-bottom: none; height: 60px; line-height: 60px; margin: 0 2px; border-radius: 8px; transition: all 0.2s">
          <el-icon style="margin-right: 6px; font-size: 16px"><WarningFilled /></el-icon>
          <span>监督管理</span>
        </el-menu-item>
        <el-sub-menu v-if="userStore.isAdmin" index="system" style="border-bottom: none; height: 60px; line-height: 60px; margin: 0 2px">
          <template #title>
            <el-icon style="margin-right: 6px; font-size: 16px"><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>

      <!-- 右侧用户 -->
      <div style="padding: 0 20px; flex-shrink: 0; border-left: 1px solid rgba(0,0,0,0.04); height: 60px; display: flex; align-items: center">
        <el-dropdown trigger="click" @command="handleCommand">
          <span style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 6px 12px; border-radius: 8px; transition: background 0.2s" class="user-dropdown-trigger">
            <el-avatar :size="30" style="background: linear-gradient(135deg, #409EFF, #36cfc9); flex-shrink: 0">
              {{ userStore.userName?.charAt(0) || '管' }}
            </el-avatar>
            <span style="font-size: 14px; color: #303133; font-weight: 500">{{ userStore.userName || '管理员' }}</span>
            <el-icon style="font-size: 12px; color: #909399"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon style="margin-right: 6px"><UserFilled /></el-icon>个人中心
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon style="margin-right: 6px"><SwitchButton /></el-icon>退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- 深色模式切换 -->
      <div style="padding: 0 12px 0 0; flex-shrink: 0; display: flex; align-items: center">
        <el-tooltip :content="isDark ? '切换亮色模式' : '切换深色模式'" placement="bottom">
          <el-button :icon="isDark ? Sunny : Moon" circle size="small"
            style="border: none; background: transparent; font-size: 18px; color: #909399"
            @click="toggleTheme"
          />
        </el-tooltip>
      </div>
    </header>

    <!-- 主内容区（带顶部 padding 避开固定导航栏） -->
    <el-main style="padding: 80px 24px 24px; background: #f5f7fa; min-height: 100vh">
      <!-- 路由页面过渡动画 -->
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../store/user'
import {
  Monitor, DataBoard, List, Calendar, Document, WarningFilled,
  Setting, User, ArrowDown, UserFilled, SwitchButton, Sunny, Moon
} from '@element-plus/icons-vue'
import { useTheme } from '../../store/theme'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const { isDark, toggleTheme } = useTheme()

const activeMenu = computed(() => route.path)

function handleCommand(command) {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
/* 菜单项悬停效果 */
.el-menu--horizontal .el-menu-item:not(.is-active):hover {
  background: rgba(64, 158, 255, 0.06) !important;
}

.el-menu--horizontal .el-menu-item.is-active {
  color: #409EFF !important;
  font-weight: 600;
  background: rgba(64, 158, 255, 0.08) !important;
}

.el-menu--horizontal .el-sub-menu__title:hover {
  background: rgba(64, 158, 255, 0.06) !important;
}

/* 用户下拉悬停 */
.user-dropdown-trigger:hover {
  background: rgba(0, 0, 0, 0.04);
}

/* 页面过渡动画 */
.page-fade-enter-active {
  transition: all 0.25s ease-out;
}
.page-fade-leave-active {
  transition: all 0.15s ease-in;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* 深色模式下子菜单适配 */
.el-menu--horizontal .el-sub-menu .el-menu {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
  border: 1px solid rgba(0,0,0,0.04);
  padding: 4px;
}
.el-menu--horizontal .el-sub-menu .el-menu .el-menu-item {
  border-radius: 6px;
  margin: 2px 0;
}
.el-menu--horizontal .el-sub-menu .el-menu .el-menu-item:hover {
  background: rgba(64, 158, 255, 0.06);
}
.el-menu--horizontal .el-sub-menu .el-menu .el-menu-item.is-active {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}
</style>
