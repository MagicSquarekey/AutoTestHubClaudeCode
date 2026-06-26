/**
 * 路由配置 / Router configuration
 * @Function: 定义前端页面路由和导航守卫 / Define frontend page routes and navigation guards
 */
import { createRouter, createWebHistory } from 'vue-router'

// 路由表 / Route table
const routes = [
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' },
      },
      {
        path: 'case',
        name: 'TestCase',
        component: () => import('@/views/TestCase.vue'),
        meta: { title: '用例管理', icon: 'Document' },
      },
      {
        path: 'case/edit/:id?',
        name: 'CaseEdit',
        component: () => import('@/views/CaseEdit.vue'),
        meta: { title: '用例编辑', hidden: true },
      },
      {
        path: 'module',
        name: 'Module',
        component: () => import('@/views/Module.vue'),
        meta: { title: '模块管理', icon: 'Folder' },
      },
      {
        path: 'tag',
        name: 'Tag',
        component: () => import('@/views/Tag.vue'),
        meta: { title: '标签管理', icon: 'PriceTag' },
      },
      {
        path: 'element',
        name: 'Element',
        component: () => import('@/views/Element.vue'),
        meta: { title: '元素管理', icon: 'Pointer' },
      },
      {
        path: 'execution',
        name: 'Execution',
        component: () => import('@/views/Execution.vue'),
        meta: { title: '执行控制', icon: 'VideoPlay' },
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('@/views/Report.vue'),
        meta: { title: '测试报告', icon: 'DataAnalysis' },
      },
      {
        path: 'device',
        name: 'Device',
        component: () => import('@/views/Device.vue'),
        meta: { title: '设备管理', icon: 'Monitor' },
      },
      {
        path: 'scheduler',
        name: 'Scheduler',
        component: () => import('@/views/Scheduler.vue'),
        meta: { title: '任务调度', icon: 'Timer' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置', icon: 'Setting' },
      },
      {
        path: 'menu-config',
        name: 'MenuConfig',
        component: () => import('@/views/MenuConfig.vue'),
        meta: { title: '菜单配置', icon: 'Menu' },
      },
      {
        path: 'record',
        name: 'Record',
        component: () => import('@/views/Record.vue'),
        meta: { title: '页面录制', icon: 'VideoCamera' },
      },
    ],
  },
]

// 创建路由实例 / Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局前置守卫：动态设置页面标题 / Global before guard: dynamically set page title
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - AutoTest Hub` : 'AutoTest Hub'
  next()
})

export default router
