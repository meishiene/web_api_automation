# Module Dependency Graph

## 模块依赖关系

```
┌─────────────────────────────────────────────────────┐
│                    用户认证层                        │
├─────────────────────────────────────────────────────┤
│  auth                                               │
│  ├── User (models/user.py)                          │
│  └── Register/Login Schema (内联)                   │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                    项目管理层                        │
├─────────────────────────────────────────────────────┤
│  projects                                           │
│  ├── Project (models/project.py)                    │
│  ├── User (models/user.py)                          │
│  └── Project Schema (内联)                          │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                   测试用例管理层                      │
├─────────────────────────────────────────────────────┤
│  test_cases                                         │
│  ├── ApiTestCase (models/api_test_case.py)          │
│  ├── Project (models/project.py)                    │
│  ├── User (models/user.py)                          │
│  └── TestCase Schema (内联)                         │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                   测试执行层                         │
├─────────────────────────────────────────────────────┤
│  test_runs                                          │
│  ├── TestRun (models/test_run.py)                   │
│  ├── ApiTestCase (models/api_test_case.py)          │
│  ├── Project (models/project.py)                    │
│  ├── User (models/user.py)                          │
│  └── execute_test (services/test_executor.py)       │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                  外部API调用层                       │
├─────────────────────────────────────────────────────┤
│  httpx (第三方库)                                    │
│  - 发起HTTP请求                                      │
│  - 处理响应                                          │
│  - 超时控制                                          │
└─────────────────────────────────────────────────────┘
```

## 数据流依赖

```
用户认证流程:
auth (验证) → User模型 → Session/Token → 所有其他API

项目管理流程:
projects (CRUD) → Project模型 → User模型 (关联) → 数据库

测试用例流程:
test_cases (CRUD) → ApiTestCase模型 → Project模型 (关联) → User模型 (权限)

测试执行流程:
test_runs (执行) → TestRun模型 → ApiTestCase模型 → execute_test服务 → httpx → 外部API
                                                               ↓
                                                        SQLite (持久化结果)
```

## 核心依赖模块

### 基础设施层
- `app/database.py`: 数据库连接和会话管理
  - 依赖: `sqlalchemy`, `app/config.py`

- `app/config.py`: 应用配置管理
  - 依赖: `pydantic-settings`
  - 提供: SECRET_KEY, DATABASE_URL等配置

- `app/dependencies.py`: 依赖注入管理
  - 依赖: `app/database.py`, `app/models/user.py`
  - 提供: `get_current_user` (认证依赖)

### 模型层 (app/models/)
- `user.py`: User模型
  - 依赖: `sqlalchemy`

- `project.py`: Project模型
  - 依赖: `sqlalchemy`, `app/models/user.py` (Base, ForeignKey)

- `api_test_case.py`: ApiTestCase模型
  - 依赖: `sqlalchemy`, `app/models/user.py` (Base, ForeignKey)

- `test_run.py`: TestRun模型
  - 依赖: `sqlalchemy`, `app/models/user.py` (Base, ForeignKey)

### 服务层 (app/services/)
- `test_executor.py`: 测试执行服务
  - 依赖: `httpx`, `json`, `time`
  - 提供: `execute_test()` (异步测试执行)

### 路由层 (app/api/)
- `auth.py`: 认证路由
  - 依赖: `app/database.py`, `app/models/user.py`, `app/dependencies.py`

- `projects.py`: 项目路由
  - 依赖: `app/database.py`, `app/models/project.py`, `app/models/user.py`, `app/dependencies.py`

- `test_cases.py`: 测试用例路由
  - 依赖: `app/database.py`, `app/models/api_test_case.py`, `app/models/project.py`, `app/models/user.py`, `app/dependencies.py`

- `test_runs.py`: 测试执行路由
  - 依赖: `app/database.py`, `app/models/test_run.py`, `app/models/api_test_case.py`, `app/models/project.py`, `app/models/user.py`, `app/dependencies.py`, `app/services/test_executor.py`

### 前端依赖 (frontend/)
- `main.js`: 应用入口
  - 依赖: `vue`, `./App.vue`, `./router`

- `App.vue`: 根组件
  - 依赖: `vue`, `vue-router`

- `router/index.js`: 路由配置
  - 依赖: `vue-router`

- `views/`: 页面组件
  - 依赖: `@/api/*` (API调用封装), `vue`
