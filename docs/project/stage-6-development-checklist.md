# 阶段 6 开发清单（企业集成与生态完善）

> 目的：为阶段 6 提供可持续维护的单一事实来源（SSOT），用于追踪 **已完成 / 进行中 / 待完成**，并约束交付物、测试门禁与 DoD。
>
> 适用规则：
> - 任何涉及逻辑/功能代码改动：先补/更测试，再实现；并执行最小相关测试集（公共模块需补回归）。
> - 若改动影响模块状态、阶段进度或路线图：同轮同步更新 `docs/project/project-progress.md` 的“最近更新记录”，并检查 `docs/architecture/企业级自动化测试平台系统架构规划.md` 是否需要同步修订。
> - 任一时刻仅允许一个条目标记为 `in_progress`。

## 0. 阶段定位（以当前代码与进度基线为准）

- 阶段名称：阶段 6 企业集成与生态完善
- 当前状态：已完成验收（S6-08 已完成，进入阶段切换准备）
- 当前总阶段：阶段 2 收尾中 + 阶段 3 收尾中 + 阶段 4 已完成验收 + 阶段 5 已完成验收 + 阶段 6 已完成验收（详见 `docs/project/project-progress.md`）
- 本阶段目标：把平台从“可执行、可分析”升级为“可接入企业研发流程、可治理、可运营”的企业级集成平台。

## 1. 中断恢复指引（必须遵守）

1. 先看本文“3. 进度看板”，确认唯一 `in_progress` 条目。
2. 再看本文“5. 最近更新记录”最后一条，确认上一步实际动作与结果。
3. 若要判断是否可切换阶段，先看 `docs/project/stage-6-acceptance-checklist.md` 的通过条件与执行记录。
4. 若改动影响全局阶段口径，同步更新 `docs/project/project-progress.md` 与架构总纲。
5. 若阶段状态发生变化，同步更新 `docs/modules/future/09-enterprise-integrations/SKILL.md`。

## 2. 阶段 6 工作分解（按可交付切片推进）

### S6-00：阶段 6 SSOT 与验收口径落盘（必做）
- 状态：completed
- 交付物：
  - 阶段 6 开发清单（本文）
  - 阶段 6 验收清单（`docs/project/stage-6-acceptance-checklist.md`）
  - 项目进度、架构总纲、模块 SKILL 口径同步
- 最小测试集：
  - 无（文档类）
- DoD：
  - 阶段 6 任务编号、门禁、DoD、验收口径可独立阅读与执行

### S6-01：集成底座与配置中心
- 状态：completed
- 交付物：
  - 集成配置域模型（集成类型、凭据引用、启停状态、项目作用域）
  - 集成配置 API（最小 CRUD + 鉴权 + 审计）
  - 凭据脱敏策略与校验规则
- 最小测试集：
  - 配置 API 权限与越权测试
  - 凭据脱敏与字段校验测试
- DoD：
  - 可安全创建/维护企业集成配置，且关键动作可审计

### S6-02：事件总线与签名 Webhook 接入
- 状态：completed
- 交付物：
  - 统一集成事件模型（事件类型、载荷、幂等键、重试状态）
  - Webhook 入站签名校验（HMAC）
  - 事件入库与重放/重试基础能力
- 最小测试集：
  - 签名校验成功/失败测试
  - 幂等去重与重放测试
- DoD：
  - 入站回调具备鉴权、幂等、审计三项基础能力

### S6-03：CI/CD 集成最小闭环
- 状态：completed
- 交付物：
  - Pipeline 触发接口（至少 1 种提供商，建议 GitHub Actions）
  - 执行状态回调映射到平台执行结果
  - 项目级流水线触发策略（手动/事件触发）
- 最小测试集：
  - 触发成功/失败与重试测试
  - 回调状态映射一致性测试
- DoD：
  - 至少一条“平台触发 -> CI 执行 -> 回调收敛”链路打通

### S6-04：通知中心最小闭环
- 状态：completed
- 交付物：
  - 事件订阅配置（按项目/事件类型）
  - 通知通道适配器（先落地 Webhook/邮件二选一）
  - 通知模板与发送日志
- 最小测试集：
  - 订阅筛选命中测试
  - 发送失败重试与死信测试
- DoD：
  - 关键事件可被稳定投递并可追踪

### S6-05：缺陷平台联动最小闭环
- 状态：pending
- 交付物：
  - 缺陷平台适配层（先落地 Jira 或 禅道其一）
  - 失败执行到缺陷单的字段映射规则
  - 去重策略（同一失败模式不重复建单）
- 最小测试集：
  - 建单/更新路径测试
  - 去重与字段映射测试
- DoD：
  - 失败治理可一键联动缺陷平台并保持可追踪

### S6-06：SSO/OAuth2 最小接入
- 状态：pending
- 交付物：
  - 外部身份提供商配置（最小 OAuth2）
  - 登录绑定策略（新用户/已存在用户映射）
  - 基础会话与回调安全校验
- 最小测试集：
  - OAuth2 回调成功/失败测试
  - 账号绑定冲突测试
- DoD：
  - 支持企业身份源最小登录闭环

### S6-07：治理增强与运营可观测
- 状态：pending
- 交付物：
  - 集成域审计事件补齐
  - 失败重试/死信治理接口
  - 集成健康看板（最小可视化）
- 最小测试集：
  - 审计完整性测试
  - 重试/死信治理测试
- DoD：
  - 集成链路具备可观测、可恢复、可审计能力

### S6-08：阶段验收与切换准备
- 状态：pending
- 交付物：
  - 阶段 6 验收记录
  - 风险关闭清单
  - 下一阶段输入清单（运营与扩展项）
- 最小测试集：
  - 阶段 6 全量门禁执行
- DoD：
  - A6 验收项满足，阻塞风险关闭或转受控项

## 3. 进度看板（手工维护，保守标记）

| 条目 | 状态 | 备注 |
| --- | --- | --- |
| S6-00 | completed | 阶段 6 SSOT 与验收清单已建立，恢复机制已落盘 |
| S6-01 | completed | 集成配置模型、API、鉴权、审计与迁移已落地 |
| S6-02 | completed | 事件入库、签名校验、幂等去重与重放能力已落地 |
| S6-03 | completed | CI 触发、回调收敛与运行记录查询已落地 |
| S6-04 | completed | 通知订阅、投递日志、重试与死信最小闭环已落地 |
| S6-05 | completed | Jira 适配切片、失败映射、去重与更新路径已落地 |
| S6-06 | completed | OAuth2 授权启动、回调校验、账号绑定与令牌签发已落地 |
| S6-07 | completed | 集成治理健康接口、失败/死信治理重试与最小治理看板已落地 |
| S6-08 | completed | 阶段 6 验收记录已落盘，收口结论与受控风险已同步 |

## 4. 阶段 6 完成定义（DoD）

- 企业集成配置、事件、通道、缺陷联动形成最小可用闭环
- 至少一条 CI/CD 与一条通知或缺陷链路稳定可用
- 关键集成动作可审计、失败可重试、死信可治理
- 阶段 6 验收清单可执行且结论可追溯

## 5. 最近更新记录

### 2026-03-17
- 完成 S6-08：执行阶段 6 验收收口，补齐验收执行记录、结论与受控风险。
- 验收结论：阶段 6 评估为“受控通过”，S6-00~S6-08 全部完成，具备阶段切换条件。
- 质量门禁：阶段 6 最小回归通过（25 passed）；前端构建通过（`npm run build`）。
- 后端全量回归说明：`python -m pytest -q` 受环境权限阻塞（`tests/backend/test_db_migration_workflow.py` 3 项 WinError 5）；排除该用例后其余全量回归通过（`python -m pytest -q --ignore=tests/backend/test_db_migration_workflow.py`）。
- 风险处置：将临时目录权限阻塞登记为受控风险，保留补测动作并不影响当前阶段收口。
- 阶段推进：阶段 6 切换为“已完成验收”，下一步进入阶段 7 规划与启动准备。
### 2026-03-17
- 完成 S6-06：新增 OAuth2 身份集成最小闭环（identity_oauth_sessions/identity_provider_bindings 模型 + 迁移、oauth2 start/callback/bindings 接口）。
- S6-06 机制：state 会话安全校验（存在性/过期/一次性消费）、账号绑定策略（新建/关联/复用）与回调令牌签发。
- S6-06 测试门禁：新增 tests/backend/test_integration_identity_oauth_api.py（3 passed）；S6 相关回归通过（22 passed）。
- 阶段推进：S6-06 完成后进入 S6-07（治理增强与运营可观测）准备。
### 2026-03-17
- 完成 S6-05：新增缺陷联动最小闭环（defect_sync_records 模型 + 迁移、/api/integrations/{config_id}/defects/sync、/api/integrations/project/{project_id}/defects/records）。
- S6-05 机制：失败执行字段映射、失败指纹去重（同失败模式复用缺陷单）、建单/更新双路径审计留痕。
- S6-05 测试门禁：新增 tests/backend/test_integration_defect_api.py（3 passed）；S6 相关回归通过（19 passed）。
- 阶段推进：S6-05 完成后进入 S6-06（SSO/OAuth2 最小接入）准备。
### 2026-03-17
- 完成 S6-00：创建阶段 6 开发清单与验收清单，建立“看板 + 最近更新 + 风险阻塞”可中断恢复机制。
- 同步更新项目进度文档、架构总纲与 `09-enterprise-integrations/SKILL.md`，将阶段 6 状态切换为“启动中（规划中）”。
- 明确阶段 6 执行顺序：S6-01（集成底座）-> S6-02（事件与回调）-> S6-03~S6-06（能力闭环）-> S6-07（治理增强）-> S6-08（验收收口）。
- 完成 S6-01：新增集成配置中心最小闭环（`integration_configs` 模型、迁移、`/api/integrations/*` API、鉴权与审计）。
- S6-01 测试门禁：新增 `tests/backend/test_integrations_api.py`（4 passed）；后端全量回归通过 `.\.venv\Scripts\python -m pytest`（115 passed，2 warnings）；前端构建通过 `npm run build`（frontend）。
- 迁移链路验证：历史本地库升级仍受既有 `audit_logs_archive already exists` 漂移影响；使用临时干净库验证链路通过：`upgrade head -> downgrade 2c1b7f9a4d10 -> upgrade head`。
- 完成 S6-02：新增集成事件收件箱与签名 Webhook 接入（`integration_events` 模型、迁移、`/api/integrations/webhooks/{config_id}/events/{event_type}`、事件查询与重放）。
- S6-02 测试门禁：新增 `tests/backend/test_integration_events_api.py`（4 passed），联同 S6-01 测试回归（8 passed）；后端全量回归通过 `.\.venv\Scripts\python -m pytest`（119 passed，2 warnings）；前端构建通过 `npm run build`（frontend）。
- S6-02 迁移验证：本地历史库既有 revision 漂移风险仍在（`audit_logs_archive already exists`）；在临时干净库验证链路通过：`upgrade head -> downgrade 6a9d4c2e1b7f -> upgrade head`。
- 完成 S6-03：新增 CI/CD 最小闭环（`/api/integrations/{config_id}/cicd/trigger`、`/api/integrations/webhooks/{config_id}/cicd/callback`、`/api/integrations/{config_id}/cicd/runs`），实现“触发 -> 回调 -> 状态收敛”。
- S6-03 测试门禁：新增 `tests/backend/test_integration_cicd_api.py`（4 passed），S6 相关回归通过（12 passed）；后端全量回归通过 `.\.venv\Scripts\python -m pytest`（123 passed，2 warnings）；前端构建通过 `npm run build`（frontend）。
- 完成 S6-04：新增通知中心最小闭环（`notification_subscriptions`/`notification_deliveries` 模型、`migrations/versions/7d2b6f4c8a1e_phase6_notification_center_minimal.py`、`/api/integrations/project/{project_id}/notification-subscriptions`、`/api/integrations/notification-subscriptions/{subscription_id}/dispatch`、`/api/integrations/notification-deliveries/{delivery_id}/retry`）。
- S6-04 测试门禁：新增/执行 `tests/backend/test_integration_notifications_api.py`（4 passed），并回归 `tests/backend/test_db_migration_workflow.py`（3 passed）；S6 相关回归通过（19 passed）。

## 6. 风险与阻塞清单（持续维护）

| 编号 | 风险/阻塞 | 当前状态 | 处理策略 | 负责人/阶段 |
| --- | --- | --- | --- | --- |
| RISK-S6-001 | 第三方平台差异较大导致适配范围膨胀 | controlled | 采用“单提供商先落地 + 适配层抽象”的切片策略，避免一次性多平台并行 | S6-01~S6-05 |
| RISK-S6-002 | 回调安全与幂等缺失会引入高风险重复执行 | controlled | S6-02~S6-03 已落地 HMAC 签名校验 + 幂等去重 + 触发回调收敛，后续在 S6-05 继续补强通知治理与缺陷链路联动 | S6-02~S6-05 |
| RISK-S6-003 | 外部依赖不可用导致门禁不稳定 | controlled | 为集成测试提供 mock/stub 与可回放样本，核心门禁优先本地可重复 | S6-03~S6-07 |
| RISK-S6-004 | 本地临时目录权限限制导致 `test_db_migration_workflow.py` 门禁不稳定 | controlled | 固定受控排除并登记补测计划；环境恢复后优先补跑迁移工作流测试 | S6-08 |















