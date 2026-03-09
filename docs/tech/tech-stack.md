# Technology Stack

## 编程语言
- **后端**: Python 3.x
- **前端**: JavaScript (ES6+)
- **模板**: Vue单文件组件 (.vue)

## 后端框架
- **Web框架**: FastAPI 0.100+
  - 异步支持
  - 自动生成OpenAPI文档
  - Pydantic数据验证

- **ORM框架**: SQLAlchemy
  - Declarative Base模型定义
  - Session管理
  - 关系映射 (ForeignKey)

- **配置管理**: pydantic-settings
  - 环境变量支持
  - 类型验证

## 前端框架
- **核心框架**: Vue 3.4+
  - Composition API (setup语法)
  - 响应式系统 (ref, reactive)
  - 组件化开发

- **路由管理**: Vue Router 4.2+
  - 客户端路由
  - 路由守卫
  - 动态路由

- **构建工具**: Vite 5.0+
  - 快速HMR (热模块替换)
  - ESBuild预构建
  - 开发服务器代理

## 数据库
- **数据库类型**: SQLite
- **连接方式**: 文件型数据库 (`./test_platform.db`)
- **ORM**: SQLAlchemy
- **连接参数**: `check_same_thread=False` (支持多线程)

## 中间件和库
- **HTTP客户端**: httpx
  - 异步HTTP请求
  - 支持超时控制
  - JSON响应处理

- **HTTP服务**: uvicorn
  - ASGI服务器
  - 异步支持

- **跨域处理**: FastAPI CORSMiddleware
  - 允许所有来源 (`*`)
  - 允许所有方法
  - 允许所有头部

- **HTTP请求库**: axios 1.6+
  - Promise API
  - 拦截器支持
  - 自动JSON转换

## 构建和运行工具
- **后端运行**: uvicorn
  - 命令: `uvicorn app.main:app --reload`
  - 端口: 8000

- **前端开发**: Vite
  - 命令: `npm run dev`
  - 端口: 5173
  - 代理: `/api` → `http://localhost:8000`

- **前端构建**: Vite build
  - 命令: `npm run build`
  - 输出: 静态文件 (dist目录)

## 依赖管理
- **后端**: pip + requirements.txt
- **前端**: npm + package.json

## 开发工具
- **代码编辑**: 任意IDE (VSCode推荐)
- **版本控制**: Git
- **包管理**:
  - Python: pip
  - Node.js: npm
