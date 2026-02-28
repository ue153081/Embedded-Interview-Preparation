# Day-Before Interview Revision (Google Embedded L4)

## Goal for this day
- Revise only high-yield patterns.
- Re-solve from scratch without looking at notes.
- Practice verbal explanation: complexity, invariants, ISR-safety, failure handling.

## Section A — Must-Do Coding Set (Top Priority)

1. UART interrupt RX driver + ISR-safe ring buffer
2. Lock-free SPSC ring queue
3. DMA double-buffered ADC or UART RX pipeline
4. Fixed-size memory pool allocator
5. Free-list allocator with split + coalesce
6. Register access API (`read/write/rmw`, bitfield macros, `volatile`)
7. Timer queue (sorted list) with cancel + periodic reschedule
8. I2C state machine (start/address/data/stop, ACK/NACK)
9. LRU cache (doubly list + hash)
10. Safe `memmove` + packet parser FSM

## Section B — High-Probability Follow-ups

1. How do you detect full vs empty in ring buffer?
2. What work is safe inside ISR vs deferred to worker/task?
3. How do you prevent DMA overrun and recover?
4. How do you protect shared registers between ISR and task?
5. Why is `volatile` needed? When is it insufficient without barriers/locks?
6. How do you handle timeout/retry/reset in driver APIs?
7. How do you prevent false sharing in hot producer/consumer structs?
8. What is ABA and why does it matter for lock-free structures?

## Section C — 4-Hour Revision Schedule

1. Hour 1: UART IRQ + ring buffer + register API
2. Hour 2: Memory pool + free-list allocator
3. Hour 3: DMA double buffer + timer queue
4. Hour 4: I2C state machine + packet parser + rapid Q&A drill

## Section D — 75-Min Mock (Night Before)

1. 35 min: code one driver problem (UART IRQ or DMA)
2. 20 min: code one DS/concurrency problem (SPSC queue or LRU)
3. 20 min: explain failure paths and test strategy out loud

## Section E — Interview-Ready Templates

### Driver API template
```c
int drv_init(const cfg_t *cfg);
int drv_start(void);
int drv_stop(void);
int drv_read(uint8_t *buf, size_t len, uint32_t timeout_ms);
int drv_write(const uint8_t *buf, size_t len, uint32_t timeout_ms);
void drv_isr_handler(void);
```

### Ring buffer template
```c
int rb_push(rb_t *r, uint8_t v); // ISR-safe, non-blocking
int rb_pop(rb_t *r, uint8_t *v); // task context
size_t rb_size(const rb_t *r);
```

### Error handling checklist
- Timeout path present
- Retry policy bounded
- Reset/re-init path available
- Error counters/telemetry updated
- No blocking call inside ISR

## Section F — Final 20-Min Checklist Before Sleep

1. Re-state complexity for top 10 problems.
2. Re-state one key invariant for each top problem.
3. Confirm you can code ring buffer + UART ISR from blank file.
4. Confirm you can explain DMA ownership and cache coherency.
5. Sleep on time; no new topics.
