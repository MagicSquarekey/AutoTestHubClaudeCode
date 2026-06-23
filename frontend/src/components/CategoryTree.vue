<!--
  分类树组件 / Category tree component
  @Function: 显示和管理多级分类树 / Display and manage multi-level category tree
-->
<template>
  <div class="category-tree">
    <!-- 操作栏 -->
    <div class="tree-actions">
      <el-button type="primary" size="small" :icon="Plus" @click="handleCreateRoot">
        新建分类
      </el-button>
      <el-button size="small" :icon="Refresh" @click="loadTree">
        刷新
      </el-button>
    </div>

    <!-- 树形结构 -->
    <el-tree
      ref="treeRef"
      :data="treeData"
      :props="treeProps"
      node-key="id"
      default-expand-all
      highlight-current
      :expand-on-click-node="false"
      @node-click="handleNodeClick"
      @node-contextmenu="handleContextMenu"
    >
      <template #default="{ node, data }">
        <div class="tree-node">
          <div class="node-content">
            <el-icon><Folder /></el-icon>
            <span class="node-label">{{ data.name }}</span>
            <el-tag v-if="data.task_count" size="small" type="info" class="node-count">
              {{ data.task_count }}
            </el-tag>
          </div>
          <div class="node-actions">
            <el-button
              type="primary"
              link
              size="small"
              @click.stop="handleEdit(data)"
            >
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click.stop="handleDelete(data)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
    </el-tree>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
    >
      <div class="menu-item" @click="handleCreateChild">
        <el-icon><Plus /></el-icon> 新建子分类
      </div>
      <div class="menu-item" @click="handleEdit(contextMenu.data)">
        <el-icon><Edit /></el-icon> 编辑
      </div>
      <div class="menu-item" @click="handleMove(contextMenu.data)">
        <el-icon><Rank /></el-icon> 移动
      </div>
      <div class="menu-item danger" @click="handleDelete(contextMenu.data)">
        <el-icon><Delete /></el-icon> 删除
      </div>
    </div>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑分类' : '新建分类'"
      width="400px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入分类名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
            maxlength="500"
          />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="formData.sort_order" :min="0" :max="9999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 移动对话框 -->
    <el-dialog v-model="moveDialogVisible" title="移动分类" width="400px">
      <el-form label-width="80px">
        <el-form-item label="目标位置">
          <el-tree-select
            v-model="moveTargetId"
            :data="treeData"
            :props="{ value: 'id', label: 'name', children: 'children' }"
            placeholder="选择目标父分类（留空移到根级别）"
            clearable
            check-strictly
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmMove">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Refresh, Folder, Rank } from '@element-plus/icons-vue'
import { categoryApi } from '@/api'

const emit = defineEmits(['select', 'change'])

// 树形数据
const treeRef = ref(null)
const treeData = ref([])
const treeProps = {
  children: 'children',
  label: 'name',
}

// 对话框状态
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const parentId = ref(null)
const formRef = ref(null)

// 表单数据
const formData = ref({
  name: '',
  description: '',
  sort_order: 0,
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' },
  ],
}

// 移动对话框状态
const moveDialogVisible = ref(false)
const moveTargetId = ref(null)
const moveData = ref(null)

// 右键菜单状态
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  data: null,
})

onMounted(() => {
  loadTree()
  // 点击其他地方关闭右键菜单
  document.addEventListener('click', closeContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
})

// 加载分类树
const loadTree = async () => {
  try {
    treeData.value = await categoryApi.getTree()
  } catch (error) {
    console.error('加载分类树失败:', error)
  }
}

// 节点点击
const handleNodeClick = (data) => {
  emit('select', data)
}

// 右键菜单
const handleContextMenu = (event, data) => {
  event.preventDefault()
  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    data: data,
  }
}

const closeContextMenu = () => {
  contextMenu.value.visible = false
}

// 新建根分类
const handleCreateRoot = () => {
  isEdit.value = false
  editId.value = null
  parentId.value = null
  resetForm()
  dialogVisible.value = true
}

// 新建子分类
const handleCreateChild = () => {
  isEdit.value = false
  editId.value = null
  parentId.value = contextMenu.value.data?.id || null
  resetForm()
  dialogVisible.value = true
  closeContextMenu()
}

// 编辑分类
const handleEdit = (data) => {
  isEdit.value = true
  editId.value = data.id
  parentId.value = data.parent_id
  formData.value = {
    name: data.name,
    description: data.description || '',
    sort_order: data.sort_order || 0,
  }
  dialogVisible.value = true
  closeContextMenu()
}

// 删除分类
const handleDelete = async (data) => {
  closeContextMenu()
  await ElMessageBox.confirm(`确定删除分类"${data.name}"？`, '提示', { type: 'warning' })
  try {
    await categoryApi.delete(data.id)
    ElMessage.success('删除成功')
    loadTree()
    emit('change')
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 移动分类
const handleMove = (data) => {
  moveData.value = data
  moveTargetId.value = data.parent_id
  moveDialogVisible.value = true
  closeContextMenu()
}

const confirmMove = async () => {
  try {
    await categoryApi.move(moveData.value.id, moveTargetId.value)
    ElMessage.success('移动成功')
    moveDialogVisible.value = false
    loadTree()
    emit('change')
  } catch (error) {
    console.error('移动失败:', error)
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      const data = {
        ...formData.value,
        parent_id: parentId.value,
      }
      if (isEdit.value) {
        await categoryApi.update(editId.value, data)
        ElMessage.success('更新成功')
      } else {
        await categoryApi.create(data)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadTree()
      emit('change')
    } catch (error) {
      console.error('提交失败:', error)
    }
  })
}

// 重置表单
const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    sort_order: 0,
  }
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
</script>

<style scoped>
.category-tree {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tree-actions {
  display: flex;
  gap: 8px;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-label {
  font-size: 14px;
}

.node-count {
  margin-left: 4px;
}

.node-actions {
  display: none;
}

.tree-node:hover .node-actions {
  display: flex;
}

.context-menu {
  position: fixed;
  z-index: 1000;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 4px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
}

.menu-item:hover {
  background: #ecf5ff;
  color: #409eff;
}

.menu-item.danger {
  color: #f56c6c;
}

.menu-item.danger:hover {
  background: #fef0f0;
}
</style>
