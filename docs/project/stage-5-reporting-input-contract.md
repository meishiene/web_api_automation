# 阶段 5 报告输入契约（S5-01）

## 1. 文档目标

本契约定义阶段 5 报告中心的统一输入口径，作为 API/Web 执行记录进入报告聚合层的唯一字段标准。  
口径以当前代码事实为准，来源包括：

- `app/models/test_run.py`
- `app/models/web_test_run.py`
- `app/schemas/test_run.py`
- `app/api/test_runs.py`（`/api/test-runs/project/{project_id}/unified-results`）
- `app/services/reporting_input.py`（统一映射、失败分类、统计口径实现）
- `tests/backend/test_reporting_input_service.py`（S5-01 最小测试集）

## 2. 统一输入模型（ReportInputRun v1）

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `run_type` | enum(`api`,`web`) | 是 | 执行来源类型 |
| `run_id` | int | 是 | 执行记录主键 |
| `project_id` | int | 是 | 项目标识 |
| `case_id` | int | 是 | 用例标识（API: `test_case_id`，Web: `web_test_case_id`） |
| `case_name` | string | 是 | 用例名称 |
| `status` | enum(`running`,`success`,`failed`,`error`) | 是 | 统一执行状态 |
| `duration_ms` | int/null | 否 | 执行耗时（毫秒） |
| `error_message` | string/null | 否 | 错误信息 |
| `created_at` | int | 是 | 创建时间（Unix 秒） |
| `started_at` | int/null | 否 | 开始时间（Web 有，API 为空） |
| `finished_at` | int/null | 否 | 结束时间（Web 有，API 为空） |
| `artifact_dir` | string/null | 否 | 产物目录（Web） |
| `artifacts` | string[]/null | 否 | 产物列表（Web） |
| `detail_api_path` | string | 是 | 详情接口路径 |
| `failure_category` | enum/null | 否 | 失败分类（报告聚合层内部字段，见 4.3） |

## 3. 源模型映射规则

### 3.1 API 执行记录（`test_runs`）映射

- `run_type` = `api`
- `run_id` = `test_runs.id`
- `project_id` = `api_test_cases.project_id`（通过 join 获取）
- `case_id` = `api_test_cases.id`
- `case_name` = `api_test_cases.name`
- `status` = `test_runs.status`（取值仅 `success/failed/error`）
- `duration_ms` = `test_runs.duration_ms`
- `error_message` = `test_runs.error_message`
- `created_at` = `test_runs.created_at`
- `started_at` = `null`
- `finished_at` = `null`
- `artifact_dir` = `null`
- `artifacts` = `null`
- `detail_api_path` = `/api/test-runs/{run_id}`

### 3.2 Web 执行记录（`web_test_runs`）映射

- `run_type` = `web`
- `run_id` = `web_test_runs.id`
- `project_id` = `web_test_runs.project_id`
- `case_id` = `web_test_cases.id`
- `case_name` = `web_test_cases.name`
- `status` = `web_test_runs.status`（取值 `running/success/failed/error`）
- `duration_ms` = `web_test_runs.duration_ms`
- `error_message` = `web_test_runs.error_message`
- `created_at` = `web_test_runs.created_at`
- `started_at` = `web_test_runs.started_at`
- `finished_at` = `web_test_runs.finished_at`
- `artifact_dir` = `web_test_runs.artifact_dir`
- `artifacts` = `json.loads(web_test_runs.artifacts_json)`（非数组/解析失败时置 `null`）
- `detail_api_path` = `/api/web-test-runs/{run_id}`

## 4. 状态与统计口径

### 4.1 状态口径

- 统一状态域：`running/success/failed/error`
- API 历史数据不含 `running`，直接按现状映射
- Web 含 `running`，在报告汇总中单独计入“进行中”

### 4.2 核心指标口径（阶段 5 最小集）

- `total_count`：时间窗口内记录总数（包含 `running`）
- `completed_count`：`success + failed + error`
- `success_count`：`status=success`
- `failed_count`：`status=failed`
- `error_count`：`status=error`
- `running_count`：`status=running`
- `pass_rate`：`success_count / completed_count`（`completed_count=0` 时为 `0`）
- `fail_rate`：`(failed_count + error_count) / completed_count`（`completed_count=0` 时为 `0`）

### 4.3 失败分类字典与映射规则（v1）

- 分类字典：`assertion_failure / timeout / network_error / execution_error / test_failure`
- 状态优先级规则：
  - `status=error` -> `execution_error`
  - `status=success` 或 `running` -> `null`（不参与失败分类）
- `status=failed` 时按 `error_message` 文本规则映射（忽略大小写）：
  - 命中 `assert / expect / mismatch` -> `assertion_failure`
  - 命中 `timeout / timed out` -> `timeout`
  - 命中 `connection / dns / network` -> `network_error`
  - 未命中以上规则 -> `test_failure`

## 5. 时间窗口口径

- 报告筛选主时间字段统一使用 `created_at`
- 趋势聚合在阶段 5 最小闭环按 `created_at` 进行分桶（日/周）
- `started_at/finished_at` 用于执行时长与可观测扩展，不作为首版筛选主键

## 6. 冲突与异常处理规则

- 非法状态值：不进入聚合，记录审计告警（后续实现）
- `duration_ms < 0`：视为脏数据，聚合时当作 `null`
- `artifacts_json` 解析失败：`artifacts = null`，不阻断主链路
- `created_from > created_to`：按现有接口约束返回 `400 VALIDATION_ERROR`

## 7. 与现有接口一致性约束

- 报告层输入必须兼容 `UnifiedRunResponse` 字段集
- 任何新增字段不得破坏 `GET /api/test-runs/project/{project_id}/unified-results` 既有响应结构
- `failure_category` 当前仅在报告聚合层内部使用，不写入 `UnifiedRunResponse` 响应字段
- 若新增报告字段，必须先更新本契约，再落地实现

## 8. S5-01 完成判定（文档侧）

满足以下条件视为 S5-01 口径冻结完成：

1. API/Web 字段映射规则完整可执行；
2. 状态与核心统计口径明确且无冲突；
3. 异常与边界处理规则可复现；
4. 本文档与 `stage-5-development-checklist.md`、`stage-5-acceptance-checklist.md` 已同步引用。
