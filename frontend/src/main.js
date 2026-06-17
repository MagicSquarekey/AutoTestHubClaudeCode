/**
 * 前端应用入口 / Frontend application entry point
 * @Function: 初始化 Vue 应用，注册全局插件和组件 / Initialize Vue app, register global plugins and components
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

// 创建 Vue 应用实例 / Create Vue application instance
const app = createApp(App)

// 注册 Element Plus 图标组件 / Register Element Plus icon components
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册状态管理、路由、UI 框架 / Register state management, router, UI framework
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// 挂载应用到 DOM / Mount application to DOM
app.mount('#app')
