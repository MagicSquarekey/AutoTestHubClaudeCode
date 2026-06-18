<!--
  页面录制页面 / Page recording page
  @Function: 录制浏览器操作，支持编辑和回放 / Record browser actions, support editing and replay
-->
<template>
  <div class="record-page">
    <el-row :gutter="16" class="main-content">
      <!-- 左侧：任务列表 / Left: Task list -->
      <el-col :span="6">
        <el-card shadow="never" class="task-list-card">
          <template #header>
            <div class="card-header">
              <span>录制任务</span>
              <el-button type="primary" :icon="Plus" size="small" @click="handleCreateTask">新建</el-button>
            </div>
          </template>

          <!-- 搜索 / Search -->
          <el-input
            v-model="searchKeyword"
            placeholder="搜索任务"
            :prefix-icon="Search"
            clearable
            class="search-input"
            @input="loadTasks"
          />

          <!-- 任务列表 / Task list -->
          <div class="task-list" v-loading="tasksLoading">
            <div
              v-for="task in taskList"
              :key="task.id"
              :class="['task-item', { active: currentTask?.id === task.id }]"
              @click="selectTask(task)"
            >
              <div class="task-info">
                <div class="task-name">{{ task.task_name }}</div>
                <div class="task-meta">
                  <el-tag :type="getStatusType(task.status)" size="small">
                    {{ getStatusLabel(task.status) }}
                  </el-tag>
                  <span class="step-count">{{ task.step_count }} 步</span>
                </div>
              </div>
              <el-button
                type="danger"
                :icon="Delete"
                link
                size="small"
                @click.stop="handleDeleteTask(task)"
              />
            </div>
            <el-empty v-if="!taskList.length && !tasksLoading" description="暂无录制任务" />
          </div>

          <!-- 分页 / Pagination -->
          <div class="pagination" v-if="tasksTotal > pageSize">
            <el-pagination
              v-model:current-page="currentTaskPage"
              v-model:page-size="pageSize"
              :total="tasksTotal"
              layout="prev, pager, next"
              small
              @current-change="loadTasks"
            />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：录制工作区 / Right: Recording workspace -->
      <el-col :span="18">
        <!-- 录制控制 / Recording controls -->
        <el-card shadow="never" class="control-card">
          <div class="control-bar">
            <el-input
              v-model="targetUrl"
              placeholder="输入目标URL，例如：https://www.example.com"
              clearable
              class="url-input"
              :disabled="isRecording"
            >
              <template #prepend>URL</template>
            </el-input>
            <el-button
              v-if="!isRecording"
              type="danger"
              :icon="VideoCamera"
              :disabled="!currentTask || isStarting"
              :loading="isStarting"
              @click="handleStartRecording"
            >
              {{ isStarting ? '启动中...' : '开始录制' }}
            </el-button>
            <el-button
              v-else
              type="warning"
              :icon="VideoPause"
              @click="handleStopRecording"
            >
              停止录制
            </el-button>
          </div>
          <div v-if="isRecording" class="recording-indicator">
            <el-badge is-dot class="recording-badge">
              <span class="recording-text">正在录制中...</span>
            </el-badge>
          </div>
        </el-card>

        <!-- 操作步骤 / Action steps -->
        <el-card shadow="never" class="steps-card">
          <template #header>
            <div class="card-header">
              <span>操作步骤</span>
              <div class="header-actions">
                <el-button
                  type="success"
                  :icon="DocumentCopy"
                  :disabled="!currentTask || !stepsList.length"
                  @click="handleConvertToCase"
                >
                  转换为用例
                </el-button>
                <el-button
                  type="danger"
                  :icon="Delete"
                  :disabled="!selectedSteps.length"
                  @click="handleBatchDeleteSteps"
                >
                  批量删除
                </el-button>
              </div>
            </div>
          </template>

          <!-- 步骤列表 / Steps list -->
          <el-table
            ref="stepsTable"
            v-loading="stepsLoading"
            :data="stepsList"
            row-key="id"
            stripe
            @selection-change="handleStepSelectionChange"
            class="steps-table"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="step_order" label="序号" width="70" align="center" />
            <el-table-column prop="action_type" label="操作" width="100">
              <template #default="{ row }">
                <el-tag :type="getActionTypeTag(row.action_type)" size="small">
                  {{ getActionTypeLabel(row.action_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="element_name" label="元素" min-width="150" show-overflow-tooltip />
            <el-table-column prop="input_value" label="值" min-width="150" show-overflow-tooltip />
            <el-table-column prop="page_url" label="页面URL" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row, $index }">
                <el-button type="primary" link size="small" @click="handleEditStep(row)">编辑</el-button>
                <el-button
                  type="primary"
                  link
                  size="small"
                  :disabled="$index === 0"
                  @click="handleMoveStep(row, 'up')"
                >上移</el-button>
                <el-button
                  type="primary"
                  link
                  size="small"
                  :disabled="$index === stepsList.length - 1"
                  @click="handleMoveStep(row, 'down')"
                >下移</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteStep(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!stepsList.length && !stepsLoading" description="暂无录制步骤，请开始录制" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 新建任务对话框 / Create task dialog -->
    <el-dialog v-model="createTaskDialogVisible" title="新建录制任务" width="500px" @keyup.enter="handleDialogEnter">
      <el-form :model="newTaskForm" label-width="80px">
        <el-form-item label="任务名称" required>
          <el-input v-model="newTaskForm.task_name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="目标URL">
          <el-input v-model="newTaskForm.target_url" placeholder="请输入目标URL" />
        </el-form-item>
        <el-form-item label="浏览器">
          <el-select v-model="newTaskForm.browser_type" style="width: 100%">
            <el-option label="Chromium" value="chromium" />
            <el-option label="Firefox" value="firefox" />
            <el-option label="WebKit" value="webkit" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newTaskForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTaskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCreateTask">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑步骤对话框 / Edit step dialog -->
    <el-dialog v-model="editStepDialogVisible" title="编辑步骤" width="600px">
      <el-form :model="editStepForm" label-width="100px">
        <el-form-item label="操作类型" required>
          <el-select v-model="editStepForm.action_type" style="width: 100%">
            <el-option label="页面导航" value="navigate" />
            <el-option label="点击" value="click" />
            <el-option label="输入" value="input" />
            <el-option label="选择" value="select" />
            <el-option label="悬停" value="hover" />
            <el-option label="等待" value="wait" />
            <el-option label="键盘" value="keyboard" />
          </el-select>
        </el-form-item>
        <el-form-item label="元素名称">
          <el-input v-model="editStepForm.element_name" placeholder="元素名称" />
        </el-form-item>
        <el-form-item label="输入值">
          <el-input v-model="editStepForm.input_value" placeholder="输入值/URL/按键" />
        </el-form-item>
        <el-form-item label="元素定位符">
          <el-input
            v-model="editStepForm.element_locators_str"
            type="textarea"
            :rows="4"
            placeholder="JSON格式的定位符"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editStepDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmEditStep">确定</el-button>
      </template>
    </el-dialog>

    <!-- 转换为用例对话框 / Convert to case dialog -->
    <el-dialog v-model="convertDialogVisible" title="转换为测试用例" width="500px">
      <el-form :model="convertForm" label-width="80px">
        <el-form-item label="用例名称" required>
          <el-input v-model="convertForm.case_name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="所属模块">
          <el-input v-model="convertForm.module" placeholder="请输入模块名称" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="convertForm.priority" style="width: 100%">
            <el-option label="P0" value="P0" />
            <el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="convertForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请输入标签"
            style="width: 100%"
          >
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="convertForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="convertDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="converting" @click="confirmConvert">确定转换</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Search, VideoCamera, VideoPause, DocumentCopy } from '@element-plus/icons-vue'
import { recordApi } from '@/api'

const router = useRouter()

// 组件卸载时停止轮询 / Stop polling when component unmounts
onUnmounted(() => {
  stopPollingStatus()
})

// ==================== 任务列表状态 / Task list state ====================
const tasksLoading = ref(false)
const taskList = ref([])
const tasksTotal = ref(0)
const currentTaskPage = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const currentTask = ref(null)

// ==================== 录制状态 / Recording state ====================
const isRecording = ref(false)
const isStarting = ref(false)  // 防止重复点击
const targetUrl = ref('')

// ==================== 步骤列表状态 / Steps list state ====================
const stepsLoading = ref(false)
const stepsList = ref([])
const selectedSteps = ref([])

// ==================== 对话框状态 / Dialog state ====================
const createTaskDialogVisible = ref(false)
const newTaskForm = ref({
  task_name: '',
  target_url: '',
  browser_type: 'chromium',
  description: '',
})

const editStepDialogVisible = ref(false)
const editStepForm = ref({
  id: null,
  action_type: '',
  element_name: '',
  input_value: '',
  element_locators_str: '',
})

const convertDialogVisible = ref(false)
const convertForm = ref({
  case_name: '',
  module: '',
  priority: 'P0',
  tags: [],
  description: '',
})
const converting = ref(false)

// ==================== 生命周期 / Lifecycle ====================
onMounted(() => {
  loadTasks()
})

// ==================== 任务操作 / Task operations ====================

async function loadTasks() {
  tasksLoading.value = true
  try {
    const res = await recordApi.getTaskList({
      keyword: searchKeyword.value,
      page: currentTaskPage.value,
      page_size: pageSize.value,
    })
    taskList.value = res.list || []
    tasksTotal.value = res.total || 0
  } catch (e) {
    console.error('加载任务列表失败:', e)
  } finally {
    tasksLoading.value = false
  }
}

function selectTask(task) {
  currentTask.value = task
  targetUrl.value = task.target_url || ''
  loadSteps()
}

function handleCreateTask() {
  newTaskForm.value = {
    task_name: '',
    target_url: '',
    browser_type: 'chromium',
    description: '',
  }
  createTaskDialogVisible.value = true
}

// 处理对话框Enter键提交 / Handle Enter key submission in dialog
function handleDialogEnter(event) {
  // 如果焦点在textarea内，不触发提交（允许textarea中换行）
  if (event.target.tagName === 'TEXTAREA') {
    return
  }
  confirmCreateTask()
}

async function confirmCreateTask() {
  if (!newTaskForm.value.task_name) {
    ElMessage.warning('请输入任务名称')
    return
  }

  try {
    const res = await recordApi.createTask(newTaskForm.value)
    ElMessage.success('创建成功')
    createTaskDialogVisible.value = false
    loadTasks()
    // 选中新创建的任务 / Select newly created task
    selectTask(res)
  } catch (e) {
    console.error('创建任务失败:', e)
  }
}

async function handleDeleteTask(task) {
  try {
    await ElMessageBox.confirm('确定要删除该录制任务吗？删除后不可恢复。', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await recordApi.deleteTask(task.id)
    ElMessage.success('删除成功')

    if (currentTask.value?.id === task.id) {
      currentTask.value = null
      stepsList.value = []
    }

    loadTasks()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除任务失败:', e)
    }
  }
}

// ==================== 录制操作 / Recording operations ====================

async function handleStartRecording() {
  if (!currentTask.value) {
    ElMessage.warning('请先选择或创建一个录制任务')
    return
  }

  // 防止重复点击
  if (isStarting.value) {
    ElMessage.warning('正在启动录制，请稍候...')
    return
  }

  isStarting.value = true

  try {
    // 更新任务的 target_url（如果已填写）
    if (targetUrl.value) {
      await recordApi.updateTask(currentTask.value.id, { target_url: targetUrl.value })
    }

    const res = await recordApi.startRecording(currentTask.value.id)

    if (res.code === 1) {
      // API 返回错误
      ElMessage.warning(res.message || '启动录制失败')
      isStarting.value = false
      return
    }

    isRecording.value = true
    ElMessage.success('录制已开始，浏览器即将打开...')

    // 更新当前任务状态
    currentTask.value.status = 'recording'

    // 延迟启动轮询，给后端时间初始化引擎
    // Delay polling start to give backend time to initialize engine
    setTimeout(() => {
      startPollingStatus()
    }, 500)
  } catch (e) {
    console.error('开始录制失败:', e)
    ElMessage.error('开始录制失败: ' + (e.message || '未知错误'))
  } finally {
    isStarting.value = false
  }
}

async function handleStopRecording() {
  try {
    const res = await recordApi.stopRecording(currentTask.value.id)
    isRecording.value = false
    ElMessage.success(res.message || '录制已停止')

    // 停止轮询 / Stop polling
    stopPollingStatus()

    // 更新当前任务状态
    if (currentTask.value) {
      currentTask.value.status = 'completed'
    }

    // 刷新步骤列表 / Refresh steps list
    loadSteps()
    loadTasks()
  } catch (e) {
    console.error('停止录制失败:', e)
    ElMessage.error('停止录制失败: ' + (e.message || '未知错误'))
  }
}

let pollingTimer = null
let pollingErrorCount = 0  // 连续轮询错误计数 / Consecutive polling error count

function startPollingStatus() {
  stopPollingStatus()
  pollingErrorCount = 0
  pollingTimer = setInterval(async () => {
    if (!currentTask.value) return

    try {
      const status = await recordApi.getRecordingStatus(currentTask.value.id)
      pollingErrorCount = 0  // 重置错误计数 / Reset error count

      // 更新步骤列表
      if (status.steps) {
        stepsList.value = status.steps
      }

      // 检查录制是否已停止（可能是浏览器被关闭）
      if (!status.is_recording && isRecording.value) {
        isRecording.value = false
        stopPollingStatus()
        if (currentTask.value) {
          currentTask.value.status = 'completed'
        }
        ElMessage.info('录制已结束')
        loadTasks()
      }
    } catch (e) {
      pollingErrorCount++
      console.error('获取录制状态失败:', e)
      // 连续失败3次以上才认为录制结束（避免网络波动误判）
      // Only consider recording ended after 3+ consecutive failures
      if (pollingErrorCount >= 3 && isRecording.value) {
        console.warn('连续轮询失败次数过多，可能录制已异常结束')
        // 不自动设置 isRecording = false，让用户手动停止
        // Don't auto-set isRecording = false, let user manually stop
      }
    }
  }, 1000)  // 每秒轮询一次
}

function stopPollingStatus() {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
  pollingErrorCount = 0
}

// ==================== 步骤操作 / Step operations ====================

async function loadSteps() {
  if (!currentTask.value) return

  stepsLoading.value = true
  try {
    const res = await recordApi.getSteps(currentTask.value.id)
    stepsList.value = res || []
  } catch (e) {
    console.error('加载步骤列表失败:', e)
  } finally {
    stepsLoading.value = false
  }
}

function handleStepSelectionChange(selection) {
  selectedSteps.value = selection
}

function handleEditStep(step) {
  editStepForm.value = {
    id: step.id,
    action_type: step.action_type,
    element_name: step.element_name,
    input_value: step.input_value,
    element_locators_str: step.element_locators || '{}',
  }
  editStepDialogVisible.value = true
}

async function confirmEditStep() {
  try {
    let elementLocators = {}
    try {
      elementLocators = JSON.parse(editStepForm.value.element_locators_str)
    } catch (e) {
      ElMessage.warning('元素定位符格式错误，请输入有效的JSON')
      return
    }

    await recordApi.updateStep(editStepForm.value.id, {
      action_type: editStepForm.value.action_type,
      element_name: editStepForm.value.element_name,
      input_value: editStepForm.value.input_value,
      element_locators: elementLocators,
    })

    ElMessage.success('更新成功')
    editStepDialogVisible.value = false
    loadSteps()
  } catch (e) {
    console.error('更新步骤失败:', e)
  }
}

async function handleMoveStep(step, direction) {
  try {
    await recordApi.moveStep(step.id, direction)
    loadSteps()
  } catch (e) {
    console.error('移动步骤失败:', e)
  }
}

async function handleDeleteStep(step) {
  try {
    await ElMessageBox.confirm('确定要删除该步骤吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await recordApi.deleteStep(step.id)
    ElMessage.success('删除成功')
    loadSteps()
    loadTasks()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除步骤失败:', e)
    }
  }
}

async function handleBatchDeleteSteps() {
  if (!selectedSteps.value.length) return

  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedSteps.value.length} 个步骤吗？`, '批量删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    for (const step of selectedSteps.value) {
      await recordApi.deleteStep(step.id)
    }

    ElMessage.success('批量删除成功')
    loadSteps()
    loadTasks()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('批量删除步骤失败:', e)
    }
  }
}

// ==================== 转换操作 / Convert operations ====================

function handleConvertToCase() {
  if (!currentTask.value || !stepsList.value.length) {
    ElMessage.warning('请先录制操作步骤')
    return
  }

  convertForm.value = {
    case_name: currentTask.value.task_name || '',
    module: '',
    priority: 'P0',
    tags: [],
    description: '',
  }
  convertDialogVisible.value = true
}

async function confirmConvert() {
  if (!convertForm.value.case_name) {
    ElMessage.warning('请输入用例名称')
    return
  }

  converting.value = true
  try {
    const res = await recordApi.convertToCase(currentTask.value.id, convertForm.value)
    ElMessage.success('转换成功')
    convertDialogVisible.value = false

    // 跳转到用例编辑页面 / Navigate to case edit page
    await ElMessageBox.confirm('转换成功！是否跳转到用例编辑页面？', '提示', {
      confirmButtonText: '去编辑',
      cancelButtonText: '留在本页',
      type: 'success',
    })

    router.push({ name: 'CaseEdit', params: { id: res.id } })
  } catch (e) {
    if (e !== 'cancel') {
      console.error('转换失败:', e)
    }
  } finally {
    converting.value = false
  }
}

// ==================== 工具函数 / Utility functions ====================

function getStatusType(status) {
  const map = {
    pending: 'info',
    recording: 'danger',
    completed: 'success',
    stopped: 'warning',
  }
  return map[status] || 'info'
}

function getStatusLabel(status) {
  const map = {
    pending: '待录制',
    recording: '录制中',
    completed: '已完成',
    stopped: '已停止',
  }
  return map[status] || status
}

function getActionTypeTag(actionType) {
  const map = {
    navigate: 'primary',
    click: 'success',
    input: 'warning',
    select: 'warning',
    hover: 'info',
    wait: 'info',
    keyboard: 'danger',
  }
  return map[actionType] || 'info'
}

function getActionTypeLabel(actionType) {
  const map = {
    navigate: '导航',
    click: '点击',
    input: '输入',
    select: '选择',
    hover: '悬停',
    wait: '等待',
    keyboard: '键盘',
  }
  return map[actionType] || actionType
}
</script>

<style scoped>
.record-page {
  height: 100%;
  padding: 16px;
}

.main-content {
  height: 100%;
}

.task-list-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-input {
  margin-bottom: 12px;
}

.task-list {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e4e7ed;
}

.task-item:hover {
  background-color: #f5f7fa;
}

.task-item.active {
  background-color: #ecf5ff;
  border-color: #409eff;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-name {
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.step-count {
  font-size: 12px;
}

.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: center;
}

.control-card {
  margin-bottom: 16px;
}

.control-bar {
  display: flex;
  gap: 12px;
}

.url-input {
  flex: 1;
}

.recording-indicator {
  margin-top: 12px;
  display: flex;
  align-items: center;
}

.recording-text {
  color: #f56c6c;
  font-weight: 500;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.steps-card {
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.steps-table {
  width: 100%;
}

/* 修复长文本换行 / Fix long text wrapping */
.record-page :deep(.el-table .cell) {
  word-break: break-all;
  white-space: pre-wrap;
}
</style>
