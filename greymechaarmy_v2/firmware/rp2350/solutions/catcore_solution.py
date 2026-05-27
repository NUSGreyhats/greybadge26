import board
import busio
import digitalio
import time
import hardware


### Dev Mode Unlock ##############################################################################################
print("-"*80)
print("Make Sure to short your Flash CS Pin first")
input()

overlay = hardware.hw_state["fpga_overlay"]
hardware.display_text(hardware.hw_state, "CTF Mode")
print("Initialising FPGA...")
overlay.init()

### Need clear Pins first #######################
DATA_PINS_NO = [board.GP8, board.GP9, board.GP10, board.GP11, board.GP12]
pins = []
overlay.set_mode((0, 0, 0))
for p in DATA_PINS_NO:
    d = digitalio.DigitalInOut(p)
    d.direction = digitalio.Direction.OUTPUT
    d.value = False
    pins.append(d)
            
for d in pins:
    d.deinit()

### Configure UART GPIO #########################
overlay.set_mode((0,1,1))
uart = busio.UART(board.GP8, board.GP9, baudrate=9600, timeout=0.1)
            
uart.write("AAA")



### CatCore Hyper #####################################################################################
print("-"*80)
def xor_decode(a: str, b: str, l: int):
    c = ""
    for i in range(l):
        c = c + (chr(ord(a[i % len(a)]) ^ ord(b[i % len(b)])))
    return c



def run_catcore_hyper_instruction(instr):
    opcode = "D"
    #instr = xor_decode(instr, KEY, len(instr))
    payload = opcode+instr+opcode
    print("payload:", payload, payload.encode(), len(payload))
    uart.write(payload)
    
KEY = "1234567890123456"
def run_catcore_hyper_admin_instruction(instr):
    opcode = "D"
    instr = xor_decode(instr, KEY, len(instr))
    payload = opcode+instr+opcode
    print("payload:", payload, len(payload))
    uart.write(payload)



print("Display Memory:")
address="\x0f"
run_catcore_hyper_instruction("C"+address+"----------DEVC")
print("    >", uart.read())
print()


print("Display Memory:")
address="\x0f"
run_catcore_hyper_instruction("C"+address+"----------DEVC")
print("    >", uart.read())
print()


print("pls short A3 to 3.3v ---------")
input()

print("Display Memory:")
address="\x0f"
run_catcore_hyper_instruction("C"+address+"----------DEVC")
print("    >", uart.read())
print()


## CatCore with signing #####################################################################################
print("-"*80)
KEY = "1234567890123456"
print()
print("Non Devmode Intro - admin:")
run_catcore_hyper_admin_instruction("@--------------@")
print("    >",uart.read())

print("CatCore Flag:")
run_catcore_hyper_admin_instruction("A1w4n7myfl49p15A")
print("    >",uart.read())

print()
 

