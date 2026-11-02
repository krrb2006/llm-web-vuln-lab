# VulnLab 原生模式：不依赖 Docker（FastAPI + SQLite + 预构建前端）
#
#   powershell -File scripts/run-native.ps1
#
# 首次运行会创建本地虚拟环境并安装依赖，之后启动秒开。
# 默认端口 8081（8080 留给 Docker 版），可用 -Port 指定。

param(
    [int]$Port = 8081,
    [string]$Bind = "127.0.0.1",   # 想在局域网访问用 -Bind 0.0.0.0（还需放行防火墙）
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$webRoot = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $webRoot "backend"
$static = Join-Path $webRoot "static"
$venv = Join-Path $webRoot ".venv-native"
$dataDir = Join-Path $webRoot "data"

function Resolve-Python {
    foreach ($candidate in @("python", "py")) {
        try {
            $version = & $candidate --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                if ($candidate -eq "py") { return @("py", "-3") }
                return @("python")
            }
        } catch { }
    }
    throw "找不到 Python 3.10+，请先安装 Python 并勾选 Add to PATH"
}

if (-not (Test-Path (Join-Path $static "index.html"))) {
    Write-Host "缺少预构建前端 static/，请先运行 npm run build 并复制到 static/。" -ForegroundColor Red
    exit 1
}

$python = @(Resolve-Python)
$pythonExe = $venv + "\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "首次运行：创建虚拟环境 $venv …" -ForegroundColor Cyan
    if ($python.Length -eq 2) { & $python[0] $python[1] -m venv $venv } else { & $python[0] -m venv $venv }
}

$dependenciesReady = $false
if (Test-Path $pythonExe) {
    # 缺少模块是首次运行的正常状态；临时关闭 Stop，避免把导入失败当成脚本异常。
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $pythonExe -c "import fastapi, sqlalchemy, uvicorn" 2>$null | Out-Null
    $dependenciesReady = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $previousErrorActionPreference
}
if (-not $dependenciesReady) {
    Write-Host "安装/修复依赖（首次约 1-2 分钟）…" -ForegroundColor Cyan
    & $pythonExe -m pip install --upgrade pip --quiet
    & $pythonExe -m pip install -r (Join-Path $backend "requirements.txt") --quiet
    if ($LASTEXITCODE -ne 0) {
        throw "Python 依赖安装失败，请检查网络后重试。"
    }
}

if (-not (Test-Path $dataDir)) { New-Item -ItemType Directory -Path $dataDir | Out-Null }

# 本地密钥：首次生成后复用，避免每次重启都让登录失效
$envFile = Join-Path $webRoot "local-native.env"
if (-not (Test-Path $envFile)) {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $secret = -join ($bytes | ForEach-Object { $_.ToString("x2") })
    Set-Content -Path $envFile -Value "JWT_SECRET=$secret" -Encoding UTF8
}

$jwt = (Get-Content $envFile | Where-Object { $_ -match '^JWT_SECRET=' }) -replace '^JWT_SECRET=', ''

$env:DATABASE_URL = "sqlite:///" + ((Join-Path $dataDir "vulnlab.db") -replace '\\', '/')
$env:DATA_DIR = $dataDir
$env:FRONTEND_DIR = $static
$env:JWT_SECRET = $jwt
$env:SEED_DEMO = "true"
$env:APP_ENV = "native"

Set-Location $backend
$url = "http://127.0.0.1:$Port"

if (-not $NoBrowser) {
    Start-Job -ScriptBlock {
        param($u)
        for ($i = 0; $i -lt 40; $i++) {
            Start-Sleep -Seconds 1
            try { Invoke-WebRequest "$u/api/health" -TimeoutSec 2 -UseBasicParsing | Out-Null; Start-Process $u; break } catch { }
        }
    } -ArgumentList $url | Out-Null
}

Write-Host ""
Write-Host "VulnLab 原生模式启动中：$url" -ForegroundColor Green
Write-Host "演示账号 demo@vulnlab.local / demo-vulnlab-2026；数据在 $dataDir" -ForegroundColor DarkGray
if ($Bind -ne "127.0.0.1") {
    Write-Host "已监听 $Bind，局域网地址形如 http://<本机IP>:$Port（需放行防火墙入站）" -ForegroundColor DarkGray
}
Write-Host "按 Ctrl+C 停止（不依赖 Docker，关掉窗口即退出）" -ForegroundColor DarkGray
Write-Host ""

& $pythonExe -m uvicorn app.main:app --host $Bind --port $Port
