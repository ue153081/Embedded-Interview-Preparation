# Additional 10 Questions - Combined C Sources

This file contains the full content of every missing `.c` file for questions `11` through `20`.

## 11_memcpy_implementation_full.c

```c
/*****************************************************************************************
 *
 *  MEMCPY IMPLEMENTATION (EMBEDDED-ORIENTED VERSION)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  memcpy copies N bytes from source memory to destination memory.
 *
 *  Common embedded use-cases:
 *      * Copy RX DMA buffers into processing buffers
 *      * Build TX packets in protocol stacks
 *      * Move sensor snapshots into logging regions
 *
 *  Important rule:
 *      memcpy assumes source and destination DO NOT overlap.
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      SOURCE POINTER  ->  COPY ENGINE  ->  DESTINATION POINTER
 *
 *      src:  [A B C D E F]
 *      dst:  [_ _ _ _ _ _]
 *
 *      result:
 *      src:  [A B C D E F]
 *      dst:  [A B C D E F]
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Correctness first
 *      Byte-for-byte exact copy for all N.
 *
 *  2. Alignment-aware fast path
 *      If pointers are aligned, copy machine words (size_t) instead of bytes.
 *
 *  3. Tail-byte cleanup
 *      Copy remaining bytes after word loop.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

void *my_memcpy(void *dest, const void *src, size_t n)
{
    uint8_t *d = (uint8_t *)dest;
    const uint8_t *s = (const uint8_t *)src;

    if (dest == src || n == 0u)
        return dest;

    /* Align both pointers so we can copy full machine words safely. */
    while (n > 0u &&
           ((((uintptr_t)d & (sizeof(size_t) - 1u)) != 0u) ||
            (((uintptr_t)s & (sizeof(size_t) - 1u)) != 0u)))
    {
        *d++ = *s++;
        n--;
    }

    /* Fast path: copy word-sized chunks. */
    {
        size_t *dw = (size_t *)d;
        const size_t *sw = (const size_t *)s;

        while (n >= sizeof(size_t))
        {
            *dw++ = *sw++;
            n -= sizeof(size_t);
        }

        d = (uint8_t *)dw;
        s = (const uint8_t *)sw;
    }

    /* Tail bytes. */
    while (n > 0u)
    {
        *d++ = *s++;
        n--;
    }

    return dest;
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Typical production optimizations:
 *      * Wider vector instructions (SIMD)
 *      * Loop unrolling
 *      * Non-temporal stores for large blocks
 *
 *  For small embedded MCUs, the above implementation is often a good tradeoff
 *  between readability and speed.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  memcpy itself has no global shared state.
 *
 *  Races can still happen if another context (ISR/task/DMA) writes to src/dest
 *  while copy is in progress.
 *
 *  Protection strategies:
 *      * Use critical sections
 *      * Copy from immutable buffers
 *      * Coordinate producer/consumer ownership
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why does memcpy not support overlapping regions?
 *
 *    Because forward-copy semantics can overwrite source bytes before they
 *    are read. Overlap-safe behavior belongs to memmove.
 *
 * 2. Why copy words instead of bytes?
 *
 *    Word copies reduce loop iterations and improve throughput on aligned data.
 *
 * 3. Why do we still need a byte loop?
 *
 *    To handle unaligned prefixes and trailing bytes not divisible by word size.
 *
 * 4. Is memcpy deterministic for real-time systems?
 *
 *    Yes in algorithmic complexity (O(N)), but exact cycle count depends on
 *    alignment, memory wait states, and bus contention.
 *
 * 5. What is a common embedded bug around memcpy?
 *
 *    Passing incorrect length (bytes vs elements), causing overflow or truncation.
 *
 *****************************************************************************************/
```

## 12_memmove_implementation_full.c

```c
/*****************************************************************************************
 *
 *  MEMMOVE IMPLEMENTATION (OVERLAP-SAFE COPY)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  memmove copies N bytes while safely handling overlapping source and destination.
 *
 *  If regions overlap, copy direction matters:
 *      * Forward copy when destination starts before source
 *      * Backward copy when destination starts inside/after source region
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *  Case A (no hazardous overlap):
 *      dest < src       -> forward copy
 *
 *  Case B (hazardous overlap):
 *      dest > src       -> backward copy
 *
 *  Example overlap:
 *      buffer: [A B C D E F]
 *      move(buffer + 1, buffer, 5)
 *
 *      backward copy avoids clobbering unread source bytes.
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Direction is chosen from pointer relationship.
 *  2. Same byte-for-byte result as if data were copied through a temporary array.
 *  3. Keep implementation branch-simple for predictable behavior.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

void *my_memmove(void *dest, const void *src, size_t n)
{
    uint8_t *d = (uint8_t *)dest;
    const uint8_t *s = (const uint8_t *)src;

    if (dest == src || n == 0u)
        return dest;

    if (d < s || d >= (s + n))
    {
        /* Safe to copy forward. */
        for (size_t i = 0u; i < n; i++)
            d[i] = s[i];
    }
    else
    {
        /* Overlap hazard: copy backward. */
        for (size_t i = n; i > 0u; i--)
            d[i - 1u] = s[i - 1u];
    }

    return dest;
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  memmove may be slightly slower than memcpy due to overlap checks and possible
 *  backward copy path.
 *
 *  For large transfers, optimized libraries still use word/vector copies in both
 *  directions, with alignment-aware prologue/epilogue handling.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  Same as memcpy: no global state, but caller must guarantee that concurrent
 *  writers do not mutate source/destination during transfer.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. When should you use memmove over memcpy?
 *
 *    Use memmove when there is any chance of overlapping memory regions.
 *
 * 2. Why backward copy for overlap?
 *
 *    It preserves unread source bytes by consuming from the end first.
 *
 * 3. Can memmove replace memcpy everywhere?
 *
 *    Yes functionally, but memcpy can be faster when overlap is impossible.
 *
 * 4. Is memmove complexity still O(N)?
 *
 *    Yes, both forward and backward paths are linear in byte count.
 *
 * 5. What embedded case commonly needs memmove?
 *
 *    In-place packet compaction where headers are removed from a receive buffer.
 *
 *****************************************************************************************/
```

## 13_bit_manipulation_library_full.c

```c
/*****************************************************************************************
 *
 *  BIT MANIPULATION LIBRARY (REGISTER-LEVEL UTILITIES)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  Embedded peripherals are controlled through memory-mapped bit fields.
 *
 *  Common operations:
 *      * Set/clear/toggle bits
 *      * Read single-bit status flags
 *      * Update multi-bit fields without disturbing neighbors
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      register (32-bit): [31 ... 8][7 6 5 4][3 2 1 0]
 *                               field A    field B
 *
 *      write field A:
 *          reg = (reg & ~maskA) | ((value << shiftA) & maskA)
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Keep APIs explicit about masks/shifts.
 *  2. Avoid duplicate ad-hoc bit-twiddling at call sites.
 *  3. Make read-modify-write intent obvious.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

#define BIT_U32(n)        (1u << (n))
#define FIELD_PREP(mask, value, shift)   (((uint32_t)(value) << (shift)) & (mask))
#define FIELD_GET(mask, reg, shift)      (((uint32_t)(reg) & (mask)) >> (shift))

typedef volatile uint32_t vuint32_t;

void reg_set_bit(vuint32_t *reg, uint8_t bit)
{
    *reg |= BIT_U32(bit);
}

void reg_clear_bit(vuint32_t *reg, uint8_t bit)
{
    *reg &= ~BIT_U32(bit);
}

void reg_toggle_bit(vuint32_t *reg, uint8_t bit)
{
    *reg ^= BIT_U32(bit);
}

uint8_t reg_read_bit(uint32_t reg, uint8_t bit)
{
    return (uint8_t)((reg >> bit) & 0x1u);
}

void reg_write_field(vuint32_t *reg,
                     uint32_t mask,
                     uint8_t shift,
                     uint32_t value)
{
    uint32_t tmp = *reg;
    tmp &= ~mask;
    tmp |= FIELD_PREP(mask, value, shift);
    *reg = tmp;
}

uint32_t reg_read_field(uint32_t reg,
                        uint32_t mask,
                        uint8_t shift)
{
    return FIELD_GET(mask, reg, shift);
}


/*****************************************************************************************
 * EXAMPLE PERIPHERAL AND USE
 *****************************************************************************************/

typedef struct
{
    vuint32_t CR;
    vuint32_t SR;
} UART_Regs;

#define UART_CR_EN_BIT       0u
#define UART_CR_PARITY_BIT   1u
#define UART_CR_STOP_MASK    (0x3u << 2)
#define UART_CR_STOP_SHIFT   2u

void uart_config(UART_Regs *u)
{
    reg_set_bit(&u->CR, UART_CR_EN_BIT);
    reg_set_bit(&u->CR, UART_CR_PARITY_BIT);
    reg_write_field(&u->CR, UART_CR_STOP_MASK, UART_CR_STOP_SHIFT, 0x1u);
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Read-modify-write costs an extra load/store cycle.
 *
 *  Many MCUs provide atomic set/clear registers (e.g., GPIOx_BSRR style) to avoid
 *  RMW hazards and reduce latency.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  RMW is vulnerable if ISR and task modify the same register concurrently.
 *
 *  Protection options:
 *      * Disable interrupts around critical writes
 *      * Use atomic set/clear hardware registers when available
 *      * Centralize ownership per register block
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why is volatile used for hardware registers?
 *
 *    Because hardware can change values asynchronously; compiler must not cache them.
 *
 * 2. Why avoid literal magic numbers at call sites?
 *
 *    Named masks/shifts prevent mistakes and improve maintainability.
 *
 * 3. What is the RMW race problem?
 *
 *    Two contexts read same old value, each writes a different update, and one update
 *    gets lost.
 *
 * 4. Why use helper macros like FIELD_PREP/FIELD_GET?
 *
 *    They standardize field encoding and reduce shift/mask bugs.
 *
 * 5. When is bit-banding useful (if supported)?
 *
 *    For atomic single-bit operations without full-register RMW.
 *
 *****************************************************************************************/
```

## 14_circular_buffer_library_full.c

```c
/*****************************************************************************************
 *
 *  CIRCULAR BUFFER LIBRARY (SPSC FRIENDLY)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  Circular buffers are core data structures for streaming firmware:
 *      * UART RX/TX
 *      * Logging channels
 *      * DMA producer-consumer pipelines
 *
 *  They provide O(1) push/pop without moving existing data.
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      index: 0 1 2 3 4 5 6 7
 *      data : A B C _ _ _ _ _
 *              ^     ^
 *             tail  head
 *
 *      Push advances head.
 *      Pop  advances tail.
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. One slot is intentionally kept free to distinguish full vs empty.
 *  2. Producer updates head; consumer updates tail (SPSC lock-free model).
 *  3. Optional overflow counter for observability.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

typedef struct
{
    uint8_t *buffer;
    uint32_t size;

    volatile uint32_t head;
    volatile uint32_t tail;

    volatile uint32_t dropped;
} CircularBuffer;

static inline uint32_t cb_next(uint32_t i, uint32_t size)
{
    return (i + 1u) % size;
}

void cb_init(CircularBuffer *cb, uint8_t *storage, uint32_t size)
{
    cb->buffer = storage;
    cb->size = size;
    cb->head = 0u;
    cb->tail = 0u;
    cb->dropped = 0u;
}

int cb_is_empty(const CircularBuffer *cb)
{
    return cb->head == cb->tail;
}

int cb_is_full(const CircularBuffer *cb)
{
    return cb_next(cb->head, cb->size) == cb->tail;
}

int cb_push(CircularBuffer *cb, uint8_t byte)
{
    uint32_t next = cb_next(cb->head, cb->size);

    if (next == cb->tail)
    {
        cb->dropped++;
        return -1;
    }

    cb->buffer[cb->head] = byte;
    cb->head = next;
    return 0;
}

int cb_pop(CircularBuffer *cb, uint8_t *out)
{
    if (cb->head == cb->tail)
        return -1;

    *out = cb->buffer[cb->tail];
    cb->tail = cb_next(cb->tail, cb->size);
    return 0;
}

uint32_t cb_available(const CircularBuffer *cb)
{
    uint32_t h = cb->head;
    uint32_t t = cb->tail;

    if (h >= t)
        return h - t;
    return cb->size - t + h;
}

uint32_t cb_free_space(const CircularBuffer *cb)
{
    return (cb->size - 1u) - cb_available(cb);
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  If size is power-of-two, modulo can be replaced with bitmask:
 *      next = (idx + 1) & (size - 1)
 *
 *  This improves speed on small MCUs where division/modulo is expensive.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  SPSC safety relies on ownership:
 *      * Only producer writes head
 *      * Only consumer writes tail
 *
 *  For MPMC workloads, add mutexes or atomic CAS-based indexing.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why leave one slot empty?
 *
 *    To differentiate empty (head == tail) from full (next(head) == tail).
 *
 * 2. Why use volatile for head/tail?
 *
 *    They can be observed across asynchronous contexts (ISR/task).
 *
 * 3. Why is circular buffer preferred over linear queue here?
 *
 *    No O(N) shifts; push/pop remain O(1).
 *
 * 4. What happens if producer outruns consumer?
 *
 *    Buffer fills; push fails (or policy may overwrite oldest).
 *
 * 5. How do you scale for high bandwidth?
 *
 *    Increase size, use DMA producer, and reduce consumer latency.
 *
 *****************************************************************************************/
```

## 15_interrupt_safe_queue_full.c

```c
/*****************************************************************************************
 *
 *  INTERRUPT-SAFE QUEUE (ISR <-> MAIN COMMUNICATION)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  Many embedded systems pass small messages from ISR to main loop.
 *
 *  Requirements:
 *      * Non-blocking ISR push
 *      * Deterministic O(1) queue operations
 *      * Overflow visibility
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      ISR context                Main loop context
 *      -----------                -----------------
 *      queue_push_isr()   --->    queue_pop_main()
 *
 *      Producer: ISR
 *      Consumer: Main
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Single-producer/single-consumer data ownership.
 *  2. Avoid dynamic allocation in ISR path.
 *  3. Count dropped messages for diagnostics.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

#define IRQ_QUEUE_CAPACITY 32u

typedef struct
{
    uint16_t id;
    uint16_t flags;
    uint32_t value;
} IRQ_Message;

typedef struct
{
    IRQ_Message items[IRQ_QUEUE_CAPACITY];

    volatile uint32_t head;
    volatile uint32_t tail;

    volatile uint32_t dropped;
} IRQ_Queue;

static inline uint32_t iq_next(uint32_t i)
{
    return (i + 1u) % IRQ_QUEUE_CAPACITY;
}

void irq_queue_init(IRQ_Queue *q)
{
    q->head = 0u;
    q->tail = 0u;
    q->dropped = 0u;
}

int irq_queue_push_isr(IRQ_Queue *q, IRQ_Message msg)
{
    uint32_t next = iq_next(q->head);

    if (next == q->tail)
    {
        q->dropped++;
        return -1;
    }

    q->items[q->head] = msg;
    q->head = next;
    return 0;
}

int irq_queue_pop_main(IRQ_Queue *q, IRQ_Message *out)
{
    if (q->head == q->tail)
        return -1;

    *out = q->items[q->tail];
    q->tail = iq_next(q->tail);
    return 0;
}


/*****************************************************************************************
 * EXAMPLE USAGE
 *****************************************************************************************/

void uart_rx_isr_example(IRQ_Queue *q, uint8_t byte)
{
    IRQ_Message m;
    m.id = 1u;      /* UART_RX_EVENT */
    m.flags = 0u;
    m.value = byte;

    (void)irq_queue_push_isr(q, m);
}

void main_loop_step(IRQ_Queue *q)
{
    IRQ_Message m;

    while (irq_queue_pop_main(q, &m) == 0)
    {
        /* Dispatch message to state machine / application logic. */
        (void)m;
    }
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Push/pop are O(1) and bounded.
 *
 *  Keep message payload small in ISR path; store pointers/IDs rather than large blobs.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  Safe for SPSC as written.
 *
 *  Not safe for multiple ISRs pushing concurrently unless:
 *      * All ISR pushes are serialized by interrupt priority model, or
 *      * Atomic/CAS index updates are used.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why avoid malloc in ISR queue push?
 *
 *    Dynamic allocation adds latency and can fail unpredictably.
 *
 * 2. Why send small messages instead of full payloads?
 *
 *    It minimizes ISR execution time and reduces memory bandwidth.
 *
 * 3. How do you detect queue pressure?
 *
 *    Track dropped count and high-water mark (optional metric).
 *
 * 4. How to support multiple producers?
 *
 *    Use per-producer queues or atomic multi-producer ring design.
 *
 * 5. Why process queue in main loop?
 *
 *    Heavy work is deferred out of interrupt context for system responsiveness.
 *
 *****************************************************************************************/
```

## 16_state_machine_full.c

```c
/*****************************************************************************************
 *
 *  STATE MACHINE FRAMEWORK (DRIVER CONTROL FLOW)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  State machines keep embedded control logic explicit and deterministic.
 *
 *  Typical applications:
 *      * Protocol parser lifecycle
 *      * Peripheral bring-up and error recovery
 *      * Command/response transaction sequencing
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      Events -> FSM -> New State + Action
 *
 *      [RESET] --BOOT--> [INIT] --INIT_DONE--> [IDLE]
 *         ^                                  |
 *         |                                  +--TX_REQ--> [TX_BUSY]
 *         |                                  +--RX_REQ--> [RX_BUSY]
 *         +-----------RESET/FAIL/TIMEOUT-----+
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Explicit transitions, no hidden side effects.
 *  2. Default-safe handling for unexpected events.
 *  3. Error path always has deterministic recovery route.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

typedef enum
{
    FSM_RESET = 0,
    FSM_INIT,
    FSM_IDLE,
    FSM_TX_BUSY,
    FSM_RX_BUSY,
    FSM_ERROR
} DriverState;

typedef enum
{
    EVT_BOOT = 0,
    EVT_INIT_DONE,
    EVT_TX_REQ,
    EVT_RX_REQ,
    EVT_DONE,
    EVT_FAIL,
    EVT_TIMEOUT,
    EVT_RESET
} DriverEvent;

typedef struct
{
    DriverState state;

    uint32_t tx_count;
    uint32_t rx_count;
    uint32_t error_count;
} DriverFSM;

void fsm_init(DriverFSM *f)
{
    f->state = FSM_RESET;
    f->tx_count = 0u;
    f->rx_count = 0u;
    f->error_count = 0u;
}

int fsm_handle_event(DriverFSM *f, DriverEvent e)
{
    switch (f->state)
    {
        case FSM_RESET:
            if (e == EVT_BOOT)
            {
                f->state = FSM_INIT;
                return 0;
            }
            break;

        case FSM_INIT:
            if (e == EVT_INIT_DONE)
            {
                f->state = FSM_IDLE;
                return 0;
            }
            if (e == EVT_FAIL)
            {
                f->error_count++;
                f->state = FSM_ERROR;
                return 0;
            }
            break;

        case FSM_IDLE:
            if (e == EVT_TX_REQ)
            {
                f->state = FSM_TX_BUSY;
                return 0;
            }
            if (e == EVT_RX_REQ)
            {
                f->state = FSM_RX_BUSY;
                return 0;
            }
            if (e == EVT_FAIL)
            {
                f->error_count++;
                f->state = FSM_ERROR;
                return 0;
            }
            break;

        case FSM_TX_BUSY:
            if (e == EVT_DONE)
            {
                f->tx_count++;
                f->state = FSM_IDLE;
                return 0;
            }
            if (e == EVT_TIMEOUT || e == EVT_FAIL)
            {
                f->error_count++;
                f->state = FSM_ERROR;
                return 0;
            }
            break;

        case FSM_RX_BUSY:
            if (e == EVT_DONE)
            {
                f->rx_count++;
                f->state = FSM_IDLE;
                return 0;
            }
            if (e == EVT_TIMEOUT || e == EVT_FAIL)
            {
                f->error_count++;
                f->state = FSM_ERROR;
                return 0;
            }
            break;

        case FSM_ERROR:
            if (e == EVT_RESET)
            {
                f->state = FSM_RESET;
                return 0;
            }
            break;

        default:
            break;
    }

    return -1; /* Invalid transition for current state. */
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Transition dispatch is O(1) with switch-case by state/event.
 *
 *  For larger machines, table-driven transitions reduce branching complexity and
 *  improve testability.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  If events can arrive from ISR and task simultaneously, protect FSM ownership.
 *
 *  Common models:
 *      * Single event queue consumer updates FSM
 *      * Mutex/critical section around fsm_handle_event
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why is a state machine better than scattered flags?
 *
 *    It makes legal transitions explicit and prevents impossible combinations.
 *
 * 2. Why return error on invalid transition?
 *
 *    It catches logic bugs early and improves diagnosability.
 *
 * 3. How do you unit test FSMs?
 *
 *    Feed deterministic event sequences and assert state/counters after each step.
 *
 * 4. How do you scale to complex protocols?
 *
 *    Use hierarchical or table-driven FSMs with clear action callbacks.
 *
 * 5. How should timeout events be modeled?
 *
 *    As first-class events, not hidden polling side effects.
 *
 *****************************************************************************************/
```

## 17_event_queue_system_full.c

```c
/*****************************************************************************************
 *
 *  EVENT QUEUE SYSTEM (BARE-METAL EVENT-DRIVEN CORE)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  Event-driven firmware keeps ISR small and defers heavy logic to the main loop.
 *
 *  Pattern:
 *      ISR produces events
 *      Main loop consumes and dispatches handlers
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      INTERRUPTS / DRIVERS
 *              |
 *              v
 *         event_post_isr()
 *              |
 *              v
 *           EVENT QUEUE
 *              |
 *              v
 *         event_dispatch_once()
 *              |
 *              v
 *          APPLICATION HANDLERS
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. ISR path must be bounded and allocation-free.
 *  2. Queue contains small, copyable event records.
 *  3. Handler table provides decoupled dispatch.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

#define EVENT_QUEUE_SIZE 64u
#define EVENT_ID_MAX     16u

typedef enum
{
    EVT_NONE = 0,
    EVT_UART_RX,
    EVT_UART_TX_DONE,
    EVT_TIMER_TICK,
    EVT_DMA_DONE,
    EVT_BUTTON_PRESS
} EventId;

typedef struct
{
    EventId id;
    uint32_t arg0;
    uint32_t arg1;
} Event;

typedef struct
{
    Event items[EVENT_QUEUE_SIZE];

    volatile uint32_t head;
    volatile uint32_t tail;

    volatile uint32_t dropped;
} EventQueue;

typedef void (*event_handler_t)(const Event *e);

static event_handler_t g_handlers[EVENT_ID_MAX];

static inline uint32_t eq_next(uint32_t i)
{
    return (i + 1u) % EVENT_QUEUE_SIZE;
}

void event_queue_init(EventQueue *q)
{
    q->head = 0u;
    q->tail = 0u;
    q->dropped = 0u;

    for (uint32_t i = 0u; i < EVENT_ID_MAX; i++)
        g_handlers[i] = NULL;
}

void event_register_handler(EventId id, event_handler_t h)
{
    if ((uint32_t)id < EVENT_ID_MAX)
        g_handlers[(uint32_t)id] = h;
}

int event_post_isr(EventQueue *q, Event e)
{
    uint32_t next = eq_next(q->head);

    if (next == q->tail)
    {
        q->dropped++;
        return -1;
    }

    q->items[q->head] = e;
    q->head = next;
    return 0;
}

int event_get(EventQueue *q, Event *out)
{
    if (q->head == q->tail)
        return -1;

    *out = q->items[q->tail];
    q->tail = eq_next(q->tail);
    return 0;
}

int event_dispatch_once(EventQueue *q)
{
    Event e;

    if (event_get(q, &e) != 0)
        return -1;

    if ((uint32_t)e.id < EVENT_ID_MAX)
    {
        event_handler_t h = g_handlers[(uint32_t)e.id];
        if (h != NULL)
            h(&e);
    }

    return 0;
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Event posting and fetching are O(1).
 *
 *  Throughput depends on:
 *      * ISR event rate
 *      * Main loop dispatch budget
 *      * Handler execution time
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  Safe in SPSC mode (ISR producer, main consumer).
 *
 *  If multiple producers exist, serialize posting or use atomic MPSC queue logic.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why event-driven architecture on bare metal?
 *
 *    It decouples interrupt timing from business logic and improves responsiveness.
 *
 * 2. Why keep ISR handlers short?
 *
 *    Long ISRs increase latency for other interrupts and can break timing guarantees.
 *
 * 3. What if handlers are too slow?
 *
 *    Queue backlog grows, then overflows. Split heavy work into incremental tasks.
 *
 * 4. Why use handler registry?
 *
 *    It avoids hard-coded switch bloating and improves modularity.
 *
 * 5. How to prioritize critical events?
 *
 *    Use separate priority queues or priority-aware scheduler in dispatch layer.
 *
 *****************************************************************************************/
```

## 18_timer_callback_scheduler_full.c

```c
/*****************************************************************************************
 *
 *  TIMER CALLBACK SCHEDULER (SOFTWARE TIMERS)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  Software timers multiplex many timed callbacks on one hardware tick source.
 *
 *  Typical usage:
 *      * Retry timeouts
 *      * Periodic health checks
 *      * Delayed work
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      HW TIMER ISR --> tick++ --> mark expired timers pending
 *                                         |
 *                                         v
 *                                main-loop timer_dispatch()
 *                                         |
 *                                         v
 *                                      callback()
 *
 *  This keeps ISR short and executes callback logic in thread/main context.
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. ISR does bookkeeping only (no heavy callback code).
 *  2. Callback execution is deferred.
 *  3. One-shot and periodic timers share same slot model.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

#define MAX_SW_TIMERS 32u

typedef void (*timer_cb_t)(void *arg);

typedef struct
{
    uint8_t active;
    uint8_t periodic;

    uint32_t period_ticks;
    uint32_t deadline;

    timer_cb_t cb;
    void *arg;

    volatile uint8_t pending;
} TimerSlot;

typedef struct
{
    TimerSlot slots[MAX_SW_TIMERS];
    volatile uint32_t tick;
} TimerScheduler;

void timer_scheduler_init(TimerScheduler *s)
{
    s->tick = 0u;

    for (uint32_t i = 0u; i < MAX_SW_TIMERS; i++)
    {
        s->slots[i].active = 0u;
        s->slots[i].periodic = 0u;
        s->slots[i].period_ticks = 0u;
        s->slots[i].deadline = 0u;
        s->slots[i].cb = NULL;
        s->slots[i].arg = NULL;
        s->slots[i].pending = 0u;
    }
}

int timer_start(TimerScheduler *s,
                uint32_t delay_ticks,
                uint32_t period_ticks,
                timer_cb_t cb,
                void *arg)
{
    for (uint32_t i = 0u; i < MAX_SW_TIMERS; i++)
    {
        TimerSlot *t = &s->slots[i];

        if (!t->active)
        {
            t->active = 1u;
            t->periodic = (period_ticks != 0u) ? 1u : 0u;
            t->period_ticks = period_ticks;
            t->deadline = s->tick + delay_ticks;
            t->cb = cb;
            t->arg = arg;
            t->pending = 0u;
            return (int)i;
        }
    }

    return -1;
}

void timer_stop(TimerScheduler *s, int id)
{
    if (id < 0 || (uint32_t)id >= MAX_SW_TIMERS)
        return;

    s->slots[(uint32_t)id].active = 0u;
    s->slots[(uint32_t)id].pending = 0u;
}

void timer_tick_isr(TimerScheduler *s)
{
    s->tick++;

    for (uint32_t i = 0u; i < MAX_SW_TIMERS; i++)
    {
        TimerSlot *t = &s->slots[i];

        if (!t->active)
            continue;

        if ((int32_t)(s->tick - t->deadline) >= 0)
        {
            t->pending = 1u;

            if (t->periodic)
                t->deadline += t->period_ticks;
            else
                t->active = 0u;
        }
    }
}

void timer_dispatch(TimerScheduler *s)
{
    for (uint32_t i = 0u; i < MAX_SW_TIMERS; i++)
    {
        TimerSlot *t = &s->slots[i];

        if (t->pending)
        {
            t->pending = 0u;

            if (t->cb != NULL)
                t->cb(t->arg);
        }
    }
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Current design scans all slots each tick: O(N).
 *
 *  For large timer counts, switch to min-heap or timer-wheel design.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  timer_tick_isr and timer_start/stop may access slots concurrently.
 *
 *  Protect start/stop with critical section or double-buffer timer commands.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why defer callbacks out of ISR?
 *
 *    To keep interrupt latency bounded and avoid long ISR critical paths.
 *
 * 2. How are periodic timers implemented?
 *
 *    After expiry, deadline is incremented by fixed period.
 *
 * 3. What causes timer drift?
 *
 *    If reschedule uses current tick instead of previous deadline, jitter accumulates.
 *
 * 4. Why signed subtraction in expiry check?
 *
 *    It handles uint32 tick wrap-around safely.
 *
 * 5. How to scale to thousands of timers?
 *
 *    Use a timer wheel or min-heap instead of full linear scan.
 *
 *****************************************************************************************/
```

## 19_dma_double_buffer_streaming_full.c

```c
/*****************************************************************************************
 *
 *  DMA DOUBLE BUFFER STREAMING (CONTINUOUS DATA PIPELINE)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  Double buffering allows DMA and CPU to work in parallel:
 *      * DMA fills one buffer
 *      * CPU processes the other buffer
 *
 *  Common workloads:
 *      * Audio capture/playback
 *      * ADC sample streams
 *      * Camera or high-rate sensor pipelines
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      DMA writes A ----> A ready for CPU
 *                |                ^
 *                v                |
 *      DMA writes B ----> B ready for CPU
 *
 *      Ping-pong pattern avoids stop-and-wait gaps.
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Separate ownership flags for buffer A/B.
 *  2. Overrun counter when DMA completes before CPU releases prior buffer.
 *  3. Zero-copy processing directly on filled buffers.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

#define STREAM_BUFFER_SIZE 256u

typedef enum
{
    DMA_BUF_A = 0,
    DMA_BUF_B = 1
} DmaBufferIndex;

typedef struct
{
    uint8_t buf_a[STREAM_BUFFER_SIZE];
    uint8_t buf_b[STREAM_BUFFER_SIZE];

    volatile uint8_t ready_a;
    volatile uint8_t ready_b;

    volatile DmaBufferIndex dma_target;
    volatile uint32_t overruns;
} DmaDoubleStream;

void stream_init(DmaDoubleStream *s)
{
    s->ready_a = 0u;
    s->ready_b = 0u;
    s->dma_target = DMA_BUF_A;
    s->overruns = 0u;
}

uint8_t *stream_dma_target_ptr(DmaDoubleStream *s)
{
    return (s->dma_target == DMA_BUF_A) ? s->buf_a : s->buf_b;
}

void stream_dma_a_complete_isr(DmaDoubleStream *s)
{
    if (s->ready_a)
        s->overruns++;

    s->ready_a = 1u;
    s->dma_target = DMA_BUF_B;
}

void stream_dma_b_complete_isr(DmaDoubleStream *s)
{
    if (s->ready_b)
        s->overruns++;

    s->ready_b = 1u;
    s->dma_target = DMA_BUF_A;
}

int stream_acquire_ready_buffer(DmaDoubleStream *s, uint8_t **buf, size_t *len)
{
    if (s->ready_a)
    {
        *buf = s->buf_a;
        *len = STREAM_BUFFER_SIZE;
        return 0;
    }

    if (s->ready_b)
    {
        *buf = s->buf_b;
        *len = STREAM_BUFFER_SIZE;
        return 0;
    }

    return -1;
}

void stream_release_buffer(DmaDoubleStream *s, uint8_t *buf)
{
    if (buf == s->buf_a)
        s->ready_a = 0u;
    else if (buf == s->buf_b)
        s->ready_b = 0u;
}


/*****************************************************************************************
 * EXAMPLE PROCESSING FUNCTION
 *****************************************************************************************/

uint32_t stream_process_sum(const uint8_t *buf, size_t len)
{
    uint32_t sum = 0u;

    for (size_t i = 0u; i < len; i++)
        sum += buf[i];

    return sum;
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Double buffering improves throughput by overlapping DMA I/O and CPU compute.
 *
 *  If processing exceeds one buffer period, overruns occur.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * CACHE / DMA COHERENCY
 *
 *  With CPU cache enabled:
 *      * Invalidate cache before CPU reads DMA-filled buffer
 *      * Clean cache before DMA reads CPU-written TX buffer
 *
 *  Otherwise CPU may see stale data.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  ready flags are shared between ISR and main loop.
 *
 *  Use volatile flags (as shown) and ensure memory barrier/critical section policy
 *  matches your CPU architecture.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why double buffering instead of single buffer?
 *
 *    It overlaps producer/consumer work and removes idle gaps.
 *
 * 2. What is an overrun in this model?
 *
 *    DMA completes a buffer that CPU has not yet consumed/released.
 *
 * 3. Why process data in-place?
 *
 *    Zero-copy minimizes memory bandwidth and CPU overhead.
 *
 * 4. Why are cache operations necessary with DMA?
 *
 *    DMA bypasses cache; CPU cache may otherwise hold stale lines.
 *
 * 5. How to scale throughput further?
 *
 *    Increase buffer size/count, optimize processing path, or offload compute.
 *
 *****************************************************************************************/
```

## 20_uart_packet_parser_full.c

```c
/*****************************************************************************************
 *
 *  UART PACKET PARSER (BYTE-STREAM STATE MACHINE)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  UART delivers raw byte streams. Packet parsers reconstruct framed messages.
 *
 *  Example protocol:
 *      START(0xAA) | LEN | PAYLOAD[LEN] | CRC8
 *
 *  This implementation uses XOR checksum for interview clarity.
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      UART RX bytes -> parser_feed_byte() -> state transitions -> packet_ready
 *
 *      WAIT_START -> WAIT_LEN -> WAIT_PAYLOAD -> WAIT_CRC -> COMPLETE
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Incremental byte-by-byte parsing.
 *  2. Explicit parser states and deterministic recovery.
 *  3. Validation (length + checksum) before publish.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>

#define PKT_START_BYTE   0xAAu
#define PKT_MAX_PAYLOAD  64u

typedef struct
{
    uint8_t length;
    uint8_t payload[PKT_MAX_PAYLOAD];
    uint8_t crc;
} UartPacket;

typedef enum
{
    PARSER_WAIT_START = 0,
    PARSER_WAIT_LEN,
    PARSER_WAIT_PAYLOAD,
    PARSER_WAIT_CRC
} ParserState;

typedef struct
{
    ParserState state;

    UartPacket current;
    uint8_t payload_index;
    uint8_t running_crc;

    UartPacket ready_packet;
    volatile uint8_t packet_ready;

    volatile uint32_t packets_ok;
    volatile uint32_t crc_fail;
    volatile uint32_t framing_fail;
} UartParser;

void parser_init(UartParser *p)
{
    p->state = PARSER_WAIT_START;
    p->payload_index = 0u;
    p->running_crc = 0u;
    p->packet_ready = 0u;

    p->packets_ok = 0u;
    p->crc_fail = 0u;
    p->framing_fail = 0u;
}

static void parser_reset_frame(UartParser *p)
{
    p->state = PARSER_WAIT_START;
    p->payload_index = 0u;
    p->running_crc = 0u;
}

void parser_feed_byte(UartParser *p, uint8_t byte)
{
    switch (p->state)
    {
        case PARSER_WAIT_START:
            if (byte == PKT_START_BYTE)
            {
                p->state = PARSER_WAIT_LEN;
                p->payload_index = 0u;
                p->running_crc = 0u;
            }
            break;

        case PARSER_WAIT_LEN:
            if (byte == 0u || byte > PKT_MAX_PAYLOAD)
            {
                p->framing_fail++;
                parser_reset_frame(p);
                break;
            }

            p->current.length = byte;
            p->running_crc ^= byte;
            p->state = PARSER_WAIT_PAYLOAD;
            break;

        case PARSER_WAIT_PAYLOAD:
            p->current.payload[p->payload_index++] = byte;
            p->running_crc ^= byte;

            if (p->payload_index >= p->current.length)
                p->state = PARSER_WAIT_CRC;
            break;

        case PARSER_WAIT_CRC:
            p->current.crc = byte;

            if (p->current.crc == p->running_crc)
            {
                p->ready_packet = p->current;
                p->packet_ready = 1u;
                p->packets_ok++;
            }
            else
            {
                p->crc_fail++;
            }

            parser_reset_frame(p);
            break;

        default:
            parser_reset_frame(p);
            break;
    }
}

void parser_feed_buffer(UartParser *p, const uint8_t *buf, size_t len)
{
    for (size_t i = 0u; i < len; i++)
        parser_feed_byte(p, buf[i]);
}

int parser_get_packet(UartParser *p, UartPacket *out)
{
    if (!p->packet_ready)
        return -1;

    *out = p->ready_packet;
    p->packet_ready = 0u;
    return 0;
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Parsing cost is O(N) over received bytes with O(1) work per byte.
 *
 *  For very high throughput, pair parser with DMA RX ring buffer to reduce ISR load.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  If parser_feed_byte runs in ISR and parser_get_packet runs in main loop,
 *  packet_ready and packet copy access must be synchronized.
 *
 *  Typical options:
 *      * Disable interrupts briefly during packet_get copy
 *      * Use double-buffered packet handoff
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why is a state machine required for UART packets?
 *
 *    UART is a stream; framing boundaries must be reconstructed incrementally.
 *
 * 2. Why validate length before payload read?
 *
 *    Prevents buffer overflow and fast-fails malformed frames.
 *
 * 3. What is parser resynchronization?
 *
 *    Returning to WAIT_START after error so parser can lock onto next valid frame.
 *
 * 4. Why use running CRC/checksum?
 *
 *    It validates payload integrity with minimal memory overhead.
 *
 * 5. How to support variable protocol versions?
 *
 *    Extend header (type/version flags) and branch to version-specific decode paths.
 *
 *****************************************************************************************/
```
