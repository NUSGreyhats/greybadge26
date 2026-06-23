#define LED_BASE       0x10000100u
#define WATCHDOG_BASE  0x10000200u
#define WATCHDOG_CTRL  0x00u

static void write32(unsigned int addr, unsigned int value)
{
    *(volatile unsigned int *)addr = value;
}

int main(void)
{
    void (*outside_payload)(void) = (void (*)(void))0x00000000u;

    write32(WATCHDOG_BASE + WATCHDOG_CTRL, 0u);
    write32(LED_BASE, 0x000000b2u);
    outside_payload();

    while (1) {
    }
}
