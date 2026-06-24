#ifndef WATCHDOG_KOTH_UART_H
#define WATCHDOG_KOTH_UART_H

#include "../include/mmio.h"

void uart_wait_till_tx_clear();
void uart_putc(u8 value);
void uart_puts(const char *value);
int uart_getc_timeout(u8 *value, u32 timeout);
void uart_put_hex32(u32 value);
void uart_put_hex64_parts(u32 high, u32 low);

#endif
