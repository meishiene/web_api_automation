# Repository Structure

## 项目根目录

```
d:\project\test/
├── app/                          # 后端Python应用目录
│   ├── __init__.py              # Python包标识
│   ├── main.py                  # FastAPI应用入口和路由配置
│   ├── config.py                # 应用配置 (数据库URL, 密钥等)
│   ├── database.py              # 数据库连接和会话管理
│   ├── dependencies.py          # 依赖注入 (用户认证等)
│   │
│   ├── api/                     # API路由层
│   │   ├── __init__.py
│   │   ├── auth.py             # 认证路由 (注册/登录)
│   │   ├── projects.py         # 项目管理路由
│   │   ├── test_cases.py       # 测试用例管理路由
│   │   └── test_runs.py        # 测试执行和报告路由
│   │
│   ├── models/                  # 数据模型层 (SQLAlchemy ORM)
│   │   ├── __init__.py
│   │   ├── user.py             # User模型
│   │   ├── project.py          # Project模型
│   │   ├── api_test_case.py    # ApiTestCase模型
│   │   └── test_run.py         # TestRun模型
│   │
│   ├── services/                # 业务服务层
│   │   ├── __init__.py
│   │   └── test_executor.py    # 测试执行服务
│   │
│   ├── schemas/                 # Pydantic数据验证Schema (未使用)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── api_test_case.py
│   │   └── test_run.py
│   │
│   └── __pycache__/            # Python字节码缓存 (自动生成)
│
├── frontend/                    # 前端Vue.js应用目录
│   ├── src/                     # 源代码目录
│   │   ├── api/                 # API调用封装
│   │   │   └── *.js            # 各模块API请求方法
│   │   │
│   │   ├── router/              # 路由配置
│   │   │   └── index.js        # Vue Router配置
│   │   │
│   │   ├── views/               # 页面组件
│   │   │   └── *.vue           # 各页面Vue组件
│   │   │
│   │   ├── App.vue              # 根组件
│   │   ├── main.js              # 应用入口
│   │   └── assets/              # 静态资源 (图片、样式等)
│   │
│   ├── public/                  # 静态资源目录
│   │   └── vite.svg            # Vite图标
│   │
│   ├── index.html               # HTML入口模板
│   ├── package.json             # Node.js依赖和脚本配置
│   ├── vite.config.js           # Vite构建配置
│   ├── .env                     # 环境变量配置
│   └── node_modules/            # Node.js依赖包
│
├── docs/                        # 项目文档目录
│   ├── project/                 # 项目概述文档
│   ├── architecture/            # 架构设计文档
│   └── tech/                    # 技术栈文档
│
├── requirements.txt             # Python依赖列表
├── test_platform.db             # SQLite数据库文件 (运行时生成)
└── .git/                        # Git版本控制目录
```

## 核心目录说明

### app/ - 后端应用
**职责**: 实现完整的RESTful API服务，处理所有业务逻辑和数据持久化。

- **分层架构**:
  - `api/`: 控制器层，处理HTTP请求和响应
  - `services/`: 服务层，封装业务逻辑
  - `models/`: 模型层，定义数据结构和数据库映射
  - `schemas/`: 验证层，定义数据验证规则 (当前未使用)

### frontend/ - 前端应用
**职责**: 提供用户界面，通过API与后端交互。

- **架构模式**: 单页应用 (SPA)
- **组件结构**:
  - `views/`: 页面级组件
  - `components/`: 可复用组件 (未显式创建)
  - `api/`: API调用封装
  - `router/`: 路由配置

### docs/ - 文档目录
**职责**: 存放项目的技术文档和架构说明。

### 根目录文件
- **requirements.txt**: Python后端依赖清单
- **package.json**: 前端Node.js依赖和构建脚本
- **test_platform.db**: SQLite数据库文件 (运行时生成)
- **.git/**: Git版本控制元数据

## 文件类型分布

| 类型 | 数量 | 说明 |
|------|------|------|
| `.py` | ~15 | Python后端代码 |
| `.vue` | ~3 | Vue组件文件 |
| `.js` | ~5 | JavaScript配置和API封装 |
| `.json` | 2 | 配置文件 (package.json, .env) |
| `.html` | 1 | 前端入口HTML |
| `.db` | 1 | SQLite数据库 |
| `.md` | 多个 | 项目文档 |
