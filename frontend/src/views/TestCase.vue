<template>
  <div class="test-case">
    <!-- 操作栏 -->
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
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="row.priority === 'P0' ? 'danger' : row.priority === 'P1' ? 'warning' : 'info'" size="small">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="platform" label="平台" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" width="150">
          <template #default="{ row }">
            <el-tag v-for="tag in row.tags" :key="tag" size="small" class="tag-item">{{ tag }}</el-tag>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, Delete, Search } from '@element-plus/icons-vue'
import { caseApi, execApi } from '@/api'

const router = useRouter()

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

onMounted(() => {
  loadData()
  loadModules()
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
    modules.value = await caseApi.getModules()
  } catch (error) {
    console.error('加载模块失败:', error)
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
    const result = await execApi.run({
      case_ids: [row.id],
      platform: row.platform,
    })
    ElMessage.success(`任务已创建: ${result.task_id}`)
  } catch (error) {
    console.error('执行失败:', error)
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
</style>
