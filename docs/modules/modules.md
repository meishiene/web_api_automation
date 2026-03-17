# System Modules

## 高频改动定位（速查）

| 你要改什么 | 先看这些文件 |
| --- | --- |
| 套件 CRUD / 编排 | `app/api/test_suites.py`、`app/models/api_test_suite.py`、`app/models/api_test_suite_case.py` |
| 套件批量执行 / 批次查询 | `app/api/test_runs.py`、`app/models/api_batch_run.py`、`app/models/api_batch_run_item.py` |
| 环境与变量管理 | `app/api/environments.py`、`app/models/project_environment.py`、`app/models/project_variable.py`、`app/models/environment_variable.py` |
| 变量替换与断言增强 | `app/services/test_executor.py`、`app/services/variable_resolver.py` |
| Web 用例与执行（阶段 3） | `app/api/web_test_cases.py`、`app/api/web_test_runs.py`、`app/services/web_executor.py` |
| 统一执行结果查询 | `app/api/test_runs.py`（`/unified-results`）、`frontend/src/views/UnifiedRunList.vue` |
| 阶段 4 执行编排骨架 | `app/models/execution_task.py`、`app/models/execution_job.py`、`app/services/execution_orchestrator.py` |
| 测试用例断言/提取字段 | `app/api/test_cases.py`、`app/schemas/api_test_case.py`、`app/models/api_test_case.py` |
| 权限问题（403） | `app/services/access_control.py`、`app/permissions.py` |
| 认证相关（401） | `app/dependencies.py`、`app/api/auth.py`、`frontend/src/utils/request.js` |
| 审计日志链路 | `app/services/audit_service.py`、`app/api/audit_logs.py` |
| 数据库结构与迁移 | `migrations/versions/*.py`、`app/models/*.py` |

## 模块清单

### 1. 应用入口
- 文件：`app/main.py`
- 职责：应用初始化、中间件、路由注册、启动建表

### 2. 认证与权限
- 文件：`app/api/auth.py`、`app/dependencies.py`、`app/permissions.py`、`app/services/access_control.py`
- 职责：登录/刷新、令牌解析、RBAC、资源级权限

### 3. 项目与组织
- 文件：`app/api/projects.py`、`app/api/organizations.py`
- 职责：项目 CRUD、成员治理、组织治理

### 4. API 用例管理
- 文件：`app/api/test_cases.py`、`app/models/api_test_case.py`
- 职责：用例 CRUD、请求参数、断言规则、提取规则

### 5. API 套件管理（阶段 2）
- 文件：`app/api/test_suites.py`、`app/models/api_test_suite.py`、`app/models/api_test_suite_case.py`
- 职责：套件 CRUD、套件-用例编排、顺序管理

### 6. 环境与变量（阶段 2）
- 文件：`app/api/environments.py`、`app/models/project_environment.py`、`app/models/project_variable.py`、`app/models/environment_variable.py`
- 职责：项目级/环境级变量管理与脱敏展示

### 7. 执行与批次（阶段 2）
- 文件：`app/api/test_runs.py`、`app/models/test_run.py`、`app/models/api_batch_run.py`、`app/models/api_batch_run_item.py`
- 职责：单用例执行、套件批量执行、批次明细追踪

### 8. 执行引擎
- 文件：`app/services/test_executor.py`、`app/services/variable_resolver.py`
- 职责：变量替换、HTTP 执行、断言、提取、结果转换

### 9. 审计与治理
- 文件：`app/services/audit_service.py`、`app/api/audit_logs.py`
- 职责：关键操作审计、查询、治理执行

### 10. Web 测试模块（阶段 3）
- 文件：`app/api/web_test_cases.py`、`app/api/web_test_runs.py`、`app/services/web_executor.py`
- 职责：Web 用例管理、单用例执行、步骤日志与产物归档

### 11. 迁移与基础设施
- 文件：`app/database.py`、`migrations/*`
- 职责：连接管理、自动迁移、版本演进

## 模块关系总结
- 所有受保护接口统一依赖 `get_current_user()`
- 套件执行由 `test_runs.py` 触发，核心执行逻辑在 `test_executor.py`
- 批次执行数据拆分为：
  - `api_batch_runs`（汇总）
  - `api_batch_run_items`（逐条明细）
  - `test_runs`（真实执行结果）
- 变量优先级：项目变量 < 环境变量 < 链路提取变量
