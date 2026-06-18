<!--
  执行控制页面 / Execution control page
  @Function: 配置和启动测试执行，实时查看执行日志 / Configure and launch test execution, view real-time logs
-->
<template>
  <div class="execution-page">
    <!-- 执行配置 / Execution configuration -->
    <el-card shadow="never" class="exec-config">
      <template #header>
        <span>执行配置</span>
      </template>
      <el-form :inline="true" :model="execConfig" size="default">
        <el-form-item label="执行平台">
          <el-select v-model="execConfig.platform" style="width: 120px">
            <el-option label="Web" value="web" />
            <el-option label="Android" value="android" />
            <el-option label="iOS" value="ios" />
            <el-option label="小程序" value="miniapp" />
          </el-select>
        </el-form-item>
        <el-form-item label="浏览器" v-if="execConfig.platform === 'web'">
          <el-select v-model="execConfig.browser_type" style="width: 120px">
            <el-option label="Chrome" value="chromium" />
            <el-option label="Edge" value="msedge" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备" v-if="execConfig.platform !== 'web'">
          <el-select v-model="execConfig.device_id" style="width: 150px" placeholder="选择设备">
            <el-option v-for="d in devices" :key="d.device_id" :label="d.name" :value="d.device_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="无头模式" v-if="execConfig.platform === 'web'">
          <el-switch v-model="execConfig.headless" />
        </el-form-item>
        <el-form-item label="超时(秒)">
          <el-input-number v-model="execConfig.timeout" :min="5" :max="120" style="width: 100px" />
        </el-form-item>
        <el-form-item label="重试次数">
          <el-input-number v-model="execConfig.retry_count" :min="0" :max="10" style="width: 100px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="VideoPlay" @click="handleRun" :loading="running">
            执行用例
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用例选择 -->
    <el-card shadow="never" class="case-select">
      <template #header>
        <div class="card-header">
          <span>选择用例</span>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索用例"
            :prefix-icon="Search"
            clearable
            style="width: 200px"
          />
        </div>
      </template>
      <el-table :data="filteredCases" row-key="id" stripe @selection-change="handleSelectionChange" max-height="300">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="case_name" label="用例名称" />
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="row.priority === 'P0' ? 'danger' : 'warning'" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="platform" label="平台" width="80" />
      </el-table>
    </el-card>

    <!-- 执行控制台 -->
    <el-card shadow="never" class="exec-console" v-if="currentTask">
      <template #header>
        <div class="card-header">
          <span>执行控制台</span>
          <div class="console-actions">
            <el-button-group>
              <el-button size="small" :icon="VideoPlay" @click="handleResume" :disabled="currentTask.status !== 'paused'">
                继续
              </el-button>
              <el-button size="small" :icon="VideoPause" @click="handlePause" :disabled="currentTask.status !== 'running'">
                暂停
              </el-button>
              <el-button size="small" :icon="Close" @click="handleStop" :disabled="!['running', 'paused'].includes(currentTask.status)">
                停止
              </el-button>
            </el-button-group>
            <el-tag :type="getStatusType(currentTask.status)">{{ currentTask.status }}</el-tag>
          </div>
        </div>
      </template>

      <!-- 进度 -->
      <el-progress
        :percentage="execProgress"
        :status="currentTask.status === 'completed' ? 'success' : currentTask.status === 'failed' ? 'exception' : undefined"
        style="margin-bottom: 16px"
      />

      <!-- 步骤执行详情 -->
      <el-table :data="execSteps" row-key="step_index" stripe max-height="300">
        <el-table-column prop="step_index" label="步骤" width="60" />
        <el-table-column prop="step_name" label="步骤名称" />
        <el-table-column prop="keyword" label="关键字" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStepStatusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="80">
          <template #default="{ row }">
            {{ row.duration ? `${row.duration}s` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="message" label="信息" />
      </el-table>

      <!-- 实时日志 -->
      <div class="log-panel">
        <div class="log-header">
          <span>实时日志</span>
          <el-button size="small" link @click="clearLogs">清空</el-button>
        </div>
        <div class="log-content" ref="logContainer">
          <div v-for="(log, index) in logs" :key="index" :class="['log-item', `log-${log.level}`]">
            <span class="log-time">{{ log.timestamp }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 执行历史 -->
    <el-card shadow="never" class="exec-history">
      <template #header>
        <span>执行历史</span>
      </template>
      <el-table :data="execHistory" stripe>
        <el-table-column prop="task_id" label="任务ID" width="280" />
        <el-table-column prop="task_name" label="任务名称" />
        <el-table-column prop="platform" label="平台" width="80" />
        <el-table-column prop="case_count" label="用例数" width="80" />
        <el-table-column prop="pass_rate" label="通过率" width="100">
          <template #default="{ row }">
            <span :class="{ 'text-success': row.pass_rate >= 90, 'text-danger': row.pass_rate < 70 }">
              {{ row.pass_rate }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exec_time" label="执行时间" width="180" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewReport(row)">查看报告</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay, VideoPause, Close, Search } from '@element-plus/icons-vue'
import { caseApi, execApi, deviceApi } from '@/api'

const router = useRouter()

const execConfig = ref({
  platform: 'web',
  browser_type: 'chromium',
  device_id: '',
  headless: false,
  timeout: 30,
  retry_count: 3,
})

const cases = ref([])
const selectedCases = ref([])
const devices = ref([])
const searchKeyword = ref('')
const running = ref(false)

const currentTask = ref(null)
const execSteps = ref([])
const logs = ref([])
const logContainer = ref(null)
const execHistory = ref([])

let pollTimer = null

const filteredCases = computed(() => {
  if (!searchKeyword.value) return cases.value
  return cases.value.filter(c => c.case_name.includes(searchKeyword.value))
})

const execProgress = computed(() => {
  if (!currentTask.value) return 0
  const { case_count, current_case_index } = currentTask.value
  if (!case_count) return 0
  return Math.round((current_case_index + 1) / case_count * 100)
})

onMounted(() => {
  loadCases()
  loadDevices()
  loadHistory()
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

const loadCases = async () => {
  try {
    const result = await caseApi.getList({ page_size: 100 })
    cases.value = result.list
  } catch (error) {
    console.error('加载用例失败:', error)
  }
}

const loadDevices = async () => {
  try {
    devices.value = await deviceApi.getList()
  } catch (error) {
    console.error('加载设备失败:', error)
  }
}

const loadHistory = async () => {
  try {
    const result = await execApi.getTasks({ page_size: 10 })
    execHistory.value = result.list
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

const handleRun = async () => {
  if (!selectedCases.value.length) {
    ElMessage.warning('请选择要执行的用例')
    return
  }

  running.value = true
  try {
    const result = await execApi.run({
      case_ids: selectedCases.value.map(c => c.id),
      ...execConfig.value,
    })
    currentTask.value = { task_id: result.task_id, status: 'pending', case_count: selectedCases.value.length }
    startPolling(result.task_id)
    ElMessage.success('任务已创建')
  } catch (error) {
    console.error('执行失败:', error)
  } finally {
    running.value = false
  }
}

const startPolling = (taskId) => {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const status = await execApi.getStatus(taskId)
      currentTask.value = status
      if (['completed', 'failed', 'stopped'].includes(status.status)) {
        clearInterval(pollTimer)
        loadHistory()
      }
    } catch (error) {
      console.error('轮询失败:', error)
    }
  }, 1000)
}

const handlePause = async () => {
  try {
    await execApi.control(currentTask.value.task_id, 'pause')
    currentTask.value.status = 'paused'
    addLog('info', '任务已暂停')
  } catch (error) {
    console.error('暂停失败:', error)
  }
}

const handleResume = async () => {
  try {
    await execApi.control(currentTask.value.task_id, 'resume')
    currentTask.value.status = 'running'
    addLog('info', '任务已继续')
  } catch (error) {
    console.error('继续失败:', error)
  }
}

const handleStop = async () => {
  try {
    await execApi.control(currentTask.value.task_id, 'stop')
    currentTask.value.status = 'stopped'
    addLog('info', '任务已停止')
  } catch (error) {
    console.error('停止失败:', error)
  }
}

const addLog = (level, message) => {
  logs.value.push({
    level,
    message,
    timestamp: new Date().toLocaleTimeString(),
  })
  // 自动滚动到底部
  setTimeout(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  }, 100)
}

const clearLogs = () => {
  logs.value = []
}

const getStatusType = (status) => {
  const map = { completed: 'success', failed: 'danger', running: 'warning', paused: 'info', stopped: 'info', pending: '' }
  return map[status] || ''
}

const getStepStatusType = (status) => {
  const map = { passed: 'success', failed: 'danger', running: 'warning', skipped: 'info' }
  return map[status] || ''
}

const viewReport = (row) => {
  router.push(`/report?task_id=${row.task_id}`)
}
</script>

<style scoped>
.execution-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.exec-config :deep(.el-card__body) {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.console-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.log-panel {
  margin-top: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.log-content {
  height: 200px;
  overflow-y: auto;
  padding: 8px 12px;
  font-family: monospace;
  font-size: 12px;
}

.log-item {
  line-height: 1.8;
}

/* 修复长文本换行 / Fix long text wrapping */
.execution-page :deep(.el-table .cell) {
  word-break: break-all;
  white-space: pre-wrap;
}

.log-time {
  color: #909399;
  margin-right: 8px;
}

.log-info .log-message { color: #303133; }
.log-success .log-message { color: #67c23a; }
.log-warning .log-message { color: #e6a23c; }
.log-error .log-message { color: #f56c6c; }

.text-success {
  color: #67c23a;
  font-weight: 600;
}

.text-danger {
  color: #f56c6c;
  font-weight: 600;
}
</style>
