"""
Diagnose-Tool für SENVEND Terminal-Verbindung
Testet Verbindung und zeigt detaillierte Fehlerinformationen
"""

import asyncio
import sys
import grpc
from gen.local.v1 import local_pb2_grpc
from gen.api.v1 import pay_pb2


async def test_connection(ip: str, port: int):
    """Testet die Verbindung zum Terminal"""
    url = f"{ip}:{port}"
    
    print("=" * 70)
    print("  SENVEND Terminal Diagnose")
    print("=" * 70)
    print()
    print(f"Ziel: {url}")
    print()
    
    # Test 1: Channel erstellen
    print("📡 Test 1: Channel erstellen...")
    try:
        channel = grpc.aio.insecure_channel(
            url,
            options=[
                ('grpc.keepalive_time_ms', 10000),
                ('grpc.keepalive_timeout_ms', 5000),
                ('grpc.keepalive_permit_without_calls', True),
                ('grpc.http2.max_pings_without_data', 0),
            ]
        )
        print("   ✅ Channel erstellt")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        return
    
    # Test 2: Channel State prüfen
    print("\n📊 Test 2: Channel State...")
    try:
        state = channel.get_state(try_to_connect=False)
        print(f"   Status: {state}")
        print("   ✅ State abgerufen")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    # Test 3: Verbindung versuchen
    print("\n🔌 Test 3: Verbindung herstellen...")
    try:
        await channel.channel_ready()
        print("   ✅ Channel bereit")
    except asyncio.TimeoutError:
        print("   ⚠️  Timeout - Server antwortet nicht")
        await channel.close()
        return
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        await channel.close()
        return
    
    # Test 4: Service-Stub erstellen
    print("\n🔧 Test 4: PayService-Stub erstellen...")
    try:
        stub = local_pb2_grpc.PayServiceStub(channel)
        print("   ✅ Stub erstellt")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        await channel.close()
        return
    
    # Test 5: Verfügbare Services abfragen (Reflection)
    print("\n📋 Test 5: Services erkunden...")
    try:
        # Versuche eine einfache Anfrage
        print("   Teste PayService.Pay Methode...")
        
        async def request_gen():
            yield pay_pb2.PayRequest(
                start=pay_pb2.PayStart(amount=1)  # Minimaler Test-Betrag
            )
        
        call = stub.Pay(request_gen())
        
        # Warte kurz auf Antwort
        try:
            response = await asyncio.wait_for(
                call.__anext__(),
                timeout=5.0
            )
            print(f"   ✅ Antwort erhalten: {response.WhichOneof('result')}")
            
            # Stream beenden
            try:
                await call.__anext__()
            except StopAsyncIteration:
                pass
                
        except asyncio.TimeoutError:
            print("   ⚠️  Timeout - Keine Antwort vom Server")
        except grpc.aio.AioRpcError as e:
            print(f"   ❌ gRPC Fehler:")
            print(f"      Code: {e.code()}")
            print(f"      Name: {e.code().name}")
            print(f"      Details: {e.details()}")
            
            if e.code() == grpc.StatusCode.UNIMPLEMENTED:
                print("\n   💡 Mögliche Ursachen:")
                print("      - Server implementiert PayService nicht")
                print("      - Falsche Proto-Version (Client/Server mismatch)")
                print("      - Server läuft, aber Service nicht aktiviert")
                print("      - Falscher Service-Name oder Namespace")
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                print("\n   💡 Server ist nicht erreichbar")
            elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                print("\n   💡 Server antwortet zu langsam")
                
    except Exception as e:
        print(f"   ❌ Unerwarteter Fehler: {type(e).__name__}: {e}")
    
    # Test 6: Channel-Informationen
    print("\n📝 Test 6: Channel-Informationen...")
    try:
        final_state = channel.get_state()
        print(f"   Finaler Status: {final_state}")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    # Cleanup
    print("\n🧹 Aufräumen...")
    await channel.close()
    print("   ✅ Channel geschlossen")
    
    print("\n" + "=" * 70)
    print("Diagnose abgeschlossen")
    print("=" * 70)


async def main():
    """Hauptprogramm"""
    if len(sys.argv) >= 2:
        ip = sys.argv[1]
    else:
        ip = input("Terminal IP-Adresse [127.0.0.1]: ").strip() or "127.0.0.1"
    
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])
    else:
        port_input = input("Terminal Port [11111]: ").strip()
        port = int(port_input) if port_input else 11111
    
    await test_connection(ip, port)


if __name__ == "__main__":
    print()
    print("SENVEND Terminal Diagnose-Tool")
    print("Verwendung: python diagnose.py [ip] [port]")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Abgebrochen durch Benutzer")
