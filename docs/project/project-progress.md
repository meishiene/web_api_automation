# 项目进度文档

## 1. 文档目的

本文档用于记录当前项目的实际开发进度，帮助后续参与开发的 AI 或开发者快速掌握：

- 当前项目做到什么程度
- 哪些模块已经完成、部分完成、未开始
- 最近新增或修改了什么
- 接下来最优先要做什么

本文件是项目级进度基线，后续凡是对代码进行新增、修改、删除，且影响功能、结构、模块状态或开发阶段判断时，都应同步更新本文档。

## 2. 当前项目阶段

- **当前总阶段**：阶段 0 已完成，阶段 1 暂停，阶段 2 收尾中，阶段 3 收尾中，阶段 4 已完成验收，阶段 5 已完成验收，阶段 6 已完成验收（S6-08 已完成），阶段 7 启动中（S7-01 已完成）。
- **项目定位**：MVP 级 API 自动化测试工具，正准备向企业级自动化测试平台演进
- **平台目标**：统一承载 `API 测试 + Web 测试 + 调度执行 + 报告治理 + 企业集成`

## 3. 当前总体进度

| 领域 | 当前状态 | 进度 |
| --- | --- | --- |
| 用户与认证 | 已完成 JWT + Refresh Token、最小 RBAC（admin/user）、角色-权限矩阵、项目成员与组织层权限基础能力 | 80% |
| 项目管理 | 已支持基础 CRUD、项目成员管理与组织归属治理 | 60% |
| API 用例管理 | 已支持基础 CRUD、套件关联与增强断言配置（阶段 2 首批已落地） | 65% |
| API 执行能力 | 已支持单条执行与套件批量执行（含批次追踪、变量链路传递、运行时变量快照） | 60% |
| 工程化与测试基线 | 已建立测试基线、统一异常错误码、结构化日志、审计治理闭环、Alembic/PG 本地测试落地与模型治理细则 | 90% |
| Web 测试能力 | 阶段 3 收尾中（领域模型、用例管理、单用例执行、前端最小闭环与 API/Web 统一结果展示已落地） | 45% |
| 环境与变量管理 | 已落地变量治理增强闭环（变量组复用、密钥受控读取、前端治理页联动） | 55% |
| 套件与批量执行 | 已落地 API 套件与批量执行首批闭环 | 45% |
| 调度与队列 | 阶段 4 已完成验收：调度/队列/Worker 最小闭环与可视化已稳定落地；阶段 5 聚焦真实消费治理与报告联动增强。 | 45% |
| 报告与分析 | 已落地统一输入映射、摘要/趋势/失败治理接口、治理页、审计事件与性能护栏，并完成阶段 5 验收收口（S5-07） | 60% |
| 权限与治理 | 已完成最小 RBAC 闭环并推进细粒度治理（权限矩阵、越权校验、项目成员协作、组织层与跨项目治理基础） | 55% |
| 企业集成 | 阶段 6 已完成 S6-01~S6-08（配置中心 + 事件回调 + CI + 通知 + 缺陷联动 + OAuth2 + 治理增强 + 验收收口） | 80% |

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
| 阶段 7 | 运营化与平台扩展 | 启动中 | 已完成 S7-00~S7-01（OpenAPI 导入最小闭环），进入 S7-02 准备。 |

## 5. 当前已完成内容

### 5.1 后端
- 已建立 `FastAPI` 应用入口
- 已接入 `auth`、`organizations`、`projects`、`test_cases`、`test_suites`、`environments`、`schedule_tasks`、`test_runs`、`web_test_cases`、`web_test_runs`、`audit_logs` 路由
- 已支持用户注册和登录
- 已支持项目 CRUD
- 已支持 API 测试用例 CRUD
- 已支持单条 API 测试执行
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
- 已新增企业集成配置中心最小闭环：`integration_configs` 模型与迁移、`/api/integrations/*` 配置 CRUD、凭据脱敏展示与审计留痕
- 已新增企业集成事件收件箱：`integration_events` 模型与迁移、签名 Webhook 入站、幂等去重、事件重放与事件查询接口
- 已新增 CI/CD 最小闭环：`/api/integrations/{config_id}/cicd/trigger`、`/api/integrations/webhooks/{config_id}/cicd/callback`、`/api/integrations/{config_id}/cicd/runs`
- 已新增通知中心最小闭环：`notification_subscriptions`/`notification_deliveries` 模型与迁移、通知订阅管理、投递日志查询、失败重试与死信收敛
- 已新增缺陷联动最小闭环：`defect_sync_records` 模型与迁移、`/api/integrations/{config_id}/defects/sync`、`/api/integrations/project/{project_id}/defects/records`、失败指纹去重与建单/更新路径审计留痕
- 已新增 OAuth2 身份集成最小闭环：`identity_oauth_sessions`/`identity_provider_bindings` 模型与迁移、`/api/integrations/{config_id}/identity/oauth2/start`、`/api/integrations/{config_id}/identity/oauth2/callback`、`/api/integrations/{config_id}/identity/bindings`、state 会话校验与账号绑定策略（新建/关联/复用）

### 5.2 前端
- 已建立登录页、注册页、项目列表页、测试用例页
- 已建立统一请求封装
- 已建立基础路由守卫
- 已打通项目管理与 API 用例管理主链路
- 已支持在测试用例页面触发执行并查看最近结果
- 已支持批次结果页与执行详情页联动（批次列表 -> 批次详情 -> 执行详情）
- 已新增环境变量治理页并与执行详情联动（变量治理页 -> 执行详情变量快照）
- 已新增 Web 用例管理页与 Web 执行详情页，并打通路由入口（API 用例页 -> Web 用例页 -> Web 执行详情）
- 已新增统一执行结果页（Execution Center），聚合 API/Web 执行记录并支持统一字段展示与详情跳转
- 已增强统一执行结果能力：支持 `run_type/status/time range` 筛选、分页与快速定位失败记录
- 已新增最小报告页（Report Center）：`frontend/src/views/ReportSummary.vue`（执行摘要 + Top 失败项）
- 已新增趋势最小可视化：Report Center 支持日/周趋势查询与条形图展示
- 已新增失败治理最小可视化：Report Center 支持失败分类筛选与失败记录详情追溯

### 5.3 文档
- 已补充项目概览文档
- 已补充系统架构文档
- 已补充模块清单、领域模型、技术栈、仓库结构文档
- 已新增企业级平台总纲文档
- 已新增阶段 4 开发清单文档（`docs/project/stage-4-development-checklist.md`）
- 已新增阶段 6 开发清单与验收清单文档（`docs/project/stage-6-development-checklist.md`、`docs/project/stage-6-acceptance-checklist.md`）

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
- 已支持 API 套件执行与批量回归（按套件顺序执行）
- 已支持批次级状态汇总与明细追踪（`success/failed/error`）
- 已支持 Web 单用例自动化执行（含步骤日志与产物路径查询）

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

## 当前阶段优先事项（阶段 2 收尾 / 阶段 3 收尾 / 阶段 5 已完成验收 / 阶段 6 已完成验收 / 阶段 7 启动中）

### P0：API 平台化首批落地（已完成）
- 已完成 API 套件模型与基础 CRUD
- 已完成批量执行最小闭环（套件触发、批次记录、结果聚合）
- 已完成环境与变量最小能力（项目级/环境级 + 执行替换）

### P1：执行与断言增强（进行中）
- 已落地断言能力（JSONPath / 正则 / 包含 / Schema）
- 已落地响应数据提取与链路变量传递
- 已落地 API 用例分组/标签/筛选/搜索（后端查询参数 + 前端筛选入口）
- 已落地变量治理增强（S2-06）：变量组复用、密钥受控读取、前端治理页、执行详情变量快照
- 执行详情页与批次结果页面已落地，后续需持续增强展示维度

### P2：阶段 1 遗留风险托管（暂停态）
- PostgreSQL 真实生产环境迁移发布演练与窗口执行（按当前决策不做压测）
- 审计治理生产定时任务与告警平台联动生产验证（脚本已落地）

### P3：阶段 3 收尾项（进行中）
- Web 领域模型首批设计与落地（`WebTestCase`、`WebStep`、`Locator`）（已完成）
- Playwright 执行引擎最小闭环接入（单用例执行）（已完成）
- Web 执行结果基础展示页与产物链路预留（已完成：Web 用例管理页 + Web 执行详情页 + 路由入口）
- API/Web 统一归档展示对齐（S3-04，已完成：统一结果接口 + Execution Center）

### P4：阶段 4 验收完成（已收口）
- 已完成阶段 4 SSOT 建立：`docs/project/stage-4-development-checklist.md`
- 已完成 S4-01：统一执行编排骨架（Execution Task/Job + API/Web 适配层）
- 已完成 S4-02：调度器最小可用（schedule_tasks 触发链路）
- 已完成 S4-03：队列与 Worker 最小闭环（run_queue + Worker 心跳/消费占位）
- 已完成 S4-04：执行管理最小可视化（前端）
- 已完成 S4-05：阶段验收与切换准备（验收结论已通过）。

### P5：阶段 6 企业集成（已完成验收）
- 已完成 S6-00：阶段 6 开发清单与验收清单落盘，建立可中断恢复机制。
- 已完成 S6-01：集成配置中心最小闭环（模型 + 迁移 + API + 鉴权 + 审计）并通过门禁。
- 已完成 S6-02：事件与签名回调最小闭环（签名校验 + 幂等去重 + 事件重放 + 查询）并通过门禁。
- 已完成 S6-03：CI/CD 最小闭环（触发 -> 回调 -> 状态收敛）并通过门禁。
- 已完成 S6-05：缺陷联动最小闭环（Jira 适配切片、失败指纹去重、建单/更新路径、记录查询与审计）。
- 已完成 S6-06：OAuth2 身份集成最小闭环（授权启动、回调校验、账号绑定与令牌签发）。
- 已完成 S6-07：治理增强最小闭环（健康看板汇总、失败/死信治理重试、集成域审计补齐、前端治理入口挂载）。
- 已完成 S6-08：阶段验收收口与切换准备（受控通过）。
- 下一步：按阶段 7 清单推进 S7-02（Provider Registry 最小骨架）。

## 10. 最近更新记录
### 2026-03-17
- 完成 S7-01：OpenAPI 导入最小闭环已落地（`app/schemas/api_test_case.py`、`app/api/test_cases.py`），支持 OpenAPI 3.x 规范最小映射与重复去重。
- 测试门禁：`python -m pytest tests/backend/test_test_cases_api.py -k openapi -q` 通过（4 passed）。
- 阶段推进：阶段 7 状态保持“启动中”，当前断点切换为 S7-02 准备。
- 文档口径同步：已同步更新阶段 7 开发/验收清单与架构总纲。
- 完成 S6-08：阶段 6 验收收口，补齐 `docs/project/stage-6-acceptance-checklist.md` 验收执行记录与收口结论。
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
- 阶段 6 验收清单口径对齐：docs/project/stage-6-acceptance-checklist.md 状态更新为 S6-00~S6-04 已完成，S6-05~S6-08 待推进。
- 模块 SKILL 口径对齐：02-user-org-auth、03-project-assets-env、04-api-testing 状态从“进行中”调整为“收尾中”，并明确仅执行阶段 2 收尾范围缺陷修复/治理优化。
### 2026-03-17
- 启动阶段 6：新增 `docs/project/stage-6-development-checklist.md` 与 `docs/project/stage-6-acceptance-checklist.md`，建立阶段 6 SSOT、门禁、DoD 与中断恢复机制。
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
- 阶段 5 SSOT 已落盘：`docs/project/stage-5-development-checklist.md`、`docs/project/stage-5-acceptance-checklist.md`。
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
- 同步阶段文档：更新 `docs/project/stage-5-development-checklist.md`、`docs/project/stage-5-acceptance-checklist.md`，完成 S5-07 记录与结论落盘。
- 同步模块与架构文档：更新 `docs/modules/future/08-reporting-analytics/SKILL.md` 与 `docs/architecture/企业级自动化测试平台系统架构规划.md`，保持阶段口径一致。
### 2026-03-16
- 阶段状态切换：`阶段 2 进行中 -> 收尾中`，`阶段 3 未开始 -> 启动中`
- 同步更新阶段门禁与模块匹配：`docs/modules/future/README.md`、`docs/modules/future/05-web-testing/SKILL.md`
- 同步检查并更新架构总纲阶段状态：`docs/architecture/企业级自动化测试平台系统架构规划.md`
- 新增阶段 3 开发清单文档：`docs/project/stage-3-development-checklist.md`（阶段 3 进度追踪 SSOT）
- 对齐文档进度口径：更新 `docs/project/project-overview.md`、`docs/architecture/system-architecture.md`、`docs/architecture/dependency-graph.md`，消除与阶段 2 实际能力的冲突表述
- 阶段 3 启动：完成 S3-00（开发准备），明确阶段 3 最小闭环路径、后端目录/命名规划、接口边界与产物归档约定（更新 `docs/project/stage-3-development-checklist.md`）
- 阶段 3 推进：完成 S3-01（Web 领域模型与用例管理），落地 `web_test_cases/web_steps/web_locators` 模型与迁移，并提供最小 CRUD API；新增后端测试 `tests/backend/test_web_test_cases_api.py`；回归通过 `.\.venv\Scripts\python -m pytest`
- 阶段 3 推进：完成 S3-02（Playwright 执行引擎最小闭环），落地 `web_test_runs` 模型与迁移、Web 单用例执行接口与执行结果查询接口，产物归档路径为 `artifacts/web-test-runs/{run_id}/`；新增后端测试 `tests/backend/test_web_test_runs_api.py`；回归通过 `.\.venv\Scripts\python -m pytest`
- 阶段 3 推进：完成 S3-03（前端最小页面闭环），新增 `frontend/src/views/WebTestCaseList.vue` 与 `frontend/src/views/WebTestRunDetail.vue`，补齐 Web 路由与 API 用例页入口按钮
- 阶段 3 验证执行：完成前端构建验证 `npm run build`（frontend，通过）
- 阶段 3 推进：完成 S3-04（统一归档与展示对齐），新增统一结果查询接口 `GET /api/test-runs/project/{project_id}/unified-results` 与前端聚合页 `frontend/src/views/UnifiedRunList.vue`
- 阶段 3 增强：统一结果接口新增分页与筛选（`run_type/status/created_from/created_to/page/page_size`），统一结果页新增筛选栏、分页与失败记录快速定位
- 阶段 3 测试门禁：新增 `tests/backend/test_unified_results_api.py`，并通过回归 `.\.venv\Scripts\python -m pytest tests/backend/test_unified_results_api.py tests/backend/test_test_runs_api.py tests/backend/test_web_test_runs_api.py`（12 passed）
- 阶段 3 测试门禁：完成前端构建验证 `npm run build`（frontend，通过）
- 阶段状态切换：`阶段 3 启动中 -> 收尾中`，`阶段 4 未开始 -> 启动中`
- 新增阶段 4 开发清单文档：`docs/project/stage-4-development-checklist.md`（阶段 4 进度追踪 SSOT）
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
- 新增阶段 2 验收清单文档：`docs/project/stage-2-acceptance-checklist.md`
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

- S4-05 kickoff: added `docs/project/stage-4-acceptance-checklist.md` with A4-01~A4-05 acceptance rubric.
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
- 新增阶段 2 执行清单文档：`docs/project/stage-2-development-checklist.md`（含已完成/进行中/待完成、优先级、验收标准、测试门禁与单人开发顺序）
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

