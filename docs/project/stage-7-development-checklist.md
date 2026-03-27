# 阶段 7 开发清单（运营化与平台扩展）

> 目的：为阶段 7 提供可持续维护的单一事实来源（SSOT），用于追踪 **已完成 / 进行中 / 待完成**，并约束交付物、测试门禁与 DoD。
>
> 适用规则：
> - 任何涉及逻辑/功能代码改动：先补/更测试，再实现；并执行最小相关测试集（公共模块需补回归）。
> - 若改动影响模块状态、阶段进度或路线图：同轮同步更新 `docs/project/project-progress.md` 的“最近更新记录”，并检查 `docs/architecture/企业级自动化测试平台系统架构规划.md` 是否需要同步修订。
> - 任一时刻仅允许一个条目标记为 `in_progress`。

## 0. 阶段定位（以当前代码与进度基线为准）

- 阶段名称：阶段 7 运营化与平台扩展
- 当前状态：已完成验收（S7-06 已完成）
- 当前总阶段：阶段 2 收尾中 + 阶段 3 收尾中 + 阶段 4 已完成验收 + 阶段 5 已完成验收 + 阶段 6 已完成验收 + 阶段 7 启动中（详见 `docs/project/project-progress.md`）
- 本阶段目标：在阶段 6 企业集成闭环基础上，完成平台的运营化、可扩展与可持续演进能力建设。

## 1. 中断恢复指引（必须遵守）

1. 先看本文“3. 进度看板”，确认唯一 `in_progress` 条目。
2. 再看本文“5. 最近更新记录”最后一条，确认上一步实际动作与结果。
3. 若要判断是否可切换阶段，先看 `docs/project/stage-7-acceptance-checklist.md` 的通过条件与执行记录。
4. 若改动影响全局阶段口径，同步更新 `docs/project/project-progress.md` 与架构总纲。
5. 若阶段状态发生变化，同步更新 `docs/modules/future/09-enterprise-integrations/SKILL.md`。

## 2. 阶段 7 工作分解（按可交付切片推进）

### S7-00：阶段 7 SSOT 与验收口径落盘（必做）
- 状态：completed
- 交付物：
  - 阶段 7 开发清单（本文）
  - 阶段 7 验收清单（`docs/project/stage-7-acceptance-checklist.md`）
  - 中断恢复机制与门禁口径
- 最小测试集：
  - 无（文档类）
- DoD：
  - 阶段 7 任务编号、门禁、DoD、验收口径可独立阅读与执行

### S7-01：导入能力最小闭环（OpenAPI/Postman 二选一先落地）
- 状态：completed
- 交付物：
  - 导入入口 API（最小能力）
  - 导入映射规则（请求、断言、变量最小映射）
  - 重复数据最小去重策略
- 最小测试集：
  - 导入成功/失败输入测试
  - 映射正确性测试
- DoD：
  - 支持至少一种标准格式导入并可生成可执行测试资产

### S7-02：扩展点骨架（Provider Registry）
- 状态：completed
- 交付物：
  - Provider 注册与发现机制
  - 最小 provider 适配模板与约束
  - 运行时选择与回退策略
- 最小测试集：
  - 注册冲突/未注册 provider 测试
  - provider 路由分发测试
- DoD：
  - 平台对外部能力扩展具备统一接入骨架

### S7-03：运营看板增强（跨项目聚合）
- 状态：completed
- 交付物：
  - 跨项目治理聚合 API
  - 高风险信号最小指标（失败积压、死信积压、重试趋势）
  - 最小前端聚合看板
- 最小测试集：
  - 聚合统计正确性测试
  - 权限隔离测试（跨项目越权 403）
- DoD：
  - 具备项目级到平台级运营可观测最小能力

### S7-04：治理执行增强（批量策略 + 幂等 + 审计）
- 状态：completed
- 交付物：
  - 批量治理任务接口
  - 幂等保护与重复执行保护
  - 审计事件补齐与追踪字段标准化
- 最小测试集：
  - 幂等与重复触发测试
  - 审计完整性测试
- DoD：
  - 治理任务可重入、可追踪、可审计

### S7-05：稳定性门禁增强（性能/容量）
- 状态：completed
- 交付物：
  - 关键链路性能基线测试
  - 中等数据量回归测试集
  - 失败场景降级与告警口径
- 最小测试集：
  - 性能基线测试
  - 稳定性回归测试
- DoD：
  - 阶段 7 关键能力具备可重复稳定门禁

### S7-06：阶段验收与切换准备
- 状态：completed
- 交付物：
  - 阶段 7 验收记录
  - 风险关闭清单与受控转移项
  - 下一阶段输入清单
- 最小测试集：
  - 阶段 7 全量门禁执行
- DoD：
  - A7 验收项满足，阻塞风险关闭或转受控项

## 3. 进度看板（手工维护，保守标记）

| 条目 | 状态 | 备注 |
| --- | --- | --- |
| S7-00 | completed | 阶段 7 SSOT 与验收清单已建立，恢复机制已落盘 |
| S7-01 | completed | OpenAPI 导入最小闭环已落地并通过最小回归（4 passed） |
| S7-02 | completed | Provider Registry 最小骨架已落地并通过最小回归（8 passed） |
| S7-03 | completed | 跨项目运营总览已落地（聚合 API + 前端看板 + 权限隔离测试） |
| S7-04 | completed | 批量治理幂等保护、执行记录与审计字段标准化已落地 |
| S7-05 | completed | 运营/治理链路性能基线、容量回归与降级/告警口径已落地 |
| S7-06 | completed | 阶段 7 验收记录、风险结论与后续输入已收口 |

## 4. 阶段 7 完成定义（DoD）

- 平台具备“可接入 + 可扩展 + 可运营 + 可治理”的统一演进能力
- 关键链路具备可观测、可恢复、可审计、可回放能力
- 阶段 7 验收清单可执行且结论可追溯

## 5. 最近更新记录

### 2026-03-26
- 完成 S7-06：执行阶段 7 最小回归、后端全量回归与前端构建，验收门禁全部通过。
- 验收结论：阶段 7 满足 A7-01~A7-06，通过“已完成验收”口径切换。
- 风险收口：阶段内无新增阻塞项；导入规格复杂度、扩展抽象度与跨项目权限边界三项风险维持受控 watch 状态，转入后续运营观察，不阻断阶段切换。
- 下一阶段输入：转入“运营维护 + 受控演进”模式，后续优先关注生产/准生产环境性能画像、外部告警通道接入、更多 provider 与治理动作扩展。

### 2026-03-26
- 完成 S7-05：为 `GET /api/reports/operations/overview` 增加降级与告警口径，输出 `guardrails`（告警列表、降级原因、TopN 截断信息）。
- 稳定性门禁：新增中等数据量基线测试，覆盖运营总览与治理执行查询链路；中等数据量下要求本地测试环境在 3 秒内完成响应。
- 最小降级策略：当跨项目风险信号过多时，仅返回 Top 20 项并显式标记 `project_signals_truncated`，避免大响应拖垮看板。
- 前端可观测性：运营总览页面新增降级提示与告警卡片展示，便于快速识别 critical/warning 信号。
- 测试门禁：通过 `python -m pytest tests/backend/test_operations_overview_api.py tests/backend/test_reporting_performance_guards.py tests/backend/test_integration_governance_api.py -q`（11 passed）。
- 前端构建：`npm run build`（frontend）通过。
- 当前断点：S7-05 completed，进入 S7-06（阶段验收与切换准备）准备。

### 2026-03-26
- 完成 S7-04：增强批量治理执行接口 `POST /api/integrations/project/{project_id}/governance/retry-failed`，新增 `idempotency_key` 支持与重复请求结果复用。
- 新增治理执行记录模型 `integration_governance_executions` 与迁移 `6c8b1f2a9d4e_phase7_governance_execution_tracking`，支撑批量治理结果持久化与追踪。
- 新增治理执行查询接口 `GET /api/integrations/project/{project_id}/governance/executions`，支持项目级历史回查。
- 审计标准化：批量治理与单事件治理审计补齐统一追踪字段（`governance_execution_id`、`execution_type`、`idempotency_key`、`governance_scope` 等）。
- 测试门禁：通过 `python -m pytest tests/backend/test_integration_governance_api.py -q`（5 passed）与集成域相关回归 `python -m pytest tests/backend/test_integrations_api.py tests/backend/test_integration_events_api.py tests/backend/test_integration_cicd_api.py tests/backend/test_integration_notifications_api.py tests/backend/test_integration_defect_api.py tests/backend/test_integration_identity_oauth_api.py tests/backend/test_integration_governance_api.py -q`（27 passed）。
- 迁移链路：`alembic upgrade head -> downgrade 4c7b2d1e9a6f -> upgrade head`（SQLite 临时库）通过。
- 当前断点：S7-04 completed，进入 S7-05（稳定性门禁增强）准备。

### 2026-03-18
- 完成 S7-03：新增跨项目运营聚合接口 `GET /api/reports/operations/overview`，输出失败积压、死信积压、重试积压与按天重试趋势。
- 权限收敛：默认仅聚合当前用户可见项目；支持 `project_ids` 精确筛选并对越权项目返回 `403 FORBIDDEN`。
- 前端最小看板：新增 `frontend/src/views/OperationsOverview.vue` 与路由 `/operations/overview`，支持趋势窗口（7/14/30 天）与项目级风险信号表。
- 测试门禁：通过 `python -m pytest tests/backend/test_operations_overview_api.py -q`（2 passed）与相关回归 `python -m pytest tests/backend/test_reporting_summary_api.py tests/backend/test_reporting_failures_api.py tests/backend/test_reporting_trends_api.py tests/backend/test_reporting_audit_api.py tests/backend/test_reporting_performance_guards.py -q`（11 passed）。
- 前端构建：`npm run build`（frontend）通过。
- 当前断点：S7-03 completed，进入 S7-04（治理执行增强）准备。

### 2026-03-17
- 完成 S7-00：创建阶段 7 开发清单与验收清单，建立“看板 + 最近更新 + 风险阻塞”可中断恢复机制。
- 阶段策略：明确按 S7-01 -> S7-06 顺序推进，每次仅保持一个 `in_progress`。
- 完成 S7-01：落地 OpenAPI 3.x 导入最小闭环（`POST /api/test-cases/project/{project_id}/import/openapi`），支持路径+方法映射、`operationId`/默认命名、响应码推断、最小去重与审计留痕。
- 测试门禁：通过 `python -m pytest tests/backend/test_test_cases_api.py -k openapi -q`（4 passed）。
- 当前断点：进入 S7-03 准备，后续按跨项目聚合看板最小骨架推进。
- 完成 S7-02：落地 Provider Registry 最小骨架（注册/发现/分发），新增统一入口 `POST /api/test-cases/project/{project_id}/import/provider` 与 provider 列表接口 `GET /api/test-cases/import/providers`。
- 运行时策略：支持显式 provider 选择与按 payload 自动回退（当前落地 openapi provider）。
- 测试门禁：通过 `python -m pytest tests/backend/test_import_provider_registry.py tests/backend/test_test_cases_api.py -k "openapi or provider" -q`（8 passed）。

## 6. 风险与阻塞清单（持续维护）

| 编号 | 风险/阻塞 | 当前状态 | 处理策略 | 负责人/阶段 |
| --- | --- | --- | --- | --- |
| RISK-S7-001 | 导入规格差异导致映射复杂度失控 | controlled-watch | 维持“单格式切片 -> 增量扩展”策略，转入后续 provider 扩展观察 | S7-01 |
| RISK-S7-002 | 扩展机制早期抽象过度影响交付效率 | controlled-watch | 保持最小 registry 抽象，后续新增 provider 时继续禁止过度框架化 | S7-02 |
| RISK-S7-003 | 跨项目聚合与权限边界冲突 | controlled-watch | 当前默认最小可见 + 越权 403 已生效，后续扩展平台级视图时继续复核 | S7-03 |

