# Testing, Fakes & Harness

**IDs:** C251–C260 (10 questions)  
**Focus:** Fake clock/UART/MMIO, branch coverage, fault injection, CI main.

[← Back to category index](./README.md)

---

### C251 — Virtual time fake clock

**Interview prompt:**  
Provide a fake clock for unit tests that you can advance manually.

**Implement:**
```c
uint32_t fake_now_ms(void);
void fake_advance_ms(uint32_t dt);
```

**Constraints / expectations:**
- Deterministic
- Used by timers under test

**Follow-ups:**
- Simulating wrap
- Multi-thread tests

---

### C252 — Fake UART byte injector

**Interview prompt:**  
Test a parser by injecting bytes through a fake UART RX API.

**Implement:**
```c
void fake_uart_inject(const uint8_t *b, size_t n);
size_t uart_read(uint8_t *dst, size_t n); /* under test uses fake */
```

**Constraints / expectations:**
- Queue inside fake
- EOF/idle

**Follow-ups:**
- Inject errors
- Baud timing sim skip

---

### C253 — Fake MMIO with side effects

**Interview prompt:**  
Writing to CMD register sets BUSY then DONE in STATUS after advance.

**Implement:**
```c
void fake_write32(...);
void fake_tick(void); /* progress simulated HW */
```

**Constraints / expectations:**
- Enough to test driver wait_for_bit
- Deterministic

**Follow-ups:**
- Interrupt simulation
- DMA simulation

---

### C254 — Ring buffer unit tests

**Interview prompt:**  
Write tests covering empty/full/wrap/partial/overwrite policies.

**Implement:**
```c
void test_ring_wrap(void);
void test_ring_full(void);
/* run_all */
```

**Constraints / expectations:**
- Asserts clear
- No host leak

**Follow-ups:**
- Property tests
- ISR concurrency test

---

### C255 — Branch-complete validator tests (Tesla-style)

**Interview prompt:**  
Function validates pointer and data (>0, not sentinel). Write tests hitting every branch.

**Implement:**
```c
bool validatePointerAndData(int32_t *dataPtr);
bool test_validatePointerAndData(void);
```

**Constraints / expectations:**
- NULL, negative, zero, sentinel, happy
- Return false on first fail in harness OK

**Follow-ups:**
- More sentinels
- Parameterized tests

---

### C256 — Fault injection hooks

**Interview prompt:**  
Inject I2C NACK or DMA error via a test hook to exercise recovery paths.

**Implement:**
```c
void inject_i2c_nack(int enable);
void inject_dma_error(int enable);
```

**Constraints / expectations:**
- Compile-out in production
- Driver checks hooks

**Follow-ups:**
- Chaos testing
- Rate of injection

---

### C257 — Deterministic PRNG

**Interview prompt:**  
Implement a small deterministic PRNG for generating test vectors.

**Implement:**
```c
void prng_seed(uint32_t s);
uint32_t prng_u32(void);
```

**Constraints / expectations:**
- Reproducible sequence
- Document algorithm (xorshift OK)

**Follow-ups:**
- Range helper
- Shuffle

---

### C258 — CRC golden tests

**Interview prompt:**  
Assert CRC implementation against known vectors.

**Implement:**
```c
void test_crc16_vectors(void);
```

**Constraints / expectations:**
- At least 2-3 vectors
- Empty input

**Follow-ups:**
- Cross-check online tool
- Incremental update test

---

### C259 — Simulated ISR concurrency test

**Interview prompt:**  
From test code, call isr() between operations to catch races in ring/flags.

**Implement:**
```c
void test_race_flag(void);
```

**Constraints / expectations:**
- Show failing case without lock
- Passing with lock

**Follow-ups:**
- Thread sanitizer
- Model checking mention

---

### C260 — Bare-metal self-test main

**Interview prompt:**  
A main() that runs all self-tests and returns non-zero on failure (host or FW).

**Implement:**
```c
int main(void);
```

**Constraints / expectations:**
- Count pass/fail
- Print summary

**Follow-ups:**
- CI integration
- HW vs host builds

---


---

[← Back to category index](./README.md)
