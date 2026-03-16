# 阶段 4 验收清单（S4 Acceptance Checklist）

## 1. 验收范围
- 验收阶段：阶段 4（调度与分布式执行）
- 验收日期：2026-03-16（口径定义版）
- 验收口径：以 `app/`、`frontend/src/`、`tests/backend/` 当前代码事实与测试结果为准
- 当前阶段状态：S4-01~S4-04 已完成，S4-05 进行中（验收与切换准备）

## 2. 功能验收项（必须满足）

| 编号 | 验收项 | 通过标准（Pass 条件） | 证据 |
| --- | --- | --- | --- |
| A4-01 | 统一编排骨架可用 | API/Web 单用例执行均走统一编排入口，`execution_tasks/execution_jobs` 可落库 | `app/services/execution_orchestrator.py`、`tests/backend/test_execution_orchestration_skeleton.py` |
| A4-02 | 调度最小 API 可用 | `schedule_tasks` 的列表/创建/更新/删除/触发接口可用，触发后可入 `run_queue` | `app/api/schedule_tasks.py`、`tests/backend/test_schedule_tasks_api.py` |
| A4-03 | 队列与 Worker 最小闭环 | 队列任务可被领取、执行占位、回写终态，Worker 心跳可上报并可查询 | `app/api/queue_worker.py`、`tests/backend/test_queue_worker_api.py` |
| A4-04 | 最小可视化可用 | 前端可查看队列任务、Worker 心跳、队列详情，且可从项目页进入 | `frontend/src/views/SchedulingDashboard.vue` |
| A4-05 | 文档与阶段口径一致 | 阶段 4 清单、项目进度、07 模块 SKILL、架构文档已同步 | `docs/project/*`、`docs/modules/future/07-scheduling-queue-worker/SKILL.md`、`docs/architecture/*` |

## 3. 质量门禁（必须通过）

| 门禁项 | 目标命令 | 通过标准 |
| --- | --- | --- |
| 后端最小回归 | `.\.venv\Scripts\python -m pytest tests/backend/test_queue_worker_api.py tests/backend/test_schedule_tasks_api.py` | 全部通过 |
| 后端全量回归 | `.\.venv\Scripts\python -m pytest` | 全部通过（允许非阻塞 warning） |
| 前端构建 | `npm run build`（frontend） | 构建成功 |
| 迁移链路（建议） | `alembic upgrade head -> downgrade f2a1c4d8b9e3 -> upgrade head` | 升降级成功 |

## 4. 非功能验收口径（阶段 4 出口）

- 可观测性：关键动作有审计记录（`schedule_task.*`、`run_queue.*`、`worker.heartbeat`）
- 可恢复性：可识别队列终态（`success/failed/error`），可区分 `queued/running` 任务
- 可维护性：接口、模型、迁移、测试、文档四类资产齐备
- 可切换性：S4-05 完成后可进入阶段 5（报告分析与治理）

## 5. 后续真实消费策略（从占位执行到真实 Worker）

### R1：真实消费主循环（优先级 P0）
- 建立独立 Worker 进程循环：`claim -> execute -> complete -> heartbeat`
- 增加 Worker 启停语义：启动注册、优雅停止、中断回写
- 将 `execute-once` 从演示接口升级为内部调度流程，不作为主执行入口

### R2：执行一致性与幂等（优先级 P0）
- 引入“领取租约”机制（lease/timeout）防止重复消费
- 增加领取冲突保护（数据库层原子更新优先）
- 明确状态机约束：`queued -> running -> success/failed/error`

### R3：失败恢复与重试（优先级 P1）
- 在队列层引入重试字段（attempt、max_attempts、next_retry_at）
- 区分可重试失败与不可重试失败
- 增加死信策略（DLQ 或等价字段标记）与治理脚本

### R4：卡死任务回收（优先级 P1）
- 建立“心跳超时扫描”任务：识别长时间 `running` 且心跳缺失任务
- 对卡死任务执行回收策略：重试或失败终结，并落审计

### R5：执行域收敛（优先级 P1）
- 将 API/Web 执行统一沉淀到编排层任务模型，不在路由层分散处理终态
- 固化运行结果结构（输入快照、执行摘要、错误分类）用于阶段 5 报告

## 6. 阶段 4 验收结论口径（通过条件）

满足以下条件可判定阶段 4 验收通过：
1. A4-01~A4-05 全部满足。
2. 质量门禁中的后端最小回归与前端构建全部通过。
3. 阶段文档与架构文档已同步，且不存在“占位能力标记为完成”的表述。
4. 真实消费策略 R1~R5 已进入明确排期（至少完成 R1 的任务拆解与负责人归属）。


## 7. S4-05 Execution Record (2026-03-16)

- Backend full regression: `python -m pytest` -> **95 passed, 2 warnings**.
- Frontend build gate: `npm run build` -> **passed**.
- Migration chain check: `alembic upgrade head -> downgrade f2a1c4d8b9e3 -> upgrade head` -> **failed**.

## 8. Risk Closure Matrix (S4-05)

| Risk ID | Description | Current State | Closure Plan | Owner/Phase |
| --- | --- | --- | --- | --- |
| RISK-S4-001 | Alembic runtime revision drift: DB current shows `01fcc228897e` while code head is `2c1b7f9a4d10`; upgrade attempts hit `audit_logs_archive already exists`. | Open (blocking migration gate) | Add one-time migration repair playbook/script for legacy SQLite revision stamping and idempotent archive table handling, then rerun migration chain. | S4-05 |
| RISK-S4-002 | FastAPI startup uses deprecated `on_event`, raises warnings in regression. | Open (non-blocking) | Move startup logic to lifespan handler in next maintenance slice. | post-S4 |
| RISK-S4-003 | Worker execution is still placeholder (`execute-once`) not full daemon loop. | Open (known scope) | Execute R1 plan: real worker loop (`claim->execute->complete->heartbeat`) and retire placeholder from main path. | next phase |

## 9. S4-05 Gate Decision

- Regression gates passed: **YES** (backend + frontend).
- Migration gate passed: **NO** (blocked by RISK-S4-001).
- Stage-4 final acceptance decision: **HOLD** until migration risk is closed.
