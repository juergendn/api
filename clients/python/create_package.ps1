# SENVEND Kartenleser - Windows Installer
# Erstellt ein ZIP-Paket zum Verteilen

$ErrorActionPreference = "Stop"

$sourceDir = "C:\Users\JürgenNiessen\Documents\GitHub\api\clients\python"
$packageDir = "$sourceDir\SENVEND_Package"
$zipFile = "$sourceDir\SENVEND_Terminal_Test.zip"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SENVEND Terminal Test - Package Creator" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Bereinige altes Package
if (Test-Path $packageDir) {
    Write-Host "Entferne altes Package..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $packageDir
}
if (Test-Path $zipFile) {
    Remove-Item -Force $zipFile
}

# Erstelle Package-Verzeichnis
Write-Host "Erstelle Package-Struktur..." -ForegroundColor Green
New-Item -ItemType Directory -Path $packageDir | Out-Null

# Kopiere benötigte Dateien
Write-Host "Kopiere Programmdateien..." -ForegroundColor Green
Copy-Item "$sourceDir\web_app.py" $packageDir
Copy-Item "$sourceDir\START_WEBSERVER.bat" $packageDir
Copy-Item -Recurse "$sourceDir\templates" $packageDir
Copy-Item -Recurse "$sourceDir\static" $packageDir
Copy-Item -Recurse "$sourceDir\gen" $packageDir
Copy-Item -Recurse "$sourceDir\venv" $packageDir

# Erstelle README
$readme = @"
SENVEND Terminal Test - Web Interface
======================================

Installation:
1. Entpacken Sie dieses ZIP-Archiv
2. Doppelklick auf START_WEBSERVER.bat
3. Browser öffnet sich automatisch auf http://localhost:5000

Konfiguration:
- Terminal IP-Adresse im Web-Interface eingeben
- Standard-Port: 11111

Systemanforderungen:
- Windows 10/11
- Keine Installation erforderlich (alles enthalten)

Support:
- api@senvend.com
"@

$readme | Out-File -FilePath "$packageDir\README.txt" -Encoding UTF8

# Erstelle ZIP
Write-Host "Erstelle ZIP-Archiv..." -ForegroundColor Green
Compress-Archive -Path $packageDir -DestinationPath $zipFile

# Bereinige Package-Verzeichnis
Remove-Item -Recurse -Force $packageDir

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  ✅ Package erfolgreich erstellt!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Speicherort: $zipFile" -ForegroundColor Cyan
Write-Host "Größe: $([math]::Round((Get-Item $zipFile).Length / 1MB, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Das ZIP kann auf jedem Windows-PC entpackt und gestartet werden." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Green
