#define UART_BASE      0x10000000u
#define UART_TXDATA    0x00u
#define UART_STATUS    0x04u
#define UART_TX_READY  0x00000001u
#define LED_BASE       0x10000100u
#define FLAG_BASE      0x20000000u

#define UART_CHAR      0x10000000u // UART_BASE + UART_TXDATA

static unsigned int read32(unsigned int addr)
{
    return *(volatile unsigned int *)addr;
}

static void write32(unsigned int addr, unsigned int value)
{
    *(volatile unsigned int *)addr = value;
}

static void uart_putc(unsigned int value)
{
    //while ((read32(UART_BASE + UART_STATUS) & UART_TX_READY) == 0u) {}
    write32(UART_BASE + UART_TXDATA, value);
}

static void uart_puts(const char *value)
{
    while (*value != '\0') {
        uart_putc((unsigned int)*value);
        value++;
    }
    uart_putc('\n');
}

int main(void)
{
    *(volatile unsigned int *)0x10000200u = 0u; // Disable MMIO
    *(volatile unsigned int *)UART_CHAR = 'g';
    *(volatile unsigned int *)UART_CHAR = 'r';
    *(volatile unsigned int *)UART_CHAR = 'e';
    *(volatile unsigned int *)UART_CHAR = 'y';
    *(volatile unsigned int *)UART_CHAR = '{';
    *(volatile unsigned int *)UART_CHAR = 'm';
    *(volatile unsigned int *)UART_CHAR = 'm';
    *(volatile unsigned int *)UART_CHAR = 'i';
    *(volatile unsigned int *)UART_CHAR = 'o';
    *(volatile unsigned int *)UART_CHAR = '_';
    *(volatile unsigned int *)UART_CHAR = 'f';
    *(volatile unsigned int *)UART_CHAR = 'u';
    *(volatile unsigned int *)UART_CHAR = 'z';
    *(volatile unsigned int *)UART_CHAR = 'z';
    *(volatile unsigned int *)UART_CHAR = 'z';
    *(volatile unsigned int *)UART_CHAR = '}';
    *(volatile unsigned int *)UART_CHAR = '\n';
}

// Main difference is enabling O3 flag

/*
[UART]: BOOT: LOADED
[UART]: BOOT: RUNNING
[UART]: grey{mmio_fuzzz}
[UART]: BOOT: CYCLE_START 0x00000000063baeb1
[UART]: BOOT: CYCLE_END 0x00000000063bb1c6
[UART]: BOOT: CYCLE_DELTA 0x0000000000000315
*/