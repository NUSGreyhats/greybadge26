param(
    [string]$BuildDir = "build/sim"
)

$ErrorActionPreference = "Stop"

$iverilog = Get-Command iverilog -ErrorAction Stop
$vvp = Get-Command vvp -ErrorAction Stop

New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

& $iverilog.Source `
    -I rtl/core `
    -o "$BuildDir/tb_soc_bus.vvp" `
    sim/tb/tb_soc_bus.v `
    rtl/top/watchdog_koth_top.v `
    rtl/core/soc_bus.v `
    rtl/core/picorv32.v `
    rtl/peripherals/uart_mmio.v `
    rtl/peripherals/led_mmio.v `
    rtl/peripherals/display_mmio.v `
    rtl/peripherals/simple_spi_master.v `
    rtl/peripherals/watchdog.v `
  rtl/peripherals/reset_reason.v `
  rtl/peripherals/flag_rom.v

& $vvp.Source "$BuildDir/tb_soc_bus.vvp"
