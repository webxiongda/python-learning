# Chapter 55 Project: Docker Compose 微服务项目

## Goal

实现一个可通过 Docker Compose 本地启动的多服务项目。

## Services

- API：提供健康检查和任务接口
- Worker：处理任务
- Redis：任务状态或缓存
- Database：SQLite 或 PostgreSQL

## Commands

```bash
docker compose up --build
docker compose down
python -m pytest
```

## Acceptance

- 所有服务有健康检查。
- `.env.example` 覆盖必要配置。
- API 能创建任务并查询状态。
- README 写清服务边界和排错步骤。
