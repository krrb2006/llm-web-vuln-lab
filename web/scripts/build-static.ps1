# 重新生成 web/static（原生模式用的预构建前端）
#
#   powershell -File scripts/build-static.ps1
#
# 需要 Node.js 18+ 与 npm。Docker 模式不需要这一步（镜像里会自己构建）。

$ErrorActionPreference = "Stop"
$webRoot = Split-Path -Parent $PSScriptRoot
$frontend = Join-Path $webRoot "frontend"
$static = Join-Path $webRoot "static"

Push-Location $frontend
try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "安装前端依赖…" -ForegroundColor Cyan
        npm install --no-audit --no-fund
    }
    Write-Host "构建前端…" -ForegroundColor Cyan
    npm run build
}
finally {
    Pop-Location
}

if (Test-Path $static) { Remove-Item $static -Recurse -Force }
New-Item -ItemType Directory -Path $static | Out-Null
Copy-Item -Path (Join-Path $frontend "dist\*") -Destination $static -Recurse -Force

Write-Host "已更新：$static" -ForegroundColor Green
