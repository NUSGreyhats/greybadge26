import hardware.fpga
jtag_rst = hardware.fpga.upload_bitstream("/projects/main.bit")

'''
import busio
import board
import digitalio

tft_clk = board.GP2 # must be a SPI CLK
tft_mosi= board.GP3 # must be a SPI TX
tft_rst = board.GP6
tft_dc  = board.GP4
tft_cs  = board.GP5 # optional, can be "None"
tft_bl  = None      # optional, can be "None"


spi = busio.SPI(clock=tft_clk, MOSI=tft_mosi)
while not spi.try_lock():
    pass

result = bytearray(4)
spi.readinto(result)
print(result)
cs = digitalio.DigitalInOut(tft_cs)
cs.direction = digitalio.Direction.INPUT
dc = digitalio.DigitalInOut(tft_dc)
dc.direction = digitalio.Direction.INPUT
'''