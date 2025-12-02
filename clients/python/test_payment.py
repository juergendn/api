"""
Test-Programm für den SENVEND Kartenleser
Sendet eine Zahlungsanforderung und wertet die Antwort aus
"""

import asyncio
import os
import sys
from typing import AsyncIterator

import grpc
from google.protobuf import empty_pb2

# Import der generierten protobuf Dateien
# Diese müssen zuerst mit generate_protos.py generiert werden
try:
    from gen.local.v1 import local_pb2_grpc
    from gen.api.v1 import pay_pb2, common_pb2
except ImportError:
    print("FEHLER: Protobuf-Dateien nicht gefunden!")
    print("Bitte zuerst die Python-Clients generieren:")
    print("  python generate_protos.py")
    sys.exit(1)


async def payment_request_stream(amount_cents: int, min_age: int = None) -> AsyncIterator:
    """
    Generator für die Payment-Request-Stream
    
    Args:
        amount_cents: Betrag in Cent (z.B. 100 = 1.00 EUR)
        min_age: Optional - Mindestalter für Altersverifikation
    """
    # Start Request
    pay_start = pay_pb2.PayStart(amount=amount_cents)
    
    # Optional: Altersverifikation hinzufügen
    if min_age:
        pay_start.age_verification.CopyFrom(
            pay_pb2.AgeStartRequest(min_age=min_age)
        )
    
    start_request = pay_pb2.PayRequest(start=pay_start)
    print(f"📤 Sende PayStart: Betrag={amount_cents} Cent")
    if min_age:
        print(f"   Mit Altersverifikation: Mindestalter={min_age}")
    yield start_request
    
    # Warte auf weitere Befehle (z.B. GoodsIssued)
    # Diese werden vom Hauptprogramm über eine Queue gesteuert


async def test_payment(terminal_ip: str, terminal_port: int, amount_cents: int, min_age: int = None):
    """
    Führt einen kompletten Zahlungsvorgang durch
    
    Args:
        terminal_ip: IP-Adresse des Terminals
        terminal_port: Port des Terminals (Standard: 11111)
        amount_cents: Betrag in Cent
        min_age: Optional - Mindestalter für Altersverifikation
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    url = f"{terminal_ip}:{terminal_port}"
    print(f"\n🔌 Verbinde mit Terminal: {url}")
    
    try:
        # gRPC Channel erstellen
        async with grpc.aio.insecure_channel(url) as channel:
            stub = local_pb2_grpc.PayServiceStub(channel)
            
            # Queue für zusätzliche Requests (z.B. GoodsIssued)
            request_queue = asyncio.Queue()
            
            async def request_generator():
                # Erster Request: PayStart
                pay_start = pay_pb2.PayStart(amount=amount_cents)
                if min_age:
                    pay_start.age_verification.CopyFrom(
                        pay_pb2.AgeStartRequest(min_age=min_age)
                    )
                yield pay_pb2.PayRequest(start=pay_start)
                
                # Weitere Requests aus der Queue
                while True:
                    request = await request_queue.get()
                    if request is None:  # Sentinel zum Beenden
                        break
                    yield request
            
            # Bidirektionaler Stream starten
            print("✅ Verbindung hergestellt")
            response_stream = stub.Pay(request_generator())
            
            payment_approved = False
            payment_uuid = None
            
            # Responses verarbeiten
            async for response in response_stream:
                payment_uuid = response.id if response.HasField('id') else payment_uuid
                result_type = response.WhichOneof('result')
                
                print(f"\n📥 Antwort erhalten: {result_type}")
                
                # Altersverifikation gestartet
                if result_type == 'age_api_success':
                    reason = response.age_api_success.reason
                    if reason == pay_pb2.AGE_API_SUCCESS_REASON_VERIFICATION_STARTED:
                        print("   ✓ Altersverifikation gestartet")
                
                # Altersverifikation erfolgreich
                elif result_type == 'age_success':
                    print("   ✓ Altersverifikation erfolgreich")
                
                # Altersverifikation fehlgeschlagen
                elif result_type == 'age_failure':
                    reason = response.age_failure.failure_reason
                    print(f"   ✗ Altersverifikation fehlgeschlagen: {reason}")
                    await request_queue.put(None)
                    return False
                
                # Zahlung gestartet
                elif result_type == 'api_success':
                    reason = response.api_success.reason
                    if reason == pay_pb2.PAY_API_SUCCESS_REASON_PAYMENT_STARTED:
                        print("   ✓ Zahlung gestartet")
                    elif reason == pay_pb2.PAY_API_SUCCESS_REASON_GOODS_ISSUED_ACCEPTED:
                        print("   ✓ Warenausgabe bestätigt")
                
                # Zahlung genehmigt
                elif result_type == 'approved':
                    print("   ✓ Zahlung genehmigt! Karte hat genug Guthaben.")
                    payment_approved = True
                    
                    # Jetzt GoodsIssued senden
                    print("\n📤 Sende GoodsIssued (Waren ausgegeben)")
                    goods_issued = pay_pb2.PayRequest(
                        goods_issued=pay_pb2.PayGoodsIssued(partial_amount=0)
                    )
                    await request_queue.put(goods_issued)
                
                # Zahlung erfolgreich abgeschlossen
                elif result_type == 'success':
                    print("   ✓✓✓ Zahlung erfolgreich abgeschlossen! ✓✓✓")
                    await request_queue.put(None)  # Stream beenden
                    return True
                
                # Zahlung fehlgeschlagen
                elif result_type == 'failure':
                    reason_field = response.failure.WhichOneof('reason')
                    reason_value = getattr(response.failure, reason_field, 'UNBEKANNT')
                    print(f"   ✗ Zahlung fehlgeschlagen: {reason_value}")
                    await request_queue.put(None)
                    return False
                
                # API Fehler
                elif result_type == 'api_failure':
                    reason = response.api_failure.reason
                    reason_name = pay_pb2.PayApiFailureReason.Name(reason)
                    print(f"   ✗ API Fehler: {reason_name}")
                    await request_queue.put(None)
                    return False
                
                else:
                    print(f"   ⚠ Unbekannter Response-Typ: {result_type}")
            
            if not payment_approved:
                print("\n✗ Zahlung wurde nicht genehmigt")
                return False
            
    except grpc.aio.AioRpcError as e:
        print(f"\n❌ gRPC Fehler: {e.code()}")
        print(f"   Details: {e.details()}")
        return False
    except asyncio.CancelledError:
        print(f"\n❌ Verbindung abgebrochen")
        return False
    except Exception as e:
        print(f"\n❌ Fehler: {type(e).__name__}: {e}")
        return False


async def main():
    """Hauptprogramm"""
    print("=" * 60)
    print("  SENVEND Kartenleser Test-Programm")
    print("=" * 60)
    
    # Konfiguration aus Umgebungsvariablen oder Defaults
    terminal_ip = os.getenv('TERMINAL_IP', '127.0.0.1')
    terminal_port = int(os.getenv('TERMINAL_PORT', '11111'))
    
    # Test-Szenarien
    print("\n--- Test 1: Einfache Zahlung (1.00 EUR) ---")
    try:
        success = await test_payment(terminal_ip, terminal_port, amount_cents=100)
        print(f"\nErgebnis: {'✅ ERFOLG' if success else '❌ FEHLER'}")
    except Exception as e:
        print(f"\nErgebnis: ❌ FEHLER - {e}")
    
    # Warte kurz zwischen Tests
    if terminal_ip != '127.0.0.1':  # Nur warten wenn echtes Terminal
        await asyncio.sleep(2)
    
    print("\n\n--- Test 2: Zahlung mit Altersverifikation (2.50 EUR, 18+) ---")
    try:
        success = await test_payment(terminal_ip, terminal_port, amount_cents=250, min_age=18)
        print(f"\nErgebnis: {'✅ ERFOLG' if success else '❌ FEHLER'}")
    except Exception as e:
        print(f"\nErgebnis: ❌ FEHLER - {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Umgebungsvariablen prüfen
    if not os.getenv('TERMINAL_IP'):
        print("⚠ HINWEIS: Umgebungsvariable TERMINAL_IP nicht gesetzt")
        print("   Verwende Standard: 127.0.0.1")
        print("   Setzen mit: $env:TERMINAL_IP='192.168.1.100'")
        print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Programm durch Benutzer abgebrochen")
