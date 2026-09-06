# Synchronization & Lock-Free Coding

**IDs:** C091–C110 (20 questions)  
**Focus:** Spinlocks, mutex/sem, seqlock, atomics, barriers, deadlock.

[← Back to category index](./README.md)

---

### C091 — Spinlock with atomic_flag

**Interview prompt:**  
Implement a spinlock using C11 atomic_flag for short critical sections on SMP or to race with DMA flags (as applicable).

**Implement:**
```c
typedef struct { atomic_flag f; } spinlock_t;
void spin_lock(spinlock_t *l);
void spin_unlock(spinlock_t *l);
```

**Constraints / expectations:**
- Correct test-and-set
- Document IRQ rules (often need irqsave variant)

**Follow-ups:**
- Why not spin in ISR holding long?
- Ticket lock fairness?

---

### C092 — Ticket lock

**Interview prompt:**  
Implement a fair ticket lock.

**Implement:**
```c
typedef struct { atomic_uint next, now; } ticket_lock_t;
void ticket_lock(ticket_lock_t *l);
void ticket_unlock(ticket_lock_t *l);
```

**Constraints / expectations:**
- FIFO fairness
- Atomics for tickets

**Follow-ups:**
- Cache line bouncing
- When vs MCS locks

---

### C093 — IRQ save/restore critical section

**Interview prompt:**  
Implement enter/exit critical section that disables interrupts and restores previous state (nested-safe).

**Implement:**
```c
typedef uint32_t irq_state_t;
irq_state_t irq_save(void);
void irq_restore(irq_state_t st);
#define CRITICAL_SECTION(code) ...
```

**Constraints / expectations:**
- Nesting safe
- No enabling IRQs if they were already off

**Follow-ups:**
- Basepri vs primask on Cortex-M
- SMP needs more than this

---

### C094 — Mutex for tasks

**Interview prompt:**  
Implement a mutex assuming a fake scheduler with block/wakeup APIs.

**Implement:**
```c
void mutex_lock(mutex_t *m);
void mutex_unlock(mutex_t *m);
```

**Constraints / expectations:**
- No spinning forever without block
- Owner tracking optional

**Follow-ups:**
- Recursive mutex?
- Priority inheritance next

---

### C095 — Binary semaphore ISR-capable

**Interview prompt:**  
Implement binary semaphore: ISR can give; task can take with optional timeout.

**Implement:**
```c
void sem_give_from_isr(sem_t *s);
int sem_take(sem_t *s, uint32_t timeout_ms);
```

**Constraints / expectations:**
- Correct wake
- Initial count 0/1

**Follow-ups:**
- Counting semaphore difference
- Spurious wake

---

### C096 — Counting semaphore

**Interview prompt:**  
Generalize to counting semaphore with max count.

**Implement:**
```c
int sem_init(sem_t *s, unsigned initial, unsigned max);
int sem_give(sem_t *s);
int sem_take(sem_t *s, uint32_t timeout_ms);
```

**Constraints / expectations:**
- Saturate or error at max—document
- ISR give variant

**Follow-ups:**
- Resource counting pattern
- Overflow

---

### C097 — Debug lock owner / recursion detect

**Interview prompt:**  
Add owner thread id and detect recursive take / unlock-by-non-owner in debug builds.

**Implement:**
```c
void mutex_lock_debug(mutex_t *m);
void mutex_unlock_debug(mutex_t *m);
```

**Constraints / expectations:**
- Assert on misuse
- Compile out in release

**Follow-ups:**
- Deadlock detector ideas
- Lockdep analogy

---

### C098 — Reader-writer lock

**Interview prompt:**  
Implement an RW lock (choose and state reader- or writer-preference).

**Implement:**
```c
void rw_rlock(rw_lock_t *l); void rw_runlock(rw_lock_t *l);
void rw_wlock(rw_lock_t *l); void rw_wunlock(rw_lock_t *l);
```

**Constraints / expectations:**
- State preference
- Correct when readers=0

**Follow-ups:**
- Starvation scenarios
- seqlock alternative

---

### C099 — Seqlock for stats

**Interview prompt:**  
Publish a multi-word stats structure using seqlock so readers never block writers long.

**Implement:**
```c
typedef struct { unsigned seq; uint64_t isr_count; uint64_t bytes; } stats_t;
void stats_write_begin(stats_t *s); void stats_write_end(stats_t *s);
void stats_read(stats_t *s, uint64_t *isr, uint64_t *bytes);
```

**Constraints / expectations:**
- Retry on inconsistency
- Odd seq means write in progress

**Follow-ups:**
- When seqlock is wrong
- Atomic 64-bit alternatives

---

### C100 — Atomic refcount

**Interview prompt:**  
Implement atomic reference counter with callback/free at zero.

**Implement:**
```c
void ref_init(ref_t *r, void (*release)(ref_t *));
void ref_get(ref_t *r);
void ref_put(ref_t *r);
```

**Constraints / expectations:**
- Use atomic_int
- No ABA on free of object containing ref

**Follow-ups:**
- Saturation?
- Weak memory barriers

---

### C101 — Lock-free SPSC queue (struct elements)

**Interview prompt:**  
Implement lock-free SPSC queue of fixed struct messages.

**Implement:**
```c
int spsc_push(spsc_t *q, const msg_t *m);
int spsc_pop(spsc_t *q, msg_t *m);
```

**Constraints / expectations:**
- Atomic indices
- memory_order rationale

**Follow-ups:**
- Batching
- Cache line pad

---

### C102 — MPSC with CAS list or documented approach

**Interview prompt:**  
Sketch/implement multi-producer single-consumer enqueue using CAS on a linked list (Treiber-like enqueue).

**Implement:**
```c
int mpsc_enqueue(mpsc_t *q, node_t *n);
node_t *mpsc_dequeue(mpsc_t *q); /* single consumer */
```

**Constraints / expectations:**
- Explain ABA risk
- Consumer algorithm correctness

**Follow-ups:**
- Vyukov MPSC
- When to just use a lock

---

### C103 — Treiber lock-free stack

**Interview prompt:**  
Implement push/pop stack with atomic compare-exchange; discuss ABA.

**Implement:**
```c
void stack_push(stack_t *s, node_t *n);
node_t *stack_pop(stack_t *s);
```

**Constraints / expectations:**
- CAS loop
- ABA explanation required

**Follow-ups:**
- Tagged pointers
- Hazard pointers mention

---

### C104 — ABA-safe stack with generation tag

**Interview prompt:**  
Mitigate ABA using a tagged pointer or separate generation counter packed with pointer (or simulated).

**Implement:**
```c
/* push/pop with tag */
```

**Constraints / expectations:**
- Show how ABA is prevented
- Platform pointer width assumptions

**Follow-ups:**
- Double-width CAS
- Other mitigations

---

### C105 — Acquire/release ISR→task flag

**Interview prompt:**  
ISR publishes data then sets a flag; task waits/ polls with correct memory ordering.

**Implement:**
```c
void isr_publish(const data_t *d);
int task_try_consume(data_t *out);
```

**Constraints / expectations:**
- Data visible before flag
- No torn reads

**Follow-ups:**
- Eventfd/sem instead of poll
- Double buffering

---

### C106 — Sense-reversing barrier

**Interview prompt:**  
Implement an N-thread barrier (C++ atomics OK).

**Implement:**
```c
class Barrier { public: explicit Barrier(int n); void arrive_and_wait(); };
```

**Constraints / expectations:**
- Reusable
- Correct sense flip

**Follow-ups:**
- vs pthread_barrier
- Last thread unlocks

---

### C107 — Producer-consumer with condition_variable

**Interview prompt:**  
Bounded buffer using mutex + condition variables (C++).

**Implement:**
```c
template<typename T, size_t N> class BoundedQueue {
 public:
  void push(T v); T pop();
};
```

**Constraints / expectations:**
- Wait predicates in loop
- Handle spurious wakeups

**Follow-ups:**
- timeout pop
- stop token

---

### C108 — Deadlock then fix

**Interview prompt:**  
Write a small two-lock example that deadlocks under some scheduling, then fix via lock ordering.

**Implement:**
```c
void transfer_bad(Account *a, Account *b, int amt);
void transfer_good(Account *a, Account *b, int amt);
```

**Constraints / expectations:**
- Demonstrate ordering by address
- Explain deadlock conditions

**Follow-ups:**
- try_lock backoff
- Lock hierarchies

---

### C109 — Priority inheritance mutex (sketch)

**Interview prompt:**  
Implement a simplified PI mutex: when a high task blocks, boost owner priority via provided scheduler hooks.

**Implement:**
```c
void pi_mutex_lock(pi_mutex_t *m);
void pi_mutex_unlock(pi_mutex_t *m);
```

**Constraints / expectations:**
- Use given set_priority/get_priority hooks
- Restore on unlock

**Follow-ups:**
- Priority ceiling alternative
- Nested locks

---

### C110 — Wait-free single-word mailbox

**Interview prompt:**  
Single-slot mailbox where producer overwrites; consumer reads latest with a sequence or valid flag protocol.

**Implement:**
```c
void mailbox_write(mailbox_t *m, uint32_t value);
int mailbox_read(mailbox_t *m, uint32_t *value); /* 1 if new */
```

**Constraints / expectations:**
- Detect new data
- Discuss torn read if >word — keep to one word

**Follow-ups:**
- Multi-word seqlock link
- Lossy vs lossless

---


---

[← Back to category index](./README.md)
