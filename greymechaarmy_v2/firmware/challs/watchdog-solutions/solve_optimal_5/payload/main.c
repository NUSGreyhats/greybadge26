#define UART_BASE      0x10000000u
#define UART_TXDATA    0x00u
#define UART_STATUS    0x04u
#define UART_TX_READY  0x00000001u
#define LED_BASE       0x10000100u
#define FLAG_BASE      0x20000000u

#define UART_CHAR      0x10000000u // UART_BASE + UART_TXDATA

int main(void){}

/*
Optimisations done
1. Move Optimization 4 to Assembly
*/

/*
WDOG_UPLOAD: sending_payload=244 bytes
[UART]: BOOT: LOADED
[UART]: BOOT: RUNNING
[UART]: grey{mmio_fuzzz}
[UART]: BOOT: CYCLE_START 0x00000000073bb8d0
[UART]: BOOT: CYCLE_END 0x00000000073bbafc
[UART]: BOOT: CYCLE_DELTA 0x000000000000022c
[UART]: BOOT: DONE
[UART]: BOOT: READY
*/