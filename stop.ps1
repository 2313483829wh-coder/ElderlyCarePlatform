# 社区养老平台 - 关闭脚本
# 在项目根目录运行: .\stop.ps1

Write-Host "===== 关闭前后端进程 =====" -ForegroundColor Cyan

$closed = $false

# 关闭占用 5173 的前端
$p5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($p5173) {
    foreach ($pid in $p5173) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host "  已关闭前端 (PID $pid)" -ForegroundColor Green
        $closed = $true
    }
}

# 关闭占用 8000 的后端
$p8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($p8000) {
    foreach ($pid in $p8000) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host "  已关闭后端 (PID $pid)" -ForegroundColor Green
        $closed = $true
    }
}

if (-not $closed) {
    Write-Host "  当前无前后端进程在运行" -ForegroundColor Gray
}

Write-Host "完成" -ForegroundColor Green
