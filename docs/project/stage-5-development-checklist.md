# 阶段 5 开发清单（报告分析与治理）

> 目的：为阶段 5 提供可持续维护的单一事实来源（SSOT），用于追踪 **已完成 / 进行中 / 待完成**，并约束交付物、测试门禁与 DoD。
>
> 适用规则：
> - 任何涉及逻辑/功能代码改动：先补/更测试，再实现；并执行最小相关测试集（公共模块需补回归）。
> - 若改动影响模块状态、阶段进度或路线图：同轮同步更新 `docs/project/project-progress.md` 的“最近更新记录”，并检查 `docs/architecture/企业级自动化测试平台系统架构规划.md` 是否需要同步修订。

## 0. 阶段定位（以当前代码与进度基线为准）

- 阶段名称：阶段 5 报告分析与治理
- 当前状态：已完成验收（S5-07 已完成）
- 当前总阶段：阶段 2 收尾中 + 阶段 3 收尾中 + 阶段 4 已完成验收 + 阶段 5 已完成验收（详见 `docs/project/project-progress.md`）
- 本阶段目标：把“执行结果记录”升级为“可分析、可治理、可决策”的报告与质量运营体系。

## 0.1 可中断恢复机制（强制）

- 恢复入口顺序（固定）：
1. 先看本文“3. 进度看板”（找唯一 in_progress 条目）
2. 再看本文“5. 最近更新记录”最后一条（获取最后动作与下一步）
3. 最后看本文“6. 风险与阻塞清单”（先解除阻塞再继续）
- 状态写法统一：`pending / in_progress / completed / blocked`（任一时刻仅允许一个条目为 `in_progress`）
- 每次提交前必须更新：任务状态、测试结果、阻塞项、下一步动作。

## 1. 范围边界

### In Scope（阶段 5）
- 报告中心最小闭环（项目级执行摘要）
- 趋势统计最小闭环（日/周维度）
- 失败分类与治理视图最小闭环
- 报告相关权限与审计对齐
- 报告查询性能与稳定性门禁

### Out of Scope（本阶段不做）
- 企业级外部 BI 平台深度集成（阶段 6）
- AI 根因分析自动化闭环（后续扩展）
- 跨区域多活报告存储架构（后续扩展）

## 2. 阶段 5 工作分解（按可交付切片推进）

### S5-00：阶段立项与 SSOT 落盘（必做）
- 状态：已完成
- 交付物：
  - 阶段 5 开发清单（本文）
  - 阶段 5 验收清单：`docs/project/stage-5-acceptance-checklist.md`
  - 可中断恢复机制（看板 + 最近更新 + 风险阻塞）
- 最小测试集：
  - 无（文档类）
- DoD：
  - 阶段 5 任务编号、门禁、DoD、验收口径可独立阅读与执行

### S5-01：报告输入口径与模型收敛
- 状态：completed
- 交付物：
  - 执行摘要字段定义（API/Web 统一口径）
  - 失败分类字典与映射规则
  - 趋势统计时间窗口与聚合规则
  - 口径冻结文档：`docs/project/stage-5-reporting-input-contract.md`
- 最小测试集：
  - 报告字段映射一致性测试
  - 失败分类映射测试
- DoD：
  - API/Web 执行记录可统一映射，且无冲突字段

### S5-02：报告中心最小闭环（MVP）
- 状态：completed
- 交付物：
  - 项目级报告摘要聚合服务
  - 报告摘要查询接口（最小筛选）
  - 前端最小报告页（摘要 + Top 失败项）
- 最小测试集：
  - 报告聚合正确性测试
  - 报告接口权限与边界测试
  - 前端构建验证
- DoD：
  - 可稳定查询并展示总量、通过率、失败率、失败 TopN

### S5-03：趋势分析最小闭环
- 状态：completed
- 交付物：
  - 日/周趋势聚合逻辑
  - 趋势查询接口
  - 前端趋势图最小展示
- 最小测试集：
  - 趋势计算一致性测试
  - 时间窗口边界测试
- DoD：
  - 同条件重复查询结果一致，图表与后端数据一致

### S5-04：失败治理闭环（分类 + 归因）
- 状态：completed
- 交付物：
  - 失败分类与归因字段
  - 失败治理视图（可筛选、可追溯）
- 最小测试集：
  - 失败分类准确性测试
  - 追溯链路可用性测试
- DoD：
  - 失败记录可按分类检索并回溯至原执行记录

### S5-05：权限与审计对齐
- 状态：completed
- 交付物：
  - 报告/治理接口权限校验收敛
  - 报告域审计事件定义与落库
- 最小测试集：
  - 越权访问测试（403）
  - 审计落库测试
- DoD：
  - 报告相关关键读写动作可审计、可追踪

### S5-06：性能与稳定性门禁
- 状态：completed
- 交付物：
  - 报告查询性能基线
  - 索引与分页策略
  - 回归门禁清单
- 最小测试集：
  - 报告查询性能回归
  - 阶段 5 最小回归测试集
- DoD：
  - 约定数据量下查询性能可接受，回归全绿

### S5-07：阶段验收与切换准备
- 状态：completed
- 交付物：
  - 阶段 5 验收记录
  - 风险关闭清单
  - 下阶段输入清单
- 最小测试集：
  - 阶段 5 全量门禁执行
- DoD：
  - A5 验收项满足，阻塞风险关闭或转受控项

## 3. 进度看板（手工维护，保守标记）

| 条目 | 状态 | 备注 |
| --- | --- | --- |
| S5-00 | completed | 阶段 5 SSOT 与验收清单已创建，恢复机制已落盘 |
| S5-01 | completed | 统一输入契约、映射服务、失败分类与最小测试已收敛完成 |
| S5-02 | completed | 报告摘要聚合服务、摘要接口与最小报告页已形成闭环并通过门禁 |
| S5-03 | completed | 趋势聚合接口与最小趋势图已形成闭环并通过门禁 |
| S5-04 | completed | 失败治理接口与最小视图已形成闭环并通过门禁 |
| S5-05 | completed | 报告域接口权限校验与审计事件落库已对齐并通过门禁 |
| S5-06 | completed | 报告性能基线、时间窗口护栏与阶段回归门禁已建立并通过 |
| S5-07 | completed | 阶段 5 验收完成，门禁已执行并通过 |

## 4. 阶段 5 完成定义（DoD）

- 报告中心、趋势分析、失败治理形成可用最小闭环
- 报告相关权限与审计能力对齐并可追踪
- 关键查询具备性能基线与稳定性门禁
- 阶段 5 验收清单可执行且结论可追溯

## 5. 最近更新记录

### 2026-03-17
- 完成 S5-00：创建阶段 5 开发清单与验收清单，建立“看板 + 最近更新 + 风险阻塞”可中断恢复机制。
- 同步更新项目进度文档与阶段 5 模块 SKILL，确保阶段口径一致。
- 启动 S5-01：新增 `docs/project/stage-5-reporting-input-contract.md`，冻结 API/Web 报告输入字段、映射规则与统计口径（v1）。
- 推进 S5-01：新增 `app/services/reporting_input.py` 收敛 API/Web 报告输入映射、失败分类与基础统计口径；新增测试 `tests/backend/test_reporting_input_service.py`，并通过最小回归。
- 完成 S5-01：统一输入口径与模型收敛任务收口，切换阶段看板状态为 `completed`。
- 启动 S5-02：新增项目级报告摘要接口 `GET /api/reports/project/{project_id}/summary`、聚合服务 `app/services/reporting_summary.py` 与前端最小页面 `frontend/src/views/ReportSummary.vue`。
- S5-02 门禁验证：后端最小回归通过（`17 passed`），前端构建通过（`npm run build`）。
- 完成 S5-02：项目级报告中心最小闭环收口（摘要 + Top 失败项），切换阶段看板状态为 `completed`。
- 启动 S5-03：新增趋势接口 `GET /api/reports/project/{project_id}/trends`（日/周聚合）与前端趋势最小展示（ReportSummary 趋势图）。
- S5-03 门禁验证：后端回归通过（`20 passed`），前端构建通过（`npm run build`）。
- 完成 S5-03：趋势分析最小闭环收口（趋势接口 + 最小图表展示），切换阶段看板状态为 `completed`。
- 启动 S5-04：新增失败治理接口 `GET /api/reports/project/{project_id}/failures`（分类筛选 + 可追溯字段）与前端失败治理视图。
- S5-04 门禁验证：后端回归通过（`22 passed`），前端构建通过（`npm run build`）。
- 完成 S5-04：失败治理最小闭环收口（分类筛选 + 失败记录追溯），切换阶段看板状态为 `completed`。
- 完成 S5-05：报告域权限与审计对齐，新增审计事件 `report.summary.read / report.trends.read / report.failures.read` 并落库。
- S5-05 门禁验证：后端回归通过 `.\.venv\Scripts\python -m pytest tests/backend/test_reporting_input_service.py tests/backend/test_reporting_summary_api.py tests/backend/test_reporting_trends_api.py tests/backend/test_reporting_failures_api.py tests/backend/test_reporting_audit_api.py tests/backend/test_unified_results_api.py tests/backend/test_test_runs_api.py`（23 passed）。
- 完成 S5-06：建立报告时间窗口性能护栏（最大 180 天）与中等数据量性能基线测试；新增 `tests/backend/test_reporting_performance_guards.py`。
- S5-06 门禁验证：后端回归通过 `.\.venv\Scripts\python -m pytest tests/backend/test_reporting_input_service.py tests/backend/test_reporting_summary_api.py tests/backend/test_reporting_trends_api.py tests/backend/test_reporting_failures_api.py tests/backend/test_reporting_audit_api.py tests/backend/test_reporting_performance_guards.py tests/backend/test_unified_results_api.py tests/backend/test_test_runs_api.py`（25 passed）。
- 完成 S5-07：执行阶段 5 核心验收门禁并收口验收记录，阶段状态切换为 `已完成验收`。
- S5-07 门禁验证：后端全量回归通过 `.\.venv\Scripts\python -m pytest`（111 passed，2 warnings）；前端构建通过 `npm run build`（frontend）。

## 6. 风险与阻塞清单（持续维护）

| 编号 | 风险/阻塞 | 当前状态 | 处理策略 | 负责人/阶段 |
| --- | --- | --- | --- | --- |
| RISK-S5-001 | 报告输入口径尚未冻结，API/Web 字段可能存在语义差异 | closed | S5-01 已完成口径冻结与实现收敛，后续由契约 + 测试持续守护 | S5-01 |
| RISK-S5-002 | 阶段 4 遗留迁移 revision 漂移仍未技术性关闭 | controlled | 作为阶段 5 受控项持续跟踪，避免影响报告相关新迁移链路 | S5-01~S5-06 |
| RISK-S5-003 | 历史数据量增长后报告查询可能退化 | controlled | S5-06 已建立性能基线与时间窗口护栏，S5-07 已完成验收收口，后续在阶段 6 持续观察 | S5-06~S5-07 |
