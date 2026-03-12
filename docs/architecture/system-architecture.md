# System Architecture

## 架构模式
当前项目采用 **前后端分离 + REST API + SQLite 本地持久化** 的轻量架构。

- 前端：Vue 3 + Vite + Vue Router
- 后端：FastAPI
- 数据访问：SQLAlchemy ORM
- 数据库：SQLite
- 外部调用：`httpx.AsyncClient`

## 分层结构
```text
浏览器 / Vue 前端
  ├─ 登录 / 注册页面
  ├─ 项目列表页面
  └─ 测试用例管理页面（含执行结果弹窗）

        │ HTTP + JSON
        ▼

FastAPI 应用
  ├─ app/main.py                应用入口与路由注册
  ├─ app/api/*.py               路由层
  ├─ app/dependencies.py        认证依赖
  ├─ app/services/test_executor.py  测试执行服务
  ├─ app/services/audit_service.py   审计治理服务
  └─ app/models/*.py            ORM 模型

        │ SQLAlchemy
        ▼

SQLite 数据库
  ├─ users
  ├─ organizations
  ├─ organization_members
  ├─ projects
  ├─ project_members
  ├─ api_test_cases
  ├─ test_runs
  ├─ audit_logs
  ├─ audit_logs_archive
  ├─ schedule_tasks   (预留)
  └─ run_queue        (预留)
```

## 后端服务结构

### 应用入口
- `app/main.py`
- 注册 CORS 中间件，当前配置为本地开发白名单（`localhost/127.0.0.1` 常用前端端口）
- 挂载路由：
  - `/api/auth`
  - `/api/organizations`
  - `/api/projects`
  - `/api/test-cases`
  - `/api/test-runs`
  - `/api/audit-logs`
- 提供健康检查：`GET /ping`
- 在 `startup` 事件中执行 `auto_migrate_db()`（本地/测试环境自动迁移，含历史 SQLite 脏库列级修复兜底）与 `init_db()` 自动建表

### 数据库迁移
- 已引入 Alembic：`alembic.ini` + `migrations/`
- 当前已有初始迁移版本：`initial_schema`
- 已支持通过 `APP_ENV` + `USE_POSTGRES` 在本地/测试环境切换 PostgreSQL
- 开发期可继续兼容 `init_db()` 自动建表，后续建议统一收敛到迁移流程

### 认证方式
- 使用 JWT Bearer Token 进行受保护接口鉴权
- 登录接口返回 `access_token` 与 `refresh_token`
- 前端把 `accessToken` / `refreshToken` 保存到 `localStorage`
- 每次请求通过 `Authorization: Bearer <access_token>` 访问受保护接口
- 当访问令牌过期时，前端调用 `POST /api/auth/refresh` 获取新 `access_token`
- `app/dependencies.py` 负责解码并校验访问令牌中的 `sub` 与 `type`
- RBAC 已落地：`users.role`（`admin` / `user`）+ `require_roles(...)`/`require_permissions(...)` 权限依赖
- 已支持项目成员协作权限：`project_members`（`maintainer` / `editor` / `viewer`）
- 已支持组织层权限治理基础能力：`organizations`、`organization_members`（`admin` / `member`）

### 路由层
- `app/api/auth.py`：注册、登录
- `app/api/organizations.py`：组织管理、组织成员管理、项目归属治理、跨项目成员治理
- `app/api/projects.py`：项目 CRUD
  - `GET /api/projects/{project_id}/members`
  - `POST /api/projects/{project_id}/members`
  - `DELETE /api/projects/{project_id}/members/{member_user_id}`
- `app/api/test_cases.py`：测试用例 CRUD
- `app/api/test_runs.py`：执行测试、按项目查询执行记录
- `app/api/audit_logs.py`：审计日志查询
  - `POST /api/audit-logs/governance/run` 仅 `admin` 可调用

### Schema / DTO 组织
- 路由层请求/响应模型已统一收敛到 `app/schemas/`
- 当前包含：`user.py`、`project.py`、`api_test_case.py`、`test_run.py`、`audit_log.py`、`common.py`
- 新增接口时优先在 `schemas/` 中定义 DTO，避免在路由文件内重复定义

### 服务层
- `app/services/test_executor.py`
- 负责把测试用例转换为 HTTP 请求参数并发起调用
- 支持解析 JSON `headers` / `body`
- 负责生成 `success` / `failed` / `error` 三种结果状态

### 模型关系映射
- 核心模型已补齐显式关系映射（`relationship + back_populates`）
- 已覆盖 `User`、`Organization`、`OrganizationMember`、`Project`、`ProjectMember`、`ApiTestCase`、`TestRun` 与预留调度/队列模型的主关联关系

### 领域模型治理
- 已在核心实体中落地数据治理规则：约束（Check/Unique）、索引（单列/组合）、级联删除策略与时间字段生命周期默认值
- 模型生命周期工具位于 `app/models/lifecycle.py`，统一提供 Unix 时间戳默认值
- 迁移版本：`migrations/versions/01fcc228897e_domain_model_governance.py`

### 异常处理与错误码
- 统一异常入口：`app/errors.py`
- 业务异常通过 `AppException` 抛出，包含 `status_code`、`code`、`message`
- 全局异常处理器统一返回错误结构：
  - `success: false`
  - `error.code` / `error.message` / `error.request_id`
  - `detail`（兼容前端旧逻辑）
- 每个请求都会生成或透传 `request_id`，并写入响应头 `X-Request-ID`

### 结构化日志与审计日志
- 日志配置入口：`app/logging_config.py`
- 请求日志：统一输出 `event=http_request`，包含方法、路径、状态码、耗时、request_id、客户端 IP
- 审计日志：`app/services/audit_service.py` 写入 `audit_logs` 表并输出 `event=audit_log`
- 审计覆盖：认证关键动作、项目写操作、测试用例写操作、测试执行触发
- 审计治理：通过 `audit_logs_archive` 归档历史日志，`scripts/audit-governance-run.py` 执行保留策略（支持 dry-run）

## 前端结构
- 路由定义：`frontend/src/router/index.js`
- 页面：
  - `/login`
  - `/register`
  - `/`
  - `/project/:projectId`
- 路由守卫：未登录时跳转 `/login`

### 前端 API 封装
- `frontend/src/utils/request.js`
  - 自动推导默认 `baseURL`
  - 自动注入 `Authorization` 请求头
  - 401 时尝试使用 `refresh_token` 自动刷新并重放请求
  - 刷新失败时清理登录态并跳转登录页
- `frontend/src/api/projects.js`
- `frontend/src/api/testCases.js`

## 关键调用流程

### 登录流程
1. 用户在前端提交用户名密码
2. 前端调用 `POST /api/auth/login`
3. 后端校验密码哈希并返回 `access_token` 与 `refresh_token`
4. 前端保存令牌与用户基础信息
5. 后续请求自动带上 `Authorization: Bearer <access_token>`

### 项目管理流程
1. 前端调用 `/api/projects`
2. 后端通过 `get_current_user()` 获取当前用户
3. 查询当前用户拥有的项目与成员项目（admin 可全量查询）
4. 返回 JSON 给前端渲染

### 测试执行流程
1. 前端在测试用例页面点击“运行”
2. 请求 `POST /api/test-runs/test-cases/{case_id}/run`
3. 后端校验用例归属
4. `test_executor.execute_test()` 调用目标 API
5. 结果写入 `test_runs`
6. 前端展示本次执行结果

## 当前架构特点
- 结构简单，适合快速开发和本地部署
- 认证链路已升级为 JWT + Refresh Token 模式
- 数据模型已为后续调度和队列做了预留
- 暂未形成完整“服务层 + 调度层 + 工作节点”体系
