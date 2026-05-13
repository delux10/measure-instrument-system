<template>
  <div>
    <el-page-header title="仪器管理" style="margin-bottom: 20px">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">仪器台账</span>
      </template>
    </el-page-header>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>仪器列表</span>
          <div>
            <el-button type="primary" icon="Plus">新增仪器</el-button>
            <el-button icon="Download">导出 Excel</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏占位 -->
      <el-form :inline="true" style="margin-bottom: 10px">
        <el-form-item label="仪器名称">
          <el-input placeholder="请输入仪器名称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select placeholder="请选择状态" clearable style="width: 150px">
            <el-option label="正常" value="正常" />
            <el-option label="待检定" value="待检定" />
            <el-option label="已过期" value="已过期" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search">查询</el-button>
          <el-button icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格占位 -->
      <el-table :data="[]" border stripe style="width: 100%">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="name" label="仪器名称" min-width="160" />
        <el-table-column prop="model" label="型号" width="140" />
        <el-table-column prop="serialNumber" label="出厂编号" width="140" />
        <el-table-column prop="department" label="使用部门" width="120" />
        <el-table-column prop="lastCalibration" label="最近检定日期" width="140" />
        <el-table-column prop="nextCalibration" label="下次检定日期" width="140" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="200" fixed="right" />
      </el-table>

      <el-empty description="暂无仪器数据" />
    </el-card>
  </div>
</template>

<script setup>
</script>
