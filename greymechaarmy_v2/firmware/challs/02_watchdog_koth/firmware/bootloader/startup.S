.section .text.start
.global _start
_start:
    la sp, _stack_top
    call main
1:
    j 1b

.global jump_to_payload_asm
jump_to_payload_asm:
    la t0, boot_return_sp
    sw sp, 0(t0)
    la t0, boot_return_ra
    sw ra, 0(t0)
    mv sp, a1
    la ra, 1f
    jr a0
1:
    la t0, boot_return_sp
    lw sp, 0(t0)
    la t0, boot_return_ra
    lw ra, 0(t0)
    ret

.section .bss
.align 2
boot_return_sp:
    .word 0
boot_return_ra:
    .word 0
