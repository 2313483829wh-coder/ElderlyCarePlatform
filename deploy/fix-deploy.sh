#!/bin/bash
# 彻底修复「无法连接服务器」：拉最新代码、重建前后端、重启
set -e
cd "$(dirname "$0")/.."
echo ">>> 拉取最新代码..."
git pull origin main
echo ">>> 重建 backend 和 frontend（无缓存）..."
docker compose build --no-cache backend frontend
echo ">>> 重启全部服务..."
docker compose up -d
echo ">>> 等待 backend 启动（约 30 秒）..."
sleep 30
echo ">>> 检查 API 是否正常..."
curl -s http://127.0.0.1/api/ | head -1
echo ""
echo ">>> 完成。请清除浏览器缓存（Ctrl+Shift+Delete）后，打开 http://你的公网IP 用 admin/admin123 登录。"
