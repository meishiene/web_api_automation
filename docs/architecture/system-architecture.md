# System Architecture

## 架构模式
当前项目采用 **前后端分离 + REST API + SQLite 本地持久化** 的轻量架构。

- 前端：Vue 3 + Vite + Vue Router
- 后端：FastAPI
- 数据访问：SQLAlchemy ORM
- 数据库：SQLite
- 外部调用：`httpx.AsyncClient`

## 分层结构
```text
浏览器 / Vue 前端
  ├─ 登录 / 注册页面
  ├─ 项目列表页面
  └─ 测试用例管理页面（含执行结果弹窗）

        │ HTTP + JSON
        ▼

FastAPI 应用
  ├─ app/main.py                应用入口与路由注册
  ├─ app/api/*.py               路由层
  ├─ app/dependencies.py        认证依赖
  ├─ app/services/test_executor.py  测试执行服务
  └─ app/models/*.py            ORM 模型

        │ SQLAlchemy
        ▼

SQLite 数据库
  ├─ users
  ├─ projects
  ├─ api_test_cases
  ├─ test_runs
  ├─ schedule_tasks   (预留)
  └─ run_queue        (预留)
```

## 后端服务结构

### 应用入口
- `app/main.py`
- 注册 CORS 中间件，当前配置为全部放开：`allow_origins=["*"]`
- 挂载路由：
  - `/api/auth`
  - `/api/projects`
  - `/api/test-cases`
  - `/api/test-runs`
- 提供健康检查：`GET /ping`
- 在 `startup` 事件中执行 `init_db()` 自动建表

### 认证方式
- 不是 JWT，也没有真正的 Bearer Token 校验
- 登录接口返回的 `access_token` 实际上是用户 `id` 的字符串
- 前端把用户 ID 保存到 `localStorage`
- 每次请求通过 `X-User-ID` 请求头传给后端
- `app/dependencies.py` 根据 `X-User-ID` 读取当前用户

这是一种 MVP 阶段的简化认证方案，便于联调，但安全性有限。

### 路由层
- `app/api/auth.py`：注册、登录
- `app/api/projects.py`：项目 CRUD
- `app/api/test_cases.py`：测试用例 CRUD
- `app/api/test_runs.py`：执行测试、按项目查询执行记录

### 服务层
- `app/services/test_executor.py`
- 负责把测试用例转换为 HTTP 请求参数并发起调用
- 支持解析 JSON `headers` / `body`
- 负责生成 `success` / `failed` / `error` 三种结果状态

## 前端结构
- 路由定义：`frontend/src/router/index.js`
- 页面：
  - `/login`
  - `/register`
  - `/`
  - `/project/:projectId`
- 路由守卫：未登录时跳转 `/login`

### 前端 API 封装
- `frontend/src/utils/request.js`
  - 自动推导默认 `baseURL`
  - 自动注入 `X-User-ID`
  - 401 时清理登录态并跳转登录页
- `frontend/src/api/projects.js`
- `frontend/src/api/testCases.js`

## 关键调用流程

### 登录流程
1. 用户在前端提交用户名密码
2. 前端调用 `POST /api/auth/login`
3. 后端校验明文密码
4. 前端保存 `userId`
5. 后续请求自动带上 `X-User-ID`

### 项目管理流程
1. 前端调用 `/api/projects`
2. 后端通过 `get_current_user()` 获取当前用户
3. 查询或写入当前用户拥有的项目
4. 返回 JSON 给前端渲染

### 测试执行流程
1. 前端在测试用例页面点击“运行”
2. 请求 `POST /api/test-runs/test-cases/{case_id}/run`
3. 后端校验用例归属
4. `test_executor.execute_test()` 调用目标 API
5. 结果写入 `test_runs`
6. 前端展示本次执行结果

## 当前架构特点
- 结构简单，适合快速开发和本地部署
- 认证链路简单，方便前后端联调
- 数据模型已为后续调度和队列做了预留
- 暂未形成完整“服务层 + 调度层 + 工作节点”体系
