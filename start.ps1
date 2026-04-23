# 社区养老平台 - 启动脚本
# 在项目根目录运行: .\start.ps1

$projectRoot = $PSScriptRoot

Write-Host "===== 启动后端 (端口 8000) =====" -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$projectRoot\backend'
if (Test-Path venv\Scripts\Activate.ps1) {
    .\venv\Scripts\Activate.ps1
    python manage.py runserver 8000 --noreload
} else {
    python manage.py runserver 8000 --noreload
}
"@

Start-Sleep -Seconds 2

Write-Host "===== 启动前端 (端口 5173) =====" -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$projectRoot\frontend'
npm run dev
"@

Write-Host ""
Write-Host "两个终端已打开：" -ForegroundColor Green
Write-Host "  后端: http://127.0.0.1:8000"
Write-Host "  管理端: http://localhost:5173/"
Write-Host "  老人端: http://localhost:5173/m/chat"
Write-Host ""
Write-Host "关闭时：分别在两个终端按 Ctrl+C，或直接关闭终端窗口" -ForegroundColor Yellow
