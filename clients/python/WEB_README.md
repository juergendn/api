# 🌐 SENVEND Kartenleser Web-Interface

Eine benutzerfreundliche Web-Oberfläche zum Testen der SENVEND Kartenleser API.

## ✨ Features

- **🔧 Einfache Konfiguration**: Terminal-IP und Port direkt im Browser einstellen
- **⚡ Schnelltests**: Vordefinierte Testbeträge mit einem Klick
- **⚙️ Benutzerdefiniert**: Eigene Beträge und Altersverifikation konfigurieren
- **📋 Live-Log**: Echtzeit-Updates während der Zahlungsabwicklung
- **🎨 Modernes Design**: Responsive und benutzerfreundliche Oberfläche

## 🚀 Starten

```powershell
# Im python-Verzeichnis
cd clients\python

# Web-App starten
C:\Users\JürgenNiessen\Documents\GitHub\api\clients\python\venv\Scripts\python.exe web_app.py

# Oder mit aktiviertem venv
.\venv\Scripts\Activate.ps1
python web_app.py
```

Die Web-Oberfläche ist dann verfügbar unter:
- **http://localhost:5000**
- **http://127.0.0.1:5000**

## 📖 Verwendung

### 1. Terminal konfigurieren
- Geben Sie die IP-Adresse des Terminals ein (z.B. `192.168.1.100`)
- Port ist standardmäßig `11111`
- Klicken Sie auf "Konfiguration speichern"

### 2. Test durchführen

**Schnelltests:**
- Klicken Sie auf einen der vordefinierten Beträge
- `1.00 EUR`, `2.50 EUR`, `5.00 EUR`
- `1.50 EUR + 18+` für Test mit Altersverifikation

**Benutzerdefiniert:**
- Geben Sie einen eigenen Betrag in Cent ein
- Optional: Aktivieren Sie die Altersverifikation
- Klicken Sie auf "Test starten"

### 3. Ergebnisse beobachten
- Alle Updates werden im Live-Log angezeigt
- Farbcodierung:
  - 🔵 Blau = Info
  - 🟢 Grün = Erfolg
  - 🔴 Rot = Fehler
  - 🟡 Gelb = Warnung

## 🔄 Ablauf einer Zahlung

1. **Verbindung** zum Terminal wird hergestellt
2. **Zahlung gestartet** mit angegebenem Betrag
3. Optional: **Altersverifikation** wird durchgeführt
4. **Zahlung genehmigt** - Karte hat genug Guthaben
5. **Warenausgabe** wird bestätigt
6. **Zahlung erfolgreich** abgeschlossen ✅

## 🛠️ Technische Details

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Real-time Updates**: Server-Sent Events (SSE)
- **gRPC**: Asynchrone Kommunikation mit dem Terminal

## 📝 API-Endpunkte

- `GET /` - Hauptseite
- `GET /api/config` - Aktuelle Konfiguration abrufen
- `POST /api/config` - Konfiguration setzen
- `POST /api/test` - Test starten
- `GET /api/stream` - SSE-Stream für Live-Updates

## 🎯 Beispiel-Requests

### Konfiguration setzen
```json
POST /api/config
{
  "terminal_ip": "192.168.1.100",
  "terminal_port": 11111
}
```

### Test starten
```json
POST /api/test
{
  "amount": 150,
  "min_age": 18
}
```

## 🔐 Sicherheitshinweis

Dies ist ein **Test-Tool** für Entwicklungs- und Testzwecke. 
Für Produktivumgebungen sollten zusätzliche Sicherheitsmaßnahmen implementiert werden:
- Authentifizierung
- HTTPS
- Rate Limiting
- Input Validation

## 📦 Abhängigkeiten

- `flask>=3.0.0`
- `grpcio>=1.76.0`
- `protobuf>=6.31.1`

## 🐛 Fehlerbehebung

### Port bereits belegt
```
OSError: [Errno 48] Address already in use
```
**Lösung**: Port 5000 ist bereits belegt. Ändern Sie den Port in `web_app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
```

### Verbindung zum Terminal fehlschlägt
```
gRPC Fehler: StatusCode.UNAVAILABLE
```
**Lösung**: 
- Prüfen Sie die Terminal-IP-Adresse
- Stellen Sie sicher, dass das Terminal auf Port 11111 erreichbar ist
- Prüfen Sie Firewall-Einstellungen

## 📄 Lizenz

Teil der SENVEND API - siehe Hauptprojekt für Lizenzinformationen.
