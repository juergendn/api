"""
Build-Skript für Windows EXE
Erstellt eine ausführbare Datei mit PyInstaller
"""
import PyInstaller.__main__
import sys
import os

# Absoluter Pfad zum Skript-Verzeichnis
script_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'web_app.py',
    '--name=SENVEND_Terminal_Test',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    '--add-data=templates;templates',
    '--add-data=static;static',
    '--add-data=gen;gen',
    '--hidden-import=grpc',
    '--hidden-import=google.protobuf',
    '--hidden-import=flask',
    '--hidden-import=asyncio',
    '--collect-all=grpc',
    '--collect-all=google.protobuf',
    '--noconfirm',
])

print("\n" + "="*60)
print("✅ EXE erfolgreich erstellt!")
print("="*60)
print(f"\nSpeicherort: {os.path.join(script_dir, 'dist', 'SENVEND_Terminal_Test.exe')}")
print("\nDoppelklick auf die EXE startet den Webserver.")
print("Dann Browser öffnen: http://localhost:5000")
print("="*60)
