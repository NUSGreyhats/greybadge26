#include "selftest.h"
#include "../include/memory_map.h"
#include "../include/mmio.h"

int selftest_run(void)
{
    mmio_write32(LED_BASE, 0x000000a5u);
    if ((mmio_read32(LED_BASE) & 0xffu) != 0xa5u) {
        return 0;
    }

    mmio_write32(WATCHDOG_BASE + 0x04u, 0x00000100u);
    if (mmio_read32(WATCHDOG_BASE + 0x04u) != 0x00000100u) {
        return 0;
    }

    if (mmio_read32(FLAG_BASE) != 0x79657267u) {
        return 0;
    }

    return 1;
}
