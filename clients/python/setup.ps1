# Setup-Script für die Python-Umgebung

Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host "  SENVEND Kartenleser API - Python Setup"
Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host ""

# 1. Virtual Environment prüfen
if (-not (Test-Path "venv")) {
    Write-Host "Erstelle Virtual Environment..."
    python -m venv venv
    Write-Host "✅ Virtual Environment erstellt" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual Environment existiert bereits" -ForegroundColor Green
}

Write-Host ""

# 2. Virtual Environment aktivieren
Write-Host "Aktiviere Virtual Environment..."
.\venv\Scripts\Activate.ps1

# 3. Abhängigkeiten installieren
Write-Host "Installiere Abhängigkeiten..."
pip install --quiet grpcio grpcio-tools
Write-Host "✅ Abhängigkeiten installiert" -ForegroundColor Green
Write-Host ""

# 4. Protobuf-Dateien generieren
Write-Host "Generiere Protobuf-Dateien..."
python generate_protos.py

# 5. Imports korrigieren
Write-Host ""
Write-Host "Korrigiere Imports..."
python fix_imports.py

# 6. Test durchführen
Write-Host ""
Write-Host "Teste Imports..."
python test_imports.py

Write-Host ""
Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host "  Setup abgeschlossen!"
Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host ""
Write-Host "Nächste Schritte:" -ForegroundColor Cyan
Write-Host "  1. Terminal-IP setzen:"
Write-Host "     `$env:TERMINAL_IP = '192.168.1.100'" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. Test-Programm ausführen:"
Write-Host "     python test_payment.py" -ForegroundColor Yellow
Write-Host ""
