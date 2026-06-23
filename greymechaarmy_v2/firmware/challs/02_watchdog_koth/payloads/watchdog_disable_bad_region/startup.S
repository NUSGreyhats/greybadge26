.section .text.start
.global _start
_start:
    call main
1:
    j 1b
