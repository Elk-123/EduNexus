@echo off
chcp 65001 > nul

echo === EduNexus 启动脚本 ===
echo.

REM 检查后端服务是否已启动
curl -s http://localhost:8001/health > nul 2>&1
if %errorlevel% neq 0 (
    echo 启动后端服务...
    cd /c/Users/The\ shy/Desktop/EduNexus/backend
    start "Backend" uvicorn app.main:app --reload --port 8001
    timeout /t 5 /nobreak > nul
)

REM 检查前端服务是否已启动
curl -s http://localhost:5173 > nul 2>&1
if %errorlevel% neq 0 (
    echo 启动前端服务...
    cd /c/Users/The\ shy/Desktop/EduNexus/EduNexus
    start "Frontend" npm run dev
    timeout /t 10 /nobreak > nul
)

echo.
echo === 服务启动完成 ===
echo.
echo 请在浏览器中打开以下地址：
echo 前端: http://localhost:5173
echo API文档: http://localhost:8001/docs
echo.
echo 要停止服务，请关闭相应的终端窗口
echo.
pause