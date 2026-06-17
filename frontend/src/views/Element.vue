<!--
  元素管理页面 / Element management page
  @Function: 元素的增删改查、多端定位符管理、健康巡检 / CRUD, multi-platform locator management, health check for elements
-->
<template>
  <div class="element-page">
    <!-- 操作栏：新建、导入、导出、健康巡检 / Action bar: create, import, export, health check -->
    <el-card shadow="never" class="action-bar">
      <div class="action-left">
        <el-button type="primary" :icon="Plus" @click="handleCreate">新建元素</el-button>
        <el-button :icon="Upload" @click="handleImport">导入</el-button>
        <el-button :icon="Download" :disabled="!selectedElements.length" @click="handleExport">导出</el-button>
        <el-button type="danger" :icon="Delete" :disabled="!selectedElements.length" @click="handleBatchDelete">
          批量删除
        </el-button>
        <el-button :icon="CircleCheck" @click="handleHealthCheck">健康巡检</el-button>
      </div>
      <div class="action-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索元素名称"
          :prefix-icon="Search"
          clearable
          style="width: 200px"
          @input="handleSearch"
        />
        <el-select v-model="filterPage" placeholder="所属页面" clearable style="width: 120px" @change="loadData">
          <el-option v-for="p in pages" :key="p" :label="p" :value="p" />
        </el-select>
        <el-select v-model="filterModule" placeholder="所属模块" clearable style="width: 120px" @change="loadData">
          <el-option v-for="m in modules" :key="m" :label="m" :value="m" />
        </el-select>
      </div>
    </el-card>

    <!-- 元素列表 -->
    <el-card shadow="never">
      <el-table
        v-loading="loading"
        :data="elementList"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="elem_name" label="元素名称" min-width="150" />
        <el-table-column prop="page_name" label="所属页面" width="120" />
        <el-table-column prop="module" label="所属模块" width="100" />
        <el-table-column label="定位方式" width="150">
          <template #default="{ row }">
            <el-tag v-for="loc in row.locators?.slice(0, 2)" :key="loc.locate_type" size="small" class="locator-tag">
              {{ loc.locate_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="健康度" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="row.health_rate"
              :color="row.health_rate >= 80 ? '#67c23a' : row.health_rate >= 50 ? '#e6a23c' : '#f56c6c'"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column prop="quote_count" label="引用次数" width="80" />
        <el-table-column prop="update_time" label="更新时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link size="small" @click="handlePick(row)">拾取</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- 元素编辑对话框 -->
    <el-dialog v-model="editDialogVisible" :title="isEdit ? '编辑元素' : '新建元素'" width="600px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="元素名称" required>
          <el-input v-model="editForm.elem_name" placeholder="输入元素名称" />
        </el-form-item>
        <el-form-item label="所属页面">
          <el-input v-model="editForm.page_name" placeholder="输入页面名称" />
        </el-form-item>
        <el-form-item label="所属模块">
          <el-input v-model="editForm.module" placeholder="输入模块名称" />
        </el-form-item>
        <el-form-item label="定位符">
          <div class="locator-list">
            <div v-for="(loc, index) in editForm.locators" :key="index" class="locator-item">
              <el-select v-model="loc.platform" style="width: 100px">
                <el-option label="Web" value="web" />
                <el-option label="Android" value="android" />
                <el-option label="iOS" value="ios" />
              </el-select>
              <el-select v-model="loc.locate_type" style="width: 120px">
                <el-option label="XPath" value="xpath" />
                <el-option label="ID" value="id" />
                <el-option label="CSS" value="css" />
                <el-option label="Accessibility" value="accessibility" />
                <el-option label="OCR" value="ocr" />
                <el-option label="图像" value="image" />
                <el-option label="坐标" value="coordinate" />
              </el-select>
              <el-input v-model="loc.locate_value" placeholder="定位值" style="flex: 1" />
              <el-input-number v-model="loc.priority" :min="1" :max="10" style="width: 100px" />
              <el-button :icon="Delete" @click="editForm.locators.splice(index, 1)" type="danger" />
            </div>
            <el-button :icon="Plus" @click="addLocator">添加定位符</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 健康巡检对话框 -->
    <el-dialog v-model="healthDialogVisible" title="元素健康巡检" width="600px">
      <div v-if="healthResult">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="总元素数">{{ healthResult.total }}</el-descriptions-item>
          <el-descriptions-item label="健康率">{{ healthResult.health_rate }}%</el-descriptions-item>
          <el-descriptions-item label="健康元素">{{ healthResult.healthy }}</el-descriptions-item>
          <el-descriptions-item label="异常元素">{{ healthResult.unhealthy }}</el-descriptions-item>
        </el-descriptions>
        <el-table :data="healthResult.details" style="margin-top: 16px" max-height="300">
          <el-table-column prop="elem_name" label="元素名称" />
          <el-table-column prop="health_rate" label="健康度" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_healthy ? 'success' : 'danger'">{{ row.health_rate }}%</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="success_count" label="成功次数" width="80" />
          <el-table-column prop="fail_count" label="失败次数" width="80" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, Delete, Search, CircleCheck } from '@element-plus/icons-vue'
import { elementApi } from '@/api'

// 列表状态 / List state
const loading = ref(false)
const elementList = ref([])
const selectedElements = ref([])
const pages = ref([])
const modules = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const searchKeyword = ref('')
const filterPage = ref('')
const filterModule = ref('')

const editDialogVisible = ref(false)
const isEdit = ref(false)
const editForm = ref({
  elem_name: '',
  page_name: '',
  module: '',
  locators: [],
})

const healthDialogVisible = ref(false)
const healthResult = ref(null)

onMounted(() => {
  loadData()
  loadPages()
  loadModules()
})

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value,
      page_name: filterPage.value,
      module: filterModule.value,
    }
    const result = await elementApi.getList(params)
    elementList.value = result.list
    total.value = result.total
  } catch (error) {
    console.error('加载元素失败:', error)
  } finally {
    loading.value = false
  }
}

const loadPages = async () => {
  try {
    pages.value = await elementApi.getPages()
  } catch (error) {
    console.error('加载页面失败:', error)
  }
}

const loadModules = async () => {
  try {
    modules.value = await elementApi.getModules()
  } catch (error) {
    console.error('加载模块失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const handleSelectionChange = (selection) => {
  selectedElements.value = selection
}

const handleCreate = () => {
  isEdit.value = false
  editForm.value = {
    elem_name: '',
    page_name: '',
    module: '',
    locators: [{ platform: 'web', locate_type: 'xpath', locate_value: '', priority: 1 }],
  }
  editDialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editForm.value = {
    ...row,
    locators: row.locators || [],
  }
  editDialogVisible.value = true
}

const addLocator = () => {
  editForm.value.locators.push({
    platform: 'web',
    locate_type: 'xpath',
    locate_value: '',
    priority: editForm.value.locators.length + 1,
  })
}

const handleSave = async () => {
  try {
    if (isEdit.value) {
      await elementApi.update(editForm.value.id, editForm.value)
    } else {
      await elementApi.create(editForm.value)
    }
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('保存失败:', error)
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该元素？', '提示', { type: 'warning' })
  try {
    await elementApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const handleBatchDelete = async () => {
  await ElMessageBox.confirm(`确定删除选中的 ${selectedElements.value.length} 个元素？`, '提示', { type: 'warning' })
  try {
    const ids = selectedElements.value.map(e => e.id)
    await elementApi.batchDelete(ids)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const handleHealthCheck = async () => {
  try {
    healthResult.value = await elementApi.healthCheck()
    healthDialogVisible.value = true
  } catch (error) {
    console.error('巡检失败:', error)
  }
}

const handlePick = (row) => {
  ElMessage.info('元素拾取功能开发中')
}

const handleImport = () => {
  ElMessage.info('导入功能开发中')
}

const handleExport = async () => {
  try {
    const ids = selectedElements.value.map(e => e.id)
    const data = await elementApi.export(ids)
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `elements_${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
  }
}
</script>

<style scoped>
.element-page {
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

.locator-tag {
  margin-right: 4px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.locator-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.locator-item {
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>
