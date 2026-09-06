# Interrupts & Deferred Work

**IDs:** C111–C120 (10 questions)  
**Focus:** ISR patterns, top/bottom half, debounce, work items, lost wakeup.

[← Back to category index](./README.md)

---

### C111 — Minimal ISR + queue

**Interview prompt:**  
Write an IRQ handler that acknowledges hardware and enqueues an event for the task context.

**Implement:**
```c
void device_isr(void);
void device_task(void); /* drains queue */
```

**Constraints / expectations:**
- ISR short
- No heavy work in ISR

**Follow-ups:**
- What if queue full?
- Nested interrupts

---

### C112 — Top-half / bottom-half

**Interview prompt:**  
Split interrupt handling: quick top half, deferred bottom half processing function.

**Implement:**
```c
void top_half_isr(void);
void bottom_half(void);
```

**Constraints / expectations:**
- Scheduling of BH (flag/workqueue)
- Shared data protection

**Follow-ups:**
- Linux softirq/tasklet analogy
- Latency budget

---

### C113 — Threaded IRQ pattern

**Interview prompt:**  
Hard IRQ wakes a high-priority thread that does the bulk work.

**Implement:**
```c
void hard_irq(void);
void irq_thread(void);
```

**Constraints / expectations:**
- Wake mechanism
- Priorities

**Follow-ups:**
- vs softirq
- Priority inversion with locks

---

### C114 — IRQ-safe reference count

**Interview prompt:**  
Reference count that can be taken/released from ISR and thread.

**Implement:**
```c
void kref_get_isrsafe(kref_t *r);
void kref_put_isrsafe(kref_t *r);
```

**Constraints / expectations:**
- Atomic ops or critical sections
- Free only from safe context if required—document

**Follow-ups:**
- Deferred free
- RCU mention

---

### C115 — GPIO debounce in ISR/timer

**Interview prompt:**  
Debounce a mechanical button: ISR starts a timer; stable reading accepted after quiet period.

**Implement:**
```c
void button_isr(void);
void debounce_timer_cb(void);
int button_read_stable(void);
```

**Constraints / expectations:**
- Ignore bounce windows
- Configurable ms

**Follow-ups:**
- Both edges
- Long press later

---

### C116 — IRQ coalescing counter

**Interview prompt:**  
Count interrupts in ISR; process accumulated count in a deferred context.

**Implement:**
```c
void line_isr(void);
void process_deferred(void);
```

**Constraints / expectations:**
- Atomic/volatile count
- No lost increments

**Follow-ups:**
- NAPI analogy
- Rate limiting

---

### C117 — IRQ storm rate limit

**Interview prompt:**  
If interrupts exceed a rate, disable IRQ briefly and signal error.

**Implement:**
```c
void noisy_isr(void);
```

**Constraints / expectations:**
- Sliding window or token bucket simple
- Re-enable policy

**Follow-ups:**
- Root cause debugging
- Hardware FIFO overrun link

---

### C118 — One-shot work item

**Interview prompt:**  
Implement a single pending work flag/function pointer deferred to main loop.

**Implement:**
```c
typedef void (*work_fn)(void *ctx);
int schedule_work(work_fn fn, void *ctx);
void work_run(void);
```

**Constraints / expectations:**
- Only one pending or queue—document
- ISR schedule safe

**Follow-ups:**
- Cancel work
- Periodic work

---

### C119 — ISR latency histogram

**Interview prompt:**  
Measure time in ISR (fake cycle counter) and bump histogram buckets.

**Implement:**
```c
void isr_with_latency_account(void);
void latency_hist_dump(void);
```

**Constraints / expectations:**
- Bucket edges defined
- Lightweight

**Follow-ups:**
- Max latency watermark
- Tracing

---

### C120 — Correct wakeup: flag vs queue race

**Interview prompt:**  
Fix a race where the task checks a flag before the ISR sets it and sleeps forever. Write the correct pattern.

**Implement:**
```c
void isr(void);
void waiter_task(void);
```

**Constraints / expectations:**
- Check-after-arm or event count
- No lost wakeup

**Follow-ups:**
- POSIX condvar analogy
- Semaphore solution

---


---

[← Back to category index](./README.md)
