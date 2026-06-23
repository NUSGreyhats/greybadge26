#ifndef WATCHDOG_KOTH_MMIO_H
#define WATCHDOG_KOTH_MMIO_H

typedef unsigned char u8;
typedef unsigned int u32;
typedef unsigned long long u64;

static inline void mmio_write32(u32 addr, u32 value)
{
    *(volatile u32 *)addr = value;
}

static inline u32 mmio_read32(u32 addr)
{
    return *(volatile u32 *)addr;
}

#endif
