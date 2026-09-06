# M006 — Ring buffers & SPSC queues (complete)

**Type:** Coding (C)  
**Merged from:** Q016, Q017, Q018, Q019, Q020, Q021  
**Companies:** Google · Apple · Amazon · Tesla · NVIDIA  
**Tier:** S (must-know)

**Question:** Byte ring with init/push/pop; spare-slot full/empty, pow2 mask, overwrite-oldest, ISR/task, lock-free SPSC, DMA contiguous read.

---

## Sub-variant coverage

| Original Q | Sub-variant |
|---|---|
| Q016 | Q016: spare-slot ring init/push/pop |
| Q017 | Q017: power-of-2 mask indexing |
| Q018 | Q018: overwrite-oldest policy |
| Q019 | Q019: ISR producer / task consumer + drops |
| Q020 | Q020: lock-free SPSC acquire/release |
| Q021 | Q021: DMA contiguous read API |

---

## Step 0 — Clarifying questions (say these out loud)

- **Candidate:** Capacity cap — usable bytes with one spare slot?
- **Candidate:** ISR producer / task consumer?
- **Candidate:** On full: reject, block, or overwrite oldest?
- **Candidate:** Need push_n/pop_n and DMA contiguous read API?

## Step 1 — Approach

Build Ring buffers & SPSC queues (complete) in layers: invariants first, happy path, then edge cases and concurrency.

- Restate API signatures and invariants aloud before coding.
- Choose spare-slot vs count field; define drop policy on full.
- Implement core logic with straightforward loops; optimize after tests pass.
- Document ownership, error codes, and ISR vs task context.

## Step 2 — Data structures / invariants

1. Structs/enums matching API — invariants in comments.
2. Platform hooks (`irq_save`, `now_ms`) isolated for host test fakes.

## Step 3 — Complete solution (compilable C)

```c
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>

/* --- Spare-slot SPSC ring (Q016) --- */
typedef struct {
    uint8_t *buf;
    uint32_t cap;
    uint32_t head;
    uint32_t tail;
    uint32_t drops;
} ring_t;

static inline uint32_t ring_next_mod(const ring_t *r, uint32_t idx) {
    return (idx + 1u) % r->cap;
}

static inline uint32_t ring_next_mask(const ring_t *r, uint32_t idx) {
    return (idx + 1u) & (r->cap - 1u);
}

static inline int ring_is_pow2(uint32_t cap) {
    return cap >= 2u && (cap & (cap - 1u)) == 0u;
}

static inline uint32_t ring_next(const ring_t *r, uint32_t idx) {
    return ring_is_pow2(r->cap) ? ring_next_mask(r, idx) : ring_next_mod(r, idx);
}

int ring_init(ring_t *r, uint8_t *buf, uint32_t cap) {
    if (!r || !buf || cap < 2u) {
        return -1;
    }
    r->buf = buf;
    r->cap = cap;
    r->head = 0u;
    r->tail = 0u;
    r->drops = 0u;
    return 0;
}

int ring_is_empty(const ring_t *r) {
    return r->head == r->tail;
}

int ring_is_full(const ring_t *r) {
    return ring_next(r, r->head) == r->tail;
}

uint32_t ring_count(const ring_t *r) {
    if (r->head >= r->tail) {
        return r->head - r->tail;
    }
    return r->cap - r->tail + r->head;
}

uint32_t ring_free_space(const ring_t *r) {
    return (r->cap - 1u) - ring_count(r);
}

int ring_push(ring_t *r, uint8_t byte) {
    uint32_t next = ring_next(r, r->head);
    if (next == r->tail) {
        r->drops++;
        return -1;
    }
    r->buf[r->head] = byte;
    r->head = next;
    return 0;
}

size_t ring_push_n(ring_t *r, const uint8_t *src, size_t n) {
    size_t pushed = 0;
    while (pushed < n && ring_push(r, src[pushed]) == 0) {
        pushed++;
    }
    return pushed;
}

int ring_pop(ring_t *r, uint8_t *byte) {
    if (r->head == r->tail) {
        return -1;
    }
    *byte = r->buf[r->tail];
    r->tail = ring_next(r, r->tail);
    return 0;
}

size_t ring_pop_n(ring_t *r, uint8_t *dst, size_t n) {
    size_t popped = 0;
    while (popped < n && ring_pop(r, &dst[popped]) == 0) {
        popped++;
    }
    return popped;
}

size_t ring_peek_n(const ring_t *r, uint8_t *dst, size_t n) {
    size_t i = 0;
    uint32_t t = r->tail;
    while (i < n && t != r->head) {
        dst[i++] = r->buf[t];
        t = ring_next(r, t);
    }
    return i;
}

/* Q018 — overwrite-oldest on full */
int ring_push_overwrite(ring_t *r, uint8_t byte) {
    uint32_t next = ring_next(r, r->head);
    if (next == r->tail) {
        r->tail = ring_next(r, r->tail);
        r->drops++;
    }
    r->buf[r->head] = byte;
    r->head = next;
    return 0;
}

/* Q021 — DMA-friendly contiguous read span */
size_t ring_contig_read(const ring_t *r, const uint8_t **ptr) {
    if (r->tail == r->head) {
        *ptr = NULL;
        return 0;
    }
    *ptr = &r->buf[r->tail];
    if (r->head > r->tail) {
        return r->head - r->tail;
    }
    return r->cap - r->tail;
}

void ring_consume(ring_t *r, size_t n) {
    while (n-- > 0 && r->tail != r->head) {
        r->tail = ring_next(r, r->tail);
    }
}

/* Q020 — SMP SPSC with acquire/release atomics */
typedef struct {
    uint8_t *buf;
    uint32_t cap;
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
} ring_atomic_t;

int ring_atomic_init(ring_atomic_t *r, uint8_t *buf, uint32_t cap) {
    if (!r || !buf || cap < 2u) {
        return -1;
    }
    r->buf = buf;
    r->cap = cap;
    atomic_store_explicit(&r->head, 0u, memory_order_relaxed);
    atomic_store_explicit(&r->tail, 0u, memory_order_relaxed);
    return 0;
}

int ring_atomic_push(ring_atomic_t *r, uint8_t byte) {
    uint32_t h = atomic_load_explicit(&r->head, memory_order_relaxed);
    uint32_t next = ring_is_pow2(r->cap) ? ((h + 1u) & (r->cap - 1u))
                                         : ((h + 1u) % r->cap);
    uint32_t t = atomic_load_explicit(&r->tail, memory_order_acquire);
    if (next == t) {
        return -1;
    }
    r->buf[h] = byte;
    atomic_store_explicit(&r->head, next, memory_order_release);
    return 0;
}

int ring_atomic_pop(ring_atomic_t *r, uint8_t *byte) {
    uint32_t t = atomic_load_explicit(&r->tail, memory_order_relaxed);
    uint32_t h = atomic_load_explicit(&r->head, memory_order_acquire);
    if (t == h) {
        return -1;
    }
    *byte = r->buf[t];
    uint32_t next = ring_is_pow2(r->cap) ? ((t + 1u) & (r->cap - 1u))
                                         : ((t + 1u) % r->cap);
    atomic_store_explicit(&r->tail, next, memory_order_release);
    return 0;
}
```

## Step 4 — Complexity

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) |

## Step 5 — Edge cases

1. NULL / zero-length — defined error or no-op.
2. Boundary at max capacity — no overrun.
3. Repeated calls idempotent where API requires.

## Step 6 — Concurrency / ISR / context notes

Label ISR-writable vs task-only fields. Keep ISR push O(1); defer parsing to task.

## Step 7 — Follow-up answers

**Q: Why spare slot?**  
**A:** Distinguish full vs empty with only head/tail — loses one byte of capacity.

**Q: Power-of-two size?**  
**A:** Enables mask indexing instead of modulo — faster on CPUs without fast divide.

**Q: Overwrite-oldest?**  
**A:** Advance tail then write — drops oldest telemetry; bad for command streams.

**Q: SMP variant?**  
**A:** Acquire/release on opposite index before checking occupancy.

**Q: DMA read?**  
**A:** Return pointer to contiguous span from tail to head or buffer end; wrap needs two segments.


## Step 8 — Tests

1. Happy path — minimal valid input produces expected output.
2. Zero/null/empty — defined error, no crash.
3. Boundary — max capacity or timeout edge.
4. Stress — back-to-back calls or burst traffic.

## Further study

- [Circular Ring Buffers](https://github.com/theEmbeddedGeorge/theEmbeddedNewTestament.github.io/blob/master/Data_Struct_Implementation/circularRingBuffer/README.md)
- [UART Protocol](https://github.com/theEmbeddedGeorge/theEmbeddedNewTestament.github.io/blob/master/Communication_Protocols/UART_Protocol.md)

---

*Generated by `tools/generate_merged_solutions.py` for M006.*