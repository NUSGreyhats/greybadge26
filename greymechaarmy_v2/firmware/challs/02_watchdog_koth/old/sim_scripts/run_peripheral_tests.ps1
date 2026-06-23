param(
    [string]$BuildDir = "build/sim"
)

$ErrorActionPreference = "Stop"

$iverilog = Get-Command iverilog -ErrorAction Stop
$vvp = Get-Command vvp -ErrorAction Stop

New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

& $iverilog.Source `
    -I rtl/core `
    -o "$BuildDir/tb_peripherals.vvp" `
    sim/tb/tb_peripherals.v `
    rtl/peripherals/uart_mmio.v `
    rtl/peripherals/led_mmio.v `
    rtl/peripherals/watchdog.v

& $vvp.Source "$BuildDir/tb_peripherals.vvp"
