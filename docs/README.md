# API测试平台 - 架构文档

## 文档结构

### 项目概述
- **[项目概览](project/project-overview.md)**: 项目目标、功能、用户角色和系统边界

### 系统架构
- **[系统架构](architecture/system-architecture.md)**: 架构模式、系统分层、服务结构、模块交互
- **[依赖关系图](architecture/dependency-graph.md)**: 模块依赖和数据流关系

### 技术栈
- **[技术栈](tech/tech-stack.md)**: 编程语言、框架、数据库、中间件、构建工具
- **[仓库结构](tech/repo-structure.md)**: 目录结构和文件组织

### 模块清单
- **[系统模块](modules/modules.md)**: 所有模块的职责、目录、依赖和接口

### 领域模型
- **[领域模型](domain/domain-model.md)**: 核心实体、关系图、聚合根和业务规则

---

## 快速导航

### 我想了解...
- **项目是做什么的?** → 查看 [项目概览](project/project-overview.md)
- **系统如何工作?** → 查看 [系统架构](architecture/system-architecture.md)
- **使用了什么技术?** → 查看 [技术栈](tech/tech-stack.md)
- **代码在哪里?** → 查看 [仓库结构](tech/repo-structure.md)
- **有哪些模块?** → 查看 [系统模块](modules/modules.md)
- **数据如何组织?** → 查看 [领域模型](domain/domain-model.md)

### 核心概念
- **用户**: 系统使用者, 拥有项目和测试用例
- **项目**: 测试用例的容器, 组织单元
- **测试用例**: 单个API测试配置
- **测试记录**: 测试执行的历史结果

### 技术关键词
- **后端**: FastAPI, SQLAlchemy, SQLite, httpx
- **前端**: Vue 3, Vite, Vue Router, axios
- **架构**: 前后端分离, RESTful API, ORM

---

## 文档版本
- **生成日期**: 2026-03-09
- **目标**: AI理解项目架构的基础文档
- **适用阶段**: Stage 1 - 架构分析
