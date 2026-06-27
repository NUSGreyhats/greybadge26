import microcontroller
import supervisor

from challs.watchdog_oled import autorun


BITSTREAM = "/challs/watchdog_oled/watchdog_koth_oled.bit"
PAYLOAD = "/challs/watchdog_oled/payload.wdog"


def main():
    print("WDOG_OLED: scheduling autorun")
    autorun.write_autorun_marker(microcontroller.nvm, BITSTREAM, PAYLOAD)
    supervisor.reload()


main()
