"""
Einfaches Demo-Programm für eine einzelne Zahlung
Verwendung: python simple_payment.py <betrag_in_cent> [<terminal_ip>]
Beispiel: python simple_payment.py 150 192.168.1.100
"""

import asyncio
import os
import sys

import grpc
from gen.local.v1 import local_pb2_grpc
from gen.api.v1 import pay_pb2


async def simple_payment(terminal_ip: str, terminal_port: int, amount_cents: int):
    """
    Einfacher Zahlungsvorgang
    
    Args:
        terminal_ip: IP des Terminals
        terminal_port: Port des Terminals
        amount_cents: Betrag in Cent
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    url = f"{terminal_ip}:{terminal_port}"
    print(f"💳 Zahlung: {amount_cents} Cent ({amount_cents/100:.2f} EUR)")
    print(f"🔌 Terminal: {url}")
    print()
    
    try:
        async with grpc.aio.insecure_channel(url) as channel:
            stub = local_pb2_grpc.PayServiceStub(channel)
            request_queue = asyncio.Queue()
            
            async def request_generator():
                # Start-Request
                yield pay_pb2.PayRequest(
                    start=pay_pb2.PayStart(amount=amount_cents)
                )
                
                # Weitere Requests
                while True:
                    request = await request_queue.get()
                    if request is None:
                        break
                    yield request
            
            response_stream = stub.Pay(request_generator())
            
            async for response in response_stream:
                result_type = response.WhichOneof('result')
                
                if result_type == 'api_success':
                    reason = response.api_success.reason
                    if reason == pay_pb2.PAY_API_SUCCESS_REASON_PAYMENT_STARTED:
                        print("⏳ Warte auf Kartenzahlung...")
                    elif reason == pay_pb2.PAY_API_SUCCESS_REASON_GOODS_ISSUED_ACCEPTED:
                        print("✅ Warenausgabe bestätigt")
                
                elif result_type == 'approved':
                    print("✅ Zahlung genehmigt!")
                    print("📦 Sende Warenausgabe...")
                    await request_queue.put(
                        pay_pb2.PayRequest(
                            goods_issued=pay_pb2.PayGoodsIssued(partial_amount=0)
                        )
                    )
                
                elif result_type == 'success':
                    print("✅✅ Zahlung erfolgreich! ✅✅")
                    await request_queue.put(None)
                    return True
                
                elif result_type == 'failure':
                    reason_field = response.failure.WhichOneof('reason')
                    reason_value = getattr(response.failure, reason_field, 'UNBEKANNT')
                    reason_name = pay_pb2.PayFailureReason.Name(reason_value) if isinstance(reason_value, int) else reason_value
                    print(f"❌ Zahlung fehlgeschlagen: {reason_name}")
                    await request_queue.put(None)
                    return False
                
                elif result_type == 'api_failure':
                    reason = response.api_failure.reason
                    reason_name = pay_pb2.PayApiFailureReason.Name(reason)
                    print(f"❌ API-Fehler: {reason_name}")
                    await request_queue.put(None)
                    return False
            
    except grpc.aio.AioRpcError as e:
        print(f"❌ Verbindungsfehler: {e.code()}")
        print(f"   {e.details()}")
        return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def main():
    """Hauptprogramm"""
    # Argumente parsen
    if len(sys.argv) < 2:
        print("Verwendung: python simple_payment.py <betrag_in_cent> [<terminal_ip>]")
        print("Beispiel:   python simple_payment.py 150 192.168.1.100")
        print()
        print("Oder setzen Sie die Umgebungsvariable TERMINAL_IP:")
        print("  $env:TERMINAL_IP = '192.168.1.100'")
        sys.exit(1)
    
    try:
        amount_cents = int(sys.argv[1])
    except ValueError:
        print("❌ Ungültiger Betrag! Bitte eine Zahl in Cent angeben.")
        sys.exit(1)
    
    if amount_cents <= 0:
        print("❌ Betrag muss größer als 0 sein!")
        sys.exit(1)
    
    # Terminal-IP
    if len(sys.argv) >= 3:
        terminal_ip = sys.argv[2]
    else:
        terminal_ip = os.getenv('TERMINAL_IP')
        if not terminal_ip:
            print("❌ Terminal-IP nicht angegeben!")
            print("   Entweder als Argument oder via Umgebungsvariable:")
            print("   $env:TERMINAL_IP = '192.168.1.100'")
            sys.exit(1)
    
    terminal_port = int(os.getenv('TERMINAL_PORT', '11111'))
    
    # Zahlung durchführen
    print()
    print("=" * 60)
    success = asyncio.run(simple_payment(terminal_ip, terminal_port, amount_cents))
    print("=" * 60)
    print()
    
    if success:
        print("🎉 Zahlung erfolgreich abgeschlossen!")
        sys.exit(0)
    else:
        print("⚠️  Zahlung fehlgeschlagen.")
        sys.exit(1)


if __name__ == "__main__":
    main()
