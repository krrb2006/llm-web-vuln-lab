# 一键启动 VulnLab（Windows / PowerShell）
#
# 用法：在 web/ 目录执行  powershell -ExecutionPolicy Bypass -File scripts/start.ps1
# 作用：确认 Docker Desktop 已运行 → 拉起 compose 栈 → 等待健康检查 → 打印访问地址

$ErrorActionPreference = "Stop"
$webRoot = Split-Path -Parent $PSScriptRoot
Set-Location $webRoot

function Test-Docker {
    try { docker version --format '{{.Server.Version}}' 2>$null | Out-Null; return $true }
    catch { return $false }
}

if (-not (Test-Docker)) {
    Write-Host "Docker 引擎未运行，尝试启动 Docker Desktop…" -ForegroundColor Yellow
    $desktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $desktop) { Start-Process $desktop | Out-Null }
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 3
        if (Test-Docker) { break }
    }
}

if (-not (Test-Docker)) {
    Write-Host "Docker 仍未就绪，请手动打开 Docker Desktop 后重试。" -ForegroundColor Red
    exit 1
}

Write-Host "启动容器…" -ForegroundColor Cyan
docker compose up -d

$port = (Select-String -Path ".env" -Pattern '^HTTP_PORT=(\d+)' -ErrorAction SilentlyContinue).Matches.Groups[1].Value
if (-not $port) { $port = "8080" }
$url = "http://localhost:$port"

for ($i = 0; $i -lt 40; $i++) {
    try {
        $health = Invoke-RestMethod "$url/api/health" -TimeoutSec 3
        if ($health.status -eq "ok") {
            Write-Host "已就绪：$url   （演示账号 demo@vulnlab.local / demo-vulnlab-2026）" -ForegroundColor Green
            exit 0
        }
    } catch { Start-Sleep -Seconds 2 }
}

Write-Host "容器已启动，但健康检查未通过，请查看：docker compose logs backend --tail 50" -ForegroundColor Yellow
