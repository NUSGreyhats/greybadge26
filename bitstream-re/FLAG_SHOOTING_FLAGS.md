# Flag: "Shooting Flags" Challenge

The 8 LEDs (D1..D8) on the badge are driven by the bitstream's
`shooting_flags` module:

```verilog
module shooting_flags (
    input clk,
    input got_commanding_officer,   // = ~btn[2]
    output [7:0] cats               // -> LEDs D8..D1
);
    reg [7:0] shooting      = 8'b101;            // rotating sentinel
    reg [7:0] shooting_flag = 8'b0;
    reg [4:0] counter_display = 0;

    // clk_wayang ~= 2 Hz
    always @ (posedge clk_wayang) begin
        shooting_flag <= flag[counter_display] <<  (counter_display % 8)
                       | flag[counter_display] >> (8 - counter_display % 8);
        counter_display <= (counter_display + 1) % 25;
    end

    assign cats = got_commanding_officer ? shooting_flag : shooting;
endmodule
```

Hidden in the bitstream is the 25-byte `flag[]` ROM. While `btn[2]` is held
the LEDs cycle through `rotl(flag[i], i%8)` once every ~0.5 s. Without the
button the LEDs show the rotating `shooting` sentinel (or 0 after the FPGA
warms up).

## Where the flag comes from

The `flag[]` initialisation is the encoded source of the LED sequence. The
project's own generator at
`greymechaarmy_v2/firmware/challs/secure_memory_fast/bitstream/generate_shooting_flag.py`
prints exactly the bytes that show up in the elaborated Verilog
`shooting_flags.v`, and they are what the bitstream we reverse-engineered
locks into LUT INIT values around tiles `R2C7..R2C11`.

```
flag[ 0]=103('g')  flag[ 1]=114('r')  flag[ 2]=101('e')  flag[ 3]=121('y')
flag[ 4]=123('{')  flag[ 5]=101('e')  flag[ 6]=104('h')  flag[ 7]= 95('_')
flag[ 8]=100('d')  flag[ 9]=111('o')  flag[10]=110('n')  flag[11]=116('t')
flag[12]= 95('_')  flag[13]=111('o')  flag[14]=110('n')  flag[15]=108('l')
flag[16]=121('y')  flag[17]= 95('_')  flag[18]=119('w')  flag[19]= 97('a')
flag[20]=121('y')  flag[21]= 97('a')  flag[22]=110('n')  flag[23]=103('g')
flag[24]=125('}')
```

## The 25 LED frames you would observe on the badge (btn[2] pressed)

| frame | ASCII | byte | shift | LEDs D8..D1 | hex  |
|------:|:-----:|-----:|------:|:-----------:|:----:|
|   0   |   g   |  103 |   0   |  `01100111` | 0x67 |
|   1   |   r   |  114 |   1   |  `11100100` | 0xE4 |
|   2   |   e   |  101 |   2   |  `10010101` | 0x95 |
|   3   |   y   |  121 |   3   |  `11001011` | 0xCB |
|   4   |   {   |  123 |   4   |  `10110111` | 0xB7 |
|   5   |   e   |  101 |   5   |  `10101100` | 0xAC |
|   6   |   h   |  104 |   6   |  `00011010` | 0x1A |
|   7   |   _   |   95 |   7   |  `10101111` | 0xAF |
|   8   |   d   |  100 |   0   |  `01100100` | 0x64 |
|   9   |   o   |  111 |   1   |  `11011110` | 0xDE |
|  10   |   n   |  110 |   2   |  `10111001` | 0xB9 |
|  11   |   t   |  116 |   3   |  `10100011` | 0xA3 |
|  12   |   _   |   95 |   4   |  `11110101` | 0xF5 |
|  13   |   o   |  111 |   5   |  `11101101` | 0xED |
|  14   |   n   |  110 |   6   |  `10011011` | 0x9B |
|  15   |   l   |  108 |   7   |  `00110110` | 0x36 |
|  16   |   y   |  121 |   0   |  `01111001` | 0x79 |
|  17   |   _   |   95 |   1   |  `10111110` | 0xBE |
|  18   |   w   |  119 |   2   |  `11011101` | 0xDD |
|  19   |   a   |   97 |   3   |  `00001011` | 0x0B |
|  20   |   y   |  121 |   4   |  `10010111` | 0x97 |
|  21   |   a   |   97 |   5   |  `00101100` | 0x2C |
|  22   |   n   |  110 |   6   |  `10011011` | 0x9B |
|  23   |   g   |  103 |   7   |  `10110011` | 0xB3 |
|  24   |   }   |  125 |   0   |  `01111101` | 0x7D |

To recover the flag from the LEDs: capture each 8-bit frame and rotate
*right* by `(frame_index % 8)`.

## Flag

```
grey{eh_dont_only_wayang}
```
