# 阶段 2 验收清单（S2 Acceptance Checklist）

## 1. 验收范围
- 验收阶段：阶段 2（API 平台化）
- 验收日期：2026-03-16
- 验收口径：以 `app/`、`frontend/src/`、`tests/backend/` 当前代码事实与回归结果为准

## 2. 功能验收项

| 编号 | 验收项 | 状态 | 证据 |
| --- | --- | --- | --- |
| A2-01 | 套件与批量执行闭环（触发、批次、明细） | Pass | `/api/test-runs/suites/{suite_id}/run`、`/api/test-runs/batches/*` |
| A2-02 | 断言能力覆盖（contains/regex/jsonpath/schema） | Pass | `tests/backend/test_test_executor_enhancements.py` |
| A2-03 | 失败重试与幂等保护 | Pass | `tests/backend/test_suite_batch_runs_api.py` |
| A2-04 | 用例治理能力（分组/标签/筛选/搜索） | Pass | `tests/backend/test_test_cases_api.py` + 前端筛选入口 |
| A2-05 | 用例资产流转（复制/导入/导出） | Pass | `app/api/test_cases.py` + `frontend/src/views/TestCaseList.vue` |
| A2-06 | 变量治理增强（变量组复用、密钥受控读取、前端联动） | Pass | `tests/backend/test_environments_api.py`、`tests/backend/test_suite_batch_runs_api.py`、`frontend/src/views/EnvironmentManager.vue` |
| A2-07 | 执行详情可定位（含运行时变量快照与来源） | Pass | `GET /api/test-runs/{run_id}`、`frontend/src/views/TestRunDetail.vue` |

## 3. 质量门禁

| 门禁项 | 结果 | 说明 |
| --- | --- | --- |
| 后端全量回归 | Pass | `.\.venv\Scripts\python -m pytest` -> `78 passed` |
| 前端构建 | Pass | `npm run build`（frontend）通过 |
| 迁移流程相关测试 | Pass | `.\.venv\Scripts\python -m pytest tests/backend/test_db_migration_workflow.py` -> `3 passed` |

## 4. 验收结论
- 阶段 2 核心能力已完成并通过全量回归，进入“可收尾发布/阶段切换评审”状态。
- 建议下一步：阶段 2 收尾文档归档 + 阶段 3 预研任务拆分。
