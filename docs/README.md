# API 测试平台文档

## 文档结构
- `docs/project/project-overview.md`：项目目标、已实现功能、边界与未实现能力
- `docs/project/project-progress.md`：项目当前进度、阶段状态、最近更新记录与维护规则
- `docs/architecture/system-architecture.md`：系统分层、调用流程、认证方式与整体架构
- `docs/architecture/企业级自动化测试平台系统架构规划.md`：企业级平台目标架构、阶段路线图与开发纲领
- `docs/architecture/dependency-graph.md`：后端、前端与数据流依赖关系
- `docs/modules/modules.md`：按文件和职责梳理模块
- `docs/modules/future/README.md`：后续开发模块结构与模块级 `SKILL.md` 导航
- `docs/domain/domain-model.md`：核心实体、关系与业务规则
- `docs/tech/tech-stack.md`：技术栈、依赖与运行方式
- `docs/tech/repo-structure.md`：仓库结构与目录说明

## 推荐阅读顺序
1. 先看 `docs/project/project-overview.md`
2. 再看 `docs/project/project-progress.md`
3. 然后看 `docs/architecture/system-architecture.md`
4. 再看 `docs/architecture/企业级自动化测试平台系统架构规划.md`
5. 然后看 `docs/modules/future/README.md`
6. 最后根据需要查看模块、领域模型和技术栈文档

## 本次文档更新重点
- 按当前代码补充了简化认证方式：`X-User-ID`
- 明确了当前真正实现的是“单条测试执行 + 结果记录”
- 补充了 `schedule_tasks` 与 `run_queue` 预留模型
- 标注了前端与后端之间尚未完全打通的接口点
- 新增项目进度文档，作为后续持续更新的项目状态基线
- 新增企业级自动化测试平台架构规划文档，作为后续开发纲领
- 新增后续开发模块目录，并为每个模块提供独立 `SKILL.md`

## 使用文档时的原则
- 若文档与代码不一致，以 `app/` 和 `frontend/src/` 中的实际实现为准
- 预留模型不等于已交付功能，只有存在路由、服务和页面的能力才算完整落地
