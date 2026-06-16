<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background-color: #409eff">
            <el-icon :size="32"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalCases }}</div>
            <div class="stat-label">用例总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background-color: #67c23a">
            <el-icon :size="32"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.passRate }}%</div>
            <div class="stat-label">通过率</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background-color: #e6a23c">
            <el-icon :size="32"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalExecutions }}</div>
            <div class="stat-label">执行次数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background-color: #909399">
            <el-icon :size="32"><Pointer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalElements }}</div>
            <div class="stat-label">元素总数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <span>执行趋势</span>
          </template>
          <div ref="trendChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <span>用例分布</span>
          </template>
          <div ref="pieChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近执行 -->
    <el-card shadow="hover" class="recent-exec">
      <template #header>
        <div class="card-header">
          <span>最近执行</span>
          <el-button type="primary" link>查看全部</el-button>
        </div>
      </template>
      <el-table :data="recentExecutions" stripe>
        <el-table-column prop="task_name" label="任务名称" />
        <el-table-column prop="platform" label="平台" width="100">
          <template #default="{ row }">
            <el-tag :type="getPlatformTag(row.platform)">{{ row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="case_count" label="用例数" width="100" />
        <el-table-column prop="pass_rate" label="通过率" width="100">
          <template #default="{ row }">
            <span :class="{ 'text-success': row.pass_rate >= 90, 'text-danger': row.pass_rate < 70 }">
              {{ row.pass_rate }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="exec_duration" label="耗时" width="100">
          <template #default="{ row }">
            {{ formatDuration(row.exec_duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exec_time" label="执行时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { reportApi } from '@/api'

const trendChart = ref(null)
const pieChart = ref(null)

const stats = ref({
  totalCases: 0,
  passRate: 0,
  totalExecutions: 0,
  totalElements: 0,
})

const recentExecutions = ref([])

onMounted(async () => {
  await loadData()
  initCharts()
})

const loadData = async () => {
  try {
    const overview = await reportApi.getStatisticsOverview()
    stats.value = {
      totalCases: overview.total_cases || 0,
      passRate: overview.avg_pass_rate || 0,
      totalExecutions: overview.total_executions || 0,
      totalElements: 0,
    }
    recentExecutions.value = overview.recent_executions || []
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const initCharts = () => {
  // 趋势图
  if (trendChart.value) {
    const chart = echarts.init(trendChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['通过率', '执行次数'] },
      xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
      yAxis: [
        { type: 'value', name: '通过率(%)', max: 100 },
        { type: 'value', name: '次数' },
      ],
      series: [
        { name: '通过率', type: 'line', data: [95, 92, 88, 96, 94, 90, 93] },
        { name: '执行次数', type: 'bar', yAxisIndex: 1, data: [10, 15, 8, 12, 20, 5, 18] },
      ],
    })
  }

  // 饼图
  if (pieChart.value) {
    const chart = echarts.init(pieChart.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left' },
      series: [
        {
          type: 'pie',
          radius: '50%',
          data: [
            { value: 40, name: 'Web端' },
            { value: 30, name: 'Android端' },
            { value: 20, name: '小程序' },
            { value: 10, name: 'iOS端' },
          ],
        },
      ],
    })
  }
}

const getPlatformTag = (platform) => {
  const map = { web: '', android: 'success', ios: 'warning', miniapp: 'info' }
  return map[platform] || ''
}

const getStatusTag = (status) => {
  const map = { completed: 'success', failed: 'danger', running: 'warning', pending: 'info' }
  return map[status] || ''
}

const formatDuration = (seconds) => {
  if (!seconds) return '-'
  const min = Math.floor(seconds / 60)
  const sec = seconds % 60
  return min > 0 ? `${min}m${sec}s` : `${sec}s`
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-cards {
  margin-bottom: 0;
}

.stat-card {
  display: flex;
  align-items: center;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 20px;
  width: 100%;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.chart-row {
  margin-bottom: 0;
}

.chart-container {
  height: 300px;
}

.recent-exec {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-success {
  color: #67c23a;
  font-weight: 600;
}

.text-danger {
  color: #f56c6c;
  font-weight: 600;
}
</style>
