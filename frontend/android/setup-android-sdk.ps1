# 将 Android SDK 下载到 A 盘并配置 local.properties
# 若没有 A 盘，把下面 $SdkRoot 改成 C:\Android 或 D:\Android 再运行

$ErrorActionPreference = "Stop"
$SdkRoot = "A:\Android\sdk"
$CmdlineToolsZip = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
$TempZip = "$env:TEMP\android-cmdline-tools.zip"

Write-Host "Android SDK 将安装到: $SdkRoot" -ForegroundColor Cyan
Write-Host ""

# 检查/创建 A 盘（若不存在则提示并退出）
$drive = Split-Path $SdkRoot -Qualifier
if (-not (Test-Path $drive)) {
    Write-Host "错误: 未找到 $drive 盘。请把本脚本里的 `$SdkRoot 改成 C:\Android\sdk 或 D:\Android\sdk 后重试。" -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Force -Path $SdkRoot | Out-Null

# 下载命令行工具
$cmdlineDir = Join-Path $SdkRoot "cmdline-tools"
$latestDir = Join-Path $cmdlineDir "latest"
if (Test-Path $latestDir) {
    Write-Host "已存在 cmdline-tools，跳过下载。若需重装请先删除 $latestDir" -ForegroundColor Yellow
} else {
    Write-Host "正在下载 Android 命令行工具（约 146MB）..." -ForegroundColor Green
    try {
        Invoke-WebRequest -Uri $CmdlineToolsZip -OutFile $TempZip -UseBasicParsing
    } catch {
        Write-Host "下载失败: $_" -ForegroundColor Red
        exit 1
    }
    Write-Host "解压到 $latestDir ..." -ForegroundColor Green
    New-Item -ItemType Directory -Force -Path $latestDir | Out-Null
    Expand-Archive -Path $TempZip -DestinationPath $env:TEMP\android-unzip -Force
    $unzipRoot = "$env:TEMP\android-unzip"
    $inner = Get-ChildItem $unzipRoot -Directory | Select-Object -First 1
    if ($inner.Name -eq "cmdline-tools") {
        Copy-Item -Path "$($inner.FullName)\*" -Destination $latestDir -Recurse -Force
    } else {
        Copy-Item -Path "$unzipRoot\*" -Destination $latestDir -Recurse -Force
    }
    Remove-Item $TempZip -Force -ErrorAction SilentlyContinue
    Remove-Item $unzipRoot -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "命令行工具已安装。" -ForegroundColor Green
}

$sdkmanager = Join-Path $latestDir "bin\sdkmanager.bat"
if (-not (Test-Path $sdkmanager)) {
    Write-Host "错误: 未找到 sdkmanager.bat，请检查解压路径。" -ForegroundColor Red
    exit 1
}

# 接受许可（非交互）
Write-Host "接受 SDK 许可..." -ForegroundColor Green
("y`n" * 20) | & $sdkmanager --sdk_root=$SdkRoot --licenses 2>&1 | Out-Null

# 安装 platform-tools、platforms、build-tools（使用 --install 参数）
Write-Host "安装 platform-tools、platforms;android-36、build-tools;36.0.0 ..." -ForegroundColor Green
& cmd /c "`"$sdkmanager`" --sdk_root=`"$SdkRoot`" --install platform-tools platforms;android-36 build-tools;36.0.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "尝试 platforms;android-35、build-tools;35.0.0 ..." -ForegroundColor Yellow
    & cmd /c "`"$sdkmanager`" --sdk_root=`"$SdkRoot`" --install platform-tools platforms;android-35 build-tools;35.0.0"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "安装失败。请手动运行: & `"$sdkmanager`" --sdk_root=`"$SdkRoot`" --list" -ForegroundColor Red
        exit 1
    }
}

# 写入 local.properties（路径中 \ 写为 \\）
$sdkDirEscaped = $SdkRoot -replace '\\', '\\'
$localProps = Join-Path $PSScriptRoot "local.properties"
Set-Content -Path $localProps -Value "sdk.dir=$sdkDirEscaped" -Encoding UTF8
Write-Host "已写入 $localProps" -ForegroundColor Green

# 设置当前用户环境变量 ANDROID_HOME
[Environment]::SetEnvironmentVariable("ANDROID_HOME", $SdkRoot, "User")
Write-Host "已设置用户环境变量 ANDROID_HOME = $SdkRoot" -ForegroundColor Green
Write-Host ""
Write-Host "完成。请关闭并重新打开终端后，在 frontend 目录执行: npm run apk" -ForegroundColor Cyan
