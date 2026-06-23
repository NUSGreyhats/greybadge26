#define LED_BASE       0x10000100u
#define WATCHDOG_BASE  0x10000200u
#define WATCHDOG_CTRL  0x00u

static void mmio_write32(unsigned int addr, unsigned int value)
{
    *(volatile unsigned int *)addr = value;
}

static void delay_100ms(void)
{
    volatile unsigned int i;

    /*
     * The GreyMecha OSCG DIV=8 build reports a derived clock around 38.75 MHz.
     * This empty volatile loop is a hardware-visible timing approximation for
     * a 0.1 s LED cadence and can be adjusted after visual measurement.
     */
    for (i = 0; i < 100000u; i++) {
    }
}

int main(void)
{
    unsigned int value = 0u;

    mmio_write32(WATCHDOG_BASE + WATCHDOG_CTRL, 0u);

    while (1) {
        mmio_write32(LED_BASE, value);
        value = (value + 1u) & 0xffu;
        delay_100ms();
    }
}
