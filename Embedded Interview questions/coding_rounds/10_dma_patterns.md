# DMA Coding Patterns

**IDs:** C161–C172 (12 questions)  
**Focus:** Descriptors, ping-pong, circular RX, cache ops, SG, ownership FSM.

[← Back to category index](./README.md)

---

### C161 — DMA descriptor fill

**Interview prompt:**  
Fill a DMA descriptor for memory-to-peripheral TX including addr, len, control bits.

**Implement:**
```c
typedef struct { uint32_t src, dst, len, ctrl; } dma_desc_t;
void dma_fill_tx(dma_desc_t *d, const void *buf, size_t len, uintptr_t peri_dr);
```

**Constraints / expectations:**
- Alignment notes
- IE bit for IRQ

**Follow-ups:**
- Chaining
- Peripheral flow control

---

### C162 — DMA channel start/stop/abort

**Interview prompt:**  
API to configure channel, start, stop, abort in-flight transfer safely.

**Implement:**
```c
int dma_start(unsigned ch, const dma_desc_t *d);
int dma_stop(unsigned ch);
int dma_abort(unsigned ch);
```

**Constraints / expectations:**
- Idle wait/timeout
- Clear IRQ flags

**Follow-ups:**
- In-use channel error
- Pause/resume

---

### C163 — DMA completion ISR

**Interview prompt:**  
ISR clears IRQ and signals completion via semaphore or callback.

**Implement:**
```c
void dma_isr(void);
int dma_wait_done(unsigned ch, uint32_t timeout_ms);
```

**Constraints / expectations:**
- No heavy work in ISR
- Spurious IRQ safe

**Follow-ups:**
- Half-transfer IRQ
- Error IRQ

---

### C164 — Ping-pong DMA

**Interview prompt:**  
Two buffers alternate; while DMA fills A, CPU processes B.

**Implement:**
```c
void dma_pingpong_on_complete(void);
uint8_t *dma_pingpong_get_ready(void);
```

**Constraints / expectations:**
- Ownership FSM
- No race on swap

**Follow-ups:**
- Triple buffer
- Overrun if CPU late

---

### C165 — Circular DMA RX index

**Interview prompt:**  
Hardware circular DMA writes continuously; compute how many new bytes using remaining-count register.

**Implement:**
```c
size_t dma_circ_new_bytes(void);
void dma_circ_consume(size_t n);
```

**Constraints / expectations:**
- Handle wrap
- Volatile HW register

**Follow-ups:**
- High-water processing
- Idle detection

---

### C166 — Cache maintenance around DMA

**Interview prompt:**  
Before TX DMA from cached memory clean cache; after RX invalidate. Write helpers with comments.

**Implement:**
```c
void dma_tx_prepare(void *buf, size_t n);
void dma_rx_complete(void *buf, size_t n);
```

**Constraints / expectations:**
- Call correct cache ops stubs
- Alignment requirements stated

**Follow-ups:**
- DMA coherent alloc alternative
- False sharing

---

### C167 — Buffer ownership FSM CPU↔DMA

**Interview prompt:**  
Encode states OWN_CPU / OWN_DMA / IN_FLIGHT and illegal transitions assert.

**Implement:**
```c
typedef enum { OWN_CPU, OWN_DMA, IN_FLIGHT } own_t;
int buf_give_to_dma(buf_t *b);
int buf_take_from_dma(buf_t *b);
```

**Constraints / expectations:**
- Illegal transition detection
- Thread/ISR rules

**Follow-ups:**
- Diagram for interviewer
- Debug logging

---

### C168 — Scatter-gather list

**Interview prompt:**  
Walk an SG list and program descriptors or compute total length.

**Implement:**
```c
typedef struct { void *addr; size_t len; } sg_t;
size_t sg_total(const sg_t *sg, size_t nents);
int dma_program_sg(unsigned ch, const sg_t *sg, size_t nents);
```

**Constraints / expectations:**
- Max segments
- Zero-length entries

**Follow-ups:**
- Partial completion
- Linux sg API analogy

---

### C169 — DMA timeout watchdog

**Interview prompt:**  
If completion doesn't arrive in time, abort and return error.

**Implement:**
```c
int dma_start_timed(unsigned ch, const dma_desc_t *d, uint32_t timeout_ms);
```

**Constraints / expectations:**
- Abort path
- Distinguish timeout vs HW error

**Follow-ups:**
- Retry policy
- Telemetry

---

### C170 — HT/TC circular DMA callbacks

**Interview prompt:**  
Handle half-transfer and transfer-complete IRQs to process the correct half buffer.

**Implement:**
```c
void dma_ht_isr(void);
void dma_tc_isr(void);
```

**Constraints / expectations:**
- No double-process
- Indices correct

**Follow-ups:**
- Idle line UART DMA
- Overrun

---

### C171 — DMA alignment checker

**Interview prompt:**  
Validate buffer pointer/size against HW alignment and max transfer rules.

**Implement:**
```c
int dma_validate(const void *buf, size_t len, size_t align, size_t max);
```

**Constraints / expectations:**
- Return clear errors
- Page crossing optional rule

**Follow-ups:**
- Bounce buffers
- Coherent pool

---

### C172 — Zero-copy RX handoff

**Interview prompt:**  
DMA completes into a buffer; hand pointer to upper layer with refcount; allocate next RX buffer immediately.

**Implement:**
```c
void dma_rx_done_give_to_net(uint8_t *buf, size_t len);
uint8_t *dma_rx_replenish(void);
```

**Constraints / expectations:**
- Never free while DMA owns
- Replenish fail policy

**Follow-ups:**
- napi analogy
- Pool exhaustion

---


---

[← Back to category index](./README.md)
