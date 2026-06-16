<template>
  <div class="scheduler-page">
    <!-- 用例集管理 -->
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
            {{ row.case_ids?.length || 0 }}
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
    <el-dialog v-model="suiteDialogVisible" :title="isEditSuite ? '编辑用例集' : '新建用例集'" width="600px">
      <el-form :model="suiteForm" label-width="80px">
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { schedulerApi, execApi } from '@/api'

const suites = ref([])
const tasks = ref([])

const suiteDialogVisible = ref(false)
const isEditSuite = ref(false)
const suiteForm = ref({
  suite_name: '',
  suite_type: 'regression',
  platform: 'web',
  description: '',
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
  }
  suiteDialogVisible.value = true
}

const editSuite = (row) => {
  isEditSuite.value = true
  suiteForm.value = { ...row }
  suiteDialogVisible.value = true
}

const saveSuite = async () => {
  try {
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
</style>
