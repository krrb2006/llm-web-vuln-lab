# 打印当前可用的访问地址（本机 + 局域网），并检查两个端口是否在线
#
#   powershell -File scripts/show-url.ps1

$ErrorActionPreference = "SilentlyContinue"

function Get-LanIp {
    $candidates = Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } |
        Where-Object { $_.InterfaceAlias -notmatch "WSL|vEthernet|Loopback|VMware|VirtualBox" }
    $wlan = $candidates | Where-Object { $_.InterfaceAlias -match "WLAN|Wi-Fi|无线" } | Select-Object -First 1
    if ($wlan) { return $wlan.IPAddress }
    $first = $candidates | Select-Object -First 1
    return $first.IPAddress
}

function Test-Url([string]$url) {
    try {
        $response = Invoke-RestMethod "$url/api/health" -TimeoutSec 3
        if ($response.status -eq "ok") { return "在线" }
        return "异常"
    } catch { return "未启动" }
}

$lan = Get-LanIp
$rows = @(
    @{ Mode = "Docker 版（推荐分享）"; Local = "http://localhost:8080"; Lan = "http://$lan`:8080" },
    @{ Mode = "原生版（无需 Docker）"; Local = "http://127.0.0.1:8081"; Lan = "http://$lan`:8081" }
)

Write-Host ""
Write-Host "VulnLab 访问地址" -ForegroundColor Cyan
Write-Host ("本机局域网 IP：{0}" -f $lan) -ForegroundColor DarkGray
Write-Host ""

foreach ($row in $rows) {
    $state = Test-Url $row.Local
    Write-Host ("{0}" -f $row.Mode) -ForegroundColor Yellow
    Write-Host ("  本机：{0}   [{1}]" -f $row.Local, $state)
    Write-Host ("  局域网：{0}" -f $row.Lan)
    Write-Host ""
}

Write-Host "提示：" -ForegroundColor DarkGray
Write-Host "  · 局域网访问要求对方连同一个 Wi-Fi（当前多为 tjuwlan，可能禁止终端互访）"
Write-Host "  · 若 8081 别人连不上，需要管理员放行端口："
Write-Host '    netsh advfirewall firewall add rule name="VulnLab 8081" dir=in action=allow protocol=TCP localport=8081' -ForegroundColor DarkGray
Write-Host "  · IP 会随 DHCP 变化，分享前重新运行本脚本即可"
Write-Host ""
