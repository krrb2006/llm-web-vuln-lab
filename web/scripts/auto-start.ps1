# VulnLab 开机 / 登录自启：拉起 Docker、启动容器，并常驻看门狗
#
# 由"启动"文件夹里的快捷方式调用（见 scripts/install-autostart.ps1），不需要管理员权限。

$ErrorActionPreference = "SilentlyContinue"
$webRoot = Split-Path -Parent $PSScriptRoot
$logFile = Join-Path $PSScriptRoot "startup.log"

function Write-Log([string]$message) {
    try {
        if (-not (Test-Path $logFile)) { New-Item -ItemType File -Path $logFile | Out-Null }
        Add-Content -Path $logFile -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $message") -Encoding UTF8
    } catch { }
}

Set-Location $webRoot
Write-Log "自启：开始"

$dockerOk = $false
try { $null = docker version --format '{{.Server.Version}}' 2>$null; $dockerOk = ($LASTEXITCODE -eq 0) } catch { }
if (-not $dockerOk) {
    $desktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $desktop) { Start-Process $desktop | Out-Null; Write-Log "已启动 Docker Desktop" }
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 3
        try { $null = docker version --format '{{.Server.Version}}' 2>$null; if ($LASTEXITCODE -eq 0) { $dockerOk = $true; break } } catch { }
    }
}
if (-not $dockerOk) { Write-Log "Docker 未就绪，退出"; exit 1 }

docker compose up -d 2>&1 | Out-Null
Write-Log "compose up 完成"

# 若看门狗循环未运行则拉起
$running = Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe'" |
    Where-Object { $_.CommandLine -like "*watchdog.ps1*-Loop*" }
if (-not $running) {
    Start-Process powershell.exe -WindowStyle Hidden -ArgumentList @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", (Join-Path $PSScriptRoot "watchdog.ps1"), "-Loop"
    )
    Write-Log "看门狗循环已启动"
} else {
    Write-Log "看门狗循环已在运行"
}
