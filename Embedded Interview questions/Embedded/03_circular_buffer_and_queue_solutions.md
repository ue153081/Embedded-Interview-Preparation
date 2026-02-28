# Topic 3 — Circular Buffer and Queue Interview Solutions (Q035-Q046)

## Q035: SPSC circular buffer (array-based)
### 1. Problem Statement
Implement single-producer single-consumer ring buffer.
### 2. Assumptions
- Producer writes head only; consumer writes tail only.
### 3. Full C Code
```c
#include <stdint.h>
#include <stdatomic.h>

typedef struct {
    uint8_t *buf;
    uint32_t cap;
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
} SpscRing;

int spsc_push(SpscRing *r, uint8_t v) {
    uint32_t h = atomic_load_explicit(&r->head, memory_order_relaxed);
    uint32_t t = atomic_load_explicit(&r->tail, memory_order_acquire);
    uint32_t n = (h + 1u) % r->cap;

    if (n == t) {
        return -1;
    }

    r->buf[h] = v;
    atomic_store_explicit(&r->head, n, memory_order_release);
    return 0;
}

int spsc_pop(SpscRing *r, uint8_t *out) {
    uint32_t t = atomic_load_explicit(&r->tail, memory_order_relaxed);
    uint32_t h = atomic_load_explicit(&r->head, memory_order_acquire);

    if (t == h) {
        return -1;
    }

    *out = r->buf[t];
    atomic_store_explicit(&r->tail, (t + 1u) % r->cap, memory_order_release);
    return 0;
}
```
### 4. Complexity
- Push/pop O(1)
### 5. Interview Follow-ups
1. Why memory-order acquire/release?
2. What changes for MPMC?

## Q036: Ring buffer full/empty via one-slot-open method
### 1. Problem Statement
Detect full/empty with one reserved slot.
### 2. Assumptions
- Usable capacity is `cap-1`.
### 3. Full C Code
```c
int rb_is_empty(uint32_t head, uint32_t tail) {
    return head == tail;
}

int rb_is_full(uint32_t head, uint32_t tail, uint32_t cap) {
    return ((head + 1u) % cap) == tail;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Pros/cons vs count method?
2. Effective capacity impact?

## Q037: Ring buffer full/empty via count field
### 1. Problem Statement
Track occupancy explicitly.
### 2. Assumptions
- Count updates synchronized.
### 3. Full C Code
```c
typedef struct {
    uint8_t *buf;
    uint32_t cap;
    uint32_t head;
    uint32_t tail;
    uint32_t count;
} CountRing;

int count_ring_push(CountRing *r, uint8_t v) {
    if (r->count == r->cap) {
        return -1;
    }
    r->buf[r->head] = v;
    r->head = (r->head + 1u) % r->cap;
    r->count++;
    return 0;
}

int count_ring_pop(CountRing *r, uint8_t *out) {
    if (r->count == 0u) {
        return -1;
    }
    *out = r->buf[r->tail];
    r->tail = (r->tail + 1u) % r->cap;
    r->count--;
    return 0;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Race risk if count non-atomic?
2. Extra storage vs one-slot method?

## Q038: Ring buffer overwrite-oldest policy
### 1. Problem Statement
Always accept new data; drop oldest on full.
### 2. Assumptions
- Best for telemetry/logging.
### 3. Full C Code
```c
int spsc_push_overwrite(SpscRing *r, uint8_t v) {
    uint32_t h = atomic_load_explicit(&r->head, memory_order_relaxed);
    uint32_t t = atomic_load_explicit(&r->tail, memory_order_relaxed);
    uint32_t n = (h + 1u) % r->cap;

    if (n == t) {
        atomic_store_explicit(&r->tail, (t + 1u) % r->cap, memory_order_relaxed);
    }

    r->buf[h] = v;
    atomic_store_explicit(&r->head, n, memory_order_release);
    return 0;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. How to expose drop metrics?
2. Where is this policy unsafe?

## Q039: Ring buffer discard-newest policy
### 1. Problem Statement
Reject write when full.
### 2. Assumptions
- Data loss must be explicit to caller.
### 3. Full C Code
```c
int spsc_push_discard_new(SpscRing *r, uint8_t v) {
    return spsc_push(r, v);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. How caller handles E_FULL?
2. Retry/backoff strategy?

## Q040: Power-of-2 optimized ring indexing
### 1. Problem Statement
Replace modulo with bitmask for speed.
### 2. Assumptions
- Capacity is power of two.
### 3. Full C Code
```c
static inline uint32_t ring_next_pow2(uint32_t idx, uint32_t cap) {
    return (idx + 1u) & (cap - 1u);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Compile-time validation of cap?
2. Performance gain on target MCU?

## Q041: ISR-producer/task-consumer queue
### 1. Problem Statement
Queue bytes safely between ISR and task.
### 2. Assumptions
- Strict SPSC ownership.
### 3. Full C Code
```c
typedef struct {
    SpscRing *ring;
} UartIsrQueue;

int uart_isr_queue_push(UartIsrQueue *q, uint8_t b) {
    return spsc_push(q->ring, b);   /* ISR context */
}

int uart_task_queue_pop(UartIsrQueue *q, uint8_t *out) {
    return spsc_pop(q->ring, out);  /* task context */
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Why avoid mutex in ISR?
2. What if two tasks consume?

## Q042: DMA-friendly contiguous-read API for ring
### 1. Problem Statement
Expose linear readable chunk before wrap.
### 2. Assumptions
- Consumer can process in two calls if wrapped.
### 3. Full C Code
```c
uint32_t ring_contiguous_readable(const SpscRing *r) {
    uint32_t h = atomic_load_explicit((atomic_uint *)&r->head, memory_order_acquire);
    uint32_t t = atomic_load_explicit((atomic_uint *)&r->tail, memory_order_relaxed);

    if (h >= t) {
        return h - t;
    }
    return r->cap - t;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. How to expose second segment?
2. Zero-copy parser design?

## Q043: MPSC queue with lock protection
### 1. Problem Statement
Multiple producers, one consumer queue.
### 2. Assumptions
- Lock available in task context.
### 3. Full C Code
```c
#include <pthread.h>

typedef struct {
    SpscRing q;
    pthread_mutex_t lock;
} MpscQueue;

int mpsc_enqueue(MpscQueue *m, uint8_t v) {
    int rc;
    pthread_mutex_lock(&m->lock);
    rc = spsc_push(&m->q, v);
    pthread_mutex_unlock(&m->lock);
    return rc;
}
```
### 4. Complexity
- O(1) average + lock contention
### 5. Interview Follow-ups
1. How to make this lock-free?
2. Priority inversion risk?

## Q044: Lock-free linked-list SPSC queue
### 1. Problem Statement
Implement linked queue with single producer and consumer.
### 2. Assumptions
- Pre-allocated nodes preferred for determinism.
### 3. Full C Code
```c
typedef struct LNode {
    uint8_t val;
    _Atomic(struct LNode *) next;
} LNode;

typedef struct {
    _Atomic(LNode *) head;
    _Atomic(LNode *) tail;
} SpscListQ;

int spsc_list_push(SpscListQ *q, LNode *n) {
    atomic_store_explicit(&n->next, NULL, memory_order_relaxed);
    LNode *tail = atomic_load_explicit(&q->tail, memory_order_relaxed);
    atomic_store_explicit(&tail->next, n, memory_order_release);
    atomic_store_explicit(&q->tail, n, memory_order_release);
    return 0;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Node lifetime ownership?
2. Why array ring may be better in embedded?

## Q045: Deferred interrupt work queue (top-half/bottom-half)
### 1. Problem Statement
Move heavy ISR work into worker context.
### 2. Assumptions
- ISR pushes event ID only.
### 3. Full C Code
```c
typedef struct {
    uint8_t type;
    uint32_t arg;
} IrqEvent;

int irq_top_half_enqueue(SpscRing *event_q, IrqEvent e) {
    return spsc_push(event_q, e.type);
}

void irq_bottom_half_worker(SpscRing *event_q) {
    uint8_t type;
    while (spsc_pop(event_q, &type) == 0) {
        /* process heavy work here */
    }
}
```
### 4. Complexity
- ISR path O(1)
### 5. Interview Follow-ups
1. Queue overflow handling?
2. Event coalescing strategy?

## Q046: Priority event queue
### 1. Problem Statement
Enqueue events ordered by priority.
### 2. Assumptions
- Smaller value = higher priority.
### 3. Full C Code
```c
typedef struct {
    uint8_t prio;
    uint8_t id;
} PrioEvent;

void prio_insert_sorted(PrioEvent *arr, int *n, PrioEvent e) {
    int i = *n;
    while (i > 0 && arr[i - 1].prio > e.prio) {
        arr[i] = arr[i - 1];
        i--;
    }
    arr[i] = e;
    (*n)++;
}
```
### 4. Complexity
- O(n) insert
### 5. Interview Follow-ups
1. Heap alternative complexity?
2. Tie-break fairness approach?
