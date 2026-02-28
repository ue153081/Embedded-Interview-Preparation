# Wrapper API Questions and Solutions (Embedded Interview)

Format matches your other sheets: problem, full C code, complexity, follow-ups.

## W01) Register Read/Write Wrapper API
### Problem Statement
Design safe MMIO wrappers for 32-bit register read and write.
### Full C Code
```c
#include <stdint.h>

typedef volatile uint32_t vuint32_t;

static inline uint32_t reg_read32(const vuint32_t *base, uint32_t offset) {
    return *(const vuint32_t *)((const uint8_t *)base + offset);
}

static inline void reg_write32(vuint32_t *base, uint32_t offset, uint32_t value) {
    *(vuint32_t *)((uint8_t *)base + offset) = value;
}
```
### Complexity
- Read/Write: O(1)
### Interview Follow-ups
1. Why `volatile` is required and where it is not enough.
2. Endianness handling for multi-byte fields.

## W02) Safe Read-Modify-Write Wrapper
### Problem Statement
Implement `reg_rmw32` with mask update and critical-section hooks.
### Full C Code
```c
#include <stdint.h>

typedef volatile uint32_t vuint32_t;

typedef void (*lock_fn_t)(void);
typedef void (*unlock_fn_t)(void);

typedef struct {
    lock_fn_t lock;
    unlock_fn_t unlock;
} reg_lock_ops_t;

void reg_rmw32(vuint32_t *base,
               uint32_t offset,
               uint32_t mask,
               uint32_t value,
               const reg_lock_ops_t *ops) {
    if (ops && ops->lock) {
        ops->lock();
    }

    uint32_t cur = *(vuint32_t *)((uint8_t *)base + offset);
    cur = (cur & ~mask) | (value & mask);
    *(vuint32_t *)((uint8_t *)base + offset) = cur;

    if (ops && ops->unlock) {
        ops->unlock();
    }
}
```
### Complexity
- O(1)
### Interview Follow-ups
1. Why lock scope should be minimal.
2. When HW set/clear alias registers are better than RMW.

## W03) Bitfield Wrapper (`FIELD_PREP` / `FIELD_GET`)
### Problem Statement
Create reusable helpers to pack and extract bitfields safely.
### Full C Code
```c
#include <stdint.h>
#include <stdbool.h>

static inline uint32_t ctz32(uint32_t x) {
    uint32_t n = 0;
    while (((x >> n) & 1u) == 0u) {
        n++;
    }
    return n;
}

static inline bool field_mask_valid(uint32_t mask) {
    return mask != 0u;
}

static inline uint32_t field_prep(uint32_t mask, uint32_t value) {
    if (!field_mask_valid(mask)) {
        return 0u;
    }
    return (value << ctz32(mask)) & mask;
}

static inline uint32_t field_get(uint32_t mask, uint32_t reg) {
    if (!field_mask_valid(mask)) {
        return 0u;
    }
    return (reg & mask) >> ctz32(mask);
}
```
### Complexity
- O(1)
### Interview Follow-ups
1. Compile-time validation for constant masks.
2. Handling sparse/non-contiguous bit masks.

## W04) Poll-Until Wrapper with Timeout
### Problem Statement
Implement a generic polling API: wait until register satisfies condition or timeout.
### Full C Code
```c
#include <stdint.h>
#include <stdbool.h>

typedef volatile uint32_t vuint32_t;

typedef enum {
    POLL_OK = 0,
    POLL_TIMEOUT = -1
} poll_status_t;

typedef uint64_t (*time_us_fn_t)(void);

poll_status_t mmio_poll_until(const vuint32_t *base,
                              uint32_t offset,
                              uint32_t mask,
                              uint32_t expected,
                              uint32_t timeout_us,
                              time_us_fn_t now_us) {
    uint64_t start = now_us();
    uint64_t deadline = start + (uint64_t)timeout_us;

    while (now_us() <= deadline) {
        uint32_t v = *(const vuint32_t *)((const uint8_t *)base + offset);
        if ((v & mask) == expected) {
            return POLL_OK;
        }
    }
    return POLL_TIMEOUT;
}
```
### Complexity
- O(iterations until match/timeout)
### Interview Follow-ups
1. Busy-wait vs sleep-based polling.
2. Handling timer wraparound safely.

## W05) HAL Ops Wrapper (Platform + Mock Backend)
### Problem Statement
Design a generic UART wrapper using function pointers for portability and testing.
### Full C Code
```c
#include <stddef.h>
#include <stdint.h>

typedef enum {
    DRV_OK = 0,
    DRV_EINVAL = -1,
    DRV_EIO = -2
} drv_status_t;

typedef struct uart_dev uart_dev_t;

typedef struct {
    drv_status_t (*init)(uart_dev_t *dev, uint32_t baud);
    int (*read)(uart_dev_t *dev, uint8_t *buf, size_t len);
    int (*write)(uart_dev_t *dev, const uint8_t *buf, size_t len);
    drv_status_t (*ioctl)(uart_dev_t *dev, uint32_t cmd, uint32_t arg);
} uart_ops_t;

struct uart_dev {
    const uart_ops_t *ops;
    void *ctx;
};

drv_status_t uart_init(uart_dev_t *dev, uint32_t baud) {
    if (!dev || !dev->ops || !dev->ops->init) {
        return DRV_EINVAL;
    }
    return dev->ops->init(dev, baud);
}

int uart_write(uart_dev_t *dev, const uint8_t *buf, size_t len) {
    if (!dev || !dev->ops || !dev->ops->write || (!buf && len != 0u)) {
        return DRV_EINVAL;
    }
    return dev->ops->write(dev, buf, len);
}
```
### Complexity
- Dispatch: O(1)
### Interview Follow-ups
1. ABI-stable ops table versioning.
2. Dependency injection for unit tests.

## W06) Non-Blocking UART Async Write Wrapper
### Problem Statement
Implement async UART TX API with completion callback and cancel support.
### Full C Code
```c
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

typedef void (*uart_tx_done_cb_t)(void *user, int status, size_t sent);

typedef struct {
    const uint8_t *buf;
    size_t len;
    size_t pos;
    uart_tx_done_cb_t cb;
    void *user;
    bool active;
    bool cancel_req;
} uart_async_tx_t;

void uart_async_start(uart_async_tx_t *tx,
                      const uint8_t *buf,
                      size_t len,
                      uart_tx_done_cb_t cb,
                      void *user) {
    tx->buf = buf;
    tx->len = len;
    tx->pos = 0;
    tx->cb = cb;
    tx->user = user;
    tx->active = true;
    tx->cancel_req = false;
}

void uart_async_cancel(uart_async_tx_t *tx) {
    tx->cancel_req = true;
}

/* Call from UART TX empty ISR */
void uart_async_isr_pump(uart_async_tx_t *tx, volatile uint32_t *uart_dr) {
    if (!tx->active) {
        return;
    }
    if (tx->cancel_req) {
        tx->active = false;
        if (tx->cb) {
            tx->cb(tx->user, -1, tx->pos);
        }
        return;
    }

    if (tx->pos < tx->len) {
        *uart_dr = tx->buf[tx->pos++];
    }
    if (tx->pos == tx->len) {
        tx->active = false;
        if (tx->cb) {
            tx->cb(tx->user, 0, tx->len);
        }
    }
}
```
### Complexity
- Per ISR step: O(1)
### Interview Follow-ups
1. Ownership/lifetime of TX buffer.
2. Multiple queued writes design.

## W07) ISR-Safe UART RX Ring Wrapper
### Problem Statement
Build an ISR-safe wrapper for RX byte enqueue and task dequeue.
### Full C Code
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    uint8_t *buf;
    size_t cap;
    volatile size_t head;
    volatile size_t tail;
} spsc_ring_t;

static inline size_t rb_next(size_t idx, size_t cap) {
    return (idx + 1u) % cap;
}

bool spsc_push_isr(spsc_ring_t *r, uint8_t b) {
    size_t h = r->head;
    size_t n = rb_next(h, r->cap);
    if (n == r->tail) {
        return false;
    }
    r->buf[h] = b;
    r->head = n;
    return true;
}

bool spsc_pop_task(spsc_ring_t *r, uint8_t *out) {
    size_t t = r->tail;
    if (t == r->head) {
        return false;
    }
    *out = r->buf[t];
    r->tail = rb_next(t, r->cap);
    return true;
}
```
### Complexity
- Push/Pop: O(1)
### Interview Follow-ups
1. Memory barriers on SMP targets.
2. Drop-oldest overwrite mode.

## W08) SPI Transfer Wrapper (Blocking + Timeout)
### Problem Statement
Implement a generic SPI transfer wrapper with timeout and full-duplex semantics.
### Full C Code
```c
#include <stddef.h>
#include <stdint.h>

typedef volatile uint32_t vuint32_t;

typedef struct {
    vuint32_t *base;
    uint32_t dr_off;
    uint32_t sr_off;
    uint32_t txe_mask;
    uint32_t rxne_mask;
} spi_hw_t;

static inline uint32_t rd32(const vuint32_t *base, uint32_t off) {
    return *(const vuint32_t *)((const uint8_t *)base + off);
}

static inline void wr32(vuint32_t *base, uint32_t off, uint32_t v) {
    *(vuint32_t *)((uint8_t *)base + off) = v;
}

int spi_transfer_blocking(spi_hw_t *hw,
                          const uint8_t *tx,
                          uint8_t *rx,
                          size_t len,
                          uint32_t spin_limit) {
    for (size_t i = 0; i < len; ++i) {
        uint32_t spin = 0;
        while ((rd32(hw->base, hw->sr_off) & hw->txe_mask) == 0u) {
            if (++spin > spin_limit) {
                return -1;
            }
        }
        wr32(hw->base, hw->dr_off, tx ? tx[i] : 0xFFu);

        spin = 0;
        while ((rd32(hw->base, hw->sr_off) & hw->rxne_mask) == 0u) {
            if (++spin > spin_limit) {
                return -2;
            }
        }
        uint8_t v = (uint8_t)rd32(hw->base, hw->dr_off);
        if (rx) {
            rx[i] = v;
        }
    }
    return 0;
}
```
### Complexity
- O(len)
### Interview Follow-ups
1. CS handling for multi-segment transfers.
2. Async SPI wrapper with DMA.

## W09) I2C Transfer Wrapper with Retry + Recovery
### Problem Statement
Design an I2C wrapper that retries on NACK and invokes bus recovery hook.
### Full C Code
```c
#include <stddef.h>
#include <stdint.h>

typedef enum {
    I2C_OK = 0,
    I2C_ENACK = -1,
    I2C_ETIMEOUT = -2,
    I2C_EBUS = -3
} i2c_status_t;

typedef i2c_status_t (*i2c_xfer_impl_t)(uint8_t addr,
                                        const uint8_t *wbuf,
                                        size_t wlen,
                                        uint8_t *rbuf,
                                        size_t rlen);
typedef void (*i2c_bus_recover_fn_t)(void);

typedef struct {
    i2c_xfer_impl_t impl;
    i2c_bus_recover_fn_t recover;
    uint32_t max_retries;
} i2c_wrapper_t;

i2c_status_t i2c_transfer_retry(i2c_wrapper_t *w,
                                uint8_t addr,
                                const uint8_t *wbuf,
                                size_t wlen,
                                uint8_t *rbuf,
                                size_t rlen) {
    for (uint32_t attempt = 0; attempt <= w->max_retries; ++attempt) {
        i2c_status_t st = w->impl(addr, wbuf, wlen, rbuf, rlen);
        if (st == I2C_OK) {
            return I2C_OK;
        }
        if (st == I2C_ENACK) {
            continue;
        }
        if (w->recover) {
            w->recover();
        }
    }
    return I2C_EBUS;
}
```
### Complexity
- O(retries * transfer_size)
### Interview Follow-ups
1. Backoff strategy between retries.
2. Repeated-start transaction API shape.

## W10) DMA Submit/Complete Wrapper
### Problem Statement
Implement a DMA API that submits descriptors and completes via callback.
### Full C Code
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef void (*dma_done_cb_t)(void *user, int status);

typedef struct dma_desc {
    uintptr_t src;
    uintptr_t dst;
    size_t len;
    struct dma_desc *next;
} dma_desc_t;

typedef struct {
    dma_desc_t *head;
    dma_desc_t *tail;
    dma_done_cb_t cb;
    void *user;
    bool busy;
} dma_chan_t;

int dma_submit(dma_chan_t *ch, dma_desc_t *d, dma_done_cb_t cb, void *user) {
    if (!ch || !d || d->len == 0u) {
        return -1;
    }
    d->next = NULL;
    if (!ch->head) {
        ch->head = ch->tail = d;
    } else {
        ch->tail->next = d;
        ch->tail = d;
    }
    ch->cb = cb;
    ch->user = user;
    if (!ch->busy) {
        ch->busy = true;
        /* Program HW with ch->head here. */
    }
    return 0;
}

/* Call from DMA completion ISR */
void dma_complete_isr(dma_chan_t *ch, int hw_status) {
    if (!ch || !ch->head) {
        return;
    }
    ch->head = ch->head->next;
    if (!ch->head) {
        ch->tail = NULL;
        ch->busy = false;
    } else {
        /* Program next descriptor. */
    }
    if (ch->cb) {
        ch->cb(ch->user, hw_status);
    }
}
```
### Complexity
- Submit/complete: O(1)
### Interview Follow-ups
1. Descriptor ownership and lifetime rules.
2. Scatter-gather and chained descriptors.

## W11) DMA Cache Maintenance Wrapper
### Problem Statement
Provide wrappers around cache clean/invalidate for DMA-safe buffers.
### Full C Code
```c
#include <stddef.h>
#include <stdint.h>

typedef void (*cache_op_t)(void *addr, size_t len);

typedef struct {
    cache_op_t clean;
    cache_op_t invalidate;
} cache_ops_t;

typedef enum {
    DMA_DIR_TX = 0,
    DMA_DIR_RX = 1
} dma_dir_t;

int dma_cache_prepare(const cache_ops_t *ops, void *buf, size_t len, dma_dir_t dir) {
    if (!ops || !buf || len == 0u) {
        return -1;
    }
    if (dir == DMA_DIR_TX) {
        ops->clean(buf, len);
    } else {
        ops->invalidate(buf, len);
    }
    return 0;
}

int dma_cache_complete(const cache_ops_t *ops, void *buf, size_t len, dma_dir_t dir) {
    if (!ops || !buf || len == 0u) {
        return -1;
    }
    if (dir == DMA_DIR_RX) {
        ops->invalidate(buf, len);
    }
    return 0;
}
```
### Complexity
- O(cache-lines touched)
### Interview Follow-ups
1. Aligning to cache-line boundaries.
2. Behavior on cache-coherent interconnects.

## W12) IRQ Register/Enable/Dispatch Wrapper
### Problem Statement
Implement a wrapper API for ISR registration with shared IRQ support.
### Full C Code
```c
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#define IRQ_MAX        128
#define IRQ_CHAIN_MAX  4

typedef bool (*irq_fn_t)(void *arg); /* returns true if interrupt handled */

typedef struct {
    irq_fn_t fn;
    void *arg;
} irq_slot_t;

typedef struct {
    irq_slot_t chain[IRQ_MAX][IRQ_CHAIN_MAX];
} irq_table_t;

int irq_register(irq_table_t *tbl, uint32_t irq, irq_fn_t fn, void *arg) {
    if (!tbl || irq >= IRQ_MAX || !fn) {
        return -1;
    }
    for (uint32_t i = 0; i < IRQ_CHAIN_MAX; ++i) {
        if (!tbl->chain[irq][i].fn) {
            tbl->chain[irq][i].fn = fn;
            tbl->chain[irq][i].arg = arg;
            return 0;
        }
    }
    return -2;
}

bool irq_dispatch(irq_table_t *tbl, uint32_t irq) {
    if (!tbl || irq >= IRQ_MAX) {
        return false;
    }
    bool handled = false;
    for (uint32_t i = 0; i < IRQ_CHAIN_MAX; ++i) {
        irq_fn_t fn = tbl->chain[irq][i].fn;
        if (fn) {
            handled |= fn(tbl->chain[irq][i].arg);
        }
    }
    return handled;
}
```
### Complexity
- Register: O(chain length), Dispatch: O(chain length)
### Interview Follow-ups
1. Interrupt affinity on SMP.
2. Spurious IRQ accounting.

## W13) Defer-From-ISR Wrapper
### Problem Statement
Implement a lightweight deferred-work wrapper so ISR can schedule bottom-half work.
### Full C Code
```c
#include <stdbool.h>
#include <stddef.h>

typedef void (*work_fn_t)(void *arg);

typedef struct {
    work_fn_t fn;
    void *arg;
} work_item_t;

typedef struct {
    work_item_t *q;
    size_t cap;
    volatile size_t head;
    volatile size_t tail;
} work_queue_t;

static inline size_t wq_next(size_t x, size_t cap) {
    return (x + 1u) % cap;
}

bool defer_from_isr(work_queue_t *wq, work_fn_t fn, void *arg) {
    size_t h = wq->head;
    size_t n = wq_next(h, wq->cap);
    if (n == wq->tail) {
        return false;
    }
    wq->q[h].fn = fn;
    wq->q[h].arg = arg;
    wq->head = n;
    return true;
}

void workqueue_run_once(work_queue_t *wq) {
    size_t t = wq->tail;
    if (t == wq->head) {
        return;
    }
    work_item_t it = wq->q[t];
    wq->tail = wq_next(t, wq->cap);
    if (it.fn) {
        it.fn(it.arg);
    }
}
```
### Complexity
- Enqueue/Dequeue: O(1)
### Interview Follow-ups
1. Priority-based deferred queues.
2. Backpressure when deferred queue is full.

## W14) Managed Resource Wrapper (Auto Cleanup on Failure)
### Problem Statement
Implement a wrapper to register cleanup callbacks and unwind on errors.
### Full C Code
```c
#include <stddef.h>

#define RES_MAX 16

typedef void (*cleanup_fn_t)(void *ctx);

typedef struct {
    cleanup_fn_t fn;
    void *ctx;
} resource_t;

typedef struct {
    resource_t items[RES_MAX];
    size_t count;
} resource_group_t;

int resource_add(resource_group_t *g, cleanup_fn_t fn, void *ctx) {
    if (!g || !fn || g->count >= RES_MAX) {
        return -1;
    }
    g->items[g->count].fn = fn;
    g->items[g->count].ctx = ctx;
    g->count++;
    return 0;
}

void resource_release_all(resource_group_t *g) {
    if (!g) {
        return;
    }
    while (g->count > 0u) {
        g->count--;
        g->items[g->count].fn(g->items[g->count].ctx);
    }
}
```
### Complexity
- Add: O(1), Release-all: O(n)
### Interview Follow-ups
1. Ordering guarantees for dependent resources.
2. Handling partial init in probe sequence.

## W15) Driver Open/Close Wrapper with Refcount
### Problem Statement
Design an API ensuring first-open initializes hardware and last-close deinitializes.
### Full C Code
```c
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    int refcnt;
    bool initialized;
} drv_state_t;

static int hw_init(void) { return 0; }
static void hw_deinit(void) {}

int drv_open(drv_state_t *s) {
    if (!s) return -1;
    if (s->refcnt == 0) {
        int rc = hw_init();
        if (rc != 0) return rc;
        s->initialized = true;
    }
    s->refcnt++;
    return 0;
}

int drv_close(drv_state_t *s) {
    if (!s || s->refcnt <= 0) return -1;
    s->refcnt--;
    if (s->refcnt == 0 && s->initialized) {
        hw_deinit();
        s->initialized = false;
    }
    return 0;
}
```
### Complexity
- Open/Close: O(1)
### Interview Follow-ups
1. Thread safety around refcount.
2. Forced-close on process crash.

## W16) Error Mapping Wrapper
### Problem Statement
Map hardware/vendor-specific status codes to unified driver error codes.
### Full C Code
```c
#include <stdint.h>

typedef enum {
    E_OK = 0,
    E_TIMEOUT = -1,
    E_BUSY = -2,
    E_IO = -3,
    E_INVALID = -4
} status_t;

typedef enum {
    HW_ST_OK = 0x00,
    HW_ST_TO = 0x10,
    HW_ST_ARB_LOST = 0x11,
    HW_ST_NACK = 0x12,
    HW_ST_BAD_ARG = 0x20
} hw_status_t;

status_t map_hw_status(hw_status_t hw) {
    switch (hw) {
        case HW_ST_OK:
            return E_OK;
        case HW_ST_TO:
            return E_TIMEOUT;
        case HW_ST_ARB_LOST:
        case HW_ST_NACK:
            return E_BUSY;
        case HW_ST_BAD_ARG:
            return E_INVALID;
        default:
            return E_IO;
    }
}
```
### Complexity
- O(1)
### Interview Follow-ups
1. Preserving root-cause details while returning generic codes.
2. Error domains across layers.

## W17) Retry + Exponential Backoff Wrapper
### Problem Statement
Create a wrapper that retries transient operations with backoff.
### Full C Code
```c
#include <stdint.h>

typedef int (*op_fn_t)(void *ctx); /* 0 success, negative failure */
typedef void (*sleep_us_fn_t)(uint32_t us);

int retry_backoff(op_fn_t op,
                  void *ctx,
                  uint32_t max_retries,
                  uint32_t base_delay_us,
                  sleep_us_fn_t sleep_us) {
    uint32_t delay = base_delay_us;

    for (uint32_t i = 0; i <= max_retries; ++i) {
        int rc = op(ctx);
        if (rc == 0) {
            return 0;
        }
        if (i == max_retries) {
            return rc;
        }
        sleep_us(delay);
        if (delay < (UINT32_MAX / 2u)) {
            delay *= 2u;
        }
    }
    return -1;
}
```
### Complexity
- O(retries)
### Interview Follow-ups
1. Jitter to avoid thundering herd.
2. Retry only for transient error classes.

## W18) Power/Clock Wrapper (`pm_get` / `pm_put`)
### Problem Statement
Implement reference-counted power/clock gating wrappers.
### Full C Code
```c
#include <stdbool.h>

typedef struct {
    int users;
    bool clock_on;
    bool power_on;
} pm_state_t;

static int hw_power_on(void) { return 0; }
static int hw_clock_on(void) { return 0; }
static void hw_clock_off(void) {}
static void hw_power_off(void) {}

int pm_get(pm_state_t *s) {
    if (!s) return -1;
    if (s->users == 0) {
        if (hw_power_on() != 0) return -2;
        s->power_on = true;
        if (hw_clock_on() != 0) {
            hw_power_off();
            s->power_on = false;
            return -3;
        }
        s->clock_on = true;
    }
    s->users++;
    return 0;
}

void pm_put(pm_state_t *s) {
    if (!s || s->users <= 0) {
        return;
    }
    s->users--;
    if (s->users == 0) {
        if (s->clock_on) {
            hw_clock_off();
            s->clock_on = false;
        }
        if (s->power_on) {
            hw_power_off();
            s->power_on = false;
        }
    }
}
```
### Complexity
- O(1)
### Interview Follow-ups
1. Runtime PM autosuspend timers.
2. Wakeup source handling.

## W19) Silicon-Revision Abstraction Wrapper
### Problem Statement
Support SoC revision differences behind one stable API.
### Full C Code
```c
#include <stdint.h>

typedef enum {
    SOC_REV_A = 0,
    SOC_REV_B = 1
} soc_rev_t;

typedef struct {
    uint32_t ctrl_off;
    uint32_t status_off;
    uint32_t start_mask;
} reg_layout_t;

static const reg_layout_t LAYOUT_A = {
    .ctrl_off = 0x10,
    .status_off = 0x14,
    .start_mask = 1u << 0
};

static const reg_layout_t LAYOUT_B = {
    .ctrl_off = 0x20,
    .status_off = 0x24,
    .start_mask = 1u << 3
};

const reg_layout_t *get_layout(soc_rev_t rev) {
    return (rev == SOC_REV_B) ? &LAYOUT_B : &LAYOUT_A;
}
```
### Complexity
- O(1)
### Interview Follow-ups
1. Capability flags vs revision checks.
2. Backward compatibility testing strategy.

## W20) Telemetry Wrapper for Driver Health
### Problem Statement
Implement a wrapper API to collect driver metrics (errors, timeouts, drops).
### Full C Code
```c
#include <stdint.h>
#include <string.h>

typedef struct {
    uint32_t tx_ok;
    uint32_t rx_ok;
    uint32_t timeouts;
    uint32_t retries;
    uint32_t drops;
    uint32_t isr_overruns;
} drv_metrics_t;

void metrics_reset(drv_metrics_t *m) {
    memset(m, 0, sizeof(*m));
}

void metrics_inc_tx_ok(drv_metrics_t *m) { m->tx_ok++; }
void metrics_inc_rx_ok(drv_metrics_t *m) { m->rx_ok++; }
void metrics_inc_timeout(drv_metrics_t *m) { m->timeouts++; }
void metrics_inc_retry(drv_metrics_t *m) { m->retries++; }
void metrics_inc_drop(drv_metrics_t *m) { m->drops++; }
void metrics_inc_isr_overrun(drv_metrics_t *m) { m->isr_overruns++; }

void metrics_snapshot(const drv_metrics_t *m, drv_metrics_t *out) {
    *out = *m;
}
```
### Complexity
- Counter updates: O(1)
### Interview Follow-ups
1. Atomic counters for multi-core access.
2. Export format for field diagnostics.

