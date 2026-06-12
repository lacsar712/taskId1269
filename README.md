# 污水处理厂智能管理系统

一个现代化的污水处理厂综合管理平台，涵盖生产管理、安全管理、设备管理、化验管理、能耗管理等核心业务模块。

## 🛠 技术栈

- **Frontend**: Vue3 + Vite + Arco Design + TypeScript
- **Backend**: Python FastAPI + SQLAlchemy
- **Database**: MySQL 8.0

## 🚀 启动指南 (How to Run)

1. 确保 Docker Desktop 已启动
2. 在根目录执行：
   ```bash
   docker compose up --build
   ```
3. 等待容器启动完成（约2-3分钟）

## 🔗 服务地址 (Services)

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend Swagger**: http://localhost:8000/docs
- **Database**: localhost:3306 (user: water_user / pass: water123)

## 🧪 测试账号

- **管理员**: admin / 123456
- **普通用户**: user / 123456

## 📁 项目结构

```
taskId1269/
├── docker-compose.yml    # Docker 编排配置
├── frontend/             # Vue3 前端项目
│   ├── src/
│   │   ├── api/         # API 接口
│   │   ├── router/      # 路由配置
│   │   ├── stores/      # 状态管理
│   │   ├── views/       # 页面视图
│   │   └── components/  # 通用组件
│   └── Dockerfile
├── backend/              # FastAPI 后端项目
│   ├── app/
│   │   ├── models/      # 数据模型
│   │   ├── routers/     # API 路由
│   │   ├── schemas/     # 数据验证
│   │   └── services/    # 业务逻辑
│   └── Dockerfile
└── mysql/                # 数据库初始化
    └── init.sql
```

## 🏗 功能模块

| 一级模块 | 二级导航 | 说明 |
|---------|---------|------|
| 生产管理 | 工艺运行监控、生产计划调度、生产日志、异常处理、工艺优化、异常告警 | 核心生产业务 |
| 安全管理 | 安全巡检、风险管控、应急管理、安全培训、作业许可 | 安全生产保障 |
| 设备管理 | 设备台账、运行监控、维护保养、故障管理、备件管理、故障告警、设备分析 | 设备全生命周期 |
| 化验管理 | 样品管理、检测任务、数据管理、报告管理、质控管理、标准库 | 水质检测化验 |
| 生产报表 | 常规报表、自定义报表、数据可视化、数据溯源、趋势预测 | 数据分析决策 |
| 能耗管理 | 实时监测、多维分析、节能策略、成本核算、能耗报表 | 节能降耗管理 |
| 资料管理 | 文档分类、上传管理、检索下载、归档备份、常用推荐 | 知识文档管理 |
| 物资管理 | 物资台账、入库管理、出库管理、库存管理、采购管理、供应商管理 | 物资供应链 |
| 绩效管理 | 考核指标、数据管理、统计分析、绩效应用 | 员工绩效考核 |
| 系统设置 | 项目管理、用户管理、角色权限、基础数据、系统参数、日志、接口、维护 | 系统基础配置 |
