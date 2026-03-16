# Repository Structure

## 根目录
```text
web_api_automation/
├─ app/                    后端代码
├─ docs/                   项目文档
├─ frontend/               前端代码
├─ infra/                  基础设施脚本（PostgreSQL 初始化等）
├─ migrations/             Alembic 迁移目录
├─ scripts/                开发辅助脚本（一键启动、数据库自检等）
├─ tests/                  后端测试
├─ alembic.ini             Alembic 配置
├─ docker-compose.postgres.yml   PostgreSQL 本地编排
├─ .env.postgres.example   PostgreSQL 环境变量样例
├─ requirements.txt        后端依赖
├─ test_platform.db        SQLite 数据库文件
├─ README.md               根说明文件
└─ ARCHITECTURE_DOCS_REPORT.md
```

## `app/` 后端目录
```text
app/
├─ api/
│  ├─ auth.py
│  ├─ audit_logs.py
│  ├─ projects.py
│  ├─ test_cases.py
│  └─ test_runs.py
├─ models/
│  ├─ user.py
│  ├─ project.py
│  ├─ api_test_case.py
│  ├─ test_run.py
│  ├─ audit_log.py
│  ├─ audit_log_archive.py
│  ├─ schedule_task.py
│  ├─ run_queue.py
│  └─ lifecycle.py
├─ schemas/
│  ├─ __init__.py
│  ├─ audit_log.py
│  ├─ common.py
│  ├─ user.py
│  ├─ project.py
│  ├─ api_test_case.py
│  └─ test_run.py
├─ services/
│  ├─ test_executor.py
│  └─ audit_service.py
├─ errors.py
├─ logging_config.py
├─ config.py
├─ database.py
├─ dependencies.py
└─ main.py
```

### 说明
- `api/` 是当前业务主入口
- `models/` 包含已落地实体和预留扩展实体，已补齐约束/索引/级联与生命周期默认值治理
- 路由 DTO（请求/响应模型）已统一复用 `app/schemas/` 下的 Pydantic 模型
- `services/` 目前包含测试执行与审计日志服务

## `frontend/` 前端目录
```text
frontend/
├─ package.json
├─ src/
│  ├─ api/
│  │  ├─ projects.js
│  │  └─ testCases.js
│  ├─ router/
│  │  └─ index.js
│  ├─ utils/
│  │  └─ request.js
│  ├─ views/
│  │  ├─ Login.vue
│  │  ├─ Register.vue
│  │  ├─ ProjectList.vue
│  │  └─ TestCaseList.vue
│  ├─ App.vue
│  └─ main.js
```

### 说明
- 页面数量较少，当前以业务闭环优先
- `TestCaseList.vue` 同时承担列表、编辑弹窗、执行结果展示等职责
- 还没有独立的测试结果列表页、报表页或系统设置页

## `docs/` 文档目录
- `project/`：项目概览
- `architecture/`：系统架构与依赖关系
- `domain/`：领域模型
- `modules/`：模块清单
- `tech/`：技术栈与仓库结构

## `scripts/` 关键脚本
- `scripts/dev-postgres-up.ps1`：一键启动 PostgreSQL（容器启动 + 迁移 + 自检）
- `scripts/dev-postgres-down.ps1`：一键停止 PostgreSQL（可选清理卷）
- `scripts/dev-api-up.ps1`：数据库就绪后自动启动 API（可 `-PrepareOnly`）
- `scripts/dev-api-down.ps1`：按端口停止 API 进程
- `scripts/prod-db-migrate.ps1`：生产环境迁移脚本（强制确认 + 可选备份 + 可选自检）
- `scripts/audit-governance-run.py`：审计归档与保留策略执行（支持 dry-run）
- `scripts/db_connectivity_check.py`：数据库连通性和必需表自检

## 代码与文档对照时的注意点
- `app/models/schedule_task.py` 与 `app/models/run_queue.py` 已接入阶段 4 最小闭环；重试/租约/死信等增强能力仍在后续迭代
- `frontend/src/api/testCases.js` 中保留了 `getTestResult()` 方法，但后端当前没有对应 `GET /api/test-runs/{runId}` 接口
- `app/schemas/` 是当前路由层 DTO 的统一入口；新增接口应优先在 `schemas/` 中定义模型
