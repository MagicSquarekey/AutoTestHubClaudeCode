<!--
  用例编辑页面 / Test case edit page
  @Function: 可视化拖拽编排测试步骤，配置关键字参数 / Visual drag-and-drop test step editing with keyword configuration
-->
<template>
  <div class="case-edit">
    <!-- 顶部操作栏：返回、用例名称、调试、保存 / Top bar: back, case name, debug, save -->
    <el-card shadow="never" class="top-bar">
      <div class="top-left">
        <el-button :icon="Back" @click="router.back()">返回</el-button>
        <el-divider direction="vertical" />
        <el-input
          v-model="formData.case_name"
          placeholder="请输入用例名称*"
          style="width: 300px"
        />
      </div>
      <div class="top-right">
        <el-button @click="handleDebug">调试运行</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </div>
    </el-card>

    <!-- 主体内容 -->
    <div class="edit-content">
      <!-- 左侧：关键字库 -->
      <el-card shadow="never" class="keyword-panel">
        <template #header>
          <span>关键字库</span>
        </template>
        <el-input
          v-model="keywordSearch"
          placeholder="搜索关键字"
          :prefix-icon="Search"
          clearable
          class="keyword-search"
        />
        <el-collapse v-model="activeKeywordGroup">
          <el-collapse-item title="通用操作" name="common">
            <div class="keyword-list">
              <div
                v-for="kw in commonKeywords"
                :key="kw.name"
                class="keyword-item"
                draggable="true"
                @dragstart="handleDragStart($event, kw)"
              >
                <el-icon><component :is="kw.icon" /></el-icon>
                <span>{{ kw.name }}</span>
              </div>
            </div>
          </el-collapse-item>
          <el-collapse-item title="Web操作" name="web">
            <div class="keyword-list">
              <div
                v-for="kw in webKeywords"
                :key="kw.name"
                class="keyword-item"
                draggable="true"
                @dragstart="handleDragStart($event, kw)"
              >
                <el-icon><component :is="kw.icon" /></el-icon>
                <span>{{ kw.name }}</span>
              </div>
            </div>
          </el-collapse-item>
          <el-collapse-item title="断言验证" name="assert">
            <div class="keyword-list">
              <div
                v-for="kw in assertKeywords"
                :key="kw.name"
                class="keyword-item"
                draggable="true"
                @dragstart="handleDragStart($event, kw)"
              >
                <el-icon><component :is="kw.icon" /></el-icon>
                <span>{{ kw.name }}</span>
              </div>
            </div>
          </el-collapse-item>
          <el-collapse-item title="流程控制" name="flow">
            <div class="keyword-list">
              <div
                v-for="kw in flowKeywords"
                :key="kw.name"
                class="keyword-item"
                draggable="true"
                @dragstart="handleDragStart($event, kw)"
              >
                <el-icon><component :is="kw.icon" /></el-icon>
                <span>{{ kw.name }}</span>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-card>

      <!-- 中间：步骤画布 -->
      <el-card shadow="never" class="step-canvas">
        <template #header>
          <div class="canvas-header">
            <span>测试步骤</span>
            <el-button-group>
              <el-button size="small" :icon="Plus" @click="addStep">添加步骤</el-button>
              <el-button size="small" :icon="Sort" @click="toggleSortMode">排序</el-button>
            </el-button-group>
          </div>
        </template>
        <div
          class="step-list"
          @dragover.prevent
          @drop="handleDrop"
        >
          <div
            v-for="(step, index) in formData.steps"
            :key="step.id"
            :class="['step-item', { active: activeStepId === step.id, disabled: step.disabled }]"
            @click="selectStep(step)"
          >
            <div class="step-header">
              <div class="step-index">{{ index + 1 }}</div>
              <div class="step-info">
                <span class="step-name">{{ step.name || step.keyword }}</span>
                <span class="step-desc" v-if="step.params?.element">元素: {{ step.params.element }}</span>
              </div>
              <div class="step-actions">
                <el-button-group size="small">
                  <el-button :icon="Top" @click.stop="moveStep(index, -1)" :disabled="index === 0" />
                  <el-button :icon="Bottom" @click.stop="moveStep(index, 1)" :disabled="index === formData.steps.length - 1" />
                  <el-button :icon="CopyDocument" @click.stop="copyStep(index)" />
                  <el-button :icon="Delete" @click.stop="removeStep(index)" type="danger" />
                </el-button-group>
                <el-switch
                  v-model="step.disabled"
                  size="small"
                  @click.stop
                  style="margin-left: 8px"
                />
              </div>
            </div>
            <div class="step-detail" v-if="step.params">
              <el-tag v-for="(value, key) in step.params" :key="key" size="small" class="param-tag">
                {{ key }}: {{ value }}
              </el-tag>
            </div>
          </div>

          <!-- 空状态 -->
          <el-empty v-if="!formData.steps.length" description="拖拽关键字到此处添加步骤" />
        </div>
      </el-card>

      <!-- 右侧：步骤编辑面板 -->
      <el-card shadow="never" class="param-panel">
        <template #header>
          <span>步骤配置</span>
        </template>
        <template v-if="activeStep">
          <el-form label-position="top" size="small">
            <el-form-item label="关键字">
              <el-input v-model="activeStep.keyword" disabled />
            </el-form-item>
            <el-form-item label="步骤名称">
              <el-input v-model="activeStep.name" placeholder="输入步骤名称" />
            </el-form-item>
            <el-form-item label="关联元素" v-if="['click', 'input_text', 'clear_input', 'hover', 'select', 'upload_file', 'wait_for_element', 'assert_element_exists'].includes(activeStep.keyword)">
              <el-input
                v-model="activeStep.params.element"
                placeholder="输入CSS选择器"
                clearable
              />
            </el-form-item>
            <el-form-item label="输入值" v-if="['input_text', 'set_value'].includes(activeStep.keyword)">
              <el-input v-model="activeStep.params.value" placeholder="输入值" />
            </el-form-item>
            <el-form-item label="URL" v-if="activeStep.keyword === 'open_url'">
              <el-input v-model="activeStep.params.url" placeholder="输入URL" />
            </el-form-item>
            <el-form-item label="等待时间(秒)" v-if="activeStep.keyword === 'wait'">
              <el-input-number v-model="activeStep.params.timeout" :min="1" :max="60" />
            </el-form-item>
            <!-- 验证码识别参数配置 -->
            <template v-if="activeStep.keyword === 'solve_captcha'">
              <el-form-item label="验证码图片选择器">
                <el-input v-model="activeStep.params.captcha_selector" placeholder="如: img.captcha" />
              </el-form-item>
              <el-form-item label="验证码输入框选择器">
                <el-input v-model="activeStep.params.input_selector" placeholder="如: input[name='captcha']" />
              </el-form-item>
              <el-form-item label="验证码长度">
                <el-input-number v-model="activeStep.params.expected_length" :min="1" :max="10" />
              </el-form-item>
              <el-form-item label="最大重试次数">
                <el-input-number v-model="activeStep.params.max_retries" :min="1" :max="10" />
              </el-form-item>
              <el-form-item label="识别失败策略">
                <el-select v-model="activeStep.params.on_fail" style="width: 100%">
                  <el-option label="终止用例" value="stop" />
                  <el-option label="跳过继续" value="skip" />
                  <el-option label="人工介入" value="manual" />
                </el-select>
              </el-form-item>
            </template>
            <el-form-item label="超时时间(秒)">
              <el-input-number v-model="activeStep.timeout" :min="1" :max="120" :default="30" />
            </el-form-item>
            <el-form-item label="重试次数">
              <el-input-number v-model="activeStep.retry_count" :min="0" :max="10" />
            </el-form-item>
            <el-form-item label="失败策略">
              <el-select v-model="activeStep.on_error" style="width: 100%">
                <el-option label="终止用例" value="stop" />
                <el-option label="继续执行" value="continue" />
                <el-option label="重试后继续" value="retry_continue" />
              </el-select>
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="activeStep.remark" type="textarea" :rows="2" placeholder="输入备注" />
            </el-form-item>
          </el-form>
        </template>
        <el-empty v-else description="选择步骤进行编辑" />
      </el-card>
    </div>

    <!-- 调试运行对话框 / Debug run dialog -->
    <el-dialog
      v-model="debugDialogVisible"
      title="调试运行"
      width="700px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="debugRunning ? false : true"
    >
      <div class="debug-content">
        <!-- 进度条 / Progress bar -->
        <div class="debug-progress" v-if="debugRunning && !waitingCaptcha">
          <el-progress
            :percentage="debugTotalSteps > 0 ? Math.round((debugCurrentStep / debugTotalSteps) * 100) : 0"
            :format="() => `${debugCurrentStep}/${debugTotalSteps}`"
          />
          <div class="debug-status">正在执行步骤 {{ debugCurrentStep }}/{{ debugTotalSteps }}...</div>
        </div>

        <!-- 人工输入验证码区域 / Manual captcha input area -->
        <div class="captcha-manual-input" v-if="waitingCaptcha">
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

        <!-- 完成状态 / Completion status -->
        <div class="debug-complete" v-else-if="debugResults.length > 0">
          <el-alert
            :title="debugError ? '执行失败' : '执行完成'"
            :type="debugError ? 'error' : 'success'"
            :description="debugError || `共执行 ${debugResults.length} 个步骤`"
            show-icon
            :closable="false"
          />
        </div>

        <!-- 执行结果列表 / Result list -->
        <div class="debug-results">
          <el-table :data="debugResults" stripe size="small" max-height="400">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="keyword" label="关键字" width="120" />
            <el-table-column prop="message" label="执行结果" show-overflow-tooltip />
            <el-table-column prop="duration" label="耗时(秒)" width="80" />
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.success ? 'success' : 'danger'" size="small">
                  {{ row.success ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button v-if="debugRunning" type="danger" @click="handleStopDebug">停止运行</el-button>
          <el-button v-else @click="debugDialogVisible = false">关闭</el-button>
          <el-button v-if="!debugRunning && debugResults.length > 0" type="primary" @click="handleDebug">重新运行</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Search, Plus, Delete, Top, Bottom, CopyDocument, Sort } from '@element-plus/icons-vue'
import { caseApi, debugApi } from '@/api'

const router = useRouter()
const route = useRoute()

// 用例表单数据 / Case form data
const formData = ref({
  case_name: '',
  module: '',
  tags: [],
  priority: 'P0',
  platform: 'web',
  steps: [],
})

const activeStepId = ref(null)
const keywordSearch = ref('')
const activeKeywordGroup = ref(['common', 'web'])

const activeStep = computed(() => {
  return formData.value.steps.find(s => s.id === activeStepId.value)
})

// 调试运行状态变量
const debugDialogVisible = ref(false)
const debugRunning = ref(false)
const debugTaskId = ref(null)
const debugCurrentStep = ref(0)
const debugTotalSteps = ref(0)
const debugResults = ref([])
const debugError = ref(null)
const debugPollingTimer = ref(null)

// 验证码人工输入相关状态
const waitingCaptcha = ref(false)
const captchaScreenshot = ref(null)
const manualCaptchaText = ref('')
const submittingCaptcha = ref(false)

// 关键字库
const commonKeywords = [
  { name: '打开URL', keyword: 'open_url', icon: 'Link', params: { url: '' } },
  { name: '等待', keyword: 'wait', icon: 'Timer', params: { timeout: 5 } },
  { name: '等待元素', keyword: 'wait_for_element', icon: 'Timer', params: { element: '' } },
  { name: '截图', keyword: 'screenshot', icon: 'Camera', params: {} },
  { name: '执行JS', keyword: 'execute_js', icon: 'Document', params: { script: '' } },
]

const webKeywords = [
  { name: '点击元素', keyword: 'click', icon: 'Mouse', params: { element: '' } },
  { name: '输入文本', keyword: 'input_text', icon: 'Edit', params: { element: '', value: '' } },
  { name: '清空输入', keyword: 'clear_input', icon: 'Delete', params: { element: '' } },
  { name: '鼠标悬停', keyword: 'hover', icon: 'Pointer', params: { element: '' } },
  { name: '下拉选择', keyword: 'select', icon: 'ArrowDown', params: { element: '', value: '' } },
  { name: '上传文件', keyword: 'upload_file', icon: 'Upload', params: { element: '', file_path: '' } },
  { name: '切换iframe', keyword: 'switch_iframe', icon: 'Switch', params: { iframe: '' } },
  { name: '切换窗口', keyword: 'switch_window', icon: 'Monitor', params: { window_index: 0 } },
  { name: '识别验证码', keyword: 'solve_captcha', icon: 'Key', params: { captcha_selector: 'img.captcha', input_selector: "input[name='captcha']", expected_length: 4, max_retries: 3 } },
]

const assertKeywords = [
  { name: '断言文本', keyword: 'assert_text', icon: 'Check', params: { expected: '' } },
  { name: '断言元素存在', keyword: 'assert_element_exists', icon: 'CircleCheck', params: { element: '' } },
  { name: '断言URL', keyword: 'assert_url', icon: 'Link', params: { expected: '' } },
  { name: '断言标题', keyword: 'assert_title', icon: 'Document', params: { expected: '' } },
]

const flowKeywords = [
  { name: '条件分支', keyword: 'if_else', icon: 'Switch', params: { condition: '' } },
  { name: '循环', keyword: 'loop', icon: 'RefreshRight', params: { count: 1 } },
  { name: '调用公共关键字', keyword: 'call_keyword', icon: 'Connection', params: { keyword_name: '' } },
]

onMounted(async () => {
  const id = route.params.id
  if (id) {
    await loadCase(id)
  }
})
const loadCase = async (id) => {
  try {
    const data = await caseApi.getDetail(id)
    const steps = data.steps ? JSON.parse(data.steps) : []
    // 为没有ID的步骤补生成唯一ID
    steps.forEach((step, index) => {
      if (!step.id) {
        step.id = `step_loaded_${Date.now()}_${index}`
      }
    })
    formData.value = {
      ...data,
      steps,
    }
  } catch (error) {
    console.error('加载用例失败:', error)
  }
}

const handleDragStart = (event, keyword) => {
  event.dataTransfer.setData('keyword', JSON.stringify(keyword))
}

const handleDrop = (event) => {
  event.preventDefault()
  const data = event.dataTransfer.getData('keyword')
  if (data) {
    const keyword = JSON.parse(data)
    addStepFromKeyword(keyword)
  }
}

const addStepFromKeyword = (keyword) => {
  const step = {
    id: `step_${Date.now()}`,
    keyword: keyword.keyword,
    name: keyword.name,
    params: { ...keyword.params },
    timeout: 30,
    retry_count: 0,
    on_error: 'stop',
    disabled: false,
    remark: '',
  }
  formData.value.steps.push(step)
  activeStepId.value = step.id
}

const addStep = () => {
  addStepFromKeyword({
    name: '自定义步骤',
    keyword: 'custom',
    params: {},
  })
}

const selectStep = (step) => {
  activeStepId.value = step.id
}

const moveStep = (index, direction) => {
  const steps = formData.value.steps
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= steps.length) return
  [steps[index], steps[newIndex]] = [steps[newIndex], steps[index]]
}

const copyStep = (index) => {
  const step = formData.value.steps[index]
  const newStep = {
    ...JSON.parse(JSON.stringify(step)),
    id: `step_${Date.now()}`,
  }
  formData.value.steps.splice(index + 1, 0, newStep)
  activeStepId.value = newStep.id
}

const removeStep = (index) => {
  formData.value.steps.splice(index, 1)
  if (activeStepId.value === formData.value.steps[index]?.id) {
    activeStepId.value = null
  }
}

const toggleSortMode = () => {
  ElMessage.info('排序模式切换')
}

const handleSave = async () => {
  // 验证用例名称必填
  if (!formData.value.case_name || !formData.value.case_name.trim()) {
    ElMessage.warning('请输入用例名称')
    return
  }
  try {
    const data = {
      ...formData.value,
      steps: JSON.stringify(formData.value.steps),
    }
    if (route.params.id) {
      await caseApi.update(route.params.id, data)
    } else {
      await caseApi.create(data)
    }
    ElMessage.success('保存成功')
    router.back()
  } catch (error) {
    console.error('保存失败:', error)
  }
}

// 调试运行相关函数 / Debug run functions
const handleDebug = async () => {
  if (!route.params.id) {
    ElMessage.warning('请先保存用例')
    return
  }

  if (formData.value.steps.length === 0) {
    ElMessage.warning('请先添加测试步骤')
    return
  }

  // 重置状态
  debugRunning.value = true
  debugResults.value = []
  debugError.value = null
  debugCurrentStep.value = 0
  debugTotalSteps.value = formData.value.steps.length
  debugDialogVisible.value = true

  try {
    const res = await debugApi.startDebug({
      case_id: parseInt(route.params.id),
      browser_type: 'chromium',
      headless: false,
      timeout: 30,
    })
    debugTaskId.value = res.task_id
    // 开始轮询状态
    startDebugPolling()
  } catch (error) {
    console.error('启动调试失败:', error)
    debugRunning.value = false
    debugError.value = error.message || '启动调试失败'
  }
}

const startDebugPolling = () => {
  if (debugPollingTimer.value) {
    clearInterval(debugPollingTimer.value)
  }
  debugPollingTimer.value = setInterval(async () => {
    if (!debugTaskId.value) return

    try {
      const res = await debugApi.getDebugStatus(debugTaskId.value)
      debugCurrentStep.value = res.current_step
      debugResults.value = res.results || []

      // 检测是否需要人工输入验证码
      if (res.waiting_captcha && res.captcha_screenshot) {
        waitingCaptcha.value = true
        captchaScreenshot.value = res.captcha_screenshot
        // 不停止轮询，继续等待用户输入
      } else if (!res.waiting_captcha) {
        // 如果不再等待验证码，清除状态
        if (waitingCaptcha.value) {
          waitingCaptcha.value = false
          captchaScreenshot.value = null
          manualCaptchaText.value = ''
        }
      }

      if (res.status === 'completed' || res.status === 'failed' || res.status === 'stopped') {
        debugRunning.value = false
        waitingCaptcha.value = false
        if (res.error) {
          debugError.value = res.error
        }
        stopDebugPolling()
      }
    } catch (error) {
      console.error('获取调试状态失败:', error)
    }
  }, 1000)
}

const stopDebugPolling = () => {
  if (debugPollingTimer.value) {
    clearInterval(debugPollingTimer.value)
    debugPollingTimer.value = null
  }
}

const handleStopDebug = async () => {
  if (debugTaskId.value) {
    try {
      await debugApi.stopDebug(debugTaskId.value)
      debugRunning.value = false
      waitingCaptcha.value = false
      stopDebugPolling()
    } catch (error) {
      console.error('停止调试失败:', error)
    }
  }
}

// 提交人工验证码
const handleSubmitCaptcha = async () => {
  if (!manualCaptchaText.value || !manualCaptchaText.value.trim()) {
    ElMessage.warning('请输入验证码')
    return
  }

  submittingCaptcha.value = true
  try {
    await debugApi.submitCaptcha(debugTaskId.value, manualCaptchaText.value.trim())
    ElMessage.success('验证码已提交')
    // 清除输入状态
    waitingCaptcha.value = false
    captchaScreenshot.value = null
    manualCaptchaText.value = ''
  } catch (error) {
    console.error('提交验证码失败:', error)
    ElMessage.error('提交验证码失败: ' + (error.message || '未知错误'))
  } finally {
    submittingCaptcha.value = false
  }
}

// 组件卸载时清理轮询
onUnmounted(() => {
  stopDebugPolling()
})
</script>

<style scoped>
.case-edit {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: calc(100vh - 120px);
}

.top-bar :deep(.el-card__body) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.top-left,
.top-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.edit-content {
  flex: 1;
  display: flex;
  gap: 16px;
  overflow: hidden;
}

.keyword-panel {
  width: 240px;
  overflow-y: auto;
}

.keyword-search {
  margin-bottom: 12px;
}

.keyword-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.keyword-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: grab;
  transition: background-color 0.2s;
}

.keyword-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.step-canvas {
  flex: 1;
  overflow-y: auto;
}

.canvas-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-list {
  min-height: 300px;
}

.step-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.step-item:hover {
  border-color: #409eff;
}

.step-item.active {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.step-item.disabled {
  opacity: 0.5;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-index {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.step-info {
  flex: 1;
}

.step-name {
  font-weight: 500;
}

.step-desc {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.step-actions {
  display: flex;
  align-items: center;
}

.step-detail {
  margin-top: 8px;
  padding-left: 40px;
}

/* 修复长文本换行 / Fix long text wrapping */
.step-item .step-info,
.step-item .step-detail,
.param-tag,
.step-item .el-tag {
  word-break: break-all;
  white-space: pre-wrap;
  overflow-wrap: break-word;
}

.step-info {
  overflow: hidden;
}

/* 防止文本被意外选中 / Prevent text selection */
.step-item {
  user-select: none;
}

.step-item .step-desc,
.step-item .step-name,
.param-tag {
  user-select: text;
}

.param-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

.param-panel {
  width: 280px;
  overflow-y: auto;
}

/* 调试运行对话框样式 / Debug dialog styles */
.debug-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.debug-progress {
  text-align: center;
}

.debug-status {
  margin-top: 12px;
  color: #606266;
  font-size: 14px;
}

.debug-complete {
  margin-bottom: 16px;
}

.debug-results {
  max-height: 400px;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 验证码人工输入样式 / Manual captcha input styles */
.captcha-manual-input {
  padding: 16px;
  background-color: #fdf6ec;
  border-radius: 8px;
  border: 1px solid #e6a23c;
}

.captcha-preview {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.captcha-label {
  font-weight: 500;
  color: #606266;
}

.captcha-image {
  max-width: 200px;
  max-height: 80px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.captcha-loading {
  color: #909399;
  font-size: 14px;
}

.captcha-input-area {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>

