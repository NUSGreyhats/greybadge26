.section .text.start
.global _start
_start:
    # === Disable MMIO ===============================
    lui	a5,0x10000 # 19e - 1a2 =>  3 cycles
    sw	zero,512(a5) # 10000200 <main+0xfff81fc> 
    # === Configure address ==========================
    lui	a1,0x20000

    # === Print UART =================================
    lb	a4,0(a1) # Read 1st character
    sb  a4,0(a5) # Write character
    lb	a4,1(a1) 
    sb  a4,0(a5) 
    lb	a4,2(a1) 
    sb  a4,0(a5) 
    lb	a4,3(a1) 
    sb  a4,0(a5) 
    lb	a4,4(a1) 
    sb  a4,0(a5) 
    lb	a4,5(a1) 
    sb  a4,0(a5) 
    lb	a4,6(a1) 
    sb  a4,0(a5) 
    lb	a4,7(a1) 
    sb  a4,0(a5) 
    lb	a4,8(a1) 
    sb  a4,0(a5) 
    lb	a4,9(a1) 
    sb  a4,0(a5) 
    lb	a4,10(a1) 
    sb  a4,0(a5) 
    lb	a4,11(a1) 
    sb  a4,0(a5) 
    lb	a4,12(a1) 
    sb  a4,0(a5) 
    lb	a4,13(a1) 
    sb  a4,0(a5) 
    lb	a4,14(a1) 
    sb  a4,0(a5) 
    lb	a4,15(a1) 
    sb  a4,0(a5) 
    lb	a4,16(a1) 
    sb  a4,0(a5) 
    addi a4, zero, 0x0a
    sw	 a4,0(a5)

