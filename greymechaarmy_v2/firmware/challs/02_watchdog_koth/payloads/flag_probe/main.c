#define LED_BASE       0x10000100u
#define UART_BASE      0x10000000u
#define UART_TXDATA    0x00u
#define UART_STATUS    0x04u
#define UART_TX_READY  0x00000001u
#define WATCHDOG_BASE  0x10000200u
#define WATCHDOG_CTRL  0x00u
#define FLAG_BASE      0x20000000u

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
    while ((read32(UART_BASE + UART_STATUS) & UART_TX_READY) == 0u) {
    }
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
    write32(WATCHDOG_BASE + WATCHDOG_CTRL, 0u);

    if (read32(FLAG_BASE + 0x00u) != 0x79657267u) goto fail;
    if (read32(FLAG_BASE + 0x04u) != 0x696d6d7bu) goto fail;
    if (read32(FLAG_BASE + 0x08u) != 0x75665f6fu) goto fail;
    if (read32(FLAG_BASE + 0x0cu) != 0x7d7a7a7au) goto fail;
    if (read32(FLAG_BASE + 0x10u) != 0x00000000u) goto fail;
    if (read32(FLAG_BASE + 0xf0u) != 16u) goto fail;
    if (read32(FLAG_BASE + 0xf4u) != 1u) goto fail;
    if (read32(FLAG_BASE + 0xf8u) != 0u) goto fail;

    write32(LED_BASE, 0x000000f1u);
    uart_puts("FLAG_OK");
    while (1) {
    }

fail:
    write32(LED_BASE, 0x000000e1u);
    uart_puts("FLAG_FAIL");
    while (1) {
    }
}
