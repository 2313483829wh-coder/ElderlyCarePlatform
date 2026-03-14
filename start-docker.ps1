# 使用 Docker 启动后端（数据库 + Redis + Django）
# 请先确保 Docker Desktop 已启动，然后双击此脚本或在终端执行: .\start-docker.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "===== Docker 启动后端 (db + redis + backend) =====" -ForegroundColor Cyan
docker compose up db redis backend -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "启动失败。请确认 Docker Desktop 已运行，且在本机终端中执行: docker compose up db redis backend -d" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "后端已启动，首次会拉镜像并初始化数据库，约 1~3 分钟。" -ForegroundColor Green
Write-Host "  API: http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host "  前端代理 /api -> 8000，刷新页面即可。" -ForegroundColor Gray
Write-Host ""
Write-Host "查看日志: docker compose logs -f backend" -ForegroundColor Yellow
Write-Host "停止: docker compose down" -ForegroundColor Yellow
