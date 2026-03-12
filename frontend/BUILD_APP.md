# 老人端 App 构建说明

本项目使用 [Capacitor](https://capacitorjs.com/) 将老人端（`/m/chat` 等）打包为 iOS 和 Android 原生应用。

## 环境要求

- **Node.js** 18+
- **Android APK**：Windows/Mac/Linux，需安装 [Android Studio](https://developer.android.com/studio) 及 Android SDK
- **iOS IPA**：**仅 Mac**，需安装 [Xcode](https://developer.apple.com/xcode/) 和 Apple Developer 账号

## 1. 配置 API 地址

App 内需要配置实际可访问的后端 API 地址。编辑 `frontend/.env.production`：

```env
# 本地测试：使用电脑局域网 IP（手机需与电脑在同一 WiFi）
VITE_API_BASE=http://192.168.1.100:8000/api

# 生产环境：使用正式域名
# VITE_API_BASE=https://api.yourdomain.com/api
```

> 请将 `192.168.1.100` 替换为你的电脑在局域网中的实际 IP（可用 `ipconfig` 查看）。

## 2. 构建 Web 资源

```bash
cd frontend
npm run build
```

## 3. 同步到原生项目

```bash
npx cap sync
```

## 4. 生成 Android APK

### 方式一：命令行（Windows 使用 `gradlew.bat`）

```bash
cd android
.\gradlew.bat assembleDebug
```

输出路径：`android/app/build/outputs/apk/debug/app-debug.apk`

### 方式二：Android Studio

```bash
npx cap open android
```

在 Android Studio 中：**Build → Build Bundle(s) / APK(s) → Build APK(s)**

### 正式发布（Release 签名）

需配置签名，参考 [Android 应用签名](https://developer.android.com/studio/publish/app-signing)。

```bash
.\gradlew.bat assembleRelease
```

输出：`android/app/build/outputs/apk/release/app-release.apk`

## 5. 生成 iOS IPA

**必须在 Mac 上执行**，并安装 Xcode。

```bash
npx cap open ios
```

在 Xcode 中：

1. 选择 **Product → Archive**
2. 配置签名和证书（需 Apple Developer 账号）
3. 导出 IPA 或上传 App Store

## 6. 快捷脚本

`package.json` 中可添加：

```json
"scripts": {
  "build:app": "npm run build && npx cap sync",
  "android": "npm run build:app && npx cap open android",
  "ios": "npm run build:app && npx cap open ios"
}
```

## 注意事项

1. **API 地址**：首次打包前务必修改 `.env.production` 中的 `VITE_API_BASE`，否则 App 可能无法访问后端。
2. **HTTP 明文**：默认已允许 HTTP（`usesCleartextTraffic`），便于本地调试；正式环境建议使用 HTTPS。
3. **iOS 限制**：无 Mac 时无法生成 iOS 安装包，可使用云构建服务（如 Ionic Appflow、Codemagic 等）。
