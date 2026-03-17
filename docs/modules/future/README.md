# 后续开发模块结构

本目录基于当前项目文档整理，用于承载后续企业级能力建设的模块化开发说明。

每个模块目录包含一个 `SKILL.md`，作为该模块的执行指南，统一约束：
- 模块目标
- 功能边界
- 开发任务
- 交付物
- 测试清单
- 完成定义（DoD）

## 强制执行规则（适用于全部模块）

- 开发任务必须同时遵守仓库根 `AGENTS.md` 与对应模块 `SKILL.md`
- 必须先以 `docs/project/project-progress.md` 的“当前总阶段”为准进行阶段匹配，再选择可执行模块
- 未命中当前阶段的模块，默认只允许方案设计/文档预研；若需越阶段落代码，必须由用户明确指令触发
- 涉及逻辑或功能代码改动时，必须执行测试并通过后才可交付
- 改动影响功能、模块状态、架构分层或路线图时，必须同步更新 `docs/project/project-progress.md`，并检查 `docs/architecture/企业级自动化测试平台系统架构规划.md`
- 当某一阶段的实际完成情况、剩余任务、交付物或 DoD 判断发生变化时，必须同步更新该阶段对应目录下的 `SKILL.md`

## 当前阶段匹配（依据 `project-progress.md`）

- 当前总阶段：阶段 2（收尾）+ 阶段 3（收尾）+ 阶段 4（已验收完成）+ 阶段 5（已验收完成）+ 阶段 6（启动中）
- 默认可执行模块：
  - `06-execution-orchestration`（阶段 4 完成态：仅缺陷修复/稳定性维护）
  - `07-scheduling-queue-worker`（阶段 4 完成态：仅缺陷修复/稳定性维护）
  - `05-web-testing`（阶段 3 收尾缺陷修复与稳定性增强）
  - `02-user-org-auth`（仅缺陷修复/治理收尾）
  - `03-project-assets-env`（仅缺陷修复/治理收尾）
  - `08-reporting-analytics`（阶段 5 完成态：缺陷修复与治理增强）
  - `09-enterprise-integrations`（阶段 6 启动：按 S6 清单推进实现）
  - `04-api-testing`（仅缺陷修复/治理收尾）
- 其余模块默认进入“设计/预研模式”，不应标记为“已完成实现”

## 模块目录

1. `01-platform-foundation`：平台基础重构
2. `02-user-org-auth`：用户、组织与认证鉴权
3. `03-project-assets-env`：项目、资产与环境变量
4. `04-api-testing`：API 测试平台化
5. `05-web-testing`：Web 自动化测试
6. `06-execution-orchestration`：统一执行编排
7. `07-scheduling-queue-worker`：调度、队列与 Worker
8. `08-reporting-analytics`：报告与质量分析
9. `09-enterprise-integrations`：企业集成与治理

## 推荐开发顺序

1. `01-platform-foundation`
2. `02-user-org-auth`
3. `03-project-assets-env`
4. `04-api-testing`
5. `05-web-testing`
6. `06-execution-orchestration`
7. `07-scheduling-queue-worker`
8. `08-reporting-analytics`
9. `09-enterprise-integrations`

