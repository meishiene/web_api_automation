# 企业级自动化测试平台

这是一个可交付使用的自动化测试平台，当前已经具备以下核心能力：

- 项目管理与项目成员协作
- 环境、变量、密钥治理
- API 用例管理、导入、套件回归、批次执行
- Web 用例管理、结构化步骤编辑、执行配置持久化
- 调度任务、队列、Worker 监控
- 统一执行中心与报告中心
- 企业集成治理工作台

## 快速开始

### 推荐启动方式

在仓库根目录执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev-start.ps1
```

这个方式适合 PowerShell 当前目录显示为 `Microsoft.PowerShell.Core\FileSystem::\\?\D:\...` 的场景，能避免 `npm.cmd` 在设备路径下启动失败。

### 常规启动方式

如果当前路径是普通磁盘路径，也可以直接执行：

```powershell
npm run dev
```

### 默认访问地址

- 前端：`http://127.0.0.1:5173`
- 后端：`http://127.0.0.1:8000`

## 初次使用建议

建议按下面顺序上手：

1. 注册并登录系统
2. 创建项目
3. 添加项目成员
4. 配置环境与变量
5. 导入或新建 API 用例
6. 建立 API 套件并执行
7. 创建并执行 Web 用例
8. 配置调度任务
9. 在执行中心、报告中心、集成治理页查看结果

## 重要文档

面向使用者：

- [用户手册](D:\project\web_api_automation\docs\project\user-manual.md)
- [项目概览](D:\project\web_api_automation\docs\project\project-overview.md)
- [最终交付说明](D:\project\web_api_automation\docs\project\final-delivery-summary.md)
- [缺陷与风险台账](D:\project\web_api_automation\docs\project\defect-register.md)

面向维护者：

- [项目进度](D:\project\web_api_automation\docs\project\project-progress.md)
- [平台功能完善计划](D:\project\web_api_automation\docs\project\platform-function-hardening-plan.md)
- [文档导航](D:\project\web_api_automation\docs\README.md)

## 常用命令

启动项目：

```powershell
npm run dev
```

前端构建：

```powershell
npm run build --prefix frontend
```

后端全量回归：

```powershell
python -m pytest tests/backend -q
```

查看数据库迁移状态：

```powershell
python -m alembic current
```

## 当前交付状态

当前仓库已完成交付级收口，具备：

- 可启动
- 可登录
- 可执行完整主链路
- 后端全量回归通过
- 前端构建通过
- 本地数据库迁移状态已对齐到当前 head

如需了解详细交付边界、保留风险和建议后续动作，请直接阅读：

- [最终交付说明](D:\project\web_api_automation\docs\project\final-delivery-summary.md)

## 技术栈

- 后端：FastAPI + SQLAlchemy + SQLite
- 前端：Vue 3 + Vite + Vue Router + Axios
- 执行：httpx / Playwright
- 迁移：Alembic

## 说明

- 若文档与代码冲突，以 `app/` 与 `frontend/src/` 的实际实现为准
- 当前仍有少量可继续增强的体验项，但不影响日常使用与交付
