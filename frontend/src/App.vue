<!--
  根组件 / Root component
  @Function: 应用顶层容器，提供国际化配置和路由出口 / Top-level container, provides i18n config and router outlet
-->
<template>
  <!-- Element Plus 国际化配置 / Element Plus i18n configuration -->
  <el-config-provider :locale="zhCn">
    <!-- 路由视图出口 / Router view outlet -->
    <router-view />
  </el-config-provider>
</template>

<script setup>
// 导入中文语言包 / Import Chinese language pack
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
</script>

<style>
/* 全局重置样式 / Global reset styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 根元素全屏布局 / Root element fullscreen layout */
html, body, #app {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
