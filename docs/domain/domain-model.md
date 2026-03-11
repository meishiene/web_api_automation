# Domain Model

## 核心实体

### User
- **表名**：`users`
- **字段**：`id`、`username`、`password`、`created_at`
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
- 测试结果必须关联到某个测试用例
- 测试用例的 `headers`、`body`、`expected_body` 以文本方式存储

## 重要实现细节
- 当前没有显式 SQLAlchemy relationship 定义，主要通过外键和查询 join 组织关联
- 时间字段使用 Unix 时间戳整数，而不是 `datetime`
- `password` 当前为明文存储，属于 MVP 实现
