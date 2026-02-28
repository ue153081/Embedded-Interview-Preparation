# Topic 2 — Bit Manipulation Interview Solutions (Q019-Q034)

## Q019: Reverse bits in 32-bit integer
### 1. Problem Statement
Reverse bit order of a 32-bit unsigned value.
### 2. Assumptions
- Unsigned arithmetic.
### 3. Full C Code
```c
#include <stdint.h>

uint32_t reverse_bits32(uint32_t x) {
    x = ((x >> 1) & 0x55555555u) | ((x & 0x55555555u) << 1);
    x = ((x >> 2) & 0x33333333u) | ((x & 0x33333333u) << 2);
    x = ((x >> 4) & 0x0F0F0F0Fu) | ((x & 0x0F0F0F0Fu) << 4);
    x = ((x >> 8) & 0x00FF00FFu) | ((x & 0x00FF00FFu) << 8);
    return (x >> 16) | (x << 16);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. LUT-based alternative?
2. Constant-time requirement implications?

## Q020: Reverse bits in 64-bit integer
### 1. Problem Statement
Reverse all bits in 64-bit value.
### 2. Assumptions
- 64-bit platform types available.
### 3. Full C Code
```c
uint64_t reverse_bits64(uint64_t x) {
    x = ((x >> 1) & 0x5555555555555555ULL) | ((x & 0x5555555555555555ULL) << 1);
    x = ((x >> 2) & 0x3333333333333333ULL) | ((x & 0x3333333333333333ULL) << 2);
    x = ((x >> 4) & 0x0F0F0F0F0F0F0F0FULL) | ((x & 0x0F0F0F0F0F0F0F0FULL) << 4);
    x = ((x >> 8) & 0x00FF00FF00FF00FFULL) | ((x & 0x00FF00FF00FF00FFULL) << 8);
    x = ((x >> 16) & 0x0000FFFF0000FFFFULL) | ((x & 0x0000FFFF0000FFFFULL) << 16);
    return (x >> 32) | (x << 32);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Builtin intrinsics portability?
2. Endianness relation?

## Q021: Count set bits (Brian Kernighan)
### 1. Problem Statement
Return number of set bits.
### 2. Assumptions
- Unsigned integer input.
### 3. Full C Code
```c
int popcount_kernighan(uint32_t x) {
    int count = 0;
    while (x) {
        x &= (x - 1u);
        count++;
    }
    return count;
}
```
### 4. Complexity
- O(k), k = set bits
### 5. Interview Follow-ups
1. Compare with LUT.
2. Worst-case timing predictability?

## Q022: Count set bits (lookup-table method)
### 1. Problem Statement
Fast predictable popcount via 8-bit table.
### 2. Assumptions
- Small static table allowed.
### 3. Full C Code
```c
static uint8_t pc8[256];

void popcount_table_init(void) {
    pc8[0] = 0;
    for (int i = 1; i < 256; i++) {
        pc8[i] = (uint8_t)((i & 1) + pc8[i >> 1]);
    }
}

int popcount_lut32(uint32_t x) {
    return pc8[x & 0xFFu] +
           pc8[(x >> 8) & 0xFFu] +
           pc8[(x >> 16) & 0xFFu] +
           pc8[(x >> 24) & 0xFFu];
}
```
### 4. Complexity
- O(1) for fixed width
### 5. Interview Follow-ups
1. Memory-speed tradeoff?
2. Thread-safe one-time init?

## Q023: Detect power of 2
### 1. Problem Statement
Return true if x is exact power-of-two.
### 2. Assumptions
- x is unsigned.
### 3. Full C Code
```c
int is_power_of_two(uint32_t x) {
    return (x != 0u) && ((x & (x - 1u)) == 0u);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Why x=0 excluded?
2. Next power-of-two relation?

## Q024: Compute next power of 2
### 1. Problem Statement
Round up to next power-of-two.
### 2. Assumptions
- Overflow handling defined by caller.
### 3. Full C Code
```c
uint32_t next_power_of_two(uint32_t x) {
    if (x == 0u) {
        return 1u;
    }
    x--;
    x |= x >> 1;
    x |= x >> 2;
    x |= x >> 4;
    x |= x >> 8;
    x |= x >> 16;
    return x + 1u;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Overflow case for large x?
2. Use in ring buffer sizing?

## Q025: Parity bit calculation
### 1. Problem Statement
Compute odd parity (1 if odd set-bit count).
### 2. Assumptions
- 32-bit input.
### 3. Full C Code
```c
int parity_odd32(uint32_t x) {
    x ^= x >> 16;
    x ^= x >> 8;
    x ^= x >> 4;
    x &= 0xFu;
    return (0x6996u >> x) & 1u;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Even parity conversion?
2. UART parity usage?

## Q026: Swap odd/even bits
### 1. Problem Statement
Swap each odd bit with adjacent even bit.
### 2. Assumptions
- 32-bit unsigned value.
### 3. Full C Code
```c
uint32_t swap_odd_even_bits(uint32_t x) {
    return ((x & 0xAAAAAAAAu) >> 1) | ((x & 0x55555555u) << 1);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Generalize to n-bit groups?
2. Signed shift pitfalls?

## Q027: Bitfield packing for sensor frame
### 1. Problem Statement
Pack three fields into one 32-bit word.
### 2. Assumptions
- Inputs prevalidated.
### 3. Full C Code
```c
uint32_t pack_sensor_fields(uint8_t type, uint8_t flags, uint16_t value) {
    return ((uint32_t)type << 24) |
           ((uint32_t)flags << 16) |
           (uint32_t)value;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Validation strategy for overflowed fields?
2. Protocol versioning concerns?

## Q028: Bitfield unpacking and range validation
### 1. Problem Statement
Extract fields and validate ranges.
### 2. Assumptions
- Packed format fixed.
### 3. Full C Code
```c
int unpack_sensor_fields(uint32_t w, uint8_t *type, uint8_t *flags, uint16_t *value) {
    if (!type || !flags || !value) {
        return -1;
    }

    *type = (uint8_t)((w >> 24) & 0xFFu);
    *flags = (uint8_t)((w >> 16) & 0xFFu);
    *value = (uint16_t)(w & 0xFFFFu);

    if (*type > 31u) {
        return -2;
    }
    return 0;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Signed sub-fields handling?
2. Endian conversion boundary?

## Q029: Missing number using XOR
### 1. Problem Statement
Array has values `[0..n]` missing one value.
### 2. Assumptions
- Exactly one missing.
### 3. Full C Code
```c
int missing_number_xor(const int *a, int n) {
    int x = 0;
    for (int i = 0; i <= n; i++) {
        x ^= i;
    }
    for (int i = 0; i < n; i++) {
        x ^= a[i];
    }
    return x;
}
```
### 4. Complexity
- O(n), O(1) extra
### 5. Interview Follow-ups
1. Input corruption behavior?
2. Sum formula overflow issue?

## Q030: Single non-duplicate using XOR
### 1. Problem Statement
All numbers appear twice except one.
### 2. Assumptions
- Exactly one unique element.
### 3. Full C Code
```c
int single_non_duplicate_xor(const int *a, int n) {
    int x = 0;
    for (int i = 0; i < n; i++) {
        x ^= a[i];
    }
    return x;
}
```
### 4. Complexity
- O(n), O(1)
### 5. Interview Follow-ups
1. If elements appear thrice?
2. Streaming version?

## Q031: CRC-8 implementation
### 1. Problem Statement
Compute CRC-8 for byte stream.
### 2. Assumptions
- Polynomial: 0x07.
### 3. Full C Code
```c
uint8_t crc8_compute(const uint8_t *data, size_t len) {
    uint8_t crc = 0x00u;

    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++) {
            if (crc & 0x80u) {
                crc = (uint8_t)((crc << 1) ^ 0x07u);
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}
```
### 4. Complexity
- O(8n)
### 5. Interview Follow-ups
1. Table-driven optimization?
2. Reflection/final XOR variants?

## Q032: CRC-16 implementation
### 1. Problem Statement
Compute CRC-16 for packet integrity.
### 2. Assumptions
- Init `0xFFFF`, poly `0xA001`.
### 3. Full C Code
```c
uint16_t crc16_compute(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFFu;

    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++) {
            if (crc & 1u) {
                crc = (uint16_t)((crc >> 1) ^ 0xA001u);
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}
```
### 4. Complexity
- O(8n)
### 5. Interview Follow-ups
1. Common CRC-CCITT difference?
2. Hardware CRC peripheral usage?

## Q033: Fast divide-by-10 without '/'
### 1. Problem Statement
Approximate exact integer division by 10 using multiply+shift.
### 2. Assumptions
- Unsigned 32-bit domain.
### 3. Full C Code
```c
uint32_t div10_u32_fast(uint32_t x) {
    return (uint32_t)(((uint64_t)x * 0xCCCCCCCDULL) >> 35);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Proof of correctness for full range?
2. Signed variant handling?

## Q034: Endianness conversion helpers (16/32/64)
### 1. Problem Statement
Provide byte-swap helpers for protocol and MMIO translation.
### 2. Assumptions
- Portable C implementation.
### 3. Full C Code
```c
uint16_t bswap16_u(uint16_t x) {
    return (uint16_t)((x >> 8) | (x << 8));
}

uint32_t bswap32_u(uint32_t x) {
    return (x >> 24) |
           ((x >> 8) & 0x0000FF00u) |
           ((x << 8) & 0x00FF0000u) |
           (x << 24);
}

uint64_t bswap64_u(uint64_t x) {
    return ((uint64_t)bswap32_u((uint32_t)x) << 32) |
           bswap32_u((uint32_t)(x >> 32));
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. When not to swap?
2. Host-endian abstraction API design?
