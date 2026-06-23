ENTRY(_start)

MEMORY
{
  PAYLOAD (rwx) : ORIGIN = 0x00008000, LENGTH = 0x4000
}

SECTIONS
{
  .text : {
    KEEP(*(.text.start))
    *(.text*)
    *(.rodata*)
  } > PAYLOAD

  .data : {
    *(.data*)
  } > PAYLOAD

  .bss : {
    *(.bss*)
    *(COMMON)
  } > PAYLOAD
}
