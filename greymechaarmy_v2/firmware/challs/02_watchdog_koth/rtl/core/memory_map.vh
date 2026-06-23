`ifndef WATCHDOG_KOTH_MEMORY_MAP_VH
`define WATCHDOG_KOTH_MEMORY_MAP_VH

`define BOOT_BASE          32'h0000_0000
`define BOOT_END           32'h0000_7fff
`define PAYLOAD_BASE       32'h0000_8000
`define PAYLOAD_END        32'h0000_bfff
`define STACK_BASE         32'h0000_c000
`define STACK_END          32'h0000_cfff

`define UART_BASE          32'h1000_0000
`define UART_END           32'h1000_00ff
`define LED_BASE           32'h1000_0100
`define LED_END            32'h1000_01ff
`define WATCHDOG_BASE      32'h1000_0200
`define WATCHDOG_END       32'h1000_02ff
`define RESET_STATUS_BASE  32'h1000_0300
`define RESET_STATUS_END   32'h1000_03ff
`define DISPLAY_BASE       32'h1000_1000
`define DISPLAY_END        32'h1000_1fff
`define FLAG_BASE          32'h2000_0000
`define FLAG_END           32'h2000_00ff

`define UNMAPPED_RDATA     32'hbad0_add5

`define RESET_CLEAN_BOOT   32'h0000_0000
`define RESET_WATCHDOG     32'h0000_0001
`define RESET_REGION       32'h0000_0002
`define RESET_PAYLOAD_FAULT 32'h0000_0003
`define RESET_NO_SUCCESS   32'h0000_0004
`define RESET_SUCCESS      32'h0000_0005

`endif
