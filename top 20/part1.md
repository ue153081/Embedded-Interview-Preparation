# Top 10 Questions - Combined C Sources

This file contains the full content of every .c file under `self prepared notes/top 10 questions`.

## 01_uart_driver_interrupt_full.c

```c
/*****************************************************************************************
 *
 *  UART DRIVER IMPLEMENTATION (INTERRUPT DRIVEN) - INTERVIEW EDITION
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  This file implements a production-style UART driver designed for embedded interviews.
 *
 *  Features:
 *      • Interrupt driven RX
 *      • Interrupt driven TX
 *      • Lock-free circular buffers
 *      • Non-blocking APIs
 *      • Overflow detection
 *      • Clear separation between ISR and application code
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      SERIAL LINE
 *           │
 *           ▼
 *      UART HARDWARE
 *           │
 *           ▼
 *      INTERRUPT HANDLER
 *      ┌───────────────┬────────────────┐
 *      ▼               ▼                │
 *   RX ISR          TX ISR              │
 *      │               │                │
 *      ▼               ▼                │
 *   RX BUFFER      TX BUFFER            │
 *      │               ▲                │
 *      ▼               │                │
 *  APPLICATION ------ WRITE API --------┘
 *         │
 *         ▼
 *      READ API
 *
 *
 *  ======================================================================================
 *  DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Interrupt-driven IO
 *
 *     Instead of polling hardware registers continuously, the UART peripheral generates
 *     interrupts whenever:
 *
 *          RXNE → Receive data register not empty
 *          TXE  → Transmit register empty
 *
 *
 *  2. Producer / Consumer Model
 *
 *     RX Path:
 *          Producer → UART ISR
 *          Consumer → Application
 *
 *     TX Path:
 *          Producer → Application
 *          Consumer → UART ISR
 *
 *
 *  3. Lock-Free Design
 *
 *     RX:
 *         ISR updates head
 *         Application updates tail
 *
 *     TX:
 *         Application updates head
 *         ISR updates tail
 *
 *     Since each variable is written by only one context, no mutex is required.
 *
 *
 *  ======================================================================================
 *  HARDWARE REGISTER MODEL
 *  ======================================================================================
 *
 *  UART peripherals are memory mapped.
 *
 *  Example:
 *
 *      Address         Register
 *      -------------------------
 *      0x40011000  →   SR
 *      0x40011004  →   DR
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>


/*****************************************************************************************
 * UART STATUS FLAGS
 *****************************************************************************************/

#define UART_SR_RXNE   (1u << 5)   /* Receive register not empty */
#define UART_SR_TXE    (1u << 7)   /* Transmit register empty   */


/*****************************************************************************************
 * UART REGISTER STRUCTURE
 *
 * volatile is required because hardware updates these registers asynchronously.
 *****************************************************************************************/

typedef struct
{
    volatile uint32_t SR;
    volatile uint32_t DR;

} UART_Regs;



/*****************************************************************************************
 * CIRCULAR BUFFER
 *
 * A ring buffer stores streaming data efficiently.
 *
 * Example layout:
 *
 * index : 0 1 2 3 4 5 6 7
 * data  : A B C D _ _ _ _
 *          ↑         ↑
 *         tail      head
 *
 *****************************************************************************************/

typedef struct
{
    uint8_t *buffer;
    uint16_t capacity;

    volatile uint16_t head;
    volatile uint16_t tail;

} RingBuffer;



/*****************************************************************************************
 * UART DRIVER OBJECT
 *****************************************************************************************/

typedef struct
{
    UART_Regs *regs;

    RingBuffer rx;
    RingBuffer tx;

    volatile uint32_t rx_overflow;
    volatile uint8_t tx_active;

} UART_Driver;

/* Fake UART peripheral for simulation */
UART_Regs UART1;


/* Buffer sizes */
#define RX_BUFFER_SIZE 64
#define TX_BUFFER_SIZE 64


/*****************************************************************************************
 * HELPER FUNCTION: NEXT INDEX
 *
 * Wraps index around circular buffer.
 *****************************************************************************************/

static uint16_t next_index(uint16_t i, uint16_t cap)
{
    return (uint16_t)((i + 1u) % cap);
}



/*****************************************************************************************
 * RING BUFFER INITIALIZATION
 *****************************************************************************************/

void ring_init(RingBuffer *r, uint8_t *buf, uint16_t cap)
{
    r->buffer = buf;
    r->capacity = cap;

    r->head = 0;
    r->tail = 0;
}



/*****************************************************************************************
 * UART INITIALIZATION
 *
 * Connects driver object with hardware registers and buffers.
 *****************************************************************************************/

void uart_init(UART_Driver *u,
               UART_Regs *regs,
               uint8_t *rx_buf,
               uint16_t rx_size,
               uint8_t *tx_buf,
               uint16_t tx_size)
{
    u->regs = regs;

    ring_init(&u->rx, rx_buf, rx_size);
    ring_init(&u->tx, tx_buf, tx_size);

    u->rx_overflow = 0;
    u->tx_active = 0;
}



/*****************************************************************************************
 * RX INTERRUPT HANDLER
 *
 * Moves received bytes from UART hardware into RX ring buffer.
 *
 * Flow:
 *
 *      UART receives byte
 *            │
 *            ▼
 *      RXNE flag set
 *            │
 *            ▼
 *      Interrupt fires
 *            │
 *            ▼
 *      Read DR register
 *            │
 *            ▼
 *      Store byte in ring buffer
 *
 *****************************************************************************************/

void uart_rx_isr(UART_Driver *u)
{
    UART_Regs *regs = u->regs;
    RingBuffer *rb = &u->rx;

    while (regs->SR & UART_SR_RXNE)
    {
        uint8_t byte = (uint8_t)(regs->DR & 0xFF);

        uint16_t next = next_index(rb->head, rb->capacity);

        if (next == rb->tail)
        {
            /* buffer full → drop byte */
            u->rx_overflow++;
            continue;
        }

        rb->buffer[rb->head] = byte;
        rb->head = next;
    }
}



/*****************************************************************************************
 * TX INTERRUPT HANDLER
 *
 * Sends bytes from TX ring buffer to UART hardware.
 *****************************************************************************************/

void uart_tx_isr(UART_Driver *u)
{
    UART_Regs *regs = u->regs;
    RingBuffer *rb = &u->tx;

    if (!(regs->SR & UART_SR_TXE))
        return;

    if (rb->tail == rb->head)
    {
        u->tx_active = 0;
        return;
    }

    regs->DR = rb->buffer[rb->tail];

    rb->tail = next_index(rb->tail, rb->capacity);
}



/*****************************************************************************************
 * COMBINED INTERRUPT HANDLER
 *
 * Most microcontrollers use a single interrupt for UART.
 *****************************************************************************************/

void uart_irq_handler(UART_Driver *u)
{
    UART_Regs *regs = u->regs;

    if (regs->SR & UART_SR_RXNE)
    {
        uart_rx_isr(u);
    }

    if (regs->SR & UART_SR_TXE)
    {
        uart_tx_isr(u);
    }
}



/*****************************************************************************************
 * APPLICATION API: READ DATA
 *
 * Non-blocking read from RX buffer.
 *****************************************************************************************/

size_t uart_read(UART_Driver *u, uint8_t *out, size_t max)
{
    RingBuffer *rb = &u->rx;

    size_t count = 0;

    while ((count < max) && (rb->tail != rb->head))
    {
        out[count++] = rb->buffer[rb->tail];

        rb->tail = next_index(rb->tail, rb->capacity);
    }

    return count;
}



/*****************************************************************************************
 * APPLICATION API: WRITE DATA
 *
 * Adds bytes into TX buffer.
 *****************************************************************************************/

size_t uart_write(UART_Driver *u, const uint8_t *data, size_t len)
{
    RingBuffer *rb = &u->tx;

    size_t count = 0;

    while (count < len)
    {
        uint16_t next = next_index(rb->head, rb->capacity);

        if (next == rb->tail)
            break;

        rb->buffer[rb->head] = data[count++];
        rb->head = next;
    }

    if ((count > 0u) && (!u->tx_active))
    {
        u->tx_active = 1u;
        uart_tx_isr(u);
    }

    return count;
}


int main(void)
{
    UART_Driver uart;

    /* Allocate buffers */
    static uint8_t rx_buffer[RX_BUFFER_SIZE];
    static uint8_t tx_buffer[TX_BUFFER_SIZE];

    /* Initialize UART driver */
    uart_init(&uart,
              &UART1,
              rx_buffer,
              RX_BUFFER_SIZE,
              tx_buffer,
              TX_BUFFER_SIZE);


    /***********************************************************
     * TRANSMIT EXAMPLE
     ***********************************************************/

    const char *msg = "Hello UART Interrupt Driver!\n";

    uart_write(&uart,
               (const uint8_t *)msg,
               strlen(msg));


    /***********************************************************
     * MAIN LOOP
     ***********************************************************/

    uint8_t rx_data[32];

    while (1)
    {
        /* Simulate interrupt being triggered */
        uart_irq_handler(&uart);

        /* Read received data */
        size_t n = uart_read(&uart, rx_data, sizeof(rx_data));

        if (n > 0)
        {
            /* Echo received data back */
            uart_write(&uart, rx_data, n);
        }
    }

    return 0;
}



/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why is volatile required for head and tail?
 *
 *    ISR and application access these fields asynchronously.
 *    volatile forces memory reads/writes so stale cached values are not used.
 *
 *
 * 2. Why use a circular buffer instead of a normal queue?
 *
 *    Circular buffers avoid data shifting and keep enqueue/dequeue O(1).
 *    This gives deterministic behavior for embedded systems.
 *
 *
 * 3. What happens if the application reads slower than UART receives?
 *
 *    Buffer eventually reaches next(head) == tail (full condition).
 *    A common policy is dropping new bytes and incrementing overflow counters.
 *
 *
 * 4. How would you support very high UART speeds (e.g. 5 Mbps)?
 *
 *    Interrupt-per-byte handling can reach around 500k IRQ/s at 5 Mbps.
 *    DMA moves bytes to RAM directly, so CPU handles chunk-level events.
 *
 *
 * 5. How would this change in an RTOS?
 *
 *    ISR could notify a task using semaphore or event queue.
 *
 *****************************************************************************************/

```

## 02_uart_dma_driver_full.c

```c

/*****************************************************************************************
 *
 *  UART DRIVER IMPLEMENTATION (DMA BASED HIGH-THROUGHPUT VERSION)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  This file implements a UART driver using DMA reception to support high data rates.
 *
 *  Motivation:
 *
 *  Interrupt-per-byte UART drivers break down at high speeds.
 *
 *  Example:
 *
 *      UART Speed: 3 Mbps
 *      Frame size: ~10 bits per byte
 *
 *      Bytes/sec ≈ 300,000
 *
 *  That means:
 *
 *      300,000 interrupts/sec
 *
 *  which can easily overload the CPU.
 *
 *  Solution:
 *
 *      Use DMA (Direct Memory Access) to transfer UART data directly into memory.
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      SERIAL LINE
 *           │
 *           ▼
 *      UART HARDWARE
 *           │
 *           ▼
 *      DMA CONTROLLER
 *           │
 *           ▼
 *      CIRCULAR RX BUFFER
 *           │
 *           ▼
 *      APPLICATION PROCESSING
 *
 *
 *  ======================================================================================
 *  KEY DESIGN PRINCIPLES
 *  ======================================================================================
 *
 *  1. Zero-Copy Reception
 *
 *     Data moves directly from UART hardware → RAM buffer.
 *
 *
 *  2. Circular DMA Buffer
 *
 *     DMA continuously writes to a circular buffer.
 *
 *
 *  3. Application Maintains Read Pointer
 *
 *     DMA maintains write pointer
 *     Application maintains read pointer
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>


/*****************************************************************************************
 * UART STATUS FLAGS
 *****************************************************************************************/

#define UART_SR_IDLE   (1u << 4)    /* Idle line detected */


/*****************************************************************************************
 * UART REGISTER MODEL
 *****************************************************************************************/

typedef struct
{
    volatile uint32_t SR;
    volatile uint32_t DR;

} UART_Regs;


/*****************************************************************************************
 * DMA STREAM REGISTER MODEL
 *
 * Simplified version used for conceptual driver explanation.
 *****************************************************************************************/

typedef struct
{
    volatile uint32_t CR;
    volatile uint32_t NDTR;    /* Number of data items remaining */
    volatile uint32_t PAR;
    volatile uint32_t M0AR;

} DMA_Stream;


/*****************************************************************************************
 * DMA RING BUFFER STRUCTURE
 *****************************************************************************************/

typedef struct
{
    uint8_t *buffer;
    uint16_t size;
    volatile uint16_t read_pos;

} DMA_RingBuffer;


/*****************************************************************************************
 * UART DMA DRIVER OBJECT
 *****************************************************************************************/

typedef struct
{
    UART_Regs *uart;
    DMA_Stream *dma;
    DMA_RingBuffer rx;

} UART_DMA_Driver;


/*****************************************************************************************
 * DRIVER INITIALIZATION
 *****************************************************************************************/

void uart_dma_init(UART_DMA_Driver *drv,
                   UART_Regs *uart,
                   DMA_Stream *dma,
                   uint8_t *rx_buffer,
                   uint16_t buffer_size)
{
    drv->uart = uart;
    drv->dma = dma;

    drv->rx.buffer = rx_buffer;
    drv->rx.size = buffer_size;
    drv->rx.read_pos = 0;
}


/*****************************************************************************************
 * GET DMA WRITE POSITION
 *
 * NDTR = remaining transfers
 *
 * write_pos = buffer_size - NDTR
 *****************************************************************************************/

static uint16_t dma_get_write_pos(UART_DMA_Driver *drv)
{
    uint16_t remaining = drv->dma->NDTR;

    return (drv->rx.size - remaining) % drv->rx.size;
}


/*****************************************************************************************
 * COMPUTE AVAILABLE BYTES
 *****************************************************************************************/

size_t uart_dma_available(UART_DMA_Driver *drv)
{
    uint16_t write = dma_get_write_pos(drv);
    uint16_t read = drv->rx.read_pos;

    if (write >= read)
        return write - read;
    else
        return drv->rx.size - read + write;
}


/*****************************************************************************************
 * APPLICATION READ API
 *****************************************************************************************/

size_t uart_dma_read(UART_DMA_Driver *drv,
                     uint8_t *out,
                     size_t maxlen)
{
    size_t count = 0;

    while (count < maxlen)
    {
        size_t available = uart_dma_available(drv);

        if (available == 0)
            break;

        uint16_t pos = drv->rx.read_pos;

        out[count++] = drv->rx.buffer[pos];

        drv->rx.read_pos = (pos + 1) % drv->rx.size;
    }

    return count;
}


/*****************************************************************************************
 * IDLE INTERRUPT HANDLER
 *
 * UART IDLE line indicates pause in transmission.
 * This is commonly used to detect packet boundaries.
 *****************************************************************************************/

void uart_idle_isr(UART_DMA_Driver *drv)
{
    if (drv->uart->SR & UART_SR_IDLE)
    {
        volatile uint32_t tmp;

        tmp = drv->uart->SR;
        tmp = drv->uart->DR;

        (void)tmp;

        /* Application may process packet here */
    }
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 * Interrupt-per-byte driver:
 *
 *      3 Mbps UART
 *      → ~300k interrupts/sec
 *
 * DMA driver:
 *
 *      Interrupt only on packet boundary
 *      → drastically reduced CPU load
 *
 *****************************************************************************************/


/*****************************************************************************************
 * CACHE / DMA COHERENCY
 *
 * On systems with CPU caches:
 *
 *      DMA writes memory
 *      CPU reads cached data
 *
 * CPU may see stale data.
 *
 * Solutions:
 *
 *      1. Cache invalidate
 *      2. Non-cacheable memory region
 *      3. Memory barriers
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 * Possible race:
 *
 *      CPU reads DMA write pointer
 *      DMA updates pointer simultaneously
 *
 * Safe technique:
 *
 *      read pointer twice
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why DMA instead of interrupts for high speed UART?
 *
 *    Interrupt-per-byte RX can hit very high IRQ rates (for example ~300k/s at 3 Mbps).
 *    DMA streams UART data to memory and CPU handles only boundary/idle events.
 *
 * 2. How do you detect packet boundaries?
 *
 *    Use UART IDLE-line detection: one frame of silence raises IDLE interrupt.
 *    That idle event is used as a packet boundary trigger.
 *
 * 3. What happens if DMA overwrites unread data?
 *
 *    If the write pointer catches the read pointer, unread bytes are overwritten.
 *    Mitigate with larger buffers, faster processing, or RTS/CTS flow control.
 *
 * 4. How do you avoid CPU cache issues with DMA?
 *
 *    DMA writes RAM while CPU may read stale cache lines.
 *    Invalidate/clean cache around DMA buffers or place buffers in non-cacheable memory.
 *
 * 5. How would you implement zero-copy packet processing?
 *
 *    Process packets directly from the DMA ring buffer without copy-out.
 *    If data wraps the buffer end, process in two segments, then advance read_pos.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * DMA CONFIGURATION AND START
 *
 * This function performs the actual DMA hardware configuration for UART RX.
 * It links UART DR register to the DMA peripheral address and enables circular mode.
 *****************************************************************************************/

#define DMA_CR_EN            (1u << 0)
#define DMA_CR_CIRC          (1u << 8)
#define DMA_CR_MINC          (1u << 10)
#define DMA_CR_DIR_P2M       (0u << 6)   /* Peripheral-to-memory */

/*****************************************************************************************
 * START UART DMA RECEPTION
 *****************************************************************************************/

void uart_dma_start(UART_DMA_Driver *drv)
{
    /* Configure peripheral address (UART data register) */
    drv->dma->PAR  = (uint32_t)&drv->uart->DR;

    /* Configure memory address (RX buffer) */
    drv->dma->M0AR = (uint32_t)drv->rx.buffer;

    /* Number of bytes to receive */
    drv->dma->NDTR = drv->rx.size;

    /* Configure DMA control register
       - Peripheral to memory
       - Memory increment enabled
       - Circular mode enabled
    */
    drv->dma->CR =
        DMA_CR_DIR_P2M |
        DMA_CR_MINC   |
        DMA_CR_CIRC;

    /* Enable DMA stream */
    drv->dma->CR |= DMA_CR_EN;
}
```

## 03_ring_buffer_lockfree_full.c

```c

/*****************************************************************************************
 *
 *  LOCK-FREE RING BUFFER IMPLEMENTATION (SPSC QUEUE)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  This file implements a lock‑free Single Producer Single Consumer (SPSC) circular buffer.
 *
 *  This data structure is extremely common in embedded systems for:
 *
 *      • UART drivers
 *      • logging systems
 *      • DMA streaming
 *      • ISR → application communication
 *
 *
 *  Why lock‑free?
 *
 *  In embedded systems, interrupts cannot block. Using mutexes or locks inside an ISR
 *  is unsafe and may cause deadlocks or priority inversion.
 *
 *  Instead we design data structures where:
 *
 *      Producer writes only HEAD
 *      Consumer writes only TAIL
 *
 *  Because each variable has a single writer, we avoid race conditions without locks.
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      PRODUCER                         CONSUMER
 *
 *      (ISR / DMA)                      (Application)
 *           │                                 │
 *           ▼                                 ▼
 *      write HEAD                        read TAIL
 *           │                                 │
 *           └─────────── RING BUFFER ─────────┘
 *
 *
 *  ======================================================================================
 *  RING BUFFER MODEL
 *  ======================================================================================
 *
 *      Capacity = 8
 *
 *      Index:   0 1 2 3 4 5 6 7
 *               ----------------
 *      Data:   [A B C D _ _ _ _]
 *               ↑       ↑
 *              tail    head
 *
 *      Available data = head - tail
 *
 *
 *  Wraparound example:
 *
 *      Index:   0 1 2 3 4 5 6 7
 *               ----------------
 *      Data:   [E F _ _ A B C D]
 *                ↑       ↑
 *               head    tail
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>


/*****************************************************************************************
 * RING BUFFER STRUCTURE
 *
 *  buffer   → pointer to memory storage
 *  size     → capacity
 *  head     → write index (producer only)
 *  tail     → read index  (consumer only)
 *
 *****************************************************************************************/

typedef struct
{
    uint8_t *buffer;
    uint32_t size;

    volatile uint32_t head;
    volatile uint32_t tail;

} RingBuffer;


/*****************************************************************************************
 * INITIALIZATION
 *****************************************************************************************/

void rb_init(RingBuffer *rb, uint8_t *storage, uint32_t size)
{
    rb->buffer = storage;
    rb->size = size;

    rb->head = 0;
    rb->tail = 0;
}


/*****************************************************************************************
 * NEXT INDEX HELPER
 *****************************************************************************************/

static inline uint32_t rb_next(uint32_t i, uint32_t size)
{
    return (i + 1) % size;
}


/*****************************************************************************************
 * BUFFER EMPTY CHECK
 *****************************************************************************************/

int rb_is_empty(RingBuffer *rb)
{
    return rb->head == rb->tail;
}


/*****************************************************************************************
 * BUFFER FULL CHECK
 *****************************************************************************************/

int rb_is_full(RingBuffer *rb)
{
    uint32_t next = rb_next(rb->head, rb->size);
    return next == rb->tail;
}


/*****************************************************************************************
 * PUSH (PRODUCER)
 *
 *  Called by producer (ISR or task).
 *
 *****************************************************************************************/

int rb_push(RingBuffer *rb, uint8_t value)
{
    uint32_t next = rb_next(rb->head, rb->size);

    if (next == rb->tail)
    {
        /* buffer full */
        return -1;
    }

    rb->buffer[rb->head] = value;

    rb->head = next;

    return 0;
}


/*****************************************************************************************
 * POP (CONSUMER)
 *
 *  Called by application thread.
 *
 *****************************************************************************************/

int rb_pop(RingBuffer *rb, uint8_t *value)
{
    if (rb->head == rb->tail)
    {
        /* buffer empty */
        return -1;
    }

    *value = rb->buffer[rb->tail];

    rb->tail = rb_next(rb->tail, rb->size);

    return 0;
}


/*****************************************************************************************
 * COMPUTE AVAILABLE DATA
 *****************************************************************************************/

uint32_t rb_available(RingBuffer *rb)
{
    uint32_t head = rb->head;
    uint32_t tail = rb->tail;

    if (head >= tail)
        return head - tail;
    else
        return rb->size - tail + head;
}


/*****************************************************************************************
 * COMPUTE FREE SPACE
 *****************************************************************************************/

uint32_t rb_free_space(RingBuffer *rb)
{
    return rb->size - rb_available(rb) - 1;
}


/*****************************************************************************************
 * PERFORMANCE OPTIMIZATION
 *
 *  If buffer size is power‑of‑two:
 *
 *      size = 256
 *
 *  modulo operation can be replaced by bitmask:
 *
 *      index = (index + 1) & (size - 1)
 *
 *  which is significantly faster on many embedded CPUs.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * CACHE / FALSE SHARING CONSIDERATIONS
 *
 *  On multicore systems, head and tail should be placed in different cache lines.
 *
 *  Example:
 *
 *      struct {
 *          volatile uint32_t head;
 *          char padding[60];
 *          volatile uint32_t tail;
 *      };
 *
 *  This prevents cache line ping‑pong between cores.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  Safe because:
 *
 *      Producer only writes HEAD
 *      Consumer only writes TAIL
 *
 *  Both sides read the other pointer but never modify it.
 *
 *  This pattern guarantees lock‑free correctness for SPSC queues.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why is this queue lock‑free?
 *
 *    In SPSC design, producer owns head and consumer owns tail.
 *    Each shared index has a single writer, so lock ownership is simple.
 *
 * 2. Why must head and tail be volatile?
 *
 *    They are shared between asynchronous contexts.
 *    volatile prevents compiler-cached stale reads.
 *
 * 3. What happens if multiple producers push data?
 *
 *    Producers can race on head and corrupt queue state.
 *    Use atomics/CAS, mutexes, or per-producer queues.
 *
 * 4. How would you modify this queue for multi‑producer support?
 *
 * 5. Why is one slot intentionally unused in ring buffers?
 *
 *    One slot is left free so states are unambiguous:
 *    head == tail is empty, next(head) == tail is full.
 *
 *      (distinguish full vs empty)
 *
 * 6. Why prefer power‑of‑two buffer sizes?
 *
 *****************************************************************************************/

```

## 04_logging_subsystem_full.c

```c

/*****************************************************************************************
 *
 *  HIGH-SPEED LOGGING SUBSYSTEM (ASYNC TELEMETRY LOGGER)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  This module implements a non-blocking logging subsystem suitable for embedded systems.
 *
 *  Logging is often required for:
 *
 *      • debugging firmware
 *      • telemetry streaming
 *      • crash diagnostics
 *      • performance monitoring
 *
 *  However, naive logging implementations can severely impact system performance.
 *
 *  Example problem:
 *
 *      printf() inside interrupt
 *
 *  This causes:
 *
 *      • large latency
 *      • blocking I/O
 *      • possible deadlocks
 *
 *  Solution:
 *
 *      Use an asynchronous logging architecture.
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      PRODUCERS (tasks / ISRs)
 *              │
 *              ▼
 *        LOG RING BUFFER
 *              │
 *              ▼
 *      LOG CONSUMER TASK
 *              │
 *              ▼
 *           UART / SWO / FILE
 *
 *
 *  Key Idea:
 *
 *      Logging should NEVER block the application.
 *
 *
 *  ======================================================================================
 *  DATA FLOW
 *  ======================================================================================
 *
 *      Task A → log_write()
 *      Task B → log_write()
 *      ISR    → log_write()
 *
 *      All producers push messages into a shared ring buffer.
 *
 *      A dedicated consumer periodically flushes logs to output.
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>
#include <string.h>


/*****************************************************************************************
 * CONFIGURATION
 *****************************************************************************************/

#define LOG_BUFFER_SIZE 4096
#define LOG_MAX_MESSAGE 128


/*****************************************************************************************
 * LOG BUFFER STRUCTURE
 *****************************************************************************************/

typedef struct
{
    char buffer[LOG_BUFFER_SIZE];

    volatile uint32_t head;
    volatile uint32_t tail;

} LogBuffer;


/*****************************************************************************************
 * LOGGER DRIVER OBJECT
 *****************************************************************************************/

typedef struct
{
    LogBuffer ring;

    uint32_t dropped_messages;

} Logger;


/*****************************************************************************************
 * INITIALIZATION
 *****************************************************************************************/

void log_init(Logger *log)
{
    log->ring.head = 0;
    log->ring.tail = 0;

    log->dropped_messages = 0;
}


/*****************************************************************************************
 * NEXT INDEX HELPER
 *****************************************************************************************/

static inline uint32_t log_next(uint32_t index)
{
    return (index + 1) % LOG_BUFFER_SIZE;
}


/*****************************************************************************************
 * COMPUTE FREE SPACE
 *****************************************************************************************/

static uint32_t log_free_space(Logger *log)
{
    uint32_t head = log->ring.head;
    uint32_t tail = log->ring.tail;

    if (head >= tail)
        return LOG_BUFFER_SIZE - (head - tail) - 1;
    else
        return tail - head - 1;
}


/*****************************************************************************************
 * WRITE LOG MESSAGE
 *
 *  Producer API
 *
 *  This function copies a message into the ring buffer.
 *
 *****************************************************************************************/

int log_write(Logger *log, const char *msg)
{
    uint32_t len = strlen(msg);

    if (len > LOG_MAX_MESSAGE)
        len = LOG_MAX_MESSAGE;

    if (log_free_space(log) < len)
    {
        log->dropped_messages++;
        return -1;
    }

    for (uint32_t i = 0; i < len; i++)
    {
        log->ring.buffer[log->ring.head] = msg[i];
        log->ring.head = log_next(log->ring.head);
    }

    return 0;
}


/*****************************************************************************************
 * READ LOG BYTE
 *
 *  Consumer API
 *****************************************************************************************/

int log_read_byte(Logger *log, char *c)
{
    if (log->ring.head == log->ring.tail)
        return -1;

    *c = log->ring.buffer[log->ring.tail];

    log->ring.tail = log_next(log->ring.tail);

    return 0;
}


/*****************************************************************************************
 * FLUSH LOGS TO OUTPUT
 *
 *  Example consumer function.
 *
 *  In a real system this might send logs to:
 *
 *      • UART
 *      • USB
 *      • network
 *
 *****************************************************************************************/

void log_flush(Logger *log,
               void (*output_func)(char))
{
    char c;

    while (log_read_byte(log, &c) == 0)
    {
        output_func(c);
    }
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 *  Logging should not block application execution.
 *
 *  Recommended design:
 *
 *      log_write()  → very fast
 *      log_flush()  → slower operation
 *
 *  Flush may be triggered:
 *
 *      • periodically
 *      • low-priority task
 *      • idle loop
 *
 *****************************************************************************************/


/*****************************************************************************************
 * CACHE CONSIDERATIONS
 *
 *  If running on multicore systems:
 *
 *      head and tail should be on separate cache lines.
 *
 *  Example:
 *
 *      struct {
 *          volatile uint32_t head;
 *          char padding[60];
 *          volatile uint32_t tail;
 *      };
 *
 *  This avoids false sharing.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 *  Multiple producers writing concurrently can cause race conditions.
 *
 *  Solutions:
 *
 *      • atomic head updates
 *      • separate per-core buffers
 *      • mutex protection
 *
 *  Simpler embedded designs often use:
 *
 *      single producer + single consumer.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why should logging never block?
 *
 *    Blocking logs add latency and can break real-time behavior.
 *    Prefer enqueue-now and asynchronous flush.
 *
 * 2. What happens if log buffer fills?
 *
 *    Typical choices are dropping new logs or overwriting oldest logs.
 *    Track dropped-message counters for visibility.
 *
 * 3. How would you support multi-core logging?
 *
 * 4. How would you compress logs for telemetry?
 *
 * 5. Why avoid printf in ISR?
 *
 *    printf is expensive (formatting, possible locks, blocking I/O).
 *    ISR code should stay short to minimize interrupt latency.
 *
 *****************************************************************************************/


```

## 05_memory_pool_allocator_full.c

```c

/*****************************************************************************************
 *
 *  FIXED-SIZE MEMORY POOL ALLOCATOR (EMBEDDED SYSTEMS)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  Embedded systems often avoid malloc()/free() for several reasons:
 *
 *      • Unpredictable latency
 *      • Memory fragmentation
 *      • Non-deterministic behavior
 *
 *  Instead, drivers frequently use memory pools (also called object pools).
 *
 *  Memory pools provide:
 *
 *      • O(1) allocation
 *      • O(1) free
 *      • Deterministic execution time
 *      • No fragmentation
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *          MEMORY ARENA
 *
 *      +-------+-------+-------+-------+
 *      | blk0  | blk1  | blk2  | blk3  |
 *      +-------+-------+-------+-------+
 *
 *          ↓ linked using next pointers
 *
 *      blk0 → blk1 → blk2 → blk3 → NULL
 *
 *      free_list points to first free block
 *
 *
 *  ======================================================================================
 *  ALLOCATION MODEL
 *  ======================================================================================
 *
 *      pool_alloc():
 *
 *          remove first node from free_list
 *
 *
 *      pool_free():
 *
 *          push node back to free_list
 *
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>


/*****************************************************************************************
 * BLOCK HEADER
 *
 * Each block begins with a next pointer used to link free blocks together.
 *****************************************************************************************/

typedef struct PoolBlock
{
    struct PoolBlock *next;

} PoolBlock;


/*****************************************************************************************
 * MEMORY POOL STRUCTURE
 *****************************************************************************************/

typedef struct
{
    PoolBlock *free_list;

    uint8_t *arena;
    size_t block_size;
    size_t block_count;

} MemPool;


/*****************************************************************************************
 * INITIALIZE MEMORY POOL
 *
 * arena: preallocated memory region
 *
 * Example:
 *
 *      uint8_t buffer[1024];
 *
 *      pool_init(&pool, buffer, 32, 32);
 *
 *****************************************************************************************/

void pool_init(MemPool *pool,
               void *arena,
               size_t block_size,
               size_t block_count)
{
    pool->arena = (uint8_t*)arena;
    pool->block_size = block_size;
    pool->block_count = block_count;

    pool->free_list = NULL;

    for(size_t i = 0; i < block_count; i++)
    {
        PoolBlock *block =
            (PoolBlock*)(pool->arena + i * block_size);

        block->next = pool->free_list;

        pool->free_list = block;
    }
}


/*****************************************************************************************
 * ALLOCATE BLOCK
 *
 * Returns pointer to memory block or NULL if pool empty.
 *****************************************************************************************/

void *pool_alloc(MemPool *pool)
{
    PoolBlock *block = pool->free_list;

    if(block == NULL)
        return NULL;

    pool->free_list = block->next;

    return (void*)block;
}


/*****************************************************************************************
 * FREE BLOCK
 *****************************************************************************************/

void pool_free(MemPool *pool, void *ptr)
{
    PoolBlock *block = (PoolBlock*)ptr;

    block->next = pool->free_list;

    pool->free_list = block;
}


/*****************************************************************************************
 * POOL STATUS HELPERS
 *****************************************************************************************/

size_t pool_free_count(MemPool *pool)
{
    size_t count = 0;

    PoolBlock *curr = pool->free_list;

    while(curr)
    {
        count++;
        curr = curr->next;
    }

    return count;
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 * pool_alloc() and pool_free() are constant time operations.
 *
 * This makes memory pools ideal for:
 *
 *      • interrupt context
 *      • real-time systems
 *      • driver buffers
 *
 *****************************************************************************************/


/*****************************************************************************************
 * DMA CONSIDERATIONS
 *
 * If blocks will be used by DMA:
 *
 *      memory must be properly aligned.
 *
 * Example:
 *
 *      block_size = ALIGN_UP(block_size, 32);
 *
 * to match cache line size.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * CACHE COHERENCY NOTES
 *
 * If CPU cache is enabled and DMA accesses pool memory:
 *
 *      cache invalidate / flush operations may be required.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 * pool_alloc() and pool_free() modify free_list.
 *
 * If called from multiple contexts:
 *
 *      • protect with mutex
 *      • disable interrupts briefly
 *      • use atomic operations
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why are memory pools preferred in embedded drivers?
 *
 *    Pools provide deterministic O(1) allocate/free behavior.
 *    Unlike malloc, they avoid fragmentation-driven timing variability.
 *
 * 2. What problem does malloc() introduce?
 *
 *    malloc can introduce fragmentation and unpredictable allocation latency.
 *
 * 3. Why does this allocator avoid fragmentation?
 *
 *    All blocks are fixed-size and interchangeable.
 *    External fragmentation does not accumulate.
 *
 * 4. How would you support variable-sized allocations?
 *
 * 5. What changes if allocator is used in ISR?
 *
 *****************************************************************************************/

```

## 06_freelist_heap_allocator_full.c

```c

/*****************************************************************************************
 *
 *  VARIABLE-SIZE FREE LIST HEAP ALLOCATOR (EMBEDDED SYSTEMS)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  This module implements a simple variable-size heap allocator using a free-list.
 *
 *  Unlike fixed-size memory pools, this allocator supports allocating blocks of
 *  different sizes. It is similar in concept to malloc/free but simplified for
 *  embedded systems and educational purposes.
 *
 *  This design demonstrates key memory-management concepts commonly discussed in
 *  embedded and systems interviews:
 *
 *      • free list management
 *      • first-fit allocation
 *      • block splitting
 *      • block coalescing
 *      • fragmentation
 *
 *
 *  ======================================================================================
 *  MEMORY LAYOUT
 *  ======================================================================================
 *
 *      HEAP MEMORY REGION
 *
 *      +-----------+-----------+-----------+-----------+
 *      |  block A  |  block B  |  block C  |  block D  |
 *      +-----------+-----------+-----------+-----------+
 *
 *  Each block contains a header describing:
 *
 *      • block size
 *      • pointer to next free block
 *
 *
 *  ======================================================================================
 *  BLOCK HEADER FORMAT
 *  ======================================================================================
 *
 *      +---------------------+
 *      | size                |
 *      | next pointer        |
 *      +---------------------+
 *      | user memory         |
 *      | ...                 |
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>


/*****************************************************************************************
 * FREE BLOCK HEADER
 *****************************************************************************************/

typedef struct FreeBlock
{
    size_t size;
    struct FreeBlock *next;

} FreeBlock;


/*****************************************************************************************
 * HEAP STRUCTURE
 *****************************************************************************************/

typedef struct
{
    uint8_t *heap_start;
    size_t heap_size;

    FreeBlock *free_list;

} Heap;


/*****************************************************************************************
 * ALIGNMENT HELPER
 *****************************************************************************************/

#define ALIGNMENT 8

static size_t align_up(size_t size)
{
    return (size + (ALIGNMENT - 1)) & ~(ALIGNMENT - 1);
}


/*****************************************************************************************
 * INITIALIZE HEAP
 *****************************************************************************************/

void heap_init(Heap *heap, void *memory, size_t size)
{
    heap->heap_start = (uint8_t*)memory;
    heap->heap_size = size;

    heap->free_list = (FreeBlock*)memory;
    heap->free_list->size = size;
    heap->free_list->next = NULL;
}


/*****************************************************************************************
 * FIRST-FIT ALLOCATION
 *
 * Searches the free list for the first block large enough to satisfy request.
 *****************************************************************************************/

void *heap_alloc(Heap *heap, size_t size)
{
    size = align_up(size);

    FreeBlock *prev = NULL;
    FreeBlock *curr = heap->free_list;

    while(curr)
    {
        if(curr->size >= size + sizeof(FreeBlock))
        {
            /* Split block */
            uint8_t *block_mem = (uint8_t*)curr;

            FreeBlock *new_block =
                (FreeBlock*)(block_mem + sizeof(FreeBlock) + size);

            new_block->size =
                curr->size - sizeof(FreeBlock) - size;

            new_block->next = curr->next;

            if(prev)
                prev->next = new_block;
            else
                heap->free_list = new_block;

            curr->size = size;

            return block_mem + sizeof(FreeBlock);
        }

        prev = curr;
        curr = curr->next;
    }

    return NULL;
}


/*****************************************************************************************
 * COALESCE BLOCKS
 *
 * Merges adjacent free blocks to reduce fragmentation.
 *****************************************************************************************/

static void coalesce(Heap *heap)
{
    FreeBlock *curr = heap->free_list;

    while(curr && curr->next)
    {
        uint8_t *end =
            (uint8_t*)curr + sizeof(FreeBlock) + curr->size;

        if(end == (uint8_t*)curr->next)
        {
            curr->size += sizeof(FreeBlock) + curr->next->size;
            curr->next = curr->next->next;
        }
        else
        {
            curr = curr->next;
        }
    }
}


/*****************************************************************************************
 * FREE BLOCK
 *****************************************************************************************/

void heap_free(Heap *heap, void *ptr)
{
    if(ptr == NULL)
        return;

    FreeBlock *block =
        (FreeBlock*)((uint8_t*)ptr - sizeof(FreeBlock));

    block->next = heap->free_list;
    heap->free_list = block;

    coalesce(heap);
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 * Allocation complexity:
 *
 *      O(n) due to free list traversal.
 *
 * For small embedded heaps this is usually acceptable.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * FRAGMENTATION DISCUSSION
 *
 * External Fragmentation:
 *
 *      Free memory split into small blocks.
 *
 * Example:
 *
 *      [free 32] [alloc] [free 16] [alloc]
 *
 * Even if total free memory is large, large allocation may fail.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * DMA / CACHE CONSIDERATIONS
 *
 * If blocks are used for DMA:
 *
 *      alignment requirements must be satisfied.
 *
 * Example:
 *
 *      align to cache line (32 or 64 bytes).
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 * heap_alloc() and heap_free() modify the free list.
 *
 * If used in multitasking environment:
 *
 *      • protect with mutex
 *      • disable interrupts briefly
 *      • use lock-free allocator design
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. What is external fragmentation?
 *
 *    Free memory is split into non-contiguous chunks.
 *    Total free bytes may be enough, but no single block is large enough.
 *
 * 2. Difference between first-fit, best-fit, and worst-fit?
 *
 * 3. Why is heap allocation usually avoided in hard real-time systems?
 *
 *    Allocation time depends on free-list traversal/coalescing.
 *    That makes worst-case timing hard to guarantee.
 *
 * 4. How would you implement thread-safe malloc?
 *
 * 5. How do production allocators improve performance?
 *
 *****************************************************************************************/

```

## 07_spi_driver_full.c

```c

/*****************************************************************************************
 *
 *  SPI DRIVER IMPLEMENTATION (BLOCKING + INTERRUPT + DMA ARCHITECTURE OVERVIEW)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  SPI (Serial Peripheral Interface) is a synchronous serial communication protocol
 *  commonly used in embedded systems for high-speed peripheral communication.
 *
 *  Typical SPI peripherals:
 *
 *      • Flash memory
 *      • ADC / DAC devices
 *      • Sensors
 *      • Displays
 *      • Ethernet / WiFi chips
 *
 *
 *  SPI Characteristics
 *  -------------------
 *
 *      • Full-duplex communication
 *      • Master-slave architecture
 *      • Synchronous clocked protocol
 *      • High throughput
 *
 *
 *  ======================================================================================
 *  SPI SIGNALS
 *  ======================================================================================
 *
 *      MOSI  → Master Out Slave In
 *      MISO  → Master In Slave Out
 *      SCLK  → Serial Clock
 *      CS    → Chip Select
 *
 *
 *          MASTER                    SLAVE
 *
 *          MOSI  ───────────────────►
 *          MISO  ◄───────────────────
 *          SCLK  ───────────────────►
 *          CS    ───────────────────►
 *
 *
 *  ======================================================================================
 *  SPI MODES
 *  ======================================================================================
 *
 *  SPI uses two configuration bits:
 *
 *      CPOL → Clock polarity
 *      CPHA → Clock phase
 *
 *  Resulting modes:
 *
 *      Mode 0: CPOL=0 CPHA=0
 *      Mode 1: CPOL=0 CPHA=1
 *      Mode 2: CPOL=1 CPHA=0
 *      Mode 3: CPOL=1 CPHA=1
 *
 *
 *  ======================================================================================
 *  TRANSFER MODEL
 *  ======================================================================================
 *
 *      SPI is full-duplex.
 *
 *      When the master transmits a byte, the slave simultaneously returns a byte.
 *
 *
 *          TX byte → shift register → MOSI
 *                                  → MISO → RX byte
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>


/*****************************************************************************************
 * SPI STATUS FLAGS
 *****************************************************************************************/

#define SPI_SR_TXE   (1 << 1)   /* transmit buffer empty */
#define SPI_SR_RXNE  (1 << 0)   /* receive buffer not empty */
#define SPI_SR_BSY   (1 << 7)   /* SPI busy */


/*****************************************************************************************
 * SPI REGISTER MODEL
 *
 * Simplified register map for driver explanation.
 *****************************************************************************************/

typedef struct
{
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SR;
    volatile uint32_t DR;

} SPI_Regs;


/*****************************************************************************************
 * SPI DRIVER STRUCTURE
 *****************************************************************************************/

typedef struct
{
    SPI_Regs *regs;

} SPI_Driver;


/*****************************************************************************************
 * INITIALIZATION
 *****************************************************************************************/

void spi_init(SPI_Driver *drv, SPI_Regs *regs)
{
    drv->regs = regs;
}


/*****************************************************************************************
 * BLOCKING SPI TRANSFER
 *
 * Simplest SPI driver model.
 *
 * Steps:
 *
 *      1. Write byte to DR
 *      2. Wait RXNE flag
 *      3. Read received byte
 *
 *****************************************************************************************/

void spi_transfer_blocking(SPI_Driver *drv,
                           const uint8_t *tx,
                           uint8_t *rx,
                           size_t len)
{
    SPI_Regs *spi = drv->regs;

    for(size_t i = 0; i < len; i++)
    {
        while(!(spi->SR & SPI_SR_TXE));

        spi->DR = tx ? tx[i] : 0xFF;

        while(!(spi->SR & SPI_SR_RXNE));

        uint8_t data = spi->DR;

        if(rx)
            rx[i] = data;
    }

    while(spi->SR & SPI_SR_BSY);
}


/*****************************************************************************************
 * INTERRUPT-DRIVEN SPI MODEL (ARCHITECTURE)
 *
 * Instead of blocking transfers, interrupts can handle TX/RX.
 *
 * Architecture:
 *
 *      Application → queue transaction
 *                  → enable SPI interrupt
 *
 *      ISR:
 *          TXE → send next byte
 *          RXNE → read received byte
 *
 *****************************************************************************************/


/*****************************************************************************************
 * DMA-BASED SPI MODEL
 *
 * For large transfers, DMA can be used.
 *
 * Architecture:
 *
 *      Application
 *          │
 *          ▼
 *      Configure DMA descriptors
 *          │
 *          ▼
 *      DMA engine
 *          │
 *          ▼
 *      SPI peripheral
 *
 *
 *  Advantages:
 *
 *      • minimal CPU overhead
 *      • high throughput
 *      • ideal for large flash reads
 *
 *****************************************************************************************/


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 * Blocking transfers:
 *
 *      simple but wastes CPU cycles.
 *
 * Interrupt transfers:
 *
 *      better for moderate sized transfers.
 *
 * DMA transfers:
 *
 *      best for large high-speed transfers.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * CACHE / DMA COHERENCY
 *
 * If SPI DMA accesses cached memory:
 *
 *      CPU cache must be flushed before DMA transmit
 *      CPU cache must be invalidated after DMA receive
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 * SPI interrupts may interact with application code.
 *
 * Typical protection:
 *
 *      • disable SPI interrupts briefly
 *      • atomic state machine updates
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. What is full-duplex SPI communication?
 *
 *    SPI shifts one bit out and one bit in on each clock cycle.
 *    Transmit and receive happen simultaneously.
 *
 * 2. What are CPOL and CPHA?
 *
 * 3. When should DMA be used with SPI?
 *
 *    Use DMA for large transfers such as flash reads, display frames, or network payloads.
 *    This reduces CPU overhead.
 *
 * 4. Why might SPI transfers stall?
 *
 * 5. How would you support multiple SPI devices?
 *
 *****************************************************************************************/


```

## 08_i2c_driver_full.c

```c

/*****************************************************************************************
 *
 *  I2C DRIVER IMPLEMENTATION (ROBUST EMBEDDED VERSION)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  I2C (Inter-Integrated Circuit) is a synchronous serial protocol designed for
 *  communication between multiple chips on the same board.
 *
 *  Typical I2C peripherals:
 *
 *      • EEPROM
 *      • Sensors (temperature, IMU, pressure)
 *      • Power management ICs
 *      • RTC clocks
 *      • ADC/DAC converters
 *
 *
 *  Key Characteristics
 *  -------------------
 *
 *      • Two-wire interface (SDA, SCL)
 *      • Multi-master capable
 *      • Address-based communication
 *      • Half-duplex protocol
 *
 *
 *  ======================================================================================
 *  I2C SIGNALS
 *  ======================================================================================
 *
 *      SDA  → Serial Data
 *      SCL  → Serial Clock
 *
 *  Both lines are open-drain and require pull-up resistors.
 *
 *
 *          MASTER                    SLAVE
 *
 *          SDA  ────────────────────↔
 *          SCL  ────────────────────►
 *
 *
 *  ======================================================================================
 *  I2C TRANSACTION SEQUENCE
 *  ======================================================================================
 *
 *      START
 *        │
 *        ▼
 *      ADDRESS + R/W
 *        │
 *        ▼
 *      ACK
 *        │
 *        ▼
 *      DATA BYTES
 *        │
 *        ▼
 *      STOP
 *
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>


/*****************************************************************************************
 * I2C STATUS FLAGS (SIMPLIFIED)
 *****************************************************************************************/

#define I2C_SR_TXE   (1 << 7)   /* transmit register empty */
#define I2C_SR_RXNE  (1 << 6)   /* receive register not empty */
#define I2C_SR_BUSY  (1 << 1)   /* bus busy */
#define I2C_SR_BERR  (1 << 8)   /* bus error */
#define I2C_SR_ARLO  (1 << 9)   /* arbitration lost */
#define I2C_SR_AF    (1 << 10)  /* acknowledge failure */


/*****************************************************************************************
 * I2C REGISTER MODEL
 *****************************************************************************************/

typedef struct
{
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SR;
    volatile uint32_t DR;

} I2C_Regs;


/*****************************************************************************************
 * I2C DRIVER STRUCTURE
 *****************************************************************************************/

typedef struct
{
    I2C_Regs *regs;

} I2C_Driver;


/*****************************************************************************************
 * INITIALIZATION
 *****************************************************************************************/

void i2c_init(I2C_Driver *drv, I2C_Regs *regs)
{
    drv->regs = regs;
}


/*****************************************************************************************
 * START CONDITION
 *****************************************************************************************/

static void i2c_start(I2C_Driver *drv)
{
    drv->regs->CR1 |= (1 << 8); /* START bit */
}


/*****************************************************************************************
 * STOP CONDITION
 *****************************************************************************************/

static void i2c_stop(I2C_Driver *drv)
{
    drv->regs->CR1 |= (1 << 9); /* STOP bit */
}


/*****************************************************************************************
 * SEND BYTE
 *****************************************************************************************/

static void i2c_send_byte(I2C_Driver *drv, uint8_t data)
{
    I2C_Regs *i2c = drv->regs;

    while(!(i2c->SR & I2C_SR_TXE));

    i2c->DR = data;
}


/*****************************************************************************************
 * RECEIVE BYTE
 *****************************************************************************************/

static uint8_t i2c_recv_byte(I2C_Driver *drv)
{
    I2C_Regs *i2c = drv->regs;

    while(!(i2c->SR & I2C_SR_RXNE));

    return i2c->DR;
}


/*****************************************************************************************
 * WRITE TRANSACTION
 *
 * Example:
 *      write register of a sensor
 *****************************************************************************************/

int i2c_write(I2C_Driver *drv,
              uint8_t addr,
              const uint8_t *data,
              size_t len)
{
    i2c_start(drv);

    i2c_send_byte(drv, addr << 1); /* write address */

    for(size_t i = 0; i < len; i++)
    {
        i2c_send_byte(drv, data[i]);
    }

    i2c_stop(drv);

    return 0;
}


/*****************************************************************************************
 * READ TRANSACTION
 *****************************************************************************************/

int i2c_read(I2C_Driver *drv,
             uint8_t addr,
             uint8_t *data,
             size_t len)
{
    i2c_start(drv);

    i2c_send_byte(drv, (addr << 1) | 1); /* read address */

    for(size_t i = 0; i < len; i++)
    {
        data[i] = i2c_recv_byte(drv);
    }

    i2c_stop(drv);

    return 0;
}


/*****************************************************************************************
 * BUS RECOVERY
 *
 * Sometimes SDA is stuck low due to a crashed slave device.
 *
 * Recovery method:
 *
 *      Toggle SCL manually 9 times.
 *
 *****************************************************************************************/

void i2c_bus_recovery(void (*toggle_scl)(void))
{
    for(int i = 0; i < 9; i++)
    {
        toggle_scl();
    }
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 * I2C speeds:
 *
 *      Standard mode   → 100 kHz
 *      Fast mode       → 400 kHz
 *      Fast mode plus  → 1 MHz
 *
 * Compared to SPI, I2C is slower but requires fewer pins.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * CACHE / DMA CONSIDERATIONS
 *
 * Some MCUs support DMA for I2C transfers.
 *
 * If DMA is used:
 *
 *      flush cache before transmit
 *      invalidate cache after receive
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 * In interrupt-based drivers:
 *
 *      application and ISR share state machine.
 *
 * Protection strategies:
 *
 *      • atomic state updates
 *      • disabling interrupts briefly
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. What is clock stretching?
 *
 * 2. What happens during I2C arbitration?
 *
 * 3. Why are pull-up resistors required on SDA/SCL?
 *
 *    I2C lines are open-drain, so devices actively pull low only.
 *    Pull-up resistors restore logic-high on SDA/SCL.
 *
 * 4. What causes I2C bus lock?
 *
 *    A stuck device can hold SDA low after fault/incomplete transaction.
 *    Bus recovery clocks SCL manually to release the slave.
 *
 * 5. Why might SPI be preferred over I2C?
 *
 *****************************************************************************************/


```

## 09_timer_scheduler_full.c

```c

/*****************************************************************************************
 *
 *  SOFTWARE TIMER SCHEDULER (INTERRUPT-DRIVEN EMBEDDED DESIGN)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  Embedded systems often need timers for:
 *
 *      • periodic tasks
 *      • communication timeouts
 *      • scheduling work
 *      • retry mechanisms
 *
 *  Hardware timers usually generate periodic interrupts (for example every 1 ms).
 *
 *  A software timer scheduler builds on top of this interrupt to manage many timers.
 *
 *
 *  ======================================================================================
 *  ARCHITECTURE
 *  ======================================================================================
 *
 *      HARDWARE TIMER
 *            │
 *            ▼
 *      TIMER INTERRUPT (tick)
 *            │
 *            ▼
 *      SOFTWARE TIMER SCHEDULER
 *            │
 *            ▼
 *      TIMER CALLBACKS
 *
 *
 *  Example:
 *
 *      1 ms hardware tick
 *
 *      Timer A expires at 50 ticks
 *      Timer B expires at 120 ticks
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>


/*****************************************************************************************
 * CONFIGURATION
 *****************************************************************************************/

#define MAX_TIMERS 32


/*****************************************************************************************
 * TIMER CALLBACK TYPE
 *****************************************************************************************/

typedef void (*timer_callback_t)(void *arg);


/*****************************************************************************************
 * TIMER OBJECT
 *****************************************************************************************/

typedef struct
{
    uint32_t expiry;
    uint32_t period;

    timer_callback_t callback;
    void *arg;

    uint8_t active;

} Timer;


/*****************************************************************************************
 * TIMER SCHEDULER
 *****************************************************************************************/

typedef struct
{
    Timer timers[MAX_TIMERS];

    volatile uint32_t tick;

} TimerScheduler;


/*****************************************************************************************
 * INITIALIZATION
 *****************************************************************************************/

void timer_scheduler_init(TimerScheduler *sched)
{
    sched->tick = 0;

    for(int i = 0; i < MAX_TIMERS; i++)
    {
        sched->timers[i].active = 0;
    }
}


/*****************************************************************************************
 * CREATE TIMER
 *****************************************************************************************/

int timer_create(TimerScheduler *sched,
                 uint32_t delay,
                 uint32_t period,
                 timer_callback_t cb,
                 void *arg)
{
    for(int i = 0; i < MAX_TIMERS; i++)
    {
        if(!sched->timers[i].active)
        {
            Timer *t = &sched->timers[i];

            t->expiry = sched->tick + delay;
            t->period = period;

            t->callback = cb;
            t->arg = arg;

            t->active = 1;

            return i;
        }
    }

    return -1;
}


/*****************************************************************************************
 * STOP TIMER
 *****************************************************************************************/

void timer_stop(TimerScheduler *sched, int id)
{
    if(id < 0 || id >= MAX_TIMERS)
        return;

    sched->timers[id].active = 0;
}


/*****************************************************************************************
 * TIMER TICK HANDLER
 *
 *  Called from hardware timer interrupt.
 *****************************************************************************************/

void timer_tick_isr(TimerScheduler *sched)
{
    sched->tick++;

    for(int i = 0; i < MAX_TIMERS; i++)
    {
        Timer *t = &sched->timers[i];

        if(!t->active)
            continue;

        if(sched->tick >= t->expiry)
        {
            t->callback(t->arg);

            if(t->period)
                t->expiry += t->period;
            else
                t->active = 0;
        }
    }
}


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 * Current implementation:
 *
 *      O(N) timer scan each tick.
 *
 * For small systems this is acceptable.
 *
 * More scalable designs:
 *
 *      • timer wheel
 *      • min-heap priority queue
 *
 *****************************************************************************************/


/*****************************************************************************************
 * RACE CONDITION ANALYSIS
 *
 * timer_tick_isr() runs in interrupt context.
 *
 * If application modifies timers concurrently:
 *
 *      • disable interrupts briefly
 *      • use atomic updates
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why implement software timers instead of many hardware timers?
 *
 *    Hardware timers are limited resources.
 *    Software timers multiplex many deadlines on a shared hardware tick.
 *
 * 2. What is timer jitter?
 *
 *    Jitter is the difference between scheduled expiry and actual callback execution.
 *    Common causes are interrupt latency and scheduler delays.
 *
 * 3. What happens if callback execution time is long?
 *
 * 4. How would you scale to thousands of timers?
 *
 * 5. Difference between periodic and one-shot timers?
 *
 *****************************************************************************************/


```

## 10_driver_framework_full.c

```c

/*****************************************************************************************
 *
 *  GENERIC EMBEDDED DRIVER FRAMEWORK (ABSTRACTION LAYER)
 *
 *  ======================================================================================
 *  OVERVIEW
 *  ======================================================================================
 *
 *  Large embedded systems often contain many hardware peripherals:
 *
 *      • UART
 *      • SPI
 *      • I2C
 *      • Timers
 *      • ADC / DAC
 *      • DMA controllers
 *
 *  Without a structured framework, driver code becomes tightly coupled to
 *  hardware details and difficult to maintain.
 *
 *  A driver framework provides:
 *
 *      • Hardware abstraction
 *      • Uniform APIs
 *      • Device portability
 *      • Easier testing
 *
 *
 *  ======================================================================================
 *  LAYERED ARCHITECTURE
 *  ======================================================================================
 *
 *          APPLICATION
 *               │
 *               ▼
 *        DRIVER INTERFACE API
 *               │
 *               ▼
 *          DRIVER LAYER
 *               │
 *               ▼
 *         HARDWARE REGISTERS
 *
 *
 *  Example:
 *
 *      Application calls:
 *
 *          device_write(dev, data)
 *
 *      The framework routes this call to the correct driver implementation.
 *
 *
 *  ======================================================================================
 *  DRIVER MODEL
 *  ======================================================================================
 *
 *  Each driver provides a table of function pointers describing its operations.
 *
 *  This pattern is similar to:
 *
 *      • Linux kernel device drivers
 *      • C++ virtual functions
 *
 *****************************************************************************************/

#include <stdint.h>
#include <stddef.h>


/*****************************************************************************************
 * DRIVER OPERATIONS TABLE
 *
 * Each driver provides implementations for these operations.
 *****************************************************************************************/

typedef struct DriverOps
{
    int (*init)(void *dev);
    int (*read)(void *dev, void *buf, size_t len);
    int (*write)(void *dev, const void *buf, size_t len);
    int (*ioctl)(void *dev, int cmd, void *arg);

} DriverOps;


/*****************************************************************************************
 * GENERIC DEVICE OBJECT
 *
 * A device instance references:
 *
 *      • driver operations
 *      • device-specific context
 *
 *****************************************************************************************/

typedef struct Device
{
    const char *name;

    const DriverOps *ops;

    void *context;

} Device;


/*****************************************************************************************
 * DEVICE INITIALIZATION
 *****************************************************************************************/

int device_init(Device *dev)
{
    if (!dev || !dev->ops || !dev->ops->init)
        return -1;

    return dev->ops->init(dev->context);
}


/*****************************************************************************************
 * DEVICE READ API
 *****************************************************************************************/

int device_read(Device *dev, void *buf, size_t len)
{
    if (!dev || !dev->ops || !dev->ops->read)
        return -1;

    return dev->ops->read(dev->context, buf, len);
}


/*****************************************************************************************
 * DEVICE WRITE API
 *****************************************************************************************/

int device_write(Device *dev, const void *buf, size_t len)
{
    if (!dev || !dev->ops || !dev->ops->write)
        return -1;

    return dev->ops->write(dev->context, buf, len);
}


/*****************************************************************************************
 * DEVICE CONTROL API
 *
 * ioctl allows device-specific commands.
 *****************************************************************************************/

int device_ioctl(Device *dev, int cmd, void *arg)
{
    if (!dev || !dev->ops || !dev->ops->ioctl)
        return -1;

    return dev->ops->ioctl(dev->context, cmd, arg);
}


/*****************************************************************************************
 * EXAMPLE: UART DRIVER INTEGRATION
 *
 * A UART driver would implement these operations:
 *
 *      uart_init()
 *      uart_read()
 *      uart_write()
 *
 *****************************************************************************************/

typedef struct
{
    int baudrate;
} UART_Context;


int uart_driver_init(void *ctx)
{
    UART_Context *uart = (UART_Context*)ctx;
    (void)uart;
    return 0;
}


int uart_driver_read(void *ctx, void *buf, size_t len)
{
    (void)ctx;
    (void)buf;
    (void)len;
    return 0;
}


int uart_driver_write(void *ctx, const void *buf, size_t len)
{
    (void)ctx;
    (void)buf;
    return (int)len;
}


int uart_driver_ioctl(void *ctx, int cmd, void *arg)
{
    (void)ctx;
    (void)cmd;
    (void)arg;
    return 0;
}


/*****************************************************************************************
 * UART DRIVER OPERATIONS TABLE
 *****************************************************************************************/

static const DriverOps uart_ops =
{
    .init  = uart_driver_init,
    .read  = uart_driver_read,
    .write = uart_driver_write,
    .ioctl = uart_driver_ioctl
};


/*****************************************************************************************
 * DEVICE INSTANCE EXAMPLE
 *****************************************************************************************/

UART_Context uart0_ctx =
{
    .baudrate = 115200
};

Device uart0 =
{
    .name = "uart0",
    .ops = &uart_ops,
    .context = &uart0_ctx
};


/*****************************************************************************************
 * PERFORMANCE NOTES
 *
 * Function pointer dispatch introduces minimal overhead but greatly improves
 * modularity and code organization.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * CONCURRENCY / RACE CONDITIONS
 *
 * Device APIs may be called from:
 *
 *      • application tasks
 *      • interrupt handlers
 *      • background threads
 *
 * Drivers should ensure thread safety when accessing shared state.
 *
 *****************************************************************************************/


/*****************************************************************************************
 * DMA / CACHE CONSIDERATIONS
 *
 * Some drivers use DMA for high-speed transfers.
 *
 * When DMA interacts with cached memory:
 *
 *      • flush cache before transmit
 *      • invalidate cache after receive
 *
 *****************************************************************************************/


/*****************************************************************************************
 * INTERVIEW DISCUSSION QUESTIONS
 *
 * 1. Why use a driver abstraction layer?
 *
 *    It separates application logic from hardware-specific register details.
 *    This improves portability, maintainability, and testability.
 *
 * 2. How does this design improve portability?
 *
 * 3. How would you support multiple UART devices?
 *
 * 4. What are alternatives to function pointer based drivers?
 *
 * 5. How does Linux organize device drivers?
 *
 *****************************************************************************************/


```
