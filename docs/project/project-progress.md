# 项目进度文档

## 1. 文档目的

本文档用于记录当前项目的实际开发进度，帮助后续参与开发的 AI 或开发者快速掌握：

- 当前项目做到什么程度
- 哪些模块已经完成、部分完成、未开始
- 最近新增或修改了什么
- 接下来最优先要做什么

本文件是项目级进度基线，后续凡是对代码进行新增、修改、删除，且影响功能、结构、模块状态或开发阶段判断时，都应同步更新本文档。

## 2. 当前项目阶段

- **当前总阶段**：阶段 0 已完成，阶段 1 进行中
- **项目定位**：MVP 级 API 自动化测试工具，正准备向企业级自动化测试平台演进
- **平台目标**：统一承载 `API 测试 + Web 测试 + 调度执行 + 报告治理 + 企业集成`

## 3. 当前总体进度

| 领域 | 当前状态 | 进度 |
| --- | --- | --- |
| 用户与认证 | 已完成 JWT + Refresh Token、最小 RBAC（admin/user）与关键治理接口权限校验 | 60% |
| 项目管理 | 已支持基础 CRUD | 40% |
| API 用例管理 | 已支持基础 CRUD | 35% |
| API 执行能力 | 已支持单条执行 | 25% |
| 工程化与测试基线 | 已建立测试基线、统一异常错误码、结构化日志、审计治理闭环、Alembic/PG 本地测试落地与模型治理细则 | 90% |
| Web 测试能力 | 未开始 | 0% |
| 环境与变量管理 | 未开始 | 0% |
| 套件与批量执行 | 未开始 | 0% |
| 调度与队列 | 已有预留模型，未打通 | 5% |
| 报告与分析 | 仅有基础结果记录 | 5% |
| 权限与治理 | 已完成最小 RBAC 闭环，细粒度治理未开始 | 20% |
| 企业集成 | 未开始 | 0% |

## 4. 当前阶段状态表

| 阶段 | 名称 | 状态 | 说明 |
| --- | --- | --- | --- |
| 阶段 0 | MVP 雏形 | 已完成 | 已完成最小 API 测试闭环 |
| 阶段 1 | 平台基础重构 | 进行中 | 已完成测试基线、认证升级、迁移基线、DTO 统一、模型关系映射、模型治理细则、审计治理闭环、最小 RBAC 与生产迁移脚本，生产窗口执行与治理运营能力待建设 |
| 阶段 2 | API 平台化 | 未开始 | 套件、批量执行、环境变量待建设 |
| 阶段 3 | Web 测试平台建设 | 未开始 | Playwright 与 Web 用例体系待建设 |
| 阶段 4 | 调度与分布式执行 | 未开始 | Scheduler、Queue、Worker 待建设 |
| 阶段 5 | 报告分析与治理 | 未开始 | 报告中心、趋势分析、治理待建设 |
| 阶段 6 | 企业集成与生态完善 | 未开始 | CI/CD、SSO、通知、缺陷集成待建设 |

## 5. 当前已完成内容

### 5.1 后端
- 已建立 `FastAPI` 应用入口
- 已接入 `auth`、`projects`、`test_cases`、`test_runs` 路由
- 已支持用户注册和登录
- 已支持项目 CRUD
- 已支持 API 测试用例 CRUD
- 已支持单条 API 测试执行
- 已支持执行结果入库
- 已保留 `schedule_tasks` 与 `run_queue` 模型
- 已建立 `pytest` 后端测试基线（28 个用例）
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

### 5.2 前端
- 已建立登录页、注册页、项目列表页、测试用例页
- 已建立统一请求封装
- 已建立基础路由守卫
- 已打通项目管理与 API 用例管理主链路
- 已支持在测试用例页面触发执行并查看最近结果

### 5.3 文档
- 已补充项目概览文档
- 已补充系统架构文档
- 已补充模块清单、领域模型、技术栈、仓库结构文档
- 已新增企业级平台总纲文档

## 6. 当前部分完成内容

### 6.1 认证
- 已完成 JWT 访问令牌与刷新令牌基础链路
- 已完成 Bearer 鉴权接入与受保护接口校验
- 已完成密码哈希存储（兼容历史明文用户登录后自动迁移）
- 已完成最小 RBAC（`admin/user`）与关键治理接口权限校验
- 组织级权限治理、细粒度权限矩阵与成员模型尚未完成

### 6.2 执行能力
- 当前只支持单条 API 用例执行
- 尚不支持 API 套件、批量回归、计划执行
- 尚未支持 Web 自动化执行

### 6.3 结果展示
- 当前已记录执行结果
- 但尚未形成正式的报告中心、趋势分析、失败聚类分析

### 6.4 数据库迁移
- 已完成 Alembic 基线和本地/测试 PostgreSQL 落地
- 已提供生产环境迁移脚本（`scripts/prod-db-migrate.ps1`，含强制确认、可选备份与可选自检）
- 生产环境迁移发布流程与回滚预案仍需在生产窗口执行并固化

### 6.5 调度与队列
- 数据模型已存在
- 尚无调度服务、消费服务、Worker 体系和前端管理页面

### 6.6 审计治理
- 已提供审计日志查询接口（按用户、动作、结果、request_id、时间范围筛选）
- 已提供审计归档表 `audit_logs_archive`
- 已提供保留策略执行脚本 `scripts/audit-governance-run.py`（支持 dry-run）
- 仍需生产环境定时任务接入与运维告警编排

## 7. 当前未开始内容

- 组织级与细粒度权限治理（RBAC 深化）
- 多环境与变量管理
- API 套件与批量执行
- Web 自动化测试模块
- 调度系统与分布式执行
- 报告中心与趋势分析
- CI/CD 集成
- SSO / LDAP / OAuth2 集成
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

## 9. 下一阶段优先事项

### P0：平台底座
- PostgreSQL 生产环境迁移发布演练与窗口执行（按当前决策不做压测）
- 认证治理收口（细粒度权限矩阵、组织/成员模型、越权校验补齐）
- 落地迁移执行流程与发布规范
- 完善审计治理的生产化编排（定时执行、告警、权限隔离）

### P1：API 平台化
- 增加 API 套件
- 增加批量执行
- 增加环境与变量管理
- 增强断言能力
- 增加执行详情与批次结果页

### P2：Web 测试模块
- 引入 `Playwright`
- 建立 Web 用例模型
- 建立页面对象、步骤与定位器模型
- 支持 Web 执行产物归档

## 10. 最近更新记录

### 2026-03-12
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
