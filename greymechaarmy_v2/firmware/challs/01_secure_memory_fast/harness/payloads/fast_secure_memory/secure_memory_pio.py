import gc,struct
import board,rp2pio,adafruit_pioasm
import hardware.default_overlay,hardware.fpga

M=(0,1,0)
P="""
.program p
set pindirs 31
set pins {addr}
set y, 2
outer:
set x, 31
loop:
nop [31]
jmp x-- loop
jmp y-- outer
set pins 31
in pins, 7
push block
"""

def setup():
    if hasattr(hardware,"hw_state") and "fpga_overlay" in hardware.hw_state:
        o=hardware.hw_state["fpga_overlay"]
    else:
        o=hardware.default_overlay.Overlay()
        hardware.hw_state={"fpga_overlay":o}
    try:o.deinit_mode_buttons()
    except Exception:pass
    try:o.deinit_mode_uart()
    except Exception:pass
    print("UPLOAD")
    r=hardware.fpga.upload_bitstream("/hardware/bitstreams/main.bit")
    try:r.deinit()
    except Exception:pass
    o.set_mode(M)

def sm(a):
    return rp2pio.StateMachine(adafruit_pioasm.assemble(P.format(addr=a)),frequency=10000,
        first_set_pin=board.GP8,set_pin_count=5,
        first_in_pin=board.GP22,in_pin_count=7,out_shift_right=True,in_shift_right=True,
        auto_push=False,auto_pull=False,initial_set_pin_state=31,initial_set_pin_direction=31)

def sample(a):
    s=sm(a)
    try:
        s.run()
        rx=bytearray(4)
        s.readinto(rx)
        return (struct.unpack_from("<I",rx,0)[0]>>25)&127
    finally:
        s.deinit()

def dec(x):
    v=0
    v|=((x>>5)&1)<<0
    v|=((x>>1)&1)<<2
    v|=((x>>3)&1)<<3
    v|=((x>>4)&1)<<4
    v|=((x>>0)&1)<<5
    v|=((x>>6)&1)<<6
    v|=((x>>2)&1)<<7
    return v

def cands(v):
    return (v&~2,(v&~2)|2)

def ch(v):
    return chr(v) if 32<=v<=126 else "\\x%02x"%v

def choose(v):
    a,b=cands(v)
    for x in (b,a):
        if chr(x) in "grey{race_flag}_abcdefghijklmnopqrstuvwxyz0123456789}":
            return chr(x)
    return ch(a)+"/"+ch(b)

gc.collect()
setup()
out=[]
for a in range(31):
    h={}
    for _ in range(3):
        v=dec(sample(a))
        h[v]=h.get(v,0)+1
    k=max(h,key=h.get)
    c0,c1=cands(k)
    print("%02d"%a,ch(c0)+"/"+ch(c1),h)
    out.append(choose(k))
print("BEST:","".join(out))
print("PIO_"+"SECMEM_DONE")
