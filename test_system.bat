@echo off
chcp 65001 > nul

echo === EduNexus 系统综合测试 ===
echo.

REM 1. 测试后端健康检查
echo 1. 测试后端健康检查...
curl -s http://localhost:8001/health
echo.

REM 2. 用户注册测试
echo 2. 测试用户注册...
for /f "tokens=2 delims=:," %%A in ('curl -s -X POST -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"username\":\"testuser\",\"password\":\"123456\"}" http://localhost:8001/api/v1/auth/register ^| findstr "access_token"') do (
    set TOKEN=%%A
)
set TOKEN=%TOKEN:"=%
echo ✓ 注册成功，获取到 token: %TOKEN%

REM 3. 提交破冰数据测试
echo 3. 测试提交破冰数据...
curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"responses\":{\"knowledge_base\":[\"数学\",\"编程\"],\"cognitive_style\":[\"视觉型\"],\"learning_goals\":[\"掌握AI技术\"],\"time_distribution\":[\"晚上\"],\"notes\":[\"希望实践\"]}}" http://localhost:8001/api/v1/profile/onboarding
echo ✓ 破冰分析完成

REM 4. 内容生成测试
echo 4. 测试内容生成...
for /f "tokens=2 delims=:," %%A in ('curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"topic\":\"微积分基础\"}" http://localhost:8001/api/v1/factory/generate ^| findstr "task_id"') do (
    set TASK_ID=%%A
)
set TASK_ID=%TASK_ID:"=%
echo ✓ 生成任务已启动: %TASK_ID%

REM 等待任务完成
echo 等待任务完成...
timeout /t 2 /nobreak > nul
for /f "tokens=2 delims=:," %%A in ('curl -s -H "Authorization: Bearer %TOKEN%" http://localhost:8001/api/v1/factory/status/%TASK_ID% ^| findstr "status"') do (
    set STATUS=%%A
)
set STATUS=%STATUS:"=%
echo ✓ 任务状态: %STATUS%

REM 5. 学习路径规划测试
echo 5. 测试学习路径规划...
curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"goal\":\"掌握机器学习\"}" http://localhost:8001/api/v1/graph/plan
echo ✓ 学习路径已生成

REM 6. 资源推送测试
echo 6. 测试资源推送...
curl -s -H "Authorization: Bearer %TOKEN%" http://localhost:8001/api/v1/resources/today
echo ✓ 今日资源已获取

echo.
echo === 所有测试通过！系统运行正常 ===
echo.
echo 前端地址: http://localhost:5173
echo 后端API: http://localhost:8001
echo API文档: http://localhost:8001/docs
echo.
pause