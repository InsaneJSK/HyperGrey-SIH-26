param(
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$Output
)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    if (Test-Path -LiteralPath $Output) { throw 'Choose a new output directory to preserve earlier runs.' }
    New-Item -ItemType Directory -Path $Output | Out-Null
    & ./scripts/build.ps1 *> (Join-Path $Output 'build.log')
    if (-not $?) { throw 'Build or C++ tests failed' }
    & $Python scripts/test_generated.py --output (Join-Path $Output 'generated-lp')
    if ($LASTEXITCODE -ne 0) { throw 'Generated LP regression failed' }
    & $Python scripts/benchmark_lp.py --output (Join-Path $Output 'netlib') --limit 30
    if ($LASTEXITCODE -ne 0) { throw 'Netlib harness failed' }
    & $Python scripts/test_milp.py --output (Join-Path $Output 'milp')
    if ($LASTEXITCODE -ne 0) { throw 'MILP harness failed' }
    & $Python scripts/test_qp.py --output (Join-Path $Output 'qp')
    if ($LASTEXITCODE -ne 0) { throw 'QP harness failed' }
    & ./build/solver_cli.exe examples/blending.lpmini --json > (Join-Path $Output 'blending.json')
    if ($LASTEXITCODE -ne 0) { throw 'Blending demo failed' }
    & ./build/solver_cli.exe examples/production.mps --milp --json > (Join-Path $Output 'production.json')
    if ($LASTEXITCODE -ne 0) { throw 'Production demo failed' }
    & ./build/solver_cli.exe examples/dispatch.qplib --json > (Join-Path $Output 'dispatch.json')
    if ($LASTEXITCODE -ne 0) { throw 'Dispatch demo failed' }
    Write-Output 'Validation completed. Review all dataset failures in results.json; harness completion does not mean every benchmark passed.'
} finally { Pop-Location }
