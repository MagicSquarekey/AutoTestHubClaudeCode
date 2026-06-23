<!--
  标签管理页面 / Tag management page
  @Function: 标签的增删改查、颜色设置、使用统计 / CRUD, color settings, usage statistics for tags
-->
<template>
  <div class="tag-page">
    <!-- 操作栏 / Action bar -->
    <el-card shadow="never" class="action-bar">
      <div class="action-left">
        <el-button type="primary" :icon="Plus" @click="handleCreate">新建标签</el-button>
      </div>
      <div class="action-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索标签名称"
          :prefix-icon="Search"
          clearable
          style="width: 200px"
          @input="handleSearch"
        />
      </div>
    </el-card>

    <!-- 标签列表 / Tag list -->
    <el-card shadow="never">
      <el-table v-loading="loading" :data="tagList" stripe>
        <el-table-column prop="name" label="标签名称" min-width="150">
          <template #default="{ row }">
            <el-tag :color="row.color" effect="dark" style="border: none;">{{ row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="usage_count" label="使用次数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.usage_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="color" label="颜色" width="100" align="center">
          <template #default="{ row }">
            <div class="color-preview" :style="{ backgroundColor: row.color }"></div>
          </template>
        </el-table-column>
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
      :title="isEdit ? '编辑标签' : '新建标签'"
      width="500px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入标签名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="颜色" prop="color">
          <el-color-picker v-model="formData.color" :predefine="predefineColors" />
          <span class="color-value">{{ formData.color }}</span>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入标签描述"
            maxlength="200"
          />
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
import { tagApi } from '@/api'

// 预定义颜色 / Predefined colors
const predefineColors = [
  '#409EFF',
  '#67C23A',
  '#E6A23C',
  '#F56C6C',
  '#909399',
  '#00CED1',
  '#FF69B4',
  '#8B4513',
]

// 列表状态 / List state
const loading = ref(false)
const tagList = ref([])
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
  color: '#409EFF',
  description: '',
  status: 1,
})

// 表单验证规则 / Form validation rules
const formRules = {
  name: [
    { required: true, message: '请输入标签名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' },
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
    const result = await tagApi.getList(params)
    tagList.value = result.list
    total.value = result.total
  } catch (error) {
    console.error('加载标签失败:', error)
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
  formData.color = row.color
  formData.description = row.description
  formData.status = row.status
  dialogVisible.value = true
}

// 删除 / Delete
const handleDelete = async (row) => {
  if (row.usage_count > 0) {
    ElMessage.warning(`该标签被 ${row.usage_count} 个用例使用，请先移除用例中的该标签`)
    return
  }
  await ElMessageBox.confirm(`确定删除标签"${row.name}"？`, '提示', { type: 'warning' })
  try {
    await tagApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 状态变更 / Status change
const handleStatusChange = async (row) => {
  try {
    await tagApi.update(row.id, { status: row.status })
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
        await tagApi.update(editId.value, formData)
        ElMessage.success('更新成功')
      } else {
        await tagApi.create(formData)
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
  formData.color = '#409EFF'
  formData.description = ''
  formData.status = 1
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
</script>

<style scoped>
.tag-page {
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

.color-preview {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  margin: 0 auto;
}

.color-value {
  margin-left: 10px;
  color: #606266;
  font-size: 14px;
}
</style>
