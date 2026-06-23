<!--
  系统设置页面 / System settings page
  @Function: 配置执行参数、AI 设置、全局变量、系统信息 / Configure execution params, AI settings, global variables, system info
-->
<template>
  <div class="settings-page">
    <!-- 执行配置 / Execution configuration -->
    <el-card shadow="never">
      <template #header>
        <span>执行配置</span>
      </template>
      <el-form :model="execConfig" label-width="120px">
        <el-form-item label="默认超时时间">
          <el-input-number v-model="execConfig.DEFAULT_TIMEOUT" :min="5" :max="120" />
          <span class="form-hint">秒</span>
        </el-form-item>
        <el-form-item label="默认重试次数">
          <el-input-number v-model="execConfig.DEFAULT_RETRY_COUNT" :min="0" :max="10" />
        </el-form-item>
        <el-form-item label="最大并行任务">
          <el-input-number v-model="execConfig.MAX_PARALLEL_TASKS" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="启用截图">
          <el-switch v-model="execConfig.ENABLE_SCREENSHOT" />
        </el-form-item>
        <el-form-item label="启用录屏">
          <el-switch v-model="execConfig.ENABLE_VIDEO" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveExecConfig">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 全局变量 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>全局变量</span>
          <el-button size="small" type="primary" :icon="Plus" @click="addVariable">添加变量</el-button>
        </div>
      </template>
      <el-table :data="variables" stripe>
        <el-table-column prop="var_name" label="变量名" width="150" />
        <el-table-column prop="var_value" label="变量值" />
        <el-table-column prop="var_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.var_type === 'encrypted' ? 'danger' : 'info'" size="small">
              {{ row.var_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="scope" label="作用域" width="100" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editVariable(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteVariable(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 第三方配置 -->
    <el-card shadow="never">
      <template #header>
        <span>第三方配置</span>
      </template>
      <el-form :model="thirdPartyConfig" label-width="120px">
        <el-divider content-position="left">消息通知</el-divider>
        <el-form-item label="飞书Webhook">
          <el-input v-model="thirdPartyConfig.FEISHU_WEBHOOK" placeholder="输入飞书机器人Webhook地址" />
        </el-form-item>
        <el-form-item label="企微Webhook">
          <el-input v-model="thirdPartyConfig.WECOM_WEBHOOK" placeholder="输入企业微信机器人Webhook地址" />
        </el-form-item>
        <el-form-item label="邮件SMTP">
          <el-input v-model="thirdPartyConfig.EMAIL_SMTP_HOST" placeholder="SMTP服务器地址" style="width: 200px" />
          <el-input-number v-model="thirdPartyConfig.EMAIL_SMTP_PORT" :min="1" :max="65535" style="width: 120px; margin-left: 8px" />
        </el-form-item>
        <el-form-item label="发件人">
          <el-input v-model="thirdPartyConfig.EMAIL_SENDER" placeholder="发件人邮箱" />
        </el-form-item>
        <el-form-item label="邮箱密码">
          <el-input v-model="thirdPartyConfig.EMAIL_PASSWORD" type="password" placeholder="邮箱密码或授权码" show-password />
        </el-form-item>

        <el-divider content-position="left">AI配置</el-divider>
        <el-form-item label="AI API Key">
          <el-input v-model="thirdPartyConfig.AI_API_KEY" type="password" placeholder="输入AI API密钥" show-password />
        </el-form-item>
        <el-form-item label="AI API URL">
          <el-input v-model="thirdPartyConfig.AI_API_URL" placeholder="输入AI API地址" />
        </el-form-item>
        <el-form-item label="AI模型">
          <el-input v-model="thirdPartyConfig.AI_MODEL" placeholder="输入模型名称" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveThirdPartyConfig">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- OCR / 验证码识别配置 -->
    <el-card shadow="never">
      <template #header>
        <span>OCR / 验证码识别配置</span>
      </template>
      <el-form :model="ocrConfig" label-width="160px">
        <el-form-item label="OCR 引擎">
          <el-select v-model="ocrConfig.OCR_ENGINE" style="width: 100%">
            <el-option label="PaddleOCR (推荐)" value="paddleocr" />
            <el-option label="Tesseract" value="tesseract" />
            <el-option label="自动选择" value="auto" />
          </el-select>
        </el-form-item>
        <el-form-item label="默认最大重试次数">
          <el-input-number v-model="ocrConfig.OCR_MAX_RETRIES" :min="1" :max="10" />
          <span class="form-hint">次</span>
        </el-form-item>
        <el-form-item label="失败后自动重试">
          <el-switch v-model="ocrConfig.OCR_AUTO_RETRY" />
          <span class="form-hint">识别失败时自动重新截图并重试</span>
        </el-form-item>
        <el-form-item label="失败提示后重试">
          <el-switch v-model="ocrConfig.OCR_RETRY_AFTER_HINT" />
          <span class="form-hint">点击"知道了"提示后重新输入验证码</span>
        </el-form-item>
        <el-form-item label="提示弹窗选择器">
          <el-input v-model="ocrConfig.OCR_HINT_SELECTOR" placeholder="如: .el-message-box .el-button--primary" />
          <span class="form-hint">识别失败提示弹窗中确认按钮的 CSS 选择器</span>
        </el-form-item>
        <el-form-item label="重试间隔 (秒)">
          <el-input-number v-model="ocrConfig.OCR_RETRY_INTERVAL" :min="1" :max="30" />
          <span class="form-hint">每次重试之间的等待时间</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveOcrConfig">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据管理 -->
    <el-card shadow="never">
      <template #header>
        <span>数据管理</span>
      </template>
      <el-space>
        <el-button type="primary" :icon="Download" @click="handleBackup">数据备份</el-button>
        <el-button :icon="Upload" @click="handleRestore">数据恢复</el-button>
        <el-button type="warning" :icon="Delete" @click="handleClearCache">清理缓存</el-button>
      </el-space>
      <div v-if="systemInfo" class="system-info">
        <el-descriptions :column="2" border style="margin-top: 16px">
          <el-descriptions-item label="应用版本">{{ systemInfo.app_version }}</el-descriptions-item>
          <el-descriptions-item label="Python版本">{{ systemInfo.python_version }}</el-descriptions-item>
          <el-descriptions-item label="操作系统">{{ systemInfo.os }}</el-descriptions-item>
          <el-descriptions-item label="CPU核心数">{{ systemInfo.cpu_count }}</el-descriptions-item>
          <el-descriptions-item label="总内存">{{ systemInfo.memory_total_gb }} GB</el-descriptions-item>
          <el-descriptions-item label="可用内存">{{ systemInfo.memory_available_gb }} GB</el-descriptions-item>
          <el-descriptions-item label="总磁盘">{{ systemInfo.disk_total_gb }} GB</el-descriptions-item>
          <el-descriptions-item label="可用磁盘">{{ systemInfo.disk_free_gb }} GB</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- 变量编辑对话框 -->
    <el-dialog v-model="varDialogVisible" :title="isEditVar ? '编辑变量' : '添加变量'" width="500px">
      <el-form :model="varForm" label-width="80px">
        <el-form-item label="变量名" required>
          <el-input v-model="varForm.var_name" placeholder="输入变量名" />
        </el-form-item>
        <el-form-item label="变量值" required>
          <el-input v-model="varForm.var_value" :type="varForm.var_type === 'encrypted' ? 'password' : 'text'" placeholder="输入变量值" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="varForm.var_type" style="width: 100%">
            <el-option label="字符串" value="string" />
            <el-option label="数字" value="number" />
            <el-option label="布尔" value="boolean" />
            <el-option label="加密" value="encrypted" />
          </el-select>
        </el-form-item>
        <el-form-item label="作用域">
          <el-select v-model="varForm.scope" style="width: 100%">
            <el-option label="全局" value="global" />
            <el-option label="模块" value="module" />
            <el-option label="用例" value="case" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="varForm.description" placeholder="输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="varDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveVariable">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Upload, Delete } from '@element-plus/icons-vue'
import { systemApi } from '@/api'

const execConfig = ref({
  DEFAULT_TIMEOUT: 30,
  DEFAULT_RETRY_COUNT: 3,
  MAX_PARALLEL_TASKS: 5,
  ENABLE_SCREENSHOT: true,
  ENABLE_VIDEO: false,
})

const thirdPartyConfig = ref({
  FEISHU_WEBHOOK: '',
  WECOM_WEBHOOK: '',
  EMAIL_SMTP_HOST: '',
  EMAIL_SMTP_PORT: 465,
  EMAIL_SENDER: '',
  EMAIL_PASSWORD: '',
  AI_API_KEY: '',
  AI_API_URL: '',
  AI_MODEL: 'gpt-3.5-turbo',
})

const ocrConfig = ref({
  OCR_ENGINE: 'paddleocr',
  OCR_MAX_RETRIES: 3,
  OCR_AUTO_RETRY: true,
  OCR_RETRY_AFTER_HINT: true,
  OCR_HINT_SELECTOR: '.el-message-box .el-button--primary',
  OCR_RETRY_INTERVAL: 3,
})

const variables = ref([])
const systemInfo = ref(null)

const varDialogVisible = ref(false)
const isEditVar = ref(false)
const varForm = ref({
  var_name: '',
  var_value: '',
  var_type: 'string',
  scope: 'global',
  description: '',
})

onMounted(async () => {
  await loadConfigs()
  await loadVariables()
  await loadSystemInfo()
})

const loadConfigs = async () => {
  try {
    const configs = await systemApi.getConfigs()
    const configMap = {}
    configs.forEach(c => {
      configMap[c.config_key] = c.config_value
    })
    // 更新执行配置
    Object.keys(execConfig.value).forEach(key => {
      if (configMap[key] !== undefined) {
        execConfig.value[key] = configMap[key]
      }
    })
    // 更新第三方配置
    Object.keys(thirdPartyConfig.value).forEach(key => {
      if (configMap[key] !== undefined) {
        thirdPartyConfig.value[key] = configMap[key]
      }
    })
    // 更新OCR配置
    Object.keys(ocrConfig.value).forEach(key => {
      if (configMap[key] !== undefined) {
        ocrConfig.value[key] = configMap[key]
      }
    })
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

const loadVariables = async () => {
  try {
    variables.value = await systemApi.getVariables()
  } catch (error) {
    console.error('加载变量失败:', error)
  }
}

const loadSystemInfo = async () => {
  try {
    systemInfo.value = await systemApi.getSystemInfo()
  } catch (error) {
    console.error('加载系统信息失败:', error)
  }
}

const saveExecConfig = async () => {
  try {
    await systemApi.batchUpdateConfigs(execConfig.value)
    ElMessage.success('配置保存成功')
  } catch (error) {
    console.error('保存配置失败:', error)
  }
}

const saveThirdPartyConfig = async () => {
  try {
    await systemApi.batchUpdateConfigs(thirdPartyConfig.value)
    ElMessage.success('配置保存成功')
  } catch (error) {
    console.error('保存配置失败:', error)
  }
}

const saveOcrConfig = async () => {
  try {
    await systemApi.batchUpdateConfigs(ocrConfig.value)
    ElMessage.success('OCR配置保存成功')
  } catch (error) {
    console.error('保存OCR配置失败:', error)
  }
}

const addVariable = () => {
  isEditVar.value = false
  varForm.value = {
    var_name: '',
    var_value: '',
    var_type: 'string',
    scope: 'global',
    description: '',
  }
  varDialogVisible.value = true
}

const editVariable = (row) => {
  isEditVar.value = true
  varForm.value = { ...row }
  varDialogVisible.value = true
}

const saveVariable = async () => {
  try {
    if (isEditVar.value) {
      await systemApi.updateVariable(varForm.value.id, varForm.value)
    } else {
      await systemApi.createVariable(varForm.value)
    }
    ElMessage.success('保存成功')
    varDialogVisible.value = false
    loadVariables()
  } catch (error) {
    console.error('保存失败:', error)
  }
}

const deleteVariable = async (row) => {
  await ElMessageBox.confirm('确定删除该变量？', '提示', { type: 'warning' })
  try {
    await systemApi.deleteVariable(row.id)
    ElMessage.success('删除成功')
    loadVariables()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const handleBackup = async () => {
  try {
    const result = await systemApi.backup()
    ElMessage.success(`备份成功: ${result.backup_path}`)
  } catch (error) {
    console.error('备份失败:', error)
  }
}

const handleRestore = async () => {
  ElMessage.info('请选择备份文件进行恢复')
}

const handleClearCache = async () => {
  await ElMessageBox.confirm('确定清理缓存？', '提示', { type: 'warning' })
  try {
    const result = await systemApi.clearCache()
    ElMessage.success(`缓存清理完成，释放 ${result.cleaned_size_mb} MB`)
  } catch (error) {
    console.error('清理失败:', error)
  }
}
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-hint {
  margin-left: 8px;
  color: #909399;
}

.system-info {
  margin-top: 16px;
}
</style>
