#define UART_BASE      0x10000000u
#define UART_TXDATA    0x00u
#define UART_STATUS    0x04u
#define UART_TX_READY  0x00000001u
#define LED_BASE       0x10000100u
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
    while ((read32(UART_BASE + UART_STATUS) & UART_TX_READY) == 0u) {}
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

static void uart_put_word_bytes(unsigned int value)
{
    uart_putc(value & 0xffu);
    uart_putc((value >> 8) & 0xffu);
    uart_putc((value >> 16) & 0xffu);
    uart_putc((value >> 24) & 0xffu);
}

int main(void)
{
    unsigned int words = (read32(FLAG_BASE + 0xf0u)) / 4u;
    for (unsigned int i = 0; i < words; i++) {uart_put_word_bytes(read32(FLAG_BASE + (i * 4u)));}
    uart_putc('\n');
}