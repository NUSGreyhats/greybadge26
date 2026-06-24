#define UART_BASE      0x10000000u
#define UART_TXDATA    0x00u
#define UART_STATUS    0x04u
#define UART_TX_READY  0x00000001u
#define LED_BASE       0x10000100u
#define FLAG_BASE      0x20000000u

#define UART_CHAR      0x10000000u // UART_BASE + UART_TXDATA

int main(void)
{
    //*(volatile unsigned int *)addr = value
    *(volatile unsigned int *)0x10000200u = 0u; // Disable MMIO
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000000u >> 0);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000000u >> 8);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000000u >> 16);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000000u >> 24);

    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000004u >> 0);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000004u >> 8);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000004u >> 16);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000004u >> 24);
    
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000008u >> 0);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000008u >> 8);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000008u >> 16);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x20000008u >> 24);
    
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x2000000cu >> 0);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x2000000cu >> 8);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x2000000cu >> 16);
    *(volatile unsigned int *)UART_CHAR = (*(volatile unsigned int *)0x2000000cu >> 24);

    *(volatile unsigned int *)UART_CHAR = '\n';
}

/*
Optimisations done
1. Loop unrolled the word loop
2. Removed UART Check
3. Removed & operation
*/

/*
[UART]: BOOT: LOADED
[UART]: BOOT: RUNNING
[UART]: grey{mmio_fuzzz}
[UART]: BOOT: CYCLE_START 0x0000000006d6df78
[UART]: BOOT: CYCLE_END 0x0000000006d6e1a4
[UART]: BOOT: CYCLE_DELTA 0x000000000000022c
[UART]: BOOT: DONE
[UART]: BOOT: READY
*/