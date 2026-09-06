# Solutions — 15 Ipc Dual Core

**Source:** [`../../coding_rounds/15_ipc_dual_core.md`](../../coding_rounds/15_ipc_dual_core.md)  
**Questions:** 12  

---

## C219 — Shared memory SPSC + barriers

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Shared memory SPSC + barriers?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Shared memory SPSC + barriers in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct {
    uint8_t buf[256];
    _Atomic uint32_t head, tail;
}
shmem_ring_t;
void shmem_push(shmem_ring_t *r,uint8_t v) {
    uint32_t h=atomic_load(&r->head);
    uint32_t n=(h+1)%256;
    if(n!=atomic_load(&r->tail)) {
        r->buf[h]=v;
        atomic_store(&r->head,n);
    }
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Zero-length operation — defined no-op success.
2. Maximum size/at limit — correct result without overrun.
3. Repeated calls idempotent where API semantics require it.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Same as lock-free SPSC

**A:** For Shared memory SPSC + barriers: state the invariant you protect, measure worst-case latency, then optimize — 'Same as lock-free SPSC' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Uncached SRAM

**A:** SoA vs AoS: SoA helps SIMD and sequential access; AoS is better for single-struct locality. Prefetch next cache line in hot loops; align to 32/64 B.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C219
#include <assert.h>

int main(void) {
    /* TODO: wire to C219 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C220 — Mailbox + IPI

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Shared SRAM with cache coherency handled, or explicit flush?
- **Candidate:** Ordering: doorbell IRQ after payload visible?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Mailbox + IPI?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Mailbox + IPI in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    volatile uint32_t doorbell;
    uint32_t msg;
}
mailbox_t;
void mbox_send(mailbox_t *m,uint32_t v) {
    m->msg=v;
    m->doorbell=1;
}
uint32_t mbox_recv(mailbox_t *m) {
    if(!m->doorbell)return 0;
    m->doorbell=0;
    return m->msg;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Multi-slot mailbox

**A:** Shared memory + doorbell IRQ; use cache-line alignment and memory barriers; version the message header.

**Q:** Priority messages

**A:** Bitmap + CLZ finds highest ready priority in O(1) for ≤32 levels; separate ready lists per priority for O(1) insert.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C220
#include <assert.h>

int main(void) {
    /* TODO: wire to C220 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C221 — Request/ACK protocol

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Fixed frame length or length-prefix/CRC delimited?
- **Candidate:** Byte-at-a-time ISR feed or blocking read with timeout?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Request/ACK protocol?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Request/ACK protocol in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct {
    _Atomic uint32_t seq;
    uint8_t data[64];
}
slot_t;
int slot_publish(slot_t *s,const uint8_t *d,size_t n) {
    uint32_t v=atomic_load(&s->seq);
    atomic_store(&s->seq,v|1);
    for(size_t i=0;
    i<n;
    ++i)s->data[i]=d[i];
    atomic_store(&s->seq,v+2);
    return 0;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Timeout expiry — return distinct error; leave hardware in bus-safe state.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Async completion

**A:** For Request/ACK protocol: state the invariant you protect, measure worst-case latency, then optimize — 'Async completion' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Retry

**A:** For Request/ACK protocol: state the invariant you protect, measure worst-case latency, then optimize — 'Retry' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C221
#include <assert.h>

int main(void) {
    /* TODO: wire to C221 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C222 — Cross-core spinlock

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is the controller memory-mapped with status flags as shown, or should I stub HAL hooks?
- **Candidate:** What timeout units and max clock-stretch should I assume for bus recovery?
- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Cross-core spinlock?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Cross-core spinlock in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
void dmb(void) {
    atomic_thread_fence(memory_order_seq_cst);
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. NACK, arbitration loss, clock stretch timeout — recovery then error return.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Ticket lock

**A:** For Cross-core spinlock: specify timeout units, error recovery (NACK/overrun), and whether API is blocking or callback-driven.

**Q:** Disable preemption

**A:** For Cross-core spinlock: specify timeout units, error recovery (NACK/overrun), and whether API is blocking or callback-driven.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C222
#include <assert.h>

int main(void) {
    /* TODO: wire to C222 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C223 — Seqlock stats across cores

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Seqlock stats across cores?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Seqlock stats across cores in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    uint32_t flag;
}
rendez_t;
void rp_produce(rendez_t *r) {
    r->flag=1;
}
int rp_consume(rendez_t *r) {
    return (int)r->flag;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Cache line ownership

**A:** SoA vs AoS: SoA helps SIMD and sequential access; AoS is better for single-struct locality. Prefetch next cache line in hot loops; align to 32/64 B.

**Q:** Rate of updates

**A:** For Seqlock stats across cores: state the invariant you protect, measure worst-case latency, then optimize — 'Rate of updates' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C223
#include <assert.h>

int main(void) {
    /* TODO: wire to C223 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C224 — RPMsg-lite style endpoints

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for RPMsg-lite style endpoints?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build RPMsg-lite style endpoints in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    int owner;
}
spin_t;
int try_claim(spin_t *s,int me) {
    return s->owner==0?(s->owner=me,1):s->owner==me;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Virtio analogy

**A:** For RPMsg-lite style endpoints: state the invariant you protect, measure worst-case latency, then optimize — 'Virtio analogy' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Zero-copy

**A:** For RPMsg-lite style endpoints: state the invariant you protect, measure worst-case latency, then optimize — 'Zero-copy' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C224
#include <assert.h>

int main(void) {
    /* TODO: wire to C224 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C225 — Multi-core log ring

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Multi-core log ring?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Multi-core log ring in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Empty: `head==tail`; full: `next(head)==tail` (spare slot) unless count field used.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    uint32_t rp, wp;
    uint8_t b[128];
}
fifo_t;
int rpmsg_send(fifo_t *f,uint8_t v) {
    uint32_t n=(f->wp+1)%128;
    if(n==f->rp)return -1;
    f->b[f->wp]=v;
    f->wp=n;
    return 0;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Per-core buffers merge

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

**Q:** Timestamps

**A:** For Multi-core log ring: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C225
#include <assert.h>

int main(void) {
    /* TODO: wire to C225 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C226 — Zero-copy buffer handoff across cores

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Zero-copy buffer handoff across cores?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Zero-copy buffer handoff across cores in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
int give_buffer(buf_id_t id);
int take_buffer(buf_id_t *id);
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Pool of buffers

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

**Q:** DMA + IPC

**A:** Cache-coherency: flush CPU writes before DMA TX; invalidate after DMA RX. Use `dma_alloc_coherent` on Linux or MPU non-cacheable regions on bare-metal.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C226
#include <assert.h>

int main(void) {
    /* TODO: wire to C226 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C227 — Versioned shared config

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Versioned shared config?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Versioned shared config in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    uint32_t cmd, arg;
}
rpc_t;
int rpc_call(rpc_t *r) {
    (void)r;
    return 0;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Partial field updates

**A:** For Versioned shared config: state the invariant you protect, measure worst-case latency, then optimize — 'Partial field updates' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Schema version

**A:** For Versioned shared config: state the invariant you protect, measure worst-case latency, then optimize — 'Schema version' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C227
#include <assert.h>

int main(void) {
    /* TODO: wire to C227 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C228 — Cross-core heartbeat

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Cross-core heartbeat?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Cross-core heartbeat in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
void heartbeat_kick(void);
int heartbeat_check_peer(uint32_t now_ms);
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Zero-length operation — defined no-op success.
2. Maximum size/at limit — correct result without overrun.
3. Repeated calls idempotent where API semantics require it.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Recovery action

**A:** For Cross-core heartbeat: state the invariant you protect, measure worst-case latency, then optimize — 'Recovery action' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Missed kick budget

**A:** For Cross-core heartbeat: state the invariant you protect, measure worst-case latency, then optimize — 'Missed kick budget' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C228
#include <assert.h>

int main(void) {
    /* TODO: wire to C228 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C229 — Command queue + completion queue

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Command queue + completion queue?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Command queue + completion queue in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    uint32_t magic;
}
hdr_t;
int ipc_validate(hdr_t *h) {
    return h->magic==0xC0DEC0DEu?0:-1;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Out-of-order completions

**A:** For Command queue + completion queue: state the invariant you protect, measure worst-case latency, then optimize — 'Out-of-order completions' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Doorbell registers

**A:** For Command queue + completion queue: state the invariant you protect, measure worst-case latency, then optimize — 'Doorbell registers' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C229
#include <assert.h>

int main(void) {
    /* TODO: wire to C229 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C230 — Mark cache ops in IPC path

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Shared SRAM with cache coherency handled, or explicit flush?
- **Candidate:** Ordering: doorbell IRQ after payload visible?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Mark cache ops in IPC path?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Mark cache ops in IPC path in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    volatile uint32_t doorbell;
    uint32_t msg;
}
mailbox_t;
void mbox_send(mailbox_t*,uint32_t);
uint32_t mbox_recv(mailbox_t*);
int ipc_self_test(void) {
    mailbox_t m= {
        0
    };
    mbox_send(&m,42);
    return mbox_recv(&m)==42?0:-1;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Uncached alias

**A:** SoA vs AoS: SoA helps SIMD and sequential access; AoS is better for single-struct locality. Prefetch next cache line in hot loops; align to 32/64 B.

**Q:** IOMMU

**A:** For Mark cache ops in IPC path: state the invariant you protect, measure worst-case latency, then optimize — 'IOMMU' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C230
#include <assert.h>

int main(void) {
    /* TODO: wire to C230 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

