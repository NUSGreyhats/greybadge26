param(
    [Parameter(Mandatory=$true)]
    [string]$Payload,

    [string]$Drive = "D:\",
    [string]$Port = "COM17",
    [string]$Harness = "",
    [string]$Bitstream = "build\greymecha_smoke\watchdog_koth_smoke.bit",
    [switch]$BuildBitstream
)

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
& (Join-Path $Root "scripts\upload_greymecha.ps1") `
    -Payload $Payload `
    -Drive $Drive `
    -Port $Port `
    -Harness $Harness `
    -Bitstream $Bitstream `
    -BuildBitstream:$BuildBitstream
exit $LASTEXITCODE
