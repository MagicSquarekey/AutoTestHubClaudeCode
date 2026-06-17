@echo off
:: AutoTest Hub 开发模式启动脚本 / AutoTest Hub dev mode startup script
:: 所有日志输出到当前终端 / All logs output to current terminal
chcp 65001 >nul 2>&1
title AutoTest Hub [Dev Mode]
:: 切换到项目根目录 / Switch to project root directory
cd /d %~dp0..

echo ========================================
echo   AutoTest Hub - Dev Mode
echo ========================================
echo   All logs visible here.
echo   Press Ctrl+C to stop.
echo ========================================
echo.

:: 清理旧进程 / Clean up old processes
echo [1/3] Cleaning up...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8686 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

:: 后台启动后端，日志输出到当前终端 / Start backend in background, logs to current terminal
echo [2/3] Starting backend...
start /B "Backend" cmd /c "cd backend && ..\.venv\Scripts\python.exe main.py"

:: 后台启动前端，日志输出到当前终端 / Start frontend in background, logs to current terminal
echo [3/3] Starting frontend...
start /B "Frontend" cmd /c "cd frontend && npm run dev"

:: 等待服务启动后打开浏览器 / Wait for services then open browser
timeout /t 5 /nobreak >nul
start http://localhost:5173
echo.
echo [OK] Browser opened. Services running...
echo.

:: 保持窗口运行，等待用户按任意键 / Keep window alive, wait for user input
pause >nul
