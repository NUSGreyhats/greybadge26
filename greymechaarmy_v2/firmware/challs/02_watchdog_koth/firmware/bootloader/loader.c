#include "loader.h"
#include "uart.h"
#include "../include/memory_map.h"
#include "../include/mmio.h"
#include "../include/status_codes.h"

#define UART_TIMEOUT 100000000u
#define WATCHDOG_REGION_BASE 0x00000000u
#define WATCHDOG_REGION_END  0xffffffffu

extern void jump_to_payload_asm(u32 entry, u32 stack_top);

static int read_byte(u8 *value)
{
    return uart_getc_timeout(value, UART_TIMEOUT);
}

static int read_u32_le(u32 *value)
{
    u8 b0;
    u8 b1;
    u8 b2;
    u8 b3;

    if (!read_byte(&b0)) return 0;
    if (!read_byte(&b1)) return 0;
    if (!read_byte(&b2)) return 0;
    if (!read_byte(&b3)) return 0;

    *value = ((u32)b0) | ((u32)b1 << 8) | ((u32)b2 << 16) | ((u32)b3 << 24);
    return 1;
}

static int read_magic(void)
{
    u32 matched = 0u;

    while (matched != 4u) {
        u8 byte_value;
        if (!read_byte(&byte_value)) {
            return 0;
        }

        if (matched == 0u && byte_value == 'W') {
            matched = 1u;
        } else if (matched == 1u && byte_value == 'D') {
            matched = 2u;
        } else if (matched == 2u && byte_value == 'O') {
            matched = 3u;
        } else if (matched == 3u && byte_value == 'G') {
            matched = 4u;
        } else if (byte_value == 'W') {
            matched = 1u;
        } else {
            matched = 0u;
        }
    }

    return 1;
}

static void clear_payload(void)
{
    volatile u32 *word = (volatile u32 *)PAYLOAD_BASE;
    u32 count = PAYLOAD_SIZE / 4u;
    u32 i;

    for (i = 0; i < count; i++) {
        word[i] = 0u;
    }
}

int loader_receive_payload(void)
{
    u32 length;
    u32 i;
    volatile u8 *payload = (volatile u8 *)PAYLOAD_BASE;

    if (!read_magic()) {
        return 0;
    }

    if (!read_u32_le(&length) || length == 0u || length > PAYLOAD_SIZE) {
        return 0;
    }

    clear_payload();

    for (i = 0; i < length; i++) {
        u8 byte_value;
        if (!read_byte(&byte_value)) {
            return 0;
        }
        payload[i] = byte_value;
    }

    return 1;
}

void loader_jump_to_payload(void)
{
    mmio_write32(WATCHDOG_BASE + 0x10u, WATCHDOG_REGION_BASE);
    mmio_write32(WATCHDOG_BASE + 0x14u, WATCHDOG_REGION_END);
    mmio_write32(WATCHDOG_BASE + 0x00u, WATCHDOG_ENABLE | WATCHDOG_ARM | WATCHDOG_CLEAR);
    jump_to_payload_asm(PAYLOAD_BASE, STACK_TOP);
}
