# M007 — IPC, mailboxes & lock-free handoff

**Type:** Coding (C)  
**Merged from:** Q022, Q023, Q024, Q025, Q026, Q027, Q028  
**Companies:** Google · Apple · Amazon · Tesla · NVIDIA · Qualcomm  

**Question:** Logging ring, priority event queue, dual-core mailbox, zero-copy buffer transfer, sequence-lock stats, ISR flag, bounded producer-consumer.

---

## Sub-variant coverage

| Original Q | Sub-variant |
|---|---|
| Q022 | Backpressure |
| Q023 | Generation counters |
| Q024 | Cache-line alignment |
| Q025 | irq_save vs atomics |
| Q026 | See merged solution |
| Q027 | See merged solution |
| Q028 | See merged solution |

---

## Step 0 — Clarifying questions (say these out loud)

- **Candidate:** SPSC or MPSC logging?
- **Candidate:** Shared SRAM cache-coherent or explicit flush?

## Step 1 — Approach

Build IPC, mailboxes & lock-free handoff in layers: invariants first, happy path, then edge cases and concurrency.

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
/* --- next section --- */
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
/* --- next section --- */
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
/* --- next section --- */
#include <stdint.h>
#include <stddef.h>
typedef struct {
    uint8_t buf[2][256];
    int write_idx, read_idx, ready;
}
dbuf_t;
uint8_t *dbuf_write_begin(dbuf_t *d) {
    return d->buf[d->write_idx];
}
void dbuf_write_end(dbuf_t *d) {
    d->ready=1;
    d->write_idx^=1;
}
const uint8_t *dbuf_read_begin(dbuf_t *d) {
    return d->ready?d->buf[d->read_idx]:0;
}
void dbuf_read_end(dbuf_t *d) {
    d->ready=0;
    d->read_idx^=1;
}
/* --- next section --- */
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

**Q: Mailbox ordering?**  
**A:** Payload visible before doorbell IRQ; use release store then trigger interrupt.


## Step 8 — Tests

1. Happy path — minimal valid input produces expected output.
2. Zero/null/empty — defined error, no crash.
3. Boundary — max capacity or timeout edge.
4. Stress — back-to-back calls or burst traffic.

## Further study

- [Shared Memory Programming](https://github.com/theEmbeddedGeorge/theEmbeddedNewTestament.github.io/blob/master/Embedded_C/Shared_Memory_Programming.md)
- [Bounded Queue](https://github.com/theEmbeddedGeorge/theEmbeddedNewTestament.github.io/blob/master/Data_Struct_Implementation/concurrency/BoundedQueue.md)

---

*Generated by `tools/generate_merged_solutions.py` for M007.*