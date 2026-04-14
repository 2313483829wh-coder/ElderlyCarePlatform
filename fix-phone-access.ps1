# 手机端无法访问时运行此脚本（在项目根目录执行）
# 作用：重新生成证书、同步到 App、重打 APK，确保服务端与 App 使用同一证书
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$ip = "47.111.26.171"
if ($env:SSL_IP) { $ip = $env:SSL_IP }

Write-Host "===== 1. 重新生成证书（服务端 + App 必须一致）=====" -ForegroundColor Cyan
Set-Location frontend
node scripts/generate-self-signed-cert.js
if ($LASTEXITCODE -ne 0) { exit 1 }
Set-Location ..

Write-Host ""
Write-Host "===== 2. 请完成以下操作 =====" -ForegroundColor Yellow
Write-Host "  [服务器] 上传 deploy/certs/ 到服务器的 deploy/certs/"
Write-Host "  [服务器] 执行: docker compose -f docker-compose.yml -f deploy/docker-compose.https-self-signed.yml up -d frontend"
Write-Host "  [服务器] 安全组放行 443 端口"
Write-Host ""
$confirm = Read-Host "已完成服务器部署？按回车继续打包 APK"
Write-Host ""

Write-Host "===== 3. 重新打包 APK =====" -ForegroundColor Cyan
Set-Location frontend
npm run apk
if ($LASTEXITCODE -ne 0) { exit 1 }
Set-Location ..

Write-Host ""
Write-Host "===== 完成 =====" -ForegroundColor Green
Write-Host "APK 位置: frontend\android\app\build\outputs\apk\debug\app-debug.apk"
Write-Host "安装到手机后，用 WiFi 或 4G 均可访问"
Write-Host ""
