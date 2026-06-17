/**
 * Electron 预加载脚本 / Electron preload script
 * @Function: 安全地暴露 Electron API 到渲染进程 / Safely expose Electron API to renderer process
 */
const { contextBridge, ipcRenderer } = require('electron')

// 向渲染进程暴露 API / Expose API to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // 获取应用版本号 / Get app version
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  // 监听主进程消息 / Listen for main process messages
  onMessage: (callback) => ipcRenderer.on('message', callback),
})
