#include "loader.h"
#include "selftest.h"
#include "uart.h"
#include "../include/memory_map.h"
#include "../include/mmio.h"
#include "../include/status_codes.h"

struct cycle64 {
    u32 high;
    u32 low;
};

static void report_reset_reason(void)
{
    u32 reason = mmio_read32(RESET_REASON_REG);

    if (reason == RESET_CLEAN_BOOT) {
        return;
    }

    if (reason == RESET_WATCHDOG) {
        uart_puts("BOOT WATCHDOG: WATCHDOG_RESET");
    } else if (reason == RESET_REGION) {
        uart_puts("BOOT WATCHDOG: REGION_RESET");
    } else if (reason == RESET_PAYLOAD_FAULT) {
        uart_puts("BOOT WATCHDOG: PAYLOAD_FAULT");
    } else if (reason == RESET_NO_SUCCESS) {
        uart_puts("BOOT WATCHDOG: NO_SUCCESS");
    } else if (reason == RESET_SUCCESS) {
        uart_puts("BOOT WATCHDOG: SUCCESS");
    } else {
        uart_puts("BOOT WATCHDOG: RESET_UNKNOWN");
        uart_put_hex32(reason);
        uart_putc('\n');
    }
}

static struct cycle64 read_cycle64(void)
{
    u32 high_before;
    struct cycle64 value;

    do {
        high_before = mmio_read32(CYCLE_HIGH_REG);
        value.low = mmio_read32(CYCLE_LOW_REG);
        value.high = mmio_read32(CYCLE_HIGH_REG);
    } while (high_before != value.high);

    return value;
}

static struct cycle64 cycle_delta(struct cycle64 end, struct cycle64 start)
{
    struct cycle64 value;

    value.low = end.low - start.low;
    value.high = end.high - start.high;
    if (end.low < start.low) {
        value.high--;
    }
    return value;
}

static void uart_put_cycle_line(const char *label, struct cycle64 value)
{
    while (*label != '\0') {
        uart_putc((u8)*label);
        label++;
    }
    uart_put_hex64_parts(value.high, value.low);
    uart_putc('\n');
}

static void watchdog_disable(void)
{
    mmio_write32(WATCHDOG_BASE + 0x00u, 0u);
}

int main(void)
{
    report_reset_reason();

    if (!selftest_run()) {
        uart_puts("BOOT: SELFTEST_FAIL");
    } else {
        uart_puts("BOOT: SELFTEST_OK");
    }

    while (1) {
        uart_puts("BOOT: READY");

        if (!loader_receive_payload()) {
            uart_puts("BOOT: UPLOAD_ERROR");
            continue;
        }

        uart_puts("BOOT: LOADED");
        uart_puts("BOOT: RUNNING");
        uart_wait_till_tx_clear();
        struct cycle64 cycle_start = read_cycle64();
        loader_jump_to_payload();
        watchdog_disable();
        struct cycle64 cycle_end = read_cycle64();
        uart_put_cycle_line("BOOT: CYCLE_START ", cycle_start);
        uart_put_cycle_line("BOOT: CYCLE_END ", cycle_end);
        uart_put_cycle_line("BOOT: CYCLE_DELTA ", cycle_delta(cycle_end, cycle_start));
        uart_puts("BOOT: DONE");
    }
}
