<!--
  任务调度页面 / Task scheduler page
  @Function: 用例集管理和定时任务配置 / Test suite management and scheduled task configuration
-->
<template>
  <div class="scheduler-page">
    <!-- 用例集管理 / Test suite management -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>用例集管理</span>
          <el-button size="small" type="primary" :icon="Plus" @click="createSuite">新建用例集</el-button>
        </div>
      </template>
      <el-table :data="suites" stripe>
        <el-table-column prop="suite_name" label="用例集名称" />
        <el-table-column prop="suite_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getSuiteTypeTag(row.suite_type)" size="small">{{ row.suite_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="platform" label="平台" width="80" />
        <el-table-column label="用例数" width="80">
          <template #default="{ row }">
            <el-tag size="small" type="primary">{{ row.case_ids?.length || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="update_time" label="更新时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="runSuite(row)">执行</el-button>
            <el-button type="primary" link size="small" @click="editSuite(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteSuite(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 定时任务管理 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>定时任务管理</span>
          <el-button size="small" type="primary" :icon="Plus" @click="createTask">新建定时任务</el-button>
        </div>
      </template>
      <el-table :data="tasks" stripe>
        <el-table-column prop="task_name" label="任务名称" />
        <el-table-column prop="suite_name" label="关联用例集" width="120" />
        <el-table-column prop="cron_expression" label="Cron表达式" width="120" />
        <el-table-column prop="platform" label="平台" width="80" />
        <el-table-column prop="notify_type" label="通知方式" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.notify_type !== 'none'" size="small">{{ row.notify_type }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="toggleTask(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="last_exec_time" label="上次执行" width="160" />
        <el-table-column prop="next_exec_time" label="下次执行" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editTask(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteTask(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 用例集编辑对话框 -->
    <el-dialog v-model="suiteDialogVisible" :title="isEditSuite ? '编辑用例集' : '新建用例集'" width="800px">
      <el-form :model="suiteForm" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="suiteForm.suite_name" placeholder="输入用例集名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="suiteForm.suite_type" style="width: 100%">
            <el-option label="冒烟测试" value="smoke" />
            <el-option label="回归测试" value="regression" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="平台">
          <el-select v-model="suiteForm.platform" style="width: 100%">
            <el-option label="Web" value="web" />
            <el-option label="Android" value="android" />
            <el-option label="iOS" value="ios" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="suiteForm.description" type="textarea" :rows="2" />
        </el-form-item>

        <!-- 用例选择区域 -->
        <el-divider content-position="left">选择用例（按执行顺序排列）</el-divider>
        <el-form-item label="选择用例">
          <div class="case-selector">
            <div class="case-selector-header">
              <el-select
                v-model="selectedCaseId"
                placeholder="添加用例到列表"
                filterable
                style="width: 100%"
                @change="addCaseToSuite"
              >
                <el-option
                  v-for="c in availableCases"
                  :key="c.id"
                  :label="`${c.case_name} (${c.module || '无模块'})`"
                  :value="c.id"
                />
              </el-select>
            </div>
            <div class="case-list" v-if="selectedCases.length > 0">
              <div
                v-for="(c, index) in selectedCases"
                :key="c.id"
                class="case-item"
              >
                <div class="case-item-left">
                  <el-icon class="drag-handle"><Rank /></el-icon>
                  <el-tag size="small" type="primary">{{ index + 1 }}</el-tag>
                  <span class="case-name">{{ c.case_name }}</span>
                  <el-tag v-if="c.module" size="small" type="info">{{ c.module }}</el-tag>
                </div>
                <div class="case-item-right">
                  <el-button
                    type="primary"
                    link
                    size="small"
                    @click="moveCaseUp(index)"
                    :disabled="index === 0"
                  >
                    <el-icon><Top /></el-icon>
                  </el-button>
                  <el-button
                    type="primary"
                    link
                    size="small"
                    @click="moveCaseDown(index)"
                    :disabled="index === selectedCases.length - 1"
                  >
                    <el-icon><Bottom /></el-icon>
                  </el-button>
                  <el-button
                    type="danger"
                    link
                    size="small"
                    @click="removeCaseFromSuite(index)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
            <div class="case-empty" v-else>
              <el-empty description="暂未选择用例" :image-size="60" />
            </div>
          </div>
        </el-form-item>

        <el-divider content-position="left">前置步骤（套件执行前）</el-divider>
        <el-form-item label="前置步骤">
          <el-input
            v-model="suiteForm.setup_steps"
            type="textarea"
            :rows="3"
            placeholder='[{"keyword": "open_url", "params": {"url": "https://example.com"}}]'
          />
          <div class="step-hint">JSON 格式，每个步骤包含 keyword 和 params</div>
        </el-form-item>
        <el-divider content-position="left">后置步骤（套件执行后）</el-divider>
        <el-form-item label="后置步骤">
          <el-input
            v-model="suiteForm.teardown_steps"
            type="textarea"
            :rows="3"
            placeholder='[{"keyword": "screenshot", "params": {}}]'
          />
          <div class="step-hint">JSON 格式，每个步骤包含 keyword 和 params</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="suiteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSuite">保存</el-button>
      </template>
    </el-dialog>

    <!-- 定时任务编辑对话框 -->
    <el-dialog v-model="taskDialogVisible" :title="isEditTask ? '编辑定时任务' : '新建定时任务'" width="600px">
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务名称" required>
          <el-input v-model="taskForm.task_name" placeholder="输入任务名称" />
        </el-form-item>
        <el-form-item label="关联用例集" required>
          <el-select v-model="taskForm.suite_id" style="width: 100%">
            <el-option v-for="s in suites" :key="s.id" :label="s.suite_name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Cron表达式" required>
          <el-input v-model="taskForm.cron_expression" placeholder="例: 0 0 20 * * * (每天20:00)" />
          <div class="cron-hint">
            格式: 秒 分 时 日 月 周
          </div>
        </el-form-item>
        <el-form-item label="执行平台">
          <el-select v-model="taskForm.platform" style="width: 100%">
            <el-option label="Web" value="web" />
            <el-option label="Android" value="android" />
            <el-option label="iOS" value="ios" />
          </el-select>
        </el-form-item>
        <el-form-item label="通知方式">
          <el-select v-model="taskForm.notify_type" style="width: 100%">
            <el-option label="不通知" value="none" />
            <el-option label="飞书" value="feishu" />
            <el-option label="企业微信" value="wecom" />
            <el-option label="邮件" value="email" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTask">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Rank, Top, Bottom, Delete } from '@element-plus/icons-vue'
import { schedulerApi, execApi, caseApi } from '@/api'

const suites = ref([])
const tasks = ref([])
const allCases = ref([]) // 所有用例

const suiteDialogVisible = ref(false)
const isEditSuite = ref(false)
const suiteForm = ref({
  suite_name: '',
  suite_type: 'regression',
  platform: 'web',
  description: '',
  case_ids: [],
  setup_steps: '[]',
  teardown_steps: '[]',
})

// 已选择的用例列表（用于排序）
const selectedCases = ref([])
const selectedCaseId = ref(null) // 当前选择的用例ID

// 可用的用例（排除已选择的）
const availableCases = computed(() => {
  const selectedIds = selectedCases.value.map(c => c.id)
  return allCases.value.filter(c => !selectedIds.includes(c.id))
})

const taskDialogVisible = ref(false)
const isEditTask = ref(false)
const taskForm = ref({
  task_name: '',
  suite_id: '',
  cron_expression: '',
  platform: 'web',
  notify_type: 'none',
})

onMounted(() => {
  loadSuites()
  loadTasks()
  loadAllCases()
})

const loadSuites = async () => {
  try {
    suites.value = await schedulerApi.getSuites()
  } catch (error) {
    console.error('加载用例集失败:', error)
  }
}

const loadTasks = async () => {
  try {
    tasks.value = await schedulerApi.getTasks()
  } catch (error) {
    console.error('加载任务失败:', error)
  }
}

const loadAllCases = async () => {
  try {
    const result = await caseApi.getList({ page_size: 1000 })
    allCases.value = result?.list || []
  } catch (error) {
    console.error('加载用例列表失败:', error)
  }
}

const getSuiteTypeTag = (type) => {
  const map = { smoke: 'danger', regression: 'warning', custom: 'info' }
  return map[type] || ''
}

const createSuite = () => {
  isEditSuite.value = false
  suiteForm.value = {
    suite_name: '',
    suite_type: 'regression',
    platform: 'web',
    description: '',
    case_ids: [],
    setup_steps: '[]',
    teardown_steps: '[]',
  }
  selectedCases.value = []
  selectedCaseId.value = null
  suiteDialogVisible.value = true
}

const editSuite = async (row) => {
  isEditSuite.value = true
  suiteForm.value = { ...row }

  // 加载已选择的用例
  const caseIds = row.case_ids || []
  selectedCases.value = caseIds
    .map(id => allCases.value.find(c => c.id === id))
    .filter(Boolean)

  selectedCaseId.value = null
  suiteDialogVisible.value = true
}

// 添加用例到套件
const addCaseToSuite = (caseId) => {
  if (!caseId) return
  const caseItem = allCases.value.find(c => c.id === caseId)
  if (caseItem && !selectedCases.value.find(c => c.id === caseId)) {
    selectedCases.value.push(caseItem)
  }
  selectedCaseId.value = null
}

// 从套件中移除用例
const removeCaseFromSuite = (index) => {
  selectedCases.value.splice(index, 1)
}

// 上移用例
const moveCaseUp = (index) => {
  if (index === 0) return
  const temp = selectedCases.value[index]
  selectedCases.value[index] = selectedCases.value[index - 1]
  selectedCases.value[index - 1] = temp
}

// 下移用例
const moveCaseDown = (index) => {
  if (index === selectedCases.value.length - 1) return
  const temp = selectedCases.value[index]
  selectedCases.value[index] = selectedCases.value[index + 1]
  selectedCases.value[index + 1] = temp
}

const saveSuite = async () => {
  try {
    // 更新 case_ids
    suiteForm.value.case_ids = selectedCases.value.map(c => c.id)

    if (isEditSuite.value) {
      await schedulerApi.updateSuite(suiteForm.value.id, suiteForm.value)
    } else {
      await schedulerApi.createSuite(suiteForm.value)
    }
    ElMessage.success('保存成功')
    suiteDialogVisible.value = false
    loadSuites()
  } catch (error) {
    console.error('保存失败:', error)
  }
}

const deleteSuite = async (row) => {
  await ElMessageBox.confirm('确定删除该用例集？', '提示', { type: 'warning' })
  try {
    await schedulerApi.deleteSuite(row.id)
    ElMessage.success('删除成功')
    loadSuites()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const runSuite = async (row) => {
  try {
    await ElMessageBox.confirm('确定执行该用例集？', '提示')
    const result = await execApi.runSuite(row.id, { platform: row.platform })
    ElMessage.success(`任务已创建: ${result.task_id}`)
  } catch (error) {
    console.error('执行失败:', error)
  }
}

const createTask = () => {
  isEditTask.value = false
  taskForm.value = {
    task_name: '',
    suite_id: '',
    cron_expression: '',
    platform: 'web',
    notify_type: 'none',
  }
  taskDialogVisible.value = true
}

const editTask = (row) => {
  isEditTask.value = true
  taskForm.value = { ...row }
  taskDialogVisible.value = true
}

const saveTask = async () => {
  try {
    if (isEditTask.value) {
      await schedulerApi.updateTask(taskForm.value.id, taskForm.value)
    } else {
      await schedulerApi.createTask(taskForm.value)
    }
    ElMessage.success('保存成功')
    taskDialogVisible.value = false
    loadTasks()
  } catch (error) {
    console.error('保存失败:', error)
  }
}

const deleteTask = async (row) => {
  await ElMessageBox.confirm('确定删除该定时任务？', '提示', { type: 'warning' })
  try {
    await schedulerApi.deleteTask(row.id)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const toggleTask = async (row) => {
  try {
    await schedulerApi.toggleTask(row.id)
    ElMessage.success('状态更新成功')
  } catch (error) {
    row.status = row.status === 1 ? 0 : 1
  }
}
</script>

<style scoped>
.scheduler-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cron-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.step-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

:deep(.el-divider__text) {
  font-size: 12px;
  color: #909399;
}

/* 用例选择器样式 */
.case-selector {
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.case-selector-header {
  padding: 12px;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.case-list {
  max-height: 300px;
  overflow-y: auto;
}

.case-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #ebeef5;
  transition: background-color 0.2s;
}

.case-item:hover {
  background-color: #f5f7fa;
}

.case-item:last-child {
  border-bottom: none;
}

.case-item-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.drag-handle {
  cursor: grab;
  color: #909399;
  font-size: 16px;
}

.drag-handle:active {
  cursor: grabbing;
}

.case-name {
  font-size: 14px;
  color: #303133;
}

.case-item-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.case-empty {
  padding: 20px;
}
</style>
