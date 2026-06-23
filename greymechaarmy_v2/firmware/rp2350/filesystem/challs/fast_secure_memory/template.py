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
    bitstream = "/tmp/main.bit" if "main.bit" in os.listdir("/tmp") else "/hardware/bitstreams/main.bit"
    if bitstream == "/tmp/main.bit" or "main.bit" in os.listdir("/hardware/bitstreams"):
        print("Uploading", bitstream)
        rst = hardware.fpga.upload_bitstream(bitstream)
        time.sleep(0.25)
        return rst
    else:
        print("No main.bit found; using current FPGA bitstream")
        return None

fpga_rst = setup_fpga()


### Setup your code here ##################
