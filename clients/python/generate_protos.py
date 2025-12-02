"""
Script zum Generieren der Python Protobuf-Dateien ohne buf CLI
Verwendet grpcio-tools direkt
"""

import os
import subprocess
import sys
from pathlib import Path

def generate_protos():
    """Generiert Python Protobuf-Dateien aus den .proto Dateien"""
    
    # Pfade
    repo_root = Path(__file__).parent.parent.parent
    proto_dir = repo_root / "proto"
    output_dir = Path(__file__).parent / "gen"
    
    # Output-Verzeichnis erstellen
    output_dir.mkdir(exist_ok=True)
    
    print(f"Repository Root: {repo_root}")
    print(f"Proto Directory: {proto_dir}")
    print(f"Output Directory: {output_dir}")
    print()
    
    # Alle .proto Dateien finden
    proto_files = list(proto_dir.rglob("*.proto"))
    
    if not proto_files:
        print("❌ Keine .proto Dateien gefunden!")
        sys.exit(1)
    
    print(f"Gefunden: {len(proto_files)} .proto Dateien")
    for proto_file in proto_files:
        print(f"  - {proto_file.relative_to(repo_root)}")
    print()
    
    # Proto-Dateien kompilieren
    print("Generiere Python-Dateien...")
    
    cmd = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"--proto_path={proto_dir}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        f"--pyi_out={output_dir}",  # Type stubs für bessere IDE-Unterstützung
    ] + [str(f) for f in proto_files]
    
    print(f"Befehl: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Fehler bei der Generierung:")
        print(result.stderr)
        sys.exit(1)
    
    print("✅ Protobuf-Dateien erfolgreich generiert!")
    print()
    
    # Generierte Dateien auflisten
    generated_files = list(output_dir.rglob("*.py"))
    print(f"Generiert: {len(generated_files)} Python-Dateien")
    for gen_file in sorted(generated_files):
        print(f"  ✓ {gen_file.relative_to(output_dir)}")
    print()
    
    # __init__.py Dateien erstellen für bessere Imports
    create_init_files(output_dir)
    
    print("✅ Setup abgeschlossen!")
    print()
    print("Sie können jetzt das Test-Programm ausführen:")
    print("  python test_payment.py")


def create_init_files(output_dir):
    """Erstellt __init__.py Dateien in allen Verzeichnissen"""
    print("Erstelle __init__.py Dateien...")
    
    for dirpath, dirnames, filenames in os.walk(output_dir):
        dir_path = Path(dirpath)
        init_file = dir_path / "__init__.py"
        
        if not init_file.exists():
            init_file.touch()
            print(f"  ✓ {init_file.relative_to(output_dir)}")


if __name__ == "__main__":
    try:
        generate_protos()
    except Exception as e:
        print(f"❌ Fehler: {e}")
        sys.exit(1)
