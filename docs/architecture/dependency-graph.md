# Module Dependency Graph

## 后端依赖关系
```text
app/main.py
  ├─ app.api.auth
  ├─ app.api.organizations
  ├─ app.api.projects
  ├─ app.api.test_cases
  ├─ app.api.test_suites
  ├─ app.api.environments
  ├─ app.api.test_runs
  └─ app.api.audit_logs

app.api.test_suites
  ├─ app.models.api_test_suite
  ├─ app.models.api_test_suite_case
  ├─ app.models.api_test_case
  ├─ app.services.access_control
  └─ app.services.audit_service

app.api.environments
  ├─ app.models.project_environment
  ├─ app.models.project_variable
  ├─ app.models.environment_variable
  ├─ app.services.access_control
  ├─ app.services.variable_resolver
  └─ app.services.audit_service

app.api.test_runs
  ├─ app.models.test_run
  ├─ app.models.api_batch_run
  ├─ app.models.api_batch_run_item
  ├─ app.models.api_test_suite
  ├─ app.models.api_test_suite_case
  ├─ app.services.test_executor
  ├─ app.services.variable_resolver
  └─ app.services.audit_service

app.services.test_executor
  ├─ httpx.AsyncClient
  └─ assertion/variable/extraction helpers
```

## 前端依赖关系
```text
frontend/src/main.js
  ├─ App.vue
  └─ router/index.js

router/index.js
  ├─ Login.vue
  ├─ Register.vue
  ├─ ProjectList.vue
  └─ TestCaseList.vue

views/*.vue
  ├─ utils/request.js
  ├─ api/projects.js
  └─ api/testCases.js
```

## 领域数据流

### 套件执行数据流（阶段 2）
```text
调用方/前端
  → POST /api/test-runs/suites/{suite_id}/run
  → 加载 suite cases（按 order_index）
  → 解析 runtime variables（project + environment）
  → execute_test(case, runtime_variables)
  → TestRun + ApiBatchRunItem
  → ApiBatchRun 汇总
  → GET /api/test-runs/batches/* 查询
```

### 环境变量数据流（阶段 2）
```text
调用方/前端
  → /api/environments/project/{project_id}
  → /api/environments/project/{project_id}/variables
  → /api/environments/{environment_id}/variables
  → 变量在执行时注入并支持链路提取覆盖
```

## 关键耦合点
- `get_current_user()` 是受保护接口统一入口
- `can_manage_test_case/can_execute_test_run` 控制套件、环境与执行权限
- `execute_test()` 是单用例与套件执行共享引擎
- `resolve_runtime_variables()` 统一变量优先级合并

## 预留模块
- `app/models/schedule_task.py`
- `app/models/run_queue.py`

两者仍未接入业务链路。
