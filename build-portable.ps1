# Versión portátil: dist\ImagenesGPT\ImagenesGPT.exe
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if ($env:OS -ne "Windows_NT") {
    throw "El ejecutable para Windows debe compilarse en Windows."
}
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Falta .venv. Ejecuta .\instalar.bat primero."
}
& $python -c "import tkinter; print('Tk disponible:', tkinter.TkVersion)"
if ($LASTEXITCODE -ne 0) {
    throw "Tkinter no esta disponible. No se genero ningun ejecutable."
}
& $python -m pip install -r "requirements-build.txt"
if ($LASTEXITCODE -ne 0) { throw "Error instalando herramientas de empaquetado." }

& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Fallaron las pruebas. Compilacion cancelada." }

& $python -m PyInstaller --noconfirm --clean "ImagenesGPT.spec"
if ($LASTEXITCODE -ne 0) { throw "PyInstaller no termino correctamente." }

$exe = Join-Path $PSScriptRoot "dist\ImagenesGPT\ImagenesGPT.exe"
if (-not (Test-Path $exe)) { throw "No se encontro el ejecutable compilado." }
Write-Host "Ejecutable listo en: $exe" -ForegroundColor Green
Write-Host "IMPORTANTE: para compartirlo, incluye toda la carpeta dist\ImagenesGPT."
