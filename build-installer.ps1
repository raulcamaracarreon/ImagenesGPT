# Segunda etapa. Utilizar SOLO despues de validar dist\ImagenesGPT\ImagenesGPT.exe.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$exe = Join-Path $PSScriptRoot "dist\ImagenesGPT\ImagenesGPT.exe"
if (-not (Test-Path $exe)) {
    throw "Primero compila y valida el portable con .\build-portable.ps1"
}

$programFiles86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
$programFiles = [Environment]::GetEnvironmentVariable("ProgramFiles")
$potentialPaths = @()
if ($programFiles86) { $potentialPaths += (Join-Path $programFiles86 "Inno Setup 6\ISCC.exe") }
if ($programFiles) { $potentialPaths += (Join-Path $programFiles "Inno Setup 6\ISCC.exe") }
$compiler = $potentialPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $compiler) {
    $command = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
    if ($command) { $compiler = $command.Source }
}
if (-not $compiler) {
    throw "Falta Inno Setup 6 en este equipo. Solo se necesita para crear el instalador."
}

& $compiler (Join-Path $PSScriptRoot "installer\ImagenesGPT.iss")
if ($LASTEXITCODE -ne 0) { throw "Falló la compilación del instalador." }
Write-Host "Instalador disponible en dist\setup\" -ForegroundColor Green
