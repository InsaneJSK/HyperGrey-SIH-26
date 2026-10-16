param([string]$Compiler = 'g++')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    & cmake -S . -B build-v2 -G 'MinGW Makefiles' -DCMAKE_BUILD_TYPE=Release "-DCMAKE_CXX_COMPILER=$Compiler"
    if ($LASTEXITCODE -ne 0) { throw 'CMake configuration failed' }
    & cmake --build build-v2 -j 4
    if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
    & ctest --test-dir build-v2 --output-on-failure
    if ($LASTEXITCODE -ne 0) { throw 'Correctness tests failed' }
    New-Item -ItemType Directory -Force build | Out-Null
    Copy-Item -LiteralPath build-v2/solver_cli.exe -Destination build/solver_cli.exe
} finally { Pop-Location }
