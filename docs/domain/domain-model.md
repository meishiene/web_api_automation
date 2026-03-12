# Domain Model

## 核心实体

### User
- **表名**：`users`
- **字段**：`id`、`username`、`role`、`password`、`created_at`
- **职责**：系统登录主体，也是项目归属的拥有者

### Project
- **表名**：`projects`
- **字段**：`id`、`name`、`description`、`owner_id`、`created_at`
- **职责**：测试资源的组织单元

### ApiTestCase
- **表名**：`api_test_cases`
- **字段**：
  - 基础信息：`id`、`name`、`project_id`
  - 请求配置：`method`、`url`、`headers`、`body`
  - 断言配置：`expected_status`、`expected_body`
  - 审计字段：`created_at`、`updated_at`
- **职责**：描述一次可执行的接口测试

### TestRun
- **表名**：`test_runs`
- **字段**：`id`、`test_case_id`、`status`、`actual_status`、`actual_body`、`error_message`、`duration_ms`、`created_at`
- **职责**：记录一次执行的实际结果

## 预留实体

### ScheduleTask
- **表名**：`schedule_tasks`
- **用途**：未来用于定义定时任务
- **当前状态**：仅建表，不参与业务链路

### RunQueue
- **表名**：`run_queue`
- **用途**：未来用于排队执行和工作节点分发
- **当前状态**：仅建表，不参与业务链路

## 实体关系
```text
User 1 ─── N Project
Project 1 ─── N ApiTestCase
ApiTestCase 1 ─── N TestRun

Project 1 ─── N ScheduleTask   (预留)
Project 1 ─── N RunQueue       (预留)
User 1 ─── N ScheduleTask      (created_by)
```

## 聚合视角

### Project 聚合
`Project` 是当前业务中最明显的聚合边界：
- 项目拥有者决定访问权限
- 测试用例归属于项目
- 测试执行记录通过测试用例间接归属于项目

### ApiTestCase 聚合
`ApiTestCase` 是执行时的直接输入：
- 它聚合了请求参数和断言配置
- `TestRun` 是其执行结果的历史快照

## 当前业务规则
- 用户只能访问自己名下的项目
- 用户只能访问自己项目下的测试用例
- 用户只能执行自己项目下的测试用例
- 用户角色最小闭环：`admin` / `user`（`admin` 可执行治理类受控接口）
- 测试结果必须关联到某个测试用例
- 测试用例的 `headers`、`body`、`expected_body` 以文本方式存储

## 重要实现细节
- 已在核心模型中显式定义 SQLAlchemy `relationship(..., back_populates=...)` 映射
- 时间字段使用 Unix 时间戳整数，而不是 `datetime`
- `password` 当前为哈希存储（PBKDF2-SHA256），并兼容历史明文用户在登录时自动迁移

## 模型治理细则（阶段 1 已落地）

### 约束（Constraints）
- `users`：用户名非空、`role` 枚举约束（`admin/user`）、`created_at` 非负
- `projects`：同一用户下项目名唯一（`owner_id + name`）、项目名非空、`created_at` 非负
- `api_test_cases`：同一项目下用例名唯一（`project_id + name`）、`method` 限定为 `GET/POST/PUT/PATCH/DELETE`、`expected_status` 约束为 `100~599`
- `test_runs`：`status` 限定为 `success/failed/error`、`actual_status` 合法范围校验、`duration_ms` 非负
- `schedule_tasks`：同一项目下任务名唯一、`enabled` 二值约束、`target_type` 枚举约束
- `run_queue`：`run_type`/`target_type`/`status`/`scheduled_by` 枚举约束、`priority` 范围约束、`finished_at >= started_at`
- `audit_logs`：`result` 限定为 `success/failed`

### 索引（Indexes）
- 新增/强化了高频查询索引，包括：
  - `projects(owner_id)`
  - `api_test_cases(project_id, updated_at)`
  - `test_runs(test_case_id, created_at)`
  - `schedule_tasks(project_id, enabled)`
  - `run_queue(project_id, status, created_at)`
  - `audit_logs(action, created_at)`、`audit_logs(user_id, created_at)`

### 级联（Cascade）
- ORM 关系层已设置核心级联删除：
  - `User -> Project/ScheduleTask`
  - `Project -> ApiTestCase/ScheduleTask/RunQueue`
  - `ApiTestCase -> TestRun`
- 删除父实体时，关联子实体会同步清理，避免孤儿数据

### 生命周期（Lifecycle）
- 时间字段统一采用 Unix 时间戳
- 关键实体（如 `ApiTestCase`、`ScheduleTask`）补齐 `created_at/updated_at` 默认值与 `updated_at` 自动更新策略
