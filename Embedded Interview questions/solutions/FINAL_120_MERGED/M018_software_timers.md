# M018 — Software timers & tick dispatch

**Type:** Coding (C)  
**Merged from:** Q061, Q062, Q063, Q064  
**Companies:** Google · Apple · Tesla  
**Tier:** S (must-know)

**Question:** SW timers on one HW timer; periodic + wrap-safe compares; sorted list / min-heap / timer wheel; regCall/callNext dispatcher.

---

## Sub-variant coverage

| Original Q | Sub-variant |
|---|---|
| Q061 | Drift-free periodic |
| Q062 | cancel_sync race |
| Q063 | Tickless sleep |
| Q064 | See merged solution |

---

## Step 0 — Clarifying questions (say these out loud)

- **Candidate:** Callback in ISR or deferred worker?
- **Candidate:** Max timer count N?

## Step 1 — Approach

Build Software timers & tick dispatch in layers: invariants first, happy path, then edge cases and concurrency.

- Restate API signatures and invariants aloud before coding.
- Implement core logic with straightforward loops; optimize after tests pass.
- Document ownership, error codes, and ISR vs task context.

## Step 2 — Data structures / invariants

1. Structs/enums matching API — invariants in comments.
2. Platform hooks (`irq_save`, `now_ms`) isolated for host test fakes.

## Step 3 — Complete solution (compilable C)

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

/* --- next section --- */

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

/* --- next section --- */

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

/* --- next section --- */

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

/* --- next section --- */

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

**Q: List vs heap vs wheel?**  
**A:** List <16 timers; heap 16–500; wheel for many coarse timeouts.


## Step 8 — Tests

1. Happy path — minimal valid input produces expected output.
2. Zero/null/empty — defined error, no crash.
3. Boundary — max capacity or timeout edge.
4. Stress — back-to-back calls or burst traffic.

## Further study

- [Timer Wheel](https://github.com/theEmbeddedGeorge/theEmbeddedNewTestament.github.io/blob/master/Data_Struct_Implementation/timerWheel/README.md)
- [Timer/Counter Programming](https://github.com/theEmbeddedGeorge/theEmbeddedNewTestament.github.io/blob/master/HW_Module/Timer_Counter_Programming.md)

---

*Generated by `tools/generate_merged_solutions.py` for M018.*