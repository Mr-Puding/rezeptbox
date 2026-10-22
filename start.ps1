# ============================================================
#  RezeptBox – Start-Skript (Schulung "Hacking mit Python")
# ------------------------------------------------------------
#  Macht automatisch:
#   1. Firewall-Regel fuer TCP 8000 oeffnen  (einmal UAC "Ja")
#   2. Server (SQLite) starten -> im Netz erreichbar
#   3. Beim Beenden (Strg+C / Fenster zu) die Regel wieder ENTFERNEN
#
#  Der Server selbst laeuft OHNE Admin-Rechte (wichtig: die App hat
#  absichtliche RCE-Luecken, die nicht als Administrator laufen sollen).
#  Nur das Firewall-Kommando wird kurz elevated ausgefuehrt.
#
#  Aufruf:   powershell -ExecutionPolicy Bypass -File .\start.ps1
# ============================================================

$ErrorActionPreference = 'Stop'
$RuleName = 'RezeptBox 8000 (Schulung)'
$Port     = 8000

Set-Location -Path $PSScriptRoot

# --- 1. Firewall-Regel oeffnen (elevated, idempotent) ---
Write-Host "[RezeptBox] Oeffne Firewall-Regel fuer Port $Port ..." -ForegroundColor Cyan
$addCmd = @"
if (-not (Get-NetFirewallRule -DisplayName '$RuleName' -ErrorAction SilentlyContinue)) {
  New-NetFirewallRule -DisplayName '$RuleName' -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow -Profile Any | Out-Null
}
"@
Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile','-Command',$addCmd
Write-Host "[RezeptBox] Firewall-Regel ist aktiv." -ForegroundColor Green

# --- 2. Server starten; 3. beim Beenden Regel wieder entfernen ---
try {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'WLAN' -ErrorAction SilentlyContinue |
           Select-Object -First 1 -ExpandProperty IPAddress)
    if ($ip) { Write-Host "[RezeptBox] Erreichbar unter:  http://$($ip):$Port" -ForegroundColor Yellow }
    Write-Host "[RezeptBox] Lokal:            http://localhost:$Port" -ForegroundColor Yellow
    Write-Host "[RezeptBox] Zum Beenden: Strg+C  (Firewall-Regel wird dann automatisch entfernt)" -ForegroundColor DarkGray

    $env:DB_BACKEND = 'sqlite'
    python app.py
}
finally {
    Write-Host "`n[RezeptBox] Entferne Firewall-Regel ..." -ForegroundColor Cyan
    $delCmd = "Remove-NetFirewallRule -DisplayName '$RuleName' -ErrorAction SilentlyContinue"
    Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile','-Command',$delCmd
    Write-Host "[RezeptBox] Firewall-Regel entfernt. Fertig." -ForegroundColor Green
}
