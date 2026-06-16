<template>
  <div class="case-edit">
    <!-- 顶部操作栏 -->
    <el-card shadow="never" class="top-bar">
      <div class="top-left">
        <el-button :icon="Back" @click="router.back()">返回</el-button>
        <el-divider direction="vertical" />
        <el-input
          v-model="formData.case_name"
          placeholder="用例名称"
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
            <el-form-item label="关联元素">
              <el-select
                v-model="activeStep.params.element"
                placeholder="选择元素"
                filterable
                clearable
                style="width: 100%"
              >
                <el-option label="元素1" value="elem1" />
                <el-option label="元素2" value="elem2" />
              </el-select>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Search, Plus, Delete, Top, Bottom, CopyDocument, Sort } from '@element-plus/icons-vue'
import { caseApi } from '@/api'

const router = useRouter()
const route = useRoute()

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

// 关键字库
const commonKeywords = [
  { name: '打开URL', keyword: 'open_url', icon: 'Link', params: { url: '' } },
  { name: '等待', keyword: 'wait', icon: 'Timer', params: { timeout: 5 } },
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
    formData.value = {
      ...data,
      steps: data.steps ? JSON.parse(data.steps) : [],
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

const handleDebug = () => {
  ElMessage.info('调试运行功能开发中')
}
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

.param-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

.param-panel {
  width: 280px;
  overflow-y: auto;
}
</style>
