<template>
  <div>
    <el-page-header title="检定管理" style="margin-bottom: 20px">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">检定计划</span>
      </template>
    </el-page-header>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>检定计划列表</span>
          <div>
            <el-button type="primary" icon="Plus">新增计划</el-button>
            <el-button icon="Download">导出 Excel</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏占位 -->
      <el-form :inline="true" style="margin-bottom: 10px">
        <el-form-item label="计划年度">
          <el-date-picker
            type="year"
            placeholder="选择年度"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select placeholder="请选择状态" clearable style="width: 150px">
            <el-option label="待执行" value="待执行" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已延期" value="已延期" />
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
        <el-table-column prop="instrumentName" label="仪器名称" min-width="160" />
        <el-table-column prop="model" label="型号" width="120" />
        <el-table-column prop="planDate" label="计划检定日期" width="140" />
        <el-table-column prop="actualDate" label="实际检定日期" width="140" />
        <el-table-column prop="result" label="检定结果" width="100" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="180" fixed="right" />
      </el-table>

      <el-empty description="暂无检定计划数据" />
    </el-card>
  </div>
</template>

<script setup>
</script>
