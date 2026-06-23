param(
    [Parameter(Mandatory=$true)]
    [string]$Payload,

    [string]$Drive = "D:\",
    [string]$Port = "COM17",
    [string]$Harness = "",
    [string]$Bitstream = "build\greymecha_smoke\watchdog_koth_smoke.bit",
    [switch]$BuildBitstream
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root
if ($Harness -eq "") {
    $Harness = Join-Path $Root "tools\badge_harness_safe.py"
}

if ($BuildBitstream) {
    wsl bash -lc "bash scripts/build_bitstream.sh"
}

$buildOutput = wsl bash -lc "bash scripts/compile_payload.sh '$Payload'"
if ($LASTEXITCODE -ne 0) {
    throw "Payload build failed"
}

$wdogWsl = ($buildOutput | Select-Object -Last 1).Trim()
if (-not $wdogWsl.EndsWith(".wdog")) {
    throw "Could not determine built .wdog path from build output: $buildOutput"
}

$wdogWin = Join-Path $Root ($wdogWsl -replace "/", "\")
$bitstreamPath = Join-Path $Root $Bitstream
if (-not (Test-Path $wdogWin)) {
    throw "Built payload not found: $wdogWin"
}
if (-not (Test-Path $bitstreamPath)) {
    throw "Bitstream not found: $bitstreamPath. Run with -BuildBitstream or build scripts/build_bitstream.sh first."
}

$stageDir = Join-Path $Drive "hackin7\watchdog_koth_board_test"
New-Item -ItemType Directory -Force -Path $stageDir | Out-Null
Copy-Item -Force $bitstreamPath (Join-Path $stageDir "watchdog_koth_smoke.bit")
Copy-Item -Force $wdogWin (Join-Path $stageDir "upload_payload.wdog")

python -c "import serial,time; s=serial.Serial('$Port',115200,timeout=0.2,write_timeout=2); s.write(b'\x04'); s.flush(); time.sleep(2); print(s.read(4096)); s.close()"

$runner = "hardware\board_tests\greymecha_uart_upload_generic_run.py"
$harnessArgs = @(
    $Harness,
    "--src", $runner,
    "--drive", $Drive,
    "--port", $Port,
    "--timeout", "60",
    "--settle", "5"
)

function Invoke-Harness {
    $output = & python @harnessArgs 2>&1
    $exitCode = $LASTEXITCODE
    $output | ForEach-Object { Write-Host $_ }
    return @{
        ExitCode = $exitCode
        Output = ($output -join "`n")
    }
}

$first = Invoke-Harness
if ($first.ExitCode -ne 0 -or $first.Output -notmatch "UART_UPLOAD_OK") {
    Write-Host "Harness did not report UART_UPLOAD_OK; retrying once in case CircuitPython dropped the leading 'e' in exec."
    $second = Invoke-Harness
    if ($second.ExitCode -ne 0 -or $second.Output -notmatch "UART_UPLOAD_OK") {
        throw "UART upload failed"
    }
}

