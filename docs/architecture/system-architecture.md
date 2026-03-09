# System Architecture

## 架构模式
**前后端分离架构** + **RESTful API** + **单用户MVP模式**

- 前端: Vue 3 + Vite + Vue Router（单页应用）
- 后端: FastAPI（异步Python Web框架）
- 数据层: SQLAlchemy ORM + SQLite（本地数据库）

## 系统分层

```
┌─────────────────────────────────────────┐
│           表示层 (Presentation)          │
│          Vue.js 前端应用                 │
│  - 项目管理界面                         │
│  - 测试用例管理界面                     │
│  - 测试执行界面                         │
│  - 测试报告界面                         │
└──────────────┬──────────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────────┐
│           应用层 (Application)           │
│          FastAPI 后端服务                │
│  - 路由控制器 (Routers)                  │
│  - 业务服务 (Services)                   │
│  - 认证中间件 (Auth)                     │
│  - CORS中间件                            │
└──────────────┬──────────────────────────┘
               │ SQLAlchemy ORM
┌──────────────▼──────────────────────────┐
│           数据层 (Data)                  │
│          SQLite 数据库                   │
│  - 用户表 (users)                        │
│  - 项目表 (projects)                     │
│  - 测试用例表 (api_test_cases)          │
│  - 测试执行记录表 (test_runs)           │
└─────────────────────────────────────────┘
```

## 服务结构

### 后端服务 (FastAPI)
- **服务名称**: API Test Platform
- **启动文件**: `app/main.py`
- **监听端口**: 8000 (默认)
- **路由结构**:
  - `/api/auth`: 认证路由 (注册、登录)
  - `/api/projects`: 项目管理路由
  - `/api/test-cases`: 测试用例管理路由
  - `/api/test-runs`: 测试执行和报告路由
  - `/ping`: 健康检查端点

### 前端服务 (Vue.js)
- **应用名称**: test-platform-frontend
- **启动文件**: `frontend/src/main.js`
- **监听端口**: 5173 (默认)
- **代理配置**: 通过Vite代理转发API请求到 `http://localhost:8000`
- **路由结构**:
  - `/login`: 登录页面
  - `/register`: 注册页面
  - `/`: 项目列表页面
  - `/project/:id`: 项目详情和测试用例页面

## 模块交互

```
用户请求
   ↓
Vue Router 路由匹配
   ↓
Vue 组件发起 HTTP 请求 (axios)
   ↓
Vite Dev Server 代理 (/api → http://localhost:8000)
   ↓
FastAPI 路由匹配
   ↓
依赖注入 (get_db, get_current_user)
   ↓
业务逻辑处理
   ↓
SQLAlchemy ORM 数据库操作
   ↓
SQLite 数据持久化
   ↓
响应返回 (JSON)
```

## 外部系统

### 被测试的API服务
- **角色**: 系统的外部依赖和测试目标
- **交互方式**: 通过 httpx 库发起HTTP请求
- **协议支持**: HTTP/HTTPS
- **超时设置**: 30秒
- **认证方式**: 无（由测试用例的headers配置决定）

### 数据库
- **类型**: SQLite (文件型数据库)
- **连接方式**: SQLAlchemy ORM
- **数据库文件**: `./test_platform.db`
- **表结构**: 4张主表（users, projects, api_test_cases, test_runs）
