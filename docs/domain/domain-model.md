# Domain Model

## 核心领域实体

### 1. User (用户)
**实体职责**: 系统用户身份标识
**数据表**: `users`
**属性**:
- `id`: Integer (主键, 自增)
- `username`: String(50) (唯一, 索引, 非空)
- `password`: String(255) (非空, 明文存储)
- `created_at`: Integer (Unix时间戳, 非空)

**关系**:
- 一对多: `User` → `Project` (一个用户拥有多个项目)
- 权限控制: 所有受保护操作都需要通过User认证

---

### 2. Project (项目)
**实体职责**: 测试用例的容器和组织单元
**数据表**: `projects`
**属性**:
- `id`: Integer (主键, 自增, 索引)
- `name`: String(100) (非空)
- `description`: String(500) (可选)
- `owner_id`: Integer (外键 → users.id, 非空)
- `created_at`: Integer (Unix时间戳, 非空)

**关系**:
- 多对一: `Project` → `User` (项目属于一个用户)
- 一对多: `Project` → `ApiTestCase` (一个项目包含多个测试用例)
- 权限边界: 用户只能访问和操作自己的项目

---

### 3. ApiTestCase (API测试用例)
**实体职责**: 描述单个API测试的配置和期望结果
**数据表**: `api_test_cases`
**属性**:
- `id`: Integer (主键, 自增, 索引)
- `name`: String(100) (非空, 测试用例名称)
- `project_id`: Integer (外键 → projects.id, 非空)
- `method`: String(10) (非空, HTTP方法: GET/POST/PUT/DELETE)
- `url`: String(500) (非空, 完整的API URL)
- `headers`: Text (可选, JSON字符串格式的请求头)
- `body`: Text (可选, JSON字符串格式的请求体)
- `expected_status`: Integer (默认200, 期望的HTTP状态码)
- `expected_body`: Text (可选, JSON字符串格式的期望响应体)
- `created_at`: Integer (Unix时间戳, 非空)
- `updated_at`: Integer (Unix时间戳, 非空)

**关系**:
- 多对一: `ApiTestCase` → `Project` (测试用例属于一个项目)
- 一对多: `ApiTestCase` → `TestRun` (一个测试用例可执行多次)

**业务规则**:
- 只有POST/PUT/PATCH方法支持请求体
- headers和body存储为JSON字符串
- expected_body用于响应体断言验证

---

### 4. TestRun (测试执行记录)
**实体职责**: 记录单次测试执行的结果和详细信息
**数据表**: `test_runs`
**属性**:
- `id`: Integer (主键, 自增, 索引)
- `test_case_id`: Integer (外键 → api_test_cases.id, 非空)
- `status`: String(20) (非空, 执行状态: success/failed/error)
- `actual_status`: Integer (实际返回的HTTP状态码)
- `actual_body`: Text (实际返回的响应体)
- `error_message`: Text (执行错误信息)
- `duration_ms`: Integer (执行耗时, 毫秒)
- `created_at`: Integer (Unix时间戳, 非空)

**关系**:
- 多对一: `TestRun` → `ApiTestCase` (测试记录关联到测试用例)

**状态说明**:
- `success`: 实际结果完全匹配期望结果
- `failed`: HTTP请求成功, 但结果不匹配期望
- `error`: HTTP请求失败或发生异常

---

## 实体关系图

```
┌─────────────┐
│    User     │
│             │
│  - id       │
│  - username │
│  - password │
│  - created  │
└──────┬──────┘
       │ 1
       │
       │ owns
       │
       │ N
       ▼
┌─────────────┐
│   Project   │
│             │
│  - id       │
│  - name     │
│  - desc     │
│  - owner_id │
│  - created  │
└──────┬──────┘
       │ 1
       │
       │ contains
       │
       │ N
       ▼
┌─────────────────┐
│  ApiTestCase    │
│                 │
│  - id           │
│  - name         │
│  - project_id   │
│  - method       │
│  - url          │
│  - headers      │
│  - body         │
│  - expected_*   │
│  - created      │
│  - updated      │
└────────┬────────┘
         │ 1
         │
         │ executed as
         │
         │ N
         ▼
   ┌─────────────┐
   │  TestRun    │
   │             │
   │  - id       │
   │  - case_id  │
   │  - status   │
   │  - actual_* │
   │  - error    │
   │  - duration │
   │  - created  │
   └─────────────┘
         │
         │
         │ uses httpx to call
         │
         ▼
   ┌──────────────────┐
   │ External API     │
   │ (3rd Party)      │
   └──────────────────┘
```

## 领域概念

### 聚合根 (Aggregate Roots)
1. **Project**: 项目是主要的聚合根, 包含多个测试用例
   - 删除项目时级联删除所有关联的测试用例和测试记录

2. **User**: 用户是认证和权限的聚合根
   - 用户删除后, 其所有项目和测试数据失去访问权限

### 值对象 (Value Objects)
- **HTTP Request Config**: (method, url, headers, body) 作为测试用例的配置属性
- **HTTP Response Data**: (status, body) 作为测试结果的记录属性
- **Time Stamps**: created_at, updated_at 作为时间戳值对象

### 领域服务 (Domain Services)
- **TestExecutor**: 执行测试用例的核心服务
  - 解析测试配置
  - 发起HTTP请求
  - 验证响应结果
  - 计算执行耗时

### 应用服务 (Application Services)
- **AuthService**: 用户认证服务 (注册/登录)
- **ProjectService**: 项目管理服务 (CRUD)
- **TestCaseService**: 测试用例管理服务 (CRUD)
- **TestRunService**: 测试执行和报告服务

### 仓储 (Repositories)
- 通过SQLAlchemy ORM实现数据持久化
- 每个实体对应一个数据库表
- 使用Session进行事务管理

## 业务规则

### 权限规则
1. 用户只能访问自己的项目
2. 用户只能操作自己拥有的测试用例
3. 用户只能查看自己项目的测试记录

### 数据完整性规则
1. 项目必须关联到一个有效的用户 (owner_id外键约束)
2. 测试用例必须关联到一个有效的项目 (project_id外键约束)
3. 测试记录必须关联到一个有效的测试用例 (test_case_id外键约束)

### 测试执行规则
1. 测试执行超时时间: 30秒
2. HTTP状态码必须精确匹配期望值
3. 响应体支持JSON或字符串匹配
4. 执行结果必须持久化到数据库
