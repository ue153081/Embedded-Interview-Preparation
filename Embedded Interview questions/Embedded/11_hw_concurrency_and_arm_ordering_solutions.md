# Topic 11 — HW Concurrency and ARM Ordering Interview Solutions (Q135-Q160)

## Q135: Store buffering litmus (SMP)
### 1. Problem Statement
Store buffering litmus (SMP).
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdatomic.h>
#include <stdint.h>

typedef struct {
    _Atomic uint32_t x;
    _Atomic uint32_t y;
    _Atomic uint32_t r1;
    _Atomic uint32_t r2;
} Litmus;

void core0(Litmus *s) {
    atomic_store_explicit(&s->x, 1u, memory_order_relaxed);
    atomic_store_explicit(&s->r1, atomic_load_explicit(&s->y, memory_order_relaxed), memory_order_relaxed);
}

void core1(Litmus *s) {
    atomic_store_explicit(&s->y, 1u, memory_order_relaxed);
    atomic_store_explicit(&s->r2, atomic_load_explicit(&s->x, memory_order_relaxed), memory_order_relaxed);
}

/* r1=0 and r2=0 can appear on weak ordering without stronger synchronization. */
```
### 4. Complexity
- O(1) per thread step
### 5. Interview Follow-ups
1. Why can both reads observe 0?
2. How do you make this test deterministic?

## Q136: Dekker failure w/o barriers
### 1. Problem Statement
Dekker failure w/o barriers.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdatomic.h>
#include <stdint.h>

typedef struct {
    _Atomic uint32_t want0;
    _Atomic uint32_t want1;
} DekkerFlags;

/* Broken variant if relaxed only: */
int enter_cs0_broken(DekkerFlags *f) {
    atomic_store_explicit(&f->want0, 1u, memory_order_relaxed);
    if (atomic_load_explicit(&f->want1, memory_order_relaxed)) return -1;
    return 0;
}

/* Fix uses acquire/release or full barrier protocol around flag publication/check. */
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Why is classic Dekker subtle on modern CPUs?
2. Would volatile fix this?

## Q137: Relaxed ordering queue bug
### 1. Problem Statement
Relaxed ordering queue bug.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdatomic.h>
#include <stdint.h>

typedef struct {
    uint8_t *buf;
    uint32_t cap;
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
} Ring;

/* Correct publish order: payload write then release-store head. */
int ring_push_fixed(Ring *r, uint8_t v) {
    uint32_t h = atomic_load_explicit(&r->head, memory_order_relaxed);
    uint32_t t = atomic_load_explicit(&r->tail, memory_order_acquire);
    uint32_t n = (h + 1u) % r->cap;
    if (n == t) return -1;
    r->buf[h] = v;
    atomic_store_explicit(&r->head, n, memory_order_release);
    return 0;
}
```
### 4. Complexity
- O(1) push/pop
### 5. Interview Follow-ups
1. What goes wrong if head is published before payload?
2. Why acquire on consumer-side head read?

## Q138: ISR<->task flag handoff
### 1. Problem Statement
ISR<->task flag handoff.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdatomic.h>
#include <stdint.h>

typedef struct { _Atomic uint32_t flag; } Handoff;

void isr_signal(Handoff *h) {
    atomic_store_explicit(&h->flag, 1u, memory_order_release);
}

int task_try_consume(Handoff *h) {
    uint32_t expected = 1u;
    return atomic_compare_exchange_strong_explicit(
        &h->flag, &expected, 0u,
        memory_order_acquire, memory_order_relaxed);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. How do you avoid lost notifications?
2. Would this support event counting?

## Q139: Multi-core stale-read ring
### 1. Problem Statement
Multi-core stale-read ring.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdatomic.h>
#include <stdint.h>

/* Fix stale-read by using release when producer publishes index and acquire on consumer read. */
static inline uint32_t load_head_acquire(_Atomic uint32_t *head) {
    return atomic_load_explicit(head, memory_order_acquire);
}

static inline void store_head_release(_Atomic uint32_t *head, uint32_t v) {
    atomic_store_explicit(head, v, memory_order_release);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Why does stale data appear without ordering?
2. Do you need barriers on single-core MCU?

## Q140: Volatile vs atomic (driver flag)
### 1. Problem Statement
Volatile vs atomic (driver flag).
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdatomic.h>
#include <stdint.h>

volatile uint32_t ready_v;
_Atomic uint32_t ready_a;
uint32_t payload;

/* Volatile does not provide inter-core synchronization. */
void producer_ok(uint32_t v) {
    payload = v;
    atomic_store_explicit(&ready_a, 1u, memory_order_release);
}

int consumer_ok(uint32_t *out) {
    if (!atomic_load_explicit(&ready_a, memory_order_acquire)) return 0;
    *out = payload;
    return 1;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. What exactly does volatile guarantee?
2. When is volatile still required?

## Q141: Write-combining MMIO hazard
### 1. Problem Statement
Write-combining MMIO hazard.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

static inline void dmb(void) { __asm__ volatile("dmb ish" : : : "memory"); }

typedef struct {
    volatile uint32_t DESC_ADDR;
    volatile uint32_t DOORBELL;
} Dev;

void submit_descriptor(Dev *d, uint32_t addr) {
    d->DESC_ADDR = addr;
    dmb();              /* Ensure descriptor pointer visible before doorbell */
    d->DOORBELL = 1u;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Why can posted writes reorder on interconnect?
2. How do you verify this race in lab?

## Q142: SMP cache vs DMA visibility
### 1. Problem Statement
SMP cache vs DMA visibility.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

void cache_clean_range(void *buf, uint32_t len);
void cache_invalidate_range(void *buf, uint32_t len);

void dma_tx_prepare(void *buf, uint32_t len) {
    cache_clean_range(buf, len);      /* CPU writes -> DMA reads */
}

void dma_rx_complete(void *buf, uint32_t len) {
    cache_invalidate_range(buf, len); /* DMA writes -> CPU reads */
}
```
### 4. Complexity
- O(len / cache_line)
### 5. Interview Follow-ups
1. When do you need clean vs invalidate?
2. What about non-cacheable memory regions?

## Q143: Correct DMB placement
### 1. Problem Statement
Correct DMB placement.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

static inline void dmb(void) { __asm__ volatile("dmb ish" : : : "memory"); }

typedef struct { volatile uint32_t CTRL, PTR; } Periph;

void start_periph(Periph *p, uint32_t ptr) {
    p->PTR = ptr;
    dmb();          /* Order descriptor/meta writes before start */
    p->CTRL = 1u;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Where should DMB be placed: before or after CTRL write?
2. DMB vs DSB difference here?

## Q144: DSB in IRQ completion
### 1. Problem Statement
DSB in IRQ completion.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

static inline void dsb(void) { __asm__ volatile("dsb ish" : : : "memory"); }

typedef struct { volatile uint32_t IRQ_ACK; } Periph;

void irq_done(Periph *p) {
    p->IRQ_ACK = 1u;
    dsb(); /* Ensure ack reaches peripheral before ISR return */
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Why is DSB used on interrupt-exit critical paths?
2. What happens if you omit it?

## Q145: ISB after control write
### 1. Problem Statement
ISB after control write.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

static inline void isb(void) { __asm__ volatile("isb" : : : "memory"); }

typedef struct { volatile uint32_t SYS_CTRL; } Cpu;

void enable_feature(Cpu *c) {
    c->SYS_CTRL |= 1u;
    isb(); /* Synchronize pipeline with new control state */
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. When is ISB mandatory vs optional?
2. Can DMB replace ISB?

## Q146: Safe MMIO polling (barriers)
### 1. Problem Statement
Safe MMIO polling (barriers).
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

static inline void dmb(void) { __asm__ volatile("dmb ish" : : : "memory"); }

int mmio_wait_mask(volatile uint32_t *reg, uint32_t mask, uint32_t exp, uint32_t timeout) {
    while (timeout--) {
        dmb();
        if ((*reg & mask) == exp) return 0;
    }
    return -1;
}
```
### 4. Complexity
- O(timeout)
### 5. Interview Follow-ups
1. How do you avoid busy-spin CPU burn?
2. How should timeout be represented wrap-safe?

## Q147: Status clear ordering race
### 1. Problem Statement
Status clear ordering race.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

static inline void dmb(void) { __asm__ volatile("dmb ish" : : : "memory"); }

typedef struct { volatile uint32_t STATUS, CLR; } IrqRegs;

void clear_status(IrqRegs *r, uint32_t mask) {
    uint32_t s = r->STATUS;
    r->CLR = s & mask; /* W1C */
    dmb();
    (void)r->STATUS;   /* Readback to drain posted write paths */
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Why do we read back STATUS after clear?
2. How does this prevent interrupt storms?

## Q148: IRQ-safe reference counter
### 1. Problem Statement
IRQ-safe reference counter.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdatomic.h>
#include <stdint.h>

typedef struct { _Atomic uint32_t ref; } RefCnt;

void ref_get(RefCnt *r) {
    atomic_fetch_add_explicit(&r->ref, 1u, memory_order_relaxed);
}

int ref_put(RefCnt *r) {
    return atomic_fetch_sub_explicit(&r->ref, 1u, memory_order_acq_rel) == 1u;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. What memory order should final put use?
2. How do you prevent underflow?

## Q149: IRQ-safe allocator (fallback)
### 1. Problem Statement
IRQ-safe allocator (fallback).
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

typedef struct Node { struct Node *next; } Node;
typedef struct { Node *head; } Pool;

static inline unsigned irq_save(void) { return 0; }
static inline void irq_restore(unsigned s) { (void)s; }

void *irq_safe_alloc(Pool *main_pool, Pool *fallback_pool) {
    unsigned s = irq_save();
    Node *n = main_pool->head;
    if (n) main_pool->head = n->next;
    irq_restore(s);
    if (n) return n;

    s = irq_save();
    n = fallback_pool->head;
    if (n) fallback_pool->head = n->next;
    irq_restore(s);
    return n;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Why keep critical section tiny?
2. When should fallback allocation be denied?

## Q150: Top/bottom-half API
### 1. Problem Statement
Top/bottom-half API.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

#define WORK_Q_CAP 32u

typedef struct {
    uint32_t q[WORK_Q_CAP];
    uint32_t head, tail;
} WorkQ;

int isr_defer_work(WorkQ *w, uint32_t id) {
    uint32_t n = (w->head + 1u) % WORK_Q_CAP;
    if (n == w->tail) return -1;
    w->q[w->head] = id;
    w->head = n;
    return 0;
}

int worker_get_work(WorkQ *w, uint32_t *id) {
    if (w->tail == w->head) return -1;
    *id = w->q[w->tail];
    w->tail = (w->tail + 1u) % WORK_Q_CAP;
    return 0;
}
```
### 4. Complexity
- O(1) enqueue/dequeue
### 5. Interview Follow-ups
1. What must remain in top-half only?
2. How do you prioritize deferred work?

## Q151: Nested IRQ-safe CS
### 1. Problem Statement
Nested IRQ-safe CS.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

typedef struct {
    uint32_t nesting;
    uint32_t saved_state;
} IrqCs;

uint32_t arch_irq_disable(void);
void arch_irq_restore(uint32_t state);

void cs_enter(IrqCs *c) {
    if (c->nesting++ == 0u) c->saved_state = arch_irq_disable();
}

void cs_exit(IrqCs *c) {
    if (c->nesting == 0u) return;
    if (--c->nesting == 0u) arch_irq_restore(c->saved_state);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. How do you detect unmatched exits?
2. Can this be used on SMP safely?

## Q152: Shared stats (ISR+task)
### 1. Problem Statement
Shared stats (ISR+task).
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

typedef struct {
    volatile uint32_t seq;
    volatile uint32_t a;
    volatile uint32_t b;
} SeqStats;

void stats_write(SeqStats *s, uint32_t a, uint32_t b) {
    s->seq++;
    s->a = a;
    s->b = b;
    s->seq++;
}

int stats_read(SeqStats *s, uint32_t *a, uint32_t *b) {
    uint32_t s1, s2;
    do {
        s1 = s->seq;
        if (s1 & 1u) continue;
        *a = s->a;
        *b = s->b;
        s2 = s->seq;
    } while (s1 != s2);
    return 0;
}
```
### 4. Complexity
- O(1) average, retries possible
### 5. Interview Follow-ups
1. Why seqlock is good for read-heavy stats?
2. What if there are multiple writers?

## Q153: Latency-bounded deferral
### 1. Problem Statement
Latency-bounded deferral.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

int process_critical_chunk(uint32_t budget_cycles);
void defer_remaining_work(void);

void isr_handler(uint32_t budget_cycles) {
    int done = process_critical_chunk(budget_cycles);
    if (!done) {
        defer_remaining_work();
    }
}
```
### 4. Complexity
- O(1) ISR decision + bounded chunk
### 5. Interview Follow-ups
1. How do you pick budget threshold?
2. How do you verify worst-case latency?

## Q154: CPU<->DMA ownership bug
### 1. Problem Statement
CPU<->DMA ownership bug.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

typedef enum { OWN_CPU, OWN_DMA, OWN_DMA_DONE } Owner;

typedef struct {
    void *buf;
    uint32_t len;
    Owner own;
} DmaBuf;

int submit_to_dma(DmaBuf *b) {
    if (b->own != OWN_CPU) return -1;
    b->own = OWN_DMA;
    return 0;
}

int reclaim_from_dma(DmaBuf *b) {
    if (b->own != OWN_DMA_DONE) return -1;
    b->own = OWN_CPU;
    return 0;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. How do you detect double submit/reclaim?
2. Where do cache ops belong in this FSM?

## Q155: Cache omission failure
### 1. Problem Statement
Cache omission failure.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

/* Bug: CPU reads stale RX data if invalidate omitted. */
void cache_invalidate_range(void *buf, uint32_t len);

int rx_consume(void *buf, uint32_t len) {
    cache_invalidate_range(buf, len);
    /* parse/consume buffer */
    return 0;
}
```
### 4. Complexity
- O(len / cache_line)
### 5. Interview Follow-ups
1. Why can stale data persist after DMA write?
2. How do you test coherency bugs?

## Q156: Ping-pong DMA race
### 1. Problem Statement
Ping-pong DMA race.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdatomic.h>
#include <stdint.h>

typedef struct {
    _Atomic uint32_t active;   /* 0 or 1 */
    _Atomic uint32_t ready[2];
} PingPong;

void dma_done_isr(PingPong *p) {
    uint32_t cur = atomic_load_explicit(&p->active, memory_order_relaxed);
    atomic_store_explicit(&p->ready[cur], 1u, memory_order_release);
    atomic_store_explicit(&p->active, cur ^ 1u, memory_order_release);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. How do you prevent both buffers being marked ready incorrectly?
2. Where are invalidate operations placed?

## Q157: Lock contention counter
### 1. Problem Statement
Lock contention counter.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdatomic.h>
#include <stdint.h>

typedef struct {
    _Atomic uint32_t attempts;
    _Atomic uint32_t contended;
} LockMetrics;

void on_lock_attempt(LockMetrics *m, int immediate_success) {
    atomic_fetch_add_explicit(&m->attempts, 1u, memory_order_relaxed);
    if (!immediate_success) atomic_fetch_add_explicit(&m->contended, 1u, memory_order_relaxed);
}
```
### 4. Complexity
- O(1) per lock attempt
### 5. Interview Follow-ups
1. How do you avoid metric overhead impacting lock behavior?
2. Would you sample instead of counting all attempts?

## Q158: ISR time histogram
### 1. Problem Statement
ISR time histogram.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

#define HIST_BINS 8

typedef struct {
    uint32_t edge[HIST_BINS];
    uint32_t count[HIST_BINS + 1];
} IsrHist;

void hist_add(IsrHist *h, uint32_t cycles) {
    uint32_t i = 0;
    while (i < HIST_BINS && cycles > h->edge[i]) i++;
    h->count[i]++;
}
```
### 4. Complexity
- O(bins) worst case
### 5. Interview Follow-ups
1. How do you choose bin edges?
2. How do you capture tail latency spikes?

## Q159: Queue watermark telemetry
### 1. Problem Statement
Queue watermark telemetry.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

typedef struct {
    uint32_t depth;
    uint32_t peak;
    uint32_t dropped;
} QStats;

void q_push_event(QStats *s, int success) {
    if (!success) { s->dropped++; return; }
    s->depth++;
    if (s->depth > s->peak) s->peak = s->depth;
}

void q_pop_event(QStats *s) {
    if (s->depth) s->depth--;
}
```
### 4. Complexity
- O(1) per queue event
### 5. Interview Follow-ups
1. How do you export this without locking overhead?
2. Would you reset peak periodically?

## Q160: Priority inversion trace
### 1. Problem Statement
Priority inversion trace.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

typedef struct {
    uint32_t ts_lock;
    uint32_t ts_block;
    uint32_t owner_prio;
    uint32_t waiter_prio;
} PiTrace;

void pi_trace_on_block(PiTrace *t, uint32_t ts, uint32_t owner, uint32_t waiter) {
    t->ts_block = ts;
    t->owner_prio = owner;
    t->waiter_prio = waiter;
}
```
### 4. Complexity
- O(1) per trace update
### 5. Interview Follow-ups
1. How do you correlate inversion events with scheduler trace?
2. What data is minimally required for diagnosis?
