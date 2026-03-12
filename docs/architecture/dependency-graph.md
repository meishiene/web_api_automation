# Module Dependency Graph

## 后端依赖关系
```text
app/main.py
  ├─ app.api.auth
  ├─ app.api.projects
  ├─ app.api.test_cases
  ├─ app.api.test_runs
  └─ app.database

app.api.auth
  ├─ app.database
  └─ app.models.user

app.api.projects
  ├─ app.database
  ├─ app.dependencies
  ├─ app.models.project
  └─ app.models.user

app.api.test_cases
  ├─ app.database
  ├─ app.dependencies
  ├─ app.models.api_test_case
  ├─ app.models.project
  └─ app.models.user

app.api.test_runs
  ├─ app.database
  ├─ app.dependencies
  ├─ app.models.test_run
  ├─ app.models.api_test_case
  ├─ app.models.project
  ├─ app.models.user
  └─ app.services.test_executor

app.database
  ├─ app.config
  └─ app.models.*
```

## 前端依赖关系
```text
frontend/src/main.js
  ├─ frontend/src/App.vue
  └─ frontend/src/router/index.js

frontend/src/router/index.js
  ├─ views/Login.vue
  ├─ views/Register.vue
  ├─ views/ProjectList.vue
  └─ views/TestCaseList.vue

views/*.vue
  ├─ frontend/src/utils/request.js
  ├─ frontend/src/api/projects.js
  └─ frontend/src/api/testCases.js
```

## 领域数据流

### 认证数据流
```text
Login.vue / Register.vue
  → /api/auth/*
  → User
  → localStorage(accessToken, refreshToken)
  → Authorization: Bearer <access_token>
  → /api/auth/refresh (token 过期时)
  → get_current_user()
```

### 项目数据流
```text
ProjectList.vue
  → /api/projects
  → Project 表
  → 返回当前用户名下项目
```

### 测试用例数据流
```text
TestCaseList.vue
  → /api/test-cases/project/{project_id}
  → ApiTestCase 表
  → 返回项目下测试用例
```

### 测试执行数据流
```text
TestCaseList.vue
  → /api/test-runs/test-cases/{case_id}/run
  → execute_test(test_case)
  → 外部目标 API
  → TestRun 表
  → 返回执行结果
```

## 关键耦合点
- `app.models.user.Base` 是所有 ORM 模型共享的 Declarative Base
- `app.dependencies.get_current_user()` 是受保护接口的统一入口
- `app.services.test_executor.execute_test()` 是测试执行的核心能力
- 前端 `request.js` 统一管理 `baseURL`、请求头和 401 跳转逻辑

## 已存在但未接入主链路的模块
- `app/models/schedule_task.py`
- `app/models/run_queue.py`

这两个模块已经被 `init_db()` 纳入建表流程，但当前没有路由、服务或页面依赖它们。
