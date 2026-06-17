@echo off
:: AutoTest Hub 停止服务脚本 / AutoTest Hub stop services script
:: 终止后端(8686)和前端(5173)的所有进程 / Kill all backend(8686) and frontend(5173) processes

:: 查找并终止占用8686端口的进程 / Find and kill processes using port 8686
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8686 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

:: 查找并终止占用5173端口的进程 / Find and kill processes using port 5173
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
