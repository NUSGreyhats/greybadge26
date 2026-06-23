#define LED_BASE       0x10000100u
#define WATCHDOG_BASE  0x10000200u
#define WATCHDOG_CTRL  0x00u
#define WATCHDOG_LIMIT 0x04u

static void write32(unsigned int addr, unsigned int value)
{
    *(volatile unsigned int *)addr = value;
}

int main(void)
{
    write32(LED_BASE, 0x00000071u);
    write32(WATCHDOG_BASE + WATCHDOG_LIMIT, 16u);
    write32(WATCHDOG_BASE + WATCHDOG_CTRL, 0x00000007u);

    while (1) {
    }
}
