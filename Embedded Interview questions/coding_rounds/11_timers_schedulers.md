# Timers & Schedulers

**IDs:** C173–C185 (13 questions)  
**Focus:** Software timers on one HW timer, wheels, heaps, coop schedulers.

[← Back to category index](./README.md)

---

### C173 — Software timers on one HW timer

**Interview prompt:**  
Classic Google-style: many software timers using one hardware timer. Absolute expiry list; reprogram HW to next deadline.

**Implement:**
```c
typedef void (*timer_cb)(void *ctx);
typedef struct sw_timer sw_timer_t;
void sw_timer_set(sw_timer_t *t, uint32_t delay_ms, timer_cb cb, void *ctx);
void sw_timer_cancel(sw_timer_t *t);
void hw_timer_irq(void); /* fires at programmed time */
```

**Constraints / expectations:**
- Store absolute deadlines
- Update HW when head changes
- Callbacks from IRQ or deferred—document

**Follow-ups:**
- Periodic timers
- MP safety
- min-heap vs sorted list

---

### C174 — Cancel + periodic race-safe

**Interview prompt:**  
Extend software timers with periodic reschedule and race-safe cancel if callback already running.

**Implement:**
```c
void sw_timer_set_periodic(sw_timer_t *t, uint32_t period_ms, timer_cb cb, void *ctx);
int sw_timer_cancel_sync(sw_timer_t *t);
```

**Constraints / expectations:**
- Define cancel during callback
- No use-after-free of timer object

**Follow-ups:**
- Drift-free period
- Timer wheel

---

### C175 — Wrap-safe time comparisons

**Interview prompt:**  
Implement time_before/time_after helpers for wrapping tick counters.

**Implement:**
```c
int time_after(uint32_t a, uint32_t b);
int time_before_eq(uint32_t a, uint32_t b);
uint32_t time_delta(uint32_t now, uint32_t then);
```

**Constraints / expectations:**
- Correct with modular arithmetic
- Document max delta

**Follow-ups:**
- 64-bit ticks
- Linux jiffies macros

---

### C176 — Timer wheel

**Interview prompt:**  
Implement a hierarchical or single-level timer wheel for many timers.

**Implement:**
```c
void wheel_insert(sw_timer_t *t, uint32_t expires);
void wheel_tick(void); /* advance one bucket */
```

**Constraints / expectations:**
- O(1) insert typical
- Explain cascade if hierarchical

**Follow-ups:**
- vs min-heap
- Hash collisions

---

### C177 — Min-heap timer queue

**Interview prompt:**  
Use a binary heap keyed by expiry time.

**Implement:**
```c
void heap_timer_insert(sw_timer_t *t);
sw_timer_t *heap_timer_pop_expired(uint32_t now);
```

**Constraints / expectations:**
- Decrease-key on reschedule or remove+insert
- Array heap

**Follow-ups:**
- Complexity
- Cache behavior vs list

---

### C178 — Drift-free periodic

**Interview prompt:**  
Schedule periodic work using absolute next+=period instead of now+period each time.

**Implement:**
```c
void periodic_arm(periodic_t *p, uint32_t period_ms);
void periodic_on_fire(periodic_t *p);
```

**Constraints / expectations:**
- Catch-up policy if late
- Wrap safety

**Follow-ups:**
- Skipped beats count
- Phase alignment

---

### C179 — Cooperative round-robin scheduler

**Interview prompt:**  
Implement a tiny coop scheduler with task list and yield.

**Implement:**
```c
typedef void (*task_fn)(void);
void task_add(task_fn fn);
void scheduler_run(void);
void yield(void);
```

**Constraints / expectations:**
- No preemption
- Fair RR

**Follow-ups:**
- Add priorities
- Stacks per task

---

### C180 — Bitmap priority ready queue

**Interview prompt:**  
Ready tasks by priority bitmap; always run highest.

**Implement:**
```c
void ready(unsigned prio, task_fn fn);
void schedule(void);
```

**Constraints / expectations:**
- ffs to find highest
- FIFO within prio optional

**Follow-ups:**
- Starvation
- Aging

---

### C181 — regCall / callNext tick dispatcher

**Interview prompt:**  
Google-style: register callbacks for future ticks; each tick call due functions.

**Implement:**
```c
void regCall(void (*fn)(void), uint32_t delay_ticks);
void callNext(void); /* invoked every tick */
```

**Constraints / expectations:**
- Efficient enough for interview
- Periodic support follow-up

**Follow-ups:**
- Complexity
- Priority callbacks

---

### C182 — Deadline miss counter

**Interview prompt:**  
Track when a periodic task runs after its deadline.

**Implement:**
```c
void task_on_schedule(uint32_t now);
uint32_t task_deadline_misses(void);
```

**Constraints / expectations:**
- Define deadline
- Increment correctly

**Follow-ups:**
- What to do on miss
- Telemetry

---

### C183 — Hashed timer wheel

**Interview prompt:**  
Hash timers into buckets by expiry; process current bucket each tick.

**Implement:**
```c
/* insert + tick */
```

**Constraints / expectations:**
- Collision chains
- Cascade or large range strategy

**Follow-ups:**
- Linux timer wheel history
- Accuracy

---

### C184 — Debounce via software timer

**Interview prompt:**  
On edge, (re)arm a one-shot timer; only commit level when timer fires quietly.

**Implement:**
```c
void edge_isr(void);
void debounce_tmr_cb(void);
```

**Constraints / expectations:**
- Retrigger extends quiet period
- Final stable level

**Follow-ups:**
- Both press/release
- Power cost

---

### C185 — One-shot vs auto-reload HAL

**Interview prompt:**  
Abstract HW timer into one-shot and periodic modes.

**Implement:**
```c
int timer_start_oneshot(uint32_t ms, void (*cb)(void));
int timer_start_periodic(uint32_t ms, void (*cb)(void));
void timer_stop(void);
```

**Constraints / expectations:**
- Single HW channel assumed
- Callback context documented

**Follow-ups:**
- Multiple channels
- PWM conflict

---


---

[← Back to category index](./README.md)
