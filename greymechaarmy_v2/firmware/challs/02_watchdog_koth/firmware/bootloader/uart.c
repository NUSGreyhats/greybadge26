#include "uart.h"
#include "../include/memory_map.h"

#define UART_TXDATA 0x00u
#define UART_STATUS 0x04u
#define UART_RXDATA 0x08u
#define UART_TX_READY 0x00000001u
#define UART_RX_FULL  0x00000002u
#define UART_TX_EMPTY 0x00000004u

void uart_wait_till_tx_clear() {
    while ((mmio_read32(UART_BASE + UART_STATUS) & UART_TX_EMPTY) == 0u) { // while not empty
    }
}
void uart_putc(u8 value)
{
    while ((mmio_read32(UART_BASE + UART_STATUS) & UART_TX_READY) == 0u) {
    }
    mmio_write32(UART_BASE + UART_TXDATA, (u32)value);
}

void uart_puts(const char *value)
{
    while (*value != '\0') {
        uart_putc((u8)*value);
        value++;
    }
    uart_putc((u8)'\n');
}

static void uart_put_hex32_digits(u32 value)
{
    static const char hex[] = "0123456789abcdef";
    int shift;

    for (shift = 28; shift >= 0; shift -= 4) {
        uart_putc((u8)hex[(value >> shift) & 0x0f]);
    }
}

int uart_getc_timeout(u8 *value, u32 timeout)
{
    while (timeout != 0u) {
        if ((mmio_read32(UART_BASE + UART_STATUS) & UART_RX_FULL) != 0u) {
            *value = (u8)mmio_read32(UART_BASE + UART_RXDATA);
            return 1;
        }
        timeout--;
    }
    return 0;
}

void uart_put_hex32(u32 value)
{
    uart_putc('0');
    uart_putc('x');
    uart_put_hex32_digits(value);
}

void uart_put_hex64_parts(u32 high, u32 low)
{
    uart_putc('0');
    uart_putc('x');
    uart_put_hex32_digits(high);
    uart_put_hex32_digits(low);
}
