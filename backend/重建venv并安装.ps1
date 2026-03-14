# 使用 Python 3.11 重建 venv 并安装依赖（无需 Docker）
# 在 backend 目录执行: .\重建venv并安装.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "===== 删除旧 venv =====" -ForegroundColor Cyan
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue

Write-Host "===== 创建新 venv (需已安装 Python 3.10+) =====" -ForegroundColor Cyan
& py -3.11 -m venv venv 2>$null
if ($LASTEXITCODE -ne 0) {
    & python -m venv venv 2>$null
}
if (-not (Test-Path venv\Scripts\python.exe)) {
    Write-Host "  失败。请先安装 Python 3.11: https://www.python.org/downloads/ 并勾选 Add to PATH" -ForegroundColor Red
    exit 1
}

Write-Host "===== 安装依赖 =====" -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Write-Host ""
Write-Host "完成。启动后端: .\venv\Scripts\Activate.ps1; python manage.py runserver 8000" -ForegroundColor Green
