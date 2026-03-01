# Topic 12 — Determinism and SMP Logging Interview Solutions (Q161-Q163)

## Q161: Wrap-safe timeout scheduler
### 1. Problem Statement
Wrap-safe timeout scheduler.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

static inline int time_after_u32(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) > 0;
}

typedef struct {
    uint32_t deadline;
} TimeoutTask;

int task_due(uint32_t now, const TimeoutTask *t) {
    return time_after_u32(now, t->deadline) || (now == t->deadline);
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Why does signed delta work across wrap?
2. What is the max safe timeout window?

## Q162: MPMC logging ring (bounded drop)
### 1. Problem Statement
MPMC logging ring (bounded drop).
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdatomic.h>
#include <stdint.h>

typedef struct { uint32_t ts, id, arg; } LogRec;

typedef struct {
    LogRec *buf;
    uint32_t cap;
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
    _Atomic uint32_t dropped;
} MpmcLog;

int mpmc_log_push(MpmcLog *r, LogRec rec) {
    uint32_t h, t, n;
    for (;;) {
        h = atomic_load_explicit(&r->head, memory_order_relaxed);
        t = atomic_load_explicit(&r->tail, memory_order_acquire);
        n = (h + 1u) % r->cap;
        if (n == t) {
            atomic_fetch_add_explicit(&r->dropped, 1u, memory_order_relaxed);
            return -1;
        }
        if (atomic_compare_exchange_weak_explicit(&r->head, &h, n,
                memory_order_acq_rel, memory_order_relaxed)) break;
    }
    r->buf[h] = rec;
    return 0;
}
```
### 4. Complexity
- O(1) average; CAS retries under contention
### 5. Interview Follow-ups
1. How do you guarantee bounded memory?
2. How do consumers avoid tearing when reading records?

## Q163: Dependency-safe driver init
### 1. Problem Statement
Dependency-safe driver init.
### 2. Assumptions
- Bare-metal/RTOS C firmware context.
- API should be deterministic and testable.
### 3. Full C Code
```c
#include <stdint.h>

typedef int (*init_fn_t)(void);

typedef struct {
    const int *deps;
    int dep_count;
    init_fn_t init;
    int inited;
} DriverNode;

int init_with_deps(DriverNode *nodes, int n) {
    int progress;
    do {
        progress = 0;
        for (int i = 0; i < n; i++) {
            if (nodes[i].inited) continue;
            int ok = 1;
            for (int d = 0; d < nodes[i].dep_count; d++) {
                if (!nodes[nodes[i].deps[d]].inited) { ok = 0; break; }
            }
            if (ok && nodes[i].init() == 0) {
                nodes[i].inited = 1;
                progress = 1;
            }
        }
    } while (progress);

    for (int i = 0; i < n; i++) if (!nodes[i].inited) return -1;
    return 0;
}
```
### 4. Complexity
- O(V * (V + E)) worst-case scan
### 5. Interview Follow-ups
1. How do you detect dependency cycles explicitly?
2. How do you rollback partial init failures?
