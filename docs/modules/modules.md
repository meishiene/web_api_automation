# System Modules

## 模块清单

### 1. 认证模块 (auth)
**模块职责**: 用户身份验证和会话管理
**代码目录**: `app/api/auth.py`
**核心功能**:
- 用户注册
- 用户登录
- Token生成
**依赖模块**:
- `app/models/user.py` (User模型)
- `app/database.py` (数据库会话)
**路由前缀**: `/api/auth`
**导出接口**:
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

---

### 2. 项目管理模块 (projects)
**模块职责**: 测试项目的创建、查询、更新和删除
**代码目录**: `app/api/projects.py`
**核心功能**:
- 创建项目
- 查询用户所有项目
- 更新项目信息
- 删除项目
**依赖模块**:
- `app/models/project.py` (Project模型)
- `app/models/user.py` (User模型)
- `app/database.py` (数据库会话)
- `app/dependencies.py` (用户认证)
**路由前缀**: `/api/projects`
**导出接口**:
- `GET /api/projects/` - 获取用户所有项目
- `POST /api/projects/` - 创建项目
- `PUT /api/projects/{project_id}` - 更新项目
- `DELETE /api/projects/{project_id}` - 删除项目

---

### 3. 测试用例模块 (test_cases)
**模块职责**: API测试用例的生命周期管理
**代码目录**: `app/api/test_cases.py`
**核心功能**:
- 创建测试用例
- 查询项目下所有测试用例
- 更新测试用例
- 删除测试用例
**依赖模块**:
- `app/models/api_test_case.py` (ApiTestCase模型)
- `app/models/project.py` (Project模型)
- `app/models/user.py` (User模型)
- `app/database.py` (数据库会话)
- `app/dependencies.py` (用户认证)
**路由前缀**: `/api/test-cases`
**导出接口**:
- `GET /api/test-cases/project/{project_id}` - 获取项目所有测试用例
- `POST /api/test-cases/project/{project_id}` - 创建测试用例
- `PUT /api/test-cases/{case_id}` - 更新测试用例
- `DELETE /api/test-cases/{case_id}` - 删除测试用例

---

### 4. 测试执行模块 (test_runs)
**模块职责**: 执行测试用例并记录测试结果
**代码目录**: `app/api/test_runs.py`
**核心功能**:
- 执行单个测试用例
- 查询项目的所有测试执行记录
- 保存测试结果
**依赖模块**:
- `app/models/test_run.py` (TestRun模型)
- `app/models/api_test_case.py` (ApiTestCase模型)
- `app/models/project.py` (Project模型)
- `app/models/user.py` (User模型)
- `app/services/test_executor.py` (测试执行服务)
- `app/database.py` (数据库会话)
- `app/dependencies.py` (用户认证)
**路由前缀**: `/api/test-runs`
**导出接口**:
- `POST /api/test-runs/test-cases/{case_id}/run` - 执行测试用例
- `GET /api/test-runs/project/{project_id}` - 获取项目测试记录

---

### 5. 测试执行服务 (test_executor)
**模块职责**: 实际执行HTTP请求并验证结果
**代码目录**: `app/services/test_executor.py`
**核心功能**:
- 解析测试用例配置
- 发起HTTP请求
- 验证响应状态码和响应体
- 计算执行耗时
- 处理异常情况
**依赖模块**:
- `httpx` (HTTP客户端库)
- `json` (JSON解析)
- `time` (时间计算)
**导出接口**:
- `execute_test(test_case)` - 异步执行测试用例

---

### 6. 用户模型 (user)
**模块职责**: 用户数据模型定义
**代码目录**: `app/models/user.py`
**核心功能**:
- 定义User表结构
- 提供SQLAlchemy Base类
**依赖模块**:
- `sqlalchemy` (ORM框架)
**表结构**:
- `users`表: id, username, password, created_at

---

### 7. 项目模型 (project)
**模块职责**: 项目数据模型定义
**代码目录**: `app/models/project.py`
**核心功能**:
- 定义Project表结构
- 关联User模型 (owner_id)
**依赖模块**:
- `sqlalchemy` (ORM框架)
- `app/models/user.py` (Base类, ForeignKey)
**表结构**:
- `projects`表: id, name, description, owner_id, created_at

---

### 8. 测试用例模型 (api_test_case)
**模块职责**: 测试用例数据模型定义
**代码目录**: `app/models/api_test_case.py`
**核心功能**:
- 定义ApiTestCase表结构
- 关联Project模型
- 存储HTTP请求配置
**依赖模块**:
- `sqlalchemy` (ORM框架)
- `app/models/user.py` (Base类, ForeignKey)
**表结构**:
- `api_test_cases`表: id, name, project_id, method, url, headers, body, expected_status, expected_body, created_at, updated_at

---

### 9. 测试执行记录模型 (test_run)
**模块职责**: 测试执行结果数据模型定义
**代码目录**: `app/models/test_run.py`
**核心功能**:
- 定义TestRun表结构
- 关联ApiTestCase模型
- 存储测试执行结果
**依赖模块**:
- `sqlalchemy` (ORM框架)
- `app/models/user.py` (Base类, ForeignKey)
**表结构**:
- `test_runs`表: id, test_case_id, status, actual_status, actual_body, error_message, duration_ms, created_at

---

### 10. 数据库管理 (database)
**模块职责**: 数据库连接和会话管理
**代码目录**: `app/database.py`
**核心功能**:
- 创建数据库引擎
- 管理数据库会话
- 初始化数据库表结构
**依赖模块**:
- `sqlalchemy` (ORM框架)
- `app/config.py` (数据库配置)
**导出接口**:
- `get_db()` - 数据库会话依赖
- `init_db()` - 初始化数据库

---

### 11. 应用配置 (config)
**模块职责**: 应用配置管理
**代码目录**: `app/config.py`
**核心功能**:
- 管理应用配置参数
- 支持环境变量覆盖
**依赖模块**:
- `pydantic-settings` (配置验证)
**配置项**:
- `SECRET_KEY`: 加密密钥
- `DATABASE_URL`: 数据库连接URL
- `ALGORITHM`: JWT算法 (未使用)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token过期时间 (未使用)

---

### 12. 依赖注入 (dependencies)
**模块职责**: FastAPI依赖注入管理
**代码目录**: `app/dependencies.py`
**核心功能**:
- 用户认证依赖注入
- 从请求头提取用户ID
- 验证用户存在性
**依赖模块**:
- `app/database.py` (数据库会话)
- `app/models/user.py` (User模型)
**导出接口**:
- `get_current_user()` - 获取当前认证用户

---

### 13. 应用入口 (main)
**模块职责**: FastAPI应用初始化和路由注册
**代码目录**: `app/main.py`
**核心功能**:
- 创建FastAPI应用实例
- 注册CORS中间件
- 注册所有API路由
- 数据库初始化钩子
**依赖模块**:
- `fastapi` (Web框架)
- `app/database.py` (数据库初始化)
- `app/api/*` (所有API路由模块)
**路由配置**:
- `/api/auth` → auth模块
- `/api/projects` → projects模块
- `/api/test-cases` → test_cases模块
- `/api/test-runs` → test_runs模块

---

### 14. 前端应用 (frontend)
**模块职责**: 用户界面和交互
**代码目录**: `frontend/src/`
**核心功能**:
- 页面路由管理
- API请求封装
- 用户界面渲染
**子模块**:
- `main.js`: 应用入口
- `App.vue`: 根组件
- `router/index.js`: 路由配置
- `views/*.vue`: 页面组件
- `api/*.js`: API调用封装
**依赖框架**:
- `vue`: 核心框架
- `vue-router`: 路由管理
- `axios`: HTTP请求库

---

## 模块关系总结

**认证流**: auth → dependencies → 所有受保护路由

**数据流**:
1. 前端 → API路由 → 服务层 → 数据模型 → 数据库
2. 前端 ← API路由 ← 服务层 ← 数据模型 ← 数据库

**执行流**:
test_runs → test_executor → httpx → 外部API → test_executor → test_runs → 数据库
