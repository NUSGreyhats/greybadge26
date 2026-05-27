from array import array
import board
from rp2pio import StateMachine
from adafruit_pioasm import assemble

import leaky_gpio25

"""
A PIO is used to encode bits into short (12 cycles) and long (32 cycles) pulses on GPIO25. 
However, it is difficult to measure this with CPU-sampling due to its short durations (<1ms). 
Instead, we use another PIO available on the RP2040 to sniff this high-speed pulses, as the 
PIO block runs independently at 150MHz, allowing cycle-accurate pulse counting (6.66ns ticks).

For this example, we wire GPIO25 to GPIO24 and sample on GPIO24.

Each RP2040 PIO has only four 32-bit RX-FIFO entries. Without packing, capturing a 64-edge
(low -> high) burst would overflow the FIFO. To avoid this, we pack four 8-bit width counts into
one 32-bit FIFO word, then DMA the packed data into RAM. After transmission, we unpack,
convert loop counts to microseconds, apply a threshold, and reconstruct the ASCII flag.
"""

program = """ 
.program measure_pulse_packed
    wait 1 pin 0       ; block until pin is HIGH

next_pulse:
    mov x, !null       ; dummy value (all 1s)

count_high:
    jmp pin, do_count
    mov osr, !x        ; pin went low, so we copy width
    in  osr, 8         ; pack 8 bits into ISR
    wait 1 pin 0
    jmp  next_pulse    ; start next measurement

do_count:
    jmp x-- count_high ; decrement x while pin is high
.wrap
"""
binary = assemble(program)

SYSCLK = 150_000_000

sm_rx = StateMachine(
    program        = binary,
    first_in_pin   = board.GP24,
    jmp_pin        = board.GP24,
    in_pin_count   = 1,
    frequency      = SYSCLK,
    auto_push      = True, # auto pushes after 32 shifted bits
    push_threshold = 32,
    in_shift_right = False
)

def read_pulses():
    while sm_rx.reading: # Blocks until DMA completes reading from RX FIFO
        pass

    bits  = []
    count = 0
    shifts = (24, 16, 8, 0)  # MSB to LSB order

    for word in buf:
        for shift in shifts:
            loops = (word >> shift) & 0xFF # 1 cycle = 6.67 ns @ 150 MHz
            cycles = loops * 2
            pulse  = cycles / SYSCLK * 1e6 

            # 0.1ms is the threshold for a short pulse. Participants should adjust this based on the output they see!
            threshold = 0.1 # ms
            bit = "1" if pulse > threshold else "0"
            bits.append(bit)
            print(f"Pulse {count+1:3d}: {pulse:.3f} µs -> bit {bit}")

            count += 1
    print(f"Done. Read {count} pulses.")
    bitstring = "".join(bits)
    return bitstring

"""
Set up DMA to get data from RX FIFO. 
This must be done before the transmitter starts sending data, else the RX FIFO will overflow.

For no. of pulses, you can either gradually increase this number to find the right answer
for the data size (it will block forever if it is too large as the buffer blocks until it is full),
or use a timeout to cut off data from fifo into the buffer otherwise it will block forever
"""
pulses = 224 
words = pulses // 4
buf = array("I", [0] * words) # DMA-once buffer
sm_rx.background_read(buf)

# Launch the transmitter
print("Starting transmission…")
leaky_gpio25.secret_in_gpio25()

# Read pulses from DMA (this function will block until DMA is done reading)
bitstring = read_pulses()

# Decode bitstring
flag = "".join(chr(int(bitstring[i:i+8], 2)) for i in range(0, len(bitstring), 8))
print(f"Decoded: {flag}")
