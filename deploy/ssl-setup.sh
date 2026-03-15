#!/bin/bash
# 为 47.111.26.171.nip.io 获取免费 HTTPS 证书（nip.io 自动解析到你的 IP）
# 在服务器项目根目录执行：bash deploy/ssl-setup.sh

set -e
DOMAIN="47.111.26.171.nip.io"
cd "$(dirname "$0")/.."

echo ">>> 1. 创建 certbot 所需目录..."
mkdir -p certbot/www
chmod -R 755 certbot

echo ">>> 2. 临时停止 frontend（释放 80 端口）..."
docker compose stop frontend 2>/dev/null || true
sleep 2

echo ">>> 3. 用 certbot 获取证书（需已安装 certbot）..."
if ! command -v certbot &>/dev/null; then
  echo "请先安装 certbot: sudo apt install certbot"
  exit 1
fi
sudo certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos --email admin@example.com

echo ">>> 4. 启动服务并启用 HTTPS..."
docker compose -f docker-compose.yml -f deploy/docker-compose.https.yml up -d frontend

echo ""
echo ">>> 5. 完成！"
echo "    请用 https://$DOMAIN 访问。"
echo "    在 frontend/.env.production 中设置：VITE_API_BASE=https://$DOMAIN/api"
echo "    然后重新打包 APK，即可在手机流量下使用。"
