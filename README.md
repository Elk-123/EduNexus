# EduNexus 基于大模型的个性化导学系统
---

## 1.快速开始
```
cd EduNexus && npm run dev  #开启前端服务器
conda activate edunexus  #后端环境
cd backend && uvicorn app.main:app --reload --port 8001  #启动后端
```

## 2.Roadmap
1.资源生成Agent优化
2.学习路径规划右侧对齐
3.资源推送左侧接后端。整体算法优化。再加StackOverflow API
4.智能指导前端展示区域分块以及json解析优化
5.Onborading进一步约束LLM稳定输出，profile总结功能完善
6.代码，数据库质量优化
7.控制台和学习效果整体对接并用真实数据
8.setting增加用户提供LLM API功能
9.构建CICD Pipeline
10.完善项目文档，issues
11.全平台发布一个月，开源。