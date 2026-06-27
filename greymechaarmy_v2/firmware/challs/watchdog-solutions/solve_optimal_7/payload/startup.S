.section .text.start
.global _start
_start:
        lui  a5, 0x10000

    addi a4, zero, 0x67   # g
    sb   a4, 0(a5)
    addi a4, a4, 11       # r
    sb   a4, 0(a5)
    addi a4, a4, -13      # e
    sb   a4, 0(a5)
    addi a4, a4, 20       # y
    sb   a4, 0(a5)
    addi a4, a4, 2        # {
    sb   a4, 0(a5)
    addi a4, a4, -14      # m
    sb   a4, 0(a5)
    sb   a4, 0(a5)        # m again
    addi a4, a4, -4       # i
    sb   a4, 0(a5)
    addi a4, a4, 6        # o
    sb   a4, 0(a5)
    addi a4, a4, -16      # _
    sb   a4, 0(a5)
    addi a4, a4, 7        # f
    sb   a4, 0(a5)
    addi a4, a4, 15       # u
    sb   a4, 0(a5)
    addi a4, a4, 5        # z
    sb   a4, 0(a5)
    sb   a4, 0(a5)        # z
    sb   a4, 0(a5)        # z
    addi a4, a4, 3        # }
    sb   a4, 0(a5)
    addi a4, a4, -115     # \n
    sb   a4, 0(a5)
    ret

