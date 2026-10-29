# ============================================================
#  RezeptBox - Stop-Skript (Schulung "Hacking mit Python")
# ------------------------------------------------------------
#  Macht automatisch:
#   1. Alle app.py-Python-Prozesse beenden (Parent + Reloader-Child)
#   2. Firewall-Regel fuer TCP 8000 ENTFERNEN, falls noch vorhanden
#      (elevated, einmal UAC "Ja")
#
#  Wird auch vom SessionEnd-Hook in .claude/settings.local.json
#  aufgerufen, damit der Port nach der Claude-Session wieder zu ist.
#
#  Aufruf:   powershell -ExecutionPolicy Bypass -File .\stop.ps1
# ============================================================

$RuleName = 'RezeptBox 8000 (Schulung)'

# --- 1. Server-Prozesse beenden ---
$procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
         Where-Object { $_.CommandLine -like '*app.py*' }
foreach ($p in $procs) {
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}
if ($procs) { Write-Host "[RezeptBox] Server beendet." -ForegroundColor Green }

# --- 2. Firewall-Regel entfernen ---
# Laeuft start.ps1 noch, entfernt dessen finally-Block die Regel selbst
# (eigene UAC-Abfrage). Darum kurz warten, um keine zweite Abfrage auszuloesen.
$deadline = (Get-Date).AddSeconds(20)
while ((Get-Date) -lt $deadline -and
       (Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue)) {
    Start-Sleep -Seconds 1
}
if (Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue) {
    Write-Host "[RezeptBox] Entferne Firewall-Regel ..." -ForegroundColor Cyan
    $delCmd = "Remove-NetFirewallRule -DisplayName '$RuleName' -ErrorAction SilentlyContinue"
    Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile','-Command',$delCmd
}
Write-Host "[RezeptBox] Port 8000 ist zu." -ForegroundColor Green
