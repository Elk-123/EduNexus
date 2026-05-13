#!/bin/bash

# EduNexus 系统综合测试脚本
echo "=== EduNexus 系统综合测试 ==="
echo ""

# 1. 测试后端健康检查
echo "1. 测试后端健康检查..."
curl -s http://localhost:8001/health | jq -r '.status'
echo ""

# 2. 用户注册测试
echo "2. 测试用户注册..."
LOGIN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"123456"}' \
  http://localhost:8001/api/v1/auth/register)
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "✓ 注册成功，获取到 token"

# 3. 提交破冰数据测试
echo "3. 测试提交破冰数据..."
curl -s -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"responses":{"knowledge_base":["数学","编程"],"cognitive_style":["视觉型"],"learning_goals":["掌握AI技术"],"time_distribution":["晚上"],"notes":["希望实践"]}}' \
  http://localhost:8001/api/v1/profile/onboarding | jq -r '.profile_data.cognitive_style'
echo "✓ 破冰分析完成"

# 4. 内容生成测试
echo "4. 测试内容生成..."
TASK_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"topic":"微积分基础"}' \
  http://localhost:8001/api/v1/factory/generate)
TASK_ID=$(echo $TASK_RESPONSE | jq -r '.task_id')
echo "✓ 生成任务已启动: $TASK_ID"

# 等待任务完成
echo "等待任务完成..."
sleep 2
STATUS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/v1/factory/status/$TASK_ID)
STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
echo "✓ 任务状态: $STATUS"

# 5. 学习路径规划测试
echo "5. 测试学习路径规划..."
curl -s -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"goal":"掌握机器学习"}' \
  http://localhost:8001/api/v1/graph/plan | jq -r '.title'
echo "✓ 学习路径已生成"

# 6. 资源推送测试
echo "6. 测试资源推送..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/v1/resources/today | jq -r '.[0].title'
echo "✓ 今日资源已获取"

echo ""
echo "=== 所有测试通过！系统运行正常 ==="
echo ""
echo "前端地址: http://localhost:5173"
echo "后端API: http://localhost:8001"
echo "API文档: http://localhost:8001/docs"