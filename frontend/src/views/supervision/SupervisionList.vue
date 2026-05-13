<template>
  <div>
    <el-page-header title="监督管理" style="margin-bottom: 20px">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">监督管理列表</span>
      </template>
    </el-page-header>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>监管记录</span>
          <div>
            <el-button type="primary" icon="Plus">新增记录</el-button>
            <el-button icon="Download">导出</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏占位 -->
      <el-form :inline="true" style="margin-bottom: 10px">
        <el-form-item label="监管编号">
          <el-input placeholder="请输入监管编号" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="监管类型">
          <el-select placeholder="请选择类型" clearable style="width: 150px">
            <el-option label="日常巡检" value="日常巡检" />
            <el-option label="专项检查" value="专项检查" />
            <el-option label="年度考核" value="年度考核" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select placeholder="请选择状态" clearable style="width: 150px">
            <el-option label="待检查" value="待检查" />
            <el-option label="已完成" value="已完成" />
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
        <el-table-column prop="supervisionNo" label="监管编号" width="160" />
        <el-table-column prop="type" label="监管类型" width="120" />
        <el-table-column prop="deptName" label="被检部门" width="140" />
        <el-table-column prop="inspector" label="检查人" width="100" />
        <el-table-column prop="planDate" label="计划日期" width="120" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="180" fixed="right" />
      </el-table>

      <el-empty description="暂无监管记录数据" />
    </el-card>
  </div>
</template>

<script setup>
</script>
