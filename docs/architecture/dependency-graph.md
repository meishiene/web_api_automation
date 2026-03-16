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
  ├─ app.api.schedule_tasks
  ├─ app.api.queue_worker
  ├─ app.api.test_runs
  ├─ app.api.web_test_cases
  ├─ app.api.web_test_runs
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

app.api.schedule_tasks
  ├─ app.models.schedule_task
  ├─ app.models.run_queue
  ├─ app.services.access_control
  └─ app.services.audit_service

app.api.queue_worker
  ├─ app.models.run_queue
  ├─ app.models.worker_heartbeat
  ├─ app.services.queue_worker_runtime
  ├─ app.services.access_control
  └─ app.services.audit_service

app.api.test_runs
  ├─ app.models.test_run
  ├─ app.models.execution_task
  ├─ app.models.execution_job
  ├─ app.models.api_batch_run
  ├─ app.models.api_batch_run_item
  ├─ app.models.api_test_suite
  ├─ app.models.api_test_suite_case
  ├─ app.services.execution_orchestrator
  ├─ app.services.test_executor
  ├─ app.services.variable_resolver
  └─ app.services.audit_service

app.services.test_executor
  ├─ httpx.AsyncClient
  └─ assertion/variable/extraction helpers

app.api.web_test_runs
  ├─ app.models.web_test_case
  ├─ app.models.web_test_run
  ├─ app.models.execution_task
  ├─ app.models.execution_job
  ├─ app.services.execution_orchestrator
  ├─ app.services.web_executor
  ├─ app.services.access_control
  └─ app.services.audit_service
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
  ├─ TestCaseList.vue
  ├─ WebTestCaseList.vue
  ├─ WebTestRunDetail.vue
  └─ UnifiedRunList.vue

views/*.vue
  ├─ utils/request.js
  ├─ api/projects.js
  ├─ api/testCases.js
  ├─ api/testRuns.js
  └─ api/environments.js

views/*.vue（阶段 2 已落地页面）
  ├─ BatchRunList.vue
  ├─ BatchRunDetail.vue
  ├─ TestRunDetail.vue
  └─ EnvironmentManager.vue

views/*.vue（阶段 3 已落地页面）
  ├─ WebTestCaseList.vue
  ├─ WebTestRunDetail.vue
  └─ UnifiedRunList.vue
```

## 领域数据流

### 套件执行数据流（阶段 2）
```text
调用方/前端
  → POST /api/test-runs/suites/{suite_id}/run
  → 加载 suite cases（按 order_index）
  → 解析 runtime variables（project + variable groups + environment）
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
  → 变量在执行时注入（支持变量组绑定/复用）并支持链路提取覆盖
```

## 关键耦合点
- `get_current_user()` 是受保护接口统一入口
- `can_manage_test_case/can_execute_test_run` 控制套件、环境与执行权限
- `execute_test()` 是单用例与套件执行共享引擎
- `resolve_runtime_variables()` 统一变量优先级合并（project < variable groups < environment < extracted runtime vars）

## 阶段 4 模块状态
- `app/models/schedule_task.py`
- `app/models/run_queue.py`
- `app/models/worker_heartbeat.py`

上述模型已接入最小业务链路（调度触发入队、队列领取/回写、Worker 心跳与最小可视化）；重试/租约/死信等工程化能力仍在后续迭代范围内。
