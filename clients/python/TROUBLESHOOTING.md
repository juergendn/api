# 🔧 Fehlerbehebung: Method not found

## Problem

```
gRPC Fehler: StatusCode.UNIMPLEMENTED
Details: Method not found: local.v1.PayService/Pay
```

## Ursachen

Dieser Fehler tritt auf, wenn:

### 1. ✅ Server ist erreichbar, aber Service nicht implementiert
- Das Terminal läuft und antwortet auf gRPC-Anfragen
- Aber der `PayService` oder die `Pay`-Methode ist nicht verfügbar

### 2. 🔄 Proto-Version-Mismatch
- Client und Server verwenden unterschiedliche Proto-Definitionen
- Namespace oder Service-Namen stimmen nicht überein

### 3. 🚫 Service nicht aktiviert
- Das Terminal läuft, aber der PayService ist nicht gestartet
- Feature-Flag oder Konfiguration fehlt

## Lösungen

### Lösung 1: Terminal-Status prüfen

Stellen Sie sicher, dass:
- Das Terminal läuft und auf Port 11111 hört
- Der PayService aktiviert ist
- Die richtige Software-Version läuft

```powershell
# Prüfen Sie ob Port 11111 offen ist
Test-NetConnection -ComputerName <TERMINAL_IP> -Port 11111
```

### Lösung 2: Diagnose-Tool verwenden

```powershell
python diagnose.py <TERMINAL_IP> 11111
```

Das Diagnose-Tool zeigt detaillierte Informationen:
- Verbindungsstatus
- Channel-State
- Verfügbare Services
- Genaue Fehlermeldungen

### Lösung 3: Proto-Versionen prüfen

```powershell
# Proto-Dateien neu generieren
python generate_protos.py
python fix_imports.py
```

### Lösung 4: Alternative Endpunkte testen

Manchmal verwendet das Terminal einen anderen Port oder Pfad:

```python
# In web_app.py oder test_payment.py
# Versuchen Sie:
url = f"http://{terminal_ip}:{terminal_port}"  # Statt nur ip:port
```

### Lösung 5: Server-Logs prüfen

Prüfen Sie die Terminal-Logs auf:
- Startup-Meldungen des PayService
- gRPC-Server-Port
- Fehler bei der Service-Registrierung

## Vergleich: Funktionierend vs. Nicht-Funktionierend

### ✅ Funktionierend (UNAVAILABLE)
```
gRPC Fehler: StatusCode.UNAVAILABLE
Details: failed to connect to all addresses
```
→ Server ist nicht erreichbar (normale Netzwerkfehler)

### ❌ Nicht-Funktionierend (UNIMPLEMENTED)
```
gRPC Fehler: StatusCode.UNIMPLEMENTED
Details: Method not found: local.v1.PayService/Pay
```
→ Server ist erreichbar, aber Service fehlt

## Weitere Schritte

### 1. Testen Sie mit dem Rust-Client

Der Rust-Client im Repository sollte funktionieren:

```bash
cd clients/rust/example
TERMINAL_IP=<IP> cargo run
```

Wenn der Rust-Client funktioniert, aber Python nicht:
→ Proto-Generierung überprüfen

Wenn auch Rust nicht funktioniert:
→ Terminal-Konfiguration prüfen

### 2. Prüfen Sie die Terminal-Dokumentation

- Welche gRPC-Services sind verfügbar?
- Welcher Port ist korrekt?
- Gibt es Authentifizierung?
- Benötigt es TLS/SSL?

### 3. Network-Trace erstellen

```powershell
# Wireshark oder tcpdump verwenden
# Prüfen Sie die gRPC-Header und Service-Namen
```

## Kontakt

Wenn das Problem weiterhin besteht:
1. Sammeln Sie Logs vom Terminal
2. Führen Sie `diagnose.py` aus und speichern Sie die Ausgabe
3. Notieren Sie die Terminal-Softwareversion
4. Kontaktieren Sie den SENVEND-Support

## Bekannte Probleme

### Problem: Proto-Namespace geändert

**Symptom:** UNIMPLEMENTED nach Proto-Update

**Lösung:**
```powershell
# Komplett neu generieren
Remove-Item -Recurse -Force gen
python generate_protos.py
python fix_imports.py
python test_imports.py
```

### Problem: gRPC-Version-Inkompatibilität

**Symptom:** Warnings über GRPC_GENERATED_VERSION

**Lösung:**
```powershell
pip install --upgrade grpcio grpcio-tools
python generate_protos.py
python fix_imports.py
```

### Problem: Bidirectional Streaming

Der `PayService.Pay` ist ein **bidirektionaler Stream**:
- Client sendet mehrere `PayRequest` Messages
- Server sendet mehrere `PayResponse` Messages

Stellen Sie sicher, dass:
1. Der Request-Generator korrekt implementiert ist
2. Der Response-Stream korrekt gelesen wird
3. Die Queue für weitere Requests funktioniert

## Erfolgreicher Test

Ein erfolgreicher Test sieht so aus:

```
🔌 Verbinde mit Terminal: 192.168.1.100:11111
✅ Verbindung hergestellt

📥 Antwort erhalten: api_success
   ✓ Zahlung gestartet

📥 Antwort erhalten: approved
   ✓ Zahlung genehmigt!

📤 Sende GoodsIssued (Waren ausgegeben)

📥 Antwort erhalten: api_success
   ✓ Warenausgabe bestätigt

📥 Antwort erhalten: success
   ✓✓✓ Zahlung erfolgreich abgeschlossen! ✓✓✓
```
