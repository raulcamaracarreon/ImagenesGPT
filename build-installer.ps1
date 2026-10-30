# Segunda etapa: compilar instalador y desinstalador con Inno Setup 7 o 6.
# Ejecutar solo tras validar dist\ImagenesGPT\ImagenesGPT.exe en Windows.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$portableDir = Join-Path $PSScriptRoot "dist\ImagenesGPT"
$exe = Join-Path $portableDir "ImagenesGPT.exe"
if (-not (Test-Path $exe)) {
    throw "Primero compila y valida el ejecutable portatil con .\build-portable.ps1"
}

# Admitir las dos versiones de Inno Setup (7 y 6) y ambas rutas de Windows.
$installDirs = @(
    [Environment]::GetEnvironmentVariable("ProgramFiles"),
    [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
) | Where-Object { $_ } | Select-Object -Unique

$candidates = foreach ($installDir in $installDirs) {
    foreach ($version in @(7, 6)) {
        Join-Path $installDir "Inno Setup $version\ISCC.exe"
    }
}
$compiler = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $compiler) {
    $command = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
    if ($command) { $compiler = $command.Source }
}
if (-not $compiler) {
    throw "No se encontro Inno Setup 7 ni 6. Instalalo desde https://jrsoftware.org/isdl.php solo en la PC de desarrollo."
}

Write-Host "Compilador encontrado: $compiler"
& $compiler (Join-Path $PSScriptRoot "installer\ImagenesGPT.iss")
if ($LASTEXITCODE -ne 0) { throw "No se pudo generar el instalador." }

$setup = Join-Path $PSScriptRoot "dist\setup\ImagenesGPT-Setup-1.0.0.exe"
if (-not (Test-Path $setup)) {
    throw "Inno Setup finalizo, pero no se encontro el archivo esperado: $setup"
}
Write-Host "Instalador creado: $setup" -ForegroundColor Green
Write-Host "El instalador incluye un desinstalador en Aplicaciones instaladas."
Write-Host "Las imagenes personales y la clave API guardada NO se eliminan al desinstalar."
