# Topic 8 — Real-Time and Reliability Interview Solutions (Q099-Q108)

## Q099: Software timer queue (sorted linked list)
### 1. Problem Statement
Insert timers by expiry in sorted order.
### 2. Assumptions
- Monotonic tick source.
### 3. Full C Code
```c
#include <stdint.h>

typedef void (*timer_cb_t)(void *);

typedef struct TimerNode {
    uint32_t expiry;
    timer_cb_t cb;
    void *arg;
    struct TimerNode *next;
} TimerNode;

void timerq_insert(TimerNode **head, TimerNode *n) {
    if (!*head || n->expiry < (*head)->expiry) {
        n->next = *head;
        *head = n;
        return;
    }

    TimerNode *cur = *head;
    while (cur->next && cur->next->expiry <= n->expiry) {
        cur = cur->next;
    }
    n->next = cur->next;
    cur->next = n;
}
```
### 4. Complexity
- Insert O(n)
### 5. Interview Follow-ups
1. Wheel/heap alternatives?
2. ISR-safe insertion strategy?

## Q100: Periodic timer rescheduling without drift
### 1. Problem Statement
Keep periodic schedule aligned to original phase.
### 2. Assumptions
- `next` stores absolute tick.
### 3. Full C Code
```c
void timer_periodic_reschedule(uint32_t *next_expiry, uint32_t period) {
    *next_expiry += period;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Missed-period catch-up policy?
2. Jitter accounting?

## Q101: Race-safe timer cancellation
### 1. Problem Statement
Cancel pending timer in queue safely.
### 2. Assumptions
- External lock/critical section held.
### 3. Full C Code
```c
int timerq_cancel(TimerNode **head, TimerNode *target) {
    TimerNode *prev = NULL;
    TimerNode *cur = *head;

    while (cur) {
        if (cur == target) {
            if (prev) {
                prev->next = cur->next;
            } else {
                *head = cur->next;
            }
            return 0;
        }
        prev = cur;
        cur = cur->next;
    }
    return -1;
}
```
### 4. Complexity
- O(n)
### 5. Interview Follow-ups
1. Cancel vs callback race handling?
2. Refcounted timer object model?

## Q102: Rate Monotonic Scheduler coding
### 1. Problem Statement
Assign priorities based on period (shorter period = higher priority).
### 2. Assumptions
- Static task set.
### 3. Full C Code
```c
typedef struct {
    uint32_t period;
    uint32_t exec;
    int task_id;
} RmTask;

int rm_priority_compare(const RmTask *a, const RmTask *b) {
    if (a->period < b->period) {
        return -1;
    }
    if (a->period > b->period) {
        return 1;
    }
    return 0;
}
```
### 4. Complexity
- Comparison O(1)
### 5. Interview Follow-ups
1. Utilization bound check?
2. Harmonic periods benefit?

## Q103: Earliest Deadline First scheduler coding
### 1. Problem Statement
Run task with nearest absolute deadline.
### 2. Assumptions
- Deadlines updated dynamically.
### 3. Full C Code
```c
typedef struct {
    uint32_t abs_deadline;
    int task_id;
} EdfTask;

int edf_compare(const EdfTask *a, const EdfTask *b) {
    if (a->abs_deadline < b->abs_deadline) {
        return -1;
    }
    if (a->abs_deadline > b->abs_deadline) {
        return 1;
    }
    return 0;
}
```
### 4. Complexity
- O(1) compare
### 5. Interview Follow-ups
1. EDF overload behavior?
2. Preemption overhead implications?

## Q104: Deadline miss detection and accounting
### 1. Problem Statement
Record misses when finish tick exceeds deadline.
### 2. Assumptions
- Wrap-safe compare helper used.
### 3. Full C Code
```c
typedef struct {
    uint32_t total_jobs;
    uint32_t missed_deadlines;
} DeadlineStats;

void deadline_account(DeadlineStats *s, uint32_t finish_tick, uint32_t deadline_tick) {
    s->total_jobs++;
    if ((int32_t)(finish_tick - deadline_tick) > 0) {
        s->missed_deadlines++;
    }
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. False positives around wrap?
2. What remediation on repeated misses?

## Q105: Driver timeout wrapper pattern
### 1. Problem Statement
Wrap operation with bounded wait.
### 2. Assumptions
- `tick_now()` monotonic.
### 3. Full C Code
```c
typedef int (*op_fn_t)(void *ctx);
typedef uint32_t (*tick_fn_t)(void);

int run_with_timeout(op_fn_t op, void *ctx, tick_fn_t tick_now, uint32_t timeout_ticks) {
    uint32_t start = tick_now();
    while ((uint32_t)(tick_now() - start) < timeout_ticks) {
        if (op(ctx) == 0) {
            return 0;
        }
    }
    return -1;
}
```
### 4. Complexity
- O(timeout window)
### 5. Interview Follow-ups
1. Sleep vs busy-wait?
2. Timeout granularity selection?

## Q106: Retry logic with exponential backoff
### 1. Problem Statement
Retry transient failures with capped attempts.
### 2. Assumptions
- Backoff wait helper available.
### 3. Full C Code
```c
int retry_with_backoff(op_fn_t op, void *ctx, int max_retry) {
    uint32_t delay = 1u;

    for (int i = 0; i < max_retry; i++) {
        if (op(ctx) == 0) {
            return 0;
        }
        /* sleep_ticks(delay); */
        delay <<= 1;
    }
    return -1;
}
```
### 4. Complexity
- O(retries)
### 5. Interview Follow-ups
1. Add jitter to avoid thundering herd?
2. Distinguish transient vs fatal errors?

## Q107: Driver reset/reinit sequence on failure
### 1. Problem Statement
Recover peripheral after repeated failures.
### 2. Assumptions
- Stop/reset/init callbacks provided.
### 3. Full C Code
```c
typedef void (*void_fn_t)(void *);

void driver_recover(void *ctx, void_fn_t stop, void_fn_t hw_reset, void_fn_t init) {
    stop(ctx);
    hw_reset(ctx);
    init(ctx);
}
```
### 4. Complexity
- O(reinit_work)
### 5. Interview Follow-ups
1. What to do with in-flight buffers?
2. How many resets before fatal error?

## Q108: Fault-tolerant driver state machine
### 1. Problem Statement
Model robust state transitions with error state.
### 2. Assumptions
- Events represented by small enum.
### 3. Full C Code
```c
typedef enum {
    DRV_ST_INIT,
    DRV_ST_IDLE,
    DRV_ST_BUSY,
    DRV_ST_ERR
} DrvState;

typedef enum {
    EV_INIT_OK,
    EV_START,
    EV_DONE,
    EV_FAIL,
    EV_RESET
} DrvEvent;

DrvState drv_step(DrvState s, DrvEvent e) {
    switch (s) {
        case DRV_ST_INIT:
            return (e == EV_INIT_OK) ? DRV_ST_IDLE : DRV_ST_INIT;
        case DRV_ST_IDLE:
            return (e == EV_START) ? DRV_ST_BUSY : DRV_ST_IDLE;
        case DRV_ST_BUSY:
            if (e == EV_DONE) return DRV_ST_IDLE;
            if (e == EV_FAIL) return DRV_ST_ERR;
            return DRV_ST_BUSY;
        case DRV_ST_ERR:
            return (e == EV_RESET) ? DRV_ST_INIT : DRV_ST_ERR;
        default:
            return DRV_ST_ERR;
    }
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Illegal transition handling policy?
2. State-specific timeout actions?
