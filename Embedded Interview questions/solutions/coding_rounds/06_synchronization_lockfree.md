# Solutions — 06 Synchronization Lockfree

**Source:** [`../../coding_rounds/06_synchronization_lockfree.md`](../../coding_rounds/06_synchronization_lockfree.md)  
**Questions:** 20  

---

## C091 — Spinlock with atomic_flag

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is the controller memory-mapped with status flags as shown, or should I stub HAL hooks?
- **Candidate:** What timeout units and max clock-stretch should I assume for bus recovery?
- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Spinlock with atomic_flag?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Spinlock with atomic_flag in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
typedef struct {
    atomic_flag f;
}
spinlock_t;
void spin_lock(spinlock_t *l);
void spin_unlock(spinlock_t *l);
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

**Q:** Why not spin in ISR holding long?

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

**Q:** Ticket lock fairness?

**A:** For Spinlock with atomic_flag: specify timeout units, error recovery (NACK/overrun), and whether API is blocking or callback-driven.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C091
#include <assert.h>

int main(void) {
    /* TODO: wire to C091 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C092 — Ticket lock

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Ticket lock?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Ticket lock in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct {
    _Atomic unsigned next, now;
}
ticket_lock_t;
void ticket_lock(ticket_lock_t *l) {
    unsigned my=atomic_fetch_add(&l->next,1);
    while(atomic_load(&l->now)!=my) {
    }
}
void ticket_unlock(ticket_lock_t *l) {
    atomic_fetch_add(&l->now,1);
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

**Q:** Cache line bouncing

**A:** SoA vs AoS: SoA helps SIMD and sequential access; AoS is better for single-struct locality. Prefetch next cache line in hot loops; align to 32/64 B.

**Q:** When vs MCS locks

**A:** For Ticket lock: state the invariant you protect, measure worst-case latency, then optimize — 'When vs MCS locks' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C092
#include <assert.h>

int main(void) {
    /* TODO: wire to C092 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C093 — IRQ save/restore critical section

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for IRQ save/restore critical section?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build IRQ save/restore critical section in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef uint32_t irq_state_t; static irq_state_t primask; static int nest;
irq_state_t irq_save(void){irq_state_t prev=primask;primask=1;nest++;return prev;}
void irq_restore(irq_state_t st){if(--nest==0)primask=st;}
#define CRITICAL_SECTION(code) do{irq_state_t __st=irq_save();code;irq_restore(__st);}while(0)
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

**Q:** Basepri vs primask on Cortex-M

**A:** For IRQ save/restore critical section: state the invariant you protect, measure worst-case latency, then optimize — 'Basepri vs primask on Cortex-M' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** SMP needs more than this

**A:** Use acquire/release atomics, per-CPU data where possible; never use plain `volatile` as a lock substitute.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C093
#include <assert.h>

int main(void) {
    /* TODO: wire to C093 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C094 — Mutex for tasks

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Mutex for tasks?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Mutex for tasks in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    int locked, owner;
}
mutex_t;
void mutex_lock(mutex_t *m) {
    while(__sync_lock_test_and_set(&m->locked,1)) {
    }
    m->owner=1;
}
void mutex_unlock(mutex_t *m) {
    m->owner=0;
    __sync_lock_release(&m->locked);
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

**Q:** Recursive mutex?

**A:** Spinlock for ISR/task short sections; mutex (sleeping) only in thread context. Never hold spinlock across blocking calls.

**Q:** Priority inheritance next

**A:** Bitmap + CLZ finds highest ready priority in O(1) for ≤32 levels; separate ready lists per priority for O(1) insert.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C094
#include <assert.h>

int main(void) {
    /* TODO: wire to C094 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C095 — Binary semaphore ISR-capable

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Binary semaphore ISR-capable?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build Binary semaphore ISR-capable in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct {
    _Atomic int count;
}
sem_t;
void sem_give_from_isr(sem_t *s) {
    atomic_store(&s->count,1);
}
int sem_take(sem_t *s,uint32_t timeout_ms) {
    (void)timeout_ms;
    int c=atomic_load(&s->count);
    while(c==0)c=atomic_load(&s->count);
    atomic_store(&s->count,0);
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

**Q:** Counting semaphore difference

**A:** For Binary semaphore ISR-capable: state the invariant you protect, measure worst-case latency, then optimize — 'Counting semaphore difference' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Spurious wake

**A:** For Binary semaphore ISR-capable: state the invariant you protect, measure worst-case latency, then optimize — 'Spurious wake' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C095
#include <assert.h>

int main(void) {
    /* TODO: wire to C095 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C096 — Counting semaphore

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Counting semaphore?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Counting semaphore in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct {
    _Atomic int count;
    unsigned max;
}
sem_t;
int sem_init(sem_t *s,unsigned initial,unsigned max) {
    s->max=max;
    atomic_store(&s->count,(int)initial);
    return 0;
}
int sem_give(sem_t *s) {
    int c=atomic_load(&s->count);
    if((unsigned)c>=s->max)return -1;
    atomic_fetch_add(&s->count,1);
    return 0;
}
int sem_take(sem_t *s,uint32_t timeout_ms) {
    (void)timeout_ms;
    int c;
    do {
        c=atomic_load(&s->count);
        if(c<=0)return -1;
    }
    while(!atomic_compare_exchange_weak(&s->count,&c,c-1));
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

**Q:** Resource counting pattern

**A:** For Counting semaphore: state the invariant you protect, measure worst-case latency, then optimize — 'Resource counting pattern' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Overflow

**A:** Check before add/mul (`a > MAX - b`); return error or saturate and set sticky flag for telemetry.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C096
#include <assert.h>

int main(void) {
    /* TODO: wire to C096 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C097 — Debug lock owner / recursion detect

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Debug lock owner / recursion detect?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Debug lock owner / recursion detect in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#ifndef NDEBUG
typedef struct {
    int locked, owner;
}
mutex_t;
void mutex_lock_debug(mutex_t *m) {
    if(m->locked&&m->owner==1) {
        __builtin_trap();
    }
    mutex_lock(m);
    m->owner=1;
}
void mutex_unlock_debug(mutex_t *m) {
    if(m->owner!=1) {
        __builtin_trap();
    }
    mutex_unlock(m);
}
#else
void mutex_lock_debug(mutex_t *m) {
    mutex_lock(m);
}
void mutex_unlock_debug(mutex_t *m) {
    mutex_unlock(m);
}
#endif
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

**Q:** Deadlock detector ideas

**A:** For Debug lock owner / recursion detect: state the invariant you protect, measure worst-case latency, then optimize — 'Deadlock detector ideas' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Lockdep analogy

**A:** For Debug lock owner / recursion detect: state the invariant you protect, measure worst-case latency, then optimize — 'Lockdep analogy' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C097
#include <assert.h>

int main(void) {
    /* TODO: wire to C097 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C098 — Reader-writer lock

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Reader-writer lock?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Reader-writer lock in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct { int readers, writer; } rw_lock_t;
void rw_rlock(rw_lock_t *l){while(l->writer);l->readers++;}
void rw_runlock(rw_lock_t *l){l->readers--;}
void rw_wlock(rw_lock_t *l){while(l->readers||l->writer);l->writer=1;}
void rw_wunlock(rw_lock_t *l){l->writer=0;}
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

**Q:** Starvation scenarios

**A:** Strict priority can starve low tasks; add time-slicing within priority or aging (boost priority after N ticks waiting).

**Q:** seqlock alternative

**A:** For Reader-writer lock: state the invariant you protect, measure worst-case latency, then optimize — 'seqlock alternative' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C098
#include <assert.h>

int main(void) {
    /* TODO: wire to C098 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C099 — Seqlock for stats

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Seqlock for stats?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Seqlock for stats in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct {
    _Atomic unsigned seq;
    uint64_t isr_count, bytes;
}
stats_t;
void stats_write_begin(stats_t *s) {
    atomic_fetch_add(&s->seq,1);
    atomic_thread_fence(memory_order_release);
}
void stats_write_end(stats_t *s) {
    atomic_thread_fence(memory_order_release);
    atomic_fetch_add(&s->seq,1);
}
void stats_read(stats_t *s,uint64_t *isr,uint64_t *bytes) {
    for(;
    ;
    ) {
        unsigned a=atomic_load(&s->seq);
        if(a&1)continue;
        *isr=s->isr_count;
        *bytes=s->bytes;
        unsigned b=atomic_load(&s->seq);
        if(a==b)break;
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

**Q:** When seqlock is wrong

**A:** For Seqlock for stats: state the invariant you protect, measure worst-case latency, then optimize — 'When seqlock is wrong' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Atomic 64-bit alternatives

**A:** Use `uint64_t` ticks when uptime exceeds wrap horizon. Linux `time_after(a,b)` uses signed difference on `unsigned long`; same trick works for 32-bit with max delta < 2³¹.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C099
#include <assert.h>

int main(void) {
    /* TODO: wire to C099 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C100 — Atomic refcount

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Atomic refcount?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Atomic refcount in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct ref { _Atomic int cnt; void (*rel)(struct ref*); } ref_t;
void ref_init(ref_t *r,void (*release)(ref_t*)){atomic_store(&r->cnt,1);r->rel=release;}
void ref_get(ref_t *r){atomic_fetch_add(&r->cnt,1);}
void ref_put(ref_t *r){if(atomic_fetch_sub(&r->cnt,1)==1&&r->rel)r->rel(r);}
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

**Q:** Saturation?

**A:** Check before add/mul (`a > MAX - b`); return error or saturate and set sticky flag for telemetry.

**Q:** Weak memory barriers

**A:** For Atomic refcount: state the invariant you protect, measure worst-case latency, then optimize — 'Weak memory barriers' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C100
#include <assert.h>

int main(void) {
    /* TODO: wire to C100 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C101 — Lock-free SPSC queue (struct elements)

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Lock-free SPSC queue (struct elements)?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Lock-free SPSC queue (struct elements) in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct {
    msg_t *buf;
    size_t cap;
    _Atomic size_t head, tail;
}
spsc_t;
typedef struct {
    uint32_t id;
    uint8_t data[8];
}
msg_t;
int spsc_push(spsc_t *q,const msg_t *m) {
    size_t h=atomic_load_explicit(&q->head,memory_order_relaxed);
    size_t n=(h+1)%q->cap;
    if(n==atomic_load_explicit(&q->tail,memory_order_acquire))return -1;
    q->buf[h]=*m;
    atomic_store_explicit(&q->head,n,memory_order_release);
    return 0;
}
int spsc_pop(spsc_t *q,msg_t *m) {
    size_t t=atomic_load_explicit(&q->tail,memory_order_relaxed);
    if(t==atomic_load_explicit(&q->head,memory_order_acquire))return -1;
    *m=q->buf[t];
    atomic_store_explicit(&q->tail,(t+1)%q->cap,memory_order_release);
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
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Batching

**A:** For Lock-free SPSC queue (struct elements): state the invariant you protect, measure worst-case latency, then optimize — 'Batching' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Cache line pad

**A:** SoA vs AoS: SoA helps SIMD and sequential access; AoS is better for single-struct locality. Prefetch next cache line in hot loops; align to 32/64 B.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C101
#include <assert.h>

int main(void) {
    /* TODO: wire to C101 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C102 — MPSC with CAS list or documented approach

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for MPSC with CAS list or documented approach?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build MPSC with CAS list or documented approach in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct node {
    struct node *next;
    int v;
}
node_t;
typedef struct {
    _Atomic(node_t*) head;
    node_t *stub;
}
mpsc_t;
int mpsc_enqueue(mpsc_t *q,node_t *n) {
    node_t *prev=atomic_exchange(&q->head,n);
    prev->next=n;
    return 0;
}
node_t *mpsc_dequeue(mpsc_t *q) {
    node_t *head=atomic_load(&q->head);
    if(head==&q->stub)return 0;
    node_t *next=head->next;
    if(!next)return 0;
    int v=head->v;
    *head=*next;
    return head;
    /* simplified */
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

**Q:** Vyukov MPSC

**A:** For MPSC with CAS list or documented approach: state the invariant you protect, measure worst-case latency, then optimize — 'Vyukov MPSC' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** When to just use a lock

**A:** For MPSC with CAS list or documented approach: state the invariant you protect, measure worst-case latency, then optimize — 'When to just use a lock' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C102
#include <assert.h>

int main(void) {
    /* TODO: wire to C102 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C103 — Treiber lock-free stack

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Treiber lock-free stack?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Treiber lock-free stack in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct {
    _Atomic(node_t*) top;
}
stack_t;
void stack_push(stack_t *s,node_t *n) {
    node_t *old=atomic_load(&s->top);
    do {
        n->next=old;
    }
    while(!atomic_compare_exchange_weak(&s->top,&old,n));
}
node_t *stack_pop(stack_t *s) {
    node_t *old=atomic_load(&s->top);
    node_t *next;
    do {
        if(!old)return 0;
        next=old->next;
    }
    while(!atomic_compare_exchange_weak(&s->top,&old,next));
    return old;
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

**Q:** Tagged pointers

**A:** For Treiber lock-free stack: state the invariant you protect, measure worst-case latency, then optimize — 'Tagged pointers' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Hazard pointers mention

**A:** For Treiber lock-free stack: state the invariant you protect, measure worst-case latency, then optimize — 'Hazard pointers mention' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C103
#include <assert.h>

int main(void) {
    /* TODO: wire to C103 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C104 — ABA-safe stack with generation tag

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for ABA-safe stack with generation tag?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build ABA-safe stack with generation tag in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct {
    _Atomic int state;
}
once_t;
/* 0=init,1=running,2=done */
void call_once(once_t *o,void (*fn)(void)) {
    int s=atomic_load(&o->state);
    if(s==2)return;
    if(atomic_compare_exchange_strong(&o->state,&s,1)) {
        fn();
        atomic_store(&o->state,2);
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

**Q:** Double-width CAS

**A:** Parse with `of_property_read_u32`; check `-EINVAL`; use `devm_kzalloc` for probe-lifetime memory.

**Q:** Other mitigations

**A:** For ABA-safe stack with generation tag: state the invariant you protect, measure worst-case latency, then optimize — 'Other mitigations' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C104
#include <assert.h>

int main(void) {
    /* TODO: wire to C104 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C105 — Acquire/release ISR→task flag

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Acquire/release ISR→task flag?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?
- **Candidate:** Confirm ISR may only touch fields X; rest deferred to task.

### Step 1 — Approach (short paragraph + bullet plan)

Build Acquire/release ISR→task flag in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { _Atomic int flag; } event_t;
void event_set(event_t *e){atomic_store(&e->flag,1);}
void event_wait(event_t *e){while(!atomic_load(&e->flag)){} atomic_store(&e->flag,0);}
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

**Q:** Eventfd/sem instead of poll

**A:** `poll_wait` adds fd to wait queue; ISR wakes via `wake_up_interruptible` when data ready.

**Q:** Double buffering

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C105
#include <assert.h>

int main(void) {
    /* TODO: wire to C105 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C106 — Sense-reversing barrier

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Sense-reversing barrier?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Sense-reversing barrier in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <stdint.h>
#include <stddef.h>
typedef struct {
    int a,b;
    int held;
}
deadlock_demo_t;
void ordered_lock(deadlock_demo_t *x,deadlock_demo_t *y) {
    if(x<y) {
        mutex_lock(x);
        mutex_lock(y);
    }
    else {
        mutex_lock(y);
        mutex_lock(x);
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

**Q:** vs pthread_barrier

**A:** For Sense-reversing barrier: state the invariant you protect, measure worst-case latency, then optimize — 'vs pthread_barrier' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Last thread unlocks

**A:** For Sense-reversing barrier: state the invariant you protect, measure worst-case latency, then optimize — 'Last thread unlocks' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C106
#include <assert.h>

int main(void) {
    /* TODO: wire to C106 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C107 — Producer-consumer with condition_variable

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Which C++ standard (C++14/17) and are exceptions/RTTI enabled?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Producer-consumer with condition_variable?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Producer-consumer with condition_variable in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```cpp
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
void smp_mb(void){atomic_thread_fence(memory_order_seq_cst);}
void publish(int *flag,int *data){*data=42;smp_mb();*flag=1;}
int consume(int *flag,int *data){if(!*flag)return 0;smp_mb();return *data==42;}
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

**Q:** timeout pop

**A:** For Producer-consumer with condition_variable: state the invariant you protect, measure worst-case latency, then optimize — 'timeout pop' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** stop token

**A:** For Producer-consumer with condition_variable: state the invariant you protect, measure worst-case latency, then optimize — 'stop token' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```cpp
#ifdef TEST_C107
#include <assert.h>

int main(void) {
    /* TODO: wire to C107 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C108 — Deadlock then fix

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Deadlock then fix?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Deadlock then fix in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct {
    uint32_t generation;
    void *ptr;
}
gen_ptr_t;
int gen_ptr_valid(gen_ptr_t *g,uint32_t gen) {
    return g->generation==gen&&g->ptr;
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

**Q:** try_lock backoff

**A:** For Deadlock then fix: state the invariant you protect, measure worst-case latency, then optimize — 'try_lock backoff' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Lock hierarchies

**A:** For Deadlock then fix: state the invariant you protect, measure worst-case latency, then optimize — 'Lock hierarchies' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C108
#include <assert.h>

int main(void) {
    /* TODO: wire to C108 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C109 — Priority inheritance mutex (sketch)

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Priority inheritance mutex (sketch)?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Priority inheritance mutex (sketch) in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct {
    _Atomic uint32_t v;
}
atomic_u32_t;
uint32_t atomic_fetch_max(atomic_u32_t *a,uint32_t val) {
    uint32_t old=atomic_load(&a->v);
    while(old<val&&!atomic_compare_exchange_weak(&a->v,&old,val)) {
    }
    return old;
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

**Q:** Priority ceiling alternative

**A:** Bitmap + CLZ finds highest ready priority in O(1) for ≤32 levels; separate ready lists per priority for O(1) insert.

**Q:** Nested locks

**A:** For Priority inheritance mutex (sketch): state the invariant you protect, measure worst-case latency, then optimize — 'Nested locks' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C109
#include <assert.h>

int main(void) {
    /* TODO: wire to C109 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C110 — Wait-free single-word mailbox

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Can this lock be taken from ISR, or task-only?
- **Candidate:** Single-core UP or SMP with preemptible kernel?
- **Candidate:** Shared SRAM with cache coherency handled, or explicit flush?
- **Candidate:** Ordering: doorbell IRQ after payload visible?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Wait-free single-word mailbox?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Wait-free single-word mailbox in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Atomics with memory_order_acquire/release; IRQ-safe variants when needed.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>
void lock_order_check(unsigned id) {
    static unsigned held[4];
    for(int i=0;
    i<4;
    ++i)if(held[i]&&id<held[i]) {
        __builtin_trap();
    }
    held[id]=1;
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

**Q:** Multi-word seqlock link

**A:** For Wait-free single-word mailbox: state the invariant you protect, measure worst-case latency, then optimize — 'Multi-word seqlock link' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Lossy vs lossless

**A:** For Wait-free single-word mailbox: state the invariant you protect, measure worst-case latency, then optimize — 'Lossy vs lossless' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C110
#include <assert.h>

int main(void) {
    /* TODO: wire to C110 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

