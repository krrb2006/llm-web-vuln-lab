# VulnLab 看门狗（单次 / 循环）
#
# 单次：  powershell -File scripts/watchdog.ps1
# 循环：  powershell -File scripts/watchdog.ps1 -Loop        （每 5 分钟检查一次）
#
# 正常情况下什么都不做；异常时自动拉起 Docker Desktop 与 compose 栈。

param(
    [switch]$Loop,
    [int]$IntervalSeconds = 300
)

$ErrorActionPreference = "SilentlyContinue"
$webRoot = Split-Path -Parent $PSScriptRoot
$logFile = Join-Path $PSScriptRoot "watchdog.log"
$port = "8080"
$envPath = Join-Path $webRoot ".env"
if (Test-Path $envPath) {
    $configuredPort = (Select-String -Path $envPath -Pattern '^HTTP_PORT=(\d+)' -ErrorAction SilentlyContinue).Matches.Groups[1].Value
    if ($configuredPort) { $port = $configuredPort }
}
$healthUrl = "http://localhost:$port/api/health"

function Write-Log([string]$message) {
    try {
        if (-not (Test-Path $logFile)) { New-Item -ItemType File -Path $logFile | Out-Null }
        if ((Get-Item $logFile).Length -gt 1MB) { Remove-Item $logFile -Force }
        Add-Content -Path $logFile -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $message") -Encoding UTF8
    } catch { }
}

function Test-Site {
    try { return ((Invoke-RestMethod $healthUrl -TimeoutSec 4).status -eq "ok") } catch { return $false }
}

function Test-Docker {
    try { $null = docker version --format '{{.Server.Version}}' 2>$null; return ($LASTEXITCODE -eq 0) } catch { return $false }
}

function Repair-Site {
    Write-Log "站点不可用，开始恢复"
    if (-not (Test-Docker)) {
        Write-Log "Docker 引擎未运行，启动 Docker Desktop"
        $desktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if (Test-Path $desktop) { Start-Process $desktop | Out-Null }
        for ($i = 0; $i -lt 40; $i++) {
            Start-Sleep -Seconds 3
            if (Test-Docker) { break }
        }
    }
    if (-not (Test-Docker)) { Write-Log "Docker 仍不可用，本次放弃"; return $false }

    Set-Location $webRoot
    docker compose up -d 2>&1 | Out-Null
    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Seconds 3
        if (Test-Site) { Write-Log "恢复成功：$healthUrl"; return $true }
    }
    Write-Log "已尝试启动，但健康检查仍未通过，请查看 docker compose logs"
    return $false
}

if ($Loop) {
    # 单实例：已有一个循环在跑时直接退出
    $mutex = New-Object System.Threading.Mutex($false, "Global\VulnLabWatchdog")
    if (-not $mutex.WaitOne(0)) { exit 0 }
    Write-Log "看门狗循环启动，间隔 ${IntervalSeconds}s"
    while ($true) {
        if (-not (Test-Site)) { Repair-Site | Out-Null }
        Start-Sleep -Seconds $IntervalSeconds
    }
}

if (Test-Site) { exit 0 }
Repair-Site | Out-Null
exit 0
