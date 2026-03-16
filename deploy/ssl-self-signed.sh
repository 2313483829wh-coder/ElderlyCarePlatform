#!/bin/bash
# 自签名证书：无域名也能用 HTTPS，让手机流量可访问
# 在服务器项目根目录执行：bash deploy/ssl-self-signed.sh
# 你的公网 IP 会作为参数，如：bash deploy/ssl-self-signed.sh 47.111.26.171

set -e
IP="${1:-47.111.26.171}"
cd "$(dirname "$0")/.."

echo ">>> 为 IP $IP 生成自签名证书（有效期 10 年）..."
mkdir -p certs
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout certs/privkey.pem -out certs/fullchain.pem \
  -subj "/CN=$IP" -addext "subjectAltName=IP:$IP"

echo ">>> 证书已生成到 certs/"
echo ">>> 启动 HTTPS 服务..."
docker compose -f docker-compose.yml -f deploy/docker-compose.https-aliyun.yml up -d frontend

echo ""
echo ">>> 完成！"
echo "    1. 安全组放行 443 端口"
echo "    2. 把 certs/fullchain.pem 复制到本地 frontend/android/app/src/main/res/raw/server.crt"
echo "    3. frontend/.env.production 改为：VITE_API_BASE=https://$IP/api"
echo "    4. 重新 npm run apk 打包，安装新 APK 即可用流量访问"
