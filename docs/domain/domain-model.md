# Domain Model

## 核心实体

### User
- 表：`users`
- 关键字段：`id`、`username`、`role`、`password`、`created_at`
- 职责：身份主体、项目/套件/环境创建者

### Project
- 表：`projects`
- 关键字段：`id`、`name`、`description`、`owner_id`、`organization_id`、`created_at`
- 职责：测试资产归属边界

### ApiTestCase
- 表：`api_test_cases`
- 关键字段：
  - 请求：`method`、`url`、`headers`、`body`
  - 基础断言：`expected_status`、`expected_body`
  - 增强规则：`assertion_rules`、`extraction_rules`
- 职责：可执行的单条 API 测试定义

### ApiTestSuite（阶段 2）
- 表：`api_test_suites`
- 关键字段：`project_id`、`name`、`description`、`created_by`
- 职责：测试用例集合与回归编排入口

### ApiTestSuiteCase（阶段 2）
- 表：`api_test_suite_cases`
- 关键字段：`suite_id`、`test_case_id`、`order_index`
- 职责：维护套件内用例顺序

### ProjectEnvironment（阶段 2）
- 表：`project_environments`
- 关键字段：`project_id`、`name`、`description`
- 职责：环境隔离（dev/test/staging/prod）

### ProjectVariable / EnvironmentVariable（阶段 2）
- 表：`project_variables`、`environment_variables`
- 关键字段：`key`、`value`、`is_secret`
- 职责：运行时变量管理，支持脱敏展示

### TestRun
- 表：`test_runs`
- 关键字段：`test_case_id`、`status`、`actual_status`、`actual_body`、`error_message`、`duration_ms`
- 职责：单次执行结果快照

### ApiBatchRun / ApiBatchRunItem（阶段 2）
- 表：`api_batch_runs`、`api_batch_run_items`
- 关键字段：
  - 批次：`status`、`total_cases`、`passed_cases`、`failed_cases`、`error_cases`
  - 明细：`test_case_id`、`test_run_id`、`order_index`、`status`
- 职责：套件批量执行的汇总与明细追踪

## 预留实体

### ScheduleTask
- 表：`schedule_tasks`
- 状态：预留（未打通业务链路）

### RunQueue
- 表：`run_queue`
- 状态：预留（未打通业务链路）

## 实体关系
```text
User 1 ─── N Project
Project 1 ─── N ApiTestCase
Project 1 ─── N ApiTestSuite
ApiTestSuite 1 ─── N ApiTestSuiteCase ─── 1 ApiTestCase

Project 1 ─── N ProjectEnvironment
Project 1 ─── N ProjectVariable
ProjectEnvironment 1 ─── N EnvironmentVariable

ApiTestCase 1 ─── N TestRun
ApiBatchRun 1 ─── N ApiBatchRunItem ─── 1 TestRun

Project 1 ─── N ScheduleTask   (预留)
Project 1 ─── N RunQueue       (预留)
```

## 业务规则（当前）
- 资源访问受项目/组织成员权限约束
- 套件中的用例必须属于同一项目
- 套件执行按 `order_index` 顺序执行
- 变量优先级：项目变量 < 环境变量 < 链路提取变量
- `is_secret=true` 的变量对查询接口默认脱敏

## 重要实现细节
- 核心模型采用显式 `relationship(..., back_populates=...)`
- 时间字段统一使用 Unix 时间戳整数
- 密码字段为哈希存储（兼容历史明文迁移）
