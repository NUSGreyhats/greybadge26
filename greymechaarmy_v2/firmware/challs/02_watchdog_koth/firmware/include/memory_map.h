#ifndef WATCHDOG_KOTH_MEMORY_MAP_H
#define WATCHDOG_KOTH_MEMORY_MAP_H

#define BOOT_BASE          0x00000000u
#define BOOT_END           0x00007fffu
#define PAYLOAD_BASE       0x00008000u
#define PAYLOAD_END        0x0000bfffu
#define STACK_BASE         0x0000c000u
#define STACK_END          0x0000cfffu

#define UART_BASE          0x10000000u
#define LED_BASE           0x10000100u
#define WATCHDOG_BASE      0x10000200u
#define RESET_STATUS_BASE  0x10000300u
#define RESET_REASON_REG   (RESET_STATUS_BASE + 0x00u)
#define CYCLE_LOW_REG      (RESET_STATUS_BASE + 0x04u)
#define CYCLE_HIGH_REG     (RESET_STATUS_BASE + 0x08u)
#define DISPLAY_BASE       0x10001000u
#define FLAG_BASE          0x20000000u

#define PAYLOAD_SIZE       (PAYLOAD_END - PAYLOAD_BASE + 1u)
#define STACK_TOP          (STACK_END + 1u)

#endif
