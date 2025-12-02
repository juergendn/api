# Schnellstart-Anleitung

## 1. Umgebung einrichten

```powershell
# Im Verzeichnis clients\python ausführen:
.\setup.ps1
```

## 2. Terminal-IP konfigurieren

```powershell
$env:TERMINAL_IP = "192.168.1.100"  # Ihre Terminal-IP hier eintragen
```

## 3. Test durchführen

### Option A: Einfache Einzelzahlung

```powershell
# Zahlung über 1.50 EUR (150 Cent)
python simple_payment.py 150

# Oder mit expliziter IP:
python simple_payment.py 150 192.168.1.100
```

### Option B: Umfangreiches Test-Programm

```powershell
# Führt mehrere Test-Szenarien durch
python test_payment.py
```

## Erwartete Ausgabe (Erfolgsfall)

```
💳 Zahlung: 150 Cent (1.50 EUR)
🔌 Terminal: 192.168.1.100:11111

⏳ Warte auf Kartenzahlung...
✅ Zahlung genehmigt!
📦 Sende Warenausgabe...
✅ Warenausgabe bestätigt
✅✅ Zahlung erfolgreich! ✅✅
```

## Fehlerbehebung

### "Module not found" Fehler
```powershell
python generate_protos.py
python fix_imports.py
```

### Verbindungsfehler
- Prüfen Sie die Terminal-IP
- Stellen Sie sicher, dass Port 11111 nicht blockiert ist
- Testen Sie die Verbindung: `Test-NetConnection 192.168.1.100 -Port 11111`

### Terminal reagiert nicht
- Ist das Terminal eingeschaltet?
- Ist das Terminal im Netzwerk erreichbar?
- Läuft die Terminal-Software?

## Datei-Übersicht

- `setup.ps1` - Automatisches Setup-Script
- `simple_payment.py` - Einfaches Zahlungs-Demo
- `test_payment.py` - Umfangreiches Test-Programm
- `generate_protos.py` - Generiert Protobuf-Dateien
- `fix_imports.py` - Korrigiert Import-Statements
- `test_imports.py` - Testet die Installation
- `gen/` - Generierte Protobuf-Dateien (automatisch erstellt)
