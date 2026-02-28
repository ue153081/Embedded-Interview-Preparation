# Topic 9 — System, MMIO, IPC, and Low-Level Interview Solutions (Q109-Q122)

## Q109: Register map abstraction layer (HAL)
### 1. Problem Statement
Create typed register read/write helpers.
### 2. Assumptions
- Memory-mapped registers use `volatile`.
### 3. Full C Code
```c
#include <stdint.h>

static inline uint32_t reg_read32(volatile uint32_t *reg) {
    return *reg;
}

static inline void reg_write32(volatile uint32_t *reg, uint32_t val) {
    *reg = val;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Why `volatile` required?
2. Why `volatile` alone is insufficient for synchronization?

## Q110: Safe register read-modify-write API
### 1. Problem Statement
Update masked bitfields safely.
### 2. Assumptions
- Caller ensures mutual exclusion if shared.
### 3. Full C Code
```c
static inline void reg_rmw32(volatile uint32_t *reg, uint32_t mask, uint32_t val) {
    uint32_t cur = *reg;
    cur = (cur & ~mask) | (val & mask);
    *reg = cur;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. RMW race with ISR/task?
2. Use set/clear alias registers if available?

## Q111: Atomic register access (ISR + task shared peripheral)
### 1. Problem Statement
Protect shared register updates.
### 2. Assumptions
- Critical section primitive available.
### 3. Full C Code
```c
void reg_rmw_protected(volatile uint32_t *reg, uint32_t mask, uint32_t val) {
    /* disable_irq(); */
    reg_rmw32(reg, mask, val);
    /* enable_irq(); */
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Critical section duration minimization?
2. SMP-safe alternative (spinlock)?

## Q112: Interrupt controller abstraction (register/enable/dispatch)
### 1. Problem Statement
Register handlers and dispatch by vector.
### 2. Assumptions
- Fixed max vectors.
### 3. Full C Code
```c
typedef void (*irq_handler_t)(void *arg);

typedef struct {
    irq_handler_t fn[128];
    void *arg[128];
} IrqController;

void irq_register(IrqController *ic, int vector, irq_handler_t h, void *arg) {
    ic->fn[vector] = h;
    ic->arg[vector] = arg;
}

void irq_dispatch(IrqController *ic, int vector) {
    if (ic->fn[vector]) {
        ic->fn[vector](ic->arg[vector]);
    }
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Spurious interrupt handling?
2. Shared IRQ fan-out model?

## Q113: Mailbox IPC driver (dual-core)
### 1. Problem Statement
Queue messages and notify peer core.
### 2. Assumptions
- Doorbell register write triggers interrupt.
### 3. Full C Code
```c
typedef struct {
    uint32_t cmd;
    uint32_t arg;
} MailMsg;

typedef struct {
    MailMsg *q;
    uint32_t cap;
    uint32_t head;
    uint32_t tail;
    volatile uint32_t *doorbell;
} Mailbox;

int mailbox_send(Mailbox *m, MailMsg msg) {
    uint32_t n = (m->head + 1u) % m->cap;
    if (n == m->tail) {
        return -1;
    }
    m->q[m->head] = msg;
    m->head = n;
    *m->doorbell = 1u;
    return 0;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Ack/sequence design?
2. Peer reset recovery?

## Q114: Shared-memory IPC ring with memory barriers
### 1. Problem Statement
Publish/consume messages with ordering guarantees.
### 2. Assumptions
- Producer and consumer on different cores.
### 3. Full C Code
```c
#include <stdatomic.h>

typedef struct {
    uint32_t payload;
} IpcMsg;

typedef struct {
    IpcMsg *buf;
    uint32_t cap;
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
} IpcRing;

int ipc_push(IpcRing *r, IpcMsg msg) {
    uint32_t h = atomic_load_explicit(&r->head, memory_order_relaxed);
    uint32_t t = atomic_load_explicit(&r->tail, memory_order_acquire);
    uint32_t n = (h + 1u) % r->cap;
    if (n == t) {
        return -1;
    }
    r->buf[h] = msg;
    atomic_store_explicit(&r->head, n, memory_order_release);
    return 0;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Non-coherent cache maintenance?
2. Cross-core interrupt signaling?

## Q115: Firmware logging subsystem (ring + backpressure)
### 1. Problem Statement
Non-blocking log storage with overflow policy.
### 2. Assumptions
- Drop-oldest policy.
### 3. Full C Code
```c
typedef struct {
    uint32_t ts;
    uint8_t level;
    uint16_t id;
} LogRec;

typedef struct {
    LogRec *buf;
    uint32_t cap;
    uint32_t head;
    uint32_t tail;
    uint32_t dropped;
} LogRing;

void log_push(LogRing *l, LogRec r) {
    uint32_t n = (l->head + 1u) % l->cap;
    if (n == l->tail) {
        l->tail = (l->tail + 1u) % l->cap;
        l->dropped++;
    }
    l->buf[l->head] = r;
    l->head = n;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. ISR-safe logging constraints?
2. Log flush strategy on crash?

## Q116: Crash-dump buffer with persistent header/checksum
### 1. Problem Statement
Store crash records in reserved memory region.
### 2. Assumptions
- Header includes validity marker.
### 3. Full C Code
```c
typedef struct {
    uint32_t magic;
    uint32_t len;
    uint32_t crc;
} DumpHeader;

void dump_commit(DumpHeader *h, uint32_t len, uint32_t crc) {
    h->len = len;
    h->crc = crc;
    h->magic = 0x44554D50u; /* 'DUMP' */
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Power-loss consistency?
2. Multi-dump ring design?

## Q117: Event-driven finite state machine engine
### 1. Problem Statement
Process events through explicit state transitions.
### 2. Assumptions
- Small enum state/event sets.
### 3. Full C Code
```c
typedef enum {
    ST_IDLE,
    ST_BUSY,
    ST_ERR
} State;

typedef enum {
    EV_START,
    EV_DONE,
    EV_FAIL,
    EV_RESET
} Event;

State fsm_step(State s, Event e) {
    if (s == ST_IDLE && e == EV_START) return ST_BUSY;
    if (s == ST_BUSY && e == EV_DONE) return ST_IDLE;
    if (s == ST_BUSY && e == EV_FAIL) return ST_ERR;
    if (s == ST_ERR && e == EV_RESET) return ST_IDLE;
    return s;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Table-driven FSM benefits?
2. How to test transition coverage?

## Q118: Telemetry pipeline (batch + retry + drop policy)
### 1. Problem Statement
Queue telemetry records, batch send, retry on transient errors.
### 2. Assumptions
- Bounded queue.
### 3. Full C Code
```c
int telemetry_enqueue(uint8_t *q, int *sz, int cap, uint8_t rec) {
    if (*sz >= cap) {
        return -1;
    }
    q[*sz] = rec;
    (*sz)++;
    return 0;
}
```
### 4. Complexity
- Enqueue O(1)
### 5. Interview Follow-ups
1. Drop newest vs oldest?
2. Retry jitter and max age?

## Q119: Bootloader update state machine (basic A/B flow)
### 1. Problem Statement
Model download/verify/switch/rollback flow.
### 2. Assumptions
- A/B slots tracked externally.
### 3. Full C Code
```c
typedef enum {
    BL_IDLE,
    BL_DOWNLOAD,
    BL_VERIFY,
    BL_SWITCH,
    BL_ROLLBACK
} BlState;

BlState bl_step(BlState s, int event) {
    if (s == BL_IDLE && event == 1) return BL_DOWNLOAD;
    if (s == BL_DOWNLOAD && event == 2) return BL_VERIFY;
    if (s == BL_VERIFY && event == 3) return BL_SWITCH;
    if (event < 0) return BL_ROLLBACK;
    return s;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Power-fail rollback safety?
2. Slot metadata integrity checks?

## Q120: Safe atoi with overflow/invalid input handling
### 1. Problem Statement
Parse signed int with strict validation.
### 2. Assumptions
- Base-10 only.
### 3. Full C Code
```c
#include <limits.h>

int safe_atoi10(const char *s, int *out) {
    long v = 0;
    int sign = 1;

    if (!s || !out) {
        return -1;
    }

    if (*s == '-') {
        sign = -1;
        s++;
    }

    if (*s == '\0') {
        return -1;
    }

    while (*s) {
        if (*s < '0' || *s > '9') {
            return -1;
        }
        v = v * 10 + (*s - '0');
        if (sign * v > INT_MAX || sign * v < INT_MIN) {
            return -1;
        }
        s++;
    }

    *out = (int)(sign * v);
    return 0;
}
```
### 4. Complexity
- O(n)
### 5. Interview Follow-ups
1. Leading/trailing spaces policy?
2. Base/radix extension?

## Q121: Correct memmove (overlap-safe) + optimized memcpy
### 1. Problem Statement
Implement safe overlap move and basic copy.
### 2. Assumptions
- Byte copy baseline.
### 3. Full C Code
```c
#include <stddef.h>
#include <stdint.h>

void *my_memcpy(void *dst, const void *src, size_t n) {
    uint8_t *d = (uint8_t *)dst;
    const uint8_t *s = (const uint8_t *)src;

    for (size_t i = 0; i < n; i++) {
        d[i] = s[i];
    }
    return dst;
}

void *my_memmove(void *dst, const void *src, size_t n) {
    uint8_t *d = (uint8_t *)dst;
    const uint8_t *s = (const uint8_t *)src;

    if (d < s) {
        for (size_t i = 0; i < n; i++) {
            d[i] = s[i];
        }
    } else if (d > s) {
        for (size_t i = n; i > 0; i--) {
            d[i - 1] = s[i - 1];
        }
    }
    return dst;
}
```
### 4. Complexity
- O(n)
### 5. Interview Follow-ups
1. Word-copy optimization conditions?
2. Alignment and UB concerns?

## Q122: Framed packet parser (length, CRC, stream resync)
### 1. Problem Statement
Parse byte stream with framing and checksum.
### 2. Assumptions
- Frame format: SOF, LEN, PAYLOAD, CRC.
### 3. Full C Code
```c
typedef enum {
    P_SOF,
    P_LEN,
    P_PAYLOAD,
    P_CRC
} ParseState;

typedef struct {
    ParseState st;
    uint8_t len;
    uint8_t idx;
    uint8_t crc;
    uint8_t payload[256];
} Parser;

int parser_feed(Parser *p, uint8_t b) {
    switch (p->st) {
        case P_SOF:
            if (b == 0xAAu) {
                p->st = P_LEN;
                p->crc = 0u;
            }
            break;
        case P_LEN:
            p->len = b;
            p->idx = 0u;
            p->st = P_PAYLOAD;
            break;
        case P_PAYLOAD:
            p->payload[p->idx++] = b;
            p->crc ^= b;
            if (p->idx == p->len) {
                p->st = P_CRC;
            }
            break;
        case P_CRC:
            p->st = P_SOF;
            return (p->crc == b) ? 1 : -1;
    }
    return 0;
}
```
### 4. Complexity
- O(n)
### 5. Interview Follow-ups
1. Resync strategy on corruption?
2. Max frame length hardening?
