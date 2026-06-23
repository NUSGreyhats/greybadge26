# Watchdog KOTH CTF Challenge

Main idea - participants can upload code to extract the flag from a memory region before the 

C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge26
C:\Users\zunmun\Documents\Stuff\Github\PERSONAL PROJECTS\GreyMechaArmy_Tests\softcores\picorv32\custom_fpga_spi

## Rough Plan

Rough plan on CTF Challenge
1. whack a watchdog that resets the softcore whenever it falls out of the mem region
2. Profile the branch predictor and other peripherals for number of clock cycles taken
3. Find the C code solution & optimise the assembly behind it
    - loop unroll
    - register reuse
4. modify the watch dog cycle ticks to fit only the optimised solution

then intended solve would be to simulate the softcore and manually count clock cycles/ simulate memory
And then run it on a board onsite


## Editing the PicoRV32 Softcore

Softcore should already have
1. access to LEDs
2. access to GC9A01 OLED

Softcore should also have
1. R/W access to UART
2. Watchdog region with proper tests

## Software on the Softcore

This should allow the user to upload custom code through uart and then run it in C
else the software can mainly either blink the LEDs, or just display a simple screen on the OLED
1. the display can be like: no flag for you

## Optimising of the C Code

The watchdog should have its number of cycles configurable
afterwards, a simple C code solution can be coded and compiled (without optimisations)
we can then profile the clock cycle taken in simulation
afterwards, the user will manually 
1. code in assembly to find the most optimal solution
2. tweak the cycles the watchdog
