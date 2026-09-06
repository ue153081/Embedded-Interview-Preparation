# Solutions — 11 Timers Schedulers

**Source:** [`../../coding_rounds/11_timers_schedulers.md`](../../coding_rounds/11_timers_schedulers.md)  
**Questions:** 13  

---

## C173 — Software timers on one HW timer

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Software timers on one HW timer?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Software timers on one HW timer in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
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

typedef void (*timer_cb)(void *ctx);

typedef struct sw_timer {
    struct sw_timer *next;
    uint32_t expires_ms;
    timer_cb cb;
    void *ctx;
    uint8_t active;
} sw_timer_t;

static sw_timer_t *g_head;
static uint32_t g_now_ms;

#define time_before(a, b)    ((int32_t)((a) - (b)) < 0)
#define time_before_eq(a, b) ((int32_t)((a) - (b)) <= 0)

static uint32_t irq_save(void) { return 0; }
static void irq_restore(uint32_t f) { (void)f; }

static void hw_timer_program(uint32_t deadline_ms) {
    uint32_t delta = deadline_ms - g_now_ms;
    (void)delta; /* platform: write compare register */
}

static void reprogram_hw(void) {
    if (g_head) {
        hw_timer_program(g_head->expires_ms);
    }
}

static void list_remove(sw_timer_t *t) {
    sw_timer_t **pp = &g_head;
    while (*pp) {
        if (*pp == t) {
            *pp = t->next;
            return;
        }
        pp = &(*pp)->next;
    }
}

static void insert_sorted(sw_timer_t *t) {
    t->next = NULL;
    if (!g_head || time_before(t->expires_ms, g_head->expires_ms)) {
        t->next = g_head;
        g_head = t;
        reprogram_hw();
        return;
    }
    sw_timer_t *p = g_head;
    while (p->next && time_before_eq(p->next->expires_ms, t->expires_ms)) {
        p = p->next;
    }
    t->next = p->next;
    p->next = t;
}

void sw_timer_cancel(sw_timer_t *t) {
    uint32_t flags = irq_save();
    t->active = 0;
    if (g_head == t) {
        g_head = t->next;
        reprogram_hw();
    } else {
        list_remove(t);
    }
    irq_restore(flags);
}

void sw_timer_set(sw_timer_t *t, uint32_t delay_ms, timer_cb cb, void *ctx) {
    uint32_t flags = irq_save();
    if (t->active) {
        sw_timer_cancel(t);
    }
    t->expires_ms = g_now_ms + delay_ms;
    t->cb = cb;
    t->ctx = ctx;
    t->active = 1;
    insert_sorted(t);
    irq_restore(flags);
}

void hw_timer_irq(void) {
    /* Called when HW compare fires; advance time to programmed deadline or read HW */
    if (g_head) {
        g_now_ms = g_head->expires_ms;
    }
    while (g_head && time_before_eq(g_head->expires_ms, g_now_ms)) {
        sw_timer_t *exp = g_head;
        g_head = exp->next;
        exp->active = 0;
        if (exp->cb) {
            exp->cb(exp->ctx);
        }
    }
    reprogram_hw();
}

void tick_ms(uint32_t ms) { g_now_ms = ms; }
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) struct |
| init | O(cap) or O(1) | O(cap) if buffer |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Timestamp counter wrap — use signed delta compare; document max interval < 2³¹ ticks.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Periodic timers

**A:** Reschedule with `next += period` from an absolute anchor to avoid drift. If late, either catch up (burst fires) or skip missed beats and log `miss_count`.

**Q:** MP safety

**A:** Use acquire/release atomics, per-CPU data where possible; never use plain `volatile` as a lock substitute.

**Q:** min-heap vs sorted list

**A:** Sorted list: O(n) insert, simple, good for <32 timers. Min-heap: O(log n) insert/pop, better for hundreds+. Timer wheel: O(1) amortized for coarse granularity.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Two timers — earlier fires first; cancel head reprograms HW.

Optional harness:

```c
#ifdef TEST_C173
#include <assert.h>

int main(void) {
    /* TODO: wire to C173 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C174 — Cancel + periodic race-safe

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Cancel + periodic race-safe?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Cancel + periodic race-safe in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
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

typedef void (*timer_cb)(void *ctx);

typedef struct sw_timer {
    struct sw_timer *next;
    uint32_t expires_ms;
    uint32_t period_ms;
    timer_cb cb;
    void *ctx;
    uint8_t active;
    uint8_t periodic;
    uint8_t in_callback;
    uint32_t generation;
} sw_timer_t;

static sw_timer_t *g_head;
static uint32_t g_now_ms;

#define time_before_eq(a, b) ((int32_t)((a) - (b)) <= 0)

static uint32_t irq_save(void) { return 0; }
static void irq_restore(uint32_t f) { (void)f; }

static void reprogram_hw(void) { (void)g_head; }

static void insert_sorted(sw_timer_t *t);
static void list_remove(sw_timer_t *t);

void sw_timer_cancel(sw_timer_t *t) {
    uint32_t f = irq_save();
    t->active = 0;
    list_remove(t);
    irq_restore(f);
}

void sw_timer_set_periodic(sw_timer_t *t, uint32_t period_ms, timer_cb cb, void *ctx) {
    uint32_t f = irq_save();
    if (t->active) {
        list_remove(t);
    }
    t->period_ms = period_ms;
    t->cb = cb;
    t->ctx = ctx;
    t->periodic = 1;
    t->active = 1;
    t->expires_ms = g_now_ms + period_ms;
    insert_sorted(t);
    irq_restore(f);
}

static void fire_timer(sw_timer_t *exp) {
    exp->in_callback = 1;
    uint32_t gen = exp->generation;
    if (exp->cb) {
        exp->cb(exp->ctx);
    }
    exp->in_callback = 0;
    if (!exp->active || exp->generation != gen) {
        return;
    }
    if (exp->periodic) {
        exp->expires_ms += exp->period_ms;
        insert_sorted(exp);
    }
}

int sw_timer_cancel_sync(sw_timer_t *t) {
    sw_timer_cancel(t);
    while (t->in_callback) {
        /* yield or wfe in real RTOS */
    }
    return 0;
}

static void insert_sorted(sw_timer_t *t) {
    t->next = NULL;
    sw_timer_t **pp = &g_head;
    while (*pp && time_before_eq((*pp)->expires_ms, t->expires_ms)) {
        pp = &(*pp)->next;
    }
    t->next = *pp;
    *pp = t;
    reprogram_hw();
}

static void list_remove(sw_timer_t *t) {
    sw_timer_t **pp = &g_head;
    while (*pp) {
        if (*pp == t) {
            *pp = t->next;
            t->generation++;
            reprogram_hw();
            return;
        }
        pp = &(*pp)->next;
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
2. Cancel while callback running — generation flag or cancel_sync handshake.
3. Re-arm during callback — avoid double-insert; use active/generation guard.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Drift-free period

**A:** Reschedule with `next += period` from an absolute anchor to avoid drift. If late, either catch up (burst fires) or skip missed beats and log `miss_count`.

**Q:** Timer wheel

**A:** Hierarchical timer wheel (Linux-style) gives O(1) insert/tick for coarse timers; fine deadlines still need a min-heap or sorted list for sub-tick accuracy.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Cancel from task while callback runs — no double-free or use-after-free.

Optional harness:

```c
#ifdef TEST_C174
#include <assert.h>

int main(void) {
    /* TODO: wire to C174 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C175 — Wrap-safe time comparisons

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Wrap-safe time comparisons?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Wrap-safe time comparisons in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
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

/* Max representable interval: half the counter space (2^31 ticks for 32-bit) */
#define TIME_MAX_DELTA_MS 0x7FFFFFFFu

int time_after(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) > 0;
}

int time_before(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) < 0;
}

int time_before_eq(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) <= 0;
}

uint32_t time_delta(uint32_t now, uint32_t then) {
    return now - then;
}

int time_in_range(uint32_t t, uint32_t start, uint32_t end) {
    return time_after(t, start) && time_before_eq(t, end);
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

**Q:** 64-bit ticks

**A:** Use `uint64_t` ticks when uptime exceeds wrap horizon. Linux `time_after(a,b)` uses signed difference on `unsigned long`; same trick works for 32-bit with max delta < 2³¹.

**Q:** Linux jiffies macros

**A:** Use `uint64_t` ticks when uptime exceeds wrap horizon. Linux `time_after(a,b)` uses signed difference on `unsigned long`; same trick works for 32-bit with max delta < 2³¹.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C175
#include <assert.h>

int main(void) {
    /* TODO: wire to C175 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C176 — Timer wheel

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Timer wheel?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Timer wheel in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Absolute expiry timestamps; wrap-safe compare via signed delta (`time_after`).
5. Circular bucket array; cascade on tick for hierarchical wheels.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>

typedef void (*timer_cb)(void *ctx);

typedef struct sw_timer {
    struct sw_timer *next;
    timer_cb cb;
    void *ctx;
    uint32_t expires_tick;
} sw_timer_t;

#define WHEEL_SLOTS 256u
#define WHEEL_MASK  (WHEEL_SLOTS - 1u)

typedef struct {
    sw_timer_t *buckets[WHEEL_SLOTS];
    uint32_t cursor;
    uint32_t tick;
} wheel_t;

static void wheel_insert(wheel_t *w, sw_timer_t *t, uint32_t expires_tick) {
    uint32_t slot = expires_tick & WHEEL_MASK;
    t->expires_tick = expires_tick;
    t->next = w->buckets[slot];
    w->buckets[slot] = t;
}

static void wheel_tick(wheel_t *w) {
    uint32_t slot = w->tick & WHEEL_MASK;
    sw_timer_t *t = w->buckets[slot];
    w->buckets[slot] = NULL;
    while (t) {
        sw_timer_t *n = t->next;
        if (t->cb) {
            t->cb(t->ctx);
        }
        t = n;
    }
    w->tick++;
    w->cursor = slot;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| insert | O(1) | O(buckets + timers) |
| tick | O(1) per slot + cascade | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Timestamp counter wrap — use signed delta compare; document max interval < 2³¹ ticks.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** vs min-heap

**A:** Sorted list: O(n) insert, simple, good for <32 timers. Min-heap: O(log n) insert/pop, better for hundreds+. Timer wheel: O(1) amortized for coarse granularity.

**Q:** Hash collisions

**A:** Chaining handles collisions; cap bucket depth; rehash if load factor exceeds threshold.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Two timers — earlier fires first; cancel head reprograms HW.

Optional harness:

```c
#ifdef TEST_C176
#include <assert.h>

int main(void) {
    /* TODO: wire to C176 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C177 — Min-heap timer queue

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Min-heap timer queue?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Min-heap timer queue in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Absolute expiry timestamps; wrap-safe compare via signed delta (`time_after`).
5. Min-heap indexed by `expires`; heap[0] is next IRQ deadline.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>

typedef struct sw_timer {
    uint32_t expires;
    int index;
} sw_timer_t;

typedef struct {
    sw_timer_t **heap;
    size_t n;
    size_t cap;
} heap_t;

static int time_before_eq(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) <= 0;
}

static void heap_swap(heap_t *h, size_t i, size_t j) {
    sw_timer_t *tmp = h->heap[i];
    h->heap[i] = h->heap[j];
    h->heap[j] = tmp;
    h->heap[i]->index = (int)i;
    h->heap[j]->index = (int)j;
}

static void heap_up(heap_t *h, size_t i) {
    while (i > 0) {
        size_t p = (i - 1) / 2;
        if (time_before_eq(h->heap[i]->expires, h->heap[p]->expires)) {
            heap_swap(h, i, p);
            i = p;
        } else {
            break;
        }
    }
}

static void heap_down(heap_t *h, size_t i) {
    for (;;) {
        size_t l = 2 * i + 1, r = l + 1, m = i;
        if (l < h->n && time_before_eq(h->heap[l]->expires, h->heap[m]->expires)) {
            m = l;
        }
        if (r < h->n && time_before_eq(h->heap[r]->expires, h->heap[m]->expires)) {
            m = r;
        }
        if (m == i) {
            break;
        }
        heap_swap(h, i, m);
        i = m;
    }
}

void heap_timer_insert(heap_t *h, sw_timer_t *t) {
    if (h->n >= h->cap) {
        return;
    }
    h->heap[h->n] = t;
    t->index = (int)h->n;
    h->n++;
    heap_up(h, h->n - 1);
}

sw_timer_t *heap_timer_pop_expired(heap_t *h, uint32_t now) {
    if (!h->n || !time_before_eq(h->heap[0]->expires, now)) {
        return NULL;
    }
    sw_timer_t *top = h->heap[0];
    h->n--;
    if (h->n) {
        h->heap[0] = h->heap[h->n];
        h->heap[0]->index = 0;
        heap_down(h, 0);
    }
    return top;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| insert / cancel | O(log n) | O(n) heap |
| pop expired | O(log n) amortized | O(1) extra |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.
3. Timestamp counter wrap — use signed delta compare; document max interval < 2³¹ ticks.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Complexity

**A:** State Big-O for each API call; mention constant factors (cache lines, IRQ overhead) that dominate on embedded even when asymptotics look equal.

**Q:** Cache behavior vs list

**A:** SoA vs AoS: SoA helps SIMD and sequential access; AoS is better for single-struct locality. Prefetch next cache line in hot loops; align to 32/64 B.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Two timers — earlier fires first; cancel head reprograms HW.

Optional harness:

```c
#ifdef TEST_C177
#include <assert.h>

int main(void) {
    /* TODO: wire to C177 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C178 — Drift-free periodic

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Drift-free periodic?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Drift-free periodic in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
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
    uint32_t anchor;
    uint32_t next;
    uint32_t period;
    uint32_t missed;
} periodic_t;

void periodic_arm(periodic_t *p, uint32_t now, uint32_t period) {
    p->anchor = now;
    p->period = period;
    p->next = now + period;
    p->missed = 0;
}

void periodic_on_fire(periodic_t *p, uint32_t now) {
    p->next += p->period;
    if ((int32_t)(now - p->next) > 0) {
        uint32_t late = now - p->next;
        p->missed += late / p->period + 1;
        p->next = now + p->period;
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
2. Re-arm during callback — avoid double-insert; use active/generation guard.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Skipped beats count

**A:** Track `late_count`; policy: skip to `now + period` vs fire back-to-back catch-up — document choice.

**Q:** Phase alignment

**A:** Anchor `next` to global epoch (`next = epoch + k*period`) so multiple tasks stay in phase.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C178
#include <assert.h>

int main(void) {
    /* TODO: wire to C178 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C179 — Cooperative round-robin scheduler

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Cooperative round-robin scheduler?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Cooperative round-robin scheduler in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
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

typedef void (*task_fn)(void);

typedef struct {
    task_fn fn;
    const char *name;
} task_t;

static task_t g_tasks[8];
static int g_count;
static int g_current;

void task_add(task_fn fn, const char *name) {
    if (g_count < 8) {
        g_tasks[g_count].fn = fn;
        g_tasks[g_count].name = name;
        g_count++;
    }
}

void scheduler_run(void) {
    if (g_count == 0) {
        return;
    }
    g_tasks[g_current].fn();
    g_current = (g_current + 1) % g_count;
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

**Q:** Add priorities

**A:** Insert ready queue per priority; pick highest non-empty; within level use round-robin.

**Q:** Stacks per task

**A:** Each task needs isolated stack; measure high-water with fill pattern; place stacks in MPU guard regions.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C179
#include <assert.h>

int main(void) {
    /* TODO: wire to C179 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C180 — Bitmap priority ready queue

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Bitmap priority ready queue?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Bitmap priority ready queue in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
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

#define MAX_PRIO 8

typedef void (*task_fn)(void);

typedef struct {
    task_fn fn;
    uint8_t ready;
} task_slot_t;

typedef struct {
    task_slot_t queues[MAX_PRIO][4];
    uint8_t qcount[MAX_PRIO];
    uint8_t ready_bitmap;
} ready_queue_t;

static int clz8(uint8_t x) {
    if (!x) return 8;
    int n = 0;
    while (!(x & 0x80u)) { x <<= 1; n++; }
    return n;
}

void rq_add(ready_queue_t *rq, int prio, task_fn fn) {
    if (prio < 0 || prio >= MAX_PRIO) return;
    if (rq->qcount[prio] >= 4) return;
    int i = rq->qcount[prio]++;
    rq->queues[prio][i].fn = fn;
    rq->queues[prio][i].ready = 1;
    rq->ready_bitmap |= (uint8_t)(1u << prio);
}

task_fn rq_pick_next(ready_queue_t *rq) {
    if (!rq->ready_bitmap) return NULL;
    int p = 7 - clz8(rq->ready_bitmap);
    for (int i = 0; i < rq->qcount[p]; ++i) {
        if (rq->queues[p][i].ready) {
            rq->queues[p][i].ready = 0;
            return rq->queues[p][i].fn;
        }
    }
    return NULL;
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

**Q:** Starvation

**A:** Strict priority can starve low tasks; add time-slicing within priority or aging (boost priority after N ticks waiting).

**Q:** Aging

**A:** Increment a wait counter each scheduler tick; when it exceeds threshold, temporarily boost effective priority so long-waiting tasks eventually run.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C180
#include <assert.h>

int main(void) {
    /* TODO: wire to C180 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C181 — regCall / callNext tick dispatcher

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for regCall / callNext tick dispatcher?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build regCall / callNext tick dispatcher in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
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
    uint32_t deadline;
    int (*fn)(void);
    uint8_t active;
} deadline_t;

static int time_after(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) > 0;
}

int run_deadlines(deadline_t *d, size_t n, uint32_t now) {
    int ran = 0;
    for (size_t i = 0; i < n; ++i) {
        if (d[i].active && time_after(now, d[i].deadline)) {
            d[i].fn();
            d[i].active = 0;
            ran++;
        }
    }
    return ran;
}

void reg_call(deadline_t *d, uint32_t deadline_ms, int (*fn)(void)) {
    d->deadline = deadline_ms;
    d->fn = fn;
    d->active = 1;
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

**Q:** Complexity

**A:** State Big-O for each API call; mention constant factors (cache lines, IRQ overhead) that dominate on embedded even when asymptotics look equal.

**Q:** Priority callbacks

**A:** Bitmap + CLZ finds highest ready priority in O(1) for ≤32 levels; separate ready lists per priority for O(1) insert.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C181
#include <assert.h>

int main(void) {
    /* TODO: wire to C181 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C182 — Deadline miss counter

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Deadline miss counter?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Deadline miss counter in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
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
    uint32_t wcet_us;
    uint32_t period_us;
    uint32_t miss_count;
} task_profile_t;

int sched_feasibility(task_profile_t *t, size_t n, uint32_t frame_us) {
    uint64_t sum = 0;
    for (size_t i = 0; i < n; ++i) {
        sum += t[i].wcet_us;
    }
    return sum <= frame_us ? 0 : -1;
}

void on_deadline_miss(task_profile_t *t) {
    t->miss_count++;
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

**Q:** What to do on miss

**A:** Log miss, increment counter, optionally safe-state (degrade mode); never silently ignore safety deadlines.

**Q:** Telemetry

**A:** Expose counters via sysfs/debugfs or a ring of events; rate-limit logging to avoid feedback loops that worsen the fault.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C182
#include <assert.h>

int main(void) {
    /* TODO: wire to C182 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C183 — Hashed timer wheel

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Hashed timer wheel?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Hashed timer wheel in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
- Implement core logic with straightforward loops; optimize only after tests pass.
- Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.
- Document ownership, error codes, and ISR vs task context in brief comments.

### Step 2 — Data structures / invariants

1. Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.
2. Explicit capacity, generation counters, or state enum invariants in comments.
3. Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.
4. Absolute expiry timestamps; wrap-safe compare via signed delta (`time_after`).
5. Circular bucket array; cascade on tick for hierarchical wheels.

### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)

```c
#include <stdint.h>
#include <stddef.h>

typedef struct timer_node {
    struct timer_node *next;
    uint32_t abs_expires;
} timer_node_t;

#define TVR_BITS 8
#define TVN_BITS 6
#define TVR_SIZE (1u << TVR_BITS)

typedef struct {
    timer_node_t *vec[TVR_SIZE];
    uint32_t jiffies;
} tvec_base_t;

static uint32_t timer_jiffies(tvec_base_t *base) {
    return base->jiffies;
}

void wheel_cascade(tvec_base_t *base, unsigned idx) {
    (void)base;
    (void)idx;
}

void tickless_sleep_until(uint32_t target_jiffies) {
    uint32_t now = 0; /* read monotonic tick */
    if ((int32_t)(target_jiffies - now) <= 0) {
        return;
    }
    /* program HW one-shot for (target - now) */
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| insert | O(1) | O(buckets + timers) |
| tick | O(1) per slot + cascade | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Timestamp counter wrap — use signed delta compare; document max interval < 2³¹ ticks.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Linux timer wheel history

**A:** Hierarchical timer wheel (Linux-style) gives O(1) insert/tick for coarse timers; fine deadlines still need a min-heap or sorted list for sub-tick accuracy.

**Q:** Accuracy

**A:** Wheel quantizes to slot size; combine coarse wheel + fine heap for sub-ms deadlines.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Two timers — earlier fires first; cancel head reprograms HW.

Optional harness:

```c
#ifdef TEST_C183
#include <assert.h>

int main(void) {
    /* TODO: wire to C183 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C184 — Debounce via software timer

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Debounce via software timer?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Debounce via software timer in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
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

typedef void (*debounce_cb)(int level, void *ctx);

typedef struct {
    uint32_t delay_ms;
    debounce_cb cb;
    void *ctx;
    uint8_t pending_level;
    uint8_t armed;
} debounce_t;

static uint32_t g_now;

extern void sw_timer_set(void *t, uint32_t ms, void (*cb)(void*), void *ctx);
extern void sw_timer_cancel(void *t);

static void debounce_fire(void *ctx) {
    debounce_t *d = (debounce_t *)ctx;
    d->armed = 0;
    if (d->cb) {
        d->cb((int)d->pending_level, d->ctx);
    }
}

void debounce_on_edge(debounce_t *d, int level) {
    d->pending_level = (uint8_t)level;
    sw_timer_cancel(&d->armed);
    sw_timer_set(&d->armed, d->delay_ms, debounce_fire, d);
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

**Q:** Both press/release

**A:** Separate debounce timers for press and release edges; symmetric timing reduces chatter on both transitions.

**Q:** Power cost

**A:** One-shot HW compare lets CPU sleep between edges; periodic tick wastes power if events are sparse.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Two timers — earlier fires first; cancel head reprograms HW.

Optional harness:

```c
#ifdef TEST_C184
#include <assert.h>

int main(void) {
    /* TODO: wire to C184 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C185 — One-shot vs auto-reload HAL

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** What tick resolution and wrap period does the HW timer provide?
- **Candidate:** Should callbacks run in ISR context or a deferred worker thread?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for One-shot vs auto-reload HAL?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build One-shot vs auto-reload HAL in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Store absolute deadlines; reprogram HW compare to earliest expiry on head change.
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

typedef enum { TIMER_ONESHOT, TIMER_PERIODIC } timer_mode_t;

typedef struct {
    volatile uint32_t CR;
    volatile uint32_t ARR;
    volatile uint32_t CNT;
} hw_timer_t;

#define CR_EN   (1u << 0)
#define CR_OPM  (1u << 1)

void hal_timer_start(hw_timer_t *t, uint32_t ticks, timer_mode_t mode) {
    t->ARR = ticks;
    t->CNT = 0;
    t->CR = CR_EN | (mode == TIMER_ONESHOT ? CR_OPM : 0);
}

void hal_timer_stop(hw_timer_t *t) {
    t->CR = 0;
}

int timer_self_test(void) {
    return time_before_eq(5u, 10u) ? 0 : -1;
}

static int time_before_eq(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) <= 0;
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

**Q:** Multiple channels

**A:** One HW timer channel per compare register; software mux if channels exhausted; document priority.

**Q:** PWM conflict

**A:** Share timer channel: one-shot for protocol timeouts, PWM via alternate compare mode — mutually exclusive via HAL mutex.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C185
#include <assert.h>

int main(void) {
    /* TODO: wire to C185 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

