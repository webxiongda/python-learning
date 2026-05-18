# 第55章：里程碑：完整微服务项目 — 项目任务

## 项目名称

Docker Compose 微服务练习项目

## 目标

把工程化章节整合成一个可本地编排的多服务项目。重点是服务边界、配置管理、健康检查、日志、容器化和基础 CI 思维。

## 交付目录

在 `projects/chapter-55/` 下完成：

```text
projects/chapter-55/
├── README.md
├── docker-compose.yml
├── services/
│   ├── api/
│   │   ├── Dockerfile
│   │   └── app/
│   └── worker/
│       ├── Dockerfile
│       └── app/
├── tests/
│   └── test_health.py
└── .env.example
```

## 服务要求

- API 服务：提供 `/health`、`/tasks`、`/tasks/{id}`。
- Worker 服务：模拟异步处理任务，可轮询 Redis 或内存队列。
- Redis：用于任务状态或缓存。
- 数据库：SQLite 或 PostgreSQL 均可，必须说明选择原因。
- docker-compose：一条命令启动所有服务。

## 工程要求

- 所有服务有健康检查。
- 配置通过环境变量读取，提交 `.env.example`，不提交真实 `.env`。
- Dockerfile 使用合理缓存层，先复制依赖文件再安装依赖。
- 日志输出包含服务名、事件、任务 ID。
- README 包含服务拓扑和本地启动步骤。

## 测试要求

- 至少测试 API 健康检查和任务创建流程。
- 测试可以在本地 Python 环境运行，不强制依赖完整容器环境。
- 如果加入 CI，至少运行 lint/test 两步。

## 阶段拆分

1. **单服务版**：先让 API 服务在本地直接运行，提供 `/health`。
2. **容器版**：为 API 写 Dockerfile，确认镜像可以独立启动。
3. **多服务版**：加入 Worker、Redis 和数据库，使用 Compose 编排。
4. **配置版**：把端口、数据库地址、Redis 地址放到环境变量。
5. **验收版**：补健康检查、日志、测试和 README 排错指南。

## 完成定义

这个项目完成时，你应该能解释清楚：

- 服务边界如何划分，API 和 Worker 分别负责什么。
- 为什么不能把真实密钥提交到仓库。
- Dockerfile 中依赖安装层为什么要放在代码复制之前。
- 健康检查和普通接口测试有什么不同。
- Compose 适合本地编排，和生产部署之间有什么差异。

## 验收清单

- [ ] `docker compose up --build` 能启动服务。
- [ ] API 服务健康检查返回正常。
- [ ] 任务创建后能查询状态。
- [ ] `.env.example` 覆盖必要配置项。
- [ ] README 写清服务边界、启动、停止、排错。
