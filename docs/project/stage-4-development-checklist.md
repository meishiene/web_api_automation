# 阶段 4 开发清单（调度与分布式执行）

> 目的：为阶段 4 提供可持续维护的单一事实来源（SSOT），用于追踪 **已完成 / 进行中 / 待完成**，并约束交付物、测试门禁与 DoD。
>
> 适用规则：
> - 任何涉及逻辑/功能代码改动：先补/更测试，再实现；并执行最小相关测试集（公共模块需补回归）。
> - 若改动影响模块状态、阶段进度或路线图：同轮同步更新 `docs/project/project-progress.md` 的“最近更新记录”，并检查 `docs/architecture/企业级自动化测试平台系统架构规划.md` 是否需要同步修订。

## 0. 阶段定位（以当前代码与进度基线为准）

- 阶段名称：阶段 4 调度与分布式执行
- 当前状态：启动中（基础骨架建设中）
- 当前总阶段：阶段 2 收尾中 + 阶段 3 收尾中 + 阶段 4 启动中（详见 `docs/project/project-progress.md`）
- 本阶段目标：把平台从“手工触发执行”升级为“可计划、可排队、可分发、可恢复”的执行中台。

## 1. 范围边界

### In Scope（阶段 4）
- 统一执行任务模型（Execution Task/Job 基础抽象）
- 调度任务管理（一次性、定频、Cron 预留）
- 队列入队/出队与基础消费机制
- Worker 生命周期管理（注册、心跳、健康状态）
- 失败重试、取消、超时、优先级
- 最小执行管理页面与任务追踪视图

### Out of Scope（本阶段不做）
- 跨地域调度与容灾编排
- 企业级容量调度优化（自动弹性扩缩容）
- 报告中心深度分析（阶段 5）

## 2. 阶段 4 工作分解（按可交付切片推进）

### S4-00：阶段 4 方案与边界收敛（必做）
- 状态：已完成
- 交付物：
  - 阶段 4 SSOT 清单（本文件）
  - 与阶段 3 的边界说明（阶段 3 收尾项转风险托管/缺陷收敛）
  - 统一任务命名、状态机与接口边界草案
- 最小测试集：
  - 无（文档类）
- DoD：
  - 阶段 4 分解项、门禁与顺序明确

### S4-01：统一执行编排骨架（06 模块）
- 状态：已完成
- 交付物：
  - `ExecutionTask` / `ExecutionJob` 领域模型（可先最小字段）
  - API/Web 执行器适配层接口
  - 统一状态枚举与错误分类映射
- 最小测试集：
  - 状态流转单测
  - API/Web 适配接口一致性测试
- DoD：
  - API/Web 执行链路可落到统一编排入口（哪怕暂不异步）

#### 交付物落地情况（2026-03-16）

- 领域模型与迁移：
  - `app/models/execution_task.py`
  - `app/models/execution_job.py`
  - `migrations/versions/f2a1c4d8b9e3_phase4_execution_orchestration_core.py`
- 编排与适配骨架：
  - `app/services/execution_contract.py`（ExecutionAdapter 协议）
  - `app/services/execution_status.py`（统一状态/错误映射）
  - `app/services/execution_orchestrator.py`（统一编排入口）
- 现有链路接入：
  - API 单用例执行接入统一编排：`app/api/test_runs.py`
  - Web 单用例执行接入统一编排：`app/api/web_test_runs.py`
- 最小测试集：
  - 新增：`tests/backend/test_execution_orchestration_skeleton.py`
  - 回归通过：`.\.venv\Scripts\python -m pytest tests/backend/test_execution_orchestration_skeleton.py tests/backend/test_test_runs_api.py tests/backend/test_web_test_runs_api.py tests/backend/test_unified_results_api.py`

### S4-02：调度器最小可用（07 模块）
- 状态：已完成
- 交付物：
  - `schedule_tasks` 业务字段扩展与接口
  - 基础触发器（一次性 + 定频）
  - 调度日志与触发记录
- 最小测试集：
  - 触发准确性测试
  - 错误输入与权限校验测试
- DoD：
  - 可配置并触发最小调度任务

#### 交付物落地情况（2026-03-16）

- 最小 API：
  - `GET /api/schedule-tasks/project/{project_id}`（列表）
  - `POST /api/schedule-tasks`（创建）
  - `PUT /api/schedule-tasks/{task_id}`（更新）
  - `DELETE /api/schedule-tasks/{task_id}`（删除）
  - `POST /api/schedule-tasks/{task_id}/trigger`（手动触发）
- 触发链路：
  - `schedule_task -> run_queue` 入队（`scheduled_by=scheduler`，`status=queued`）
  - 审计动作：`schedule_task.create/update/delete/trigger`
- 代码落地：
  - `app/api/schedule_tasks.py`
  - `app/schemas/schedule_task.py`
  - `app/main.py`（注册 `/api/schedule-tasks` 路由）
- 最小测试集：
  - 新增：`tests/backend/test_schedule_tasks_api.py`
  - 回归通过：`.\.venv\Scripts\python -m pytest tests/backend/test_schedule_tasks_api.py tests/backend/test_execution_orchestration_skeleton.py tests/backend/test_test_runs_api.py tests/backend/test_web_test_runs_api.py`

### S4-03：队列与 Worker 最小闭环（07 模块）
- 状态：已完成
- 交付物：
  - `run_queue` 入队/出队机制
  - Worker 心跳与任务领取
  - 超时、重试、取消最小策略
- 最小测试集：
  - 入队/出队一致性测试
  - Worker 故障恢复测试
  - 超时重试与取消场景测试
- DoD：
  - 至少一条任务可通过队列由 Worker 执行并回写状态

#### 交付物落地情况（2026-03-16）

- 最小 API：
  - `POST /api/run-queue/claim`（领取队列任务并置为 `running`）
  - `POST /api/run-queue/{queue_item_id}/complete`（Worker 回写终态 `success/failed/error`）
  - `POST /api/run-queue/worker/execute-once`（Worker 真实执行一次：领取 + 执行 + 回写）
  - `POST /api/run-queue/worker/heartbeat`（Worker 心跳上报）
- 数据模型：
  - 新增 `worker_heartbeats`（项目级 Worker 心跳状态）
  - 新增迁移：`migrations/versions/2c1b7f9a4d10_phase4_worker_heartbeat_minimal_loop.py`
- 代码落地：
  - `app/api/queue_worker.py`
  - `app/schemas/queue_worker.py`
  - `app/models/worker_heartbeat.py`
  - `app/main.py`（注册 `/api/run-queue` 路由）
- 最小测试集：
  - 新增：`tests/backend/test_queue_worker_api.py`
  - 回归通过：`.\.venv\Scripts\python -m pytest tests/backend/test_queue_worker_api.py tests/backend/test_schedule_tasks_api.py`

### S4-04：执行管理最小可视化（前端）
- 状态：已完成
- 交付物：
  - 调度任务列表页（状态、下次触发、最近结果）
  - 队列任务/Worker 状态页（最小监控）
  - 执行任务详情页（统一查看 API/Web 执行任务生命周期）
- 最小测试集：
  - `npm run build`（frontend）
- DoD：
  - 可在前端查看并追踪阶段 4 新增核心对象状态

#### 交付物落地情况（2026-03-16）

- 最小可视化页面：
  - `frontend/src/views/SchedulingDashboard.vue`（队列任务列表 + Worker 心跳列表 + 队列详情弹窗）
- 前端路由与入口：
  - `frontend/src/router/index.js` 新增 `/project/:projectId/scheduling`
  - `frontend/src/views/TestCaseList.vue` 新增“调度与Worker”入口按钮
  - `frontend/src/App.vue` 侧栏新增“调度与Worker”导航项
- 前端 API 封装：
  - `frontend/src/api/queueWorker.js`（队列列表/详情、Worker 心跳查询）
- 后端查询接口支撑：
  - `GET /api/run-queue/project/{project_id}`
  - `GET /api/run-queue/{queue_item_id}`
  - `GET /api/run-queue/worker/heartbeats/project/{project_id}`
- 最小测试集：
  - 后端回归：`.\.venv\Scripts\python -m pytest tests/backend/test_queue_worker_api.py tests/backend/test_schedule_tasks_api.py`
  - 前端构建：`npm run build`（frontend）

### S4-05：阶段验收与切换准备
- 状态：验收中（前端构建门禁需在可运行构建的环境/CI复核）
- 交付物：
  - 阶段 4 验收清单文档（`stage-4-acceptance-checklist.md`）
  - 全量回归与风险清单
  - 真实 Worker 消费主循环（R1）最小可运行实现（服务层 + 脚本）
- 最小测试集：
  - 后端回归：`.\.venv\Scripts\python -m pytest`
  - 前端构建：`npm run build`（frontend）
- DoD：
  - 阶段 4 核心能力可稳定运行，具备进入阶段 5 的前置条件


#### Delivery Status (2026-03-16, criteria defined)


## 3. 进度看板（手工维护，保守标记）

| 条目 | 状态 | 备注 |
| --- | --- | --- |
| S4-00 | 已完成 | 阶段 4 SSOT 建立，边界与顺序明确 |
| S4-01 | 已完成 | 执行任务/作业模型 + 编排入口 + API/Web 单用例接入 |
| S4-02 | 已完成 | schedule_tasks 最小 API + trigger 入队链路 + 审计 |
| S4-03 | 已完成 | run_queue 领取/回写 + Worker 心跳 + execute-once 真实执行闭环 |
| S4-04 | 已完成 | 调度/队列/Worker 最小可视化页面与路由入口已落地 |
| S4-05 | in_progress | 后端全量回归与迁移链路已通过；前端构建门禁需在可运行构建的环境/CI复核 |

## 4. 阶段 4 完成定义（DoD）

- 任务可被调度并进入队列
- Worker 可稳定消费任务并回写状态
- API/Web 执行任务具备统一追踪与最小可视化能力
- 故障场景具备最小恢复策略（超时/重试/取消）

## 5. 最近更新记录

### 2026-03-16
- 新增阶段 4 开发清单：用于后续阶段 4 迭代的进度追踪与门禁对齐
- 完成 S4-00：明确阶段 4 工作分解、执行顺序、测试门禁与 DoD
- 完成 S4-01：落地统一执行编排骨架（ExecutionTask/ExecutionJob + 编排入口 + API/Web 适配协议）
- 完成 S4-01 测试门禁：新增编排骨架测试并通过相关回归（14 passed）
- 完成 S4-02：落地 `schedule_tasks` 最小 API 与触发入队链路（`run_queue`）
- 完成 S4-02 测试门禁：新增调度任务 API 测试并通过相关回归（14 passed）
- 完成 S4-03：落地队列领取、Worker 最小执行回写与心跳接口（`/api/run-queue/*`）
- 完成 S4-03 测试门禁：新增队列/Worker 闭环测试并通过最小回归（6 passed）
- 完成 S4-04：落地执行管理最小可视化页面（Scheduling Dashboard）及入口路由
- 完成 S4-04 测试门禁：后端最小回归通过（6 passed）+ 前端构建通过（vite build）

- S4-05 started: phase-4 acceptance criteria documented in `stage-4-acceptance-checklist.md`.
- Real-consumption strategy defined: R1~R5 (worker loop, idempotent claim, retry/recovery, execution convergence).


- S4-05 execution: backend full regression passed (95 passed) and migration chain recheck passed after legacy SQLite revision repair; frontend build gate is blocked in this environment (spawn EPERM), pending CI/standard dev validation.

- Closed RISK-S4-001: added `scripts/legacy_sqlite_revision_repair.py`, repaired legacy SQLite revision drift, and revalidated migration chain.
- S4-05 推进：落地 `app/services/queue_worker_runtime.py`，将 `execute-once` 从占位回写升级为真实执行链路（`claim -> execute -> complete -> heartbeat`）。
- S4-05 推进：新增 `scripts/run_queue_worker_loop.py` 独立 Worker 循环脚本，支持持续消费与优雅退出离线心跳回写。
- S4-05 测试门禁：更新 `tests/backend/test_queue_worker_api.py` 覆盖真实执行路径，并通过回归 `.\.venv\Scripts\python -m pytest tests/backend/test_queue_worker_api.py tests/backend/test_schedule_tasks_api.py tests/backend/test_test_runs_api.py tests/backend/test_execution_orchestration_skeleton.py`（14 passed）。
