#!/bin/bash
# python-learning 免登录版部署脚本（在 ECS 上执行）
#
# 关键事实（探查所得）：
#   - 后端由 PM2 托管：python-learning-workbench-api
#   - 必须用 /usr/bin/python3.11；系统默认 python3 是 3.6.8，装不了 FastAPI
#   - pm2 不认 --app-dir（那是 uvicorn 的参数，不是 pm2 的），故用 ecosystem + PYTHONPATH
#   - 持久化：python-workbench.db 与 node_modules 必须保留
set -eo pipefail

SITE_DIR='/www/wwwroot/python-learning-workbench'
PY=/usr/bin/python3.11
PM2_NAME=python-learning-workbench-api
BACKEND_PORT=8004

echo "=== 0. 前置检查 ==="
[ -x "$PY" ] || { echo "❌ $PY 不存在"; exit 1; }
"$PY" --version

echo "=== 1. 下载源码 ==="
TAR=/tmp/_python-learning.tar.gz
rm -f "$TAR"
http=$(curl -sSL -o "$TAR" -w '%{http_code}' --max-time 240 \
  "https://codeload.github.com/webxiongda/python-learning/tar.gz/refs/heads/main")
[ "$http" = "200" ] || { echo "❌ 下载失败 HTTP=$http"; exit 1; }
tar -tzf "$TAR" >/dev/null && echo "tar OK ($(du -h $TAR | cut -f1))"

echo "=== 2. 备份并替换源码（保留 db 与 node_modules）==="
BAK="${SITE_DIR}-bak-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BAK"
cd "$SITE_DIR"
for item in backend/app src index.html package.json package-lock.json tsconfig.app.json tsconfig.json tsconfig.node.json; do
  [ -e "$item" ] && cp -a "$item" "$BAK/" 2>/dev/null || true
done
echo "已备份 -> $BAK"

KEEP=/tmp/_py_keep
rm -rf "$KEEP"; mkdir -p "$KEEP"
[ -f python-workbench.db ] && mv python-workbench.db "$KEEP/" || true
[ -d node_modules ] && mv node_modules "$KEEP/" || true
rm -rf backend src dist
tar -xzf "$TAR" --strip-components=1
rm -f "$TAR"
[ -f "$KEEP/python-workbench.db" ] && mv "$KEEP/python-workbench.db" ./ || true
[ -d "$KEEP/node_modules" ] && mv "$KEEP/node_modules" ./ || true
rm -rf "$KEEP"

echo "免登录逻辑: $(grep -q AUTO_LOGIN_USERNAME backend/app/auth.py && echo YES || echo '❌ 缺失')"
echo "db 保留:    $([ -f python-workbench.db ] && echo YES || echo '❌ 缺失')"

echo "=== 3. 安装后端依赖 ==="
"$PY" -m pip install -q -r backend/requirements.txt 2>&1 | grep -v "WARNING: Running pip" | tail -3
"$PY" -c "import fastapi, sqlalchemy, uvicorn; print('依赖 OK, fastapi', fastapi.__version__)"

echo "=== 4. 构建前端 ==="
export PATH=/usr/local/bin:$PATH
[ -d node_modules ] || npm install --no-audit --no-fund 2>&1 | tail -3
npm run build 2>&1 | tail -8

echo "=== 5. 重启 PM2 后端 ==="
cat > "$SITE_DIR/ecosystem.config.cjs" << 'EOF'
module.exports = {
  apps: [
    {
      name: 'python-learning-workbench-api',
      script: '/usr/bin/python3.11',
      args: '-m uvicorn app.main:app --host 127.0.0.1 --port 8004',
      interpreter: 'none',
      cwd: '/www/wwwroot/python-learning-workbench',
      env: {
        PYTHONPATH: '/www/wwwroot/python-learning-workbench/backend',
        PYTHONUNBUFFERED: '1'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '400M'
    }
  ]
};
EOF

pm2 delete "$PM2_NAME" 2>/dev/null || true
pm2 start "$SITE_DIR/ecosystem.config.cjs" 2>&1 | tail -5
pm2 save --force 2>&1 | tail -1

echo "=== 6. 等待就绪并做免登录验证（无 Authorization 头）==="
for i in $(seq 1 15); do
  sleep 4
  code=$(curl -s -m 4 -o /dev/null -w "%{http_code}" "http://127.0.0.1:${BACKEND_PORT}/api/health" 2>/dev/null || echo 000)
  echo "  探测 ${i}: $code"
  [ "$code" = "200" ] && break
  [ "$i" = "15" ] && { echo "❌ 未就绪"; pm2 logs "$PM2_NAME" --lines 30 --nostream; exit 1; }
done

echo -n "health  : "; curl -s -m 8 "http://127.0.0.1:${BACKEND_PORT}/api/health"; echo ""
echo -n "auth/me : "; curl -s -m 8 "http://127.0.0.1:${BACKEND_PORT}/api/auth/me"; echo ""
for p in summary chapters; do
  printf "  %-12s %s\n" "$p:" "$(curl -s -m 8 -o /dev/null -w '%{http_code}' "http://127.0.0.1:${BACKEND_PORT}/api/$p")"
done

echo ""
echo "如需回滚：cp -a '$BAK/backend' '$SITE_DIR/backend' && pm2 restart $PM2_NAME"
echo "=== PYTHON-LEARNING DEPLOY DONE ==="