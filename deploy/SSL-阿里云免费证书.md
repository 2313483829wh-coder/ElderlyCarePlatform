# 阿里云免费 SSL 证书（国内服务器推荐）

Let's Encrypt 在国内服务器上常无法连接，建议用 **阿里云免费 DV 证书**。

## 前提

- 需有一个**已备案域名**（如 `api.你的域名.com`），并解析到你的服务器 IP（47.111.26.171）
- 阿里云账号

## 步骤

### 1. 申请证书

1. 登录 [阿里云控制台](https://www.aliyun.com) → 搜索「**数字证书管理服务**」或「**SSL 证书**」
2. 免费证书 → 立即购买 → 选择「**DV 单域名**」免费版
3. 证书申请 → 填写域名（如 `elder.你的域名.com` 或 `api.你的域名.com`）
4. DNS 验证：按提示在域名 DNS 解析中添加 TXT 记录
5. 验证通过后，下载证书，选择「**Nginx**」格式

### 2. 上传证书到服务器

下载得到两个文件：`xxx.pem`（证书）和 `xxx.key`（私钥）。

在**项目根目录**创建 `certs` 目录，上传并重命名：

```bash
cd ~/ElderlyCarePlatform
mkdir -p certs
# 把 .pem 上传为 certs/fullchain.pem，.key 上传为 certs/privkey.pem
# 例如用 scp：scp xxx.pem user@服务器:~/ElderlyCarePlatform/certs/fullchain.pem
#          scp xxx.key user@服务器:~/ElderlyCarePlatform/certs/privkey.pem
```

### 3. 使用项目自带的 Nginx 配置

项目已包含 `deploy/nginx-ssl-aliyun.conf`，证书路径已配置为 `/etc/ssl/elderlycare/`，`server_name _` 可匹配任意域名/IP。若需指定域名，可编辑该文件将 `server_name _` 改为 `server_name 你的域名;`。

### 4. 启动 HTTPS

项目已包含 `deploy/docker-compose.https-aliyun.yml`，证书需放在项目根目录的 `certs/` 下。执行：

```bash
docker compose -f docker-compose.yml -f deploy/docker-compose.https-aliyun.yml up -d frontend
```

### 5. 安全组放行 443，并在 App 中使用

- 阿里云安全组 → 入方向 → 添加 443 端口
- `frontend/.env.production` 中设置：`VITE_API_BASE=https://你的域名/api`
- 重新 `npm run apk` 打包
