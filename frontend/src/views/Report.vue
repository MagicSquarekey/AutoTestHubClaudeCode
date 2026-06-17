<!--
  测试报告页面 / Test report page
  @Function: 展示执行统计、报告列表、失败分析 / Display execution stats, report list, failure analysis
-->
<template>
  <div class="report-page">
    <!-- 统计概览 / Statistics overview -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总执行次数" :value="stats.total_executions" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总用例数" :value="stats.total_cases" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="平均通过率" :value="stats.avg_pass_rate" suffix="%" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="最近执行" :value="recentExecTime" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势图 -->
    <el-card shadow="never" class="trend-card">
      <template #header>
        <div class="card-header">
          <span>执行趋势</span>
          <el-select v-model="trendDays" size="small" style="width: 100px" @change="loadTrend">
            <el-option label="近7天" :value="7" />
            <el-option label="近30天" :value="30" />
            <el-option label="近90天" :value="90" />
          </el-select>
        </div>
      </template>
      <div ref="trendChart" class="chart-container"></div>
    </el-card>

    <!-- 报告列表 -->
    <el-card shadow="never">
      <template #header>
        <span>执行报告</span>
      </template>
      <el-table :data="reportList" stripe>
        <el-table-column prop="task_id" label="任务ID" width="280" />
        <el-table-column prop="task_name" label="任务名称" />
        <el-table-column prop="platform" label="平台" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="case_count" label="用例数" width="80" />
        <el-table-column prop="pass_count" label="通过" width="70">
          <template #default="{ row }">
            <span class="text-success">{{ row.pass_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="fail_count" label="失败" width="70">
          <template #default="{ row }">
            <span class="text-danger">{{ row.fail_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pass_rate" label="通过率" width="100">
          <template #default="{ row }">
            <el-progress
              :percentage="row.pass_rate"
              :color="row.pass_rate >= 90 ? '#67c23a' : row.pass_rate >= 70 ? '#e6a23c' : '#f56c6c'"
              :stroke-width="6"
            />
          </template>
        </el-table-column>
        <el-table-column prop="exec_duration" label="耗时" width="80">
          <template #default="{ row }">
            {{ formatDuration(row.exec_duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="exec_time" label="执行时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">详情</el-button>
            <el-button type="primary" link size="small" @click="downloadReport(row)">下载报告</el-button>
            <el-button type="primary" link size="small" @click="exportDefect(row)">导出缺陷</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadReports"
        />
      </div>
    </el-card>

    <!-- 报告详情对话框 -->
    <el-dialog v-model="detailVisible" title="报告详情" width="800px">
      <template v-if="currentReport">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ currentReport.task_id }}</el-descriptions-item>
          <el-descriptions-item label="任务名称">{{ currentReport.task_name }}</el-descriptions-item>
          <el-descriptions-item label="执行平台">{{ currentReport.platform }}</el-descriptions-item>
          <el-descriptions-item label="执行时间">{{ currentReport.exec_time }}</el-descriptions-item>
          <el-descriptions-item label="用例总数">{{ currentReport.case_count }}</el-descriptions-item>
          <el-descriptions-item label="通过率">{{ currentReport.pass_rate }}%</el-descriptions-item>
          <el-descriptions-item label="通过数">{{ currentReport.pass_count }}</el-descriptions-item>
          <el-descriptions-item label="失败数">{{ currentReport.fail_count }}</el-descriptions-item>
          <el-descriptions-item label="执行耗时">{{ formatDuration(currentReport.exec_duration) }}</el-descriptions-item>
          <el-descriptions-item label="设备信息">{{ currentReport.device_info }}</el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h4>失败分析</h4>
        <div v-if="failureAnalysis" class="failure-analysis">
          <el-row :gutter="16">
            <el-col :span="6">
              <el-statistic title="业务缺陷" :value="failureAnalysis.categories?.business_defect || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="元素失效" :value="failureAnalysis.categories?.element_failure || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="环境问题" :value="failureAnalysis.categories?.environment_issue || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="用例错误" :value="failureAnalysis.categories?.case_error || 0" />
            </el-col>
          </el-row>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { reportApi } from '@/api'

const stats = ref({
  total_executions: 0,
  total_cases: 0,
  avg_pass_rate: 0,
})

const recentExecTime = ref('-')
const trendDays = ref(30)
const trendChart = ref(null)

const reportList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const detailVisible = ref(false)
const currentReport = ref(null)
const failureAnalysis = ref(null)

onMounted(async () => {
  await loadStats()
  await loadReports()
  loadTrend()
})

const loadStats = async () => {
  try {
    const data = await reportApi.getStatisticsOverview()
    stats.value = data
    if (data.recent_executions?.length) {
      recentExecTime.value = data.recent_executions[0].exec_time
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadReports = async () => {
  try {
    const result = await reportApi.getList({ page: currentPage.value, page_size: pageSize.value })
    reportList.value = result.list
    total.value = result.total
  } catch (error) {
    console.error('加载报告失败:', error)
  }
}

const loadTrend = async () => {
  try {
    const data = await reportApi.getStatisticsTrend({ days: trendDays.value })
    initTrendChart(data.trend || [])
  } catch (error) {
    console.error('加载趋势失败:', error)
  }
}

const initTrendChart = (trend) => {
  if (!trendChart.value) return

  const chart = echarts.init(trendChart.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['通过率', '执行次数'] },
    xAxis: {
      type: 'category',
      data: trend.map(t => t.date),
    },
    yAxis: [
      { type: 'value', name: '通过率(%)', max: 100 },
      { type: 'value', name: '次数' },
    ],
    series: [
      {
        name: '通过率',
        type: 'line',
        data: trend.map(t => t.pass_rate),
        smooth: true,
      },
      {
        name: '执行次数',
        type: 'bar',
        yAxisIndex: 1,
        data: trend.map(t => t.execution_count),
      },
    ],
  })
}

const viewDetail = async (row) => {
  currentReport.value = row
  detailVisible.value = true

  try {
    failureAnalysis.value = await reportApi.getFailureAnalysis(row.task_id)
  } catch (error) {
    console.error('加载失败分析失败:', error)
  }
}

const downloadReport = (row) => {
  window.open(reportApi.getHtml(row.task_id), '_blank')
}

const exportDefect = async (row) => {
  try {
    const data = await reportApi.exportDefect(row.task_id)
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `defect_${row.task_id}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
  }
}

const formatDuration = (seconds) => {
  if (!seconds) return '-'
  const min = Math.floor(seconds / 60)
  const sec = seconds % 60
  return min > 0 ? `${min}m${sec}s` : `${sec}s`
}
</script>

<style scoped>
.report-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-row {
  margin-bottom: 0;
}

.stat-card :deep(.el-card__body) {
  text-align: center;
}

.trend-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.failure-analysis {
  margin-top: 16px;
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
