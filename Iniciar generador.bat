@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo Primero ejecuta instalar.bat
    pause
    exit /b 1
)
start "" /min cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"
.venv\Scripts\python.exe app.py
pause
