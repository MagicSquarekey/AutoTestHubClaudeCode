<!--
  菜单配置页面 / Menu Config Page
  @Function: 管理侧边栏菜单的显示和排序 / Manage sidebar menu display and sorting
-->
<template>
  <div class="menu-config-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span>菜单配置</span>
            <el-tag type="info" size="small" style="margin-left: 12px">拖拽调整顺序</el-tag>
          </div>
          <div class="header-right">
            <el-button @click="resetConfig">重置默认</el-button>
            <el-button type="primary" @click="saveConfig" :loading="saving">
              <el-icon><Check /></el-icon>
              保存配置
            </el-button>
          </div>
        </div>
      </template>

      <div class="config-hint">
        <el-icon><InfoFilled /></el-icon>
        <span>配置侧边栏菜单的显示顺序和是否可见。隐藏的菜单将不会在侧边栏显示，但可以通过 URL 直接访问。拖拽行来调整顺序。</span>
      </div>

      <div class="menu-list" v-loading="loading">
        <draggable
          v-model="menus"
          item-key="path"
          handle=".drag-handle"
          ghost-class="ghost"
          @start="dragging = true"
          @end="dragging = false"
        >
          <template #item="{ element, index }">
            <div
              class="menu-item"
              :class="{ 'menu-item-hidden': !element.visible }"
            >
              <div class="menu-item-left">
                <el-icon class="drag-handle"><Rank /></el-icon>
                <el-tag size="small" type="primary">{{ index + 1 }}</el-tag>
                <el-icon :size="18"><component :is="element.icon" /></el-icon>
                <span class="menu-title">{{ element.title }}</span>
                <el-tag v-if="!element.visible" size="small" type="info">已隐藏</el-tag>
              </div>
              <div class="menu-item-right">
                <el-switch
                  v-model="element.visible"
                  active-text="显示"
                  inactive-text="隐藏"
                  style="margin-right: 16px"
                />
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="moveMenuUp(index)"
                  :disabled="index === 0"
                >
                  <el-icon><Top /></el-icon>
                </el-button>
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="moveMenuDown(index)"
                  :disabled="index === menus.length - 1"
                >
                  <el-icon><Bottom /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
        </draggable>
      </div>

      <div class="config-actions">
        <el-button @click="resetConfig">重置默认</el-button>
        <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, InfoFilled, Rank, Top, Bottom } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import { systemApi } from '@/api'

const loading = ref(false)
const saving = ref(false)
const dragging = ref(false)
const menus = ref([])

// 默认菜单配置
const defaultMenus = [
  { path: "", name: "Dashboard", title: "仪表盘", icon: "Odometer", visible: true, sort_order: 0 },
  { path: "case", name: "TestCase", title: "用例管理", icon: "Document", visible: true, sort_order: 1 },
  { path: "module", name: "Module", title: "模块管理", icon: "Folder", visible: true, sort_order: 2 },
  { path: "tag", name: "Tag", title: "标签管理", icon: "PriceTag", visible: true, sort_order: 3 },
  { path: "element", name: "Element", title: "元素管理", icon: "Pointer", visible: true, sort_order: 4 },
  { path: "execution", name: "Execution", title: "执行控制", icon: "VideoPlay", visible: true, sort_order: 5 },
  { path: "report", name: "Report", title: "测试报告", icon: "DataAnalysis", visible: true, sort_order: 6 },
  { path: "device", name: "Device", title: "设备管理", icon: "Monitor", visible: true, sort_order: 7 },
  { path: "scheduler", name: "Scheduler", title: "任务调度", icon: "Timer", visible: true, sort_order: 8 },
  { path: "settings", name: "Settings", title: "系统设置", icon: "Setting", visible: true, sort_order: 9 },
  { path: "menu-config", name: "MenuConfig", title: "菜单配置", icon: "Menu", visible: true, sort_order: 10 },
  { path: "record", name: "Record", title: "页面录制", icon: "VideoCamera", visible: true, sort_order: 11 },
]

// 加载菜单配置
const loadConfig = async () => {
  loading.value = true
  try {
    const result = await systemApi.getMenuConfig()
    if (result?.menus) {
      menus.value = result.menus
      // 确保菜单配置项本身也被包含在列表中
      if (!menus.value.find(m => m.path === 'menu-config')) {
        menus.value.push({
          path: 'menu-config',
          name: 'MenuConfig',
          title: '菜单配置',
          icon: 'Menu',
          visible: true,
          sort_order: menus.value.length,
        })
      }
    } else {
      menus.value = [...defaultMenus]
    }
  } catch (error) {
    console.error('加载菜单配置失败:', error)
    menus.value = [...defaultMenus]
  } finally {
    loading.value = false
  }
}

// 保存配置
const saveConfig = async () => {
  saving.value = true
  try {
    // 更新 sort_order
    const configData = {
      menus: menus.value.map((menu, index) => ({
        ...menu,
        sort_order: index,
      })),
    }
    await systemApi.updateMenuConfig(configData)
    ElMessage.success('菜单配置已保存，刷新页面后生效')
  } catch (error) {
    console.error('保存配置失败:', error)
  } finally {
    saving.value = false
  }
}

// 重置为默认配置
const resetConfig = async () => {
  await ElMessageBox.confirm('确定重置为默认菜单配置？', '提示', { type: 'warning' })
  menus.value = [...defaultMenus]
  ElMessage.success('已重置为默认配置，请点击保存')
}

// 上移菜单
const moveMenuUp = (index) => {
  if (index === 0) return
  const temp = menus.value[index]
  menus.value[index] = menus.value[index - 1]
  menus.value[index - 1] = temp
}

// 下移菜单
const moveMenuDown = (index) => {
  if (index === menus.value.length - 1) return
  const temp = menus.value[index]
  menus.value[index] = menus.value[index + 1]
  menus.value[index + 1] = temp
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.menu-config-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  background: #f4f4f5;
  border-radius: 4px;
  color: #909399;
  font-size: 14px;
}

.menu-list {
  min-height: 200px;
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  margin-bottom: 8px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  transition: all 0.2s;
}

.menu-item:hover {
  background: #f5f7fa;
  border-color: #409eff;
}

.menu-item-hidden {
  opacity: 0.6;
  background: #fafafa;
}

.menu-item-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.drag-handle {
  cursor: grab;
  color: #909399;
  font-size: 18px;
}

.drag-handle:active {
  cursor: grabbing;
}

.menu-title {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.menu-item-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.ghost {
  opacity: 0.5;
  background: #c8ebfb;
  border: 1px dashed #409eff;
}
</style>
