# Solutions — 05 Rings Queues Buffers

**Source:** [`../../coding_rounds/05_rings_queues_buffers.md`](../../coding_rounds/05_rings_queues_buffers.md)  
**Questions:** 20  

---

## C071 — SPSC byte ring buffer

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for SPSC byte ring buffer?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build SPSC byte ring buffer in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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

/* Spare-slot SPSC ring: usable capacity = cap - 1. Empty: head==tail. Full: next(head)==tail. */
typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;

static size_t ring_next(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}

void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf = buf;
    r->cap = cap;
    r->head = r->tail = 0;
}

size_t ring_count(const ring_t *r) {
    if (r->head >= r->tail) {
        return r->head - r->tail;
    }
    return r->cap - (r->tail - r->head);
}

static size_t ring_free(const ring_t *r) {
    return (r->cap - 1u) - ring_count(r);
}

size_t ring_push(ring_t *r, const uint8_t *src, size_t n) {
    size_t pushed = 0;
    while (pushed < n && ring_free(r) > 0) {
        r->buf[r->head] = src[pushed++];
        r->head = ring_next(r, r->head);
    }
    return pushed;
}

size_t ring_pop(ring_t *r, uint8_t *dst, size_t n) {
    size_t popped = 0;
    while (popped < n && r->tail != r->head) {
        dst[popped++] = r->buf[r->tail];
        r->tail = ring_next(r, r->tail);
    }
    return popped;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** ISR producer safety

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

**Q:** Power-of-two optimize

**A:** Power-of-two capacity enables `(idx+1) & (cap-1)` indexing without division; tradeoff is sizing up to the next pow2 (up to ~2× waste).

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C071
#include <assert.h>

int main(void) {
    /* TODO: wire to C071 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C072 — Power-of-two ring with mask

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Power-of-two ring with mask?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Power-of-two ring with mask in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *buf;
    size_t cap, head, tail;
}
ring_t;
static size_t rn(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}
void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf=buf;
    r->cap=cap;
    r->head=r->tail=0;
}
size_t ring_count(const ring_t *r) {
    return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head);
}
static int is_pow2(size_t x) {
    return x&&(x&(x-1))==0;
}
size_t ring_push(ring_t *r,const uint8_t *src,size_t n) {
    size_t m=r->cap-1;
    if(!is_pow2(r->cap))return 0;
    size_t pushed=0;
    while(pushed<n&&((r->head+1)&(r->cap-1))!=r->tail) {
        r->buf[r->head]=src[pushed++];
        r->head=(r->head+1)&(r->cap-1);
    }
    return pushed;
}
size_t ring_pop(ring_t *r,uint8_t *dst,size_t n) {
    size_t popped=0;
    while(popped<n&&r->tail!=r->head) {
        dst[popped++]=r->buf[r->tail];
        r->tail=(r->tail+1)&(r->cap-1);
    }
    return popped;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Capacity exhausted — return NULL/`-ENOMEM`/drop with stats.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Why force pow2?

**A:** Power-of-two capacity enables `(idx+1) & (cap-1)` indexing without division; tradeoff is sizing up to the next pow2 (up to ~2× waste).

**Q:** Memory waste?

**A:** For Power-of-two ring with mask: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C072
#include <assert.h>

int main(void) {
    /* TODO: wire to C072 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C073 — Count-field vs spare-slot ring

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Count-field vs spare-slot ring?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Count-field vs spare-slot ring in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *buf;
    size_t cap, head, tail;
}
ring_t;
static size_t rn(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}
void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf=buf;
    r->cap=cap;
    r->head=r->tail=0;
}
size_t ring_count(const ring_t *r) {
    return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head);
}
typedef struct {
    ring_t r;
    size_t count;
}
ring_count_t;
size_t rc_push(ring_count_t *rc,const uint8_t *s,size_t n) {
    size_t p=0;
    while(p<n&&rc->count<rc->r.cap) {
        rc->r.buf[rc->r.head]=s[p++];
        rc->r.head=rn(&rc->r,rc->r.head);
        rc->count++;
    }
    return p;
}
size_t rc_pop(ring_count_t *rc,uint8_t *d,size_t n) {
    size_t p=0;
    while(p<n&&rc->count) {
        d[p++]=rc->r.buf[rc->r.tail];
        rc->r.tail=rn(&rc->r,rc->r.tail);
        rc->count--;
    }
    return p;
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

**Q:** Which for ISR?

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

**Q:** Atomicity of count?

**A:** For Count-field vs spare-slot ring: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C073
#include <assert.h>

int main(void) {
    /* TODO: wire to C073 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C074 — Overwrite-oldest ring

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Overwrite-oldest ring?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Overwrite-oldest ring in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *buf;
    size_t cap, head, tail;
}
ring_t;
static size_t rn(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}
void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf=buf;
    r->cap=cap;
    r->head=r->tail=0;
}
size_t ring_count(const ring_t *r) {
    return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head);
}
size_t ring_push_overwrite(ring_t *r,const uint8_t *src,size_t n) {
    size_t pushed=0;
    while(pushed<n) {
        if(((r->head+1)%r->cap)==r->tail)r->tail=rn(r,r->tail);
        r->buf[r->head]=src[pushed++];
        r->head=rn(r,r->head);
    }
    return pushed;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Record-oriented overwrite

**A:** For Overwrite-oldest ring: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

**Q:** Notify reader of drops

**A:** For Overwrite-oldest ring: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C074
#include <assert.h>

int main(void) {
    /* TODO: wire to C074 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C075 — Discard-newest on full

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Discard-newest on full?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Discard-newest on full in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *buf;
    size_t cap, head, tail;
}
ring_t;
static size_t rn(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}
void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf=buf;
    r->cap=cap;
    r->head=r->tail=0;
}
size_t ring_count(const ring_t *r) {
    return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head);
}
size_t ring_push(ring_t *r,const uint8_t *src,size_t n) {
    size_t pushed=0;
    while(pushed<n&&((r->head+1)%r->cap)!=r->tail) {
        r->buf[r->head]=src[pushed++];
        r->head=rn(r,r->head);
    }
    return pushed;
}
static size_t drops;
size_t ring_push_drop_newest(ring_t *r,const uint8_t *src,size_t n) {
    size_t free=(r->cap-1)-ring_count(r);
    if(n>free) {
        drops+=n-free;
        n=free;
    }
    return ring_push(r,src,n);
}
size_t ring_drop_count(const ring_t *r) {
    (void)r;
    return drops;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.
3. Capacity exhausted — return NULL/`-ENOMEM`/drop with stats.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** When choose this vs overwrite?

**A:** For Discard-newest on full: state the invariant you protect, measure worst-case latency, then optimize — 'When choose this vs overwrite?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Backpressure signal

**A:** For Discard-newest on full: state the invariant you protect, measure worst-case latency, then optimize — 'Backpressure signal' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C075
#include <assert.h>

int main(void) {
    /* TODO: wire to C075 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C076 — Peek and skip

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Peek and skip?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Peek and skip in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *buf;
    size_t cap, head, tail;
}
ring_t;
static size_t rn(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}
void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf=buf;
    r->cap=cap;
    r->head=r->tail=0;
}
size_t ring_count(const ring_t *r) {
    return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head);
}
size_t ring_peek(const ring_t *r,uint8_t *dst,size_t n) {
    size_t i=0, t=r->tail;
    while(i<n&&t!=r->head) {
        dst[i++]=r->buf[t];
        t=rn(r,t);
    }
    return i;
}
size_t ring_skip(ring_t *r,size_t n) {
    size_t c=ring_count(r);
    if(n>c)n=c;
    while(n--)r->tail=rn(r,r->tail);
    return n;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Zero-copy peek pointer API

**A:** For Peek and skip: state the invariant you protect, measure worst-case latency, then optimize — 'Zero-copy peek pointer API' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Wrap issues

**A:** For Peek and skip: state the invariant you protect, measure worst-case latency, then optimize — 'Wrap issues' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C076
#include <assert.h>

int main(void) {
    /* TODO: wire to C076 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C077 — Contiguous read slice for DMA

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is the buffer cache-coherent, or do I need explicit flush/invalidate?
- **Candidate:** Single-shot or circular descriptor chain?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Contiguous read slice for DMA?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Contiguous read slice for DMA in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *buf;
    size_t cap, head, tail;
}
ring_t;
static size_t rn(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}
void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf=buf;
    r->cap=cap;
    r->head=r->tail=0;
}
size_t ring_count(const ring_t *r) {
    return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head);
}
size_t ring_contig_read(const ring_t *r,const uint8_t **ptr) {
    if(r->tail==r->head) {
        *ptr=0;
        return 0;
    }
    *ptr=&r->buf[r->tail];
    if(r->head>r->tail)return r->head-r->tail;
    return r->cap-r->tail;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Contiguous write space API

**A:** For Contiguous read slice for DMA: state the invariant you protect, measure worst-case latency, then optimize — 'Contiguous write space API' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** DMA half-complete

**A:** Cache-coherency: flush CPU writes before DMA TX; invalidate after DMA RX. Use `dma_alloc_coherent` on Linux or MPU non-cacheable regions on bare-metal.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C077
#include <assert.h>

int main(void) {
    /* TODO: wire to C077 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C078 — Reserve/commit write API

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Reserve/commit write API?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Reserve/commit write API in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *buf;
    size_t cap, head, tail;
}
ring_t;
static size_t rn(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}
void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf=buf;
    r->cap=cap;
    r->head=r->tail=0;
}
size_t ring_count(const ring_t *r) {
    return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head);
}
size_t ring_reserve(ring_t *r,uint8_t **ptr) {
    size_t f=(r->cap-1)-ring_count(r);
    if(!f) {
        *ptr=0;
        return 0;
    }
    *ptr=&r->buf[r->head];
    size_t contig=(r->head>=r->tail)?(r->cap-r->head):(r->tail-r->head-1);
    return contig<f?contig:f;
}
void ring_commit(ring_t *r,size_t n) {
    while(n--)r->head=rn(r,r->head);
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Abort reserve?

**A:** For Reserve/commit write API: state the invariant you protect, measure worst-case latency, then optimize — 'Abort reserve?' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Multi-reserve?

**A:** For Reserve/commit write API: state the invariant you protect, measure worst-case latency, then optimize — 'Multi-reserve?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C078
#include <assert.h>

int main(void) {
    /* TODO: wire to C078 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C079 — Typed element ring

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Typed element ring?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Typed element ring in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint32_t id;
    int32_t val;
}
event_t;
typedef struct {
    event_t *buf;
    size_t cap, head, tail;
}
event_ring_t;
int event_ring_push(event_ring_t *r,const event_t *e) {
    size_t n=(r->head+1)%r->cap;
    if(n==r->tail)return -1;
    r->buf[r->head]=*e;
    r->head=n;
    return 0;
}
int event_ring_pop(event_ring_t *r,event_t *e) {
    if(r->head==r->tail)return -1;
    *e=r->buf[r->tail];
    r->tail=(r->tail+1)%r->cap;
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
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Zero-copy slot API

**A:** For Typed element ring: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

**Q:** ISR push

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C079
#include <assert.h>

int main(void) {
    /* TODO: wire to C079 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C080 — MPSC queue with locking

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for MPSC queue with locking?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build MPSC queue with locking in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
#include <stdatomic.h>
typedef struct {
    uint32_t id;
    int32_t val;
}
event_t;
typedef struct {
    event_t buf[16];
    size_t cap;
    _Atomic size_t head, tail;
}
mpsc_t;
int mpsc_push(mpsc_t *q,const event_t *e) {
    size_t h=atomic_load(&q->head);
    size_t n=(h+1)%q->cap;
    if(n==atomic_load(&q->tail))return -1;
    q->buf[h]=*e;
    atomic_store(&q->head,n);
    return 0;
}
int mpsc_pop(mpsc_t *q,event_t *e) {
    size_t t=atomic_load(&q->tail);
    if(t==atomic_load(&q->head))return -1;
    *e=q->buf[t];
    atomic_store(&q->tail,(t+1)%q->cap);
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
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Lock-free MPSC hard—discuss

**A:** For MPSC queue with locking: state the invariant you protect, measure worst-case latency, then optimize — 'Lock-free MPSC hard—discuss' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Priority producers

**A:** Bitmap + CLZ finds highest ready priority in O(1) for ≤32 levels; separate ready lists per priority for O(1) insert.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C080
#include <assert.h>

int main(void) {
    /* TODO: wire to C080 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C081 — Priority event queues

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Priority event queues?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Priority event queues in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    event_t q[8][16];
    unsigned head[8], tail[8];
    uint32_t bitmap;
}
prio_q_t;
int prio_push(prio_q_t *q,unsigned prio,const event_t *e) {
    if(prio>7)return -1;
    unsigned t=(q->tail[prio]+1)%16;
    if(t==q->head[prio])return -1;
    q->q[prio][q->tail[prio]]=*e;
    q->tail[prio]=t;
    q->bitmap|=(1u<<prio);
    return 0;
}
int prio_pop_highest(prio_q_t *q,event_t *e) {
    for(int p=7;
    p>=0;
    --p)if(q->bitmap&(1u<<p)) {
        *e=q->q[p][q->head[p]];
        q->head[p]=(q->head[p]+1)%16;
        if(q->head[p]==q->tail[p])q->bitmap&=~(1u<<p);
        return 0;
    }
    return -1;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Starvation of low prio

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
#ifdef TEST_C081
#include <assert.h>

int main(void) {
    /* TODO: wire to C081 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C082 — Ping-pong double buffer

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Ping-pong double buffer?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Ping-pong double buffer in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
typedef struct { uint8_t buf[2][256]; int write_idx, read_idx, ready; } dbuf_t;
uint8_t *dbuf_write_begin(dbuf_t *d){return d->buf[d->write_idx];}
void dbuf_write_end(dbuf_t *d){d->ready=1;d->write_idx^=1;}
const uint8_t *dbuf_read_begin(dbuf_t *d){return d->ready?d->buf[d->read_idx]:0;}
void dbuf_read_end(dbuf_t *d){d->ready=0;d->read_idx^=1;}
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

**Q:** Triple buffering next

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

**Q:** DMA ownership

**A:** Cache-coherency: flush CPU writes before DMA TX; invalidate after DMA RX. Use `dma_alloc_coherent` on Linux or MPU non-cacheable regions on bare-metal.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C082
#include <assert.h>

int main(void) {
    /* TODO: wire to C082 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C083 — Triple buffering

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Triple buffering?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Triple buffering in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
typedef struct { uint8_t b[3][128]; int wi, ri, pending; } tbuf_t;
uint8_t *tbuf_acquire_write(tbuf_t *t){return t->b[t->wi];}
void tbuf_submit(tbuf_t *t){t->pending++;t->wi=(t->wi+1)%3;}
const uint8_t *tbuf_acquire_read(tbuf_t *t){if(!t->pending)return 0;return t->b[t->ri];}
void tbuf_release_read(tbuf_t *t){t->pending--;t->ri=(t->ri+1)%3;}
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

**Q:** Tearing prevention

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

**Q:** Latency vs double buffer

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C083
#include <assert.h>

int main(void) {
    /* TODO: wire to C083 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C084 — Length-prefixed messages in byte ring

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Length-prefixed messages in byte ring?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Length-prefixed messages in byte ring in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *buf;
    size_t cap, head, tail;
}
ring_t;
static size_t rn(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}
void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf=buf;
    r->cap=cap;
    r->head=r->tail=0;
}
size_t ring_count(const ring_t *r) {
    return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head);
}
size_t ring_push(ring_t *r,const uint8_t *src,size_t n) {
    size_t pushed=0;
    while(pushed<n&&((r->head+1)%r->cap)!=r->tail) {
        r->buf[r->head]=src[pushed++];
        r->head=rn(r,r->head);
    }
    return pushed;
}
size_t ring_pop(ring_t *r,uint8_t *dst,size_t n) {
    size_t popped=0;
    while(popped<n&&r->tail!=r->head) {
        dst[popped++]=r->buf[r->tail];
        r->tail=rn(r,r->tail);
    }
    return popped;
}
int msg_push(ring_t *r,const uint8_t *payload,uint16_t len) {
    if(len+2>(r->cap-1)-ring_count(r))return -1;
    uint8_t hdr[2]= {
        (uint8_t)(len>>8),(uint8_t)len
    };
    return (ring_push(r,hdr,2)+ring_push(r,payload,len)==(size_t)len+2)?0:-1;
}
int msg_pop(ring_t *r,uint8_t *payload,uint16_t cap,uint16_t *len_out) {
    uint8_t hdr[2];
    if(ring_pop(r,hdr,2)!=2)return -1;
    uint16_t len=(uint16_t)((hdr[0]<<8)|hdr[1]);
    if(len>cap||ring_count(r)<len)return -2;
    ring_pop(r,payload,len);
    *len_out=len;
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
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Zero-copy msg peek

**A:** For Length-prefixed messages in byte ring: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

**Q:** Corruption recovery

**A:** For Length-prefixed messages in byte ring: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C084
#include <assert.h>

int main(void) {
    /* TODO: wire to C084 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C085 — Zero-copy slot ring

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Zero-copy slot ring?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Zero-copy slot ring in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *slots;
    size_t slot_size, cap, wr, rd, count;
}
slot_ring_t;
uint8_t *slot_alloc(slot_ring_t *s) {
    if(s->count>=s->cap)return 0;
    return s->slots+((s->wr%s->cap)*s->slot_size);
}
void slot_submit(slot_ring_t *s) {
    s->wr++;
    s->count++;
}
const uint8_t *slot_acquire(slot_ring_t *s) {
    if(!s->count)return 0;
    return s->slots+((s->rd%s->cap)*s->slot_size);
}
void slot_release(slot_ring_t *s) {
    s->rd++;
    s->count--;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Cancel alloc?

**A:** For Zero-copy slot ring: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

**Q:** Multi-size slots

**A:** For Zero-copy slot ring: document SPSC vs MPSC topology, full/empty semantics, and whether ISR or task owns each index.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.
5. Fill exactly to full then push one — reject or drop per policy.

Optional harness:

```c
#ifdef TEST_C085
#include <assert.h>

int main(void) {
    /* TODO: wire to C085 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C086 — Watermark callbacks

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Watermark callbacks?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Watermark callbacks in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
typedef void (*wm_cb)(void *ctx, int high);
void ring_set_watermarks(ring_t *r, size_t low, size_t high, wm_cb cb, void *ctx);
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Hysteresis

**A:** For Watermark callbacks: state the invariant you protect, measure worst-case latency, then optimize — 'Hysteresis' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** Flow control link

**A:** For Watermark callbacks: state the invariant you protect, measure worst-case latency, then optimize — 'Flow control link' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C086
#include <assert.h>

int main(void) {
    /* TODO: wire to C086 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C087 — Lock-free SPSC with memory orders

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Lock-free SPSC with memory orders?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Lock-free SPSC with memory orders in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *buf;
    size_t cap, head, tail;
}
ring_t;
static size_t rn(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}
void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf=buf;
    r->cap=cap;
    r->head=r->tail=0;
}
size_t ring_count(const ring_t *r) {
    return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head);
}
size_t ring_push(ring_t *r,const uint8_t *src,size_t n) {
    size_t pushed=0;
    while(pushed<n&&((r->head+1)%r->cap)!=r->tail) {
        r->buf[r->head]=src[pushed++];
        r->head=rn(r,r->head);
    }
    return pushed;
}
size_t ring_pop(ring_t *r,uint8_t *dst,size_t n) {
    size_t popped=0;
    while(popped<n&&r->tail!=r->head) {
        dst[popped++]=r->buf[r->tail];
        r->tail=rn(r,r->tail);
    }
    return popped;
}
size_t ring_push_batch(ring_t *r,const uint8_t *src,size_t n) {
    return ring_push(r,src,n);
}
size_t ring_pop_batch(ring_t *r,uint8_t *dst,size_t n) {
    return ring_pop(r,dst,n);
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

**Q:** False sharing padding

**A:** Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics.

**Q:** MPSC?

**A:** For Lock-free SPSC with memory orders: state the invariant you protect, measure worst-case latency, then optimize — 'MPSC?' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C087
#include <assert.h>

int main(void) {
    /* TODO: wire to C087 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C088 — RTOS blocking queue

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for RTOS blocking queue?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build RTOS blocking queue in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *buf;
    size_t cap, rd, wr;
}
dma_ring_t;
size_t dma_ring_avail(const dma_ring_t *r) {
    return (r->wr+r->cap-r->rd)%r->cap;
}
const uint8_t *dma_ring_read_ptr(dma_ring_t *r,size_t *len) {
    *len=dma_ring_avail(r);
    return r->buf+r->rd;
}
```

### Step 4 — Complexity (table or bullets)

| Operation | Time | Space |
|---|---:|---:|
| push / pop | O(k) bytes moved | O(cap) buffer |
| init | O(1) | O(1) |

### Step 5 — Edge cases (numbered list)

1. NULL pointer arguments — return error code, never dereference.
2. Timeout expiry — return distinct error; leave hardware in bus-safe state.
3. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** ISR put variant

**A:** Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state.

**Q:** Priority inheritance

**A:** Bitmap + CLZ finds highest ready priority in O(1) for ≤32 levels; separate ready lists per priority for O(1) insert.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C088
#include <assert.h>

int main(void) {
    /* TODO: wire to C088 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C089 — Batch pop

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for Batch pop?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build Batch pop in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    int16_t samples[256];
    size_t head, tail, cap;
}
sample_ring_t;
int sample_push(sample_ring_t *r,int16_t v) {
    size_t n=(r->head+1)%r->cap;
    if(n==r->tail)return -1;
    r->samples[r->head]=v;
    r->head=n;
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
2. Push burst larger than free space — partial push or drop policy with counter.

### Step 6 — Concurrency / ISR / context notes (if applicable, else "N/A for this problem")

Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing.

### Step 7 — Follow-up answers (answer each follow-up from the question file)

**Q:** Batch push

**A:** For Batch pop: state the invariant you protect, measure worst-case latency, then optimize — 'Batch push' trades complexity vs determinism; pick based on N and IRQ rate.

**Q:** SIMD copy

**A:** For Batch pop: state the invariant you protect, measure worst-case latency, then optimize — 'SIMD copy' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C089
#include <assert.h>

int main(void) {
    /* TODO: wire to C089 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

## C090 — History / mirror debug buffer

### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)

- **Candidate:** Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?
- **Candidate:** Producer in ISR and consumer in task (SPSC), or different topology?
- **Candidate:** Should the solution target bare-metal, or is POSIX/Linux acceptable for History / mirror debug buffer?
- **Candidate:** Return codes, assertions, or silent drop with counters on error?

### Step 1 — Approach (short paragraph + bullet plan)

Build History / mirror debug buffer in layers: define invariants first, implement the happy path, then harden edge cases and concurrency.

- Restate API signatures and invariants aloud before writing code.
- Choose spare-slot vs count field for occupancy; never mix models.
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
    uint8_t *buf;
    size_t cap, head, tail;
}
ring_t;
static size_t rn(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}
void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf=buf;
    r->cap=cap;
    r->head=r->tail=0;
}
size_t ring_count(const ring_t *r) {
    return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head);
}
size_t ring_push(ring_t *r,const uint8_t *src,size_t n) {
    size_t pushed=0;
    while(pushed<n&&((r->head+1)%r->cap)!=r->tail) {
        r->buf[r->head]=src[pushed++];
        r->head=rn(r,r->head);
    }
    return pushed;
}
size_t ring_pop(ring_t *r,uint8_t *dst,size_t n) {
    size_t popped=0;
    while(popped<n&&r->tail!=r->head) {
        dst[popped++]=r->buf[r->tail];
        r->tail=rn(r,r->tail);
    }
    return popped;
}
int ring_self_test(void) {
    uint8_t mem[8];
    ring_t r;
    ring_init(&r,mem,8);
    ring_push(&r,(const uint8_t*)"ab",2);
    uint8_t out[2]= {
        0
    };
    ring_pop(&r,out,2);
    return out[0]=='a'&&out[1]=='b'?0:-1;
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

**Q:** Crash dump integration

**A:** Capture LR/PC/stack in fault handler; use `.noinit` ram console or post-mortem dump over UART.

**Q:** Binary vs text

**A:** For History / mirror debug buffer: state the invariant you protect, measure worst-case latency, then optimize — 'Binary vs text' trades complexity vs determinism; pick based on N and IRQ rate.

### Step 8 — Tests (test case list + optional small test code)

1. Happy path — minimal valid input produces expected output/state.
2. Zero/null/empty input — defined no-op or error code, no crash.
3. Boundary — max capacity, max timeout, wrap boundary minus one.
4. Stress — back-to-back calls, burst traffic, re-entrancy where applicable.

Optional harness:

```c
#ifdef TEST_C090
#include <assert.h>

int main(void) {
    /* TODO: wire to C090 APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}
#endif
```

---

