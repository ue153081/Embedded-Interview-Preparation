# Advanced Timer Scheduling Techniques (Embedded Systems)

This document explains three common timer scheduling techniques used in
operating systems and high‑performance embedded systems.

Methods covered:

1.  **Min‑Heap Timer Scheduler**
2.  **Timer Wheel Scheduler**
3.  **Calendar Queue Scheduler**

Each section includes:

-   Overview
-   Architecture
-   Design explanation
-   C implementation
-   Performance notes
-   Interview follow‑up questions with answers

  -----------------------------------------------------------------------
  \# 1. MIN‑HEAP TIMER SCHEDULER
  -----------------------------------------------------------------------
  \## DATA STRUCTURES

  \`\`\`c #include \<stdint.h\> #include \<stddef.h\>

  #define MAX_TIMERS 128

  typedef void (*timer_callback_t)(void *arg);

  typedef struct { uint32_t expiry; timer_callback_t cb; void \*arg;

  } Timer;

  typedef struct { Timer heap\[MAX_TIMERS\]; size_t size;

  } TimerHeap; \`\`\`
  -----------------------------------------------------------------------

## HEAP HELPERS

``` c
static void swap(Timer *a, Timer *b)
{
    Timer tmp = *a;
    *a = *b;
    *b = tmp;
}
```

### Heapify Up

``` c
static void heapify_up(TimerHeap *h, int idx)
{
    while(idx > 0)
    {
        int parent = (idx - 1) / 2;

        if(h->heap[parent].expiry <= h->heap[idx].expiry)
            break;

        swap(&h->heap[parent], &h->heap[idx]);

        idx = parent;
    }
}
```

### Heapify Down

``` c
static void heapify_down(TimerHeap *h, int idx)
{
    while(1)
    {
        int left = idx * 2 + 1;
        int right = idx * 2 + 2;
        int smallest = idx;

        if(left < h->size &&
           h->heap[left].expiry < h->heap[smallest].expiry)
            smallest = left;

        if(right < h->size &&
           h->heap[right].expiry < h->heap[smallest].expiry)
            smallest = right;

        if(smallest == idx)
            break;

        swap(&h->heap[idx], &h->heap[smallest]);

        idx = smallest;
    }
}
```

  -----------------------------------------------------------------------
  \## ADD TIMER
  -----------------------------------------------------------------------
  \## PROCESS TIMERS

  \`\`\`c void timer_heap_process(TimerHeap \*h, uint32_t now) {
  while(h-\>size \> 0 && h-\>heap\[0\].expiry \<= now) { Timer t =
  h-\>heap\[0\];

  t.cb(t.arg);

  h-\>heap\[0\] = h-\>heap\[--h-\>size\];

  heapify_down(h, 0); } } \`\`\`
  -----------------------------------------------------------------------

## INTERVIEW QUESTIONS

Q: Why is a min‑heap useful for timers?\
A: It keeps the earliest timer at the root so it can be accessed
quickly.

Q: Complexity of operations?

Insert → O(log N)\
Remove → O(log N)\
Peek → O(1)

  -----------------------------------------------------------------------
  \# 2. TIMER WHEEL SCHEDULER
  -----------------------------------------------------------------------
  \## ARCHITECTURE

  Example wheel (size = 8)

  \[0\] \[1\] \[2\] \[3\] \[4\] \[5\] \[6\] \[7\] \^ current slot

  Every timer tick moves to the next slot.
  -----------------------------------------------------------------------

## DATA STRUCTURES

``` c
#define WHEEL_SIZE 256

typedef struct TimerNode
{
    uint32_t expiry;
    timer_callback_t cb;
    void *arg;

    struct TimerNode *next;

} TimerNode;

typedef struct
{
    TimerNode *slots[WHEEL_SIZE];

    uint32_t current_slot;

} TimerWheel;
```

  -----------------------------------------------------------------------
  \## ADD TIMER
  -----------------------------------------------------------------------
  \## PROCESS TICK

  \`\`\`c void timer_wheel_tick(TimerWheel *wheel) { TimerNode *node =
  wheel-\>slots\[wheel-\>current_slot\];

  while(node) { node-\>cb(node-\>arg);

  node = node-\>next; }

  wheel-\>slots\[wheel-\>current_slot\] = NULL;

  wheel-\>current_slot = (wheel-\>current_slot + 1) % WHEEL_SIZE; }
  \`\`\`
  -----------------------------------------------------------------------

## INTERVIEW QUESTIONS

Q: Advantage of timer wheel?\
A: O(1) timer insertion and processing.

Q: Disadvantage?\
A: Limited time resolution.

  -----------------------------------------------------------------------
  \# 3. CALENDAR QUEUE SCHEDULER
  -----------------------------------------------------------------------
  \## DATA STRUCTURES

  \`\`\`c #define CAL_BUCKETS 64

  typedef struct CalNode { uint32_t expiry;

  timer_callback_t cb;

  void \*arg;

  struct CalNode \*next;

  } CalNode;

  typedef struct { CalNode \*buckets\[CAL_BUCKETS\];

  uint32_t current_time;

  } CalendarQueue; \`\`\`
  -----------------------------------------------------------------------

## INSERT TIMER

``` c
void calendar_add(CalendarQueue *q,
                  CalNode *node)
{
    uint32_t bucket =
        node->expiry % CAL_BUCKETS;

    node->next = q->buckets[bucket];

    q->buckets[bucket] = node;
}
```

  -----------------------------------------------------------------------
  \## PROCESS TIMERS
  -----------------------------------------------------------------------
  \## INTERVIEW QUESTIONS

  Q: Difference between timer wheel and calendar queue?

  Timer wheel → fixed slots Calendar queue → dynamic distribution of
  timers

  Q: Complexity?

  Average O(1) operations.
  -----------------------------------------------------------------------

# COMPARISON

## Method Insert Process Best Use

Min Heap O(log N) O(log N) OS schedulers Timer Wheel O(1) O(1)
networking Calendar Queue O(1) avg O(1) avg large timer systems
