# 公网一键部署说明

你只需要：**一台有公网 IP 的云服务器**（阿里云 / 腾讯云 / 华为云等），然后按下面步骤操作即可。我无法直接登录你的服务器，但已经把部署所需都准备好，你在服务器上执行几条命令就能跑起来。

---

## 一、你需要准备什么

1. **一台云服务器**
   - 配置建议：2 核 2G 起，系统选 **Ubuntu 22.04** 或 **CentOS 7+**。
   - 购买后记下：**公网 IP**、**SSH 登录账号密码（或密钥）**。
   - 在云控制台**安全组**里放行：**80**（网页和 API）、**22**（SSH）。

2. **（可选）域名**
   - 有域名可解析到该 IP，后面 App 和网页都用 `https://你的域名`；没有则先用 `http://公网IP` 也可。

### 阿里云 ECS 特别说明

- **安全组**：登录 [阿里云控制台](https://ecs.console.aliyun.com) → 你的 ECS 实例 → 安全组 → 配置规则 → 入方向，新增两条：
  - 端口 **22**（SSH），授权对象 `0.0.0.0/0`
  - 端口 **80**（HTTP），授权对象 `0.0.0.0/0`
- **公网 IP**：在 ECS 实例列表里点你的实例，即可看到「公网 IP」。
- **Git 克隆**：阿里云服务器在国内，直连 GitHub 可能很慢或超时。建议用**方式 B（本地上传）**，或克隆时用镜像：  
  `git clone https://ghproxy.com/https://github.com/2313483829wh-coder/ElderlyCarePlatform.git`

---

## 二、在服务器上执行（一次性）

用 SSH 登录到服务器后，依次执行下面命令（一行一行复制执行即可）。

### 1. 安装 Docker 和 Docker Compose

**Ubuntu / Debian：**

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
```

执行完后**退出 SSH 再重新登录一次**，再继续下面步骤。

**若已安装过 Docker**，可跳过上面，直接执行：

```bash
docker --version
docker compose version
```

有版本输出即可。

### 2. 把项目放到服务器上

任选一种方式：

**方式 A：在服务器上用 Git 克隆**

在服务器上（国内服务器建议用镜像地址，否则可能超时）：

```bash
cd ~
# 使用 GitHub 镜像（国内推荐）
git clone https://ghproxy.com/https://github.com/2313483829wh-coder/ElderlyCarePlatform.git
cd ElderlyCarePlatform
```

**方式 B：本机打包上传**

在你**本地电脑**上（项目根目录）打包并上传：

```bash
# Windows PowerShell 示例（把 你的公网IP 换成实际 IP）：
scp -r . root@你的公网IP:~/ElderlyCarePlatform
```

上传后在服务器上：

```bash
cd ~/ElderlyCarePlatform
```

### 3. 配置环境变量

在服务器上、**项目根目录**（和 `docker-compose.yml` 同级）执行：

```bash
cp deploy/.env.example .env
nano .env
```

在 `.env` 里至少改这两项：

- **DJANGO_SECRET_KEY**：改成随机字符串（可用 `openssl rand -base64 48` 生成）。
- **DJANGO_ALLOWED_HOSTS**：改成你的**公网 IP** 或域名，例如 `42.123.45.67` 或 `api.yourname.com`。

保存退出（nano：Ctrl+O 回车，Ctrl+X）。

### 4. 启动所有服务

仍在项目根目录执行：

```bash
docker compose up -d --build
```

首次会拉镜像、构建镜像，可能要几分钟。完成后用：

```bash
docker compose ps
```

看到 backend、frontend、db、redis、celery 都是 `Up` 即表示成功。

### 5. 获取 API 地址（用于打包 App）

- **若用 IP 访问**：API 基地址为  
  **`http://你的公网IP/api`**  
  例如：`http://42.123.45.67/api`

- **若用域名访问**：API 基地址为  
  **`https://你的域名/api`**（需在服务器或前面再配一层 Nginx 做 HTTPS）

在浏览器打开 `http://你的公网IP`，能看到管理端页面；打开 `http://你的公网IP/api/` 能收到接口响应或 404（说明路由正常），即表示部署成功。

---

## 三、打包 App 并让全国各地的人用

在你**本地电脑**上：

1. 在 `frontend` 目录下创建 **`.env.production`**，内容为（把地址换成上面得到的 API 地址）：

   ```env
   VITE_API_BASE=http://你的公网IP/api
   ```

   若有域名且配了 HTTPS，则用：

   ```env
   VITE_API_BASE=https://你的域名/api
   ```

2. 打包 APK：

   ```bash
   cd frontend
   npm run apk
   ```

3. 把生成的 **app-debug.apk** 发给别人安装；对方只要有网络即可使用，不限于同一 WiFi。

---

## 四、常见问题

- **安全组 / 防火墙**：确保云控制台里该服务器**开放 80 端口**（和 22 用于 SSH）。
- **无法访问**：先在本机 `curl http://你的公网IP` 或浏览器访问，确认能通再在手机 App 里用该地址。
- **管理端登录不上**：按下面顺序排查。
  1. **先创建/重置管理员账号**（在服务器项目根目录执行）：
     ```bash
     docker compose exec backend python manage.py createadmin
     ```
     会创建或重置为 **admin** / **admin123**。若需自定义账号密码：
     ```bash
     docker compose exec backend python manage.py createadmin --username=你的用户名 --password=你的密码
     ```
  2. **仍无法登录时**：在浏览器按 F12 打开开发者工具 → 切到「网络 / Network」→ 再点一次登录，看 **login** 或 **auth** 请求：
     - 若状态码 **401**：用户名或密码错误，再执行一次上面 `createadmin` 后重试。
     - 若状态码 **404** 或 **failed**：接口地址不对，确认访问的是 `http://你的公网IP`（前端会请求同源的 `/api/auth/login/`）。
     - 若状态码 **500**：看服务器后端日志：`docker compose logs backend`，把报错贴给开发者。
  3. **确认后端正常**：在浏览器新开标签访问 `http://你的公网IP/api/`，若看到 `{"status":"ok",...}` 说明 API 可达；若“无法访问”说明请求没到后端。
  4. **管理端一直提示「无法连接服务器」**  
     **原因**：① 旧版前端把 API 写死成绝对地址；② axios 对以 `/` 开头的 URL 会忽略 baseURL，导致请求发到 `/auth/login/` 而不是 `/api/auth/login/`。  
     **一键修复**：在服务器项目根目录执行：
     ```bash
     bash deploy/fix-deploy.sh
     ```
     或手动执行：
     ```bash
     git pull origin main
     docker compose build --no-cache backend frontend
     docker compose up -d
     ```
     然后**清除浏览器缓存**（Ctrl+Shift+Delete 或强刷 Ctrl+F5），再打开 `http://你的公网IP` 用 admin / admin123 登录。  
     若仍不行：在服务器上执行 `curl -s http://127.0.0.1/api/`，应返回 `{"status":"ok",...}`；若这里都失败，说明后端或 nginx 未正常转发。
- **重启服务**：在服务器项目根目录执行 `docker compose restart`。
- **看日志**：`docker compose logs -f backend` 或 `docker compose logs -f frontend`。
- **Docker 构建失败**：项目已配置国内镜像（pip 清华源、npm npmmirror、sharp 镜像）。
  - 先 `docker compose build --no-cache` 清除缓存重试。
  - 分步构建定位：`docker compose build backend`、`docker compose build frontend` 分别执行。
  - 前端 npm 超时：已设 npmmirror + 5 分钟超时 + 5 次重试，多试几次。
  - 后端 pip 超时：已用清华源，可改为阿里云 `https://mirrors.aliyun.com/pypi/simple/`。
- **手机流量无法连接**：运营商常屏蔽 HTTP，需启用 HTTPS。见下方「六、启用 HTTPS」。

---

## 六、启用 HTTPS（手机流量可用）

手机 4G/5G 常屏蔽 HTTP，需 HTTPS 才能用流量访问。

### 推荐：无域名自签名（最简单，有网就能用）

**没有域名**时，用自签名证书，让 App 在手机流量下像普通 App 一样使用。步骤如下：

**1. 本地生成证书（项目根目录）：**

```bash
cd frontend
node scripts/generate-self-signed-cert.js
```

证书会写入 `deploy/certs/` 和 `frontend/android/.../res/raw/server_crt`。若服务器 IP 不是 47.111.26.171，可先设置：`$env:SSL_IP="你的IP"; node scripts/generate-self-signed-cert.js`（PowerShell）。

**2. 上传 certs 到服务器：**

把整个 `deploy/certs/` 目录上传到服务器项目的 `deploy/certs/` 下（脚本已在本地生成好）。

**3. 服务器启动 HTTPS：**

使用自签名专用的 compose 配置（挂载 `deploy/certs`）：

```bash
docker compose -f docker-compose.yml -f deploy/docker-compose.https-self-signed.yml up -d frontend
```

`deploy/nginx-ssl-aliyun.conf` 中 `server_name _` 已匹配任意 IP，无需修改。

**4. 安全组放行 443**，在 `frontend/.env.production` 中写 `VITE_API_BASE=https://47.111.26.171/api`，执行 `npm run apk` 重打 APK。

App 内已配置信任 `res/raw/server_crt`，安装新 APK 后即可用手机流量访问。

### 有域名时：阿里云免费证书

有已备案域名时，可用 **阿里云免费 SSL 证书**。详见 **[deploy/SSL-阿里云免费证书.md](SSL-阿里云免费证书.md)**：

1. 阿里云控制台 → 数字证书管理服务 → 免费证书 → 申请（需域名）
2. 下载 Nginx 格式证书，上传到服务器 `certs/fullchain.pem` 和 `certs/privkey.pem`
3. 执行：`docker compose -f docker-compose.yml -f deploy/docker-compose.https-aliyun.yml up -d frontend`
4. 安全组放行 443，`.env.production` 改为 `https://你的域名/api`，重打 APK

---

## 五、小结

| 你提供 | 我这边已准备好 |
|--------|----------------|
| 一台有公网 IP 的云服务器（能 SSH、开放 80） | 项目里的 Docker 配置、后端 CORS、`deploy/.env.example` |
| 在服务器上：复制 `.env`、改两行、执行 `docker compose up -d` | 一键启动后端 + 前端 + 数据库 + Redis + Celery |
| 本地用 API 地址打 APK 并分发 | 全国各地的人装 App 即可用 |

你不需要把服务器交给我，只要按上述步骤在**你自己的服务器**上执行即可完成部署。
