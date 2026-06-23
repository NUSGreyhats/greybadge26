# Challenges

Challenges can be found at https://github.com/NUSGreyhats/greyctf25-challs-public/tree/main/finals/hardware 

## Hornet Revenge

### Details

I want revenge.

Stop the backend and run this in the Thonny REPL to start the challenge.

```python
from hornet_revenge import *
```

### Author

Hackin7



## Bricked Up

### Details
Hardware/Reverse

A classic game of brick! 

### Author
fieash




## Leaky Pin

### Details

I wonder if there's something special in the secret pin....

Stop the backend and run this in the Thonny REPL to start the challenge.

```python
from leaky_gpio25 import *
```

### Author

itsme-zeix


## Shooting Flags

### Details

We have some Secure Armed Forces (SAF) on our badge. They are well trained to follow instructions and patterns.

```verilog
module shooting_flags #(
    parameter CLK_FREQ = 48_000_000 // not the actual clock frequency
) (
    input clk, input got_commanding_officer, output [7:0] cats
);
    //// Shooting Rate ////////////////////////////////////////////////////
    // Create a new clock
    reg [31:0] counter_shooting = 0;
    reg clk_shooting = 0;
    always @ (posedge clk) begin
        counter_shooting <= counter_shooting + 1;
        if (counter_shooting == CLK_FREQ/30) begin
            clk_shooting <= ~clk_shooting;
            counter_shooting <= 0;
        end
    end
    
    reg [31:0] counter_wayang = 0;
    reg clk_wayang = 0;
    always @ (posedge clk) begin
        counter_wayang <= counter_wayang + 1;
        if (counter_wayang == CLK_FREQ/4) begin
            clk_wayang <= ~clk_wayang;
            counter_wayang <= 0;
        end
    end
    //// Shooting /////////////////////////////////////////////////////////
    localparam FLAG_LEN = 25;
    reg [7:0] flag[FLAG_LEN];
    always @ (*) begin
        // lmao no flag
    end

    reg [7:0] shooting = 8'b101;
    reg [7:0] shooting_flag = 8'b0;
    reg [$clog2(FLAG_LEN)-1:0] counter_display = 0;
    always @ (posedge clk_shooting) begin
        shooting <= shooting << 1 | shooting[7];
    end
    always @ (posedge clk_wayang) begin
        shooting_flag <= (
            flag[counter_display] << counter_display % 8 | 
            flag[counter_display] >> (8-counter_display%8)
        );
        counter_display <= (counter_display + 1) % FLAG_LEN;
    end
    /// LED output //////////////////////////////////////////////////////
    assign cats = (got_commanding_officer ? shooting_flag : shooting);

endmodule

/* in the top module it is used as such

wire [7:0] chall_shootingflags_leds;
shooting_flags #(.CLK_FREQ(CLK_FREQ)) chall_shootingflags (
    .clk(clk), 
    .got_commanding_officer(~btn[2]),
    .cats(chall_shootingflags_leds)
);

*/
```

### Author

Hackin7


## Secure Memory

### Details

It's security at the hardware level so it must be secure right?

Clock Frequency - 15Hz

Verilog Reference

```verilog
// Code your design here
module regular_synchronous_memory(input clk, input [4:0] address, output reg [7:0] value);
	// memory retrieval
	always @ (posedge clk) begin // 10Hz
		value <= (
            // lmao you think i'll just give you the flag here? go extract it from your catcore.
			0
		);
	end
endmodule

module secure_memory(input clk, input [4:0] address, output [7:0] value);
	wire [4:0] mem_address;
	wire [7:0] mem_value;
	regular_synchronous_memory mem (clk, mem_address, mem_value);
	assign mem_address = address;
    assign value = ( mem_address == 5'd31 ? mem_value : "?" );
endmodule

/* 
At the top module
----------------------
assign chall_secmem_address = interconnect[4:0];
assign pmod_j2 = (
    mode == MODE_CHALL_SECURE_MEM ? chall_secmem_value : 
    8'bzzzzzzzz
);

Pinouts
-----------------------
LOCATE COMP "pmod_j2[0]" SITE "A14";
IOBUF PORT  "pmod_j2[0]" IO_TYPE=LVCMOS25;
LOCATE COMP "pmod_j2[1]" SITE "A13";
IOBUF PORT  "pmod_j2[1]" IO_TYPE=LVCMOS25;
LOCATE COMP "pmod_j2[2]" SITE "A12";
IOBUF PORT  "pmod_j2[2]" IO_TYPE=LVCMOS25;
LOCATE COMP "pmod_j2[3]" SITE "A11";
IOBUF PORT  "pmod_j2[3]" IO_TYPE=LVCMOS25;
LOCATE COMP "pmod_j2[4]" SITE "B14";
IOBUF PORT  "pmod_j2[4]" IO_TYPE=LVCMOS25;
LOCATE COMP "pmod_j2[5]" SITE "B13";
IOBUF PORT  "pmod_j2[5]" IO_TYPE=LVCMOS25;
LOCATE COMP "pmod_j2[6]" SITE "B12";
IOBUF PORT  "pmod_j2[6]" IO_TYPE=LVCMOS25;
LOCATE COMP "pmod_j2[7]" SITE "B11";
IOBUF PORT  "pmod_j2[7]" IO_TYPE=LVCMOS25;
*/
```


Solution Template

```python
import board
import digitalio
import time
import hardware.fpga

hardware.hw_state["fpga_overlay"].deinit()
if input("type something to update fpga: ") != "":
    h = hardware.fpga.upload_bitstream("/hardware/bitstreams/main.bit")
    h.deinit()

fpga_interconnect_pins = [board.GP8, board.GP9, board.GP10, board.GP11,	board.GP12, board.GP13, board.GP14, board.GP15]
rp2350_pmod_pins = [board.GP27, board.GP16, board.GP23, board.GP25, board.GP26, board.GP28, board.GP22, board.GP24]

### FPGA Interconnect
def overlay_interconnect_pins():
    dio = []
    for p in fpga_interconnect_pins:
        d = digitalio.DigitalInOut(p)
        d.direction = digitalio.Direction.OUTPUT
        dio.append(d)
    return dio

def pmod_pins():
    dio = []
    for p in rp2350_pmod_pins:
        if p == None: pass
        d = digitalio.DigitalInOut(p)
        d.direction = digitalio.Direction.INPUT
        dio.append(d)
    return dio


interconnect = overlay_interconnect_pins()
pmod = pmod_pins()

fpga_mode = [0, 1, 0]
interconnect[7].value = 0
interconnect[6].value = 1
interconnect[5].value = 0

def read_char():
    value = 0
    for p in range(len(pmod)):
        if pmod[p] == None: pass
        value |= pmod[p].value << p;
    return chr(value)

def set_address(addr):
    addr_bits = [0, 0, 0, 0, 0]
    addr_val = addr
    for i in range(len(addr_bits)):
        addr_bits[i] = addr_val % 2
        addr_val = addr_val // 2
    print("Address:",addr, addr_bits)
    for v in range(len(addr_bits)):
        interconnect[v].value = addr_bits[v]


### Insert Solution Code Below
```


### Author

Hackin7

## CatCore

### Details

Here at GreyCatTheFlag we have experience managing cats of different types. We have elmocat, we have jrocat, we have GPMGcat, and much more. 
You can now leverage our year of experience with CatCore Hyper, the latest version of our Hardware Coprocessor, specifically designed for managing cats.

Worried about security? No worries, being cat experts we have made sure that no one can anyhow mobilise your cats or show the white flag.
Only we can do it lmao.


### Relevant Files

Read the CatCore Hyper Datasheet in `/hardware`

### Author

Hackin7
