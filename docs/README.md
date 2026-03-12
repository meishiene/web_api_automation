# API 测试平台文档导航

## 1. AI 快速熟悉（必读）
按下面顺序阅读，可在最短时间内理解“做什么、做到哪、改哪里”：

1. `docs/project/project-overview.md`：项目目标、已实现能力、边界
2. `docs/project/project-progress.md`：当前进度、阶段状态、下一步优先级
3. `docs/architecture/system-architecture.md`：系统分层、调用流程、认证链路
4. `docs/modules/modules.md`：按文件定位模块职责（最重要的改码索引）
5. `docs/architecture/dependency-graph.md`：前后端与数据流依赖关系

## 2. 按任务找文档
- 需要快速定位代码文件：看 `docs/modules/modules.md`
- 需要理解调用链和耦合点：看 `docs/architecture/dependency-graph.md`
- 需要确认技术约束和运行方式：看 `docs/tech/tech-stack.md`
- 需要确认目录结构：看 `docs/tech/repo-structure.md`
- 需要确认核心实体与业务关系：看 `docs/domain/domain-model.md`
- 需要数据库迁移规范：看 `docs/tech/db-migration.md`
- 需要日志与审计规范：看 `docs/tech/logging-audit-spec.md`
- 需要中长期路线图：看 `docs/architecture/企业级自动化测试平台系统架构规划.md`
- 需要后续模块化开发指引：看 `docs/modules/future/README.md`

## 3. 文档使用原则
- 文档与代码冲突时，以 `app/` 与 `frontend/src/` 实际代码为准
- 仅有模型或页面占位，不算功能已完成
- 任何影响功能/架构/阶段状态的改动，都必须同步更新 `docs/project/project-progress.md`
