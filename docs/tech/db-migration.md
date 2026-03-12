# 数据库迁移与 PostgreSQL 落地指南

## 1. 当前状态

- 已接入 Alembic
- 配置文件：`alembic.ini`
- 迁移目录：`migrations/`
- 基线版本：`migrations/versions/8daac485a5f7_initial_schema.py`
- 当前最新版本：`migrations/versions/fcf57b5ad65c_minimal_rbac_role.py`
- 已支持本地/测试环境切换 PostgreSQL

## 2. 配置说明

核心配置位于 `app/config.py`：

- `APP_ENV`：`local` / `test` / `prod`
- `USE_POSTGRES`：是否启用 PostgreSQL
- `DATABASE_URL`：显式数据库连接串（优先级最高）
- `TEST_DATABASE_URL`：测试环境连接串（`APP_ENV=test` 时优先）
- `POSTGRES_*`：当未显式配置 URL 时，用于拼接 PostgreSQL URL

本地示例文件：`.env.postgres.example`

## 3. 本地 PostgreSQL 启动

使用仓库内编排文件启动：

```bash
docker compose -f docker-compose.postgres.yml up -d
```

说明：
- 本地开发库：`web_api_automation_dev`
- 测试库：`web_api_automation_test`
- 测试库由 `infra/postgres/init/01-create-test-db.sql` 自动创建

## 3.1 一键启动（推荐）

脚本：`scripts/dev-postgres-up.ps1`

### 本地环境
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\dev-postgres-up.ps1 -TargetEnv local
```

### 测试环境
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\dev-postgres-up.ps1 -TargetEnv test
```

脚本会自动执行：
- Docker 健康检查
- `alembic upgrade head`
- 连通性与表结构自检（`scripts/db_connectivity_check.py`）

## 3.2 一键关闭（支持可选清理卷）

脚本：`scripts/dev-postgres-down.ps1`

### 仅停止服务
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\dev-postgres-down.ps1
```

### 停止并清理卷
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\dev-postgres-down.ps1 -RemoveVolumes -RemoveOrphans
```

## 3.3 API 启动脚本（数据库就绪后自动启动）

脚本：`scripts/dev-api-up.ps1`

### 本地环境启动 API
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\dev-api-up.ps1 -TargetEnv local
```

### 测试环境启动 API
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\dev-api-up.ps1 -TargetEnv test
```

### 仅做数据库准备（不启动 API）
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\dev-api-up.ps1 -TargetEnv local -PrepareOnly
```

## 3.4 API 停止脚本

脚本：`scripts/dev-api-down.ps1`

### 按端口停止 API（默认 8000）
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\dev-api-down.ps1
```

### 指定端口停止 API
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\dev-api-down.ps1 -Port 8011
```

## 3.5 生产环境迁移脚本（不含压测）

脚本：`scripts/prod-db-migrate.ps1`

用途：
- 在 `prod` 环境执行 Alembic 迁移
- 支持迁移前数据库备份（默认启用）
- 支持迁移后连通性与表结构自检（默认启用）

强制保护：
- 必须传入 `-ConfirmText I_UNDERSTAND_THIS_IS_PRODUCTION`
- 必须显式提供 `DATABASE_URL`（环境变量或 `-DatabaseUrl`）

### 生产迁移（默认：备份 + 迁移 + 自检）
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\prod-db-migrate.ps1 `
  -ConfirmText I_UNDERSTAND_THIS_IS_PRODUCTION `
  -DatabaseUrl "postgresql+psycopg://user:password@host:5432/dbname"
```

### 指定目标版本
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\prod-db-migrate.ps1 `
  -ConfirmText I_UNDERSTAND_THIS_IS_PRODUCTION `
  -DatabaseUrl "postgresql+psycopg://user:password@host:5432/dbname" `
  -TargetRevision 01fcc228897e
```

### 仅演练流程（Dry Run）
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\prod-db-migrate.ps1 `
  -ConfirmText I_UNDERSTAND_THIS_IS_PRODUCTION `
  -DryRun -SkipBackup -SkipConnectivityCheck
```

## 4. 迁移命令

### 4.1 升级到最新版本
```bash
.\.venv\Scripts\alembic upgrade head
```

### 4.2 回滚到 base
```bash
.\.venv\Scripts\alembic downgrade base
```

### 4.3 创建新迁移（自动比对）
```bash
.\.venv\Scripts\alembic revision --autogenerate -m "your_message"
```

### 4.4 创建空迁移（手写）
```bash
.\.venv\Scripts\alembic revision -m "your_message"
```

## 5. 本地/测试环境运行示例

### 5.1 本地开发（PostgreSQL）
```bash
$env:APP_ENV='local'
$env:USE_POSTGRES='true'
.\.venv\Scripts\alembic upgrade head
uvicorn app.main:app --reload
```

### 5.2 测试环境（PostgreSQL）
```bash
$env:APP_ENV='test'
$env:USE_POSTGRES='true'
.\.venv\Scripts\alembic upgrade head
```

### 5.3 测试环境（显式 URL）
```bash
$env:APP_ENV='test'
$env:TEST_DATABASE_URL='postgresql+psycopg://postgres:postgres@127.0.0.1:5432/web_api_automation_test'
.\.venv\Scripts\alembic upgrade head
```

## 6. 开发约束

- 涉及数据库结构变更时，必须提交 Alembic 迁移脚本
- 迁移脚本必须包含完整 `upgrade()` 与 `downgrade()`
- 提交前至少执行一次：
  - `alembic upgrade head`
  - `alembic downgrade base`
  - 再 `alembic upgrade head`
