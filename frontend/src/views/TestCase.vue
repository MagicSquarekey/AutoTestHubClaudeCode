<!--
  用例管理页面 / Test case management page
  @Function: 用例的增删改查、导入导出、批量操作 / CRUD, import/export, batch operations for test cases
-->
<template>
  <div class="test-case">
    <!-- 操作栏：新建、导入、导出、搜索、筛选 / Action bar: create, import, export, search, filter -->
    <el-card shadow="never" class="action-bar">
      <div class="action-left">
        <el-button type="primary" :icon="Plus" @click="handleCreate">新建用例</el-button>
        <el-button :icon="Upload" @click="handleImport">导入</el-button>
        <el-button :icon="Download" :disabled="!selectedCases.length" @click="handleExport">导出</el-button>
        <el-button type="danger" :icon="Delete" :disabled="!selectedCases.length" @click="handleBatchDelete">
          批量删除
        </el-button>
      </div>
      <div class="action-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用例名称"
          :prefix-icon="Search"
          clearable
          style="width: 200px"
          @input="handleSearch"
        />
        <el-select v-model="filterModule" placeholder="所属模块" clearable style="width: 120px" @change="loadData">
          <el-option v-for="m in modules" :key="m" :label="m" :value="m" />
        </el-select>
        <el-select v-model="filterPriority" placeholder="优先级" clearable style="width: 100px" @change="loadData">
          <el-option label="P0" value="P0" />
          <el-option label="P1" value="P1" />
          <el-option label="P2" value="P2" />
        </el-select>
        <el-select v-model="filterPlatform" placeholder="平台" clearable style="width: 100px" @change="loadData">
          <el-option label="Web" value="web" />
          <el-option label="Android" value="android" />
          <el-option label="iOS" value="ios" />
          <el-option label="小程序" value="miniapp" />
        </el-select>
      </div>
    </el-card>

    <!-- 用例列表 -->
    <el-card shadow="never">
      <el-table
        v-loading="loading"
        :data="caseList"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="case_name" label="用例名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="handleEdit(row)">{{ row.case_name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="120">
          <template #default="{ row }">
            <el-select
              v-model="row.module"
              size="small"
              filterable
              allow-create
              placeholder="选择模块"
              @change="(val) => handleFieldChange(row, 'module', val)"
              @visible-change="(val) => { if (!val) loadData() }"
            >
              <el-option v-for="m in modules" :key="m" :label="m" :value="m" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-select
              v-model="row.priority"
              size="small"
              @change="(val) => handleFieldChange(row, 'priority', val)"
            >
              <el-option label="P0" value="P0">
                <el-tag type="danger" size="small">P0</el-tag>
              </el-option>
              <el-option label="P1" value="P1">
                <el-tag type="warning" size="small">P1</el-tag>
              </el-option>
              <el-option label="P2" value="P2">
                <el-tag type="info" size="small">P2</el-tag>
              </el-option>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="platform" label="平台" width="100">
          <template #default="{ row }">
            <el-select
              v-model="row.platform"
              size="small"
              @change="(val) => handleFieldChange(row, 'platform', val)"
            >
              <el-option
                v-for="item in platformOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" width="200">
          <template #default="{ row }">
            <el-select
              v-model="row.tags"
              size="small"
              multiple
              filterable
              allow-create
              collapse-tags
              collapse-tags-tooltip
              placeholder="选择标签"
              @change="(val) => handleFieldChange(row, 'tags', val)"
            >
              <el-option v-for="tag in tags" :key="tag" :label="tag" :value="tag" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="70" />
        <el-table-column prop="update_time" label="更新时间" width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link size="small" @click="handleCopy(row)">复制</el-button>
            <el-button type="primary" link size="small" @click="handleRun(row)">执行</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入用例" width="500px">
      <el-upload
        drag
        :auto-upload="false"
        :limit="1"
        accept=".json"
        :on-change="handleFileChange"
      >
        <el-icon :size="48"><Upload /></el-icon>
        <div>将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">仅支持 JSON 格式文件</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmImport">确定导入</el-button>
      </template>
    </el-dialog>

    <!-- 执行状态对话框 -->
    <el-dialog v-model="execDialogVisible" title="执行状态" width="600px" :close-on-click-modal="false">
      <!-- 执行进度 -->
      <div v-if="execRunning && !waitingCaptcha" class="exec-progress">
        <el-progress :percentage="execProgress" :format="() => `${execCurrentStep}/${execTotalSteps}`" />
        <div class="exec-status">正在执行中...</div>
      </div>

      <!-- 执行结果 -->
      <div v-if="execResults.length > 0 && !waitingCaptcha" class="exec-results">
        <el-table :data="execResults" size="small" max-height="300">
          <el-table-column prop="case_name" label="用例" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'passed' ? 'success' : 'danger'" size="small">
                {{ row.status === 'passed' ? '通过' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 执行错误 -->
      <el-alert v-if="execError && !waitingCaptcha" :title="execError" type="error" show-icon style="margin-top: 16px;" />

      <!-- 人工输入验证码区域 -->
      <div v-if="waitingCaptcha" class="captcha-manual-input">
        <el-alert
          title="验证码识别失败，请手动输入"
          type="warning"
          description="OCR 自动识别未能成功，请查看下方验证码图片并手动输入"
          show-icon
          :closable="false"
          style="margin-bottom: 16px"
        />
        <div class="captcha-preview">
          <div class="captcha-label">验证码图片：</div>
          <img
            v-if="captchaScreenshot"
            :src="`data:image/png;base64,${captchaScreenshot}`"
            class="captcha-image"
            alt="验证码"
          />
          <div v-else class="captcha-loading">加载中...</div>
        </div>
        <div class="captcha-input-area">
          <el-input
            v-model="manualCaptchaText"
            placeholder="请输入验证码"
            clearable
            @keyup.enter="handleSubmitCaptcha"
            style="width: 200px"
          />
          <el-button type="primary" @click="handleSubmitCaptcha" :loading="submittingCaptcha">
            提交
          </el-button>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button v-if="execRunning" type="danger" @click="handleStopExec">停止执行</el-button>
          <el-button v-else @click="execDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, Delete, Search } from '@element-plus/icons-vue'
import { caseApi, execApi, moduleApi, tagApi } from '@/api'

const router = useRouter()

// 列表状态 / List state
const loading = ref(false)
const caseList = ref([])
const selectedCases = ref([])
const modules = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const searchKeyword = ref('')
const filterModule = ref('')
const filterPriority = ref('')
const filterPlatform = ref('')

const importDialogVisible = ref(false)
const importFile = ref(null)

// 执行状态相关 / Execution status
const execDialogVisible = ref(false)
const execRunning = ref(false)
const execTaskId = ref(null)
const execCurrentStep = ref(0)
const execTotalSteps = ref(0)
const execProgress = ref(0)
const execResults = ref([])
const execError = ref(null)
const execPollingTimer = ref(null)

// 验证码人工输入相关 / Manual captcha input
const waitingCaptcha = ref(false)
const captchaScreenshot = ref(null)
const manualCaptchaText = ref('')
const submittingCaptcha = ref(false)

// 行内编辑选项 / Inline edit options
const tags = ref([])
const platformOptions = [
  { label: 'Web', value: 'web' },
  { label: 'Android', value: 'android' },
  { label: 'iOS', value: 'ios' },
  { label: '小程序', value: 'miniapp' },
]

onMounted(() => {
  loadData()
  loadModules()
  loadTags()
})

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value,
      module: filterModule.value,
      priority: filterPriority.value,
      platform: filterPlatform.value,
    }
    const result = await caseApi.getList(params)
    caseList.value = result.list
    total.value = result.total
  } catch (error) {
    console.error('加载用例失败:', error)
  } finally {
    loading.value = false
  }
}

const loadModules = async () => {
  try {
    const result = await moduleApi.getAll()
    modules.value = result.map(m => m.name)
  } catch (error) {
    // 新接口失败时，降级使用旧接口 / Fallback to old API if new one fails
    try {
      modules.value = await caseApi.getModules()
    } catch (e) {
      console.error('加载模块失败:', e)
    }
  }
}

const loadTags = async () => {
  try {
    const result = await tagApi.getAll()
    tags.value = result.map(t => t.name)
  } catch (error) {
    // 新接口失败时，降级使用旧接口 / Fallback to old API if new one fails
    try {
      tags.value = await caseApi.getTags()
    } catch (e) {
      console.error('加载标签失败:', e)
    }
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

const handleCreate = () => {
  router.push('/case/edit')
}

const handleEdit = (row) => {
  router.push(`/case/edit/${row.id}`)
}

const handleCopy = async (row) => {
  try {
    await caseApi.copy(row.id)
    ElMessage.success('复制成功')
    loadData()
  } catch (error) {
    console.error('复制失败:', error)
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该用例？', '提示', { type: 'warning' })
  try {
    await caseApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const handleBatchDelete = async () => {
  await ElMessageBox.confirm(`确定删除选中的 ${selectedCases.value.length} 条用例？`, '提示', { type: 'warning' })
  try {
    const ids = selectedCases.value.map(c => c.id)
    await caseApi.batchDelete(ids)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const handleStatusChange = async (row) => {
  try {
    await caseApi.update(row.id, { status: row.status })
    ElMessage.success('状态更新成功')
  } catch (error) {
    row.status = row.status === 1 ? 0 : 1
  }
}

// 行内编辑字段更新 / Inline field update
const handleFieldChange = async (row, field, oldValue) => {
  try {
    await caseApi.update(row.id, { [field]: row[field] })
    ElMessage.success('更新成功')
  } catch (error) {
    row[field] = oldValue
    console.error('更新失败:', error)
  }
}

const handleImport = () => {
  importFile.value = null
  importDialogVisible.value = true
}

const handleFileChange = (file) => {
  importFile.value = file.raw
}

const confirmImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  try {
    await caseApi.import(importFile.value)
    ElMessage.success('导入成功')
    importDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('导入失败:', error)
  }
}

const handleExport = async () => {
  try {
    const ids = selectedCases.value.map(c => c.id)
    const data = await caseApi.export(ids)
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `cases_${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
  }
}

const handleRun = async (row) => {
  try {
    await ElMessageBox.confirm('确定执行该用例？', '提示')

    // 重置状态
    execRunning.value = true
    execResults.value = []
    execError.value = null
    execCurrentStep.value = 0
    execTotalSteps.value = 1
    execProgress.value = 0
    waitingCaptcha.value = false
    captchaScreenshot.value = null
    manualCaptchaText.value = ''
    execDialogVisible.value = true

    const result = await execApi.run({
      case_ids: [row.id],
      platform: row.platform,
    })
    execTaskId.value = result.task_id
    ElMessage.success(`任务已创建: ${result.task_id}`)

    // 开始轮询状态
    startExecPolling()
  } catch (error) {
    console.error('执行失败:', error)
    execRunning.value = false
  }
}

const startExecPolling = () => {
  if (execPollingTimer.value) {
    clearInterval(execPollingTimer.value)
  }
  execPollingTimer.value = setInterval(async () => {
    if (!execTaskId.value) return

    try {
      const res = await execApi.getStatus(execTaskId.value)
      console.log('任务状态:', res)  // 调试日志
      console.log('waiting_captcha:', res.waiting_captcha)  // 调试日志
      console.log('captcha_screenshot:', res.captcha_screenshot ? '有截图' : '无截图')  // 调试日志

      execCurrentStep.value = res.current_case_index + 1
      execTotalSteps.value = res.case_count || 1
      execProgress.value = Math.round((execCurrentStep.value / execTotalSteps.value) * 100)
      execResults.value = res.results || []

      // 检测是否需要人工输入验证码
      if (res.waiting_captcha && res.captcha_screenshot) {
        console.log('设置验证码弹窗')  // 调试日志
        waitingCaptcha.value = true
        captchaScreenshot.value = res.captcha_screenshot
      } else if (!res.waiting_captcha) {
        // 如果不再等待验证码，清除状态
        if (waitingCaptcha.value) {
          waitingCaptcha.value = false
          captchaScreenshot.value = null
          manualCaptchaText.value = ''
        }
      }

      if (res.status === 'completed' || res.status === 'failed' || res.status === 'stopped') {
        execRunning.value = false
        waitingCaptcha.value = false
        if (res.status === 'failed') {
          execError.value = '执行失败'
        }
        stopExecPolling()
      }
    } catch (error) {
      console.error('获取执行状态失败:', error)
    }
  }, 1000)
}

const stopExecPolling = () => {
  if (execPollingTimer.value) {
    clearInterval(execPollingTimer.value)
    execPollingTimer.value = null
  }
}

const handleStopExec = async () => {
  if (!execTaskId.value) return
  try {
    await execApi.control(execTaskId.value, 'stop')
    ElMessage.success('已停止执行')
    execRunning.value = false
    waitingCaptcha.value = false
    stopExecPolling()
  } catch (error) {
    console.error('停止执行失败:', error)
  }
}

const handleSubmitCaptcha = async () => {
  if (!manualCaptchaText.value) {
    ElMessage.warning('请输入验证码')
    return
  }
  submittingCaptcha.value = true
  try {
    await execApi.submitCaptcha(execTaskId.value, manualCaptchaText.value)
    ElMessage.success('验证码已提交')
    waitingCaptcha.value = false
    captchaScreenshot.value = null
    manualCaptchaText.value = ''
  } catch (error) {
    console.error('提交验证码失败:', error)
    ElMessage.error('提交验证码失败')
  } finally {
    submittingCaptcha.value = false
  }
}
</script>

<style scoped>
.test-case {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-bar :deep(.el-card__body) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.action-left,
.action-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-item {
  margin-right: 4px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* 行内编辑下拉框样式 / Inline edit select styles */
:deep(.el-table .el-select) {
  width: 100%;
}

:deep(.el-table .el-select .el-input__wrapper) {
  box-shadow: none !important;
}

:deep(.el-table .el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--el-border-color-hover) inset !important;
}

:deep(.el-table .el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--el-color-primary) inset !important;
}

/* 执行状态对话框样式 */
.exec-content {
  min-height: 100px;
}

.exec-progress {
  margin-bottom: 16px;
}

.exec-status {
  margin-top: 8px;
  color: #909399;
  font-size: 14px;
}

.exec-results {
  margin-top: 16px;
}

/* 验证码输入区域样式 */
.captcha-manual-input {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.captcha-preview {
  margin-bottom: 16px;
}

.captcha-label {
  margin-bottom: 8px;
  font-weight: 500;
}

.captcha-image {
  max-width: 300px;
  max-height: 100px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.captcha-loading {
  color: #909399;
  font-style: italic;
}

.captcha-input-area {
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>
