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
1. Remove byte shifting and loop unroll
*/

/*
WDOG_UPLOAD: sending_payload=172 bytes
[UART]: BOOT: LOADED
[UART]: BOOT: RUNNING
[UART]: grey{mmio_fuzzz}
[UART]: BOOT: CYCLE_START 0x000000000653561c
[UART]: BOOT: CYCLE_END 0x00000000065357d6
[UART]: BOOT: CYCLE_DELTA 0x00000000000001ba
[UART]: BOOT: DONE
[UART]: BOOT: READY
*/