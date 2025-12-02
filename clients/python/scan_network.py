"""
Netzwerk-Scanner für SENVEND Terminals
Findet erreichbare Terminals im lokalen Netzwerk
"""

import socket
import asyncio
import grpc
from concurrent.futures import ThreadPoolExecutor
import ipaddress


def check_port(ip: str, port: int, timeout: float = 1.0) -> bool:
    """Prüft ob ein Port offen ist"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False


async def check_grpc_service(ip: str, port: int) -> tuple:
    """Prüft ob ein gRPC-Service auf dem Port läuft"""
    url = f"{ip}:{port}"
    try:
        channel = grpc.aio.insecure_channel(url)
        await asyncio.wait_for(channel.channel_ready(), timeout=2.0)
        
        # Versuche zu prüfen ob PayService verfügbar ist
        from gen.local.v1 import local_pb2_grpc
        from gen.api.v1 import pay_pb2
        
        stub = local_pb2_grpc.PayServiceStub(channel)
        
        # Minimal-Test
        async def test_gen():
            yield pay_pb2.PayRequest(start=pay_pb2.PayStart(amount=1))
        
        try:
            call = stub.Pay(test_gen())
            response = await asyncio.wait_for(call.__anext__(), timeout=1.0)
            await channel.close()
            return (ip, port, "PayService", "✅ VERFÜGBAR")
        except grpc.aio.AioRpcError as e:
            await channel.close()
            if e.code() == grpc.StatusCode.UNIMPLEMENTED:
                return (ip, port, "gRPC", "⚠️  Server läuft, aber PayService nicht verfügbar")
            else:
                return (ip, port, "gRPC", f"⚠️  {e.code().name}")
        except asyncio.TimeoutError:
            await channel.close()
            return (ip, port, "gRPC", "⏱️  Timeout")
            
    except asyncio.TimeoutError:
        return (ip, port, "TCP", "⏱️  Timeout")
    except Exception as e:
        return (ip, port, "Error", f"❌ {type(e).__name__}")


def get_local_ip():
    """Ermittelt die lokale IP-Adresse"""
    try:
        # Verbindung zu Google DNS (nicht wirklich verbinden)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"


async def scan_network(network: str, port: int = 11111):
    """Scannt ein Netzwerk nach SENVEND Terminals"""
    print("=" * 80)
    print("  SENVEND Terminal Scanner")
    print("=" * 80)
    print()
    print(f"Scanne Netzwerk: {network}")
    print(f"Port: {port}")
    print()
    
    try:
        net = ipaddress.ip_network(network, strict=False)
    except ValueError as e:
        print(f"❌ Ungültiges Netzwerk: {e}")
        return
    
    total_hosts = net.num_addresses
    print(f"Zu scannende Hosts: {total_hosts}")
    
    if total_hosts > 256:
        print("⚠️  Warnung: Großes Netzwerk - Scan kann lange dauern!")
        response = input("Fortfahren? (j/n): ")
        if response.lower() != 'j':
            return
    
    print()
    print("Schneller Port-Scan läuft...")
    print("-" * 80)
    
    # Schritt 1: Schneller TCP-Port-Scan
    open_ports = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for ip in net.hosts():
            ip_str = str(ip)
            futures.append(executor.submit(check_port, ip_str, port, 0.5))
        
        for i, (ip, future) in enumerate(zip(net.hosts(), futures)):
            if future.result():
                ip_str = str(ip)
                open_ports.append(ip_str)
                print(f"✓ {ip_str}:{port} - Port offen")
            
            # Fortschritt anzeigen
            if (i + 1) % 50 == 0:
                print(f"  ... {i + 1}/{total_hosts} IPs gescannt")
    
    print()
    print(f"Gefunden: {len(open_ports)} offene Ports")
    print()
    
    if not open_ports:
        print("❌ Keine offenen Ports gefunden")
        return
    
    # Schritt 2: gRPC-Service-Check für gefundene IPs
    print("Prüfe gRPC-Services...")
    print("-" * 80)
    
    results = []
    for ip in open_ports:
        result = await check_grpc_service(ip, port)
        results.append(result)
        print(f"{result[0]}:{result[1]} - {result[2]}: {result[3]}")
    
    print()
    print("=" * 80)
    print("Scan abgeschlossen")
    print("=" * 80)
    
    # Zusammenfassung
    available = [r for r in results if "VERFÜGBAR" in r[3]]
    if available:
        print()
        print("✅ Verfügbare SENVEND Terminals:")
        for r in available:
            print(f"   {r[0]}:{r[1]}")
        print()
        print("Verwenden Sie eine dieser Adressen in der Web-App oder test_payment.py")
    else:
        print()
        print("⚠️  Keine funktionierenden PayService-Instanzen gefunden")
        print()
        print("Mögliche Gründe:")
        print("  - Terminal läuft, aber PayService nicht aktiviert")
        print("  - Falsche Proto-Version")
        print("  - Terminal benötigt Authentifizierung")


async def main():
    """Hauptprogramm"""
    local_ip = get_local_ip()
    local_network = '.'.join(local_ip.split('.')[:-1]) + '.0/24'
    
    print()
    print("SENVEND Terminal Scanner")
    print()
    print(f"Ihre lokale IP: {local_ip}")
    print(f"Ihr lokales Netzwerk: {local_network}")
    print()
    
    # Benutzer-Eingabe
    network_input = input(f"Netzwerk zum Scannen [{local_network}]: ").strip()
    network = network_input if network_input else local_network
    
    port_input = input("Port [11111]: ").strip()
    port = int(port_input) if port_input else 11111
    
    print()
    await scan_network(network, port)


if __name__ == "__main__":
    print()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan abgebrochen")
