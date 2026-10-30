@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo No se encontro Python Launcher. Instala Python 3.11 o superior.
    pause
    exit /b 1
)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo Error creando el entorno virtual.
    pause
    exit /b 1
)
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error instalando dependencias.
    pause
    exit /b 1
)
if not exist .env copy .env.example .env >nul
echo.
echo Instalacion terminada. Edita el archivo .env para configurar OPENAI_API_KEY.
pause
