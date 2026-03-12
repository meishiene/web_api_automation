# 结构化日志与审计日志规范

## 1. 目标

本规范用于统一后端日志输出格式与审计记录口径，确保具备以下能力：
- 可检索（按请求、用户、资源、错误码快速定位）
- 可追踪（请求链路可回放）
- 可审计（关键写操作可追溯）

## 2. 结构化日志规范

### 2.1 输出格式
- 格式：JSON（单行）
- 输出目标：标准输出（stdout）
- 编码：UTF-8

### 2.2 必填字段
- `timestamp`：UTC 时间
- `level`：日志级别
- `logger`：日志器名称
- `message`：日志消息

### 2.3 常用扩展字段
- `event`：事件类型（如 `http_request`、`app_exception`、`audit_log`）
- `request_id`：请求标识
- `method` / `path`：HTTP 请求信息
- `status_code`：HTTP 状态码
- `duration_ms`：请求耗时（毫秒）
- `client_ip`：客户端 IP
- `user_id`：当前用户 ID（可为空）
- `code`：统一错误码
- `action` / `resource_type` / `resource_id` / `result`：审计相关字段

### 2.4 级别约定
- `INFO`：正常业务事件（请求完成、审计落库）
- `WARNING`：可预期异常（业务异常、校验失败、鉴权失败）
- `ERROR/EXCEPTION`：系统异常（未处理错误）

## 3. 请求追踪规范

- 每个请求必须具备 `request_id`
- 优先透传客户端 `X-Request-ID`，缺失时服务端生成 UUID
- 响应头必须回写 `X-Request-ID`
- 错误响应体必须包含 `error.request_id`

## 4. 审计日志规范

### 4.1 审计范围
必须记录以下“写操作”：
- 用户认证关键动作（注册、登录、刷新令牌）
- 项目创建、修改、删除
- 测试用例创建、修改、删除
- 测试执行触发

### 4.2 审计数据表
- 表：`audit_logs`
- 核心字段：
  - `user_id`
  - `action`
  - `resource_type`
  - `resource_id`
  - `result`
  - `request_id`
  - `client_ip`
  - `method` / `path`
  - `details`
  - `created_at`

归档表：
- 表：`audit_logs_archive`
- 关键字段：`original_id`、`archived_at` 以及 `audit_logs` 的核心审计字段镜像
- 用途：承接超出活动保留周期的历史审计记录

### 4.3 动作命名约定
- 格式：`<domain>.<verb>`
- 示例：
  - `auth.register`
  - `auth.login`
  - `project.create`
  - `test_case.update`
  - `test_run.execute`

### 4.4 审计结果约定
- 成功：`success`
- 失败：`failed`（后续可扩展）

## 5. 统一错误码规范

### 5.1 响应结构
```json
{
  "success": false,
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project not found",
    "request_id": "..."
  },
  "detail": "Project not found"
}
```

### 5.2 最小错误码集
- 鉴权类：`NOT_AUTHENTICATED`、`INVALID_TOKEN`、`INVALID_TOKEN_TYPE`、`INVALID_TOKEN_SUBJECT`
- 用户类：`USER_NOT_FOUND`、`USERNAME_ALREADY_EXISTS`、`INVALID_CREDENTIALS`
- 业务类：`PROJECT_NOT_FOUND`、`TEST_CASE_NOT_FOUND`
- 通用类：`VALIDATION_ERROR`、`INTERNAL_SERVER_ERROR`

## 6. 开发与测试要求

- 新增写操作接口时，必须同步接入审计记录
- 新增异常分支时，必须映射到统一错误码
- 涉及日志/审计逻辑改动时，必须补测试并执行回归
- 当前基线测试命令：`.\.venv\Scripts\python -m pytest`

## 7. 查询、归档与保留策略

### 7.1 查询能力
- 接口：`GET /api/audit-logs/`
- 支持过滤：`action`、`result`、`request_id`、`path_contains`、`created_from`、`created_to`
- 支持分页：`page`、`page_size`
- 支持查询归档：`include_archived=true`
- 权限规则：普通用户仅可查询本人日志；`admin` 可全局查询并支持 `user_id` 过滤

### 7.2 归档策略
- 将超过活动保留期的记录从 `audit_logs` 迁移到 `audit_logs_archive`
- 归档时保留原始字段与 `original_id` 映射，便于追溯

### 7.3 保留策略
- 活动日志保留天数：`AUDIT_LOG_ACTIVE_RETENTION_DAYS`（默认 30）
- 归档日志保留天数：`AUDIT_LOG_ARCHIVE_RETENTION_DAYS`（默认 180）
- 批处理大小：`AUDIT_LOG_RETENTION_BATCH_SIZE`（默认 500）

执行脚本：
```bash
.\.venv\Scripts\python .\scripts\audit-governance-run.py
```

Dry-run：
```bash
.\.venv\Scripts\python .\scripts\audit-governance-run.py --dry-run
```

治理接口（admin）：
```bash
POST /api/audit-logs/governance/run
```
