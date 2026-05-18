# 第53章：Docker 与容器化 — 自测题

## 题目1：Dockerfile 指令辨析

说明以下 Dockerfile 指令的区别：

1. `COPY` vs `ADD`
2. `CMD` vs `ENTRYPOINT`
3. `ENV` vs `ARG`
4. `RUN` vs `CMD`

### 参考答案

**1. COPY vs ADD：**
- `COPY`：简单的文件复制，只支持本地文件。推荐优先使用。
- `ADD`：支持 URL 下载和自动解压 tar.gz 文件。但行为复杂，不推荐用于简单复制。
- 最佳实践：只有需要自动解压 tar 时才用 `ADD`，其余用 `COPY`。

**2. CMD vs ENTRYPOINT：**
- `CMD`：提供默认命令，可被 `docker run` 后面的参数完全覆盖。
- `ENTRYPOINT`：容器的固定入口点，`docker run` 后面的参数会作为参数追加。
- 组合使用：`ENTRYPOINT` 定义命令，`CMD` 提供默认参数；`docker run` 可覆盖 `CMD` 部分。

**3. ENV vs ARG：**
- `ENV`：运行时环境变量，在构建时和容器运行时都可见。
- `ARG`：构建时参数，只在构建阶段可用，不会泄露到运行时的容器中。
- 使用场景：密钥等敏感信息绝对不能用 `ENV`（会暴露在镜像中），应通过运行时挂载 secrets。

**4. RUN vs CMD：**
- `RUN`：构建时执行，每次执行创建一个新的镜像层（如 `pip install`）。
- `CMD`：仅在容器启动时执行，不创建新层，是容器的默认入口命令。

---

## 题目2：层缓存优化

以下两个 Dockerfile，哪个更优？为什么？修改后每次代码变更时，哪些层会被重新构建？

**Dockerfile A：**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

**Dockerfile B：**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### 参考答案

**Dockerfile B 更优。**

**原因（层缓存机制）：**

Docker 按从上到下的顺序构建，当某一层的内容变化时，该层及其之后的所有层缓存都会失效，需要重新构建。

**Dockerfile A 的问题：**
- `COPY . .` 复制所有源码，每次修改任何源码文件都会使该层缓存失效
- 缓存失效后，`pip install` 也会重新执行，即使 `requirements.txt` 没有变化
- 结果：每次代码改动都要重新安装所有依赖，构建很慢

**Dockerfile B 的优化：**
- 先 `COPY requirements.txt`，再安装依赖
- 只要 `requirements.txt` 不变，`pip install` 层就会被缓存
- 最后 `COPY . .` 复制源码，只有这一层会因代码变化而重建

**每次代码变更时重建的层：**
- Dockerfile A：`COPY . .` + `pip install` = 重新安装所有依赖
- Dockerfile B：只有 `COPY . .` = 几乎瞬间完成

---

## 题目3：docker-compose 配置

解释以下 docker-compose.yml 片段中各字段的含义：

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### 参考答案

- `build: .`：从当前目录的 `Dockerfile` 构建镜像（而不是使用现有镜像）
- `ports: "8000:8000"`：端口映射，格式为 `宿主机端口:容器端口`。宿主机访问 8000 端口会转发到容器的 8000 端口
- `depends_on: db: condition: service_healthy`：等待 `db` 服务的健康检查通过后再启动 `api`。若只写 `depends_on: - db` 则只等待容器启动（不等数据库就绪），`api` 可能连接失败
- `environment: DATABASE_URL=${DATABASE_URL}`：从宿主机环境变量或 `.env` 文件读取 `DATABASE_URL` 并注入容器，避免在 compose 文件中硬编码密钥
- `volumes: ./data:/app/data`：将宿主机的 `./data` 目录挂载到容器的 `/app/data`，容器删除后数据仍然保留在宿主机
- `restart: unless-stopped`：容器异常退出时自动重启，但手动停止的不会自动重启（其他选项：`always`、`on-failure`、`no`）

---

## 题目4：多阶段构建

编写一个多阶段 Dockerfile，要求：
- 第一阶段安装所有依赖（含开发依赖）并运行测试
- 第二阶段只包含生产依赖，不包含测试工具和源码（只有 wheel 包）

### 参考答案

```dockerfile
# ===== 阶段一：测试阶段 =====
FROM python:3.11-slim AS tester

WORKDIR /app

# 安装所有依赖（含开发依赖）
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir \
    -r requirements.txt \
    -r requirements-dev.txt

# 复制源码并运行测试
COPY . .
RUN pytest tests/ -v && echo "测试全部通过！"

# ===== 阶段二：构建 wheel =====
FROM python:3.11-slim AS builder

WORKDIR /build
COPY . .
RUN pip install build && python -m build --wheel

# ===== 阶段三：生产镜像 =====
FROM python:3.11-slim AS production

WORKDIR /app

# 只从 builder 阶段复制 wheel 文件
COPY --from=builder /build/dist/*.whl /tmp/

# 安装 wheel（不需要源码）
RUN pip install --no-cache-dir /tmp/*.whl \
    && rm -rf /tmp/*.whl

# 非 root 用户
RUN adduser --disabled-password appuser
USER appuser

CMD ["my-app"]
```

**优势：**
- 测试失败时构建中止，确保生产镜像都是通过测试的
- 生产镜像不包含 pytest、源码等，体积更小，安全面更小

---

## 题目5：.dockerignore 的重要性

为什么 `.venv/` 目录必须加入 `.dockerignore`？如果不加会有什么后果？

### 参考答案

**.venv 不加 .dockerignore 的后果：**

1. **镜像体积巨大**：`.venv` 目录通常有几百 MB，将其复制进镜像会使镜像体积翻倍甚至更大。

2. **依赖可能损坏**：
   - 本地 `.venv` 是针对宿主机（macOS/Windows）编译的，容器内（Linux）可能无法使用
   - 尤其是带 C 扩展的包（如 numpy、psycopg2），跨平台后会损坏

3. **`pip install` 被覆盖**：Dockerfile 中通过 `pip install` 安装的包会被 `.venv` 中的包覆盖，导致版本不一致

4. **安全风险**：本地 `.venv` 可能包含开发时安装的调试工具、本地配置等，不应暴露在生产镜像中

**标准 .dockerignore 中应包含的 Python 相关条目：**
```
.venv/
venv/
env/
__pycache__/
*.py[cod]
.pytest_cache/
.env            # 本地密钥文件！
dist/
build/
```
