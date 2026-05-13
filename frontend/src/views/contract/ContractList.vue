<template>
  <div>
    <el-page-header title="合同管理" style="margin-bottom: 20px">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">合同列表</span>
      </template>
    </el-page-header>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>合同列表</span>
          <div>
            <el-button type="primary" icon="Plus">新增合同</el-button>
            <el-button icon="Upload">导入</el-button>
            <el-button icon="Download">导出</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏占位 -->
      <el-form :inline="true" style="margin-bottom: 10px">
        <el-form-item label="合同编号">
          <el-input placeholder="请输入合同编号" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input placeholder="请输入供应商名称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select placeholder="请选择状态" clearable style="width: 150px">
            <el-option label="进行中" value="进行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已终止" value="已终止" />
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
        <el-table-column prop="contractNo" label="合同编号" width="160" />
        <el-table-column prop="title" label="合同名称" min-width="180" />
        <el-table-column prop="supplier" label="供应商" width="160" />
        <el-table-column prop="amount" label="合同金额" width="120" />
        <el-table-column prop="signDate" label="签订日期" width="120" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="180" fixed="right" />
      </el-table>

      <el-empty description="暂无合同数据" />
    </el-card>
  </div>
</template>

<script setup>
</script>
