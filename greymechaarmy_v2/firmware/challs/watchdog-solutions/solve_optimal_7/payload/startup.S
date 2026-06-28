.section .text.start
.global _start
_start:
    # === Disable MMIO ===============================
    lui	a5,0x10000 # 19e - 1a2 =>  3 cycles
    # === Print UART =================================
    addi a4, zero, 0x67
    sb  a4,0(a5) 
    addi a4, zero, 0x72
    sb  a4,0(a5) 
    addi a4, zero, 0x65
    sb  a4,0(a5) 
    addi a4, zero, 0x79
    sb  a4,0(a5) 
    addi a4, zero, 0x7b
    sb  a4,0(a5) 
    addi a4, zero, 0x6d
    sb  a4,0(a5) 
    addi a4, zero, 0x6d
    sb  a4,0(a5) 
    addi a4, zero, 0x69
    sb  a4,0(a5) 
    addi a4, zero, 0x6f
    sb  a4,0(a5) 
    addi a4, zero, 0x5f
    sb  a4,0(a5) 
    addi a4, zero, 0x66
    sb  a4,0(a5) 
    addi a4, zero, 0x75
    sb  a4,0(a5) 
    addi a4, zero, 0x7a
    sb  a4,0(a5) 
    sb  a4,0(a5) 
    sb  a4,0(a5) 
    addi a4, zero, 0x7D
    sb  a4,0(a5) 
    addi a4, zero, 0x0a
    sw	 a4,0(a5)
    ret

