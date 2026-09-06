# Solutions — 07 Interrupts Deferred Work

**Source:** [`../../coding_rounds/07_interrupts_deferred_work.md`](../../coding_rounds/07_interrupts_deferred_work.md)  
**Questions:** 10  

---

## C111 — Minimal ISR + queue

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Minimal ISR + queue?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build Minimal ISR + queue in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
    uint8_t q[64];
    volatile uint16_t h,t;
}
isr_q_t;
void isr_push(isr_q_t *q,uint8_t b) {
    uint16_t n=(q->h+1)%64;
    if(n!=q->t) {
        q->q[q->h]=b;
        q->h=n;
    }
}
void isr_drain(isr_q_t *q) {
    while(q->t!=q->h) {
        handle(q->q[q->t]);
        q->t=(q->t+1)%64;
    }
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

**Q:** What if queue full?

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

**Q:** Nested interrupts

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C111
#include <assert.h>

int main(void) {
    /* TODO: wire to C111 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C112 — Top-half / bottom-half

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Top-half / bottom-half?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Top-half / bottom-half in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
volatile int top_flag;
void top_isr(void) {
    top_flag=1;
}
void bottom_half(void) {
    if(top_flag) {
        top_flag=0;
        process();
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

**Q:** Linux softirq/tasklet analogy

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

**Q:** Latency budget

**A:** For Top-half / bottom-half: state the invariant you protect, measure worst-case latency, then optimize — 'Latency budget' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C112
#include <assert.h>

int main(void) {
    /* TODO: wire to C112 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C113 — Threaded IRQ pattern

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Threaded IRQ pattern?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build Threaded IRQ pattern in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
    void (*fn)(void*);
    void *ctx;
}
work_t;
static work_t pending;
void schedule_work(work_t w) {
    pending=w;
}
void run_work(void) {
    if(pending.fn)pending.fn(pending.ctx);
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

**Q:** vs softirq

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

**Q:** Priority inversion with locks

**A:** Bitmap + CLZ finds highest ready priority in O(1) for ≤32 levels; separate ready lists per priority for O(1) insert.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C113
#include <assert.h>

int main(void) {
    /* TODO: wire to C113 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C114 — IRQ-safe reference count

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for IRQ-safe reference count?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build IRQ-safe reference count in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
volatile int dsr_pending;
void dsr_request(void) {
    dsr_pending=1;
}
void dsr_run(void) {
    while(dsr_pending) {
        dsr_pending=0;
        handle();
    }
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

**Q:** Deferred free

**A:** For IRQ-safe reference count: state the invariant you protect, measure worst-case latency, then optimize — 'Deferred free' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** RCU mention

**A:** For IRQ-safe reference count: state the invariant you protect, measure worst-case latency, then optimize — 'RCU mention' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C114
#include <assert.h>

int main(void) {
    /* TODO: wire to C114 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C115 — GPIO debounce in ISR/timer

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for GPIO debounce in ISR/timer?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build GPIO debounce in ISR/timer in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Absolute expiry timestamps; wrap-safe compare via signed delta (`time_after`).

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    int en;
}
irq_line_t;
void irq_enable(irq_line_t *l) {
    l->en=1;
}
void irq_disable(irq_line_t *l) {
    l->en=0;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Timestamp counter wrap — use signed delta compare; document max interval < 2³¹ ticks.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Both edges

**A:** For GPIO debounce in ISR/timer: state the invariant you protect, measure worst-case latency, then optimize — 'Both edges' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Long press later

**A:** For GPIO debounce in ISR/timer: state the invariant you protect, measure worst-case latency, then optimize — 'Long press later' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Two timers — earlier fires first; cancel head reprograms HW.

Optional harness:

```c
#ifdef TEST_C115
#include <assert.h>

int main(void) {
    /* TODO: wire to C115 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C116 — IRQ coalescing counter

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for IRQ coalescing counter?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build IRQ coalescing counter in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
static int nest;
void nested_enter(void) {
    nest++;
}
void nested_leave(void) {
    if(nest)nest--;
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

**Q:** NAPI analogy

**A:** For IRQ coalescing counter: state the invariant you protect, measure worst-case latency, then optimize — 'NAPI analogy' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Rate limiting

**A:** For IRQ coalescing counter: state the invariant you protect, measure worst-case latency, then optimize — 'Rate limiting' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C116
#include <assert.h>

int main(void) {
    /* TODO: wire to C116 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C117 — IRQ storm rate limit

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for IRQ storm rate limit?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build IRQ storm rate limit in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
    uint32_t pending;
}
irq_ctrl_t;
void irq_set_pending(irq_ctrl_t *c,unsigned b) {
    c->pending|=(1u<<b);
}
void irq_clear(irq_ctrl_t *c,unsigned b) {
    c->pending&=~(1u<<b);
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

**Q:** Root cause debugging

**A:** For IRQ storm rate limit: state the invariant you protect, measure worst-case latency, then optimize — 'Root cause debugging' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Hardware FIFO overrun link

**A:** Read and clear error flags in ISR; count in stats; optionally flush RX FIFO on overrun.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C117
#include <assert.h>

int main(void) {
    /* TODO: wire to C117 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C118 — One-shot work item

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for One-shot work item?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build One-shot work item in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
void defer_to_thread(volatile int *flag) {
    *flag=1;
}
void thread_poll(volatile int *flag) {
    if(*flag) {
        *flag=0;
        handle();
    }
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

**Q:** Cancel work

**A:** For One-shot work item: state the invariant you protect, measure worst-case latency, then optimize — 'Cancel work' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Periodic work

**A:** Reschedule with `next += period` from an absolute anchor to avoid drift. If late, either catch up (burst fires) or skip missed beats and log `miss_count`.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C118
#include <assert.h>

int main(void) {
    /* TODO: wire to C118 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C119 — ISR latency histogram

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for ISR latency histogram?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build ISR latency histogram in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
    uint32_t count;
}
isr_stats_t;
void isr_count(isr_stats_t *s) {
    s->count++;
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

**Q:** Max latency watermark

**A:** For ISR latency histogram: state the invariant you protect, measure worst-case latency, then optimize — 'Max latency watermark' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Tracing

**A:** For ISR latency histogram: state the invariant you protect, measure worst-case latency, then optimize — 'Tracing' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C119
#include <assert.h>

int main(void) {
    /* TODO: wire to C119 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C120 — Correct wakeup: flag vs queue race

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Correct wakeup: flag vs queue race?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build Correct wakeup: flag vs queue race in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

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
int irq_affinity_set(unsigned cpu) {
    return cpu<4?0:-1;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** POSIX condvar analogy

**A:** For Correct wakeup: flag vs queue race: state the invariant you protect, measure worst-case latency, then optimize — 'POSIX condvar analogy' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Semaphore solution

**A:** For Correct wakeup: flag vs queue race: state the invariant you protect, measure worst-case latency, then optimize — 'Semaphore solution' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C120
#include <assert.h>

int main(void) {
    /* TODO: wire to C120 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

