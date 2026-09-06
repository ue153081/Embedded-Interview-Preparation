# Q016 — SPSC Circular Buffer (byte) — init / push / pop / full / empty

**Type:** Coding (C)  
**Companies:** Google · Apple · Amazon · Tesla · NVIDIA  
**Tier:** S (must-know)

**Question (from FINAL 120):** Implement a single-producer single-consumer circular buffer (byte-oriented) with `init`, `push`, `pop`; define full/empty semantics clearly.

---

## Step 0 — Clarifying questions (say these out loud)

- **Candidate:** Is capacity `cap` the number of **usable** bytes, or total buffer size? I'll use **one spare slot**: usable = `cap - 1`.
- **Candidate:** Who is producer and who is consumer — **ISR produces / task consumes**, or both in task context?
- **Candidate:** On full push, should I **return an error**, block, or **drop**? I'll return `-ENOSPC` (or `-1`) unless you want overwrite policy.
- **Candidate:** Do you want **single-byte** API only, or also `push_n` / `pop_n` for bursts?
- **Candidate:** Single-core UP only, or should I mention **memory ordering** for SMP?

*Interviewer usually says:* ISR producer, task consumer, reject on full, byte API is fine.

---

## Step 1 — Approach

Use a **classic array ring** with indices `head` (next write) and `tail` (next read).

- **Empty:** `head == tail`
- **Full:** `(head + 1) % cap == tail` (one slot always wasted — avoids ambiguous full/empty)
- **Producer** updates only `head`; **consumer** updates only `tail` → safe on single-core without locks when roles are strict SPSC.
- If producer can be ISR: keep push **O(1)**, no malloc, no blocking; consumer runs in task.

**Plan:**
1. Define `ring_t` + invariants in comments.
2. Implement `ring_init`, `ring_push`, `ring_pop`, helpers `ring_count`, `ring_free_space`.
3. Add `ring_push_n` / `ring_pop_n` for realistic UART/DMA use.
4. State concurrency rules and optional IRQ-save wrapper for shared stats.

---

## Step 2 — Data structures / invariants

```c
typedef struct {
    uint8_t  *buf;   /* backing store, length cap */
    uint32_t  cap;   /* physical size >= 2 */
    uint32_t  head;  /* producer write index — only producer touches */
    uint32_t  tail;  /* consumer read index  — only consumer touches */
} ring_t;
```

**Invariants (spare-slot model):**
- `0 <= head, tail < cap`
- Empty: `head == tail`
- Full: `ring_next(head) == tail`
- Count: `head >= tail ? head - tail : cap - tail + head`
- Free space: `cap - 1 - count`

---

## Step 3 — Complete solution (compilable C)

```c
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint8_t *buf;
    uint32_t cap;
    uint32_t head;
    uint32_t tail;
} ring_t;

static inline uint32_t ring_next(const ring_t *r, uint32_t idx) {
    return (idx + 1u) % r->cap;
}

int ring_init(ring_t *r, uint8_t *buf, uint32_t cap) {
    if (!r || !buf || cap < 2u) {
        return -1;
    }
    r->buf  = buf;
    r->cap  = cap;
    r->head = 0u;
    r->tail = 0u;
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

/* Producer API — call from ISR or sole producer task */
int ring_push(ring_t *r, uint8_t byte) {
    uint32_t next = ring_next(r, r->head);
    if (next == r->tail) {
        return -1; /* full */
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

/* Consumer API — call from sole consumer task */
int ring_pop(ring_t *r, uint8_t *byte) {
    if (r->head == r->tail) {
        return -1; /* empty */
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

/* Optional: peek without consuming (consumer only) */
size_t ring_peek_n(const ring_t *r, uint8_t *dst, size_t n) {
    size_t i = 0;
    uint32_t t = r->tail;
    while (i < n && t != r->head) {
        dst[i++] = r->buf[t];
        t = ring_next(r, t);
    }
    return i;
}
```

---

## Step 4 — Complexity

| Operation | Time | Extra space |
|-----------|------|-------------|
| `ring_init` | O(1) | O(1) |
| `ring_push` / `ring_pop` | O(1) | O(1) |
| `ring_push_n` / `ring_pop_n` | O(k) for k bytes moved | O(1) |
| `ring_count` | O(1) | O(1) |

Backing buffer: **O(cap)** bytes.

---

## Step 5 — Edge cases

1. **`cap < 2`** — reject in `ring_init`; a ring needs at least one data slot plus spare slot semantics.
2. **Push when full** — return error; caller decides drop metric or backpressure (RTS, throttle producer).
3. **Pop when empty** — return error; don't block inside primitive (blocking belongs in higher layer).
4. **Burst larger than free space** — `ring_push_n` returns partial count; document behavior.
5. **`cap` not power-of-two** — modulo `% cap` is fine for small rings; for hot paths use Q017 mask trick.
6. **Producer and consumer on same index variable** — UB if both write `head`/`tail`; roles must be strict.

---

## Step 6 — Concurrency / ISR / context notes

**Single-core, ISR = producer, task = consumer (most common interview setup):**

- ISR writes `head` only; task writes `tail` only → **no lock** needed for data path on UP.
- ISR must not call `ring_count` if task also reads `head`/`tail` without coordination — if stats needed, use IRQ-save snapshot or update a `volatile`/atomic drop counter only from ISR.
- Keep ISR push minimal: `ring_push` only — no `printf`, no malloc.

**If both sides can run on different cores (SMP):** use **acquire/release atomics** on `head`/`tail` (see Q020). Producer loads `tail` with `acquire` before checking full; stores `head` with `release` after write.

**Memory barrier one-liner for interview:** consumer must not see new `head` until byte is visible → release after store to `buf`, acquire before read of `head` on consumer side in SMP variant.

---

## Step 7 — Follow-up answers

**Q: Why one spare slot instead of a count field?**  
**A:** Empty and full are both detectable with only `head`/`tail` — no third variable to keep in sync. Tradeoff: you lose one byte of storage. Count field gives full `cap` usable bytes but needs atomic count or a lock if both sides touch it.

**Q: Power-of-two size?**  
**A:** Replace `% cap` with `& (cap - 1)` when `cap` is pow2 — faster on CPUs without fast hardware divide. See Q017.

**Q: Overwrite-oldest when full (Tesla-style)?**  
**A:** On full, advance `tail` then write — drops oldest. Good for telemetry; bad for command/control streams. See Q018.

**Q: How does this connect to UART IRQ RX?**  
**A:** `uart_rx_isr` calls `ring_push` per byte; task drains with `ring_pop_n`. On full, increment `rx_drops` and optionally signal high-water callback. See Q019/Q049.

**Q: DMA-friendly read from ring?**  
**A:** If contiguous run from `tail` to end of buffer or `head`, DMA can read that span in one shot; wrap requires two segments. See Q021.

**Q: MPMC?**  
**A:** This design is **wrong** for multiple producers — need locks or lock-free MPSC (Vyukov). Don't bolt mutex on SPSC and call it done without stating new invariants.

---

## Step 8 — Tests

**Manual test matrix:**

| # | Case | Expected |
|---|------|----------|
| 1 | init cap=4, push 'A','B', pop twice | 'A','B', then empty |
| 2 | fill until full (cap=4 → 3 bytes) | 4th push fails |
| 3 | pop empty | returns -1 |
| 4 | push_n 10 into cap=8 ring | partial push, count == 7 max |
| 5 | peek_n doesn't move tail | pop still returns same first byte |

**Optional host test harness:**

```c
#include <assert.h>
#include <stdio.h>

int main(void) {
    uint8_t storage[4];
    ring_t r;
    assert(ring_init(&r, storage, 4) == 0);

    assert(ring_push(&r, 1) == 0);
    assert(ring_push(&r, 2) == 0);
    assert(ring_push(&r, 3) == 0);
    assert(ring_push(&r, 4) == -1); /* full: 3 usable bytes */

    uint8_t b;
    assert(ring_pop(&r, &b) == 0 && b == 1);
    assert(ring_push(&r, 4) == 0);

    assert(ring_count(&r) == 3);
    printf("Q016 tests passed\n");
    return 0;
}
```

---

## Interview delivery tip (30–45 min round)

1. State **spare-slot** full/empty rules **before** coding (2 min).
2. Implement `init` + single-byte push/pop (15 min).
3. Add `push_n` if time permits (5 min).
4. Close with ISR producer story + SMP follow-up (5 min).

**Your TI hook:** "On PRU/R5F UART paths we used the same SPSC pattern — ISR enqueues raw bytes, R5F task parses EnDAT/HDSL frames; on full we counted drops and throttled the host poll rate."
