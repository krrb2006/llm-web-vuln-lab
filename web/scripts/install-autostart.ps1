# 安装 / 卸载「登录时自动启动 VulnLab」的快捷方式（不需要管理员权限）
#
#   powershell -File scripts/install-autostart.ps1           安装
#   powershell -File scripts/install-autostart.ps1 -Remove   卸载

param([switch]$Remove)

$ErrorActionPreference = "Stop"
$startup = [Environment]::GetFolderPath("Startup")
$lnkPath = Join-Path $startup "VulnLab 自启.lnk"

if ($Remove) {
    if (Test-Path $lnkPath) { Remove-Item $lnkPath -Force; Write-Host "已移除：$lnkPath" }
    else { Write-Host "未安装" }
    return
}

$webRoot = Split-Path -Parent $PSScriptRoot
$target = Join-Path $PSScriptRoot "auto-start.ps1"
if (-not (Test-Path $target)) { Write-Host "找不到 $target"; exit 1 }

$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath = "powershell.exe"
$lnk.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$target`""
$lnk.WorkingDirectory = $webRoot
$lnk.WindowStyle = 7
$lnk.Description = "登录时启动 VulnLab（Docker + 容器 + 看门狗）"
$lnk.Save()

Write-Host "已安装：$lnkPath"
Write-Host "登录后将自动启动 Docker、拉起容器，并常驻看门狗（每 5 分钟自愈一次）。"
