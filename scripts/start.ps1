# AutoTest Hub PowerShell 启动脚本 / AutoTest Hub PowerShell startup script
# 后台启动所有服务，自动打开浏览器，无多余终端窗口 / Start all services in background, auto-open browser, no extra windows

$ErrorActionPreference = "Stop"

# 获取项目根目录（脚本在 scripts/ 下，需上跳一级）/ Get project root (script is in scripts/, go up one level)
$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$VenvPython = Join-Path $RootDir ".venv\Scripts\python.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AutoTest Hub 一键启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境 / Check virtual environment
if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] 虚拟环境不存在，请先运行: python -m venv .venv" -ForegroundColor Red
    exit 1
}

# 检查后端依赖 / Check backend dependencies
Write-Host "[1/4] 检查后端依赖..." -ForegroundColor Yellow
$backendDeps = & $VenvPython -m pip list 2>$null | Select-String "fastapi"
if (-not $backendDeps) {
    Write-Host "  安装后端依赖..." -ForegroundColor Yellow
    & $VenvPython -m pip install -r (Join-Path $BackendDir "requirements.txt") --quiet
}

# 检查前端依赖 / Check frontend dependencies
Write-Host "[2/4] 检查前端依赖..." -ForegroundColor Yellow
if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Host "  安装前端依赖..." -ForegroundColor Yellow
    Push-Location $FrontendDir
    npm install --silent
    Pop-Location
}

# 清理占用端口的旧进程 / Clean up old processes occupying ports
Write-Host "[3/4] 清理旧进程..." -ForegroundColor Yellow
$ports = @(8686, 5173)
foreach ($port in $ports) {
    $connections = netstat -aon | Select-String ":${port}\s" | Select-String "LISTENING"
    foreach ($conn in $connections) {
        $procId = ($conn -split '\s+')[-1]
        if ($procId -match '^\d+$') {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
}

# 后台启动后端服务（隐藏窗口）/ Start backend service in background (hidden window)
Write-Host "[4/4] 启动服务..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "cd /d `"$BackendDir`" && `"$VenvPython`" main.py" -WindowStyle Hidden -PassThru

# 后台启动前端服务（隐藏窗口）/ Start frontend service in background (hidden window)
$frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "cd /d `"$FrontendDir`" && npm run dev" -WindowStyle Hidden -PassThru

# 等待服务就绪 / Wait for services to be ready
Write-Host ""
Write-Host "  等待服务启动..." -ForegroundColor Yellow

$maxWait = 30
$ready = $false
for ($i = 0; $i -lt $maxWait; $i++) {
    Start-Sleep -Seconds 1
    try {
        Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop | Out-Null
        $ready = $true
        break
    } catch {
        # 还没就绪，继续等待 / Not ready yet, keep waiting
    }
}

if ($ready) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  AutoTest Hub 启动完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  正在打开浏览器..." -ForegroundColor Cyan
    # 打开浏览器 / Open browser
    Start-Process "http://localhost:5173"
    Write-Host ""
    Write-Host "  按任意键停止所有服务..." -ForegroundColor Yellow
    Write-Host ""

    # 等待用户按键后停止服务 / Wait for user input then stop services
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} else {
    Write-Host "[ERROR] 服务启动超时，请检查日志" -ForegroundColor Red
    Write-Host "  按任意键退出..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# 清理：停止所有后台进程 / Cleanup: stop all background processes
Write-Host ""
Write-Host "正在停止服务..." -ForegroundColor Yellow

# 停止后端和前端进程 / Stop backend and frontend processes
$backendProcess | Stop-Process -Force -ErrorAction SilentlyContinue
$frontendProcess | Stop-Process -Force -ErrorAction SilentlyContinue

# 清理端口上的残留进程 / Clean up residual processes on ports
foreach ($port in $ports) {
    $connections = netstat -aon | Select-String ":${port}\s" | Select-String "LISTENING"
    foreach ($conn in $connections) {
        $procId = ($conn -split '\s+')[-1]
        if ($procId -match '^\d+$') {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "所有服务已停止" -ForegroundColor Green
