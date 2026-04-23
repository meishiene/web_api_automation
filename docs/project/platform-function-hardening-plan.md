# 平台功能完善计划（可投入使用阶段）

> 目的：在 **不变动原阶段 8 / 阶段 9 规划** 的前提下，新增一条并行工作线，围绕现有已落地的最小闭环能力，持续补齐产品能力、治理细节与稳定性门禁，使平台达到“团队可持续使用”的水平。
>
> 适用规则：
> - 本计划不替代阶段清单，不改变阶段 8 / 9 的原有规划与命名。
> - 涉及逻辑/功能代码改动：先补/更测试，再实现；并执行最小相关测试集（公共模块需补回归）。
> - 若改动影响模块状态、阶段进度或路线图：同轮同步更新 `docs/project/project-progress.md` 的“最近更新记录”，并检查 `docs/architecture/企业级自动化测试平台系统架构规划.md` 是否需要同步修订。
> - 任一时刻仅允许一个条目标记为 `in_progress`。

## 0. 工作线定位（以当前代码与进度基线为准）

- 工作线名称：平台功能完善计划
- 当前状态：启动中（FH-00 已完成，FH-01 已完成，FH-02 执行中）
- 与阶段关系：并行工作线，不替代阶段 8 / 9
- 当前总阶段：阶段 2 收尾中 + 阶段 3 收尾中 + 阶段 4 已完成验收 + 阶段 5 已完成验收 + 阶段 6 已完成验收 + 阶段 7 已完成验收
- 核心目标：
  - 把现有“最小闭环”能力补到“团队可长期使用”
  - 优先完善项目资产、API 测试、Web 测试、执行调度、报告诊断与集成协作
  - 持续收敛缺陷、补齐高频场景与稳定性门禁

## 1. 中断恢复指引（必须遵守）

1. 先看本文“3. 进度看板”，确认唯一 `in_progress` 条目。
2. 再看本文“5. 最近更新记录”最后一条，确认上一步实际动作与结果。
3. 若改动影响总阶段判断，先同步 `docs/project/project-progress.md` 与架构总纲。
4. 若改动影响 API / Web / 报告 / 集成 / 调度模块状态，再同步对应 `docs/modules/future/*/SKILL.md`。
5. 本计划优先级高于新阶段预研，但不改变原有阶段 8 / 9 的长期路线。

## 2. 工作分解（按模块与步骤推进）

### FH-00：功能完善 SSOT 落盘（必做）
- 状态：completed
- 交付物：
  - 平台功能完善计划（本文）
  - 与总进度、架构总纲、项目概览的并行工作线口径同步
- 最小测试集：
  - 无（文档类）
- DoD：
  - 明确该工作线不替代阶段 8 / 9
  - 后续可按模块和步骤直接接力执行

### FH-01：项目与资产管理完善
- 状态：completed
- 目标：
  - 让项目、成员、环境、变量能力从“有入口”变成“可稳定管理”
- 子步骤：
  1. 项目列表 / 项目详情能力补齐：项目概览信息、最近活动、进入路径统一
  2. 项目成员管理前端补齐：成员列表、角色维护、基础协作入口
  3. 环境与变量页增强：变量组、密钥、来源与覆盖关系展示清晰
  4. 资产导入/导出链路梳理：项目内资产流转更明确
- 最小测试集：
  - 项目 / 成员 / 环境相关回归
  - 前端构建
- DoD：
  - 团队用户可稳定管理项目、成员、环境与变量资产

### FH-02：API 测试功能完善
- 状态：in_progress
- 目标：
  - 让 API 测试从“可创建并执行”提升到“适合日常维护与回归”
- 子步骤：
  1. 用例编辑器增强：结构化编辑 Params / Headers / Body / Assertions / Extraction
  2. 导入能力增强：补齐 Postman 等常用格式，完善错误提示与映射策略
  3. 套件管理增强：批量编排、排序、批次重跑、失败重跑
  4. 执行反馈增强：响应 diff、断言失败定位、变量来源展示
  5. 批次与详情页增强：筛选、对比、回溯链路更完整
- 最小测试集：
  - `test_test_cases_api.py`
  - `test_suite_batch_runs_api.py`
  - `test_test_runs_api.py`
  - `test_test_executor_enhancements.py`
  - 前端构建
- DoD：
  - API 用例维护、执行、回归、失败定位形成稳定工作流

### FH-03：Web 测试功能完善
- 状态：in_progress
- 目标：
  - 让 Web 测试从“单用例最小闭环”提升到“能做实际业务回归”
- 子步骤：
  1. Web 步骤配置增强：步骤模板、参数校验、拖拽排序、定位器体验
  2. 浏览器配置增强：浏览器类型、窗口大小、超时、无头模式、截图/视频/Trace
  3. 产物查看增强：截图、日志、错误步骤、产物入口更直观
  4. Web 套件 / 批量执行规划与落地
  5. Web 执行稳定性增强：失败重试、等待策略、元素定位韧性
- 最小测试集：
  - `test_web_test_cases_api.py`
  - `test_web_test_runs_api.py`
  - 前端构建
- DoD：
  - Web 测试具备可维护、可回归、可定位的稳定工作流

### FH-04：执行与调度能力完善
- 状态：in_progress
- 目标：
  - 让执行中心、批次、调度和 Worker 从“最小运行”提升到“可运维使用”
- 子步骤：
  1. 执行中心增强：统一结果查询、快速筛选、重跑入口、详情联动
  2. 调度管理增强：任务模板、Cron 辅助、启停、最近结果
  3. 队列与 Worker 治理增强：取消、超时、重试、恢复、优先级
  4. 批次执行增强：失败重跑、重试策略、执行链路可观察性
- 最小测试集：
  - `test_execution_orchestration_skeleton.py`
  - `test_schedule_tasks_api.py`
  - `test_queue_worker_api.py`
  - 前端构建
- DoD：
  - 执行与调度链路支持日常运维和问题定位

### FH-05：结果、报告与诊断能力完善
- 状态：in_progress
- 目标：
  - 让结果和报告从“可看”提升到“可诊断、可决策”
- 子步骤：
  1. 统一结果页增强：更多筛选、更多聚合、更多失败定位动作
  2. 报告中心增强：报告详情、趋势对比、失败聚类、导出能力
  3. 慢步骤与异常诊断：补齐耗时分析、异常分类和根因线索
  4. 运营总览增强：平台级信号、治理趋势、告警口径联动
- 最小测试集：
  - `test_unified_results_api.py`
  - `test_reporting_summary_api.py`
  - `test_reporting_trends_api.py`
  - `test_reporting_failures_api.py`
  - `test_reporting_performance_guards.py`
  - 前端构建
- DoD：
  - 报告和结果页面支持稳定排障与质量判断

### FH-06：企业集成与协作能力完善
- 状态：in_progress
- 目标：
  - 在现有最小闭环基础上，让集成能力更贴近日常使用
- 子步骤：
  1. 通知中心增强：更多事件订阅、模板、失败治理
  2. 缺陷联动增强：失败映射、批量操作、记录查询体验
  3. OAuth2 / 身份映射增强：绑定展示、异常提示、协作边界
  4. CI/CD 增强：触发模板、回调收敛展示、运行历史查询
- 最小测试集：
  - `test_integrations_api.py`
  - `test_integration_events_api.py`
  - `test_integration_cicd_api.py`
  - `test_integration_notifications_api.py`
  - `test_integration_defect_api.py`
  - `test_integration_identity_oauth_api.py`
- DoD：
  - 集成能力可稳定支撑项目内协作与通知闭环

### FH-07：缺陷修复与稳定性回归
- 状态：in_progress
- 目标：
  - 建立可持续的缺陷收敛与高频回归机制
- 子步骤：
  1. 建立缺陷清单：按模块沉淀高频问题
  2. 建立主链路回归矩阵：API、Web、执行、报告、集成
  3. 建立中等数据量性能回归与构建门禁
  4. 逐步关闭高频 UX / 数据一致性 / 权限类问题
- 最小测试集：
  - 按缺陷所在模块执行最小相关测试集
  - 后端全量回归（必要时）
  - 前端构建
- DoD：
  - 已知高频缺陷持续收敛，核心链路稳定

### FH-08：功能完善收口评审
- 状态：in_progress
- 目标：
  - 形成“可投入使用阶段”的阶段性结论与后续输入
- 子步骤：
  1. 汇总已解决项 / 延后项 / 风险项
  2. 执行工作线回归门禁
  3. 形成对阶段 8 / 9 的输入建议
- 最小测试集：
  - 工作线相关回归汇总
- DoD：
  - 形成清晰的投入使用结论与后续路线，不与原阶段 8 / 9 冲突

## 3. 进度看板（手工维护，保守标记）

| 条目 | 状态 | 备注 |
| --- | --- | --- |
| FH-00 | completed | 平台功能完善计划已建立，不替代阶段 8 / 9 |
| FH-01 | completed | 项目详情 / 成员治理 / 环境变量治理工作台已形成闭环 |
| FH-02 | in_progress | API 套件与回归工作台增强进行中 |
| FH-03 | in_progress | Web 执行配置持久化已落地，后续补更多运行稳定性增强 |
| FH-04 | in_progress | 调度工作台已补模板、最近结果与失败重试入口 |
| FH-05 | in_progress | 报告详情与执行中心联动已补齐，后续补趋势对比与导出 |
| FH-06 | in_progress | 集成治理工作台已接入通知 / 缺陷 / CI / 身份 / 治理执行 |
| FH-07 | in_progress | 已建立缺陷与风险台账并通过后端全量回归 |
| FH-08 | in_progress | 已产出最终交付说明，等待最终路线确认 |

## 4. 完成定义（DoD）

- 核心模块不再停留在“最小闭环”，能够支持团队日常稳定使用
- API / Web / 执行 / 报告 / 集成能力具备清晰的产品工作流
- 高频缺陷和稳定性问题持续收敛
- 形成面向阶段 8 / 9 的真实输入，而非替代原路线

## 5. 最近更新记录

### 2026-04-03
- FH-04 / FH-05 继续增强：调度页支持取消队列任务，报告页支持导出当前筛选快照 JSON，执行与分析动作进一步闭环。
- 本地数据库迁移状态推进到最新 head：当前 `python -m alembic current` 为 `2b7c4e1a9d0f (head)`。
- 验证通过：`python -m pytest tests/backend/test_queue_worker_api.py tests/backend/test_reporting_summary_api.py tests/backend/test_reporting_trends_api.py tests/backend/test_reporting_failures_api.py -q`（12 passed）；`npm run build`（frontend）通过。
### 2026-04-02
- FH-03 继续增强：Web 步骤编辑器由原始 JSON 输入改为结构化定位编辑，支持 CSS / XPath / Text / TestId / Role 下拉选择与单输入框填写。
- `web_executor.py` 同步支持多种定位策略解析，`wait` 步骤兼容“等待元素”与“固定等待”两种模式，保留旧 `selector` 参数兼容。
- 验证通过：`python -m pytest tests/backend/test_web_executor.py tests/backend/test_web_test_cases_api.py tests/backend/test_web_test_runs_api.py -q`（10 passed）；`npm run build`（frontend）通过。
### 2026-04-01
- FH-08 / FH-07 收口：新增 `docs/project/defect-register.md` 与 `docs/project/final-delivery-summary.md`，沉淀已处理项、保留风险、数据库迁移修复与最终交付建议。
- 执行验证：`python -m pytest tests/backend -q` 全量通过；`npm run build`（frontend）通过。
### 2026-04-01
- FH-06 推进：重构 `IntegrationGovernanceDashboard.vue`，接入现有通知订阅/投递、缺陷记录、CI/CD 运行、身份绑定、治理执行与集成配置查询链路，形成企业集成工作台。
- 验证通过：`python -m pytest tests/backend/test_integration_notifications_api.py tests/backend/test_integration_cicd_api.py tests/backend/test_integration_defect_api.py tests/backend/test_integration_identity_oauth_api.py -q`（14 passed）；`npm run build`（frontend）通过。
### 2026-04-01
- FH-05 / FH-04 增强：执行中心新增统一“重跑”入口，报告详情新增“打开执行中心 / 定位首个失败”，执行排障动作更闭环。
- FH-03 启动：Web 用例新增执行配置持久化字段（浏览器、窗口、超时、headless、失败截图、录制视频），前端配置区从占位升级为真实可保存配置；执行器同步接入这些配置。
- 迁移验证通过：使用临时空库执行 `python -m alembic upgrade head` 成功升级到 `1f4e2a7c9b3d`；当前本地 `test_platform.db` 因历史 Alembic 状态不一致未直接升级，需后续单独整理。
- 验证通过：`python -m pytest tests/backend/test_web_test_cases_api.py tests/backend/test_test_runs_api.py -q`（10 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- FH-02 继续推进：统一导入 provider 链路新增 Postman Collection 支持，前端 API 工作台导入弹窗现覆盖 JSON / OpenAPI / Postman 三类入口。
- 验证通过：`python -m pytest tests/backend/test_test_cases_api.py tests/backend/test_suite_batch_runs_api.py -q`（18 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- FH-02 启动：在 `TestCaseList.vue` 中补齐 API 套件工作台，支持套件创建、选择、加入/移出当前用例、套件执行与环境选择，打通现有 `test_suites` / `suite run` 链路。
- 验证通过：`python -m pytest tests/backend/test_suite_batch_runs_api.py tests/backend/test_project_members_api.py tests/backend/test_environments_api.py -q`（14 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- FH-01 收口：补齐项目详情抽屉、资产流转入口、成员治理弹窗与用户列表接口，项目、成员、环境、变量治理形成首个可用闭环。
- 验证通过：`python -m pytest tests/backend/test_project_members_api.py tests/backend/test_environments_api.py -q`（10 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- FH-01 继续推进：补齐项目成员管理前端，新增用户列表接口 `/api/users`、项目成员返回用户名字段，并在 `ProjectList.vue` 中落地成员治理弹窗（列表、角色调整、添加、移除）。
- 项目管理页同步补齐成员统计口径：项目卡片现展示真实成员数量，并将“成员治理”从占位入口升级为可操作闭环。
- 验证通过：`python -m pytest tests/backend/test_project_members_api.py tests/backend/test_environments_api.py -q`（10 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- FH-01 启动：重构 `frontend/src/views/EnvironmentManager.vue`，将环境与变量治理页升级为统一工作台布局，补齐项目切换、环境卡片管理、项目/环境变量编辑与变量组绑定分区。
- 同步补齐前端环境管理接口：新增环境更新/删除能力，环境治理页与现有后端接口（环境、变量、变量组、secret reveal）全部打通。
- 验证通过：`python -m pytest tests/backend/test_environments_api.py -q`（4 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- 创建平台功能完善计划，替代原“页面优化”并行清单，后续聚焦现有功能从最小闭环向“可投入使用”演进。
- 计划按模块推进：项目与资产、API 测试、Web 测试、执行与调度、结果与报告、企业集成、缺陷修复与收口评审。
- 当前断点：FH-01 已完成，进入 FH-02 执行中，优先完善 API 套件与回归工作台。

## 6. 风险与边界清单（持续维护）

| 编号 | 风险/边界 | 当前状态 | 处理策略 | 归属 |
| --- | --- | --- | --- | --- |
| RISK-FH-001 | 功能完善计划与阶段 8 / 9 路线混淆 | watch | 明确写入“并行工作线，不替代阶段 8 / 9” | FH-00 |
| RISK-FH-002 | 功能补齐过程中演变为无边界重构 | watch | 仅围绕现有能力、现有链路、现有缺陷做增量改进 | FH-01~FH-07 |
| RISK-FH-003 | 前端/功能优化脱离后端事实，出现“界面存在但链路未通” | watch | 以 `app/` 与 `frontend/src/` 实际能力为准，禁止把占位能力标为完成 | 全工作线 |
