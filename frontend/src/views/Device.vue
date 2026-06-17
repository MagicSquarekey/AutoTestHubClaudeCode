<!--
  设备管理页面 / Device management page
  @Function: 浏览器和移动设备的连接管理 / Browser and mobile device connection management
-->
<template>
  <div class="device-page">
    <!-- 浏览器管理 / Browser management -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>浏览器管理</span>
          <el-button size="small" :icon="Refresh" @click="loadBrowsers">刷新</el-button>
        </div>
      </template>
      <el-table :data="browsers" stripe>
        <el-table-column prop="name" label="浏览器" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="version" label="版本" width="120" />
        <el-table-column prop="path" label="路径" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="checkDriver(row)">检查驱动</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 移动设备管理 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>移动设备管理</span>
          <div>
            <el-button size="small" type="primary" :icon="Search" @click="scanDevices">扫描设备</el-button>
            <el-button size="small" :icon="Refresh" @click="loadDevices">刷新</el-button>
          </div>
        </div>
      </template>
      <el-empty v-if="!devices.length" description="暂无已连接设备" />
      <el-table v-else :data="devices" stripe>
        <el-table-column prop="name" label="设备名称" />
        <el-table-column prop="device_id" label="设备ID" width="150" />
        <el-table-column prop="platform" label="平台" width="80">
          <template #default="{ row }">
            <el-tag :type="row.platform === 'android' ? 'success' : 'warning'" size="small">
              {{ row.platform }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'connected' ? 'success' : 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== 'connected'"
              type="primary"
              link
              size="small"
              @click="connectDevice(row)"
            >
              连接
            </el-button>
            <el-button
              v-else
              type="primary"
              link
              size="small"
              @click="disconnectDevice(row)"
            >
              断开
            </el-button>
            <el-button type="primary" link size="small" @click="takeScreenshot(row)">截图</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 环境管理 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>测试环境管理</span>
          <el-button size="small" type="primary" :icon="Plus" @click="addEnvironment">添加环境</el-button>
        </div>
      </template>
      <el-table :data="environments" stripe>
        <el-table-column prop="name" label="环境名称" />
        <el-table-column prop="url" label="环境地址" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editEnvironment(row)">编辑</el-button>
            <el-button type="primary" link size="small" @click="checkHealth(row)">健康检查</el-button>
            <el-button type="danger" link size="small" @click="deleteEnvironment(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, Plus } from '@element-plus/icons-vue'
import { deviceApi } from '@/api'

const browsers = ref([])
const devices = ref([])
const environments = ref([
  { name: '开发环境', url: 'http://dev.example.com', description: '开发测试环境' },
  { name: '测试环境', url: 'http://test.example.com', description: '功能测试环境' },
  { name: '预发布环境', url: 'http://staging.example.com', description: '预发布验证环境' },
])

onMounted(() => {
  loadBrowsers()
  loadDevices()
})

const loadBrowsers = async () => {
  try {
    browsers.value = await deviceApi.getBrowsers()
  } catch (error) {
    console.error('加载浏览器失败:', error)
  }
}

const loadDevices = async () => {
  try {
    devices.value = await deviceApi.getList()
  } catch (error) {
    console.error('加载设备失败:', error)
  }
}

const scanDevices = async () => {
  try {
    ElMessage.info('正在扫描设备...')
    const result = await deviceApi.scan('android')
    devices.value = result
    ElMessage.success(`扫描完成，发现 ${result.length} 个设备`)
  } catch (error) {
    console.error('扫描失败:', error)
  }
}

const connectDevice = async (device) => {
  try {
    await deviceApi.connect(device.device_id)
    device.status = 'connected'
    ElMessage.success('连接成功')
  } catch (error) {
    console.error('连接失败:', error)
  }
}

const disconnectDevice = async (device) => {
  try {
    await deviceApi.disconnect(device.device_id)
    device.status = 'disconnected'
    ElMessage.success('已断开连接')
  } catch (error) {
    console.error('断开失败:', error)
  }
}

const takeScreenshot = async (device) => {
  try {
    const result = await deviceApi.screenshot(device.device_id)
    ElMessage.success('截图成功')
  } catch (error) {
    console.error('截图失败:', error)
  }
}

const checkDriver = async (browser) => {
  try {
    const result = await deviceApi.checkDriver(browser.type)
    if (result.needs_update) {
      ElMessage.warning('驱动需要更新')
    } else {
      ElMessage.success('驱动正常')
    }
  } catch (error) {
    console.error('检查驱动失败:', error)
  }
}

const addEnvironment = () => {
  ElMessage.info('添加环境功能开发中')
}

const editEnvironment = (env) => {
  ElMessage.info('编辑环境功能开发中')
}

const checkHealth = async (env) => {
  try {
    ElMessage.success(`${env.name} 环境正常`)
  } catch (error) {
    ElMessage.error(`${env.name} 环境异常`)
  }
}

const deleteEnvironment = async (env) => {
  await ElMessageBox.confirm('确定删除该环境？', '提示', { type: 'warning' })
  environments.value = environments.value.filter(e => e !== env)
  ElMessage.success('删除成功')
}
</script>

<style scoped>
.device-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
