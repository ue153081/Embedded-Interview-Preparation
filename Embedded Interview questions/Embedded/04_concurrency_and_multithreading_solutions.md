# Topic 4 — Concurrency and Multithreading Interview Solutions (Q047-Q060)

## Q047: Spinlock using atomic_flag
### 1. Problem Statement
Implement a minimal spinlock.
### 2. Assumptions
- Very short critical sections.
### 3. Full C Code
```c
#include <stdatomic.h>

typedef struct {
    atomic_flag flag;
} SpinLock;

void spinlock_init(SpinLock *l) {
    atomic_flag_clear(&l->flag);
}

void spinlock_lock(SpinLock *l) {
    while (atomic_flag_test_and_set_explicit(&l->flag, memory_order_acquire)) {
        /* spin */
    }
}

void spinlock_unlock(SpinLock *l) {
    atomic_flag_clear_explicit(&l->flag, memory_order_release);
}
```
### 4. Complexity
- O(1) uncontended
### 5. Interview Follow-ups
1. Why dangerous in ISR/low-priority tasks?
2. Backoff strategy?

## Q048: Ticket lock implementation
### 1. Problem Statement
Fair lock with FIFO ordering.
### 2. Assumptions
- Atomics available.
### 3. Full C Code
```c
typedef struct {
    _Atomic unsigned next_ticket;
    _Atomic unsigned now_serving;
} TicketLock;

void ticket_lock(TicketLock *l) {
    unsigned my = atomic_fetch_add_explicit(&l->next_ticket, 1u, memory_order_relaxed);
    while (atomic_load_explicit(&l->now_serving, memory_order_acquire) != my) {
        /* spin */
    }
}

void ticket_unlock(TicketLock *l) {
    atomic_fetch_add_explicit(&l->now_serving, 1u, memory_order_release);
}
```
### 4. Complexity
- O(1) uncontended
### 5. Interview Follow-ups
1. Fairness vs cache traffic?
2. Counter wrap concerns?

## Q049: Minimal mutex using atomics
### 1. Problem Statement
Implement simple non-recursive mutex.
### 2. Assumptions
- Busy-wait variant acceptable for exercise.
### 3. Full C Code
```c
typedef struct {
    _Atomic int locked;
} TinyMutex;

void tiny_mutex_lock(TinyMutex *m) {
    int expected;
    for (;;) {
        expected = 0;
        if (atomic_compare_exchange_weak_explicit(
                &m->locked, &expected, 1,
                memory_order_acquire, memory_order_relaxed)) {
            return;
        }
    }
}

void tiny_mutex_unlock(TinyMutex *m) {
    atomic_store_explicit(&m->locked, 0, memory_order_release);
}
```
### 4. Complexity
- O(1) uncontended
### 5. Interview Follow-ups
1. How to avoid CPU burn?
2. Add owner tracking?

## Q050: Counting semaphore implementation
### 1. Problem Statement
Manage available resource units.
### 2. Assumptions
- Try-wait style shown.
### 3. Full C Code
```c
typedef struct {
    _Atomic int count;
} CountSem;

void sem_post(CountSem *s) {
    atomic_fetch_add_explicit(&s->count, 1, memory_order_release);
}

int sem_try_wait(CountSem *s) {
    int c = atomic_load_explicit(&s->count, memory_order_relaxed);
    while (c > 0) {
        if (atomic_compare_exchange_weak_explicit(
                &s->count, &c, c - 1,
                memory_order_acquire, memory_order_relaxed)) {
            return 0;
        }
    }
    return -1;
}
```
### 4. Complexity
- O(1) average
### 5. Interview Follow-ups
1. Blocking wait integration?
2. Overflow/underflow checks?

## Q051: Binary semaphore (ISR give, task take)
### 1. Problem Statement
Signal task from ISR.
### 2. Assumptions
- Value is 0/1 only.
### 3. Full C Code
```c
typedef struct {
    _Atomic int value;
} BinSem;

void binsem_give_isr(BinSem *s) {
    atomic_store_explicit(&s->value, 1, memory_order_release);
}

int binsem_take_task(BinSem *s) {
    int expected = 1;
    if (atomic_compare_exchange_strong_explicit(
            &s->value, &expected, 0,
            memory_order_acquire, memory_order_relaxed)) {
        return 0;
    }
    return -1;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Lost wakeup prevention?
2. Event flag alternative?

## Q052: Reader-writer lock
### 1. Problem Statement
Allow concurrent readers, exclusive writers.
### 2. Assumptions
- Demonstration-level implementation.
### 3. Full C Code
```c
typedef struct {
    TinyMutex gate;
    _Atomic int readers;
} RWLock;

void rw_read_lock(RWLock *l) {
    atomic_fetch_add_explicit(&l->readers, 1, memory_order_acquire);
}

void rw_read_unlock(RWLock *l) {
    atomic_fetch_sub_explicit(&l->readers, 1, memory_order_release);
}

void rw_write_lock(RWLock *l) {
    tiny_mutex_lock(&l->gate);
    while (atomic_load_explicit(&l->readers, memory_order_acquire) != 0) {
        /* spin */
    }
}

void rw_write_unlock(RWLock *l) {
    tiny_mutex_unlock(&l->gate);
}
```
### 4. Complexity
- O(1) bookkeeping
### 5. Interview Follow-ups
1. Starvation risk?
2. Fair RW policy design?

## Q053: Atomic counter with overflow-safe logic
### 1. Problem Statement
Increment counter safely at max value.
### 2. Assumptions
- Saturating semantics.
### 3. Full C Code
```c
#include <limits.h>

unsigned sat_inc_u32(_Atomic unsigned *v) {
    unsigned cur = atomic_load_explicit(v, memory_order_relaxed);

    for (;;) {
        if (cur == UINT_MAX) {
            return cur;
        }
        if (atomic_compare_exchange_weak_explicit(
                v, &cur, cur + 1u,
                memory_order_release, memory_order_relaxed)) {
            return cur + 1u;
        }
    }
}
```
### 4. Complexity
- O(1) average
### 5. Interview Follow-ups
1. Wrap vs saturate policy?
2. 64-bit counter tradeoffs?

## Q054: Producer-consumer bounded buffer
### 1. Problem Statement
Classic bounded queue with synchronization.
### 2. Assumptions
- Hosted environment primitives.
### 3. Full C Code
```c
typedef struct {
    uint8_t *buf;
    uint32_t cap;
    uint32_t head;
    uint32_t tail;
    TinyMutex lock;
    CountSem items;
    CountSem slots;
} BoundedQ;

int bq_push(BoundedQ *q, uint8_t v) {
    if (sem_try_wait(&q->slots) != 0) {
        return -1;
    }

    tiny_mutex_lock(&q->lock);
    q->buf[q->head] = v;
    q->head = (q->head + 1u) % q->cap;
    tiny_mutex_unlock(&q->lock);

    sem_post(&q->items);
    return 0;
}

int bq_pop(BoundedQ *q, uint8_t *out) {
    if (sem_try_wait(&q->items) != 0) {
        return -1;
    }

    tiny_mutex_lock(&q->lock);
    *out = q->buf[q->tail];
    q->tail = (q->tail + 1u) % q->cap;
    tiny_mutex_unlock(&q->lock);

    sem_post(&q->slots);
    return 0;
}
```
### 4. Complexity
- O(1) per operation
### 5. Interview Follow-ups
1. Deadlock if lock order wrong?
2. ISR compatibility?

## Q055: Deadlock detection (wait-for graph)
### 1. Problem Statement
Detect cycle in wait-for dependency graph.
### 2. Assumptions
- Directed graph adjacency matrix.
### 3. Full C Code
```c
int dfs_cycle(int u, int n, int g[n][n], int vis[], int stack[]) {
    vis[u] = 1;
    stack[u] = 1;

    for (int v = 0; v < n; v++) {
        if (!g[u][v]) {
            continue;
        }
        if (!vis[v] && dfs_cycle(v, n, g, vis, stack)) {
            return 1;
        }
        if (stack[v]) {
            return 1;
        }
    }

    stack[u] = 0;
    return 0;
}
```
### 4. Complexity
- O(V+E)
### 5. Interview Follow-ups
1. Runtime detection overhead?
2. Lock-order prevention strategy?

## Q056: Priority inversion mitigation design coding
### 1. Problem Statement
Raise owner priority when high-priority waiter blocks.
### 2. Assumptions
- OS supports dynamic priority change.
### 3. Full C Code
```c
typedef struct {
    int owner_prio;
    int inherited_prio;
} PiMutex;

void pi_on_wait(PiMutex *m, int waiter_prio) {
    if (waiter_prio > m->inherited_prio) {
        m->inherited_prio = waiter_prio;
    }
}

void pi_on_unlock(PiMutex *m) {
    m->inherited_prio = m->owner_prio;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Chained inheritance handling?
2. Priority ceiling alternative?

## Q057: Starvation-free reader/writer policy
### 1. Problem Statement
Prevent writers from starving under heavy read load.
### 2. Assumptions
- Writer-waiting flag used.
### 3. Full C Code
```c
typedef struct {
    _Atomic int readers;
    _Atomic int writer_waiting;
    TinyMutex writer_lock;
} FairRW;

int fairrw_try_read(FairRW *l) {
    if (atomic_load_explicit(&l->writer_waiting, memory_order_acquire)) {
        return -1;
    }
    atomic_fetch_add_explicit(&l->readers, 1, memory_order_acquire);
    return 0;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Throughput impact?
2. Queue-based fairness?

## Q058: ABA issue demo on lock-free stack
### 1. Problem Statement
Show CAS can succeed incorrectly after A->B->A pointer reuse.
### 2. Assumptions
- Memory reclamation naive.
### 3. Full C Code
```c
typedef struct StackNode {
    struct StackNode *next;
} StackNode;

typedef struct {
    _Atomic(StackNode *) head;
} LockFreeStack;

int aba_demo_pop(LockFreeStack *s, StackNode **out) {
    StackNode *old_head = atomic_load_explicit(&s->head, memory_order_acquire);
    if (!old_head) return -1;

    StackNode *next = old_head->next;
    if (atomic_compare_exchange_strong_explicit(
            &s->head, &old_head, next,
            memory_order_acq_rel, memory_order_acquire)) {
        *out = old_head;
        return 0;
    }
    return -1;
}
```
### 4. Complexity
- Conceptual
### 5. Interview Follow-ups
1. Tagged pointers solution?
2. Hazard pointers/epoch GC?

## Q059: Lock-free stack with tagged-pointer sketch
### 1. Problem Statement
Mitigate ABA via versioned head.
### 2. Assumptions
- Pointer alignment leaves low bits free.
### 3. Full C Code
```c
#include <stdint.h>

typedef struct {
    uintptr_t ptr_ver;
} TaggedHead;

uintptr_t make_tagged(void *ptr, uint16_t ver) {
    return ((uintptr_t)ptr & ~0xFFFFu) | (uintptr_t)ver;
}
```
### 4. Complexity
- O(1) per CAS loop
### 5. Interview Follow-ups
1. Version wraparound risk?
2. Portable wide CAS requirement?

## Q060: Acquire/release memory-order correctness exercise
### 1. Problem Statement
Publish data with release, consume with acquire.
### 2. Assumptions
- Shared `flag` and `data`.
### 3. Full C Code
```c
typedef struct {
    _Atomic int flag;
    int data;
} MsgCell;

void producer_publish(MsgCell *m, int v) {
    m->data = v;
    atomic_store_explicit(&m->flag, 1, memory_order_release);
}

int consumer_try_read(MsgCell *m, int *out) {
    if (atomic_load_explicit(&m->flag, memory_order_acquire) == 0) {
        return -1;
    }
    *out = m->data;
    return 0;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Why relaxed is unsafe here?
2. When seq_cst is needed?
