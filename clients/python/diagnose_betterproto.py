"""
Diagnose-Tool mit betterproto für SENVEND Terminal
"""

import grpc
from senvend_api.local.v1 import PayServiceStub
from senvend_api.api.v1 import PayRequest, PayStart

def test_terminal(ip: str, port: int = 11111):
    """Testet Verbindung zum Terminal"""
    connection = f"{ip}:{port}"
    print(f"🔌 Verbinde mit: {connection}")
    print()
    
    try:
        channel = grpc.insecure_channel(connection)
        
        # Teste Channel
        try:
            grpc.channel_ready_future(channel).result(timeout=5)
            print("✅ Channel ist bereit")
        except grpc.FutureTimeoutError:
            print("❌ Timeout - Server antwortet nicht")
            return
        
        # Erstelle Stub
        stub = PayServiceStub(channel)
        print("✅ PayServiceStub erstellt")
        print()
        
        # Teste Pay-Methode
        print("📤 Teste PayService.Pay Methode...")
        
        def request_gen():
            yield PayRequest(start=PayStart(amount=1))
        
        try:
            for response in stub.pay(request_gen()):
                print(f"📥 Antwort erhalten: {response}")
                break
            print("✅ PayService.Pay funktioniert!")
            
        except grpc.RpcError as e:
            print(f"❌ gRPC Fehler:")
            print(f"   Code: {e.code()}")
            print(f"   Details: {e.details()}")
            print()
            
            if e.code() == grpc.StatusCode.UNIMPLEMENTED:
                print("💡 UNIMPLEMENTED bedeutet:")
                print("   - Server ist erreichbar")
                print("   - Aber die Methode 'local.v1.PayService/Pay' existiert nicht")
                print()
                print("🔍 Mögliche Ursachen:")
                print("   1. PayService ist auf dem Terminal nicht aktiviert")
                print("   2. Terminal verwendet andere Proto-Version")
                print("   3. Service hat anderen Namen/Namespace")
                print("   4. Terminal benötigt Update/Konfiguration")
                print()
                print("📞 Kontaktieren Sie SENVEND Support:")
                print("   - Welche Services sind auf dem Terminal verfügbar?")
                print("   - Welche gRPC-Methoden werden unterstützt?")
                print("   - Terminal-Software-Version?")
        
        channel.close()
        
    except Exception as e:
        print(f"❌ Fehler: {type(e).__name__}: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        ip = input("Terminal IP [172.16.1.201]: ").strip() or "172.16.1.201"
    
    test_terminal(ip)
