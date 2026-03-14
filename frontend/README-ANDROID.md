# 老人端 Android 应用打包说明

老人端（/m/* 路由）已通过 **Capacitor** 打包为 Android 应用，安装后打开即进入「健康助手」对话页。

## 环境要求

- Node.js 18+
- JDK 17（Android 开发推荐）
- **Android SDK**（必须）  
  - 安装 [Android Studio](https://developer.android.com/studio) 后会自带 SDK，默认路径：  
    - Windows: `C:\Users\你的用户名\AppData\Local\Android\Sdk`  
    - macOS: `~/Library/Android/sdk`
- 已配置好的后端 API 地址（打包正式版时必填）

### 若报错「SDK location not found」

任选其一即可：

1. **设置环境变量**（推荐）  
   - 新建系统/用户变量 `ANDROID_HOME`，值为 SDK 目录（如上路径）。
2. **写 local.properties**  
   - 在 `frontend/android/` 下新建 `local.properties`（该文件已在 .gitignore，不会提交），内容示例：  
     - Windows: `sdk.dir=C\:\\Users\\你的用户名\\AppData\\Local\\Android\\Sdk`  
     - macOS/Linux: `sdk.dir=/Users/你的用户名/Library/Android/sdk`  
   - 路径中的反斜杠要写成 `\\`。

## 1. 安装依赖

在项目根目录下：

```bash
cd frontend
npm install
```

## 2. 配置后端地址（正式版必做）

在真机或发布版中，应用需要访问真实后端。在 `frontend` 目录下创建 `.env` 或 `.env.production`，例如：

```env
VITE_API_BASE=https://你的服务器域名/api
```

例如后端部署在 `https://api.example.com`，则：

```env
VITE_API_BASE=https://api.example.com/api
```

不设置时，请求会发往相对路径 `/api`，仅适合与网页同域或本地调试。

## 3. 构建并同步到 Android

```bash
npm run build:app
```

会依次执行：

- `vite build`：打包前端到 `dist/`
- `npx cap sync`：把 `dist/` 同步到 `android/` 工程

## 4. 生成 APK

### 方式一：命令行打 Debug 包（无需 Android Studio）

在 **frontend** 目录下：

**Windows：**

```bash
npm run apk
```

或分步执行：

```bash
npm run build:app
cd android
.\gradlew.bat assembleDebug
```

**macOS / Linux：**

```bash
npm run build:app
cd android && ./gradlew assembleDebug
```

生成的 APK 路径：

- `frontend/android/app/build/outputs/apk/debug/app-debug.apk`

安装到手机即可测试（需允许「未知来源」安装）。

### 方式二：用 Android Studio 打 Release 包（可签名上架）

1. 用 Android Studio 打开 `frontend/android` 目录。
2. 菜单 **Build → Generate Signed Bundle / APK**，选择 APK，配置签名。
3. 选择 **release**，生成已签名的 `app-release.apk`。

## 5. 在模拟器或真机上运行

```bash
npm run android
```

会先执行 `build:app`，再打开 Android Studio 中的 Android 工程。在 Android Studio 里选择设备（模拟器或真机）点击 Run 即可。

## 脚本说明（package.json）

| 命令 | 说明 |
|------|------|
| `npm run build` | 仅构建前端到 `dist/` |
| `npm run build:app` | 构建前端并执行 `cap sync` 同步到原生工程 |
| `npm run android` | 构建 + 同步 + 用 Android Studio 打开工程 |
| `npm run apk` | 构建 + 同步 + 打 Debug APK（Windows 下用 gradlew.bat） |

## 注意事项

1. **首次打包**：若未执行过 `npx cap add android`，当前仓库已包含 `android` 目录，可直接使用；若缺失，在 frontend 下执行 `npx cap add android` 再按上述步骤操作。
2. **网络权限**：`AndroidManifest.xml` 已声明 `INTERNET`，可访问外网接口。
3. **HTTP 后端**：已开启 `usesCleartextTraffic="true"`，可访问 HTTP 接口（仅建议内网或测试使用，正式环境请用 HTTPS）。
4. **老人端入口**：应用启动后由路由自动跳转到 `/m/chat`（健康助手），无需再选管理端或老人端。
