# System Modules

## 高频改动定位（速查）

| 你要改什么 | 先看这些文件 |
| --- | --- |
| 登录/注册/刷新令牌 | `app/api/auth.py`、`app/dependencies.py`、`app/security.py`、`frontend/src/utils/request.js` |
| 最小 RBAC / 角色校验 | `app/models/user.py`、`app/dependencies.py`、`app/api/audit_logs.py`、`migrations/versions/fcf57b5ad65c_minimal_rbac_role.py` |
| 组织层权限治理 | `app/models/organization.py`、`app/models/organization_member.py`、`app/api/organizations.py`、`migrations/versions/d1f8902c4b61_organization_layer_governance.py` |
| 项目成员权限治理 | `app/models/project_member.py`、`app/services/access_control.py`、`app/api/projects.py`、`migrations/versions/9b1f0b38d7d2_project_member_model.py` |
| 鉴权失败/401 重试 | `app/dependencies.py`、`app/errors.py`、`frontend/src/utils/request.js` |
| 项目增删改查 | `app/api/projects.py`、`frontend/src/api/projects.js`、`frontend/src/views/ProjectList.vue` |
| 测试用例增删改查 | `app/api/test_cases.py`、`frontend/src/api/testCases.js`、`frontend/src/views/TestCaseList.vue` |
| 单条 API 执行结果异常 | `app/api/test_runs.py`、`app/services/test_executor.py`、`app/models/test_run.py` |
| 测试执行断言逻辑 | `app/services/test_executor.py` |
| 统一错误结构/错误码 | `app/errors.py`、`app/main.py` |
| 请求追踪与 `X-Request-ID` | `app/errors.py`、`app/logging_config.py`、`app/main.py` |
| 审计日志落库 | `app/services/audit_service.py`、`app/models/audit_log.py` |
| 审计查询/归档/保留策略 | `app/api/audit_logs.py`、`app/services/audit_service.py`、`app/models/audit_log_archive.py`、`scripts/audit-governance-run.py` |
| 审计治理生产化编排 | `scripts/audit-governance-run.py`、`scripts/prod-audit-governance-run.ps1`、`app/services/audit_governance_orchestrator.py` |
| 数据库连接与建表 | `app/config.py`、`app/database.py` |
| 领域模型治理（约束/索引/级联/生命周期） | `app/models/*.py`、`app/models/lifecycle.py`、`migrations/versions/01fcc228897e_domain_model_governance.py` |
| 数据库迁移 | `migrations/env.py`、`migrations/versions/*.py`、`alembic.ini` |
| 生产环境迁移执行 | `scripts/prod-db-migrate.ps1`、`scripts/db_connectivity_check.py`、`docs/tech/db-migration.md` |
| 生产窗口迁移演练留档 | `scripts/prod-db-window-drill.ps1`、`artifacts/prod-db-window-drill/*.json`、`docs/tech/db-migration.md` |
| 路由与页面跳转 | `frontend/src/router/index.js`、`frontend/src/views/*.vue` |
| 调度/队列预留模型 | `app/models/schedule_task.py`、`app/models/run_queue.py` |

## 模块清单

### 1. 应用入口模块
- **文件**：`app/main.py`
- **职责**：创建 FastAPI 应用、配置 CORS、注册路由、启动建表、提供 `/ping`

### 2. 配置模块
- **文件**：`app/config.py`
- **职责**：管理 `SECRET_KEY`、`ALGORITHM`、`ACCESS_TOKEN_EXPIRE_MINUTES`、`REFRESH_TOKEN_EXPIRE_MINUTES`、`PASSWORD_HASH_ITERATIONS`、`DATABASE_URL`
- **说明**：已用于 JWT 签发/校验与密码哈希配置

### 3. 日志配置模块
- **文件**：`app/logging_config.py`
- **职责**：提供统一 JSON 结构化日志格式与日志初始化
- **特点**：统一输出请求日志、异常日志、审计日志

### 4. 数据库模块
- **文件**：`app/database.py`
- **职责**：创建 SQLAlchemy `engine`、`SessionLocal`、`get_db()` 和 `init_db()`
- **说明**：`init_db()` 会创建核心业务表（含 `project_members` 成员协作表）与预留扩展表

### 5. 数据库迁移模块
- **文件**：`alembic.ini`、`migrations/env.py`、`migrations/versions/*.py`
- **职责**：管理数据库结构版本，支持 `upgrade` / `downgrade`
- **现状**：已建立首个基线迁移 `initial_schema`
- **本地落地**：`docker-compose.postgres.yml` + `infra/postgres/init/01-create-test-db.sql`

### 6. 依赖注入模块
- **文件**：`app/dependencies.py`
- **职责**：从 `Authorization: Bearer` 令牌中解析当前用户
- **特点**：校验 JWT 的 `sub` 与 `type`，并基于数据库确认用户存在

### 7. 认证模块
- **文件**：`app/api/auth.py`
- **职责**：用户注册、登录与访问令牌刷新
- **接口**：
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `POST /api/auth/refresh`
- **现状**：密码以哈希形式存储；登录返回 `access_token` + `refresh_token`

### 8. 组织治理模块
- **文件**：`app/api/organizations.py`
- **职责**：组织管理、组织成员治理、项目归属治理、跨项目成员治理
- **接口**：
  - `GET /api/organizations/`
  - `POST /api/organizations/`
  - `GET /api/organizations/{organization_id}/members`
  - `POST /api/organizations/{organization_id}/members`
  - `POST /api/organizations/{organization_id}/projects/attach`
  - `POST /api/organizations/{organization_id}/members/governance/cross-project`

### 9. 项目管理模块
- **文件**：`app/api/projects.py`
- **职责**：项目增删改查与项目成员管理
- **接口**：
  - `GET /api/projects/`
  - `POST /api/projects/`
  - `PUT /api/projects/{project_id}`
  - `DELETE /api/projects/{project_id}`
  - `GET /api/projects/{project_id}/members`
  - `POST /api/projects/{project_id}/members`
  - `DELETE /api/projects/{project_id}/members/{member_user_id}`

### 10. 测试用例管理模块
- **文件**：`app/api/test_cases.py`
- **职责**：按项目维护测试用例
- **接口**：
  - `GET /api/test-cases/project/{project_id}`
  - `POST /api/test-cases/project/{project_id}`
  - `PUT /api/test-cases/{case_id}`
  - `DELETE /api/test-cases/{case_id}`

### 11. 测试执行模块
- **文件**：`app/api/test_runs.py`
- **职责**：执行单个测试用例，并按项目查询执行记录
- **接口**：
  - `POST /api/test-runs/test-cases/{case_id}/run`
  - `GET /api/test-runs/project/{project_id}`

### 12. 审计查询模块
- **文件**：`app/api/audit_logs.py`
- **职责**：按用户维度查询审计日志，支持动作、结果、request_id、路径关键字、时间范围过滤；管理员支持治理执行
- **接口**：
  - `GET /api/audit-logs/`
  - `POST /api/audit-logs/governance/run`（admin）

### 12. 测试执行服务模块
- **文件**：`app/services/test_executor.py`
- **职责**：封装真实 HTTP 请求、超时控制、断言与结果转换
- **输出状态**：`success`、`failed`、`error`

### 13. 异常与错误码模块
- **文件**：`app/errors.py`
- **职责**：定义统一错误码、业务异常类型与全局异常处理器
- **特点**：统一错误响应结构，并支持请求级 `request_id` 追踪

### 14. 用户模型模块
- **文件**：`app/models/user.py`
- **职责**：定义 `users` 表，并提供全局 `Base`

### 15. 项目模型模块
- **文件**：`app/models/project.py`
- **职责**：定义 `projects` 表

### 16. 测试用例模型模块
- **文件**：`app/models/api_test_case.py`
- **职责**：定义 `api_test_cases` 表，保存请求配置和断言配置

### 17. 测试执行记录模型模块
- **文件**：`app/models/test_run.py`
- **职责**：定义 `test_runs` 表，保存执行状态、响应内容、耗时和错误信息

### 18. 审计日志模型模块
- **文件**：`app/models/audit_log.py`
- **职责**：定义 `audit_logs` 表，记录关键写操作审计信息

### 19. 审计归档模型模块
- **文件**：`app/models/audit_log_archive.py`
- **职责**：定义 `audit_logs_archive` 表，承载历史审计归档数据

### 20. 审计服务模块
- **文件**：`app/services/audit_service.py`
- **职责**：统一创建审计记录、查询过滤、归档迁移与保留策略执行

### 21. 调度任务模型模块（预留）
- **文件**：`app/models/schedule_task.py`
- **职责**：为后续定时任务提供表结构
- **现状**：仅有数据模型，无 API / 服务 / UI

### 22. 执行队列模型模块（预留）
- **文件**：`app/models/run_queue.py`
- **职责**：为后续任务排队和执行状态跟踪提供表结构
- **现状**：仅有数据模型，无 API / 服务 / UI

### 23. 生命周期工具模块
- **文件**：`app/models/lifecycle.py`
- **职责**：提供统一 Unix 时间戳生成函数，供模型默认值和更新时间字段复用

### 24. 前端路由模块
- **文件**：`frontend/src/router/index.js`
- **职责**：定义页面路由和登录拦截逻辑

### 25. 前端请求模块
- **文件**：`frontend/src/utils/request.js`
- **职责**：封装 axios 实例、动态 `baseURL`、用户头注入和 401 处理

### 26. 前端页面模块
- **文件**：`frontend/src/views/*.vue`
- **职责**：实现登录、注册、项目列表、测试用例管理与执行结果展示

## 模块关系总结
- 受保护的后端接口统一依赖 `get_current_user()`
- 测试执行能力由 `test_runs.py` 驱动，真正执行逻辑在 `test_executor.py`
- 前端目前没有独立“执行记录页”，测试结果主要在 `TestCaseList.vue` 中查看
- 文档中原先强调的“测试报告模块”在当前代码里还未形成独立模块
