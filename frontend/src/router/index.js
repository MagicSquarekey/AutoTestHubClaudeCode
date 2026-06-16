import { createRouter, createWebHistory } from 'vue-router'

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
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - AutoTest Hub` : 'AutoTest Hub'
  next()
})

export default router
