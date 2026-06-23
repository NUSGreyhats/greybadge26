import gc
import os
import struct
import time

#import adafruit_pioasm
import board
import digitalio
import hardware.fpga
#import rp2pio

def setup_fpga():
    rst = hardware.fpga.upload_bitstream("/challs/fast_secure_memory/main.bit")
    return rst

fpga_rst = setup_fpga()


### Setup your code here ##################

