# 阶段 7 验收清单（S7 Acceptance Checklist）

## 1. 验收范围
- 验收阶段：阶段 7（运营化与平台扩展）
- 验收口径：以 `app/`、`frontend/src/`、`tests/backend/` 当前代码事实与测试结果为准
- 当前阶段状态：S7-00~S7-06 已完成，阶段 7 已完成验收

## 2. 功能验收项（必须满足）

| 编号 | 验收项 | 通过标准（Pass 条件） | 证据 |
| --- | --- | --- | --- |
| A7-01 | 导入能力可用 | 至少支持一种标准格式导入并形成可执行资产 | 导入 API + 映射测试 |
| A7-02 | 扩展骨架可用 | provider 注册、发现、分发机制可用 | provider 骨架实现 + 分发测试 |
| A7-03 | 运营看板增强可用 | 支持跨项目最小聚合与关键风险信号展示 | 聚合 API/前端 + 权限测试 |
| A7-04 | 治理执行增强可用 | 批量治理具备幂等与审计追踪 | 治理 API + 审计测试 |
| A7-05 | 稳定性门禁成立 | 性能与中等数据量回归门禁可重复执行 | 性能/稳定性测试报告 |
| A7-06 | 文档口径一致 | 阶段 7 清单、项目进度、模块 SKILL、架构文档同步一致 | `docs/project/*`、`docs/modules/future/*`、`docs/architecture/*` |

## 3. 质量门禁（必须通过）

| 门禁项 | 目标命令 | 通过标准 |
| --- | --- | --- |
| 阶段 7 最小回归 | `python -m pytest <阶段7相关测试集> -q` | 全部通过 |
| 后端全量回归 | `python -m pytest -q` | 全部通过（允许非阻塞 warning） |
| 前端构建 | `npm run build`（frontend） | 构建成功 |
| 迁移链路（建议） | `alembic upgrade head -> downgrade <阶段7前一revision> -> upgrade head` | 升降级成功 |

## 4. 非功能验收口径（阶段 7 出口）

- 安全性：扩展点接入边界清晰、权限校验一致
- 可观测性：跨项目治理指标可追踪、异常可定位
- 可恢复性：治理任务可重试、可幂等、可审计
- 可维护性：阶段 7 新增能力具备清晰边界与可替换性

## 5. 阶段 7 验收结论口径（通过条件）

满足以下条件可判定阶段 7 验收通过：
1. A7-01~A7-06 全部满足。
2. 质量门禁中的阶段 7 最小回归、后端全量回归、前端构建全部通过。
3. 阶段文档、项目进度与架构文档已同步，不存在“占位能力标记为完成”的表述。
4. 阶段 7 风险与阻塞清单中无未声明的阻塞项。

## 6. 验收执行记录

### 2026-03-26
- 阶段 7 最小回归：`python -m pytest tests/backend/test_import_provider_registry.py tests/backend/test_test_cases_api.py tests/backend/test_operations_overview_api.py tests/backend/test_integration_governance_api.py tests/backend/test_reporting_performance_guards.py -q`
  - 结果：通过（25 passed，2 warnings）
- 后端全量回归：`python -m pytest -q`
  - 结果：通过（允许非阻塞 warnings）
- 前端构建：`npm run build`（frontend）
  - 结果：通过
- 迁移链路：`alembic upgrade head -> downgrade 4c7b2d1e9a6f -> upgrade head`
  - 结果：通过（SQLite 临时库）

### 验收结论
- A7-01：通过
- A7-02：通过
- A7-03：通过
- A7-04：通过
- A7-05：通过
- A7-06：通过
- 阶段 7 验收结论：通过，可切换为“已完成验收”。

