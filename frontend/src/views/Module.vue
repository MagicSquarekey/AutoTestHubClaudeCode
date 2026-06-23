<!--
  模块管理页面 / Module management page
  @Function: 模块的增删改查、排序、统计 / CRUD, sorting, statistics for modules
-->
<template>
  <div class="module-page">
    <!-- 操作栏 / Action bar -->
    <el-card shadow="never" class="action-bar">
      <div class="action-left">
        <el-button type="primary" :icon="Plus" @click="handleCreate">新建模块</el-button>
      </div>
      <div class="action-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索模块名称"
          :prefix-icon="Search"
          clearable
          style="width: 200px"
          @input="handleSearch"
        />
      </div>
    </el-card>

    <!-- 模块列表 / Module list -->
    <el-card shadow="never">
      <el-table v-loading="loading" :data="moduleList" stripe>
        <el-table-column prop="name" label="模块名称" min-width="150">
          <template #default="{ row }">
            <el-link type="primary" @click="handleEdit(row)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="case_count" label="用例数量" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.case_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 / Pagination -->
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

    <!-- 新建/编辑弹窗 / Create/Edit dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑模块' : '新建模块'"
      width="500px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="模块名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入模块名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模块描述"
            maxlength="500"
          />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="formData.sort_order" :min="0" :max="9999" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { moduleApi } from '@/api'

// 列表状态 / List state
const loading = ref(false)
const moduleList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')

// 弹窗状态 / Dialog state
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

// 表单数据 / Form data
const formData = reactive({
  name: '',
  description: '',
  sort_order: 0,
  status: 1,
})

// 表单验证规则 / Form validation rules
const formRules = {
  name: [
    { required: true, message: '请输入模块名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' },
  ],
}

onMounted(() => {
  loadData()
})

// 加载数据 / Load data
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value,
    }
    const result = await moduleApi.getList(params)
    moduleList.value = result.list
    total.value = result.total
  } catch (error) {
    console.error('加载模块失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索 / Search
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 新建 / Create
const handleCreate = () => {
  isEdit.value = false
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

// 编辑 / Edit
const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  formData.name = row.name
  formData.description = row.description
  formData.sort_order = row.sort_order
  formData.status = row.status
  dialogVisible.value = true
}

// 删除 / Delete
const handleDelete = async (row) => {
  if (row.case_count > 0) {
    ElMessage.warning(`该模块下有 ${row.case_count} 个用例，请先移除用例的模块归属`)
    return
  }
  await ElMessageBox.confirm(`确定删除模块"${row.name}"？`, '提示', { type: 'warning' })
  try {
    await moduleApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 状态变更 / Status change
const handleStatusChange = async (row) => {
  try {
    await moduleApi.update(row.id, { status: row.status })
    ElMessage.success('状态更新成功')
  } catch (error) {
    row.status = row.status === 1 ? 0 : 1
    console.error('状态更新失败:', error)
  }
}

// 提交表单 / Submit form
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (isEdit.value) {
        await moduleApi.update(editId.value, formData)
        ElMessage.success('更新成功')
      } else {
        await moduleApi.create(formData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadData()
    } catch (error) {
      console.error('提交失败:', error)
    }
  })
}

// 重置表单 / Reset form
const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.sort_order = 0
  formData.status = 1
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
</script>

<style scoped>
.module-page {
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

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
