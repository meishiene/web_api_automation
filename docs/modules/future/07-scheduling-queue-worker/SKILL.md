# 模块技能：调度、队列与 Worker

## 0. 强制执行约束（必须遵守）

- 开发前先读取仓库根 `AGENTS.md` 与 `docs/project/project-progress.md`
- 本模块关联阶段为阶段 4；当前总阶段为“阶段 2 收尾中 + 阶段 3 收尾中 + 阶段 4 启动中”
- 涉及逻辑或功能代码改动时，必须补充/更新测试并执行最小相关测试集；影响公共模块时补充回归测试
- 改动影响功能实现、模块状态、架构分层或路线图时，必须同步更新 `docs/project/project-progress.md`
- 必须检查 `docs/architecture/企业级自动化测试平台系统架构规划.md` 是否需要同步修订
- 阶段状态变化时，必须同步更新对应阶段目录下 `SKILL.md`

## 1. 模块目标

构建可计划、可排队、可分发、可恢复的执行中台能力，并支持 API/Web 任务统一进入调度与执行链路。

## 2. 当前状态（2026-03-16）

- 阶段状态：启动中（首批闭环已落地）
- 关联阶段：阶段 4
- 风险等级：高
- 已完成项：
  - S4-01：统一执行编排骨架（ExecutionTask/ExecutionJob + API/Web 单用例接入）
  - S4-02：调度器最小可用（`schedule_tasks` 最小 API + trigger 入队）
  - S4-03：队列与 Worker 最小闭环（任务领取、占位执行回写、心跳上报）
  - S4-04：执行管理最小可视化（Scheduling Dashboard + 路由入口）
- 待完成项：
  - S4-05：阶段验收与切换准备

## 3. 范围边界

### In Scope
- 调度任务管理（一次性/定频/Cron）
- 队列入队、领取、状态回写
- Worker 心跳与最小健康状态上报
- 超时、重试、取消、优先级策略（持续增强）

### Out of Scope
- 跨地域调度与灾备体系（后续阶段扩展）
- 企业级弹性调度优化（后续阶段扩展）

## 4. 关键任务（当前优先级）

1. 完成 S4-05：阶段验收清单与回归验证
2. 增强队列消费策略（超时、重试、取消）并补齐测试
3. 逐步从占位执行迁移到真实 Worker 消费执行

## 5. 当前交付物

- 调度任务 API：`app/api/schedule_tasks.py`
- 队列/Worker API：`app/api/queue_worker.py`
- 队列模型：`app/models/run_queue.py`
- Worker 心跳模型：`app/models/worker_heartbeat.py`
- 队列/Worker Schema：`app/schemas/queue_worker.py`

## 6. 测试要求

- 队列领取与状态回写一致性测试
- Worker 心跳上报与项目权限校验测试
- 调度触发与入队链路回归测试

## 7. 完成定义（DoD）

- 至少一条任务可通过 `run_queue` 被 Worker 领取并完成状态回写
- Worker 心跳可稳定上报并可追踪最近状态
- API/Web 任务可持续接入统一调度与队列链路
