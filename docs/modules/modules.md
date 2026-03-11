# System Modules

## 模块清单

### 1. 应用入口模块
- **文件**：`app/main.py`
- **职责**：创建 FastAPI 应用、配置 CORS、注册路由、启动建表、提供 `/ping`

### 2. 配置模块
- **文件**：`app/config.py`
- **职责**：管理 `SECRET_KEY`、`ALGORITHM`、`ACCESS_TOKEN_EXPIRE_MINUTES`、`DATABASE_URL`
- **说明**：虽然保留了 JWT 相关配置字段，但当前代码没有真正使用 JWT

### 3. 数据库模块
- **文件**：`app/database.py`
- **职责**：创建 SQLAlchemy `engine`、`SessionLocal`、`get_db()` 和 `init_db()`
- **说明**：`init_db()` 会创建 6 张表，包括两个预留扩展表

### 4. 依赖注入模块
- **文件**：`app/dependencies.py`
- **职责**：从 `X-User-ID` 头中解析当前用户
- **特点**：实现简单，依赖数据库查询用户是否存在

### 5. 认证模块
- **文件**：`app/api/auth.py`
- **职责**：用户注册与登录
- **接口**：
  - `POST /api/auth/register`
  - `POST /api/auth/login`
- **现状**：密码明文存储；返回的 `access_token` 本质上是用户 ID 字符串

### 6. 项目管理模块
- **文件**：`app/api/projects.py`
- **职责**：项目的增删改查
- **接口**：
  - `GET /api/projects/`
  - `POST /api/projects/`
  - `PUT /api/projects/{project_id}`
  - `DELETE /api/projects/{project_id}`

### 7. 测试用例管理模块
- **文件**：`app/api/test_cases.py`
- **职责**：按项目维护测试用例
- **接口**：
  - `GET /api/test-cases/project/{project_id}`
  - `POST /api/test-cases/project/{project_id}`
  - `PUT /api/test-cases/{case_id}`
  - `DELETE /api/test-cases/{case_id}`

### 8. 测试执行模块
- **文件**：`app/api/test_runs.py`
- **职责**：执行单个测试用例，并按项目查询执行记录
- **接口**：
  - `POST /api/test-runs/test-cases/{case_id}/run`
  - `GET /api/test-runs/project/{project_id}`

### 9. 测试执行服务模块
- **文件**：`app/services/test_executor.py`
- **职责**：封装真实 HTTP 请求、超时控制、断言与结果转换
- **输出状态**：`success`、`failed`、`error`

### 10. 用户模型模块
- **文件**：`app/models/user.py`
- **职责**：定义 `users` 表，并提供全局 `Base`

### 11. 项目模型模块
- **文件**：`app/models/project.py`
- **职责**：定义 `projects` 表

### 12. 测试用例模型模块
- **文件**：`app/models/api_test_case.py`
- **职责**：定义 `api_test_cases` 表，保存请求配置和断言配置

### 13. 测试执行记录模型模块
- **文件**：`app/models/test_run.py`
- **职责**：定义 `test_runs` 表，保存执行状态、响应内容、耗时和错误信息

### 14. 调度任务模型模块（预留）
- **文件**：`app/models/schedule_task.py`
- **职责**：为后续定时任务提供表结构
- **现状**：仅有数据模型，无 API / 服务 / UI

### 15. 执行队列模型模块（预留）
- **文件**：`app/models/run_queue.py`
- **职责**：为后续任务排队和执行状态跟踪提供表结构
- **现状**：仅有数据模型，无 API / 服务 / UI

### 16. 前端路由模块
- **文件**：`frontend/src/router/index.js`
- **职责**：定义页面路由和登录拦截逻辑

### 17. 前端请求模块
- **文件**：`frontend/src/utils/request.js`
- **职责**：封装 axios 实例、动态 `baseURL`、用户头注入和 401 处理

### 18. 前端页面模块
- **文件**：`frontend/src/views/*.vue`
- **职责**：实现登录、注册、项目列表、测试用例管理与执行结果展示

## 模块关系总结
- 受保护的后端接口统一依赖 `get_current_user()`
- 测试执行能力由 `test_runs.py` 驱动，真正执行逻辑在 `test_executor.py`
- 前端目前没有独立“执行记录页”，测试结果主要在 `TestCaseList.vue` 中查看
- 文档中原先强调的“测试报告模块”在当前代码里还未形成独立模块
