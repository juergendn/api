<<<<<<< HEAD
# SENVEND Kartenleser API - Python Test Client

Dieses Verzeichnis enthält Python-Test-Programme für die SENVEND Kartenleser API.

## Voraussetzungen

- **Python 3.8+** installiert

## Schnell-Setup (Automatisch)

Führen Sie einfach das Setup-Script aus:

```powershell
.\setup.ps1
```

Dieses Script:
- Erstellt ein Virtual Environment
- Installiert alle Abhängigkeiten
- Generiert die Protobuf-Dateien
- Korrigiert die Imports
- Testet die Installation

## Manuelles Setup

### 1. Virtual Environment erstellen

```powershell
cd clients\python
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Abhängigkeiten installieren

```powershell
pip install -r requirements.txt
```

### 3. Protobuf-Dateien generieren

```powershell
python generate_protos.py
python fix_imports.py
```

### 4. Installation testen

```powershell
python test_imports.py
```powershell
python test_imports.py
```

## Verwendung

### Terminal-IP konfigurieren

Setzen Sie die Umgebungsvariable für die Terminal-IP:

```powershell
$env:TERMINAL_IP = "192.168.1.100"  # Ihre Terminal-IP
$env:TERMINAL_PORT = "11111"         # Optional, Standard ist 11111
```

### Test-Programm ausführen

```powershell
python test_payment.py
```

Das Programm führt zwei Tests durch:
1. Einfache Zahlung von 1.00 EUR (100 Cent)
2. Zahlung von 2.50 EUR (250 Cent) mit Altersverifikation (18+)

### Ablauf einer Zahlung

1. **PayStart** - Zahlung mit Betrag starten
2. **PayApproved** - Terminal bestätigt, dass Karte genug Guthaben hat
3. **PayGoodsIssued** - Wir bestätigen, dass Waren ausgegeben wurden
4. **PaySuccess** - Zahlung erfolgreich abgeschlossen

### Response-Typen

- `age_api_success` - Altersverifikation gestartet
- `age_success` - Altersverifikation erfolgreich
- `age_failure` - Altersverifikation fehlgeschlagen
- `api_success` - API-Befehl erfolgreich (z.B. Zahlung gestartet)
- `approved` - Zahlung genehmigt (Karte hat Guthaben)
- `success` - Zahlung erfolgreich abgeschlossen
- `failure` - Zahlung fehlgeschlagen
- `api_failure` - API-Fehler (z.B. ungültiger Betrag)

### Fehlerbehebung

### Import-Fehler

Falls Import-Fehler auftreten:
```powershell
python generate_protos.py
python fix_imports.py
python test_imports.py
```

### Verbindungsfehler

- Prüfen Sie, ob die Terminal-IP korrekt ist
- Prüfen Sie, ob das Terminal auf Port 11111 erreichbar ist
- Stellen Sie sicher, dass keine Firewall die Verbindung blockiert

## Beispiel-Ausgabe

```
============================================================
  SENVEND Kartenleser Test-Programm
============================================================

--- Test 1: Einfache Zahlung (1.00 EUR) ---

🔌 Verbinde mit Terminal: 192.168.1.100:11111
✅ Verbindung hergestellt
📤 Sende PayStart: Betrag=100 Cent

📥 Antwort erhalten: api_success
   ✓ Zahlung gestartet

📥 Antwort erhalten: approved
   ✓ Zahlung genehmigt! Karte hat genug Guthaben.

📤 Sende GoodsIssued (Waren ausgegeben)

📥 Antwort erhalten: api_success
   ✓ Warenausgabe bestätigt

📥 Antwort erhalten: success
   ✓✓✓ Zahlung erfolgreich abgeschlossen! ✓✓✓

Ergebnis: ✅ ERFOLG
```
=======
# SENVEND Python API

## example code

Take a look at [packages/example](./packages/example/) for a simple example of how to use the SENVEND Python API.
>>>>>>> 66ea39dee573b02a335a6bbfccc08d39c77d063f
