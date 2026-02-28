# Google Embedded L4 — Top 30 In-Depth Interview Discussions

This file covers the 30 highest-priority questions with the same 9 sections for each problem:
1. Problem Statement
2. Clarifying Questions
3. Chosen Approach
4. Full C Code
5. Complexity
6. Core Invariants
7. Alternative Implementations
8. Follow-up Questions + Strong Answers
9. Interview Pitfalls

---

## Q082 — UART interrupt-based RX driver + ISR-safe ring buffer
### 1) Problem Statement
You are writing firmware for a battery-powered device. Implement an interrupt-driven UART RX path that handles burst traffic without blocking in ISR, exposes a non-blocking read API, and reports dropped bytes.

### 2) Clarifying Questions
1. Is producer strictly ISR and consumer strictly one task?
2. Overflow policy: drop newest or overwrite oldest?
3. Need timeout/blocking read or non-blocking only?

### 3) Chosen Approach
Use SPSC ring buffer, one-slot-open full detection, ISR-only enqueue, task-only dequeue.

### 4) Full C Code
```c
#include <stdint.h>
#include <stddef.h>

#define UART_SR_RXNE (1u << 5)

typedef struct {
    volatile uint32_t SR;
    volatile uint32_t DR;
} UartRegs;

typedef struct {
    uint8_t *buf;
    uint16_t cap;
    volatile uint16_t head;
    volatile uint16_t tail;
    volatile uint32_t overruns;
} UartRx;

static uint16_t nx(uint16_t i, uint16_t cap) { return (uint16_t)((i + 1u) % cap); }

void uart_rx_isr(UartRegs *u, UartRx *r) {
    while ((u->SR & UART_SR_RXNE) != 0u) {
        uint8_t b = (uint8_t)(u->DR & 0xFFu);
        uint16_t n = nx(r->head, r->cap);
        if (n == r->tail) { r->overruns++; continue; }
        r->buf[r->head] = b;
        r->head = n;
    }
}

size_t uart_rx_read_nb(UartRx *r, uint8_t *out, size_t max_len) {
    size_t n = 0;
    while (n < max_len && r->tail != r->head) {
        out[n++] = r->buf[r->tail];
        r->tail = nx(r->tail, r->cap);
    }
    return n;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Start from data-flow: ISR produces bytes, task consumes bytes.
2. Choose SPSC ring because it gives O(1) enqueue/dequeue with explicit overflow behavior.
3. This works because head/tail ownership is separated by context, keeping races and ISR latency low.

### 5) Complexity
- ISR enqueue per byte: O(1)
- Read per byte: O(1)
- Space: O(capacity)

### 6) Core Invariants
1. ISR writes `head`, task writes `tail`.
2. Full: `next(head) == tail`.
3. Empty: `head == tail`.

### 7) Alternative Implementations
1. Polling UART RX (simpler, CPU expensive).
2. DMA circular RX (better throughput, more complexity).

### 8) Follow-up Questions + Strong Answers
1. Why no parsing in ISR? ISR must stay bounded and minimal.
2. How detect data loss? expose `overruns` counter.
3. How add blocking read? wrap NB read with task wait/event.

### 9) Interview Pitfalls
1. No overflow policy.
2. Wrong full/empty logic.
3. Heavy ISR work.

---

## Q035 — SPSC circular buffer (array-based)
### 1) Problem Statement
Implement an SPSC ring buffer used between ISR and worker task with push/pop/available APIs, lock-free index ownership, and strict O(1) operations.

### 2) Clarifying Questions
1. Is capacity power-of-2?
2. Drop policy on full?
3. Atomic requirements on target?

### 3) Chosen Approach
Head/tail indices with one-slot-open rule and atomic publish.

### 4) Full C Code
```c
#include <stdatomic.h>
#include <stdint.h>

typedef struct {
    uint8_t *buf;
    uint32_t cap;
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
} SpscQ;

int spsc_push(SpscQ *q, uint8_t v) {
    uint32_t h = atomic_load_explicit(&q->head, memory_order_relaxed);
    uint32_t t = atomic_load_explicit(&q->tail, memory_order_acquire);
    uint32_t n = (h + 1u) % q->cap;
    if (n == t) return -1;
    q->buf[h] = v;
    atomic_store_explicit(&q->head, n, memory_order_release);
    return 0;
}

int spsc_pop(SpscQ *q, uint8_t *v) {
    uint32_t t = atomic_load_explicit(&q->tail, memory_order_relaxed);
    uint32_t h = atomic_load_explicit(&q->head, memory_order_acquire);
    if (t == h) return -1;
    *v = q->buf[t];
    atomic_store_explicit(&q->tail, (t + 1u) % q->cap, memory_order_release);
    return 0;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Identify that only one producer and one consumer exist.
2. Use ring indices with one-slot-open rule for simple full/empty detection.
3. This works because each operation updates constant state and preserves queue invariants.

### 5) Complexity
- Push/pop O(1)

### 6) Core Invariants
1. Producer only mutates head.
2. Consumer only mutates tail.

### 7) Alternative Implementations
1. Count-based full/empty.
2. Mutex-protected queue.

### 8) Follow-up Questions + Strong Answers
1. Why acquire/release? publish/consume ordering.
2. Why one-slot-open? avoids ambiguous full==empty.
3. How to support MPSC? add lock or queue-per-producer.

### 9) Interview Pitfalls
1. Non-atomic shared indices.
2. Cap < 2.

---

## Q084 — UART DMA TX driver
### 1) Problem Statement
Design a DMA-based UART TX path (`write_async`) with busy-state handling, completion interrupt callback, and deterministic error return codes.

### 2) Clarifying Questions
1. Can submit while busy?
2. Need cancellation API?
3. Cache coherent or not?

### 3) Chosen Approach
Track `tx_busy`; program DMA SRC/DST/LEN; ISR clears busy.

### 4) Full C Code
```c
#include <stdint.h>
#include <stddef.h>

typedef struct {
    volatile uint32_t SRC;
    volatile uint32_t DST;
    volatile uint32_t LEN;
    volatile uint32_t CTRL;
    volatile uint32_t STAT;
} DmaRegs;

typedef struct {
    DmaRegs *dma;
    volatile uint32_t *uart_dr;
    volatile int tx_busy;
} UartDmaTx;

int uart_dma_tx_start(UartDmaTx *d, const uint8_t *buf, uint32_t len) {
    if (!buf || len == 0u || d->tx_busy) return -1;
    d->tx_busy = 1;
    d->dma->SRC = (uint32_t)(uintptr_t)buf;
    d->dma->DST = (uint32_t)(uintptr_t)d->uart_dr;
    d->dma->LEN = len;
    d->dma->CTRL = 1u;
    return 0;
}

void uart_dma_tx_done_isr(UartDmaTx *d) {
    d->tx_busy = 0;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Model transfer lifecycle first: idle -> busy -> done.
2. Program DMA once and complete in ISR callback.
3. This works because buffer ownership and busy-state transitions are explicit and bounded.

### 5) Complexity
- Setup O(1)

### 6) Core Invariants
1. `tx_busy` true from submit until done ISR.
2. Source buffer remains valid while DMA owns it.

### 7) Alternative Implementations
1. IRQ TX FIFO drain.
2. Polling TX loop.

### 8) Follow-up Questions + Strong Answers
1. What if submit while busy? queue or return EBUSY.
2. Need cache clean? yes on non-coherent systems.
3. Timeout handling? abort DMA and reset channel.

### 9) Interview Pitfalls
1. Not handling in-flight buffer ownership.
2. No abort path.

---

## Q085 — UART DMA circular RX driver
### 1) Problem Statement
Implement UART circular-DMA RX consumption logic that uses hardware write index, handles wraparound correctly, and detects software overrun.

### 2) Clarifying Questions
1. How to obtain hardware write index?
2. Overrun policy?
3. Is zero-copy read required?

### 3) Chosen Approach
DMA writes circular buffer, software tracks read index and computes available bytes.

### 4) Full C Code
```c
#include <stdint.h>

typedef struct {
    uint8_t *buf;
    uint32_t cap;
    volatile uint32_t sw_read;
    volatile uint32_t overrun;
} UartDmaRx;

static uint32_t dma_avail(uint32_t hw_w, uint32_t sw_r, uint32_t cap) {
    return (hw_w + cap - sw_r) % cap;
}

uint32_t uart_dma_rx_read(UartDmaRx *r, uint32_t hw_w, uint8_t *out, uint32_t max_len) {
    uint32_t n = dma_avail(hw_w, r->sw_read, r->cap);
    if (n > max_len) n = max_len;
    for (uint32_t i = 0; i < n; i++) {
        out[i] = r->buf[r->sw_read];
        r->sw_read = (r->sw_read + 1u) % r->cap;
    }
    return n;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Treat hardware write index and software read index as two moving pointers.
2. Compute available bytes with wrap-safe modulo arithmetic.
3. This works because reads never pass hardware write boundary and wrap is handled deterministically.

### 5) Complexity
- Read O(n), availability O(1)

### 6) Core Invariants
1. DMA only writes hardware index region.
2. Software never advances beyond `hw_w`.

### 7) Alternative Implementations
1. Interrupt-per-byte RX.
2. Ping-pong DMA buffers.

### 8) Follow-up Questions + Strong Answers
1. How detect overrun? if distance exceeds cap-1.
2. Cache invalidate needed? yes for RX on non-coherent systems.
3. Parsing location? worker/task, not ISR.

### 9) Interview Pitfalls
1. Ignoring wrap boundary.
2. Missing cache maintenance.

---

## Q016 — Double-buffer DMA manager (ping-pong)
### 1) Problem Statement
Implement a ping-pong DMA buffer manager for continuous sampling where ISR flips active buffers and worker processes completed buffers safely.

### 2) Clarifying Questions
1. Half/full callbacks available?
2. Consumer latency bound?
3. What if both buffers pending?

### 3) Chosen Approach
Two equal buffers; DMA fills active one; ISR flips and queues completed buffer.

### 4) Full C Code
```c
#include <stdint.h>

typedef struct {
    uint8_t *buf_a;
    uint8_t *buf_b;
    volatile int active;   /* 0: A active, 1: B active */
    volatile int ready_a;
    volatile int ready_b;
} PingPong;

void pp_init(PingPong *p, uint8_t *a, uint8_t *b) {
    p->buf_a = a;
    p->buf_b = b;
    p->active = 0;
    p->ready_a = 0;
    p->ready_b = 0;
}

void pp_dma_done_isr(PingPong *p) {
    if (p->active == 0) p->ready_a = 1;
    else p->ready_b = 1;
    p->active ^= 1;
}

uint8_t *pp_take_ready(PingPong *p) {
    if (p->ready_a) { p->ready_a = 0; return p->buf_a; }
    if (p->ready_b) { p->ready_b = 0; return p->buf_b; }
    return 0;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Break stream handling into producer (DMA) and consumer (worker).
2. Use two buffers and flip active side on completion interrupt.
3. This works because one buffer is written while the other is processed, avoiding copy stalls.

### 5) Complexity
- ISR flip O(1)

### 6) Core Invariants
1. Exactly one active DMA target.
2. Ready flags represent completed buffers only.

### 7) Alternative Implementations
1. Circular DMA with software watermark.
2. N-buffer descriptor ring.

### 8) Follow-up Questions + Strong Answers
1. Consumer slower than producer? drop/overwrite/backpressure.
2. How signal worker? queue/event flag.
3. Cache invalidate point? before consumer reads ready buffer.

### 9) Interview Pitfalls
1. Data race on ready flags.
2. No overrun strategy.

---

## Q125 — Cache maintenance API for non-coherent DMA (clean/invalidate)
### 1) Problem Statement
Implement cache maintenance APIs for non-coherent DMA (`sync_for_device`, `sync_for_cpu`) with cache-line alignment and correct TX/RX ownership semantics.

### 2) Clarifying Questions
1. Is platform cache coherent?
2. Alignment constraints for cache lines?
3. Clean+invalidate granularity?

### 3) Chosen Approach
Expose two primitives: `sync_for_device` (TX) and `sync_for_cpu` (RX).

### 4) Full C Code
```c
#include <stddef.h>
#include <stdint.h>

#define CACHE_LINE 64u

static uintptr_t align_down(uintptr_t x, uintptr_t a) { return x & ~(a - 1u); }
static uintptr_t align_up(uintptr_t x, uintptr_t a) { return (x + a - 1u) & ~(a - 1u); }

void cache_clean_range(void *addr, size_t len) {
    uintptr_t s = align_down((uintptr_t)addr, CACHE_LINE);
    uintptr_t e = align_up((uintptr_t)addr + len, CACHE_LINE);
    for (uintptr_t p = s; p < e; p += CACHE_LINE) {
        /* platform_clean_line((void *)p); */
    }
}

void cache_invalidate_range(void *addr, size_t len) {
    uintptr_t s = align_down((uintptr_t)addr, CACHE_LINE);
    uintptr_t e = align_up((uintptr_t)addr + len, CACHE_LINE);
    for (uintptr_t p = s; p < e; p += CACHE_LINE) {
        /* platform_invalidate_line((void *)p); */
    }
}

void dma_sync_for_device(void *buf, size_t len) { cache_clean_range(buf, len); }
void dma_sync_for_cpu(void *buf, size_t len) { cache_invalidate_range(buf, len); }
```

### Quick Summary (How to come up with it + Why this works)
1. Separate TX and RX cache responsibilities.
2. Align ranges to cache-line boundaries before maintenance operations.
3. This works because CPU and DMA see consistent memory ownership at each handoff.

### 5) Complexity
- O(buffer_size / cache_line)

### 6) Core Invariants
1. TX buffer cleaned before DMA read.
2. RX buffer invalidated before CPU read.

### 7) Alternative Implementations
1. Uncached DMA heap region.
2. Bounce buffers.

### 8) Follow-up Questions + Strong Answers
1. Why clean and not invalidate on TX? device must see CPU writes.
2. Why invalidate on RX? CPU must drop stale lines.
3. Partial-line risk? align range to full cache lines.

### 9) Interview Pitfalls
1. Forgetting alignment to cache lines.
2. Calling invalidate before DMA completion.

---

## Q109 — Register map abstraction layer (HAL)
### 1) Problem Statement
Build a minimal MMIO HAL for peripheral registers with typed read/write helpers and clear separation between hardware access and driver logic.

### 2) Clarifying Questions
1. 8/16/32-bit register access needed?
2. Endianness conversion location?
3. Thread/ISR shared access?

### 3) Chosen Approach
Inline typed wrappers for direct MMIO operations.

### 4) Full C Code
```c
#include <stdint.h>

static inline uint32_t hal_reg_read32(volatile uint32_t *r) {
    return *r;
}

static inline void hal_reg_write32(volatile uint32_t *r, uint32_t v) {
    *r = v;
}

static inline void hal_reg_set_bits32(volatile uint32_t *r, uint32_t bits) {
    *r = *r | bits;
}

static inline void hal_reg_clr_bits32(volatile uint32_t *r, uint32_t bits) {
    *r = *r & ~bits;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Start with the smallest safe MMIO abstraction.
2. Provide typed inline read/write primitives only.
3. This works because all driver code uses one audited access path.

### 5) Complexity
- O(1)

### 6) Core Invariants
1. Register pointers are `volatile`.
2. Access width matches hardware spec.

### 7) Alternative Implementations
1. Macro-based accessors.
2. Function-pointer backend (for unit tests).

### 8) Follow-up Questions + Strong Answers
1. Why volatile? prevent compiler elision/reordering of MMIO operations.
2. Is volatile enough for synchronization? no, may still need barriers/locks.
3. How to unit test? use fake register backend.

### 9) Interview Pitfalls
1. Wrong register width access.
2. No abstraction for portability.

---

## Q110 — Safe register read-modify-write API
### 1) Problem Statement
Implement a safe register update helper that performs masked read-modify-write without clobbering unrelated bits and is reusable across drivers.

### 2) Clarifying Questions
1. Can register be concurrently updated by ISR/hardware?
2. Are there atomic set/clear alias registers?
3. Bitfield mask and shift conventions?

### 3) Chosen Approach
Central RMW helper + optional critical section wrapper.

### 4) Full C Code
```c
#include <stdint.h>

static inline uint32_t field_prep(uint32_t mask, uint32_t val) {
    uint32_t shift = 0u;
    while (((mask >> shift) & 1u) == 0u) shift++;
    return (val << shift) & mask;
}

static inline void hal_reg_rmw32(volatile uint32_t *r, uint32_t mask, uint32_t val) {
    uint32_t cur = *r;
    cur = (cur & ~mask) | field_prep(mask, val);
    *r = cur;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Identify risk: direct writes can clobber unrelated bits.
2. Use mask-based read-modify-write helper.
3. This works because only target field changes while all other bits are preserved.

### 5) Complexity
- O(number of trailing zeros) for `field_prep`, otherwise O(1)

### 6) Core Invariants
1. Only masked bits change.
2. Unmasked bits preserved.

### 7) Alternative Implementations
1. Pre-shifted value API.
2. Hardware SET/CLEAR registers (preferred if available).

### 8) Follow-up Questions + Strong Answers
1. RMW race with ISR? protect using lock/irq-off around operation.
2. Why not write whole register always? risks clobbering status/control bits.
3. How avoid shift loop cost? pass explicit shift.

### 9) Interview Pitfalls
1. Forgetting to mask input value.
2. Unprotected RMW in concurrent contexts.

---

## Q123 — Safe MMIO polling helper with timeout + typed errors
### 1) Problem Statement
Write a generic poll-with-timeout utility for MMIO status bits that returns typed outcomes (success/timeout) and is wraparound-safe for ticks.

### 2) Clarifying Questions
1. Timeout in ticks or microseconds?
2. Wraparound-safe time compare needed?
3. Busy-wait or sleep-yield allowed?

### 3) Chosen Approach
Polling helper with monotonic tick and typed return codes.

### 4) Full C Code
```c
#include <stdint.h>

typedef enum {
    POLL_OK = 0,
    POLL_TIMEOUT = -1
} PollStatus;

typedef uint32_t (*tick_fn)(void);

PollStatus wait_mask_eq(volatile uint32_t *reg,
                        uint32_t mask,
                        uint32_t expected,
                        tick_fn now,
                        uint32_t timeout_ticks) {
    uint32_t start = now();
    while ((uint32_t)(now() - start) < timeout_ticks) {
        if ((*reg & mask) == expected) return POLL_OK;
    }
    return POLL_TIMEOUT;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Define a generic polling contract (condition + deadline).
2. Use monotonic tick subtraction for timeout checks.
3. This works because loops are bounded and return typed outcomes for recovery logic.

### 5) Complexity
- O(timeout window)

### 6) Core Invariants
1. Poll exits only on success or timeout.
2. Wrap-safe tick subtraction used.

### 7) Alternative Implementations
1. Interrupt/event-driven completion.
2. Poll + sleep/yield backoff.

### 8) Follow-up Questions + Strong Answers
1. Why typed errors? cleaner driver diagnostics and recovery logic.
2. How reduce CPU burn? add delay/yield in loop.
3. What about spurious transient bits? require stable samples.

### 9) Interview Pitfalls
1. Infinite polling without timeout.
2. Incorrect timeout compare on wrap.

---

## Q089 — I2C master write transaction (start/stop + ACK)
### 1) Problem Statement
Implement blocking I2C master write transaction flow (START, address+W, payload, STOP) with ACK/NACK checks and timeout at every stage.

### 2) Clarifying Questions
1. 7-bit or 10-bit addressing?
2. Need repeated-start support in same API?
3. What error code on NACK vs timeout?

### 3) Chosen Approach
Stateful blocking transfer with bounded wait at each stage.

### 4) Full C Code
```c
#include <stdint.h>

typedef struct {
    volatile uint32_t CR;
    volatile uint32_t SR;
    volatile uint32_t DR;
} I2cRegs;

#define I2C_START   (1u << 8)
#define I2C_STOP    (1u << 9)
#define I2C_EV_SB   (1u << 0)
#define I2C_EV_TXE  (1u << 1)

int i2c_write_blocking(I2cRegs *i2c, uint8_t addr7, const uint8_t *data, uint32_t n, uint32_t to) {
    i2c->CR |= I2C_START;
    while (((i2c->SR & I2C_EV_SB) == 0u) && to--) {}
    if (to == 0u) return -1;

    i2c->DR = (uint32_t)(addr7 << 1); /* write bit = 0 */
    to = 100000u;
    while (((i2c->SR & I2C_EV_TXE) == 0u) && to--) {}
    if (to == 0u) return -2;

    for (uint32_t i = 0; i < n; i++) {
        i2c->DR = data[i];
        to = 100000u;
        while (((i2c->SR & I2C_EV_TXE) == 0u) && to--) {}
        if (to == 0u) return -3;
    }

    i2c->CR |= I2C_STOP;
    return 0;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Expand protocol into strict ordered states: START, ADDR, DATA, STOP.
2. Add timeout at every wait point.
3. This works because each stage either succeeds or exits with clear error status.

### 5) Complexity
- O(n + waits)

### 6) Core Invariants
1. STOP sent on successful completion.
2. Each stage has timeout guard.

### 7) Alternative Implementations
1. Interrupt-driven I2C state machine.
2. DMA for long writes.

### 8) Follow-up Questions + Strong Answers
1. NACK handling? return typed error and optionally issue recovery.
2. Bus busy forever? timeout then reset/recover bus.
3. Where add retries? wrapper layer, not inside low-level primitive.

### 9) Interview Pitfalls
1. No timeout on stage waits.
2. Ignoring NACK path.

---

## Q090 — I2C master read transaction (repeated start)
### 1) Problem Statement
Implement I2C master read flow using repeated START (optional register-address phase + address+R + N-byte read + STOP) with timeout handling.

### 2) Clarifying Questions
1. Single-byte read special handling required?
2. Need repeated-start after register address write?
3. Last-byte NACK sequence specifics?

### 3) Chosen Approach
Blocking read with stage timeouts; NACK on final byte.

### 4) Full C Code
```c
#include <stdint.h>

#define I2C_EV_RXNE (1u << 6)

int i2c_read_blocking(I2cRegs *i2c, uint8_t addr7, uint8_t *out, uint32_t n, uint32_t to) {
    i2c->CR |= I2C_START;
    while (((i2c->SR & I2C_EV_SB) == 0u) && to--) {}
    if (to == 0u) return -1;

    i2c->DR = (uint32_t)((addr7 << 1) | 1u); /* read bit = 1 */
    to = 100000u;
    while (((i2c->SR & I2C_EV_TXE) == 0u) && to--) {}
    if (to == 0u) return -2;

    for (uint32_t i = 0; i < n; i++) {
        to = 100000u;
        while (((i2c->SR & I2C_EV_RXNE) == 0u) && to--) {}
        if (to == 0u) return -3;
        out[i] = (uint8_t)i2c->DR;
    }

    i2c->CR |= I2C_STOP;
    return 0;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Break read flow into address phase and data phase.
2. Wait on RX-ready before each byte.
3. This works because transaction progress is validated at every stage with timeout safety.

### 5) Complexity
- O(n + waits)

### 6) Core Invariants
1. RX read only when RXNE set.
2. Transfer bounded by timeout.

### 7) Alternative Implementations
1. IRQ-driven read state machine.
2. Combined register-read helper (write reg, repeated-start read).

### 8) Follow-up Questions + Strong Answers
1. Clock stretching handling? wait loops naturally account for it with timeout.
2. Why repeated-start? avoids releasing bus between phases.
3. Last-byte ACK/NACK detail? hardware-specific, configure before final read.

### 9) Interview Pitfalls
1. Missing STOP on exit paths.
2. Not handling single-byte edge case.

---

## Q091 — I2C bus recovery for stuck lines
### 1) Problem Statement
Implement I2C bus-recovery routine for stuck SDA by toggling SCL pulses, issuing STOP, and returning a recover/fail status for caller escalation.

### 2) Clarifying Questions
1. Are SCL/SDA controllable via GPIO fallback?
2. How many recovery pulses expected?
3. What is failure escalation policy?

### 3) Chosen Approach
Generate up to 9 SCL pulses, attempt STOP condition, then reinit controller.

### 4) Full C Code
```c
void i2c_recover_lines(void (*set_scl)(int), void (*set_sda)(int), int (*get_sda)(void)) {
    set_sda(1);
    for (int i = 0; i < 9 && !get_sda(); i++) {
        set_scl(0);
        set_scl(1);
    }
    /* STOP: SDA rising while SCL high */
    set_sda(0);
    set_scl(1);
    set_sda(1);
}
```

### Quick Summary (How to come up with it + Why this works)
1. Start from physical bus behavior: stuck SDA can be clocked out.
2. Generate bounded SCL pulses then STOP.
3. This works because recovery is deterministic and leaves bus in known idle state.

### 5) Complexity
- O(1), bounded pulses

### 6) Core Invariants
1. Recovery attempts bounded.
2. STOP condition attempted before exit.

### 7) Alternative Implementations
1. Peripheral soft reset only.
2. Full bus reset including power-cycle of slave.

### 8) Follow-up Questions + Strong Answers
1. If recovery fails? mark bus fault, escalate reset.
2. Why 9 pulses? release potential stuck slave shift state.
3. Should this run in ISR? no, run in task/recovery context.

### 9) Interview Pitfalls
1. Infinite pulse loop.
2. Not restoring pinmux/peripheral state.

---

## Q086 — SPI master blocking transfer
### 1) Problem Statement
Implement SPI master blocking transfer (`transfer(tx, rx, len)`) for full-duplex operation with bounded wait and clean chip-select sequencing assumptions.

### 2) Clarifying Questions
1. CPOL/CPHA mode selection?
2. Chip-select controlled by driver or caller?
3. Timeout needed for each byte?

### 3) Chosen Approach
For each byte: write TX, wait RX ready, read RX. Bound waits with timeout.

### 4) Full C Code
```c
#include <stdint.h>

typedef struct {
    volatile uint32_t SR;
    volatile uint32_t DR;
} SpiRegs;

#define SPI_RX_READY (1u << 0)

int spi_transfer_blocking(SpiRegs *s, const uint8_t *tx, uint8_t *rx, uint32_t n, uint32_t to) {
    for (uint32_t i = 0; i < n; i++) {
        s->DR = tx ? tx[i] : 0xFFu;
        uint32_t t = to;
        while (((s->SR & SPI_RX_READY) == 0u) && t--) {}
        if (t == 0u) return -1;
        if (rx) rx[i] = (uint8_t)s->DR;
    }
    return 0;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Model each SPI byte as TX then RX completion.
2. Loop for length and bound wait on status bit.
3. This works because full-duplex semantics are respected per byte with no hidden state.

### 5) Complexity
- O(n + waits)

### 6) Core Invariants
1. One RX read per TX write.
2. Wait path bounded by timeout.

### 7) Alternative Implementations
1. Interrupt-driven SPI state machine.
2. DMA full-duplex transfer.

### 8) Follow-up Questions + Strong Answers
1. Why read RX in TX-only transfer? clear shift register data path.
2. CS timing? assert before first byte, deassert after last.
3. Larger throughput path? DMA.

### 9) Interview Pitfalls
1. Ignoring RX in full-duplex peripheral.
2. Missing timeout causing deadlock.

---

## Q088 — SPI DMA full-duplex transfer
### 1) Problem Statement
Implement SPI full-duplex DMA transfer using paired TX/RX channels; operation completes only when both channels report done or error.

### 2) Clarifying Questions
1. Separate TX/RX DMA channels?
2. Completion condition: both done?
3. Need cancellation API?

### 3) Chosen Approach
Program both descriptors, start RX then TX, complete when both done flags set.

### 4) Full C Code
```c
#include <stdint.h>

typedef struct {
    volatile uint32_t SRC;
    volatile uint32_t DST;
    volatile uint32_t LEN;
    volatile uint32_t CTRL;
    volatile uint32_t STAT;
} DmaCh;

int spi_dma_duplex_start(DmaCh *tx, DmaCh *rx,
                         const uint8_t *src, uint8_t *dst,
                         volatile uint32_t *spi_dr, uint32_t len) {
    rx->SRC = (uint32_t)(uintptr_t)spi_dr;
    rx->DST = (uint32_t)(uintptr_t)dst;
    rx->LEN = len;

    tx->SRC = (uint32_t)(uintptr_t)src;
    tx->DST = (uint32_t)(uintptr_t)spi_dr;
    tx->LEN = len;

    rx->CTRL = 1u;
    tx->CTRL = 1u;
    return 0;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Treat TX and RX DMA as one atomic transfer operation.
2. Configure both descriptors and start in safe order.
3. This works because both directions are synchronized and completion criteria are explicit.

### 5) Complexity
- O(1) setup

### 6) Core Invariants
1. RX/TX lengths match.
2. Destination/source ownership valid for DMA lifetime.

### 7) Alternative Implementations
1. Blocking SPI loop.
2. IRQ-driven finite-state transfer.

### 8) Follow-up Questions + Strong Answers
1. Why start RX first? avoid losing early incoming data.
2. How abort transfer? disable both channels and flush SPI.
3. Cache actions needed? clean TX, invalidate RX (non-coherent).

### 9) Interview Pitfalls
1. Asymmetric channel completion handling.
2. Not checking DMA error flags.

---

## Q099 — Software timer queue (sorted linked list)
### 1) Problem Statement
Implement a software timer queue with deterministic insert/cancel/expire behavior suitable for RTOS-style periodic tick processing.

### 2) Clarifying Questions
1. Callback context ISR or worker?
2. Stable order for equal expiry?
3. Tick wraparound behavior?

### 3) Chosen Approach
Maintain ascending list by expiry; pop from head while expired.

### 4) Full C Code
```c
#include <stdint.h>

typedef void (*tm_cb)(void *);

typedef struct TNode {
    uint32_t exp;
    tm_cb cb;
    void *arg;
    struct TNode *next;
} TNode;

void timer_insert(TNode **head, TNode *n) {
    if (!*head || n->exp < (*head)->exp) {
        n->next = *head;
        *head = n;
        return;
    }
    TNode *c = *head;
    while (c->next && c->next->exp <= n->exp) c = c->next;
    n->next = c->next;
    c->next = n;
}

void timer_run_expired(TNode **head, uint32_t now) {
    while (*head && (int32_t)((*head)->exp - now) <= 0) {
        TNode *n = *head;
        *head = n->next;
        if (n->cb) n->cb(n->arg);
    }
}
```

### Quick Summary (How to come up with it + Why this works)
1. Use earliest-expiry-first ordering as core invariant.
2. Insert timers in sorted position and expire from head.
3. This works because expiration scanning is linear only over due timers.

### 5) Complexity
- Insert O(n), expire O(k)

### 6) Core Invariants
1. Queue sorted by `exp`.
2. Head is earliest timer.

### 7) Alternative Implementations
1. Min-heap timer queue.
2. Timer wheel for high timer count.

### 8) Follow-up Questions + Strong Answers
1. Equal expiry order? keep insertion order by `<=` condition.
2. Callback latency issue? dispatch callbacks in worker.
3. Wrap-safe compare? signed delta or helper macro.

### 9) Interview Pitfalls
1. Incorrect wrap comparison.
2. Long callback execution inside time-critical path.

---

## Q100 — Periodic timer rescheduling without drift
### 1) Problem Statement
Implement periodic timer rescheduling logic that preserves phase (no drift) even when callbacks run late under system load.

### 2) Clarifying Questions
1. Should missed periods be skipped or replayed?
2. Is strict phase alignment required?
3. max backlog policy?

### 3) Chosen Approach
Update `next_expiry += period` instead of `now + period`.

### 4) Full C Code
```c
#include <stdint.h>

void periodic_next_no_drift(uint32_t *next_exp, uint32_t period) {
    *next_exp += period;
}

void periodic_catch_up(uint32_t *next_exp, uint32_t period, uint32_t now) {
    while ((int32_t)(*next_exp - now) <= 0) {
        *next_exp += period;
    }
}
```

### Quick Summary (How to come up with it + Why this works)
1. Keep periodic schedule anchored to previous target time.
2. Reschedule with `next += period` instead of `now + period`.
3. This works because callback delay does not accumulate into long-term drift.

### 5) Complexity
- O(1) normal, O(missed_periods) with catch-up loop

### 6) Core Invariants
1. Phase anchored to original schedule.
2. Drift does not accumulate from callback delay.

### 7) Alternative Implementations
1. `next = now + period` (simple, drifts).
2. Skip-missed-only-once strategy.

### 8) Follow-up Questions + Strong Answers
1. Why no-drift needed? periodic control loops/timers require phase stability.
2. Missed many periods? choose skip or catch-up policy explicitly.
3. Jitter metrics? track callback lateness histogram.

### 9) Interview Pitfalls
1. Using `now + period` unintentionally.
2. Unbounded catch-up loop under overload.

---

## Q101 — Race-safe timer cancellation
### 1) Problem Statement
Implement timer cancellation that is race-safe when cancel requests and expiry callbacks can occur nearly simultaneously.

### 2) Clarifying Questions
1. Is cancel called from ISR/task/both?
2. Can callback run concurrently with cancel?
3. Do we need synchronous cancel semantics?

### 3) Chosen Approach
Protected queue remove + cancelled flag checked before callback execute.

### 4) Full C Code
```c
#include <stdint.h>

typedef struct CTimer {
    uint32_t exp;
    volatile int cancelled;
    void (*cb)(void *);
    void *arg;
    struct CTimer *next;
} CTimer;

int timer_cancel(CTimer **head, CTimer *t) {
    CTimer *p = 0, *c = *head;
    while (c) {
        if (c == t) {
            if (p) p->next = c->next;
            else *head = c->next;
            t->cancelled = 1;
            return 0;
        }
        p = c;
        c = c->next;
    }
    t->cancelled = 1;
    return -1;
}

void timer_fire_if_valid(CTimer *t) {
    if (!t->cancelled && t->cb) t->cb(t->arg);
}
```

### Quick Summary (How to come up with it + Why this works)
1. Identify race window between cancel and fire.
2. Remove from queue and keep cancelled marker for safety.
3. This works because callback path checks validity before executing.

### 5) Complexity
- Cancel O(n)

### 6) Core Invariants
1. Cancelled timer callback must not run.
2. Queue links remain valid after removal.

### 7) Alternative Implementations
1. Lazy cancel flag without physical removal.
2. Refcounted timer objects.

### 8) Follow-up Questions + Strong Answers
1. Cancel while callback running? need sync cancel + callback state handshake.
2. Why cancelled flag if removed? handles race windows.
3. Bulk cancel approach? generation counters.

### 9) Interview Pitfalls
1. Use-after-free timer node.
2. Cancel API without race semantics defined.

---

## Q105 — Driver timeout wrapper pattern
### 1) Problem Statement
Wrap a non-blocking driver primitive with timeout control so callers get bounded latency and explicit status for success/retry/timeout.

### 2) Clarifying Questions
1. Polling operation or event-based completion?
2. Timeout units and source clock?
3. Distinguish timeout vs device error?

### 3) Chosen Approach
Generic retry loop over non-blocking op until success or timeout expiry.

### 4) Full C Code
```c
#include <stdint.h>

typedef int (*op_try_fn)(void *ctx);
typedef uint32_t (*tick_now_fn)(void);

int op_with_timeout(op_try_fn fn, void *ctx, tick_now_fn now, uint32_t timeout_ticks) {
    uint32_t start = now();
    while ((uint32_t)(now() - start) < timeout_ticks) {
        int rc = fn(ctx);
        if (rc == 0) return 0;
        if (rc < 0 && rc != -11) return rc; /* -11: EAGAIN-like */
    }
    return -1;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Keep core operation non-blocking and wrap externally with timeout.
2. Retry only while deadline not exceeded.
3. This works because latency stays bounded and control flow stays composable.

### 5) Complexity
- O(timeout window)

### 6) Core Invariants
1. Wrapper exits on success or deadline.
2. Non-retryable errors propagate immediately.

### 7) Alternative Implementations
1. Blocking wait on interrupt/event.
2. Hardware timer one-shot timeout callback.

### 8) Follow-up Questions + Strong Answers
1. Why separate timeout wrapper? keeps low-level op deterministic and reusable.
2. Should wrapper sleep? yes in task context to reduce CPU.
3. Timeout telemetry? count and expose per-driver metrics.

### 9) Interview Pitfalls
1. Infinite loop on repeated EAGAIN.
2. Timeout logic not wrap-safe.

---

## Q106 — Retry logic with exponential backoff
### 1) Problem Statement
Implement bounded retry with exponential backoff (and optional jitter hook) for transient transport/peripheral failures.

### 2) Clarifying Questions
1. Which errors are retryable?
2. Max retry count and max delay?
3. Need jitter?

### 3) Chosen Approach
Bounded retries with exponential backoff and optional jitter hook.

### 4) Full C Code
```c
#include <stdint.h>

typedef int (*run_fn)(void *);
typedef void (*sleep_fn)(uint32_t ticks);

int retry_exp_backoff(run_fn fn, void *ctx, sleep_fn sleep_ticks, int max_retry) {
    uint32_t delay = 1u;
    for (int i = 0; i < max_retry; i++) {
        int rc = fn(ctx);
        if (rc == 0) return 0;
        if (rc < 0 && rc != -11) return rc; /* non-retryable */
        sleep_ticks(delay);
        if (delay < 1024u) delay <<= 1;
    }
    return -1;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Classify errors as retryable vs fatal first.
2. Apply bounded exponential backoff per retry attempt.
3. This works because retry storms are reduced and termination is guaranteed.

### 5) Complexity
- O(max_retry)

### 6) Core Invariants
1. Retries bounded.
2. Delay non-decreasing and capped.

### 7) Alternative Implementations
1. Fixed retry interval.
2. Fibonacci backoff.

### 8) Follow-up Questions + Strong Answers
1. Why jitter? avoids synchronized retry storms.
2. Where to retry? wrapper layer, not deep HAL.
3. Logging strategy? log final failure + retry count.

### 9) Interview Pitfalls
1. Retrying fatal errors.
2. Unbounded backoff growth.

---

## Q107 — Driver reset/reinit sequence on failure
### 1) Problem Statement
Implement driver recovery workflow (`stop -> abort -> reset -> reinit`) with strict stage-by-stage error reporting and no stale in-flight state.

### 2) Clarifying Questions
1. What must be drained before reset?
2. Preserve configuration across reset?
3. max reset attempts?

### 3) Chosen Approach
Quiesce -> abort IO -> HW reset -> reconfigure -> resume.

### 4) Full C Code
```c
typedef struct {
    int (*stop_io)(void *);
    int (*abort_dma)(void *);
    int (*hw_reset)(void *);
    int (*reinit)(void *);
} RecoverOps;

int driver_recover(void *ctx, const RecoverOps *ops) {
    if (ops->stop_io(ctx) != 0) return -1;
    if (ops->abort_dma(ctx) != 0) return -2;
    if (ops->hw_reset(ctx) != 0) return -3;
    if (ops->reinit(ctx) != 0) return -4;
    return 0;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Sequence recovery explicitly: stop, abort, reset, reinit.
2. Return stage-specific failure codes.
3. This works because stale hardware/software state is cleared before restart.

### 5) Complexity
- O(recovery workflow)

### 6) Core Invariants
1. No in-flight DMA after abort.
2. Driver state transitions are explicit.

### 7) Alternative Implementations
1. Soft reset only.
2. Full subsystem reset including clocks/power.

### 8) Follow-up Questions + Strong Answers
1. What happens to queued requests? fail or replay with clear policy.
2. How avoid reset loops? cap attempts + escalate fatal state.
3. What telemetry to keep? reset count, reason code, last error.

### 9) Interview Pitfalls
1. Reset without quiescing IO.
2. Losing synchronization after reinit.

---

## Q108 — Fault-tolerant driver state machine
### 1) Problem Statement
Implement explicit driver finite-state machine (INIT/IDLE/BUSY/ERR) that rejects illegal transitions and defines recovery entry points.

### 2) Clarifying Questions
1. Required states?
2. Which events valid in each state?
3. Recovery transition requirements?

### 3) Chosen Approach
Enumerated state+event transition function with invalid-event handling.

### 4) Full C Code
```c
typedef enum { ST_INIT, ST_IDLE, ST_BUSY, ST_ERR } DrvState;
typedef enum { EV_INIT_OK, EV_START, EV_DONE, EV_FAIL, EV_RESET } DrvEvent;

DrvState drv_state_step(DrvState s, DrvEvent e) {
    switch (s) {
        case ST_INIT:
            return (e == EV_INIT_OK) ? ST_IDLE : ST_INIT;
        case ST_IDLE:
            return (e == EV_START) ? ST_BUSY : ST_IDLE;
        case ST_BUSY:
            if (e == EV_DONE) return ST_IDLE;
            if (e == EV_FAIL) return ST_ERR;
            return ST_BUSY;
        case ST_ERR:
            return (e == EV_RESET) ? ST_INIT : ST_ERR;
        default:
            return ST_ERR;
    }
}
```

### Quick Summary (How to come up with it + Why this works)
1. Make state transitions explicit with enum-based FSM.
2. Handle only valid events per state.
3. This works because illegal flows cannot silently corrupt driver lifecycle.

### 5) Complexity
- O(1)

### 6) Core Invariants
1. Illegal transitions do not silently enter undefined state.
2. Error state is terminal until explicit reset.

### 7) Alternative Implementations
1. Table-driven transition matrix.
2. Object-oriented state handlers.

### 8) Follow-up Questions + Strong Answers
1. Why explicit FSM? prevents hidden error paths.
2. How test? transition table coverage tests.
3. Add timeout state? yes if operation deadlines required.

### 9) Interview Pitfalls
1. Implicit transitions in scattered code.
2. No clear recovery path from error state.

---

## Q001 — Fixed-size memory pool allocator
### 1) Problem Statement
Implement a fixed-size memory pool allocator for embedded firmware with O(1) allocate/free, deterministic behavior, and no dynamic heap calls.

### 2) Clarifying Questions
1. Required alignment?
2. Need double-free detection?
3. ISR-safe usage required?

### 3) Chosen Approach
Intrusive free-list stored inside blocks.

### 4) Full C Code
```c
#include <stddef.h>
#include <stdint.h>

typedef struct Node { struct Node *next; } Node;

typedef struct {
    uint8_t *arena;
    size_t block_size;
    size_t blocks;
    Node *free_head;
} Pool;

void pool_init(Pool *p, void *arena, size_t block_size, size_t blocks) {
    p->arena = (uint8_t *)arena;
    p->block_size = block_size;
    p->blocks = blocks;
    p->free_head = 0;
    for (size_t i = 0; i < blocks; i++) {
        Node *n = (Node *)(p->arena + i * block_size);
        n->next = p->free_head;
        p->free_head = n;
    }
}

void *pool_alloc(Pool *p) {
    if (!p->free_head) return 0;
    Node *n = p->free_head;
    p->free_head = n->next;
    return n;
}

void pool_free(Pool *p, void *ptr) {
    if (!ptr) return;
    Node *n = (Node *)ptr;
    n->next = p->free_head;
    p->free_head = n;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Recognize fixed object size requirement and determinism goal.
2. Use intrusive free-list inside preallocated blocks.
3. This works because alloc/free are constant-time and heap fragmentation is eliminated.

### 5) Complexity
- Alloc O(1), free O(1)

### 6) Core Invariants
1. Each free block appears once in list.
2. Allocated block not in free list.

### 7) Alternative Implementations
1. Bitmap allocator.
2. Slab cache wrapper.

### 8) Follow-up Questions + Strong Answers
1. How detect invalid free? address-range + alignment checks.
2. How expose stats? in-use, peak, fail counters.
3. Why useful in embedded? deterministic, no fragmentation.

### 9) Interview Pitfalls
1. Allowing misaligned block size.
2. No validation hooks in debug builds.

---

## Q004 — Variable-size free-list allocator (first-fit)
### 1) Problem Statement
Implement variable-size arena allocator using first-fit split strategy from static memory, intended for task context (not ISR hot path).

### 2) Clarifying Questions
1. First-fit or best-fit?
2. Minimum split threshold?
3. Need coalescing on free?

### 3) Chosen Approach
Address-sorted free list with split on alloc and coalesce on free.

### 4) Full C Code
```c
#include <stddef.h>
#include <stdint.h>

typedef struct FreeBlock {
    size_t size;
    struct FreeBlock *next;
} FreeBlock;

static size_t a8(size_t n) { return (n + 7u) & ~7u; }

void *fl_alloc(FreeBlock **head, size_t req) {
    req = a8(req);
    FreeBlock *p = 0, *c = *head;
    while (c) {
        if (c->size >= req) {
            size_t rem = c->size - req;
            if (rem > sizeof(FreeBlock) + 8u) {
                FreeBlock *s = (FreeBlock *)((uint8_t *)c + sizeof(FreeBlock) + req);
                s->size = rem - sizeof(FreeBlock);
                s->next = c->next;
                if (p) p->next = s; else *head = s;
                c->size = req;
            } else {
                if (p) p->next = c->next; else *head = c->next;
            }
            return (uint8_t *)c + sizeof(FreeBlock);
        }
        p = c; c = c->next;
    }
    return 0;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Start from static arena and variable-size request needs.
2. Use first-fit with split threshold.
3. This works because memory usage is flexible while staying within bounded storage.

### 5) Complexity
- Worst-case O(n) scan

### 6) Core Invariants
1. Free blocks do not overlap.
2. Header immediately precedes payload.

### 7) Alternative Implementations
1. Buddy allocator.
2. Segregated free lists.

### 8) Follow-up Questions + Strong Answers
1. Why first-fit? simpler and typically fast enough.
2. Fragmentation mitigation? coalescing + thresholds.
3. RT suitability? avoid on hard ISR paths.

### 9) Interview Pitfalls
1. Splitting into unusable tiny fragments.
2. Missing alignment handling.

---

## Q006 — Free-list coalescing (prev/next/both sides)
### 1) Problem Statement
Implement coalescing for freed variable-size blocks so adjacent regions merge correctly and long-run fragmentation is reduced.

### 2) Clarifying Questions
1. Is free list address-sorted?
2. Merge policy both sides?
3. Need validation against double-free?

### 3) Chosen Approach
Insert by address, then coalesce with immediate prev/next neighbors.

### 4) Full C Code
```c
void fl_free(FreeBlock **head, void *ptr, size_t sz) {
    if (!ptr) return;
    sz = a8(sz);
    FreeBlock *b = (FreeBlock *)((uint8_t *)ptr - sizeof(FreeBlock));
    b->size = sz;

    FreeBlock *p = 0, *c = *head;
    while (c && c < b) { p = c; c = c->next; }
    b->next = c;
    if (p) p->next = b; else *head = b;

    if (b->next && (uint8_t *)b + sizeof(FreeBlock) + b->size == (uint8_t *)b->next) {
        b->size += sizeof(FreeBlock) + b->next->size;
        b->next = b->next->next;
    }
    if (p && (uint8_t *)p + sizeof(FreeBlock) + p->size == (uint8_t *)b) {
        p->size += sizeof(FreeBlock) + b->size;
        p->next = b->next;
    }
}
```

### Quick Summary (How to come up with it + Why this works)
1. Observe that fragmentation comes from adjacent free fragments.
2. Insert by address and merge neighbors immediately.
3. This works because contiguous space is restored as soon as possible.

### 5) Complexity
- O(n) insert + O(1) neighbor merge checks

### 6) Core Invariants
1. Free list remains address-sorted.
2. Adjacent free blocks eventually merged.

### 7) Alternative Implementations
1. Lazy coalescing pass.
2. Boundary-tag allocator.

### 8) Follow-up Questions + Strong Answers
1. Why sorted list? enables O(1) adjacency checks.
2. Both-side merge needed? yes to reduce fragmentation quickly.
3. How detect overlap bugs? debug assertions on insert.

### 9) Interview Pitfalls
1. Forgetting second merge with previous block.
2. Broken links after merge.

---

## Q017 — ISR-safe object pool
### 1) Problem Statement
Implement ISR-safe object pool allocation/free with short critical sections and explicit behavior when pool is exhausted.

### 2) Clarifying Questions
1. Lock-free required or short critical section allowed?
2. Exhaustion behavior?
3. Multi-producer contexts?

### 3) Chosen Approach
Fixed pool + brief critical section around free-list head updates.

### 4) Full C Code
```c
typedef struct INode { struct INode *next; } INode;

typedef struct {
    INode *free_head;
} IsrPool;

static inline void enter_critical(void) { /* disable irq */ }
static inline void exit_critical(void) { /* enable irq */ }

void isr_pool_init(IsrPool *p, void *arena, size_t bs, size_t n) {
    p->free_head = 0;
    uint8_t *b = (uint8_t *)arena;
    for (size_t i = 0; i < n; i++) {
        INode *node = (INode *)(b + i * bs);
        node->next = p->free_head;
        p->free_head = node;
    }
}

void *isr_pool_alloc(IsrPool *p) {
    enter_critical();
    INode *n = p->free_head;
    if (n) p->free_head = n->next;
    exit_critical();
    return n;
}

void isr_pool_free(IsrPool *p, void *obj) {
    if (!obj) return;
    enter_critical();
    INode *n = (INode *)obj;
    n->next = p->free_head;
    p->free_head = n;
    exit_critical();
}
```

### Quick Summary (How to come up with it + Why this works)
1. Identify ISR constraints: no blocking and no general heap.
2. Use fixed pool with tiny critical section around head updates.
3. This works because allocation remains O(1) and interrupt-safe.

### 5) Complexity
- O(1)

### 6) Core Invariants
1. Free list head updates are atomic w.r.t. ISR/task access.
2. No blocking or dynamic allocation in ISR.

### 7) Alternative Implementations
1. Lock-free stack with tagged pointers.
2. Per-context pools.

### 8) Follow-up Questions + Strong Answers
1. What on exhaustion? return NULL and count drops/failures.
2. Why fixed-size only? deterministic and fragmentation-free.
3. Critical section too long? keep only pointer swap inside.

### 9) Interview Pitfalls
1. Calling malloc in ISR fallback.
2. Missing critical section around head updates.

---

## Q074 — LRU cache (hash + doubly linked list)
### 1) Problem Statement
Implement a fixed-capacity LRU cache in C using hash table + doubly linked list with O(1) average get/put and eviction.

### 2) Clarifying Questions
1. Fixed capacity?
2. Collision strategy in hash map?
3. Thread safety required?

### 3) Chosen Approach
Hash map from key->node, DLL for MRU/LRU order.

### 4) Full C Code
```c
#include <stdlib.h>

typedef struct LNode {
    int key, val;
    struct LNode *prev, *next;
} LNode;

typedef struct Ent {
    int key;
    LNode *node;
    struct Ent *next;
} Ent;

typedef struct {
    int cap, size, buckets;
    Ent **tab;
    LNode *head, *tail;
} LRU;

static unsigned h(int k, int b) { return ((unsigned)k * 2654435761u) % (unsigned)b; }

static void attach_front(LRU *c, LNode *n) {
    n->prev = 0; n->next = c->head;
    if (c->head) c->head->prev = n;
    c->head = n;
    if (!c->tail) c->tail = n;
}

static void detach_node(LRU *c, LNode *n) {
    if (n->prev) n->prev->next = n->next; else c->head = n->next;
    if (n->next) n->next->prev = n->prev; else c->tail = n->prev;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Break requirement into lookup speed and recency order.
2. Combine hash map (find) + doubly list (order updates).
3. This works because get/put and eviction stay O(1) on average.

### 5) Complexity
- `get/put`: O(1) average

### 6) Core Invariants
1. Head = MRU, tail = LRU.
2. Hash entry always points to active DLL node.

### 7) Alternative Implementations
1. Tree map + list (O(log n)).
2. Clock algorithm approximation.

### 8) Follow-up Questions + Strong Answers
1. Why DLL not singly list? O(1) detach with prev.
2. Collision impact? worst-case O(n), average O(1).
3. Thread safety? lock around both map and list updates.

### 9) Interview Pitfalls
1. Forgetting to update both structures on eviction.
2. Memory leaks on delete path.

---

## Q078 — Intrusive linked list (Linux style)
### 1) Problem Statement
Implement Linux-style intrusive doubly linked list primitives for driver queue management where node is embedded in owner struct.

### 2) Clarifying Questions
1. Singly or doubly intrusive list?
2. Need safe iteration during delete?
3. Allocation ownership model?

### 3) Chosen Approach
Circular doubly intrusive list with head sentinel.

### 4) Full C Code
```c
struct list_head {
    struct list_head *next;
    struct list_head *prev;
};

static inline void INIT_LIST_HEAD(struct list_head *h) {
    h->next = h;
    h->prev = h;
}

static inline void list_add(struct list_head *n, struct list_head *h) {
    n->next = h->next;
    n->prev = h;
    h->next->prev = n;
    h->next = n;
}

static inline void list_del(struct list_head *e) {
    e->prev->next = e->next;
    e->next->prev = e->prev;
    e->next = e->prev = 0;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Notice node allocation overhead is avoidable.
2. Embed list node in owner object and operate on links directly.
3. This works because insertion/removal are O(1) with strong locality.

### 5) Complexity
- Add/delete known node O(1)

### 6) Core Invariants
1. Head remains circular sentinel.
2. Node removed has null links for debug safety.

### 7) Alternative Implementations
1. Non-intrusive list (extra node allocations).
2. Singly intrusive list.

### 8) Follow-up Questions + Strong Answers
1. Why intrusive in kernels? avoids alloc overhead, better locality.
2. Safe delete during traversal? use next-temp iteration macro pattern.
3. Ownership? owner struct lifetime controls node lifetime.

### 9) Interview Pitfalls
1. Deleting node twice.
2. Corrupting prev/next symmetry.

---

## Q079 — container_of() macro
### 1) Problem Statement
Implement and use `container_of()` to recover parent object from embedded member pointer in intrusive data-structure code.

### 2) Clarifying Questions
1. Is member guaranteed valid?
2. Need const-correct variant?
3. Compiler extensions allowed?

### 3) Chosen Approach
Use `offsetof(type, member)` pointer arithmetic.

### 4) Full C Code
```c
#include <stddef.h>

#define container_of(ptr, type, member) \
    ((type *)((char *)(ptr) - offsetof(type, member)))
```

### Quick Summary (How to come up with it + Why this works)
1. Need generic way to recover owner from embedded node pointer.
2. Use offset arithmetic via `offsetof`.
3. This works because member address and type layout determine parent base reliably.

### 5) Complexity
- O(1)

### 6) Core Invariants
1. `ptr` must point to `member` inside valid `type` object.
2. `member` offset must be compile-time known.

### 7) Alternative Implementations
1. Compiler builtins/wrapper macros.
2. Safer typed inline helper per struct.

### 8) Follow-up Questions + Strong Answers
1. Why important? enables generic intrusive data structures.
2. UB risk? invalid member pointer causes undefined behavior.
3. How to improve safety? static analysis + wrapper macros.

### 9) Interview Pitfalls
1. Wrong member name/struct type pairing.
2. Using with temporary or invalid pointers.

---

## Q121 — Correct memmove (overlap-safe) + optimized memcpy
### 1) Problem Statement
Implement production-correct `memmove` (overlap-safe) and baseline `memcpy`, then reason about alignment/performance follow-ups.

### 2) Clarifying Questions
1. Need strict standard-conforming behavior?
2. Word-copy optimization expected?
3. Alignment guarantees?

### 3) Chosen Approach
Direction-aware byte copy for memmove; straightforward memcpy baseline.

### 4) Full C Code
```c
#include <stddef.h>
#include <stdint.h>

void *my_memcpy(void *dst, const void *src, size_t n) {
    uint8_t *d = (uint8_t *)dst;
    const uint8_t *s = (const uint8_t *)src;
    for (size_t i = 0; i < n; i++) d[i] = s[i];
    return dst;
}

void *my_memmove(void *dst, const void *src, size_t n) {
    uint8_t *d = (uint8_t *)dst;
    const uint8_t *s = (const uint8_t *)src;
    if (d < s) {
        for (size_t i = 0; i < n; i++) d[i] = s[i];
    } else if (d > s) {
        for (size_t i = n; i > 0; i--) d[i - 1] = s[i - 1];
    }
    return dst;
}
```

### Quick Summary (How to come up with it + Why this works)
1. First decide overlap semantics before optimization.
2. Copy forward or backward based on pointer order.
3. This works because source bytes are preserved even when regions overlap.

### 5) Complexity
- O(n)

### 6) Core Invariants
1. memmove preserves source bytes with overlap.
2. memcpy assumes non-overlap.

### 7) Alternative Implementations
1. Word-sized copy fast paths.
2. SIMD optimized versions.

### 8) Follow-up Questions + Strong Answers
1. Why memcpy undefined on overlap? standard contract.
2. How optimize safely? align then copy machine words.
3. How test? random overlap fuzz matrix.

### 9) Interview Pitfalls
1. Wrong backward loop indices.
2. Assuming overlap-safe memcpy.

---

## Q122 — Framed packet parser (length, CRC, stream resync)
### 1) Problem Statement
Implement streaming packet parser FSM (SOF/LEN/PAYLOAD/CRC) that can resynchronize after corrupted bytes in a continuous input stream.

### 2) Clarifying Questions
1. Max frame size?
2. CRC polynomial?
3. Resync behavior on corruption?

### 3) Chosen Approach
Byte-wise finite-state machine with reset to SOF on error.

### 4) Full C Code
```c
#include <stdint.h>

typedef enum { ST_SOF, ST_LEN, ST_PAY, ST_CRC } PState;

typedef struct {
    PState st;
    uint8_t len;
    uint8_t idx;
    uint8_t crc;
    uint8_t payload[256];
} Parser;

int parser_feed(Parser *p, uint8_t b) {
    switch (p->st) {
        case ST_SOF:
            if (b == 0xAAu) { p->st = ST_LEN; p->crc = 0u; }
            break;
        case ST_LEN:
            p->len = b;
            p->idx = 0u;
            p->st = ST_PAY;
            break;
        case ST_PAY:
            p->payload[p->idx++] = b;
            p->crc ^= b;
            if (p->idx == p->len) p->st = ST_CRC;
            break;
        case ST_CRC:
            p->st = ST_SOF;
            return (p->crc == b) ? 1 : -1;
    }
    return 0;
}
```

### Quick Summary (How to come up with it + Why this works)
1. Convert stream protocol into finite parser states.
2. Validate LEN/CRC before frame acceptance and reset on error.
3. This works because parser progress is explicit and corruption recovery is bounded.

### 5) Complexity
- O(n) stream processing

### 6) Core Invariants
1. State transitions are explicit and bounded.
2. Parser returns to SOF after frame complete/error.

### 7) Alternative Implementations
1. Delimiter-based parser without length.
2. HDLC/COBS framing schemes.

### 8) Follow-up Questions + Strong Answers
1. How resync quickly? scan until next SOF.
2. How prevent oversized length abuse? enforce max LEN bounds.
3. CRC failure handling? drop frame + increment error counter.

### 9) Interview Pitfalls
1. No bounds check on payload index.
2. Parser stuck in bad state after error.

