# Repository Structure

## 根目录
```text
web_api_automation/
├─ app/                    后端代码
├─ docs/                   项目文档
├─ frontend/               前端代码
├─ requirements.txt        后端依赖
├─ test_platform.db        SQLite 数据库文件
├─ README.md               根说明文件
└─ ARCHITECTURE_DOCS_REPORT.md
```

## `app/` 后端目录
```text
app/
├─ api/
│  ├─ auth.py
│  ├─ projects.py
│  ├─ test_cases.py
│  └─ test_runs.py
├─ models/
│  ├─ user.py
│  ├─ project.py
│  ├─ api_test_case.py
│  ├─ test_run.py
│  ├─ schedule_task.py
│  └─ run_queue.py
├─ schemas/
│  ├─ user.py
│  ├─ project.py
│  ├─ api_test_case.py
│  └─ test_run.py
├─ services/
│  └─ test_executor.py
├─ config.py
├─ database.py
├─ dependencies.py
└─ main.py
```

### 说明
- `api/` 是当前业务主入口
- `models/` 包含已落地实体和预留扩展实体
- `schemas/` 目录存在，但当前路由文件大多直接在文件内定义 Pydantic 模型，尚未统一复用 `schemas/`
- `services/` 当前只有一个 `test_executor.py`

## `frontend/` 前端目录
```text
frontend/
├─ package.json
├─ src/
│  ├─ api/
│  │  ├─ projects.js
│  │  └─ testCases.js
│  ├─ router/
│  │  └─ index.js
│  ├─ utils/
│  │  └─ request.js
│  ├─ views/
│  │  ├─ Login.vue
│  │  ├─ Register.vue
│  │  ├─ ProjectList.vue
│  │  └─ TestCaseList.vue
│  ├─ App.vue
│  └─ main.js
```

### 说明
- 页面数量较少，当前以业务闭环优先
- `TestCaseList.vue` 同时承担列表、编辑弹窗、执行结果展示等职责
- 还没有独立的测试结果列表页、报表页或系统设置页

## `docs/` 文档目录
- `project/`：项目概览
- `architecture/`：系统架构与依赖关系
- `domain/`：领域模型
- `modules/`：模块清单
- `tech/`：技术栈与仓库结构

## 代码与文档对照时的注意点
- `app/models/schedule_task.py` 与 `app/models/run_queue.py` 已在代码中存在，但尚未形成完整功能
- `frontend/src/api/testCases.js` 中保留了 `getTestResult()` 方法，但后端当前没有对应 `GET /api/test-runs/{runId}` 接口
- `app/schemas/` 与当前路由的实际使用方式存在一定重复，后续可以考虑统一整理
