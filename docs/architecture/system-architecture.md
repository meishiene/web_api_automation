# System Architecture

## 架构模式
当前项目采用 **前后端分离 + REST API + 单体后端服务** 的轻量架构。

- 前端：Vue 3 + Vite + Vue Router
- 后端：FastAPI
- 数据访问：SQLAlchemy ORM
- 数据库：SQLite（支持切换 PostgreSQL）
- 外部调用：`httpx.AsyncClient`

## 分层结构
```text
浏览器 / Vue 前端
  ├─ 登录 / 注册页面
  ├─ 项目列表页面
  └─ 测试用例管理页面

        │ HTTP + JSON
        ▼

FastAPI 应用
  ├─ app/main.py                     应用入口与路由注册
  ├─ app/api/*.py                    路由层
  ├─ app/dependencies.py             认证依赖
  ├─ app/services/execution_orchestrator.py 统一执行编排服务（阶段 4 骨架）
  ├─ app/services/test_executor.py   测试执行服务
  ├─ app/services/web_executor.py    Web 执行服务
  ├─ app/services/variable_resolver.py 变量解析服务
  ├─ app/services/audit_service.py   审计服务
  └─ app/models/*.py                 ORM 模型

        │ SQLAlchemy
        ▼

SQLite / PostgreSQL
  ├─ users
  ├─ organizations
  ├─ organization_members
  ├─ projects
  ├─ project_members
  ├─ api_test_cases
  ├─ api_test_suites
  ├─ api_test_suite_cases
  ├─ web_test_cases
  ├─ web_steps
  ├─ web_locators
  ├─ web_test_runs
  ├─ project_environments
  ├─ project_variables
  ├─ environment_variables
  ├─ test_runs
  ├─ api_batch_runs
  ├─ api_batch_run_items
  ├─ audit_logs
  ├─ audit_logs_archive
  ├─ schedule_tasks   (阶段 4：最小 API 已接入)
  └─ run_queue        (阶段 4：trigger 入队已接入)
```

## 后端服务结构

### 应用入口
- `app/main.py`
- 挂载路由：
  - `/api/auth`
  - `/api/organizations`
  - `/api/projects`
  - `/api/test-cases`
  - `/api/test-suites`
  - `/api/environments`
  - `/api/test-runs`
  - `/api/web-test-cases`
  - `/api/web-test-runs`
  - `/api/audit-logs`
- 提供健康检查：`GET /ping`
- 启动阶段执行 `auto_migrate_db()`（非生产）和 `init_db()`

### 认证与权限
- JWT Bearer + Refresh Token
- `app/dependencies.py` 负责令牌校验与用户注入
- RBAC + 资源级权限：
  - 全局角色：`admin` / `user`
  - 项目成员角色：`maintainer/editor/viewer`
  - 组织成员角色：`admin/member`

### 路由层
- `app/api/auth.py`：注册、登录、刷新令牌
- `app/api/organizations.py`：组织与跨项目治理
- `app/api/projects.py`：项目 CRUD 与成员管理
- `app/api/test_cases.py`：测试用例 CRUD（含 `assertion_rules` / `extraction_rules`）
- `app/api/test_suites.py`：套件 CRUD、套件用例编排
- `app/api/environments.py`：环境与变量管理（项目级/环境级）
- `app/api/schedule_tasks.py`：调度任务管理与触发入队（阶段 4）
- `app/api/test_runs.py`：
  - 单用例执行：`POST /api/test-runs/test-cases/{case_id}/run`
  - 套件执行：`POST /api/test-runs/suites/{suite_id}/run`
  - 执行记录：`GET /api/test-runs/project/{project_id}`
  - 统一结果：`GET /api/test-runs/project/{project_id}/unified-results`（聚合 API/Web，支持 `run_type/status/created_from/created_to/page/page_size`）
  - 批次查询：`GET /api/test-runs/batches/project/{project_id}`
  - 批次明细：`GET /api/test-runs/batches/{batch_id}`
- `app/api/audit_logs.py`：审计查询与治理执行
- `app/api/web_test_cases.py`：Web 用例管理（阶段 3）
- `app/api/web_test_runs.py`：Web 单用例执行与结果查询（阶段 3）

### Schema / DTO
- 路由 DTO 统一收敛在 `app/schemas/`
- 阶段 2 重点 DTO：
  - `test_suite.py`
  - `environment.py`
  - `batch_run.py`

### 服务层
- `app/services/test_executor.py`
  - 变量替换：`{{var}}`
  - 断言能力：`contains` / `regex` / `jsonpath`
  - 响应提取：按 `extraction_rules` 输出变量
- `app/services/variable_resolver.py`
  - 合并运行时变量：项目变量 + 变量组 + 环境变量（环境覆盖变量组，变量组覆盖项目）；执行过程中链路提取变量可继续覆盖
- `app/services/audit_service.py`
  - 关键写操作审计落库
- `app/services/web_executor.py`
  - Web 步骤执行与失败截图产物输出（`artifacts/web-test-runs/{run_id}/`）
- `app/services/execution_orchestrator.py`
  - 统一执行任务/作业编排骨架（ExecutionTask/ExecutionJob）
  - API/Web 适配协议接入与统一状态映射

## 数据库迁移
- Alembic：`alembic.ini` + `migrations/`
- 阶段 2 新增迁移：
  - `e2b4c6a8d901_phase2_api_platform_core.py`
- 新增内容：
  - 套件模型
  - 环境与变量模型
  - 批次执行模型
  - 用例增强字段（断言规则、提取规则）

## 关键调用流程

### 单用例执行流程
1. 请求 `POST /api/test-runs/test-cases/{case_id}/run`
2. 校验权限
3. `execute_test()` 调用目标 API
4. 写入 `test_runs`

### 套件批量执行流程（阶段 2）
1. 请求 `POST /api/test-runs/suites/{suite_id}/run`
2. 加载套件有序用例列表
3. 解析运行时变量（项目变量 + 变量组 + 环境变量）
4. 逐条执行并提取链路变量（链路变量优先级最高）
5. 写入 `test_runs`、`api_batch_run_items`
6. 汇总写入 `api_batch_runs`
7. 通过批次接口查询结果

## 当前架构特点
- 已从“单用例执行”演进到“套件 + 批次 + 变量链路”的阶段 2 首批能力
- 执行、变量、审计三条链路已贯通
- 前端已落地批次列表/批次详情/执行详情页面与 Web 执行相关页面，后续仍需持续增强展示维度与报告能力
- 阶段 4 已启动（开发清单已建立），调度、队列、Worker 尚未打通实现链路


## 2026-03-16 ?? 4 ??

- Stage 4 status: S4-01~S4-04 completed; S4-05 acceptance/cutover in progress.


## Stage-4 Acceptance And Real-Consumption Strategy (2026-03-16)

- Acceptance rubric: A4-01~A4-05 + regression/build gates (see `docs/project/stage-4-acceptance-checklist.md`).
- Real-consumption strategy: R1~R5 prioritizing worker loop and idempotent claim before retry/recovery enhancements.
