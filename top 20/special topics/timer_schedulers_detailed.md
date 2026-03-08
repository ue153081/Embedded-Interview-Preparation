# Advanced Timer Schedulers - Detailed Implementations

This file contains detailed, interview-ready implementations for one simple baseline scheduler plus three advanced timer schedulers used in embedded and systems software.

Included implementations:

1. `simple_linear_timer_scheduler_full.c` (O(N) scan, baseline from top-10 Q9)
2. `min_heap_timer_scheduler_full.c`
3. `timer_wheel_scheduler_full.c`
4. `calendar_queue_scheduler_full.c`

Each section includes:

- Overview
- Architecture
- Design principles
- Full C implementation
- Performance notes
- Race condition analysis
- Interview discussion questions with answers

## 0_simple_linear_timer_scheduler_full.c

```c
/*****************************************************************************************
 *
 *  SIMPLE LINEAR TIMER SCHEDULER (O(N) PER TICK)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  This is the baseline software timer approach used in top-10 problem 9.
 *
 *  Idea:
 *      * Keep timers in a fixed array
 *      * Increment global tick in timer ISR
 *      * Scan all active timers each tick
 *
 *  It is simple, predictable, and very common in small embedded systems.
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      HARDWARE TIMER IRQ
 *             |
 *             v
 *         tick++
 *             |
 *             v
 *    for each active timer:
 *       if tick >= expiry:
 *           callback()
 *           reschedule periodic or disable one-shot
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Fixed memory footprint (no dynamic allocation).
 *  2. O(1) create/stop average with free-slot search.
 *  3. O(N) per tick timer scan.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

#define SIMPLE_MAX_TIMERS 32u

typedef void (*simple_timer_callback_t)(void *arg);

typedef struct
{
    uint32_t expiry;
    uint32_t period;

    simple_timer_callback_t callback;
    void *arg;

    uint8_t active;
} SimpleTimer;

typedef struct
{
    SimpleTimer timers[SIMPLE_MAX_TIMERS];
    volatile uint32_t tick;
} SimpleTimerScheduler;

void simple_timer_scheduler_init(SimpleTimerScheduler *sched)
{
    uint32_t i;

    sched->tick = 0u;

    for (i = 0u; i < SIMPLE_MAX_TIMERS; i++)
        sched->timers[i].active = 0u;
}

int simple_timer_create(SimpleTimerScheduler *sched,
                        uint32_t delay,
                        uint32_t period,
                        simple_timer_callback_t cb,
                        void *arg)
{
    uint32_t i;

    if (cb == NULL)
        return -1;

    for (i = 0u; i < SIMPLE_MAX_TIMERS; i++)
    {
        if (!sched->timers[i].active)
        {
            SimpleTimer *t = &sched->timers[i];

            t->expiry = sched->tick + delay;
            t->period = period;
            t->callback = cb;
            t->arg = arg;
            t->active = 1u;

            return (int)i;
        }
    }

    return -1;
}

void simple_timer_stop(SimpleTimerScheduler *sched, int id)
{
    if (id < 0 || (uint32_t)id >= SIMPLE_MAX_TIMERS)
        return;

    sched->timers[(uint32_t)id].active = 0u;
}

void simple_timer_tick_isr(SimpleTimerScheduler *sched)
{
    uint32_t i;

    sched->tick++;

    for (i = 0u; i < SIMPLE_MAX_TIMERS; i++)
    {
        SimpleTimer *t = &sched->timers[i];

        if (!t->active)
            continue;

        if (sched->tick >= t->expiry)
        {
            t->callback(t->arg);

            if (t->period != 0u)
                t->expiry += t->period;
            else
                t->active = 0u;
        }
    }
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Tick cost is O(N) due to full array scan.
 *
 *  This is acceptable for:
 *      * Small timer counts
 *      * Low tick rates
 *      * Simpler firmware with deterministic structure
 *
 *  For larger timer sets, min-heap or timer wheel usually scales better.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  tick ISR may run concurrently with create/stop calls.
 *
 *  Protection options:
 *      * Disable timer IRQ briefly during create/stop
 *      * Use atomic fields for active/expiry updates
 *      * Queue timer commands and apply in single owner context
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why is this scheduler O(N)?
 *
 *    Because each tick iterates through all timer slots, active or inactive.
 *
 * 2. Why is it still used in embedded products?
 *
 *    It is easy to reason about, low-risk, and efficient enough at small scale.
 *
 * 3. What is the biggest downside?
 *
 *    CPU cost grows linearly with timer count and tick frequency.
 *
 * 4. When should we move away from this design?
 *
 *    When tick ISR load becomes significant or timer count grows substantially.
 *
 * 5. How do periodic timers work here?
 *
 *    After firing, expiry is incremented by fixed period instead of disabling.
 *
 *****************************************************************************************/
```

## 1_min_heap_timer_scheduler_full.c

```c
/*****************************************************************************************
 *
 *  MIN-HEAP TIMER SCHEDULER (PRIORITY QUEUE BY EXPIRY)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  A min-heap keeps the earliest timer at index 0.
 *
 *  Why this is useful:
 *      * Fast lookup of next deadline (O(1) peek)
 *      * Efficient insertion/removal (O(log N))
 *      * Good fit for general-purpose event loops
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      add_timer() ---> heapify_up()
 *                             |
 *                             v
 *                       heap[0] = earliest expiry
 *                             |
 *                             v
 *                   process_due(now) + heapify_down()
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Strict ordering by expiry tick.
 *  2. Stable tie-break using monotonic timer ID.
 *  3. Wrap-safe time comparison for uint32 ticks.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

#define HEAP_MAX_TIMERS 256u

typedef void (*timer_callback_t)(void *arg);

typedef struct
{
    uint32_t expiry;
    uint32_t id;
    timer_callback_t cb;
    void *arg;
} HeapTimer;

typedef struct
{
    HeapTimer heap[HEAP_MAX_TIMERS];
    size_t size;
    uint32_t next_id;
} TimerHeap;

/* True if a occurs before b in wrap-safe 32-bit time domain. */
static int time_before_u32(uint32_t a, uint32_t b)
{
    return (int32_t)(a - b) < 0;
}

static int timer_less(const HeapTimer *a, const HeapTimer *b)
{
    if (a->expiry == b->expiry)
        return a->id < b->id;

    return time_before_u32(a->expiry, b->expiry);
}

static void heap_swap(HeapTimer *a, HeapTimer *b)
{
    HeapTimer t = *a;
    *a = *b;
    *b = t;
}

static void heapify_up(TimerHeap *h, size_t idx)
{
    while (idx > 0u)
    {
        size_t parent = (idx - 1u) / 2u;

        if (!timer_less(&h->heap[idx], &h->heap[parent]))
            break;

        heap_swap(&h->heap[idx], &h->heap[parent]);
        idx = parent;
    }
}

static void heapify_down(TimerHeap *h, size_t idx)
{
    while (1)
    {
        size_t left = (idx * 2u) + 1u;
        size_t right = left + 1u;
        size_t smallest = idx;

        if (left < h->size && timer_less(&h->heap[left], &h->heap[smallest]))
            smallest = left;

        if (right < h->size && timer_less(&h->heap[right], &h->heap[smallest]))
            smallest = right;

        if (smallest == idx)
            break;

        heap_swap(&h->heap[idx], &h->heap[smallest]);
        idx = smallest;
    }
}

void timer_heap_init(TimerHeap *h)
{
    h->size = 0u;
    h->next_id = 1u;
}

int timer_heap_add(TimerHeap *h,
                   uint32_t expiry,
                   timer_callback_t cb,
                   void *arg,
                   uint32_t *out_id)
{
    HeapTimer t;

    if (h->size >= HEAP_MAX_TIMERS || cb == NULL)
        return -1;

    t.expiry = expiry;
    t.id = h->next_id++;
    t.cb = cb;
    t.arg = arg;

    h->heap[h->size] = t;
    heapify_up(h, h->size);
    h->size++;

    if (out_id != NULL)
        *out_id = t.id;

    return 0;
}

int timer_heap_peek_next(const TimerHeap *h, HeapTimer *out)
{
    if (h->size == 0u)
        return -1;

    if (out != NULL)
        *out = h->heap[0];

    return 0;
}

static int timer_due(uint32_t now, uint32_t expiry)
{
    return !time_before_u32(now, expiry);
}

int timer_heap_pop(TimerHeap *h, HeapTimer *out)
{
    if (h->size == 0u)
        return -1;

    if (out != NULL)
        *out = h->heap[0];

    h->size--;
    if (h->size > 0u)
    {
        h->heap[0] = h->heap[h->size];
        heapify_down(h, 0u);
    }

    return 0;
}

/* budget limits callback burst to keep loop responsive. budget==0 means unlimited. */
uint32_t timer_heap_process_due(TimerHeap *h, uint32_t now, uint32_t budget)
{
    uint32_t processed = 0u;

    while (h->size > 0u)
    {
        HeapTimer t = h->heap[0];

        if (!timer_due(now, t.expiry))
            break;

        if (budget != 0u && processed >= budget)
            break;

        (void)timer_heap_pop(h, NULL);
        t.cb(t.arg);
        processed++;
    }

    return processed;
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Insert: O(log N)
 *  Pop due: O(log N) each
 *  Peek next: O(1)
 *
 *  Good for broad timer ranges and sparse expiries.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  Heap operations mutate shared array and size.
 *
 *  If called from ISR + thread contexts, protect with:
 *      * Critical section / interrupt masking
 *      * Or single-owner thread + command queue model
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why use a min-heap for timers?
 *
 *    It keeps earliest expiry at root, so next deadline lookup is O(1).
 *
 * 2. Why not a sorted linked list?
 *
 *    Sorted list has O(N) insertion, which is expensive for large timer sets.
 *
 * 3. Why tie-break by timer ID?
 *
 *    It provides deterministic ordering when expiries are equal.
 *
 * 4. What does wrap-safe comparison solve?
 *
 *    It prevents incorrect ordering when uint32 tick counter overflows.
 *
 * 5. Why use callback budget in processing loop?
 *
 *    It prevents long callback bursts from starving other event-loop work.
 *
 *****************************************************************************************/
```

## 2_timer_wheel_scheduler_full.c

```c
/*****************************************************************************************
 *
 *  TIMER WHEEL SCHEDULER (O(1)-STYLE SLOT BUCKETING)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  Timer wheel maps timers into cyclic slots.
 *
 *  Characteristics:
 *      * Very fast insertion in many workloads
 *      * Excellent for high timer churn with moderate resolution needs
 *      * Works well in networking and embedded periodic systems
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      slots[0 ... WHEEL_SIZE-1], current_slot advances every tick.
 *
 *      Each timer stores:
 *          * target slot
 *          * remaining rounds (full wheel revolutions before firing)
 *
 *      On each tick:
 *          * advance current_slot
 *          * process linked list in that slot
 *          * fire nodes with rounds == 0, else rounds--
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Allocation-free runtime via static node pool.
 *  2. Deterministic ISR-safe tick path.
 *  3. Overrun-free list operations with clear ownership.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

#define WHEEL_SIZE 256u
#define WHEEL_MAX_TIMERS 256u

typedef void (*timer_callback_t)(void *arg);

typedef struct TimerWheelNode
{
    uint32_t rounds;
    timer_callback_t cb;
    void *arg;

    struct TimerWheelNode *next;
    uint8_t in_use;
} TimerWheelNode;

typedef struct
{
    TimerWheelNode *slots[WHEEL_SIZE];

    TimerWheelNode nodes[WHEEL_MAX_TIMERS];
    TimerWheelNode *free_list;

    uint32_t now_tick;
    uint32_t current_slot;

    uint32_t dropped;
} TimerWheel;

static TimerWheelNode *tw_alloc_node(TimerWheel *w)
{
    TimerWheelNode *n = w->free_list;

    if (n == NULL)
        return NULL;

    w->free_list = n->next;
    n->next = NULL;
    n->in_use = 1u;
    return n;
}

static void tw_free_node(TimerWheel *w, TimerWheelNode *n)
{
    n->cb = NULL;
    n->arg = NULL;
    n->rounds = 0u;
    n->in_use = 0u;

    n->next = w->free_list;
    w->free_list = n;
}

void timer_wheel_init(TimerWheel *w)
{
    uint32_t i;

    for (i = 0u; i < WHEEL_SIZE; i++)
        w->slots[i] = NULL;

    w->free_list = NULL;

    for (i = 0u; i < WHEEL_MAX_TIMERS; i++)
    {
        w->nodes[i].next = w->free_list;
        w->nodes[i].in_use = 0u;
        w->free_list = &w->nodes[i];
    }

    w->now_tick = 0u;
    w->current_slot = 0u;
    w->dropped = 0u;
}

/* delay_ticks==0 schedules for next tick to keep tick semantics deterministic. */
int timer_wheel_add(TimerWheel *w,
                    uint32_t delay_ticks,
                    timer_callback_t cb,
                    void *arg)
{
    TimerWheelNode *n;
    uint32_t ticks;
    uint32_t rem;
    uint32_t rounds;
    uint32_t slot;

    if (cb == NULL)
        return -1;

    ticks = (delay_ticks == 0u) ? 1u : delay_ticks;

    n = tw_alloc_node(w);
    if (n == NULL)
    {
        w->dropped++;
        return -1;
    }

    rem = ticks % WHEEL_SIZE;
    rounds = ticks / WHEEL_SIZE;
    slot = (w->current_slot + rem) % WHEEL_SIZE;

    if (slot == w->current_slot && rounds > 0u)
        rounds--;

    n->rounds = rounds;
    n->cb = cb;
    n->arg = arg;

    n->next = w->slots[slot];
    w->slots[slot] = n;

    return 0;
}

void timer_wheel_tick(TimerWheel *w)
{
    TimerWheelNode **pp;

    w->now_tick++;
    w->current_slot = (w->current_slot + 1u) % WHEEL_SIZE;

    pp = &w->slots[w->current_slot];

    while (*pp != NULL)
    {
        TimerWheelNode *n = *pp;

        if (n->rounds == 0u)
        {
            timer_callback_t cb = n->cb;
            void *arg = n->arg;

            *pp = n->next;
            tw_free_node(w, n);

            cb(arg);
        }
        else
        {
            n->rounds--;
            pp = &n->next;
        }
    }
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Add timer: O(1) average
 *  Tick processing: O(k) where k is timers in current slot
 *
 *  Tradeoff:
 *      * Great constant-time behavior
 *      * Granularity tied to tick and wheel size
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  Slot lists and free list are mutable shared state.
 *
 *  If add/tick occur from different contexts, protect with critical section or
 *  queue add requests and apply from a single scheduler context.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why can timer wheel be faster than heap?
 *
 *    Insertion is typically O(1) and does not require heap reordering.
 *
 * 2. What does rounds represent?
 *
 *    Number of full wheel cycles remaining before timer fires.
 *
 * 3. What is the main limitation?
 *
 *    Resolution and max-delay granularity depend on wheel configuration.
 *
 * 4. Why use static node pool?
 *
 *    Avoids malloc in real-time paths and gives predictable memory behavior.
 *
 * 5. How to support very long delays efficiently?
 *
 *    Use hierarchical timer wheels (multiple levels of wheels).
 *
 *****************************************************************************************/
```

## 3_calendar_queue_scheduler_full.c

```c
/*****************************************************************************************
 *
 *  CALENDAR QUEUE TIMER SCHEDULER (BUCKETED TIME PRIORITY QUEUE)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  Calendar queue maps expiry times into time buckets (like a hashed priority queue).
 *
 *  Goal:
 *      * Near O(1) average insert/remove under good timer distribution
 *
 *  Typical use:
 *      * Large timer populations with broad time spread
 *      * Simulation/event systems and high-scale scheduling
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      bucket = (expiry / bucket_width) % CAL_BUCKETS
 *
 *      Each bucket is a sorted linked list by expiry.
 *
 *      On tick:
 *          * advance current_time
 *          * process current bucket
 *          * fire all timers with expiry <= current_time
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Time-domain bucketing to reduce global ordering cost.
 *  2. Sorted list per bucket for cheap due extraction.
 *  3. Static memory pool for deterministic allocation.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

#define CAL_BUCKETS 64u
#define CAL_MAX_TIMERS 256u

typedef void (*timer_callback_t)(void *arg);

typedef struct CalNode
{
    uint32_t expiry;
    timer_callback_t cb;
    void *arg;

    struct CalNode *next;
    uint8_t in_use;
} CalNode;

typedef struct
{
    CalNode *buckets[CAL_BUCKETS];

    CalNode nodes[CAL_MAX_TIMERS];
    CalNode *free_list;

    uint32_t current_time;
    uint32_t bucket_width;

    uint32_t dropped;
} CalendarQueue;

/* Wrap-safe compare: a before b. */
static int cq_time_before(uint32_t a, uint32_t b)
{
    return (int32_t)(a - b) < 0;
}

static int cq_time_due(uint32_t now, uint32_t expiry)
{
    return !cq_time_before(now, expiry);
}

static uint32_t cq_bucket_index(const CalendarQueue *q, uint32_t expiry)
{
    return (expiry / q->bucket_width) % CAL_BUCKETS;
}

static CalNode *cq_alloc_node(CalendarQueue *q)
{
    CalNode *n = q->free_list;

    if (n == NULL)
        return NULL;

    q->free_list = n->next;
    n->next = NULL;
    n->in_use = 1u;
    return n;
}

static void cq_free_node(CalendarQueue *q, CalNode *n)
{
    n->cb = NULL;
    n->arg = NULL;
    n->expiry = 0u;
    n->in_use = 0u;

    n->next = q->free_list;
    q->free_list = n;
}

void calendar_queue_init(CalendarQueue *q, uint32_t bucket_width)
{
    uint32_t i;

    if (bucket_width == 0u)
        bucket_width = 1u;

    for (i = 0u; i < CAL_BUCKETS; i++)
        q->buckets[i] = NULL;

    q->free_list = NULL;

    for (i = 0u; i < CAL_MAX_TIMERS; i++)
    {
        q->nodes[i].next = q->free_list;
        q->nodes[i].in_use = 0u;
        q->free_list = &q->nodes[i];
    }

    q->current_time = 0u;
    q->bucket_width = bucket_width;
    q->dropped = 0u;
}

/* Insert node into bucket sorted by expiry time. */
static void cq_insert_sorted(CalNode **head, CalNode *node)
{
    CalNode **pp = head;

    while (*pp != NULL && !cq_time_before(node->expiry, (*pp)->expiry))
        pp = &(*pp)->next;

    node->next = *pp;
    *pp = node;
}

int calendar_queue_add_abs(CalendarQueue *q,
                           uint32_t expiry,
                           timer_callback_t cb,
                           void *arg)
{
    CalNode *n;
    uint32_t idx;

    if (cb == NULL)
        return -1;

    n = cq_alloc_node(q);
    if (n == NULL)
    {
        q->dropped++;
        return -1;
    }

    n->expiry = expiry;
    n->cb = cb;
    n->arg = arg;

    idx = cq_bucket_index(q, expiry);
    cq_insert_sorted(&q->buckets[idx], n);

    return 0;
}

int calendar_queue_add_after(CalendarQueue *q,
                             uint32_t delay,
                             timer_callback_t cb,
                             void *arg)
{
    return calendar_queue_add_abs(q, q->current_time + delay, cb, arg);
}

void calendar_queue_tick(CalendarQueue *q)
{
    uint32_t idx;
    CalNode **pp;

    q->current_time++;
    idx = cq_bucket_index(q, q->current_time);
    pp = &q->buckets[idx];

    while (*pp != NULL)
    {
        CalNode *n = *pp;

        if (!cq_time_due(q->current_time, n->expiry))
            break;

        {
            timer_callback_t cb = n->cb;
            void *arg = n->arg;

            *pp = n->next;
            cq_free_node(q, n);

            cb(arg);
        }
    }
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Average insert/remove can approach O(1) with good bucket width and timer distribution.
 *
 *  Worst-case degrades if many timers collide in the same bucket.
 *
 *  In production systems, bucket_width is often adapted dynamically.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  Buckets and free list are mutable shared structures.
 *
 *  Same protection model as other schedulers applies:
 *      * Single scheduler owner thread/task, or
 *      * Critical sections around add/tick operations
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. How is calendar queue different from timer wheel?
 *
 *    Both bucket by time, but calendar queue targets average priority-queue behavior
 *    with bucketed ordering rather than fixed-slot round counters.
 *
 * 2. Why sort nodes inside each bucket?
 *
 *    It allows early stop during processing once first not-due timer is reached.
 *
 * 3. What parameter most affects performance?
 *
 *    bucket_width: too small or too large increases bucket imbalance.
 *
 * 4. When does performance degrade?
 *
 *    When many expiries hash to same bucket, causing long list traversal.
 *
 * 5. Why keep add_abs and add_after APIs?
 *
 *    Absolute deadlines simplify integration with external clocks, while relative
 *    delays are convenient for application scheduling.
 *
 *****************************************************************************************/
```

## Quick Comparison

| Method | Insert | Process Due | Best Use |
|---|---|---|---|
| Simple Linear Scan | O(1) avg create, O(N) tick | O(N) each tick | Small embedded systems, low timer counts |
| Min-Heap | O(log N) | O(log N) each due timer | General-purpose event loops |
| Timer Wheel | O(1) avg | O(k) for current slot | High-throughput periodic systems |
| Calendar Queue | O(1) avg | O(1) avg / collision-dependent | Large timer populations with spread expiries |
