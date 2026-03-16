# 阶段 3 开发清单（Web 测试平台建设）

> 目的：给阶段 3 提供一个“随时可读的单一事实来源（SSOT）”，用于追踪 **已完成 / 进行中 / 待完成**，并约束交付物、测试门禁与 DoD。
>
> 适用规则：
> - 任何涉及逻辑/功能代码改动：先补/更测试，再实现；并执行最小相关测试集（公共模块需要补回归）。
> - 若改动影响模块状态、阶段进度或路线图：同轮同步更新 `docs/project/project-progress.md` 的“最近更新记录”，并检查 `docs/architecture/企业级自动化测试平台系统架构规划.md` 是否需要同步修订。

## 0. 阶段定位（以当前代码与进度基线为准）

- 阶段名称：阶段 3 Web 测试平台建设
- 当前状态：启动中（首批能力待落地）
- 当前总阶段：阶段 2 收尾中 + 阶段 3 启动中（详见 `docs/project/project-progress.md`）
- 本阶段目标：建立 Web 自动化测试模块，使平台具备 API + Web 双引擎能力，并实现统一执行结果归档/展示的最小闭环。

## 1. 范围边界

### In Scope（阶段 3 首批）
- Web 用例与套件（最小可执行闭环）
- 定位器（Locator）与步骤（Step）编排：打开、点击、输入、等待、断言、截图
- Playwright 执行引擎接入（单用例执行最小闭环）
- 产物链路预留：截图、视频、Trace（先最小可用，后续增强）
- Web 执行结果最小展示链路（与 API 结果风格一致，至少可回溯）

### Out of Scope（本阶段不做）
- 像素级视觉回归（可作为后续扩展）
- 分布式调度/队列/Worker（属于阶段 4）
- 报告中心与趋势分析（属于阶段 5）

## 2. 阶段 3 工作分解（以可交付切片推进）

> 说明：为了让“进度可证据化”，每个条目都明确：交付物、最小测试集、DoD。未打通链路不得标记为完成。

### S3-00：开发准备（必做）
- 状态：已完成
- 交付物：
  - 明确阶段 3 的最小闭环路径（从 Web 用例创建 -> 执行 -> 结果/产物查看）
  - 统一命名与目录规划（Web 领域模型、执行入口、产物归档）
- 最小测试集：
  - 无（仅文档/方案）
- DoD：
  - 本清单中的 S3-01~S3-04 的接口边界与落地顺序明确

#### 2.1 最小闭环路径（阶段 3 首批）

> 目标：先做“能跑、可回溯、可定位”的 Web 单用例闭环，再扩展套件、更多步骤与更完整的报告。

1. Web 用例管理
   - 在项目内创建/编辑 Web 用例
   - 在用例中编排最小步骤序列（打开/点击/输入/等待/断言/截图）
2. Web 单用例执行
   - 平台内触发执行（后端调用 Playwright）
   - 写入一次 Web 执行记录（状态、开始/结束、错误信息）
3. 结果与产物回溯
   - 可查看执行详情（至少：总体状态、关键错误、步骤日志摘要）
   - 可查看产物（至少：失败截图；后续扩展 trace/video）

#### 2.2 命名与目录规划（后端）

> 原则：与阶段 2 既有结构保持一致，先“隔离新增领域”，避免把 Web 能力硬塞进 API 用例/执行表导致大改。

- 模型（ORM）：`app/models/`
  - `web_test_case.py`：`WebTestCase`（表：`web_test_cases`）
  - `web_step.py`：`WebStep`（表：`web_steps`，按 `order_index` 排序）
  - `web_locator.py`：`WebLocator`（表：`web_locators`，可复用定位器资产）
  - 说明：`PageObject` 作为阶段 3 扩展项预留（先不强制落地，避免放大首批范围）
- DTO（Schema）：`app/schemas/`
  - `web_test_case.py`：创建/更新/详情响应（可内嵌步骤列表）
  - `web_step.py`、`web_locator.py`：若需要拆分独立 CRUD，再分别引入
- 路由（API）：`app/api/`
  - `web_test_cases.py`：Web 用例管理
  - `web_test_runs.py`：Web 执行与结果查询（与现有 `test_runs.py` 平行）
- 服务层：`app/services/`
  - `web_executor.py`：Playwright 封装执行器（浏览器/上下文生命周期、超时、截图等）
  - （可选）`web_artifacts.py`：产物归档工具函数（路径生成、文件写入、索引元数据）

#### 2.3 API 边界（阶段 3 首批）

> 约束：阶段 3 首批只承诺“Web 单用例执行闭环”。Web 套件（`WebTestSuite`）可在阶段 3 后续迭代或作为阶段 4 前置补齐。

- Web 用例管理（建议前缀）：`/api/web-test-cases`
  - `GET /api/web-test-cases/project/{project_id}`：列表（按项目）
  - `POST /api/web-test-cases`：创建（含步骤）
  - `GET /api/web-test-cases/{case_id}`：详情（含步骤）
  - `PUT /api/web-test-cases/{case_id}`：更新（含步骤）
  - `DELETE /api/web-test-cases/{case_id}`：删除
- Web 执行与结果
  - `POST /api/web-test-runs/web-test-cases/{case_id}/run`：触发单用例执行
  - `GET /api/web-test-runs/{run_id}`：执行详情（含错误、步骤摘要、产物索引）
  - （可选）`GET /api/web-test-runs/project/{project_id}`：按项目查询最近执行列表

#### 2.4 权限与访问控制（沿用既有治理口径）

- Web 用例与 Web 执行的权限规则对齐现有 `access_control`：
  - 项目 owner 或项目成员（maintainer/editor/viewer）可 view
  - 需要“管理用例”的能力：owner/maintainer/editor（viewer 只读）
  - 需要“执行”的能力：owner/maintainer/editor（viewer 默认不允许执行，避免资源滥用）

#### 2.5 产物归档（阶段 3 首批约定）

- 产物根目录：仓库根 `artifacts/`
- Web 执行产物目录建议：
  - `artifacts/web-test-runs/<run_id>/`
    - `screenshot.png`（失败截图或最后截图）
    - `trace.zip`（后续启用）
    - `video.webm`（后续启用）
    - `meta.json`（产物索引与关键信息，便于前端展示）

### S3-01：Web 领域模型与迁移（最小可执行资产）
- 状态：已完成
- 范围（首批模型建议）：
  - `WebTestCase`：用例元数据 + 与 Project 绑定
  - `WebStep`：按顺序编排步骤
  - `Locator`：定位器资产（可复用）
- 交付物：
  - ORM 模型 + Alembic 迁移
  - 最小 CRUD API（至少用例与步骤可保存/查询）
- 最小测试集（后端）：
  - 模型/接口基础 CRUD 测试
  - 权限隔离测试（owner/成员越权 403）
- DoD：
  - 可在 DB 中持久化 Web 用例 + 步骤，并能按项目查询与编辑

#### 交付物落地情况（2026-03-16）

- 领域模型（ORM）：
  - `app/models/web_test_case.py`（`web_test_cases`）
  - `app/models/web_step.py`（`web_steps`）
  - `app/models/web_locator.py`（`web_locators`）
- 迁移：
  - `migrations/versions/adeb808fa0e9_phase3_web_testing_core.py`
- 后端 API：
  - `app/api/web_test_cases.py`
  - 路由前缀：`/api/web-test-cases`
    - `GET /api/web-test-cases/project/{project_id}`
    - `POST /api/web-test-cases`
    - `GET /api/web-test-cases/{case_id}`
    - `PUT /api/web-test-cases/{case_id}`
    - `DELETE /api/web-test-cases/{case_id}`
- 最小测试集：
  - 新增：`tests/backend/test_web_test_cases_api.py`
  - 验证通过：`.\.venv\Scripts\python -m pytest`（全量通过）

### S3-02：Playwright 执行引擎接入（单用例执行）
- 状态：已完成
- 交付物：
  - Playwright 执行器封装（浏览器启动/复用策略可先简化）
  - Web 单用例执行 API（最小闭环：执行一个 WebTestCase 并落库结果/状态）
  - 失败定位最小信息：步骤级日志 + 至少一张失败截图（或最后截图）
- 最小测试集（后端）：
  - 执行入口的权限与参数校验（bad request / forbidden）
  - 执行失败场景的产物生成测试（至少截图链路）
- DoD：
  - 可通过 API 触发 Web 单用例执行，并能在平台侧查询到执行结果与关键失败信息

#### 交付物落地情况（2026-03-16）

- 执行模型与迁移：
  - `app/models/web_test_run.py`（`web_test_runs`）
  - `migrations/versions/11eb5f289eaf_phase3_web_test_runs.py`
- 执行服务：
  - `app/services/web_executor.py`
  - 基于 Playwright 的最小步骤执行（open/click/input/wait/assert/screenshot）
  - 失败场景自动尝试写入 `failure.png`
- 执行 API：
  - `app/api/web_test_runs.py`
  - 路由前缀：`/api/web-test-runs`
    - `POST /api/web-test-runs/web-test-cases/{case_id}/run`
    - `GET /api/web-test-runs/project/{project_id}`
    - `GET /api/web-test-runs/{run_id}`
- 产物归档：
  - `artifacts/web-test-runs/{run_id}/...`
- 最小测试集：
  - 新增：`tests/backend/test_web_test_runs_api.py`
  - 验证通过：`.\.venv\Scripts\python -m pytest`

### S3-03：前端最小页面闭环（管理 + 执行 + 查看）
- 状态：待开始
- 交付物（最小页面集合）：
  - Web 用例管理页（列表/编辑/步骤编排最小形态）
  - 执行入口（触发执行）
  - 结果查看页（最小展示：状态、耗时、关键日志/截图入口）
- 最小测试集（前端）：
  - `npm run build`（门禁）
- DoD：
  - 平台内完成 Web 用例创建/编辑/执行/查看（最小闭环）

### S3-04：统一归档与展示对齐（API/Web 同口径）
- 状态：待开始
- 交付物：
  - 统一的执行结果“展示/归档约定”（字段口径与链接策略）
  - Web 执行结果与 API 执行结果在展示层的最低一致性（例如：状态枚举、开始/结束时间、产物入口）
- 最小测试集：
  - API/Web 结果查询的兼容性测试（至少 schema/关键字段）
- DoD：
  - Web 结果可以在平台内被稳定查询与回溯，且与 API 的结果结构不冲突

## 3. 进度看板（手工维护，保守标记）

| 条目 | 状态 | 备注 |
| --- | --- | --- |
| S3-00 | 已完成 | 明确最小闭环路径、后端目录/命名、接口边界、产物归档约定 |
| S3-01 | 已完成 | Web 领域模型 + 迁移 + 最小 CRUD API + 最小测试集 |
| S3-02 | 已完成 | Playwright 执行器 + 单用例执行接口 + 结果/产物查询 |
| S3-03 | 待开始 |  |
| S3-04 | 待开始 |  |

## 4. 阶段 3 完成定义（DoD）

- 可在平台内管理并执行 Web 用例
- 关键失败场景可定位（日志 + 产物）
- Web 模块具备稳定回归能力（最小回归测试集可运行、可重复）

## 5. 最近更新记录

### 2026-03-16
- 新增阶段 3 开发清单：用于后续阶段 3 迭代的进度追踪与门禁对齐
- 完成 S3-00：明确阶段 3 最小闭环路径、后端目录/命名规划、接口边界与产物归档约定
- 完成 S3-01：落地 Web 领域模型与迁移，并提供最小 Web 用例 CRUD API（含测试门禁）
- 完成 S3-02：落地 Playwright 执行引擎最小闭环（单用例执行）与 Web 执行结果/产物查询接口
