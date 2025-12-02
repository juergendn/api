"""
Korrigiert die Import-Statements in den generierten Protobuf-Dateien
"""

import os
from pathlib import Path
import re

def fix_imports(file_path):
    """Korrigiert die Imports in einer generierten Python-Datei"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Ersetze "from api.v1 import" mit "from gen.api.v1 import"
    content = re.sub(
        r'from api\.v1 import',
        'from gen.api.v1 import',
        content
    )
    
    # Ersetze "from local.v1 import" mit "from gen.local.v1 import"
    content = re.sub(
        r'from local\.v1 import',
        'from gen.local.v1 import',
        content
    )
    
    # Ersetze "from cloud.v1 import" mit "from gen.cloud.v1 import"
    content = re.sub(
        r'from cloud\.v1 import',
        'from gen.cloud.v1 import',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False


def main():
    """Hauptfunktion"""
    gen_dir = Path(__file__).parent / "gen"
    
    if not gen_dir.exists():
        print("❌ gen/ Verzeichnis nicht gefunden!")
        print("Bitte führen Sie zuerst aus: python generate_protos.py")
        return
    
    print("Korrigiere Imports in generierten Dateien...")
    print()
    
    fixed_count = 0
    total_count = 0
    
    for py_file in gen_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        total_count += 1
        
        if fix_imports(py_file):
            fixed_count += 1
            print(f"  ✓ {py_file.relative_to(gen_dir)}")
    
    print()
    print(f"✅ {fixed_count} von {total_count} Dateien korrigiert")
    print()
    print("Die generierten Dateien sind jetzt bereit!")


if __name__ == "__main__":
    main()
