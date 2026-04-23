#!/bin/bash
# 自动修复部署：拉最新代码、重建前后端，并自动保留 HTTPS 覆盖配置
set -e

cd "$(dirname "$0")/.."

COMPOSE_ARGS=(-f docker-compose.yml)
DEPLOY_MODE="http"

if [ -f "deploy/certs/fullchain.pem" ] && [ -f "deploy/certs/privkey.pem" ] && [ -f "deploy/docker-compose.https-self-signed.yml" ]; then
  COMPOSE_ARGS+=(-f deploy/docker-compose.https-self-signed.yml)
  DEPLOY_MODE="https-self-signed"
elif [ -f "certs/fullchain.pem" ] && [ -f "certs/privkey.pem" ] && [ -f "deploy/docker-compose.https-aliyun.yml" ]; then
  COMPOSE_ARGS+=(-f deploy/docker-compose.https-aliyun.yml)
  DEPLOY_MODE="https-aliyun"
fi

echo ">>> 拉取最新代码..."
git pull origin main

echo ">>> 当前部署模式: ${DEPLOY_MODE}"
echo ">>> 重建 backend 和 frontend（无缓存）..."
docker compose "${COMPOSE_ARGS[@]}" build --no-cache backend frontend

echo ">>> 重启全部服务..."
docker compose "${COMPOSE_ARGS[@]}" up -d

echo ">>> 等待 backend 启动（约 30 秒）..."
sleep 30

echo ">>> 检查 API 是否正常..."
if [[ "${DEPLOY_MODE}" == https-* ]]; then
  curl -ks https://127.0.0.1/api/ | head -1
else
  curl -s http://127.0.0.1/api/ | head -1
fi

echo ""
if [[ "${DEPLOY_MODE}" == https-* ]]; then
  echo ">>> 完成。当前按 HTTPS 模式启动，手机 App 和公网网页可继续使用。"
else
  echo ">>> 完成。当前按 HTTP 模式启动，如需手机流量访问，请启用 HTTPS。"
fi
