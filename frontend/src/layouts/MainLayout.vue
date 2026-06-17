<!--
  主布局组件 / Main layout component
  @Function: 侧边栏导航 + 顶部面包屑 + 内容区 / Sidebar navigation + breadcrumb header + content area
-->
<template>
  <el-container class="layout-container">
    <!-- 侧边栏导航 / Sidebar navigation -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo" @click="router.push('/')">
        <el-icon :size="24"><Cpu /></el-icon>
        <span v-show="!isCollapse" class="logo-text">AutoTest Hub</span>
      </div>
      <el-menu
        :default-active="currentRoute"
        :collapse="isCollapse"
        router
        class="side-menu"
      >
        <template v-for="route in menuRoutes" :key="route.path">
          <el-menu-item :index="'/' + route.path">
            <el-icon><component :is="route.meta.icon" /></el-icon>
            <template #title>{{ route.meta.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>
      <div class="collapse-btn" @click="isCollapse = !isCollapse">
        <el-icon>
          <Fold v-if="!isCollapse" />
          <Expand v-else />
        </el-icon>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute !== '/'">
              {{ currentRouteMeta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-badge :value="notifyCount" :hidden="notifyCount === 0" class="notify-badge">
            <el-button :icon="Bell" circle />
          </el-badge>
          <el-dropdown>
            <el-button :icon="User" circle />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>系统设置</el-dropdown-item>
                <el-dropdown-item divided>关于</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Bell, User } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 侧边栏折叠状态 / Sidebar collapse state
const isCollapse = ref(false)
// 通知数量 / Notification count
const notifyCount = ref(0)

const currentRoute = computed(() => route.path)
const currentRouteMeta = computed(() => route.meta || {})

const menuRoutes = computed(() => {
  const mainRoute = router.options.routes.find(r => r.path === '/')
  if (!mainRoute || !mainRoute.children) return []
  return mainRoute.children.filter(r => !r.meta?.hidden)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background-color: #304156;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  cursor: pointer;
  border-bottom: 1px solid #3d4f65;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.side-menu {
  flex: 1;
  border-right: none;
  background-color: #304156;
}

.side-menu:not(.el-menu--collapse) {
  width: 220px;
}

.side-menu .el-menu-item {
  color: #bfcbd9;
}

.side-menu .el-menu-item:hover,
.side-menu .el-menu-item.is-active {
  background-color: #263445;
  color: #409eff;
}

.collapse-btn {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bfcbd9;
  cursor: pointer;
  border-top: 1px solid #3d4f65;
}

.collapse-btn:hover {
  background-color: #263445;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
