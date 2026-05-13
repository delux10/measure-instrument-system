<template>
  <div>
    <el-page-header title="仪表盘" style="margin-bottom: 20px">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">工作台</span>
      </template>
    </el-page-header>

    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center; padding: 10px 0">
            <el-icon :size="40" color="#409EFF"><List /></el-icon>
            <h3 style="margin: 10px 0 5px">仪器总数</h3>
            <p style="font-size: 28px; font-weight: bold; color: #303133; margin: 0">—</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center; padding: 10px 0">
            <el-icon :size="40" color="#67C23A"><Calendar /></el-icon>
            <h3 style="margin: 10px 0 5px">待检定</h3>
            <p style="font-size: 28px; font-weight: bold; color: #303133; margin: 0">—</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center; padding: 10px 0">
            <el-icon :size="40" color="#E6A23C"><WarningFilled /></el-icon>
            <h3 style="margin: 10px 0 5px">即将到期</h3>
            <p style="font-size: 28px; font-weight: bold; color: #303133; margin: 0">—</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center; padding: 10px 0">
            <el-icon :size="40" color="#F56C6C"><CircleCloseFilled /></el-icon>
            <h3 style="margin: 10px 0 5px">已过期</h3>
            <p style="font-size: 28px; font-weight: bold; color: #303133; margin: 0">—</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>最近动态</span>
      </template>
      <el-empty description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup>
import { List, Calendar, WarningFilled, CircleCloseFilled } from '@element-plus/icons-vue'
</script>
