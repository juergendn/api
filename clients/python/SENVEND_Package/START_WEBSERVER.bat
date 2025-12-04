@echo off
echo ============================================================
echo   SENVEND Kartenleser Web-Interface
echo ============================================================
echo.
echo   Starte Webserver...
echo.

cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" web_app.py

pause
