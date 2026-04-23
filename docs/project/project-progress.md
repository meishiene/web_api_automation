# 项目进度文档

## 1. 文档目的

本文档用于记录当前项目的实际开发进度，帮助后续参与开发的 AI 或开发者快速掌握：

- 当前项目做到什么程度
- 哪些模块已经完成、部分完成、未开始
- 最近新增或修改了什么
- 接下来最优先要做什么

本文件是项目级进度基线，后续凡是对代码进行新增、修改、删除，且影响功能、结构、模块状态或开发阶段判断时，都应同步更新本文档。

## 2. 当前项目阶段

- **当前总阶段**：阶段 0 已完成，阶段 1 暂停，阶段 2 收尾中，阶段 3 收尾中，阶段 4 已完成验收，阶段 5 已完成验收，阶段 6 已完成验收（S6-08 已完成），阶段 7 已完成验收（S7-06 已完成）。
- **并行工作线**：已新增“平台功能完善计划”，用于承载现有功能从最小闭环到可投入使用的持续补齐，不替代原阶段 8 / 9；当前 FH-00 已完成。
- **项目定位**：MVP 级 API 自动化测试工具，正准备向企业级自动化测试平台演进
- **平台目标**：统一承载 `API 测试 + Web 测试 + 调度执行 + 报告治理 + 企业集成`

## 3. 当前总体进度

| 领域 | 当前状态 | 进度 |
| --- | --- | --- |
| 用户与认证 | 已完成 JWT + Refresh Token、最小 RBAC（admin/user）、角色-权限矩阵、项目成员与组织层权限基础能力 | 80% |
| 项目管理 | 已支持基础 CRUD、项目成员管理与组织归属治理 | 60% |
| API 用例管理 | 已支持基础 CRUD、批量删除、套件关联与增强断言配置（阶段 2 首批已落地） | 68% |
| API 执行能力 | 已支持单条执行、选中用例批量执行与套件批量执行（含批次追踪、变量链路传递、运行时变量快照） | 65% |
| 工程化与测试基线 | 已建立测试基线、统一异常错误码、结构化日志、审计治理闭环、Alembic/PG 本地测试落地与模型治理细则 | 90% |
| Web 测试能力 | 阶段 3 收尾中（领域模型、用例管理、复制、批量管理、单/批用例执行、步骤插入、Excel 导入导出、Web 批次结果页与 API/Web 统一结果展示已落地） | 61% |
| 环境与变量管理 | 已落地变量治理增强闭环（变量组复用、密钥受控读取、前端治理页联动） | 55% |
| 套件与批量执行 | 已落地 API 套件批量执行、选中 API 用例批量执行、选中 Web 用例批量执行与 Web 批次查询首批闭环 | 60% |
| 调度与队列 | 阶段 4 已完成验收：调度/队列/Worker 最小闭环与可视化已稳定落地；阶段 5 聚焦真实消费治理与报告联动增强。 | 45% |
| 报告与分析 | 已落地统一输入映射、摘要/趋势/失败治理接口、治理页、审计事件与性能护栏，并在阶段 7 补齐运营总览 guardrails 与稳定性门禁 | 68% |
| 权限与治理 | 已完成最小 RBAC 闭环并推进细粒度治理（权限矩阵、越权校验、项目成员协作、组织层与跨项目治理基础） | 55% |
| 企业集成 | 阶段 6 已完成 S6-01~S6-08，并在阶段 7 补齐批量治理幂等保护、执行追踪与审计标准化 | 85% |

## 4. 当前阶段状态表

| 阶段 | 名称 | 状态 | 说明 |
| --- | --- | --- | --- |
| 阶段 0 | MVP 雏形 | 已完成 | 已完成最小 API 测试闭环 |
| 阶段 1 | 平台基础重构 | 暂停 | 已完成测试基线、认证升级、迁移基线、DTO 统一、模型关系映射、模型治理细则、审计治理闭环、最小 RBAC 与生产迁移脚本；生产窗口执行与治理运营能力暂挂 |
| 阶段 2 | API 平台化 | 收尾中 | 核心能力已落地并通过验收回归，进入收尾与阶段切换准备 |
| 阶段 3 | Web 测试平台建设 | 收尾中 | 阶段 3 首批闭环（S3-00~S3-04）已完成，进入稳定性收敛与遗留优化 |
| 阶段 4 | 调度与分布式执行 | 已完成验收 | 已完成 S4-01~S4-05（含验收与切换准备），具备进入阶段 5 的前置条件。 |
| 阶段 5 | 报告分析与治理 | 已完成验收 | 阶段 5 已完成 S5-00~S5-07，验收门禁通过并完成阶段收口。 |
| 阶段 6 | 企业集成与生态完善 | 已完成验收 | 阶段 6 已完成 S6-00~S6-08，并完成验收收口与阶段切换准备。 |
| 阶段 7 | 运营化与平台扩展 | 已完成验收 | 已完成 S7-00~S7-06（导入、扩展骨架、运营看板、治理执行增强、稳定性门禁与阶段验收收口）。 |

## 5. 当前已完成内容

### 5.1 后端
- 已建立 `FastAPI` 应用入口
- 已接入 `auth`、`organizations`、`projects`、`test_cases`、`test_suites`、`environments`、`schedule_tasks`、`test_runs`、`web_test_cases`、`web_test_runs`、`audit_logs` 路由
- 已支持用户注册和登录
- 已支持项目 CRUD
- 已支持 API 测试用例 CRUD
- 已支持单条 API 测试执行
- 已支持选中 API 用例批量执行与批量删除
- 已支持执行结果入库
- 已保留 `schedule_tasks` 与 `run_queue` 模型
- 已建立并持续扩展 `pytest` 后端测试基线（持续增长中）
- 已建立统一异常响应格式与错误码体系（含全局异常处理）
- 已接入请求级 `request_id` 透传（响应头 `X-Request-ID`）
- 已建立结构化日志输出（JSON 单行日志）
- 已建立 `audit_logs` 审计表与关键写操作审计落库
- 已建立 Alembic 迁移基线（`alembic.ini` + `migrations/` + 初始 schema 版本）
- 已支持本地/测试环境 PostgreSQL 连接配置与迁移执行
- 已提供 PostgreSQL 本地编排文件与测试库初始化脚本
- 已提供一键启动脚本（Docker 启动 + 自动迁移 + 连通性自检）
- 已提供一键停止脚本（可选清理卷）与 API 启动脚本（数据库就绪后自动启动）
- 已提供 API 停止脚本（按端口停止 `uvicorn` 进程）
- 已完成路由层 DTO 统一：请求/响应模型全部切换到 `app/schemas/`
- 已补齐核心 ORM 模型关系映射（`relationship + back_populates`）
- 已完成领域模型治理细则落地（约束、索引、级联、生命周期）
- 已新增领域治理测试与接口侧防护（重名约束校验、方法规范化）
- 已完成审计治理闭环：查询接口、归档表、保留策略执行脚本（含 dry-run）
- 已落地最小 RBAC 闭环：`users.role`（`admin/user`）、`require_roles` 权限依赖、治理接口 admin 限制
- 已落地角色-权限矩阵与统一权限依赖：`app/permissions.py`、`require_permissions(...)`
- 已落地项目成员模型与接口：`project_members`、`/api/projects/{project_id}/members`
- 已落地组织层模型与接口：`organizations`、`organization_members`、`/api/organizations/*`
- 已落地跨项目成员治理：组织管理员可批量下发成员项目角色
- 已落地 API 套件模型与接口：`api_test_suites`、`api_test_suite_cases`、`/api/test-suites/*`
- 已落地批次执行模型与接口：`api_batch_runs`、`api_batch_run_items`、`/api/test-runs/suites/{suite_id}/run`
- 已落地批次查询接口：`/api/test-runs/batches/project/{project_id}`、`/api/test-runs/batches/{batch_id}`
- 已新增选中 API 用例批量执行接口：`POST /api/test-runs/project/{project_id}/batch-run`
- 已新增 API / Web 用例批量删除接口：`POST /api/test-cases/project/{project_id}/bulk-delete`、`POST /api/web-test-cases/project/{project_id}/bulk-delete`
- 已新增选中 Web 用例批量执行接口：`POST /api/web-test-runs/project/{project_id}/batch-run`
- 已新增 Web 批次结果接口：`GET /api/web-test-runs/batches/project/{project_id}`、`GET /api/web-test-runs/batches/{batch_id}`
- 已新增 Web 用例 Excel 资产流转接口：`GET /api/web-test-cases/project/{project_id}/template.xlsx`、`GET /api/web-test-cases/project/{project_id}/export.xlsx`、`POST /api/web-test-cases/project/{project_id}/import/xlsx`
- 已新增 Web 用例复制接口：`POST /api/web-test-cases/{case_id}/copy`
- 已落地环境与变量模型及接口：`project_environments`、`project_variables`、`environment_variables`、`/api/environments/*`
- 已落地变量组复用与环境绑定：`project_variables.group_name`、`environment_variable_group_bindings`、`/api/environments/*/variable-groups/*`
- 已落地密钥受控读取接口（管理权限 + 审计留痕）：`/api/environments/project/{project_id}/variables/{key}/secret-value`、`/api/environments/{environment_id}/variables/{key}/secret-value`
- 已落地执行详情运行时变量快照与来源追踪：`test_runs.runtime_variables/variable_sources`、`GET /api/test-runs/{run_id}`
- 已增强执行引擎：支持运行时变量替换、`contains/regex/jsonpath` 断言、响应数据提取与链路传递
- 已落地阶段 4 首批统一执行编排骨架：`execution_tasks/execution_jobs` 模型、统一编排入口与状态映射
- API/Web 单用例执行已接入统一编排入口（同步执行模式，队列/Worker 待后续阶段 4 任务）
- 已落地阶段 4 调度器最小可用：`schedule_tasks` 最小 API 与手动触发入队链路（`run_queue`）
- 已落地阶段 4 队列与 Worker 最小闭环：`/api/run-queue/claim`、`/api/run-queue/{id}/complete`、`/api/run-queue/worker/execute-once`、`/api/run-queue/worker/heartbeat`
- 已新增 `worker_heartbeats` 模型与迁移，支持项目级 Worker 心跳状态追踪
- 已落地阶段 4 执行管理最小可视化：调度/队列/Worker 监控页 `SchedulingDashboard` 与路由入口
- 已新增报告输入收敛服务：`app/services/reporting_input.py`（统一映射、失败分类、核心统计口径），并在统一结果接口中复用映射实现
- 已新增项目级报告摘要接口：`GET /api/reports/project/{project_id}/summary`（最小筛选 + Top 失败项）
- 已新增项目级趋势接口：`GET /api/reports/project/{project_id}/trends`（`granularity=day/week`，支持时间窗口与类型筛选）
- 已新增项目级失败治理接口：`GET /api/reports/project/{project_id}/failures`（失败分类筛选 + 可追溯详情路径）
- 已新增报告查询性能护栏：报告接口统一限制 `created_to - created_from <= 180 天`（防止超大窗口查询）
- 已新增跨项目运营总览接口：`GET /api/reports/operations/overview`（失败积压、死信积压、重试积压与按天重试趋势，支持 `project_ids/days`）
- 已为跨项目运营总览补齐稳定性 guardrails：`guardrails.alerts/degradation_reasons/project_signal_limit`，并在项目过多时执行 TopN 截断降级
- 已新增企业集成配置中心最小闭环：`integration_configs` 模型与迁移、`/api/integrations/*` 配置 CRUD、凭据脱敏展示与审计留痕
- 已新增企业集成事件收件箱：`integration_events` 模型与迁移、签名 Webhook 入站、幂等去重、事件重放与事件查询接口
- 已新增 CI/CD 最小闭环：`/api/integrations/{config_id}/cicd/trigger`、`/api/integrations/webhooks/{config_id}/cicd/callback`、`/api/integrations/{config_id}/cicd/runs`
- 已新增通知中心最小闭环：`notification_subscriptions`/`notification_deliveries` 模型与迁移、通知订阅管理、投递日志查询、失败重试与死信收敛
- 已新增缺陷联动最小闭环：`defect_sync_records` 模型与迁移、`/api/integrations/{config_id}/defects/sync`、`/api/integrations/project/{project_id}/defects/records`、失败指纹去重与建单/更新路径审计留痕
- 已新增 OAuth2 身份集成最小闭环：`identity_oauth_sessions`/`identity_provider_bindings` 模型与迁移、`/api/integrations/{config_id}/identity/oauth2/start`、`/api/integrations/{config_id}/identity/oauth2/callback`、`/api/integrations/{config_id}/identity/bindings`、state 会话校验与账号绑定策略（新建/关联/复用）
- 已增强治理执行能力：新增 `integration_governance_executions` 模型与迁移、`GET /api/integrations/project/{project_id}/governance/executions` 查询接口，并为 `POST /api/integrations/project/{project_id}/governance/retry-failed` 补齐幂等保护与结果复用

### 5.2 前端
- 已建立登录页、注册页、项目列表页、测试用例页
- 已建立统一请求封装
- 已建立基础路由守卫
- 已打通项目管理与 API 用例管理主链路
- 已支持在测试用例页面触发执行并查看最近结果
- 已支持批次结果页与执行详情页联动（批次列表 -> 批次详情 -> 执行详情）
- 已新增环境变量治理页并与执行详情联动（变量治理页 -> 执行详情变量快照）
- 已新增 Web 用例管理页与 Web 执行详情页，并打通路由入口（API 用例页 -> Web 用例页 -> Web 执行详情）
- 已新增 Web 批次结果页与详情页，并打通批量执行后跳转链路（Web 用例页 -> Web 批次列表 -> Web 批次详情 -> Web 执行详情）
- 已新增统一执行结果页（Execution Center），聚合 API/Web 执行记录并支持统一字段展示与详情跳转
- 已增强统一执行结果能力：支持 `run_type/status/time range` 筛选、分页与快速定位失败记录
- 已新增最小报告页（Report Center）：`frontend/src/views/ReportSummary.vue`（执行摘要 + Top 失败项）
- 已新增趋势最小可视化：Report Center 支持日/周趋势查询与条形图展示
- 已新增失败治理最小可视化：Report Center 支持失败分类筛选与失败记录详情追溯
- 已新增跨项目运营看板：`frontend/src/views/OperationsOverview.vue`（聚合指标卡 + 重试趋势 + 项目风险信号表）并挂载全局路由入口 `/operations/overview`
- 已完成前端框架与导航体验首轮优化：全局壳层支持深浅色切换、Workspace / Current Project 导航分区与项目仪表盘首页
- 已完成 API 测试页首轮产品化改造：`TestCaseList.vue` 升级为工作台式布局，支持资产树浏览、内联编辑、JSON/OpenAPI 导入与执行反馈面板
- 已完成 Web 测试页首轮产品化改造：`WebTestCaseList.vue` 升级为 UI 自动化工作台布局，支持步骤编排、执行日志、运行记录切换与配置分区展示
- 已补齐 API / Web 工作台批量操作入口：API 资产树支持多选、批量执行、批量删除；Web 工作台新增用例清单选择区，支持多选、批量执行、批量删除
- 已补齐 Web 工作台步骤插入与 Excel 资产流转：步骤支持前插/后插；支持下载双语 Excel 模板、导出当前项目 Web 用例、按 Excel 回导更新/新建用例，并提供字段说明 sheet
- 已补齐 Web 工作台复制能力：当前选中 Web 用例可一键复制生成副本，并保留原有执行配置与步骤编排
- 已完成统一结果与报告页首轮产品化改造：`UnifiedRunList.vue`、`ReportSummary.vue` 已按报告工作台风格重做，统一筛选、图表、列表与详情视图语法

### 5.3 文档
- 已补充项目概览文档
- 已补充系统架构文档
- 已补充模块清单、领域模型、技术栈、仓库结构文档
- 已新增企业级平台总纲文档
- 已补齐阶段性开发/验收清单（现已归档清理）

## 6. 当前部分完成内容

### 6.1 认证
- 已完成 JWT 访问令牌与刷新令牌基础链路
- 已完成 Bearer 鉴权接入与受保护接口校验
- 已完成密码哈希存储（兼容历史明文用户登录后自动迁移）
- 已完成最小 RBAC（`admin/user`）与关键治理接口权限校验
- 已完成角色-权限矩阵基础落地（`app/permissions.py`）与统一权限依赖
- 已补齐核心资源越权访问校验，越权场景统一返回 `403 FORBIDDEN`
- 已落地项目成员模型（`project_members`）与成员协作权限（`maintainer/editor/viewer`）
- 已落地组织层级与跨项目成员治理基础能力（组织成员、项目归属、跨项目角色下发）
- 已完成组织级权限治理深化收口（部门/工作区维度 + 组织策略细化）：组织成员新增 `department/workspace` 维度，成员治理接口支持维度维护与筛选，跨项目治理新增同部门/同工作区策略边界校验

### 6.2 执行能力
- 已支持单条 API 用例执行
- 已支持选中 API 用例批量执行与 API 套件执行（按所选顺序或套件顺序执行）
- 已支持批次级状态汇总与明细追踪（`success/failed/error`）
- 已支持 Web 单用例自动化执行与选中用例批量执行（含步骤日志与产物路径查询），并支持复制与 Excel 管理用例资产
- 已支持 Web 批量执行结果持久化与按批次查询，不再只依赖临时汇总响应

### 6.3 结果展示
- 当前已记录单次执行结果与套件批次结果
- 已支持按项目查询批次列表与批次明细
- 已形成阶段 2 最小结果可视化闭环（批次结果页、批次详情、执行详情）
- 已形成 API/Web 统一执行结果查询与前端聚合展示（`/api/test-runs/project/{project_id}/unified-results` + Execution Center）
- 已形成阶段 5 最小报告中心与趋势/失败治理分析闭环，后续在阶段 6 持续增强高级分析能力

### 6.4 数据库迁移
- 已完成 Alembic 基线和本地/测试 PostgreSQL 落地
- 已提供生产环境迁移/回滚脚本（`scripts/prod-db-migrate.ps1`、`scripts/prod-db-rollback.ps1`），含强制确认、可选备份、可选自检与迁移清单留痕
- 已固化生产迁移发布与回滚 runbook
- 已完成窗口流程本地实操演练与留档脚本（`scripts/prod-db-window-drill.ps1`），并生成演练记录
- 真实生产环境窗口实操演练仍待执行

### 6.5 调度与队列
- 数据模型已存在
- 已落地最小调度触发与入队链路（`schedule_tasks` -> `run_queue`）
- 已落地最小 Worker 闭环：任务领取、占位执行、状态回写与心跳上报
- 已落地前端调度/队列/Worker 最小管理页面（列表与详情）
- 已建立阶段 4 SSOT 与任务分解（S4-00 已完成）
- 已完成 S4-01：统一执行编排骨架（ExecutionTask/ExecutionJob + API/Web 单用例接入）
- 已完成 S4-02：`schedule_tasks` 最小 API 与 trigger 入队链路
- 已完成 S4-03：队列与 Worker 最小闭环（run_queue + Worker 心跳/消费占位）
- 已完成 S4-04：执行管理最小可视化（Scheduling Dashboard）
- 已完成 S4-05：阶段验收与切换准备（阶段 4 已验收完成）

### 6.6 审计治理
- 已提供审计日志查询接口（按用户、动作、结果、request_id、时间范围筛选）
- 已提供审计归档表 `audit_logs_archive`
- 已提供保留策略执行脚本 `scripts/audit-governance-run.py`（支持 dry-run）
- 已补齐生产化编排基础能力：锁文件防重入、执行清单留痕、阈值告警、生产执行脚本 `scripts/prod-audit-governance-run.ps1`
- 已补齐真实定时任务与告警联动脚本：`setup-audit-governance-schedule.ps1`、`remove-audit-governance-schedule.ps1`、`alert_webhook_notify.py`
- 已完成一次联调演练（本地生产参数）：`prod-audit-governance-run.ps1` 全链路执行通过，并验证“阈值触发 -> webhook 回调”闭环（`FailOnAlert + AlertWebhookUrl`）
- 已完成定时任务注册命令联调校验（DryRun）：`setup-audit-governance-schedule.ps1` 成功输出 `schtasks /Create` 命令
- 仍需在真实生产环境完成任务注册与告警平台配置生效验证

### 6.7 阶段切换状态（2026-03-13）
- 已按项目决策将阶段 1 调整为“暂停”，并将阶段 2 调整为“进行中”
- 阶段 1 未完成项（生产窗口演练、审计治理生产联调）转为风险托管项
- 阶段 2 当前处于启动态，功能代码交付将从 API 套件、批量执行、环境变量能力开始

### 6.8 阶段切换状态（2026-03-16）
- 阶段 2 状态由“进行中”切换为“收尾中”，以阶段验收与收尾优化为主
- 阶段 3 状态由“未开始”切换为“启动中”，已解除 Web 模块实现门禁并进入首批建设准备

### 6.9 阶段切换状态（2026-03-16）
- 阶段 3 状态由“启动中”切换为“收尾中”，首批闭环（S3-00~S3-04）已全部完成
- 阶段 4 状态由“未开始”切换为“启动中”，已建立阶段 4 开发清单并进入首批骨架建设准备

## 7. 当前未开始内容

- 多环境与变量管理（高级能力：第三方密钥托管系统对接、变量组版本化治理）
- API 套件与批量执行（高级能力：重试策略、并发编排）
- 调度系统与分布式执行
- 报告高级分析能力（跨版本对比、慢步骤根因、治理看板深化）
- CI/CD 集成
- SSO / LDAP 高级集成能力（多提供商、多租户策略与治理增强）
- 缺陷管理平台对接

## 8. 当前代码基线判断

以下内容可视为后续建设的基础：

- `app/services/test_executor.py`
  - 可演进为 API 执行引擎起点
- `app/models/schedule_task.py`
  - 可演进为调度任务模型起点
- `app/models/run_queue.py`
  - 可演进为执行队列模型起点
- `app/api/test_runs.py`
  - 可演进为统一执行入口的一部分
- `frontend/src/views/TestCaseList.vue`
  - 当前承担过多职责，后续应拆分

## 当前阶段优先事项（阶段 2 收尾 / 阶段 3 收尾 / 阶段 5 已完成验收 / 阶段 6 已完成验收 / 阶段 7 已完成验收 + 平台功能完善并行工作线）

### P0：平台功能完善并行工作线（启动中）
- 已新增 `docs/project/platform-function-hardening-plan.md`，明确该工作线不替代原阶段 8 / 9。
- 当前聚焦：现有功能从“最小闭环”向“可投入使用”演进。
- 计划模块：项目与资产、API 测试、Web 测试、执行与调度、结果与报告、企业集成、缺陷修复与收口评审。
- 当前进行：FH-07 / FH-08 收口阶段（缺陷台账、全量回归、最终交付说明已启动）。

### P1：API 平台化首批落地（已完成）
- 已完成 API 套件模型与基础 CRUD
- 已完成批量执行最小闭环（套件触发、批次记录、结果聚合）
- 已完成环境与变量最小能力（项目级/环境级 + 执行替换）

### P2：执行与断言增强（进行中）
- 已落地断言能力（JSONPath / 正则 / 包含 / Schema）
- 已落地响应数据提取与链路变量传递
- 已落地 API 用例分组/标签/筛选/搜索（后端查询参数 + 前端筛选入口）
- 已落地变量治理增强（S2-06）：变量组复用、密钥受控读取、前端治理页、执行详情变量快照
- 执行详情页与批次结果页面已落地，后续需持续增强展示维度

### P3：阶段 1 遗留风险托管（暂停态）
- PostgreSQL 真实生产环境迁移发布演练与窗口执行（按当前决策不做压测）
- 审计治理生产定时任务与告警平台联动生产验证（脚本已落地）

### P4：阶段 3 收尾项（进行中）
- Web 领域模型首批设计与落地（`WebTestCase`、`WebStep`、`Locator`）（已完成）
- Playwright 执行引擎最小闭环接入（单用例执行）（已完成）
- Web 执行结果基础展示页与产物链路预留（已完成：Web 用例管理页 + Web 执行详情页 + 路由入口）
- API/Web 统一归档展示对齐（S3-04，已完成：统一结果接口 + Execution Center）

### P5：阶段 4 验收完成（已收口）
- 已完成阶段 4 SSOT 建立（阶段文档现已归档）
- 已完成 S4-01：统一执行编排骨架（Execution Task/Job + API/Web 适配层）
- 已完成 S4-02：调度器最小可用（schedule_tasks 触发链路）
- 已完成 S4-03：队列与 Worker 最小闭环（run_queue + Worker 心跳/消费占位）
- 已完成 S4-04：执行管理最小可视化（前端）
- 已完成 S4-05：阶段验收与切换准备（验收结论已通过）。

### P6：阶段 6 企业集成（已完成验收）
- 已完成 S6-00：阶段 6 开发清单与验收清单落盘，建立可中断恢复机制。
- 已完成 S6-01：集成配置中心最小闭环（模型 + 迁移 + API + 鉴权 + 审计）并通过门禁。
- 已完成 S6-02：事件与签名回调最小闭环（签名校验 + 幂等去重 + 事件重放 + 查询）并通过门禁。
- 已完成 S6-03：CI/CD 最小闭环（触发 -> 回调 -> 状态收敛）并通过门禁。
- 已完成 S6-05：缺陷联动最小闭环（Jira 适配切片、失败指纹去重、建单/更新路径、记录查询与审计）。
- 已完成 S6-06：OAuth2 身份集成最小闭环（授权启动、回调校验、账号绑定与令牌签发）。
- 已完成 S6-07：治理增强最小闭环（健康看板汇总、失败/死信治理重试、集成域审计补齐、前端治理入口挂载）。
- 已完成 S6-08：阶段验收收口与切换准备（受控通过）。
- 下一步：转入阶段 7 后运营维护，优先关注生产/准生产环境性能画像、外部告警通道接入与更多 provider/治理动作扩展。

## 10. 最近更新记录
### 2026-04-21
- 修复本地开发端口切换登录报错：后端 CORS 由固定白名单扩展为允许 `localhost / 127.0.0.1` 的任意本地端口，解决前端切到 `5175` 后登录预检被拒的问题。
- 验证通过：`python -m pytest tests/backend/test_error_response_format.py tests/backend/test_health_and_auth.py -q`（9 passed）。
### 2026-04-17
- 新增 Web 用例复制能力：`POST /api/web-test-cases/{case_id}/copy` 已落地，前端 UI 自动化页补齐“复制”按钮，可基于当前用例直接生成副本，并自动切换到新副本继续编辑。
- 复制副本会保留原用例的描述、Base URL、浏览器/视口/超时/录像等执行配置，以及完整步骤编排；名称按 `原名-copy` 自动去重生成。
- 验证通过：`python -m pytest tests/backend/test_web_test_cases_api.py -q`（7 passed）；`npm run build`（frontend）通过。
### 2026-04-17
- 修复执行类请求超时误报：前端全局 `10000ms` 超时会把实际仍在运行的 API / Web 执行请求提前判失败；现已为 `runWebTestCase / runBatchWebTestCases / runTestCase / runBatchTestCases / runTestSuite` 单独提升超时窗口，避免“后端已成功执行但前端超时误报失败”。
- 结合本地 PostgreSQL 核对：`project_id=10 (DSDL)` 的 Web 批量执行在数据库中真实状态为 `success`，此前页面弹窗属于超时误报而非执行失败。
- 验证通过：`npm run build`（frontend）通过。
### 2026-04-17
- 新增 Web 批次结果页闭环：选中 Web 用例批量执行现在会持久化 `web_batch_runs / web_batch_run_items`，并补齐列表、详情与执行详情跳转，不再只返回一次性汇总结果。
- Web 工作台的“批次结果”入口已切换到独立的 Web 批次列表；批量执行成功后会直接进入对应 Web 批次详情页，失败批次也可按条查看具体 run。
- 验证通过：`python -m pytest tests/backend/test_web_test_runs_api.py tests/backend/test_reporting_summary_api.py tests/backend/test_unified_results_api.py -q`（10 passed）；`npm run build`（frontend）通过；`python -m alembic upgrade head` 已验证 SQLite 与 PostgreSQL 均可升级到 `3d9e7b1c4a2f`.
### 2026-04-17
- 修复 Web 批量执行误报失败：核对本地 PostgreSQL 中 `project_id=10 (DSDL)` 的 `web_test_runs` 与 `audit_logs` 后确认批量执行真实结果为 `success`，前端 `WebTestCaseList.vue` 仅在批量请求成功后的界面同步阶段误触发失败提示。
- 批量执行前端现改为区分“请求失败”和“执行结果失败”：请求异常才弹“批量执行请求失败”，业务结果为 `failed/error` 时展示成功/失败/异常汇总，且优先定位首个失败 run，不再把成功执行误报为失败。
- 验证通过：读取本地 PostgreSQL 记录确认 `web_test_run.batch_execute` 为 `success`；`python -m pytest tests/backend/test_web_test_runs_api.py tests/backend/test_reporting_summary_api.py tests/backend/test_unified_results_api.py -q`（10 passed）；`npm run build`（frontend）通过。
### 2026-04-17
- 推进 Web UI 自动化工作台增强：步骤编辑区新增“前插/后插”能力，已添加步骤中可直接插入新步骤，不再只能末尾追加。
- 新增 Web 用例 Excel 管理链路：支持下载双语模板、导出当前项目 Web 用例、按 Excel 回导新建/更新用例；模板内附带 `字段说明 Field Guide` sheet 解释各字段用途。
- 验证通过：`python -m pytest tests/backend/test_web_test_cases_api.py -q`（6 passed）；`npm run build`（frontend）通过。
### 2026-04-03
- 修复 PostgreSQL 开发启动阻塞：迁移 `migrations/versions/2b7c4e1a9d0f_phase4_queue_cancel_status.py` 去掉对 `sqlite_master` 的硬编码依赖，改为通过通用约束检查兼容 SQLite / PostgreSQL，避免 `npm run dev` 在本地 pgsql 上因自动迁移失败导致后端未启动。
- 验证通过：`python -m alembic current`（PostgreSQL 本地库返回 `2b7c4e1a9d0f (head)`）；真实链路验证通过（注册 / 登录 / 创建项目 / 查询项目）；`python -m pytest tests/backend/test_projects_api.py tests/backend/test_health_and_auth.py -q`（9 passed）。
### 2026-04-03
- 修复仪表盘加载兜底：`Dashboard.vue` 现会校验本地缓存的当前项目是否仍可访问，若项目已删除或无权限则自动回退到首个可访问项目，避免首页直接提示“加载仪表盘失败”。
- 验证通过：`npm run build`（frontend）通过。
### 2026-04-03
- 推进 FH-02 / FH-03：API 工作台新增多选批量执行 / 批量删除，复用批次结果页承接批量回归详情；Web 工作台新增用例清单选择区，支持多选批量执行与批量删除。
- 后端补齐页面批量链路：新增 `/api/test-runs/project/{project_id}/batch-run`、`/api/test-cases/project/{project_id}/bulk-delete`、`/api/web-test-runs/project/{project_id}/batch-run`、`/api/web-test-cases/project/{project_id}/bulk-delete`。
- 验证通过：`python -m pytest tests/backend/test_test_cases_api.py tests/backend/test_test_runs_api.py tests/backend/test_web_test_cases_api.py tests/backend/test_web_test_runs_api.py -q`（31 passed）；`npm run build`（frontend）通过。
### 2026-04-03
- 重写根目录 `README.md`，改为面向交付用户的一页式入口说明，聚合启动方式、访问地址、上手路径、关键文档与常用命令。
- 当前对外主入口文档已统一为：`README.md`（仓库入口）+ `docs/README.md`（文档导航）+ `docs/project/user-manual.md`（详细使用说明）。
### 2026-04-03
- 新增正式用户手册：`docs/project/user-manual.md`，覆盖启动、登录、项目管理、环境变量、API 测试、Web 测试、调度、报告、集成治理与常见问题，作为面向使用者的主入口文档。
- 清理阶段性冗余文档：删除阶段 2~7 的开发/验收清单与临时交接摘要，仅保留持续有效的总进度、交付说明、缺陷台账、功能完善计划、报告输入契约与用户手册。
- 更新文档导航：`docs/README.md` 重写为面向“使用者 / 维护者 / 技术排查”的稳定入口。
### 2026-04-03
- 推进 FH-04 / FH-05：调度页支持取消队列任务，报告页支持导出当前筛选快照 JSON，执行与分析动作更完整。
- 本地数据库迁移状态同步到最新 head：当前 `python -m alembic current` 为 `2b7c4e1a9d0f (head)`。
- 验证通过：`python -m pytest tests/backend/test_queue_worker_api.py tests/backend/test_reporting_summary_api.py tests/backend/test_reporting_trends_api.py tests/backend/test_reporting_failures_api.py -q`（12 passed）；`npm run build`（frontend）通过。
### 2026-04-02
- 推进 FH-03：`WebTestCaseList.vue` 的步骤编辑器由原始 JSON 输入改为结构化定位编辑，支持 CSS / XPath / Text / TestId / Role 下拉选择与单输入框填写。
- `web_executor.py` 同步支持多种定位策略解析，`wait` 步骤兼容“等待元素”与“固定等待”两种模式，保留旧 `selector` 参数兼容。
- 验证通过：`python -m pytest tests/backend/test_web_executor.py tests/backend/test_web_test_cases_api.py tests/backend/test_web_test_runs_api.py -q`（10 passed）；`npm run build`（frontend）通过。
### 2026-04-01
- 推进 FH-07 / FH-08：新增 `docs/project/defect-register.md` 与 `docs/project/final-delivery-summary.md`，沉淀已处理项、保留风险、数据库迁移修复与最终交付结论。
- 执行验证：`python -m pytest tests/backend -q` 全量通过；`npm run build`（frontend）通过。
### 2026-04-01
- 推进 FH-06：`IntegrationGovernanceDashboard.vue` 重构为企业集成工作台，接入通知订阅/投递、缺陷记录、CI/CD 运行、身份绑定、治理执行与集成配置查询链路。
- 集成治理页支持实操动作：失败积压重试、通知订阅创建、测试派发、投递重试、凭据查看、缺陷定位与项目切换。
- 验证通过：`python -m pytest tests/backend/test_integration_notifications_api.py tests/backend/test_integration_cicd_api.py tests/backend/test_integration_defect_api.py tests/backend/test_integration_identity_oauth_api.py -q`（14 passed）；`npm run build`（frontend）通过。
### 2026-04-01
- 推进 FH-03：Web 用例新增执行配置持久化字段（浏览器、窗口、超时、headless、失败截图、录制视频），`WebTestCaseList.vue` 配置区从占位切换为真实可保存配置，执行器同步接入这些配置。
- 推进 FH-04 / FH-05：执行中心新增统一“重跑”入口，报告详情新增“打开执行中心 / 定位首个失败”入口，排障与回归动作更闭环。
- 迁移验证通过：使用临时空库执行 `python -m alembic upgrade head` 成功升级到 `1f4e2a7c9b3d`；当前本地 `test_platform.db` 因历史 Alembic 状态不一致未直接升级。
- 验证通过：`python -m pytest tests/backend/test_web_test_cases_api.py tests/backend/test_test_runs_api.py -q`（10 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- 推进 FH-02：统一导入 provider 链路新增 Postman Collection 支持，`TestCaseList.vue` 导入弹窗现覆盖 JSON / OpenAPI / Postman 三类导入入口。
- API 工作台继续增强：套件治理入口与多源导入入口同时落地，日常回归工作流更完整。
- 验证通过：`python -m pytest tests/backend/test_test_cases_api.py tests/backend/test_suite_batch_runs_api.py -q`（18 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- 启动 FH-02：`TestCaseList.vue` 新增 API 套件工作台，支持套件创建、选择、加入/移出当前用例、套件执行与环境选择，补齐日常回归链路的前端入口。
- 验证通过：`python -m pytest tests/backend/test_suite_batch_runs_api.py tests/backend/test_project_members_api.py tests/backend/test_environments_api.py -q`（14 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- 收口 FH-01：补齐项目详情抽屉、成员治理弹窗与用户列表接口，项目、成员、环境、变量治理形成首个可用闭环。
- 项目详情现统一承接资产流转入口：支持进入 API / UI / 环境 / 成员 / 报告，并补齐 API 用例导出入口。
- 验证通过：`python -m pytest tests/backend/test_project_members_api.py tests/backend/test_environments_api.py -q`（10 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- 推进 FH-01：补齐项目成员管理前端，新增 `/api/users` 最小用户列表接口、项目成员用户名返回字段，并在 `ProjectList.vue` 中落地成员治理弹窗（列表、角色调整、添加、移除）。
- 项目管理页同步补齐成员统计：项目卡片现展示真实成员数量，项目成员治理入口不再是占位按钮。
- 验证通过：`python -m pytest tests/backend/test_project_members_api.py tests/backend/test_environments_api.py -q`（10 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- 启动 FH-01：重构 `EnvironmentManager.vue`，将环境与变量治理页升级为统一工作台布局，补齐项目切换、环境卡片管理、项目/环境变量编辑与变量组绑定分区。
- 同步补齐环境管理前端接口：新增环境更新 / 删除调用，环境治理页现已覆盖环境、变量、变量组、密钥明文查看等现有后端能力。
- 验证通过：`python -m pytest tests/backend/test_environments_api.py -q`（4 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- 完成前端主工作台 UI 对齐改造：`App.vue` 现按设计稿切换为统一后台壳层，并补齐 `仪表盘 / 项目管理 / 测试用例 / API测试 / UI自动化 / 任务管理 / 测试报告` 导航映射。
- 新增 `Dashboard.vue` 与 `TestCases.vue`：前者承接项目级执行概览与最近执行记录，后者提供跨类型用例浏览工作台；现有 `ProjectList.vue`、`SchedulingDashboard.vue` 同步按新 UI 结构重做。
- 补齐项目切换入口：`TestCaseList.vue`、`WebTestCaseList.vue`、`SchedulingDashboard.vue` 现均支持直接切换当前项目，并在路由切换后自动刷新页面数据与上下文。
- 保留并迁移现有能力入口：项目级 API/UI/任务/报告/环境/集成/批次等能力继续可达，其中设计稿未覆盖的能力按同一视觉风格补充到项目页、API 页与 UI 页扩展入口中。
- 验证通过：`npm run build`（frontend）通过。
### 2026-03-31
- 修复 API 测试执行覆盖链路：`POST /api/test-runs/test-cases/{id}/run` 现支持接收当前编辑态的 `method/url/headers/body/expected_status/expected_body/assertion_rules/extraction_rules`，本次执行不再被数据库中的旧断言配置强行覆盖。
- 后端区分“字段未传”与“显式传 `null` / 空白”：页面执行时可显式清空旧 `expected_body` / `assertion_rules`，避免历史脏数据继续把正确响应判为 `failed`。
- 断言兜底与前端同步修正：空白 `expected_body` 不再参与响应体断言；`TestCaseList.vue` 执行时直接提交当前表单中的断言/提取配置，空值统一传 `null`。
- 兼容旧占位脏数据：对历史遗留的 `headers/body/expected_body/assertion_rules/extraction_rules` 默认 `{}` / `\"{}\"` 占位值增加执行期兜底，GET 页面抓取场景不再把这类占位值误当成真实断言。
- 验证通过：`python -m pytest tests/backend/test_test_executor_enhancements.py tests/backend/test_test_runs_api.py -q`（15 passed）；`npm run build`（frontend）通过。
### 2026-03-31
- 删除旧入口：移除 `docs/project/platform-improvement-checklist.md`。
- 新增并行工作线文档：`docs/project/platform-function-hardening-plan.md`，后续聚焦现有功能从最小闭环向“可投入使用”演进。
- 当前断点：FH-01 已完成，进入 FH-02（API 测试功能完善）执行中，当前聚焦 API 套件与回归工作台。
### 2026-03-30
- PF-02 / PF-04 细节对齐增强：继续收敛 `frontend/src/App.vue`、`frontend/src/views/TestCaseList.vue`、`frontend/src/views/UnifiedRunList.vue`、`frontend/src/views/ReportSummary.vue` 的视觉细节，减少旧风格残留。
- 前端构建通过：`npm run build`（frontend）。
### 2026-03-30
- 完成 PF-04：重做 `frontend/src/views/UnifiedRunList.vue`，按提供的 React UI `TestReports.tsx` 结构落地为统一执行结果工作台。
- 完成 PF-04：重做 `frontend/src/views/ReportSummary.vue`，将统计、趋势、失败治理与详情查看统一到报告工作台风格。
- 功能承接：保留统一结果筛选/分页/失败定位与报告摘要/趋势/失败治理等现有能力，并按新 UI 风格重新组织。
- 前端构建通过：`npm run build`（frontend）。
- 平台完善工作线推进：当前断点由 PF-04 切换为 PF-05（缺陷修复与稳定性回归）准备。
### 2026-03-30
- 完成 PF-03：重做 `frontend/src/views/WebTestCaseList.vue`，按提供的 React UI `UiAutomation.tsx` 结构落地为 UI 自动化工作台。
- 功能承接：保留现有 Web 用例切换、创建、保存、删除、执行、执行详情查看与产物查看能力，并按新 UI 风格重新组织。
- 前端构建通过：`npm run build`（frontend）。
- 平台完善工作线推进：当前断点由 PF-03 切换为 PF-04（统一结果与报告体验优化）准备。
### 2026-03-30
- 修复本地开发启动韧性：`scripts/dev-runner.mjs` 不再强依赖失效的 `.venv\Scripts\python.exe`，会自动回退到系统 `python` / `py -3`。
- 新增 PowerShell 启动脚本：`scripts/dev-start.ps1`，用于规避 `\\?\D:\...` 设备路径下 `npm.cmd` / `cmd.exe` 无法正常工作的场景。
- 同步更新 `docs/tech/tech-stack.md` 的开发运行说明，补充 PowerShell 异常路径下的启动方式。
### 2026-03-30
- PF-02 对齐增强：`frontend/src/App.vue` 改按提供的 React UI `Layout.tsx` 结构重做，全局壳层切换为深色侧边栏 + 顶部搜索 + 页签栏的后台管理样式。
- PF-02 对齐增强：`frontend/src/views/ProjectList.vue` 改按 Dashboard 风格重做，首页统一到统计卡片 + 功能分区 + 项目表格布局。
- PF-02 对齐增强：`frontend/src/views/TestCaseList.vue` 继续按 `ApiTest.tsx` 视觉语法收敛，避免仍保留原有平台风格。
- 前端构建通过：`npm run build`（frontend）。

### 2026-03-30
- 完成 PF-02：重做 `frontend/src/views/TestCaseList.vue`，将 API 测试页升级为“资产树 + 编辑工作台 + 执行反馈”布局。
- 功能承接：保留并增强现有新建、保存、执行、复制、删除、JSON 导入、OpenAPI 导入、导出等能力；新增更明确的 API 页面功能分区入口。
- 前端构建通过：`npm run build`（frontend）。
- 平台完善工作线推进：当前断点由 PF-02 切换为 PF-03（Web 测试产品化完善）准备。
### 2026-03-27
- 完成 PF-01：重做前端全局应用壳层与项目仪表盘，新增深浅色切换、导航分区与更清晰的项目列表入口结构。
- 前端构建通过：`npm run build`（frontend）。
- 平台完善工作线推进：当前断点由 PF-01 切换为 PF-02（API 测试产品化完善）准备。
### 2026-03-27
- 新增并行工作线文档（后于 2026-03-31 替换为 `docs/project/platform-function-hardening-plan.md`），用于承载前端页面优化、现有功能完善与 bug 修复。
- 路线说明：该工作线不替代原阶段 8 / 9，仅作为阶段 7 验收后的产品完善与体验优化工作线。
- 当前断点：进入平台完善工作线 PF-01 准备，优先处理前端框架与导航体验优化。
### 2026-03-26
- 完成 S7-06：执行阶段 7 最小回归、后端全量回归、前端构建与迁移链路校验，门禁全部通过。
- 验收结论：阶段 7 满足 A7-01~A7-06，状态由“启动中”切换为“已完成验收”。
- 后续输入：项目转入“运营维护 + 受控演进”阶段，重点关注生产环境性能画像、告警通道接入与扩展能力继续演进。
### 2026-03-26
- 完成 S7-05：补齐阶段 7 关键链路稳定性门禁，为运营总览接口新增 `guardrails` 输出（告警、降级原因、TopN 截断信息）。
- 新增容量/性能基线：中等数据量下验证 `GET /api/reports/operations/overview` 与 `GET /api/integrations/project/{project_id}/governance/executions` 响应性能门限。
- 前端增强：`OperationsOverview.vue` 新增降级提示与告警卡片，前端对运营总览的异常信号具备可见性。
- 测试门禁通过：`python -m pytest tests/backend/test_operations_overview_api.py tests/backend/test_reporting_performance_guards.py tests/backend/test_integration_governance_api.py -q`（11 passed）。
- 前端构建通过：`npm run build`（frontend）。
- 阶段推进：阶段 7 状态保持“启动中”，当前断点由 S7-05 切换为 S7-06 准备。
### 2026-03-26
- 完成 S7-04：治理执行增强最小闭环已落地（批量治理幂等保护、治理执行记录、项目级治理执行查询接口）。
- 新增模型与迁移：`app/models/integration_governance_execution.py`、`migrations/versions/6c8b1f2a9d4e_phase7_governance_execution_tracking.py`。
- 接口增强：`POST /api/integrations/project/{project_id}/governance/retry-failed` 新增 `idempotency_key`，重复请求可直接复用既有执行结果；新增 `GET /api/integrations/project/{project_id}/governance/executions` 用于治理执行历史追踪。
- 审计标准化：批量治理与单事件治理审计补齐统一追踪字段（`governance_execution_id`、`execution_type`、`idempotency_key`、`governance_scope`）。
- 测试门禁通过：`python -m pytest tests/backend/test_integration_governance_api.py -q`（5 passed）；集成域相关回归 `python -m pytest tests/backend/test_integrations_api.py tests/backend/test_integration_events_api.py tests/backend/test_integration_cicd_api.py tests/backend/test_integration_notifications_api.py tests/backend/test_integration_defect_api.py tests/backend/test_integration_identity_oauth_api.py tests/backend/test_integration_governance_api.py -q`（27 passed）。
- 迁移链路验证通过：`alembic upgrade head -> downgrade 4c7b2d1e9a6f -> upgrade head`（SQLite 临时库）。
- 阶段推进：阶段 7 状态保持“启动中”，当前断点由 S7-04 切换为 S7-05 准备。
### 2026-03-18
- 完成 S7-03：落地跨项目运营看板最小闭环（后端聚合 API + 前端总览页面 + 全局导航入口）。
- 后端新增 `GET /api/reports/operations/overview`，支持失败积压、死信积压、重试积压与 7/14/30 天重试趋势；默认按当前用户可见项目聚合，并对 `project_ids` 越权筛选返回 `403 FORBIDDEN`。
- 前端新增 `OperationsOverview.vue` 与路由 `/operations/overview`，支持趋势窗口切换与项目级风险信号展示。
- 测试门禁通过：`python -m pytest tests/backend/test_operations_overview_api.py -q`（2 passed）；相关报告回归 `python -m pytest tests/backend/test_reporting_summary_api.py tests/backend/test_reporting_failures_api.py tests/backend/test_reporting_trends_api.py tests/backend/test_reporting_audit_api.py tests/backend/test_reporting_performance_guards.py -q`（11 passed）。
- 前端构建通过：`npm run build`（frontend）。
- 阶段推进：阶段 7 状态保持“启动中”，当前断点由 S7-03 切换为 S7-04 准备。
### 2026-03-17
- 完成 S7-02：Provider Registry 最小骨架已落地（`app/services/test_case_import_providers.py`、`POST /api/test-cases/project/{project_id}/import/provider`、`GET /api/test-cases/import/providers`）。
- 运行时策略：支持 provider 显式选择与按 payload 自动回退（openapi provider）。
- 测试门禁：`python -m pytest tests/backend/test_import_provider_registry.py tests/backend/test_test_cases_api.py -k "openapi or provider" -q` 通过（8 passed）。
- 阶段推进：阶段 7 状态保持“启动中”，当前断点切换为 S7-03 准备。
- 文档口径同步：已同步更新阶段 7 开发/验收清单、API 模块 SKILL 与架构总纲。
- 完成 S7-01：OpenAPI 导入最小闭环已落地（`app/schemas/api_test_case.py`、`app/api/test_cases.py`），支持 OpenAPI 3.x 规范最小映射与重复去重。
- 测试门禁：`python -m pytest tests/backend/test_test_cases_api.py -k openapi -q` 通过（4 passed）。
- 阶段推进：阶段 7 状态保持“启动中”，当前断点切换为 S7-02 准备。
- 文档口径同步：已同步更新阶段 7 开发/验收清单与架构总纲。
- 完成 S6-08：阶段 6 验收收口，并完成验收执行记录与收口结论归档。
- 阶段状态切换：阶段 6 由“启动中”切换为“已完成验收”，企业集成进度由 60% 更新为 80%。
- 测试门禁：阶段 6 最小回归通过（25 passed），前端构建通过（`npm run build`）；后端全量回归受 `tests/backend/test_db_migration_workflow.py` 临时目录权限（WinError 5）阻塞，受控排除该用例后其余全量回归通过。
- 文档口径同步：已同步更新阶段 6 开发清单、验收清单、架构总纲与 09-enterprise-integrations 模块 SKILL。
### 2026-03-17
- 完成 S6-06：新增 OAuth2 身份集成最小闭环（app/models/identity_oauth_session.py、app/models/identity_provider_binding.py、migrations/versions/4c7b2d1e9a6f_phase6_identity_oauth_minimal.py、/api/integrations/{config_id}/identity/oauth2/start、/api/integrations/{config_id}/identity/oauth2/callback、/api/integrations/{config_id}/identity/bindings）。
- S6-06 能力：支持 OAuth2 state 会话与过期校验、一次性回调消费、账号绑定策略（新用户创建/已有用户关联/既有绑定复用）与回调后令牌签发。
- S6-06 测试门禁：新增 tests/backend/test_integration_identity_oauth_api.py（3 passed）；S6 相关回归通过 python -m pytest tests/backend/test_integration_identity_oauth_api.py tests/backend/test_integration_defect_api.py tests/backend/test_integrations_api.py tests/backend/test_integration_events_api.py tests/backend/test_integration_cicd_api.py tests/backend/test_integration_notifications_api.py -q（22 passed）。
### 2026-03-17
- 完成 S6-05：新增缺陷联动最小闭环（`app/models/defect_sync_record.py`、`migrations/versions/5f1e2a9c7d3b_phase6_defect_sync_minimal.py`、`/api/integrations/{config_id}/defects/sync`、`/api/integrations/project/{project_id}/defects/records`）。
- S6-05 能力：支持失败执行字段映射、失败指纹去重（同模式不重复建单）、既有缺陷单更新路径与事件审计（integration_defect.sync、integration_defect.record.list）。
- S6-05 测试门禁：新增 `tests/backend/test_integration_defect_api.py`（3 passed）；S6 相关回归通过 `python -m pytest tests/backend/test_integration_defect_api.py tests/backend/test_integrations_api.py tests/backend/test_integration_events_api.py tests/backend/test_integration_cicd_api.py tests/backend/test_integration_notifications_api.py -q`（19 passed）。
- 说明：`tests/backend/test_db_migration_workflow.py` 在当前环境受 `pytest` 临时目录权限限制（WinError 5）未完成执行；本次改动已补齐迁移文件并完成相关接口回归验证。
### 2026-03-17
- 文档口径补齐：同步修订 docs/project/project-overview.md，更新为“阶段 5 已验收完成、阶段 6 启动中（S6-04 已完成）”并移除已过期“未打通能力”表述。
- 阶段 6 验收口径已完成对齐并归档。
- 模块 SKILL 口径对齐：02-user-org-auth、03-project-assets-env、04-api-testing 状态从“进行中”调整为“收尾中”，并明确仅执行阶段 2 收尾范围缺陷修复/治理优化。
### 2026-03-17
- 启动阶段 6：建立阶段 6 SSOT、门禁、DoD 与中断恢复机制（阶段文档现已归档）。
- 阶段状态切换：`阶段 6 未开始 -> 启动中（规划中）`，后续按 `S6-01~S6-08` 顺序推进。
- 完成 S6-01：新增企业集成配置中心最小闭环（`app/models/integration_config.py`、`migrations/versions/6a9d4c2e1b7f_phase6_integration_config_center.py`、`app/api/integrations.py`）。
- S6-01 测试门禁：新增 `tests/backend/test_integrations_api.py` 并通过（4 passed）；后端全量回归通过 `.\.venv\Scripts\python -m pytest`（115 passed，2 warnings）；前端构建通过 `npm run build`（frontend）。
- S6-01 迁移验证：本地历史库仍存在既有 revision 漂移风险（`audit_logs_archive already exists`）；在临时干净库验证迁移链路通过（`upgrade head -> downgrade 2c1b7f9a4d10 -> upgrade head`）。
- 完成 S6-02：新增事件收件箱与签名 Webhook 接入（`app/models/integration_event.py`、`migrations/versions/9c4e7a1d2f6b_phase6_integration_event_inbox.py`、`/api/integrations/webhooks/{config_id}/events/{event_type}`）。
- S6-02 测试门禁：新增 `tests/backend/test_integration_events_api.py` 并通过（4 passed）；S6-01+S6-02 相关回归通过（8 passed）；后端全量回归通过 `.\.venv\Scripts\python -m pytest`（119 passed，2 warnings）；前端构建通过 `npm run build`（frontend）。
- S6-02 迁移验证：本地历史库既有 revision 漂移风险未变；在临时干净库验证迁移链路通过（`upgrade head -> downgrade 6a9d4c2e1b7f -> upgrade head`）。
- 完成 S6-03：新增 CI/CD 最小闭环接口（`/api/integrations/{config_id}/cicd/trigger`、`/api/integrations/webhooks/{config_id}/cicd/callback`、`/api/integrations/{config_id}/cicd/runs`），实现触发与回调状态收敛。
- S6-03 测试门禁：新增 `tests/backend/test_integration_cicd_api.py` 并通过（4 passed）；S6 相关回归通过（12 passed）；后端全量回归通过 `.\.venv\Scripts\python -m pytest`（123 passed，2 warnings）；前端构建通过 `npm run build`（frontend）。
- 完成 S6-04：新增通知中心最小闭环（`app/models/notification_subscription.py`、`app/models/notification_delivery.py`、`migrations/versions/7d2b6f4c8a1e_phase6_notification_center_minimal.py`、`app/api/integrations.py` 通知订阅与投递接口）。
- S6-04 测试门禁：执行 `tests/backend/test_integration_notifications_api.py`（4 passed）与 `tests/backend/test_db_migration_workflow.py`（3 passed）；S6 相关回归通过（19 passed）。
- S6-04 迁移验证：新增通知迁移版本 `7d2b6f4c8a1e`，支持 `upgrade/downgrade` 回滚链路。
- 同步模块与架构文档：更新 `docs/modules/future/09-enterprise-integrations/SKILL.md` 与 `docs/architecture/企业级自动化测试平台系统架构规划.md`，对齐阶段 6 启动口径。
- 更新模块匹配规则：更新 `docs/modules/future/README.md`，将 `09-enterprise-integrations` 纳入当前默认可执行模块。
- 完成 S5-00：创建阶段 5 开发清单与验收清单，建立“看板 + 最近更新 + 风险阻塞”可中断恢复机制。
- 阶段 5 SSOT 已落盘（阶段文档现已归档）。
- 阶段切换：阶段 4 已完成并关闭，阶段 5 进入启动中（首批任务推进）。
- 启动 S5-01：新增 `docs/project/stage-5-reporting-input-contract.md`，冻结 API/Web 报告输入字段、映射规则与统计口径（v1）。
- 修复进度文档历史编码污染行，并统一阶段 5 口径为“启动中（S5-01 进行中）”，同步与架构总纲对齐。
- 推进 S5-01：新增 `app/services/reporting_input.py`，收敛 API/Web 输入映射、失败分类与统计口径实现；新增 `tests/backend/test_reporting_input_service.py` 并通过回归 `.\.venv\Scripts\python -m pytest tests/backend/test_reporting_input_service.py tests/backend/test_unified_results_api.py`（8 passed）。
- 完成 S5-01：输入口径与映射实现收口，阶段看板切换为 `S5-01 completed`。
- 启动 S5-02：新增报告聚合服务 `app/services/reporting_summary.py`、报告接口 `GET /api/reports/project/{project_id}/summary`、前端页面 `frontend/src/views/ReportSummary.vue` 与路由入口。
- S5-02 测试门禁：后端回归通过 `.\.venv\Scripts\python -m pytest tests/backend/test_reporting_summary_api.py tests/backend/test_reporting_input_service.py tests/backend/test_unified_results_api.py tests/backend/test_test_runs_api.py`（17 passed）。
- S5-02 测试门禁：前端构建通过 `npm run build`（frontend）。
- 完成 S5-02：报告中心最小闭环收口（摘要 + Top 失败项）。
- 启动 S5-03：新增趋势聚合接口 `GET /api/reports/project/{project_id}/trends` 与前端趋势最小展示（日/周维度）。
- S5-03 测试门禁：后端回归通过 `.\.venv\Scripts\python -m pytest tests/backend/test_reporting_input_service.py tests/backend/test_reporting_summary_api.py tests/backend/test_reporting_trends_api.py tests/backend/test_unified_results_api.py tests/backend/test_test_runs_api.py`（20 passed）。
- S5-03 测试门禁：前端构建通过 `npm run build`（frontend）。
- 完成 S5-03：趋势分析最小闭环收口（趋势查询 + 日/周图表展示）。
- 启动 S5-04：新增失败治理接口 `GET /api/reports/project/{project_id}/failures` 与失败治理视图（分类筛选 + 可追溯跳转）。
- S5-04 测试门禁：后端回归通过 `.\.venv\Scripts\python -m pytest tests/backend/test_reporting_failures_api.py tests/backend/test_reporting_summary_api.py tests/backend/test_reporting_trends_api.py tests/backend/test_reporting_input_service.py tests/backend/test_unified_results_api.py tests/backend/test_test_runs_api.py`（22 passed）。
- S5-04 测试门禁：前端构建通过 `npm run build`（frontend）。
- 完成 S5-05：报告域权限与审计对齐，摘要/趋势/失败治理接口统一写入审计事件（`report.summary.read`、`report.trends.read`、`report.failures.read`）。
- S5-05 测试门禁：后端回归通过 `.\.venv\Scripts\python -m pytest tests/backend/test_reporting_input_service.py tests/backend/test_reporting_summary_api.py tests/backend/test_reporting_trends_api.py tests/backend/test_reporting_failures_api.py tests/backend/test_reporting_audit_api.py tests/backend/test_unified_results_api.py tests/backend/test_test_runs_api.py`（23 passed）。
- 完成 S5-06：建立报告性能与稳定性门禁，新增时间窗口护栏（180 天）与性能基线测试 `tests/backend/test_reporting_performance_guards.py`。
- S5-06 测试门禁：后端回归通过 `.\.venv\Scripts\python -m pytest tests/backend/test_reporting_input_service.py tests/backend/test_reporting_summary_api.py tests/backend/test_reporting_trends_api.py tests/backend/test_reporting_failures_api.py tests/backend/test_reporting_audit_api.py tests/backend/test_reporting_performance_guards.py tests/backend/test_unified_results_api.py tests/backend/test_test_runs_api.py`（25 passed）。
- 完成 S5-07：执行阶段 5 核心验收门禁并收口验收记录，阶段 5 状态切换为“已完成验收”。
- S5-07 测试门禁：后端全量回归通过 `.\.venv\Scripts\python -m pytest`（111 passed，2 warnings）；前端构建通过 `npm run build`（frontend）。
- 同步阶段文档：完成 S5-07 记录与结论落盘（阶段文档现已归档）。
- 同步模块与架构文档：更新 `docs/modules/future/08-reporting-analytics/SKILL.md` 与 `docs/architecture/企业级自动化测试平台系统架构规划.md`，保持阶段口径一致。
### 2026-03-16
- 阶段状态切换：`阶段 2 进行中 -> 收尾中`，`阶段 3 未开始 -> 启动中`
- 同步更新阶段门禁与模块匹配：`docs/modules/future/README.md`、`docs/modules/future/05-web-testing/SKILL.md`
- 同步检查并更新架构总纲阶段状态：`docs/architecture/企业级自动化测试平台系统架构规划.md`
- 新增阶段 3 开发清单文档（阶段 3 进度追踪 SSOT，现已归档）
- 对齐文档进度口径：更新 `docs/project/project-overview.md`、`docs/architecture/system-architecture.md`、`docs/architecture/dependency-graph.md`，消除与阶段 2 实际能力的冲突表述
- 阶段 3 启动：完成 S3-00（开发准备），明确阶段 3 最小闭环路径、后端目录/命名规划、接口边界与产物归档约定。
- 阶段 3 推进：完成 S3-01（Web 领域模型与用例管理），落地 `web_test_cases/web_steps/web_locators` 模型与迁移，并提供最小 CRUD API；新增后端测试 `tests/backend/test_web_test_cases_api.py`；回归通过 `.\.venv\Scripts\python -m pytest`
- 阶段 3 推进：完成 S3-02（Playwright 执行引擎最小闭环），落地 `web_test_runs` 模型与迁移、Web 单用例执行接口与执行结果查询接口，产物归档路径为 `artifacts/web-test-runs/{run_id}/`；新增后端测试 `tests/backend/test_web_test_runs_api.py`；回归通过 `.\.venv\Scripts\python -m pytest`
- 阶段 3 推进：完成 S3-03（前端最小页面闭环），新增 `frontend/src/views/WebTestCaseList.vue` 与 `frontend/src/views/WebTestRunDetail.vue`，补齐 Web 路由与 API 用例页入口按钮
- 阶段 3 验证执行：完成前端构建验证 `npm run build`（frontend，通过）
- 阶段 3 推进：完成 S3-04（统一归档与展示对齐），新增统一结果查询接口 `GET /api/test-runs/project/{project_id}/unified-results` 与前端聚合页 `frontend/src/views/UnifiedRunList.vue`
- 阶段 3 增强：统一结果接口新增分页与筛选（`run_type/status/created_from/created_to/page/page_size`），统一结果页新增筛选栏、分页与失败记录快速定位
- 阶段 3 测试门禁：新增 `tests/backend/test_unified_results_api.py`，并通过回归 `.\.venv\Scripts\python -m pytest tests/backend/test_unified_results_api.py tests/backend/test_test_runs_api.py tests/backend/test_web_test_runs_api.py`（12 passed）
- 阶段 3 测试门禁：完成前端构建验证 `npm run build`（frontend，通过）
- 阶段状态切换：`阶段 3 启动中 -> 收尾中`，`阶段 4 未开始 -> 启动中`
- 新增阶段 4 开发清单文档（阶段 4 进度追踪 SSOT，现已归档）
- 同步更新阶段匹配与模块技能文档：`docs/modules/future/README.md`、`docs/modules/future/06-execution-orchestration/SKILL.md`、`docs/modules/future/07-scheduling-queue-worker/SKILL.md`
- 同步更新架构总纲与项目概览阶段口径，消除阶段状态冲突
- 阶段 4 推进：完成 S4-01（统一执行编排骨架），新增 `execution_tasks/execution_jobs` 模型与迁移，落地统一编排服务并接入 API/Web 单用例执行入口
- 阶段 4 测试门禁：新增 `tests/backend/test_execution_orchestration_skeleton.py`，并通过回归 `.\.venv\Scripts\python -m pytest tests/backend/test_execution_orchestration_skeleton.py tests/backend/test_test_runs_api.py tests/backend/test_web_test_runs_api.py tests/backend/test_unified_results_api.py`（14 passed）
- 阶段 4 推进：完成 S4-02（调度器最小可用），新增 `schedule_tasks` 最小 API 与 `trigger -> run_queue` 入队链路
- 阶段 4 测试门禁：新增 `tests/backend/test_schedule_tasks_api.py`，并通过回归 `.\.venv\Scripts\python -m pytest tests/backend/test_schedule_tasks_api.py tests/backend/test_execution_orchestration_skeleton.py tests/backend/test_test_runs_api.py tests/backend/test_web_test_runs_api.py`（14 passed）
- 阶段 4 推进：完成 S4-03（队列与 Worker 最小闭环），新增 `run_queue` 领取/回写接口、Worker 占位执行接口与心跳接口（`/api/run-queue/*`）
- 阶段 4 数据模型：新增 `worker_heartbeats` 与迁移 `2c1b7f9a4d10_phase4_worker_heartbeat_minimal_loop`
- 阶段 4 测试门禁：新增 `tests/backend/test_queue_worker_api.py`，并通过最小回归 `.\.venv\Scripts\python -m pytest tests/backend/test_queue_worker_api.py tests/backend/test_schedule_tasks_api.py`（6 passed）
- 阶段 4 推进：完成 S4-04（执行管理最小可视化），新增 `SchedulingDashboard` 页面与项目内导航入口
- 阶段 4 API 补齐：新增队列只读查询接口 `GET /api/run-queue/project/{project_id}`、`GET /api/run-queue/{queue_item_id}`、`GET /api/run-queue/worker/heartbeats/project/{project_id}`
- 阶段 4 测试门禁：后端最小回归继续通过（6 passed）；前端构建验证通过 `npm run build`（frontend）
- 阶段 2 验收执行：完成全量后端回归 `.\.venv\Scripts\python -m pytest`（78 passed）
- 阶段 2 验收执行：完成前端构建验证 `npm run build`（frontend，通过）
- 阶段 2 验收执行：完成迁移流程相关测试 `.\.venv\Scripts\python -m pytest tests/backend/test_db_migration_workflow.py`（3 passed）
- 新增阶段 2 验收清单文档（现已归档）
- 完成阶段 2 S2-06：变量治理增强闭环（变量组复用、密钥受控读取、前端治理页联动、执行详情变量快照）
- 新增迁移：`c3e8a6b1d2f4_phase2_variable_governance_enhancement`（`project_variables.group_name`、`environment_variable_group_bindings`、`test_runs.runtime_variables/variable_sources`）
- 后端接口增强：新增变量组绑定/解绑与查询、密钥明文读取接口（管理权限 + 审计）、项目变量 `group_name` 管理能力
- 执行链路增强：运行时变量解析支持“项目变量 + 变量组 + 环境变量”优先级覆盖，执行详情新增变量快照与来源展示（secret 默认脱敏）
- 前端能力增强：新增环境变量治理页 `EnvironmentManager.vue`，并在用例页/执行详情页打通导航联动
- 新增测试：`test_variable_groups_and_secret_reveal_api`、`test_non_owner_cannot_reveal_foreign_secret`、`test_run_suite_uses_bound_variable_group`、`test_run_detail_contains_runtime_variable_snapshot`
- 验证通过：`.\.venv\Scripts\python -m pytest tests/backend/test_environments_api.py tests/backend/test_suite_batch_runs_api.py tests/backend/test_test_runs_api.py tests/backend/test_test_executor_enhancements.py`（19 passed）
- 前端构建验证通过：`npm run build`（frontend）
- 完成组织级权限治理深化收口（阶段 1 风险托管项）：组织成员模型新增 `department/workspace` 维度（迁移 `b8f56e6e43f1_organization_member_scope_policy`）
- 组织治理接口增强：`/api/organizations/{id}/members` 支持维度维护与维度筛选（`department/workspace`），跨项目治理接口新增组织策略边界（同部门/同工作区）
- 新增组织治理策略测试：覆盖维度写入、维度筛选、跨维度越权拦截；验证通过 `tests/backend/test_organization_governance.py`（6 passed）
- 新增迁移链路验证：`alembic upgrade head -> downgrade a7c3d9e1f2b4 -> upgrade head`（通过）
- 完成生产迁移窗口演练复核（本地 PostgreSQL 演练库）：执行 `迁移 -> 回滚 -> 再迁移` 全流程，产出 `artifacts/prod-db-window-drill/window_drill_20260316_111751.{json,md}`
- 完成审计治理生产联调验证演练（本地生产参数）：执行 `scripts/prod-audit-governance-run.ps1`，验证治理任务执行成功与清单产物落地
- 完成告警联动闭环验证：通过阈值触发告警并回调 webhook（HTTP 200），联调产物写入 `artifacts/audit-governance/`
- 完成定时任务注册命令校验（DryRun）：`scripts/setup-audit-governance-schedule.ps1` 可正确生成 `schtasks /Create` 命令
- 说明：以上为“演练/联调验证”完成，阶段 1 仍保持“暂停态风险托管”；真实生产环境任务注册与窗口执行闭环仍待落地

- S4-05 kickoff: added stage-4 acceptance rubric with A4-01~A4-05（现已归档）。
- Defined R1~R5 strategy for real worker consumption (loop, idempotent claim, retry/dead-letter, stale recovery, orchestration convergence).

### 2026-03-13
- 完成阶段 2 S2-04：落地用例分组/标签/筛选/搜索（新增 `case_group/tags` 字段、查询参数 `keyword/case_group/tag`、前端筛选交互）
- 新增迁移：`a7c3d9e1f2b4_phase2_test_case_group_tags`（`api_test_cases.case_group/tags`）
- 新增测试：`test_test_case_group_tags_and_filters`、`test_update_test_case_group_and_tags`
- 验证通过：`.\.venv\Scripts\python -m pytest tests/backend/test_test_cases_api.py tests/backend/test_suite_batch_runs_api.py tests/backend/test_test_runs_api.py tests/backend/test_test_executor_enhancements.py`（18 passed）
- 前端构建验证通过：`npm run build`（frontend）
- 完成阶段 2 S2-02：执行引擎新增 Schema 断言能力（规则校验 + 递归校验，覆盖 type/required/properties/items/enum/const/边界约束）
- 完成阶段 2 S2-03：落地失败重试与幂等保护（`retry_count/retry_on/idempotency_key`），并保证重试场景仅持久化最终执行结果
- 新增测试：`test_run_suite_retries_error_then_success`、`test_run_suite_with_same_idempotency_key_reuses_batch`
- 验证通过：`.\.venv\Scripts\python -m pytest tests/backend/test_suite_batch_runs_api.py tests/backend/test_test_runs_api.py tests/backend/test_test_executor_enhancements.py`（13 passed）
- 新增测试：`test_execute_test_supports_schema_assertion_success`、`test_execute_test_schema_assertion_failed_when_payload_mismatch`、`test_execute_test_schema_assertion_rejects_invalid_schema_rule`
- 验证通过：`.\.venv\Scripts\python -m pytest tests/backend/test_test_executor_enhancements.py`（5 passed）
- 回归通过：`.\.venv\Scripts\python -m pytest tests/backend/test_suite_batch_runs_api.py tests/backend/test_test_runs_api.py`（6 passed）
- 完成阶段 2 S2-01：新增执行详情与批次结果可视化链路（后端 `GET /api/test-runs/{run_id}`、批次详情增强字段；前端新增批次列表页/批次详情页/执行详情页）
- 新增测试覆盖：`test_get_test_run_detail_returns_case_metadata`、`test_non_owner_cannot_view_foreign_test_run_detail`，并增强 `test_suite_batch_runs_api.py` 的批次详情字段断言
- 验证通过：`.\.venv\Scripts\python -m pytest tests/backend/test_test_runs_api.py tests/backend/test_suite_batch_runs_api.py`（6 passed）
- 前端构建验证通过：`npm run build`（frontend）
- 新增阶段 2 执行清单文档（含已完成/进行中/待完成、优先级、验收标准、测试门禁与单人开发顺序，现已归档）
- 基于当前代码基线补齐文档：核对 `app/`、`frontend/src/` 与 `tests/backend` 现状，修正文档中阶段 2 能力评估不一致项
- 同步补全后端路由现状描述：`auth`、`organizations`、`projects`、`test_cases`、`test_suites`、`environments`、`test_runs`、`audit_logs`
- 同步更新 `docs/architecture/企业级自动化测试平台系统架构规划.md`：修正“环境变量/套件批量未开始”等过期表述，统一为与当前代码一致的阶段 2 状态与优先级
- 同步补齐阶段 2 对应模块技能文档：更新 docs/modules/future/03-project-assets-env/SKILL.md 与 docs/modules/future/04-api-testing/SKILL.md 的待完成项、关键任务、测试要求与 DoD

### 2026-03-13
- 阶段 2 首批后端能力落地：新增 API 套件模块（`/api/test-suites/*`）
- 阶段 2 首批后端能力落地：新增环境与变量模块（`/api/environments/*`，含敏感变量脱敏展示）
- 阶段 2 首批后端能力落地：新增套件批量执行与批次查询（`/api/test-runs/suites/{suite_id}/run`、`/api/test-runs/batches/*`）
- 执行引擎增强：支持运行时变量替换、`contains/regex/jsonpath` 断言、响应提取与链路传递
- 新增迁移 `e2b4c6a8d901_phase2_api_platform_core`（suite/batch/environment 及用例增强字段）
- 新增测试：`test_test_suites_api.py`、`test_environments_api.py`、`test_suite_batch_runs_api.py`、`test_test_executor_enhancements.py`
- 回归验证通过：`.\.venv\Scripts\python -m pytest`（62 passed）

### 2026-03-13
- 根据项目决策，阶段状态切换为“阶段 1 暂停、阶段 2 进行中”
- 更新“当前总体进度”与“当前阶段状态表”，同步标注阶段 2 启动状态
- 重排当前优先事项为阶段 2 开发顺序（P0 API 套件/批量/环境变量）
- 同步更新 `docs/modules/future/README.md` 阶段匹配规则与默认可执行模块
- 同步更新 `docs/modules/future/*/SKILL.md`（阶段 1/2 状态与阶段匹配门禁）
- 同步检查并更新 `docs/architecture/企业级自动化测试平台系统架构规划.md` 阶段状态与实施优先级

### 2026-03-12
- 修复本地登录跨域失败：后端 CORS 改为明确白名单（`localhost/127.0.0.1` 常用前端端口），避免 `allow_credentials=true` 与 `*` 组合导致浏览器拦截
- 修复本地旧库导致登录 500：启动阶段新增本地/测试环境自动迁移（`auto_migrate_db()`），并对历史 SQLite 脏库增加列级修复兜底（`users.role`、`projects.organization_id`）
- 修复登录页展示异常：重写 `frontend/src/views/Login.vue` 文案与样式兜底，解决乱码与变量缺省导致的样式错乱
- 新增 CORS 回归测试 `test_error_response_format.py`，并验证前端构建通过
- 完成组织层权限治理与跨项目成员治理（阶段 1）：新增组织模型 `organizations`、`organization_members` 与迁移 `d1f8902c4b61_organization_layer_governance`
- 新增组织治理接口：`/api/organizations/`、`/api/organizations/{id}/members`、`/api/organizations/{id}/projects/attach`、`/api/organizations/{id}/members/governance/cross-project`
- 访问控制升级：`app/services/access_control.py` 增加组织层判定，项目/用例/执行鉴权接入组织管理员能力
- 新增组织治理测试 `tests/backend/test_organization_governance.py`，回归通过：`.\.venv\Scripts\python -m pytest`（52 passed）
- 迁移链路验证通过（临时库）：`alembic upgrade head -> downgrade 9b1f0b38d7d2 -> upgrade head`
- 完成审计治理“真实定时任务 + 告警联动”落地：新增 `setup-audit-governance-schedule.ps1`、`remove-audit-governance-schedule.ps1` 与 `alert_webhook_notify.py`
- 增强 `prod-audit-governance-run.ps1`：支持 `-AlertWebhookUrl`，任务失败或阈值告警时自动推送 webhook
- 新增告警构造测试 `tests/backend/test_alert_webhook_notify.py`，并通过回归：`.\.venv\Scripts\python -m pytest`（46 passed）
- 完成生产窗口流程本地实操演练与留档：新增 `scripts/prod-db-window-drill.ps1`，执行 `迁移 -> 回滚 -> 再迁移` 全链路并产出报告
- 演练留档产物：`artifacts/prod-db-window-drill/window_drill_20260312_150938.json` 与同名 `.md`
- 补齐配置与测试验证缺口：`scripts/audit-governance-run.py` 默认编排参数接入 `app/config.py`（`AUDIT_GOVERNANCE_*`）
- 新增日志字段完整性测试 `tests/backend/test_logging_config.py`，补充配置默认值测试 `test_database_config.py`
- 回归验证通过：`.\.venv\Scripts\python -m pytest`（46 passed）
- 完成审计治理生产化编排（阶段 1）：增强 `scripts/audit-governance-run.py`，支持锁文件防重入、执行清单留痕、阈值告警与告警退出码
- 新增生产执行脚本 `scripts/prod-audit-governance-run.ps1`（强制确认 + 显式 `DATABASE_URL`）
- 新增编排单测 `tests/backend/test_audit_governance_orchestrator.py`，并通过全量回归：`.\.venv\Scripts\python -m pytest`（43 passed）
- 完成权限治理深化（阶段 1 第二批）：新增项目成员模型 `project_members`（迁移 `9b1f0b38d7d2_project_member_model`）与成员管理接口
- 项目/用例/执行接入成员角色鉴权：`owner/maintainer/editor/viewer`，并通过 `app/services/access_control.py` 统一判定
- 新增成员权限测试 `tests/backend/test_project_members_api.py`，并更新相关鉴权测试，回归通过：`.\.venv\Scripts\python -m pytest`（41 passed）
- 迁移链路验证通过（临时库）：`alembic upgrade head -> downgrade fcf57b5ad65c -> upgrade head`
- 完成权限治理深化（阶段 1）：新增 `app/permissions.py` 角色-权限矩阵，鉴权依赖新增 `require_permissions(...)`
- 补齐越权校验：项目/用例/执行/审计查询等关键接口统一返回 `403 FORBIDDEN`，并补充 admin 跨资源治理权限
- 新增并更新权限治理测试：`test_projects_api.py`、`test_test_cases_api.py`、`test_test_runs_api.py`、`test_audit_governance.py`
- 回归验证通过：`.\.venv\Scripts\python -m pytest`（36 passed）
- 新增根目录开发入口：补充 `package.json` 与 `scripts/dev-runner.mjs`，支持在仓库根目录执行 `npm run dev` 同时启动后端与前端
- 同步修正文档 `docs/tech/tech-stack.md`，明确根目录 `npm run dev` 与 `frontend` 独立启动方式
- 固化生产迁移流程闭环：新增 `scripts/db_revision_check.py`、`scripts/prod-db-rollback.ps1`，迁移脚本 `scripts/prod-db-migrate.ps1` 增加迁移清单留痕（前后版本、备份文件、回滚命令、状态）
- 补充生产迁移 runbook：更新 `docs/tech/db-migration.md`，明确窗口前检查、执行步骤、回滚决策与留档项
- 新增迁移流程测试 `tests/backend/test_db_migration_workflow.py`，验证版本探测脚本基础行为
- 完成最小 RBAC/权限校验闭环：新增 `users.role`（`admin/user`）与权限依赖 `require_roles(...)`
- 新增治理权限接口：`POST /api/audit-logs/governance/run`（admin）
- 增强审计查询权限：admin 可全局查询，普通用户仅可查询本人日志
- 新增迁移 `fcf57b5ad65c_minimal_rbac_role`（用户角色字段与约束）
- 新增 RBAC 测试场景并通过，全量回归：`.\.venv\Scripts\python -m pytest`（28 passed）
- 迁移链路验证通过：`alembic upgrade head -> downgrade 802c16c9f78e -> upgrade head`

### 2026-03-11
- 完成日志/审计治理闭环（查询、归档、保留策略）：新增 `/api/audit-logs` 查询接口、`audit_logs_archive` 归档表、`scripts/audit-governance-run.py` 策略执行脚本
- 新增迁移 `802c16c9f78e_audit_log_governance`，新增审计治理相关模型与索引
- 新增治理测试 `test_audit_governance.py`，全量回归通过：`.\.venv\Scripts\python -m pytest`（25 passed）
- 迁移链路验证通过：`alembic upgrade head -> downgrade 01fcc228897e -> upgrade head`
- 完成 PostgreSQL 生产环境迁移能力建设（不含压测）：新增 `scripts/prod-db-migrate.ps1`，支持强制确认、目标版本迁移、可选备份、可选迁移后自检
- 补充生产迁移文档：`docs/tech/db-migration.md`，新增生产迁移执行示例与 dry-run 演练命令
- 完成阶段 1 领域模型治理细则：落地约束、索引、级联、生命周期（含新迁移 `01fcc228897e_domain_model_governance`）
- 同步增强接口防护：项目/用例重名校验、用例 `method` 规范化、请求参数约束收敛
- 新增测试 `test_model_governance.py`、`test_test_cases_api.py` 与项目重名校验用例，回归通过：`.\.venv\Scripts\python -m pytest`（22 passed）
- 迁移链路验证通过：`alembic upgrade head -> downgrade 8daac485a5f7 -> upgrade head`
- 更新 `docs/modules/future/README.md`：新增“强制执行规则”和“当前阶段匹配”说明，明确当前阶段默认可执行模块与越阶段门禁
- 同步更新 `docs/modules/future/*/SKILL.md`（9 个模块）：统一加入 AGENTS 强制约束、测试门禁、进度文档同步规则与阶段匹配执行策略
- 完成“代码层统一”：路由 DTO 全量切换到 `app/schemas/`，并补齐核心模型关系映射（`relationship + back_populates`）
- 执行全量回归测试：`.\.venv\Scripts\python -m pytest`（15 passed，2 warnings），确认无回归
- 同步修正文档：`system-architecture`、`repo-structure`、`domain-model`、`project-progress`
- 精简文档入口：删除冗余文档 `docs/SUMMARY.md` 与 `docs/文档清单.txt`，其余低优先级文档保留
- 重构 `docs/README.md` 为 AI 快速熟悉导航，按“项目目标→项目进度→系统架构→模块定位→依赖关系”给出必读顺序
- 增强 `docs/modules/modules.md`，新增“高频改动定位（速查）”以支持按需求快速定位代码文件
- 修正 `docs/domain/domain-model.md` 中密码字段描述，更新为“哈希存储并兼容历史明文自动迁移”
- 阅读并整理了 `docs/` 现有文档
- 新增企业级平台总纲：`docs/architecture/企业级自动化测试平台系统架构规划.md`
- 建立本项目进度文档，用于后续持续维护项目状态
- 新增并中文化仓库级约束文档 `AGENTS.md`，明确代码规范与测试门禁：逻辑/功能改动必须执行测试并通过后方可交付
- 新增后续开发模块目录 `docs/modules/future/`，并为每个后续模块创建独立 `SKILL.md` 执行指南
- 启动阶段 1 开发：新增 `pytest` 测试基线（健康检查、认证、项目管理、测试执行接口），本地执行通过（7 passed）
- 完成阶段 1 认证升级：后端切换为 JWT + Refresh Token + Bearer 鉴权，密码改为哈希存储并兼容历史明文用户自动迁移
- 前端联动认证升级：请求头改为 Authorization Bearer，401 时自动刷新 access token，刷新失败自动清理登录态
- 补充认证测试并通过：`.\.venv\Scripts\python -m pytest`（8 passed）
- 完成阶段 1 工程化项：建立统一异常/错误码体系，新增全局异常处理与请求 `request_id` 透传
- 补充异常体系测试并通过：`.\.venv\Scripts\python -m pytest`（10 passed）
- 完成阶段 1 工程化项：新增结构化日志配置与请求日志中间件，日志统一 JSON 输出
- 完成阶段 1 工程化项：新增审计日志模型与服务，覆盖认证、项目、用例、执行触发等关键写操作
- 新增日志与审计规范文档：`docs/tech/logging-audit-spec.md`
- 补充审计测试并通过：`.\.venv\Scripts\python -m pytest`（11 passed）
- 完成阶段 1 数据库迁移基线：接入 Alembic、生成 `initial_schema` 首版迁移并完成升级/降级验证
- 新增迁移规范文档：`docs/tech/db-migration.md`
- 完成阶段 1 PostgreSQL 落地：支持 `APP_ENV + USE_POSTGRES` 配置切换，新增本地编排文件 `docker-compose.postgres.yml`
- 新增 PostgreSQL 环境样例：`.env.postgres.example`，并新增测试配置用例
- 回归测试通过：`.\.venv\Scripts\python -m pytest`（15 passed）
- 新增一键脚本：`scripts/dev-postgres-up.ps1` 与 `scripts/db_connectivity_check.py`
- 端到端验证通过：`local` 与 `test` 两种目标环境均可自动迁移并完成自检
- 新增一键脚本：`scripts/dev-postgres-down.ps1`（停服务+可选清理卷）
- 新增一键脚本：`scripts/dev-api-up.ps1`（数据库就绪后自动启动 `uvicorn`）
- 脚本端到端验证通过：`dev-postgres-down` 与 `dev-api-up -PrepareOnly`
- 新增一键脚本：`scripts/dev-api-down.ps1`（按端口停止 API）
- 脚本端到端验证通过：启动临时 `uvicorn` 后，`dev-api-down` 可成功结束进程

## 11. 更新规则

后续任何 AI 或开发者在以下情况下都必须更新本文档：

- 新增模块
- 删除模块
- 调整架构分层
- 新增或完成某阶段的重要能力
- 某模块从“未开始”变为“进行中”或“已完成”
- 对项目目标、路线图、阶段判断产生影响的改动

最少应同步更新以下内容：
- `第 3 节：当前总体进度`
- `第 4 节：当前阶段状态表`
- `第 5~7 节：已完成 / 部分完成 / 未开始`
- `第 10 节：最近更新记录`

如果本次改动影响平台路线图，还应同步检查：
- `docs/architecture/企业级自动化测试平台系统架构规划.md`

## 12. 维护原则

- 文档内容必须以当前实际代码为准，不得只写计划不写现状
- 进度判断应保守，不夸大完成度
- 如果某项能力只有模型或页面占位，不应标记为完成
- 进度更新应写明日期和具体变化
- 若文档与代码冲突，以代码事实为准，并尽快修正文档

- S4-05 验收收口：后端全量回归通过、前端构建通过；迁移 revision 漂移风险转入阶段 5 受控技术债，不阻断阶段切换。

- 2026-03-17：阶段 4（S4-01~S4-05）完成验收并切换为“已完成验收”；阶段 5 当日由“启动中”推进至“已完成验收”，并同步对齐阶段 4/阶段 5 相关 SSOT 文档与模块 SKILL。

