import os,struct,gc
import board,rp2pio,adafruit_pioasm
import hardware.default_overlay,hardware.fpga

M=(0,1,0)
N=300
P0="""
.program p
set pins, {addr}
nop [3]
set pins, 31
in pins, 7
push block
"""

def ov():
    o=hardware.default_overlay.Overlay()
    hardware.hw_state={"fpga_overlay":o}
    return o

def setup():
    o=ov()
    print("UPLOAD")
    r=hardware.fpga.upload_bitstream("/hardware/bitstreams/main.bit")
    try:r.deinit()
    except Exception:pass
    o.set_mode(M)

def sm(a):
    return rp2pio.StateMachine(adafruit_pioasm.assemble(P0.format(addr=a)),frequency=125000000,
        first_set_pin=board.GP8,set_pin_count=5,
        first_in_pin=board.GP22,in_pin_count=7,out_shift_right=True,in_shift_right=True,
        auto_push=False,auto_pull=False,initial_set_pin_state=31,initial_set_pin_direction=31)

def samp(s,n):
    rx=bytearray(n*4)
    s.readinto(rx)
    return [(struct.unpack_from("<I",rx,i*4)[0]>>25)&127 for i in range(n)]

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

def best(h):
    if not h:return "?"
    k=max(h,key=h.get)
    a,b=cands(k)
    for x in (b,a):
        if chr(x) in "fun{}_abcdefghijklmnopqrstuvwxyz0123456789": return chr(x)
    return ch(b)

gc.collect()
setup()
out=[]
for a in range(31):
    s=sm(a)
    try:
        h={}
        for x in samp(s,N):
            v=dec(x)
            if v: h[v]=h.get(v,0)+1
        row=sorted(h.items(),key=lambda z:z[1],reverse=True)[:4]
        print("%02d"%a," ".join("%s/%s:%d"%(ch(cands(k)[0]),ch(cands(k)[1]),n) for k,n in row))
        out.append(best(h))
    finally:
        s.deinit()
print("BEST:","".join(out))
print("FAST_"+"SECMEM_DONE")
