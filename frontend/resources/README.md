# App 图标资源

将你的 **App 图标** 放到此目录，文件名为 `icon.png`。

## 要求

- **尺寸**：建议 1024×1024 像素
- **格式**：PNG，透明背景或纯色背景均可

## 使用步骤

1. 把你的图标图片复制到本目录，命名为 `icon.png`
2. 在 frontend 目录下执行：
   ```bash
   npm run generate:icons
   ```
3. 然后按正常流程打 APK：
   ```bash
   npm run apk
   ```

`generate:icons` 会将 `icon.png` 生成 Android 所需的各尺寸图标并覆盖现有图标。
