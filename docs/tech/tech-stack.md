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
- **数据库**：SQLite
- **连接串默认值**：`sqlite:///./test_platform.db`
- **线程参数**：`check_same_thread=False`

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
npm run dev
```

## 已声明依赖

### Python 依赖
`requirements.txt` 中当前声明：
- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `pydantic-settings`
- `httpx`

### Node 依赖
`frontend/package.json` 中当前声明：
- `vue`
- `vue-router`
- `axios`
- `vite`
- `@vitejs/plugin-vue`

## 与代码一致的重要说明
- 当前认证不是 JWT 真正落地方案，`ALGORITHM` 与 `ACCESS_TOKEN_EXPIRE_MINUTES` 只是保留配置
- 当前没有 Redis、Celery、消息队列、任务调度器等基础设施
- 当前没有测试框架依赖，执行器是应用内自定义实现
