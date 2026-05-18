# 第53章：Docker 与容器化 — 理论

## 为什么需要容器化？

经典问题："在我电脑上能跑！"

```
传统部署问题
┌─────────────────────────────────────────────────────┐
│  开发机               测试机              生产机      │
│  Python 3.11         Python 3.9         Python 3.8  │
│  Ubuntu 22.04        CentOS 7           RHEL 8      │
│  libssl 3.0          libssl 1.1.1       libssl 1.0  │
│                                                     │
│  → 同一份代码，三个环境表现不同！                     │
└─────────────────────────────────────────────────────┘

Docker 容器化解决方案
┌─────────────────────────────────────────────────────┐
│           容器镜像（Image）                          │
│  ┌─────────────────────────────────────────────┐   │
│  │  Python 3.11 + 所有依赖 + 应用代码           │   │
│  │  完全隔离，任何支持Docker的机器上行为一致     │   │
│  └─────────────────────────────────────────────┘   │
│  开发机 ✓    测试机 ✓    生产机 ✓    云服务 ✓        │
└─────────────────────────────────────────────────────┘
```

---

## 1. Docker 核心概念

```
核心概念关系图
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Dockerfile ──build──▶ Image（镜像） ──run──▶ Container │
│  （构建脚本）          （只读模板）          （运行实例） │
│                                                        │
│  Registry（注册中心）                                   │
│  ├── Docker Hub（公共）                                  │
│  └── 私有 Registry（公司内部）                           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

| 概念 | 类比 | 说明 |
|------|------|------|
| Image（镜像）| 程序安装包 | 只读的模板，包含运行所需的一切 |
| Container（容器）| 运行中的程序 | 由镜像启动的隔离进程 |
| Dockerfile | 制作安装包的脚本 | 描述如何构建镜像的文件 |
| Registry | 应用商店 | 存储和分发镜像的仓库 |

---

## 2. Dockerfile 核心指令

### 完整指令说明

```dockerfile
# FROM：指定基础镜像（必须是第一条指令）
FROM python:3.11-slim

# LABEL：添加元数据标签
LABEL maintainer="zhangsan@example.com" \
      version="1.0"

# WORKDIR：设置工作目录（不存在则自动创建）
WORKDIR /app

# ENV：设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# COPY：复制文件（推荐优先于 ADD）
# 语法：COPY <源路径> <目标路径>
COPY requirements.txt .
COPY src/ ./src/

# ADD：高级版 COPY（支持 URL 和自动解压 tar）
ADD https://example.com/config.tar.gz /config/

# RUN：构建时执行命令（每个 RUN 创建一个新层）
RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE：声明容器监听的端口（文档性质，不自动映射）
EXPOSE 8000

# VOLUME：声明挂载点（数据持久化）
VOLUME /data

# ARG：构建时参数（build-time，运行时不可见）
ARG BUILD_ENV=production

# CMD：容器启动时的默认命令（可被 docker run 覆盖）
CMD ["python", "main.py"]

# ENTRYPOINT：容器入口点（不易被覆盖，CMD作为参数）
ENTRYPOINT ["uvicorn", "main:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
```

### CMD vs ENTRYPOINT 对比

```
ENTRYPOINT + CMD 组合使用
┌──────────────────────────────────────────────────┐
│  ENTRYPOINT ["uvicorn", "main:app"]              │
│  CMD ["--host", "0.0.0.0", "--port", "8000"]     │
│                                                  │
│  实际执行：                                        │
│  uvicorn main:app --host 0.0.0.0 --port 8000    │
│                                                  │
│  覆盖端口（docker run 追加参数）：                  │
│  docker run myapp --port 9000                    │
│  → uvicorn main:app --port 9000                  │
└──────────────────────────────────────────────────┘
```

---

## 3. Python 应用的标准 Dockerfile

```dockerfile
# 标准 Python Web 应用 Dockerfile
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 先复制依赖文件（利用层缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制源码（代码变化不影响依赖层缓存）
COPY src/ ./src/
COPY main.py .

# 创建非 root 用户（安全最佳实践）
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**层缓存优化原理：**

```
Dockerfile 层结构（从上到下）
┌────────────────────────────────────┐
│ FROM python:3.11-slim              │ 基础层（很少变化）
├────────────────────────────────────┤
│ COPY requirements.txt .            │ 依赖描述（偶尔变化）
│ RUN pip install ...               │
├────────────────────────────────────┤
│ COPY src/ .                        │ 源代码（频繁变化）
└────────────────────────────────────┘

将变化频率低的层放在前面 = 构建更快！
```

---

## 4. 多阶段构建

多阶段构建让生产镜像更小、更安全：

```dockerfile
# ===== 阶段一：构建阶段 =====
FROM python:3.11 AS builder

WORKDIR /build

# 安装构建工具
RUN pip install build

# 复制项目文件
COPY . .

# 构建 wheel 包
RUN python -m build --wheel

# ===== 阶段二：生产阶段 =====
FROM python:3.11-slim AS production

WORKDIR /app

# 只复制构建好的 wheel（不包含源码和构建工具）
COPY --from=builder /build/dist/*.whl /tmp/

# 安装 wheel
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# 非 root 用户
RUN adduser --disabled-password appuser
USER appuser

CMD ["my-app"]
```

**多阶段构建的优势：**

```
对比镜像大小
┌────────────────────────────────────────────────┐
│  单阶段构建                                     │
│  python:3.11 + 编译工具 + 源码 + 依赖           │
│  ≈ 1.2 GB                                      │
│                                                │
│  多阶段构建（生产镜像）                           │
│  python:3.11-slim + 仅运行时依赖                │
│  ≈ 200 MB  （节省约 80%）                       │
└────────────────────────────────────────────────┘
```

---

## 5. docker-compose.yml

`docker-compose` 用于编排多容器应用：

```yaml
# docker-compose.yml
version: "3.9"

services:
  # Web API 服务
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"      # 宿主机端口:容器端口
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy  # 等待数据库健康检查通过
      cache:
        condition: service_started
    volumes:
      - ./logs:/app/logs   # 挂载日志目录
    restart: unless-stopped

  # PostgreSQL 数据库
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data  # 命名卷持久化数据
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存
  cache:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

---

## 6. .dockerignore 文件

类似 `.gitignore`，防止将不必要的文件复制进镜像：

```
# .dockerignore

# 版本控制
.git/
.gitignore

# Python 缓存
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/

# 虚拟环境（绝对不能打包进镜像！）
.venv/
venv/
env/

# 构建产物
dist/
build/
*.egg-info/

# 测试和开发文件
tests/
docs/
*.md
.coverage
htmlcov/

# 本地配置（含密钥！）
.env
.env.local
*.local

# Docker 自身文件
Dockerfile*
docker-compose*
```

---

## 关键命令速查

```bash
# 构建镜像
docker build -t my-app:1.0.0 .
docker build -t my-app:latest --no-cache .

# 运行容器
docker run -d -p 8000:8000 --name my-app my-app:1.0.0
docker run -it --rm python:3.11-slim bash  # 交互式，退出后删除

# 查看和管理
docker ps            # 查看运行中的容器
docker ps -a         # 查看所有容器
docker images        # 查看本地镜像
docker logs my-app   # 查看日志
docker exec -it my-app bash  # 进入容器

# docker-compose 命令
docker-compose up -d          # 后台启动所有服务
docker-compose down           # 停止并删除容器
docker-compose logs -f api    # 跟踪服务日志
docker-compose ps             # 查看服务状态
docker-compose build          # 重新构建镜像
```
