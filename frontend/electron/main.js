/**
 * Electron 主进程 / Electron main process
 * @Function: 管理应用窗口、生命周期、IPC 通信 / Manage app window, lifecycle, IPC communication
 */
const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')

// 主窗口引用 / Main window reference
let mainWindow

function createWindow() {
  // 创建浏览器窗口 / Create browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    title: 'AutoTest Hub',
    icon: path.join(__dirname, '../public/icon.ico'),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  })

  // 开发环境加载本地服务器，生产环境加载打包文件 / Load dev server or built files
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  // 窗口关闭时清空引用 / Clear reference when window closed
  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 应用就绪后创建窗口 / Create window when app is ready
app.whenReady().then(createWindow)

// 所有窗口关闭时退出应用（macOS 除外）/ Quit when all windows closed (except macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// macOS 点击 dock 图标时重新创建窗口 / Recreate window on macOS dock click
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// IPC 通信：获取应用版本 / IPC: get app version
ipcMain.handle('get-app-version', () => {
  return app.getVersion()
})
