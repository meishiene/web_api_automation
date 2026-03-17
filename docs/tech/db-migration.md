# 数据库迁移与 PostgreSQL 落地指南

## 1. 当前状态

- 已接入 Alembic
- 配置文件：`alembic.ini`
- 迁移目录：`migrations/`
- 基线版本：`migrations/versions/8daac485a5f7_initial_schema.py`
- 当前最新版本：`migrations/versions/7d2b6f4c8a1e_phase6_notification_center_minimal.py`
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

配套脚本：
- `scripts/db_revision_check.py`：读取当前数据库 `alembic_version`
- `scripts/prod-db-rollback.ps1`：按目标版本或迁移清单执行回滚

用途：
- 在 `prod` 环境执行 Alembic 迁移
- 支持迁移前数据库备份（默认启用）
- 支持迁移后连通性与表结构自检（默认启用）
- 自动记录迁移清单（迁移前版本、目标版本、备份文件、回滚命令、完成状态）

强制保护：
- 必须传入 `-ConfirmText I_UNDERSTAND_THIS_IS_PRODUCTION`
- 必须显式提供 `DATABASE_URL`（环境变量或 `-DatabaseUrl`）
- 运行环境需提供可用的 `python` / `alembic`，脚本优先使用仓库 `.venv`，缺失时回退到系统 `PATH`

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

### 迁移产物
- 默认备份目录：`backups/prod-db/`
- 默认迁移清单目录：`artifacts/prod-db-migrations/`
- 每次迁移都会生成一份 JSON 清单，包含：
  - `pre_revision`
  - `target_revision`
  - `post_revision`
  - `backup_file`
  - `status`
  - `rollback_command`

## 3.6 生产回滚脚本

脚本：`scripts/prod-db-rollback.ps1`

用途：
- 在 `prod` 环境按目标版本执行 Alembic 回滚
- 支持直接读取迁移清单中的 `pre_revision`
- 支持回滚后连通性与表结构自检（默认启用）

强制保护：
- 必须传入 `-ConfirmText I_UNDERSTAND_THIS_WILL_ROLLBACK_PRODUCTION`
- 必须显式提供 `DATABASE_URL`（环境变量或 `-DatabaseUrl`）；迁移清单不保存生产连接串
- 运行环境需提供可用的 `python` / `alembic`，脚本优先使用仓库 `.venv`，缺失时回退到系统 `PATH`

### 基于迁移清单回滚
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\prod-db-rollback.ps1 `
  -ConfirmText I_UNDERSTAND_THIS_WILL_ROLLBACK_PRODUCTION `
  -ManifestPath .\artifacts\prod-db-migrations\prod_migration_20260312_120000.json `
  -DatabaseUrl "postgresql+psycopg://user:password@host:5432/dbname"
```

### 指定目标版本回滚
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\prod-db-rollback.ps1 `
  -ConfirmText I_UNDERSTAND_THIS_WILL_ROLLBACK_PRODUCTION `
  -DatabaseUrl "postgresql+psycopg://user:password@host:5432/dbname" `
  -TargetRevision 802c16c9f78e
```

### 仅演练回滚流程（Dry Run）
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\prod-db-rollback.ps1 `
  -ConfirmText I_UNDERSTAND_THIS_WILL_ROLLBACK_PRODUCTION `
  -TargetRevision 802c16c9f78e `
  -DryRun -SkipConnectivityCheck
```

## 3.7 生产窗口执行 Runbook

### 窗口前检查
- 确认目标版本与对应迁移脚本已在测试环境完成 `upgrade -> downgrade -> upgrade` 验证
- 确认应用发布包、数据库连接串、值班人和回滚责任人已就位
- 确认 `pg_dump` 可用，且备份目录剩余空间充足
- 确认业务低峰窗口、只读/停写策略和公告已执行

### 窗口执行步骤
1. 先执行 dry-run，确认命令参数和目录输出无误
2. 执行正式迁移命令，保留终端日志与生成的迁移清单
3. 检查迁移清单 `status=completed`，并确认 `post_revision` 符合预期
4. 执行应用健康检查与关键接口冒烟
5. 完成窗口记录，登记执行人、时间、版本、备份文件与结果

### 回滚决策
- 若 Alembic 迁移失败且尚未切流，优先依据迁移清单执行 `alembic downgrade` 回到 `pre_revision`
- 若数据库状态异常且无法通过降级恢复，使用迁移前备份按数据库恢复流程执行 `pg_restore`
- 回滚后必须重新执行连通性检查、关键接口冒烟和版本确认

### 建议留档项
- 迁移命令
- 迁移清单路径
- 备份文件路径
- 执行终端日志
- 冒烟验证结果
- 是否触发回滚及原因

## 3.8 生产窗口实操演练脚本（留档）

脚本：`scripts/prod-db-window-drill.ps1`

用途：
- 演练完整窗口流程：`迁移到目标版本 -> 回滚到迁移前版本 -> 再迁移到目标版本`
- 自动产出演练留档（JSON + Markdown）
- 支持使用独立演练库，避免影响现有开发/测试库

强制保护：
- 必须传入 `-ConfirmText I_UNDERSTAND_THIS_IS_DB_WINDOW_DRILL`
- 默认会创建临时 SQLite 演练库；也可通过 `-DatabaseUrl` 指定演练数据库

### 执行示例（推荐）
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\prod-db-window-drill.ps1 `
  -ConfirmText I_UNDERSTAND_THIS_IS_DB_WINDOW_DRILL
```

### 关键参数
- `-TargetRevision`：目标版本（默认 `head`）
- `-BootstrapRevision`：临时演练库引导版本（默认 `fcf57b5ad65c`）
- `-ReportDir`：演练报告目录（默认 `artifacts/prod-db-window-drill`）
- `-SkipConnectivityCheck`：跳过迁移后连通性检查

### 演练产物
- `artifacts/prod-db-window-drill/window_drill_<timestamp>.json`
- `artifacts/prod-db-window-drill/window_drill_<timestamp>.md`
- `artifacts/prod-db-window-drill/manifests/prod_migration_<timestamp>.json`

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
- 生产迁移需保留迁移清单与备份信息，禁止只执行命令不留痕

