@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ==========================================
echo     ImagenesGPT - Instalacion local
echo ==========================================
echo.

rem Reutilizar el entorno virtual si ya existe y es valido.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1
    if errorlevel 1 (
        echo El entorno .venv existente no funciona o usa Python anterior a 3.11.
        echo No se ha borrado ninguna carpeta. Revisalo antes de continuar.
        goto error
    )
    goto instalar_dependencias
)

rem Miniforge/Conda suele disponer de python, pero no del comando py.
set "PYTHON_EXE="
set "PYTHON_ARGS="
where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_EXE=py"
        set "PYTHON_ARGS=-3"
    )
)
if not defined PYTHON_EXE (
    where python >nul 2>&1
    if not errorlevel 1 (
        python -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1
        if not errorlevel 1 set "PYTHON_EXE=python"
    )
)
if not defined PYTHON_EXE (
    where python3 >nul 2>&1
    if not errorlevel 1 (
        python3 -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1
        if not errorlevel 1 set "PYTHON_EXE=python3"
    )
)
if not defined PYTHON_EXE (
    if defined CONDA_PREFIX (
        if exist "%CONDA_PREFIX%\python.exe" (
            "%CONDA_PREFIX%\python.exe" -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1
            if not errorlevel 1 set "PYTHON_EXE=%CONDA_PREFIX%\python.exe"
        )
    )
)

if not defined PYTHON_EXE (
    echo.
    echo No se encontro una instalacion accesible de Python 3.11 o superior.
    echo.
    echo Abre PowerShell y ejecuta:
    echo     python --version
    echo     py --version
    echo     where.exe python
    echo.
    echo Si utilizas Miniforge, abre Miniforge Prompt, activa un entorno
    echo con Python 3.11 o superior y ejecuta instalar.bat desde ahi.
    echo No es obligatorio instalar Python otra vez si ya lo tienes.
    goto error
)

echo Python detectado mediante: "%PYTHON_EXE%" %PYTHON_ARGS%
echo Creando entorno virtual .venv ...
"%PYTHON_EXE%" %PYTHON_ARGS% -m venv ".venv"
if errorlevel 1 (
    echo No se pudo crear .venv. Comprueba que Python incluya venv.
    goto error
)

:instalar_dependencias
echo.
echo Instalando dependencias en el entorno local...
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 (
    echo Error instalando dependencias. Revisa los mensajes anteriores.
    goto error
)

if not exist ".env" (
    copy ".env.example" ".env" >nul
    if errorlevel 1 (
        echo No se pudo crear el archivo .env.
        goto error
    )
)

echo.
echo Instalacion completada correctamente.
echo Abre .env y configura OPENAI_API_KEY antes de generar imagenes.
pause
exit /b 0

:error
echo.
echo La instalacion NO se completo.
pause
exit /b 1
