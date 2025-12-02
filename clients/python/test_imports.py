"""
Test-Script um die Protobuf-Imports zu überprüfen
"""

import sys

print("Teste Imports...")
print()

try:
    from gen.local.v1 import local_pb2_grpc
    print("✅ local_pb2_grpc importiert")
    
    from gen.api.v1 import pay_pb2, common_pb2
    print("✅ pay_pb2 importiert")
    print("✅ common_pb2 importiert")
    
    import grpc
    print("✅ grpc importiert")
    
    print()
    print("✅ Alle Imports erfolgreich!")
    print()
    
    # Zeige verfügbare Enums und Messages
    print("Verfügbare PayApiSuccessReason:")
    for name, value in pay_pb2.PayApiSuccessReason.items():
        print(f"  - {name} = {value}")
    
    print()
    print("Verfügbare PayFailureReason:")
    for name, value in pay_pb2.PayFailureReason.items():
        print(f"  - {name} = {value}")
    
    print()
    print("✅ Umgebung ist bereit für Tests!")
    
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
    print()
    print("Bitte führen Sie zuerst aus:")
    print("  python generate_protos.py")
    sys.exit(1)
