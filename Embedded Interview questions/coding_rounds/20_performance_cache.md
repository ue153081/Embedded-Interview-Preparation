# Performance & Cache Coding

**IDs:** C276–C285 (10 questions)  
**Focus:** SoA, false sharing, branchless, fast copy, hot/cold split.

[← Back to category index](./README.md)

---

### C276 — AoS to SoA transform

**Interview prompt:**  
Convert array-of-structs samples to struct-of-arrays for processing speed.

**Implement:**
```c
typedef struct { int16_t x,y,z; } sample_t;
void aos_to_soa(const sample_t *in, size_t n, int16_t *x, int16_t *y, int16_t *z);
```

**Constraints / expectations:**
- Correctness
- Discuss cache why

**Follow-ups:**
- In-place?
- SIMD

---

### C277 — Prefetch-friendly loop

**Interview prompt:**  
Process a large buffer in a cache-friendly way; optional __builtin_prefetch.

**Implement:**
```c
uint32_t checksum(const uint8_t *b, size_t n);
```

**Constraints / expectations:**
- Sequential access
- Explain prefetch placement

**Follow-ups:**
- Blocking for L1
- Prefetch distance

---

### C278 — False sharing fix

**Interview prompt:**  
Two cores increment counters that falsely share a cache line; fix with padding/alignas.

**Implement:**
```c
struct Counters { atomic_uint a; atomic_uint b; }; /* buggy layout */
struct CountersFixed { /* padded */ };
```

**Constraints / expectations:**
- alignas(64) or pad
- Show before/after

**Follow-ups:**
- How to measure
- Destructive interference

---

### C279 — Branchless clamp

**Interview prompt:**  
Implement clamp/min/max branchlessly (or discuss when compiler does it).

**Implement:**
```c
int clamp(int x, int lo, int hi);
```

**Constraints / expectations:**
- Correct for all ints careful with overflow
- Document approach

**Follow-ups:**
- Conditional move
- SIMD select

---

### C280 — Word-wise checksum

**Interview prompt:**  
Checksum using 32-bit loads with byte tail handling.

**Implement:**
```c
uint32_t sum32(const uint8_t *b, size_t n);
```

**Constraints / expectations:**
- Alignment handling
- Endian defined

**Follow-ups:**
- Unaligned BE CPU
- IP checksum

---

### C281 — Alignment-aware copy

**Interview prompt:**  
Copy memory faster when both pointers aligned; fallback byte copy.

**Implement:**
```c
void *fast_memcpy(void *dst, const void *src, size_t n);
```

**Constraints / expectations:**
- Correct for all alignments
- Optional NEON mention

**Follow-ups:**
- memmove overlap
- Benchmark

---

### C282 — Hot/cold structure split

**Interview prompt:**  
Refactor a driver struct so rarely used fields don't pollute hot cache lines.

**Implement:**
```c
struct drv_hot { /* ... */ };
struct drv_cold { /* ... */ };
struct drv { struct drv_hot hot; struct drv_cold *cold; };
```

**Constraints / expectations:**
- Justify split
- Allocation strategy

**Follow-ups:**
- Profile-guided
- False sharing again

---

### C283 — Reduce copies in TX path

**Interview prompt:**  
Redesign API so TX can take ownership of a buffer instead of copying into driver.

**Implement:**
```c
/* old: write(const uint8_t*, n) copies */
/* new: write_buf(owned_buf_t*) zero-copy */
```

**Constraints / expectations:**
- Ownership clear
- Fallback copy API

**Follow-ups:**
- Lifetime scatterlist
- Lifetime lifetime

---

### C284 — Bit-reverse LUT vs compute

**Interview prompt:**  
Implement bit reverse with compute and LUT; discuss space/time.

**Implement:**
```c
uint8_t rev_compute(uint8_t x);
uint8_t rev_lut(uint8_t x);
```

**Constraints / expectations:**
- 256-byte table
- When LUT wins

**Follow-ups:**
- Generate LUT at compile time
- Cache pressure

---

### C285 — Ring indices cache-line placement

**Interview prompt:**  
Place producer/consumer indices on separate cache lines in shared ring.

**Implement:**
```c
struct spsc_shared { /* alignas pads */ };
```

**Constraints / expectations:**
- Explain false sharing
- Works with atomics

**Follow-ups:**
- Linux kernel ring examples
- Performance test

---


---

[← Back to category index](./README.md)
