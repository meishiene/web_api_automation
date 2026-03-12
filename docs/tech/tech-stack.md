# Technology Stack

## 后端
- **语言**：Python 3
- **Web 框架**：FastAPI
- **ASGI 服务**：uvicorn
- **ORM**：SQLAlchemy
- **配置管理**：pydantic-settings
- **HTTP 客户端**：httpx

## 前端
- **语言**：JavaScript ES Modules
- **框架**：Vue 3
- **路由**：Vue Router 4
- **请求库**：axios
- **构建工具**：Vite 5

## 数据存储
- **默认数据库**：SQLite
- **已支持数据库**：SQLite、PostgreSQL（本地/测试环境）
- **默认连接串**：`sqlite:///./test_platform.db`
- **PostgreSQL 驱动**：`psycopg[binary]`

## 当前技术实现特征
- FastAPI 同时承载同步路由与异步测试执行接口
- 测试执行通过 `httpx.AsyncClient` 发起外部请求
- 前端通过 axios 拦截器统一处理认证头与 401 跳转
- 前端 `baseURL` 支持两种来源：
  - `VITE_API_BASE_URL`
  - 根据当前页面 origin 推导 `:8000`

## 运行方式

### 后端开发运行
```bash
uvicorn app.main:app --reload
```

### 前端开发运行
```bash
cd frontend
npm run dev
```

### 根目录一键开发运行
```bash
npm run dev
```

说明：
- 根目录 `package.json` 已提供统一开发入口
- `npm run dev` 会同时启动后端与前端开发服务
- 后端固定使用仓库内 `.venv\Scripts\python.exe` 启动 `uvicorn`
- 根目录 `npm run dev` 默认走本地开发配置，可直接使用默认 `SQLite`
- 前端通过 `frontend/package.json` 的 `vite` 启动

## 已声明依赖

### Python 依赖
`requirements.txt` 中当前声明：
- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `pydantic-settings`
- `httpx`
- `pytest`
- `python-jose[cryptography]`
- `alembic`
- `psycopg[binary]`

### Node 依赖
`frontend/package.json` 中当前声明：
- `vue`
- `vue-router`
- `axios`
- `vite`
- `@vitejs/plugin-vue`

### 根目录 Node 脚本
`package.json` 中当前声明：
- `dev`
- `dev:backend`
- `dev:frontend`
- `build`
- `preview`

## 与代码一致的重要说明
- 当前认证已使用 JWT + Refresh Token；受保护接口走 Bearer 鉴权
- 当前已引入 Alembic 作为数据库迁移工具，迁移目录为 `migrations/`
- 当前已支持按环境切换 SQLite / PostgreSQL（见 `app/config.py`）
- 当前没有 Redis、Celery、消息队列、任务调度器等基础设施
- 当前已引入 `pytest` 作为后端测试门禁基础
