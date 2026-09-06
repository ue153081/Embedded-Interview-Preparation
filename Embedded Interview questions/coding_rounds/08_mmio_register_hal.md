# MMIO & Register HAL

**IDs:** C121–C135 (15 questions)  
**Focus:** reg read/write/RMW, poll timeout, shadows, fake MMIO, field macros.

[← Back to category index](./README.md)

---

### C121 — MMIO read/write

**Interview prompt:**  
Implement 32-bit MMIO accessors using volatile.

**Implement:**
```c
uint32_t reg_read32(volatile uint32_t *addr);
void reg_write32(volatile uint32_t *addr, uint32_t val);
```

**Constraints / expectations:**
- volatile correct
- Explain why pointers are volatile

**Follow-ups:**
- 8/16-bit accessors
- Memory barriers for posting

---

### C122 — Register RMW helper

**Interview prompt:**  
Implement read-modify-write with mask.

**Implement:**
```c
void reg_rmw32(volatile uint32_t *addr, uint32_t mask, uint32_t value);
```

**Constraints / expectations:**
- Only modify masked bits
- Document concurrency needs

**Follow-ups:**
- Atomic RMW if ISR shares
- Write-only regs

---

### C123 — Bit set/clear/toggle helpers

**Interview prompt:**  
Convenience wrappers around RMW.

**Implement:**
```c
void reg_set_bits(volatile uint32_t *a, uint32_t bits);
void reg_clr_bits(volatile uint32_t *a, uint32_t bits);
void reg_toggle_bits(volatile uint32_t *a, uint32_t bits);
```

**Constraints / expectations:**
- Correctness
- No accidental wider clears

**Follow-ups:**
- HW toggle registers that aren't RMW

---

### C124 — wait_for_bit with timeout

**Interview prompt:**  
Poll until a status bit becomes set/cleared or timeout.

**Implement:**
```c
int wait_for_bit(volatile uint32_t *addr, uint32_t mask, int set, uint32_t timeout_us);
```

**Constraints / expectations:**
- Use provided delay/timebase
- Return timeout error

**Follow-ups:**
- Busy wait vs sleep
- WFE/WFI

---

### C125 — Poll with deadline API

**Interview prompt:**  
Same as wait_for_bit but using absolute deadline ticks to avoid drift.

**Implement:**
```c
int wait_until(volatile uint32_t *addr, uint32_t mask, int set, uint32_t deadline_ticks);
```

**Constraints / expectations:**
- Wrap-safe time compare
- No extra drift

**Follow-ups:**
- Backoff delay
- Instrumentation

---

### C126 — Register map + static assert offsets

**Interview prompt:**  
Define a peripheral register map struct and assert offsets match the datasheet numbers given in the prompt.

**Implement:**
```c
struct uart_regs { uint32_t dr; uint32_t rsr; uint32_t reserved0[4]; uint32_t fr; /* ... */ };
/* static asserts */
```

**Constraints / expectations:**
- Match fictional datasheet offsets you state
- volatile uint32_t fields

**Follow-ups:**
- Reserved holes
- Array of instances

---

### C127 — Write posting barrier

**Interview prompt:**  
After writing a control register, ensure it is visible to device before continuing (readback barrier helper).

**Implement:**
```c
void reg_write32_posted(volatile uint32_t *addr, uint32_t val);
void mmio_barrier_after_write(volatile uint32_t *dummy_status);
```

**Constraints / expectations:**
- Explain posted writes
- Use readback pattern

**Follow-ups:**
- DMA coherency vs MMIO posting
- DMB on ARM

---

### C128 — Shadow registers for write-only HW

**Interview prompt:**  
Keep software shadows for write-only registers so you can RMW fields.

**Implement:**
```c
typedef struct { volatile uint32_t *hw; uint32_t shadow; } wo_reg_t;
void wo_set_bits(wo_reg_t *r, uint32_t bits);
void wo_clr_bits(wo_reg_t *r, uint32_t bits);
```

**Constraints / expectations:**
- Shadow and HW stay in sync
- Init shadow

**Follow-ups:**
- HW can change under you?
- Multi-thread shadows

---

### C129 — Fake MMIO for host tests

**Interview prompt:**  
Create a fake register block so driver logic can be unit-tested on host.

**Implement:**
```c
typedef struct { uint32_t storage[64]; } fake_mmio_t;
uint32_t fake_read32(fake_mmio_t *f, size_t off);
void fake_write32(fake_mmio_t *f, size_t off, uint32_t v);
```

**Constraints / expectations:**
- Hook side effects optional (e.g., writing CMD sets STATUS)
- Pointer map API like real driver

**Follow-ups:**
- How far to simulate HW
- CI usage

---

### C130 — Atomic RMW shared with ISR

**Interview prompt:**  
Thread and ISR both modify the same control register; make it safe.

**Implement:**
```c
void thread_enable_rx(void);
void isr_clear_error(void);
```

**Constraints / expectations:**
- Critical section or atomic HW bit set regs
- No lost bits

**Follow-ups:**
- HW bit-band / set-clear regs
- Compare-and-swap MMIO?

---

### C131 — Multi-register update sequence

**Interview prompt:**  
Some devices require writing REG_A then REG_B within constraints, or holding a latch. Implement a safe update function.

**Implement:**
```c
int device_set_config(uint32_t cfg_hi, uint32_t cfg_lo);
```

**Constraints / expectations:**
- Document required order
- Timeout if HW rejects

**Follow-ups:**
- Partial failure recovery
- IRQs during sequence

---

### C132 — Endian MMIO helpers

**Interview prompt:**  
Peripheral is big-endian; CPU is little-endian. Implement accessors that swap as needed.

**Implement:**
```c
uint32_t be_reg_read32(volatile uint32_t *addr);
void be_reg_write32(volatile uint32_t *addr, uint32_t cpu_val);
```

**Constraints / expectations:**
- Clear CPU vs wire endian
- Use byteswap

**Follow-ups:**
- 16-bit buses
- When HW does swapping

---

### C133 — FIELD_GET / FIELD_PREP macros

**Interview prompt:**  
Implement Linux-style field get/prep macros for a mask.

**Implement:**
```c
#define FIELD_GET(mask, reg) ...
#define FIELD_PREP(mask, val) ...
uint32_t encode_speed(uint32_t speed_code);
uint32_t decode_speed(uint32_t reg);
```

**Constraints / expectations:**
- mask contiguous bits
- No undefined shifts

**Follow-ups:**
- GENMASK combo
- Compile-time checks

---

### C134 — Soft reset with timeout

**Interview prompt:**  
Write a soft-reset sequence: set reset bit, wait for ack/clear, timeout and return error.

**Implement:**
```c
int device_soft_reset(uint32_t timeout_ms);
```

**Constraints / expectations:**
- Don't spin forever
- Leave device in known state on failure if possible

**Follow-ups:**
- Reset from ISR?
- Recovery retries

---

### C135 — Register dump logger

**Interview prompt:**  
Dump a range of registers into a caller buffer as text or binary words for debug.

**Implement:**
```c
size_t reg_dump(volatile uint32_t *base, size_t count, char *out, size_t out_cap);
```

**Constraints / expectations:**
- Bounded output
- Readable format

**Follow-ups:**
- debugfs analogy
- Sensitive registers redaction

---


---

[← Back to category index](./README.md)
