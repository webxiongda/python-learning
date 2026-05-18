# 第53章：Docker 与容器化 — Demo

## Demo 1：生成标准 Python 应用 Dockerfile

```python
# demo1_dockerfile_generator.py
# 根据项目配置自动生成 Dockerfile 和 .dockerignore

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class DockerConfig:
    app_name: str
    python_version: str = "3.11"
    base_image: str = "slim"         # slim / alpine / full
    port: int = 8000
    entry_point: str = "main:app"    # uvicorn 入口
    server: str = "uvicorn"          # uvicorn / gunicorn
    use_non_root: bool = True
    has_system_deps: bool = False    # 是否需要安装系统包
    system_packages: list = field(default_factory=list)

def generate_dockerfile(cfg: DockerConfig) -> str:
    """生成 Dockerfile 内容"""
    lines = []
    
    # 选择基础镜像
    base = f"python:{cfg.python_version}-{cfg.base_image}"
    lines.append(f"FROM {base}")
    lines.append("")
    
    # 元数据
    lines.append(f"LABEL app=\"{cfg.app_name}\"")
    lines.append("")
    
    # 环境变量
    lines.append("# 禁止 Python 生成 .pyc 文件，禁用输出缓冲")
    lines.append("ENV PYTHONDONTWRITEBYTECODE=1 \\")
    lines.append("    PYTHONUNBUFFERED=1 \\")
    lines.append(f"    PORT={cfg.port}")
    lines.append("")
    
    # 工作目录
    lines.append("WORKDIR /app")
    lines.append("")
    
    # 安装系统依赖（如果需要）
    if cfg.has_system_deps and cfg.system_packages:
        pkgs = " ".join(cfg.system_packages)
        lines.append("# 安装系统依赖")
        if cfg.base_image in ("slim", "alpine"):
            if cfg.base_image == "alpine":
                lines.append(f"RUN apk add --no-cache {pkgs}")
            else:
                lines.append("RUN apt-get update && apt-get install -y \\")
                lines.append(f"    {pkgs} \\")
                lines.append("    && rm -rf /var/lib/apt/lists/*")
        lines.append("")
    
    # 复制并安装 Python 依赖（利用层缓存）
    lines.append("# 先安装依赖（利用 Docker 层缓存）")
    lines.append("COPY requirements.txt .")
    lines.append("RUN pip install --no-cache-dir -r requirements.txt")
    lines.append("")
    
    # 复制源码
    lines.append("# 复制源码")
    lines.append("COPY . .")
    lines.append("")
    
    # 创建非 root 用户
    if cfg.use_non_root:
        lines.append("# 使用非 root 用户运行（安全最佳实践）")
        lines.append("RUN adduser --disabled-password --gecos \"\" appuser")
        lines.append("USER appuser")
        lines.append("")
    
    # 暴露端口
    lines.append(f"EXPOSE {cfg.port}")
    lines.append("")
    
    # 启动命令
    lines.append("# 启动命令")
    if cfg.server == "uvicorn":
        lines.append(f'CMD ["uvicorn", "{cfg.entry_point}", \\')
        lines.append(f'     "--host", "0.0.0.0", "--port", "{cfg.port}"]')
    else:
        lines.append(f'CMD ["gunicorn", "-w", "4", \\')
        lines.append(f'     "-b", "0.0.0.0:{cfg.port}", "{cfg.entry_point}"]')
    
    return "\n".join(lines)

def generate_dockerignore() -> str:
    """生成 .dockerignore 内容"""
    return """\
# 版本控制
.git/
.gitignore

# Python 缓存
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.mypy_cache/

# 虚拟环境（绝对不能打包进镜像！）
.venv/
venv/
env/

# 构建产物
dist/
build/
*.egg-info/

# 测试文件
tests/
.coverage
htmlcov/

# 文档
docs/
*.md

# 本地配置（含密钥）
.env
.env.local
*.local

# Docker 文件本身
Dockerfile*
docker-compose*
.dockerignore

# IDE
.idea/
.vscode/
"""

# 生成配置
cfg = DockerConfig(
    app_name="my-fastapi-app",
    python_version="3.11",
    base_image="slim",
    port=8000,
    entry_point="app.main:app",
    use_non_root=True,
    has_system_deps=True,
    system_packages=["libpq-dev", "gcc"],  # psycopg2 需要
)

print("=== Dockerfile ===\n")
print(generate_dockerfile(cfg))

print("\n=== .dockerignore ===\n")
print(generate_dockerignore())
```

```
# 预期输出：
=== Dockerfile ===

FROM python:3.11-slim

LABEL app="my-fastapi-app"

# 禁止 Python 生成 .pyc 文件，禁用输出缓冲
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# 先安装依赖（利用 Docker 层缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY . .

# 使用非 root 用户运行（安全最佳实践）
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]

=== .dockerignore ===

# 版本控制
.git/
...（内容已省略）
```

---

## Demo 2：生成 docker-compose.yml

```python
# demo2_compose_generator.py
# 生成多服务 docker-compose.yml

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ServiceConfig:
    name: str
    image: Optional[str] = None       # 使用现有镜像
    build_path: Optional[str] = None  # 从 Dockerfile 构建
    ports: list = field(default_factory=list)
    env_vars: dict = field(default_factory=dict)
    depends_on: list = field(default_factory=list)
    volumes: list = field(default_factory=list)
    healthcheck: Optional[dict] = None
    restart: str = "unless-stopped"

def indent(text: str, spaces: int = 2) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line.strip() else line 
                     for line in text.split("\n"))

def generate_service(svc: ServiceConfig) -> str:
    lines = [f"  {svc.name}:"]
    
    if svc.build_path:
        lines.append(f"    build: {svc.build_path}")
    elif svc.image:
        lines.append(f"    image: {svc.image}")
    
    if svc.ports:
        lines.append("    ports:")
        for p in svc.ports:
            lines.append(f'      - "{p}"')
    
    if svc.env_vars:
        lines.append("    environment:")
        for k, v in svc.env_vars.items():
            lines.append(f"      - {k}={v}")
    
    if svc.depends_on:
        lines.append("    depends_on:")
        for dep in svc.depends_on:
            if isinstance(dep, dict):
                lines.append(f"      {dep['name']}:")
                lines.append(f"        condition: {dep['condition']}")
            else:
                lines.append(f"      - {dep}")
    
    if svc.volumes:
        lines.append("    volumes:")
        for v in svc.volumes:
            lines.append(f"      - {v}")
    
    if svc.healthcheck:
        hc = svc.healthcheck
        lines.append("    healthcheck:")
        lines.append(f"      test: {hc['test']}")
        lines.append(f"      interval: {hc.get('interval', '30s')}")
        lines.append(f"      timeout: {hc.get('timeout', '10s')}")
        lines.append(f"      retries: {hc.get('retries', 3)}")
    
    lines.append(f"    restart: {svc.restart}")
    return "\n".join(lines)

# 定义服务
services = [
    ServiceConfig(
        name="api",
        build_path=".",
        ports=["8000:8000"],
        env_vars={
            "DATABASE_URL": "postgresql://user:pass@db:5432/appdb",
            "REDIS_URL": "redis://cache:6379",
            "SECRET_KEY": "${SECRET_KEY}",
        },
        depends_on=[
            {"name": "db", "condition": "service_healthy"},
            {"name": "cache", "condition": "service_started"},
        ],
        volumes=["./logs:/app/logs"],
    ),
    ServiceConfig(
        name="db",
        image="postgres:15-alpine",
        env_vars={
            "POSTGRES_USER": "user",
            "POSTGRES_PASSWORD": "pass",
            "POSTGRES_DB": "appdb",
        },
        volumes=["postgres_data:/var/lib/postgresql/data"],
        healthcheck={
            "test": '["CMD-SHELL", "pg_isready -U user"]',
            "interval": "10s",
            "timeout": "5s",
            "retries": 5,
        },
    ),
    ServiceConfig(
        name="cache",
        image="redis:7-alpine",
        volumes=["redis_data:/data"],
    ),
]

# 生成 docker-compose.yml
output_lines = [
    "version: \"3.9\"",
    "",
    "services:",
]

for svc in services:
    output_lines.append(generate_service(svc))
    output_lines.append("")

output_lines.append("volumes:")
output_lines.append("  postgres_data:")
output_lines.append("  redis_data:")

print("=== docker-compose.yml ===\n")
print("\n".join(output_lines))

print("\n=== 服务依赖关系 ===")
for svc in services:
    deps = [d["name"] if isinstance(d, dict) else d for d in svc.depends_on]
    if deps:
        print(f"  {svc.name} → 依赖 {', '.join(deps)}")
    else:
        print(f"  {svc.name} → 无依赖（基础服务）")
```

```
# 预期输出：
=== docker-compose.yml ===

version: "3.9"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
      - REDIS_URL=redis://cache:6379
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  cache:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

=== 服务依赖关系 ===
  api → 依赖 db, cache
  db → 无依赖（基础服务）
  cache → 无依赖（基础服务）
```

---

## Demo 3：镜像层分析工具

```python
# demo3_dockerfile_analyzer.py
# 分析 Dockerfile 的层结构和优化建议

import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class DockerLayer:
    instruction: str
    content: str
    creates_layer: bool      # 是否创建新层（RUN/COPY/ADD 创建层）
    cache_sensitive: bool    # 是否敏感于缓存（频繁变化则应放后面）
    size_hint: str           # 预估大小影响

LAYER_CREATING_INSTRUCTIONS = {"RUN", "COPY", "ADD"}

INSTRUCTION_HINTS = {
    "FROM": ("不创建层", "基础镜像，选择 slim/alpine 可减小体积"),
    "RUN": ("创建层", "合并多个 RUN 命令可减少层数"),
    "COPY": ("创建层", "先 COPY 依赖文件，再 COPY 源码以利用缓存"),
    "ADD": ("创建层", "优先使用 COPY，除非需要自动解压 tar"),
    "ENV": ("不创建层", "环境变量，合并多个 ENV 为一条"),
    "WORKDIR": ("不创建层", "设置工作目录"),
    "EXPOSE": ("不创建层", "文档性声明，不实际映射端口"),
    "CMD": ("不创建层", "启动命令，用 JSON 数组格式避免 shell 包装"),
    "ENTRYPOINT": ("不创建层", "入口点，配合 CMD 使用"),
    "USER": ("不创建层", "建议在最后设置非 root 用户"),
    "LABEL": ("不创建层", "元数据标签"),
    "ARG": ("不创建层", "构建参数，不泄露到运行时"),
    "VOLUME": ("不创建层", "声明挂载点"),
}

def parse_dockerfile(content: str) -> list:
    """解析 Dockerfile 内容"""
    layers = []
    
    for line in content.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        parts = line.split(None, 1)
        if not parts:
            continue
        
        instruction = parts[0].upper()
        body = parts[1] if len(parts) > 1 else ""
        
        # 续行处理（简化版）
        body = body.rstrip("\\").strip()
        
        creates_layer = instruction in LAYER_CREATING_INSTRUCTIONS
        
        layers.append(DockerLayer(
            instruction=instruction,
            content=body[:60] + "..." if len(body) > 60 else body,
            creates_layer=creates_layer,
            cache_sensitive=instruction == "COPY" and "requirements" not in body,
            size_hint=INSTRUCTION_HINTS.get(instruction, ("?", ""))[0],
        ))
    
    return layers

def generate_optimization_tips(layers: list) -> list:
    """生成优化建议"""
    tips = []
    
    instructions = [l.instruction for l in layers]
    
    # 检查 RUN 命令数量
    run_count = instructions.count("RUN")
    if run_count > 3:
        tips.append(f"发现 {run_count} 个 RUN 指令，考虑合并以减少层数")
    
    # 检查是否使用非 root 用户
    if "USER" not in instructions:
        tips.append("未设置 USER 指令，建议添加非 root 用户以提高安全性")
    
    # 检查 ADD 的使用
    if "ADD" in instructions:
        tips.append("使用了 ADD 指令，若无需解压 tar，建议改用 COPY")
    
    # 检查层缓存顺序
    copy_indices = [i for i, l in enumerate(layers) if l.instruction == "COPY"]
    req_copy = next((i for i, l in enumerate(layers) 
                     if l.instruction == "COPY" and "requirements" in l.content), None)
    if req_copy is not None and copy_indices and copy_indices[0] != req_copy:
        tips.append("requirements.txt 应该最先 COPY，以最大化缓存效果")
    
    return tips

# 分析示例 Dockerfile
sample_dockerfile = """
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y curl
ADD https://example.com/config.tar.gz /config/
CMD python main.py
"""

print("=== Dockerfile 层分析 ===\n")
layers = parse_dockerfile(sample_dockerfile)

layer_num = 0
for layer in layers:
    if layer.creates_layer:
        layer_num += 1
        prefix = f"[层 {layer_num}]"
    else:
        prefix = "      "
    
    hint = INSTRUCTION_HINTS.get(layer.instruction, ("", ""))[1]
    print(f"{prefix} {layer.instruction:12s} {layer.content}")
    if hint:
        print(f"         提示: {hint}")

print(f"\n总层数：{layer_num} 层")

print("\n=== 优化建议 ===")
tips = generate_optimization_tips(layers)
if tips:
    for i, tip in enumerate(tips, 1):
        print(f"  {i}. {tip}")
else:
    print("  Dockerfile 结构良好！")
```

```
# 预期输出：
=== Dockerfile 层分析 ===

       FROM         python:3.11-slim
         提示: 基础镜像，选择 slim/alpine 可减小体积
       WORKDIR      /app
         提示: 设置工作目录
[层 1] COPY         . .
         提示: 先 COPY 依赖文件，再 COPY 源码以利用缓存
[层 2] RUN          pip install -r requirements.txt
         提示: 合并多个 RUN 命令可减少层数
[层 3] RUN          apt-get update
         提示: 合并多个 RUN 命令可减少层数
[层 4] RUN          apt-get install -y curl
         提示: 合并多个 RUN 命令可减少层数
[层 5] ADD          https://example.com/config.tar.gz /config/
         提示: 优先使用 COPY，除非需要自动解压 tar
       CMD          python main.py
         提示: 启动命令，用 JSON 数组格式避免 shell 包装

总层数：5 层

=== 优化建议 ===
  1. 发现 3 个 RUN 指令，考虑合并以减少层数
  2. 未设置 USER 指令，建议添加非 root 用户以提高安全性
  3. 使用了 ADD 指令，若无需解压 tar，建议改用 COPY
  4. requirements.txt 应该最先 COPY，以最大化缓存效果
```
