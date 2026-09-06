# Rings, Queues & Buffers

**IDs:** C071–C090 (20 questions)  
**Focus:** SPSC/MPSC rings, overwrite policies, DMA contiguous APIs, watermarks.

[← Back to category index](./README.md)

---

### C071 — SPSC byte ring buffer

**Interview prompt:**  
Implement a single-producer single-consumer circular byte buffer (classic embedded interview).

**Implement:**
```c
typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
void ring_init(ring_t *r, uint8_t *buf, size_t cap);
size_t ring_push(ring_t *r, const uint8_t *src, size_t n);
size_t ring_pop(ring_t *r, uint8_t *dst, size_t n);
size_t ring_count(const ring_t *r);
```

**Constraints / expectations:**
- Define full vs empty clearly
- Document if capacity is cap or cap-1

**Follow-ups:**
- ISR producer safety
- Power-of-two optimize

---

### C072 — Power-of-two ring with mask

**Interview prompt:**  
Implement a ring that requires capacity power-of-two and uses bitmask indexing.

**Implement:**
```c
/* same API; assert pow2 capacity */
```

**Constraints / expectations:**
- Faster index math
- Prove full/empty logic

**Follow-ups:**
- Why force pow2?
- Memory waste?

---

### C073 — Count-field vs spare-slot ring

**Interview prompt:**  
Implement both full/empty strategies and explain tradeoffs.

**Implement:**
```c
/* spare-slot version and count version */
```

**Constraints / expectations:**
- Correct under concurrent SPSC assumptions you state
- Compare RAM/CPU

**Follow-ups:**
- Which for ISR?
- Atomicity of count?

---

### C074 — Overwrite-oldest ring

**Interview prompt:**  
Telemetry ring that always accepts new data by dropping the oldest bytes/records.

**Implement:**
```c
size_t ring_push_overwrite(ring_t *r, const uint8_t *src, size_t n);
```

**Constraints / expectations:**
- Never fails push (unless n>cap)
- Update read index correctly

**Follow-ups:**
- Record-oriented overwrite
- Notify reader of drops

---

### C075 — Discard-newest on full

**Interview prompt:**  
Opposite policy: if ring full, drop incoming data and count drops.

**Implement:**
```c
size_t ring_push_drop_newest(ring_t *r, const uint8_t *src, size_t n);
size_t ring_drop_count(const ring_t *r);
```

**Constraints / expectations:**
- Track drops
- Partial push policy documented

**Follow-ups:**
- When choose this vs overwrite?
- Backpressure signal

---

### C076 — Peek and skip

**Interview prompt:**  
Add non-destructive peek and skip APIs to the ring.

**Implement:**
```c
size_t ring_peek(const ring_t *r, uint8_t *dst, size_t n);
size_t ring_skip(ring_t *r, size_t n);
```

**Constraints / expectations:**
- peek doesn't advance
- skip <= count

**Follow-ups:**
- Zero-copy peek pointer API
- Wrap issues

---

### C077 — Contiguous read slice for DMA

**Interview prompt:**  
Return the largest contiguous unread region pointer+length (may be less than total available due to wrap).

**Implement:**
```c
size_t ring_contig_read(const ring_t *r, const uint8_t **ptr);
```

**Constraints / expectations:**
- Does not advance indices
- Pair with skip after DMA/consume

**Follow-ups:**
- Contiguous write space API
- DMA half-complete

---

### C078 — Reserve/commit write API

**Interview prompt:**  
Producer reserves contiguous space, fills it, then commits.

**Implement:**
```c
size_t ring_reserve(ring_t *r, uint8_t **ptr);
void ring_commit(ring_t *r, size_t n);
```

**Constraints / expectations:**
- commit <= reserved
- Handle wrap (maybe reserve only contig)

**Follow-ups:**
- Abort reserve?
- Multi-reserve?

---

### C079 — Typed element ring

**Interview prompt:**  
Circular queue of fixed-size structs (e.g., events), not raw bytes.

**Implement:**
```c
typedef struct { uint32_t id; int32_t val; } event_t;
typedef struct event_ring event_ring_t;
int event_ring_push(event_ring_t *r, const event_t *e);
int event_ring_pop(event_ring_t *r, event_t *e);
```

**Constraints / expectations:**
- By value copy semantics
- Full/empty codes

**Follow-ups:**
- Zero-copy slot API
- ISR push

---

### C080 — MPSC queue with locking

**Interview prompt:**  
Multiple producers, single consumer queue protected by a lock/critical section.

**Implement:**
```c
int mpsc_push(mpsc_t *q, const event_t *e);
int mpsc_pop(mpsc_t *q, event_t *e);
```

**Constraints / expectations:**
- Document IRQ safety of lock
- No lost wakeups if combined with waiting

**Follow-ups:**
- Lock-free MPSC hard—discuss
- Priority producers

---

### C081 — Priority event queues

**Interview prompt:**  
Implement multi-priority FIFOs with a bitmap to find highest priority non-empty queue.

**Implement:**
```c
int prio_push(prio_q_t *q, unsigned prio, const event_t *e);
int prio_pop_highest(prio_q_t *q, event_t *e);
```

**Constraints / expectations:**
- prio range small (e.g. 0..31)
- O(1) find with bitmap + ffs

**Follow-ups:**
- Starvation of low prio
- Aging

---

### C082 — Ping-pong double buffer

**Interview prompt:**  
Implement producer/consumer handoff using two buffers and an ownership flag/index.

**Implement:**
```c
uint8_t *dbuf_write_begin(dbuf_t *d);
void dbuf_write_end(dbuf_t *d);
const uint8_t *dbuf_read_begin(dbuf_t *d);
void dbuf_read_end(dbuf_t *d);
```

**Constraints / expectations:**
- No simultaneous write to buffer being read
- Define blocking vs overwrite if reader slow

**Follow-ups:**
- Triple buffering next
- DMA ownership

---

### C083 — Triple buffering

**Interview prompt:**  
Extend to three buffers so producer rarely blocks if consumer is slow (display-style).

**Implement:**
```c
/* triple buffer acquire/release APIs */
```

**Constraints / expectations:**
- Clear state machine
- Drop policy when all busy

**Follow-ups:**
- Tearing prevention
- Latency vs double buffer

---

### C084 — Length-prefixed messages in byte ring

**Interview prompt:**  
Push/pop variable-length messages (u16 len + payload) into a byte ring atomically from the caller's view.

**Implement:**
```c
int msg_push(ring_t *r, const uint8_t *payload, uint16_t len);
int msg_pop(ring_t *r, uint8_t *payload, uint16_t cap, uint16_t *len_out);
```

**Constraints / expectations:**
- Don't leave partial messages if not enough space
- Max len check

**Follow-ups:**
- Zero-copy msg peek
- Corruption recovery

---

### C085 — Zero-copy slot ring

**Interview prompt:**  
Allocate a slot pointer, let producer fill, then publish; consumer acquires slot.

**Implement:**
```c
uint8_t *slot_alloc(slot_ring_t *s); /* NULL if full */
void slot_submit(slot_ring_t *s);
uint8_t *slot_acquire(slot_ring_t *s); /* NULL if empty */
void slot_release(slot_ring_t *s);
```

**Constraints / expectations:**
- Ownership transitions clear
- Fixed slot size

**Follow-ups:**
- Cancel alloc?
- Multi-size slots

---

### C086 — Watermark callbacks

**Interview prompt:**  
Fire callbacks when fill level crosses high/low watermarks.

**Implement:**
```c
typedef void (*wm_cb)(void *ctx, int high);
void ring_set_watermarks(ring_t *r, size_t low, size_t high, wm_cb cb, void *ctx);
```

**Constraints / expectations:**
- Edge-triggered not level-spam
- Document ISR context of cb

**Follow-ups:**
- Hysteresis
- Flow control link

---

### C087 — Lock-free SPSC with memory orders

**Interview prompt:**  
Implement lock-free SPSC ring using C11 atomics; annotate memory orders.

**Implement:**
```c
/* atomic head/tail indices */
```

**Constraints / expectations:**
- Correct acquire/release
- Explain why not seq_cst everywhere

**Follow-ups:**
- False sharing padding
- MPSC?

---

### C088 — RTOS blocking queue

**Interview prompt:**  
Against a fake RTOS API (semaphores), implement blocking put/get with timeout.

**Implement:**
```c
int queue_put(queue_t *q, const event_t *e, uint32_t timeout_ms);
int queue_get(queue_t *q, event_t *e, uint32_t timeout_ms);
```

**Constraints / expectations:**
- Assume given sem_take/sem_give
- Handle timeout

**Follow-ups:**
- ISR put variant
- Priority inheritance

---

### C089 — Batch pop

**Interview prompt:**  
Pop up to N elements efficiently.

**Implement:**
```c
size_t ring_pop_batch(ring_t *r, uint8_t *dst, size_t n);
```

**Constraints / expectations:**
- Minimize index updates
- Correct wrap

**Follow-ups:**
- Batch push
- SIMD copy

---

### C090 — History / mirror debug buffer

**Interview prompt:**  
Keep a mirror of the last N bytes processed for postmortem.

**Implement:**
```c
void hist_push(hist_t *h, uint8_t b);
size_t hist_snapshot(const hist_t *h, uint8_t *dst, size_t cap);
```

**Constraints / expectations:**
- Overwrite oldest
- ISR-safe if claimed

**Follow-ups:**
- Crash dump integration
- Binary vs text

---


---

[← Back to category index](./README.md)
