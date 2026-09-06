# IPC / Dual-Core / Shared Memory

**IDs:** C219–C230 (12 questions)  
**Focus:** Shared rings, mailbox/IPI, seqlock config, SQ/CQ, cache ops.

[← Back to category index](./README.md)

---

### C219 — Shared memory SPSC + barriers

**Interview prompt:**  
Two cores share a ring in memory; use memory barriers appropriately.

**Implement:**
```c
int shm_push(...); int shm_pop(...);
```

**Constraints / expectations:**
- Explain barrier placement
- Cache notes

**Follow-ups:**
- Same as lock-free SPSC
- Uncached SRAM

---

### C220 — Mailbox + IPI

**Interview prompt:**  
Write message to mailbox register/memory and raise interrupt to other core.

**Implement:**
```c
int mailbox_send(const msg_t *m);
void mailbox_isr(void);
```

**Constraints / expectations:**
- Full mailbox handling
- Clear IRQ correctly

**Follow-ups:**
- Multi-slot mailbox
- Priority messages

---

### C221 — Request/ACK protocol

**Interview prompt:**  
Sender waits for ACK from remote core with timeout.

**Implement:**
```c
int rpc_call(const req_t *r, resp_t *resp, uint32_t timeout_ms);
```

**Constraints / expectations:**
- Match sequence numbers
- Timeout path

**Follow-ups:**
- Async completion
- Retry

---

### C222 — Cross-core spinlock

**Interview prompt:**  
Test-and-set spinlock in shared memory for short critical sections.

**Implement:**
```c
void shm_spin_lock(shm_lock_t *l);
void shm_spin_unlock(shm_lock_t *l);
```

**Constraints / expectations:**
- Barriers
- No long holds

**Follow-ups:**
- Ticket lock
- Disable preemption

---

### C223 — Seqlock stats across cores

**Interview prompt:**  
RT core publishes stats; Linux core reads with seqlock.

**Implement:**
```c
/* write side RT, read side app */
```

**Constraints / expectations:**
- Retry loop
- No tear

**Follow-ups:**
- Cache line ownership
- Rate of updates

---

### C224 — RPMsg-lite style endpoints

**Interview prompt:**  
Stub an endpoint send/recv API over a shared virtqueue-like ring.

**Implement:**
```c
int rpmsg_send(uint32_t dst, const void *data, size_t len);
int rpmsg_recv(uint32_t *src, void *data, size_t cap, size_t *len);
```

**Constraints / expectations:**
- Name service optional skip
- Document blocking

**Follow-ups:**
- Virtio analogy
- Zero-copy

---

### C225 — Multi-core log ring

**Interview prompt:**  
Multiple cores print; either lock or drop-on-contention policy.

**Implement:**
```c
void log_putc(char c);
void log_write(const char *s);
```

**Constraints / expectations:**
- State policy clearly
- ISR safety

**Follow-ups:**
- Per-core buffers merge
- Timestamps

---

### C226 — Zero-copy buffer handoff across cores

**Interview prompt:**  
Ownership enum transferred via mailbox; no copying payload.

**Implement:**
```c
int give_buffer(buf_id_t id);
int take_buffer(buf_id_t *id);
```

**Constraints / expectations:**
- Only owner accesses data
- Invalid double-give detected

**Follow-ups:**
- Pool of buffers
- DMA + IPC

---

### C227 — Versioned shared config

**Interview prompt:**  
Writer updates config with sequence begin/end; reader retries if changed mid-read.

**Implement:**
```c
void config_write(const cfg_t *c);
void config_read(cfg_t *c);
```

**Constraints / expectations:**
- Seqlock pattern
- Default config

**Follow-ups:**
- Partial field updates
- Schema version

---

### C228 — Cross-core heartbeat

**Interview prompt:**  
Each core increments a counter; peer faults if stalled.

**Implement:**
```c
void heartbeat_kick(void);
int heartbeat_check_peer(uint32_t now_ms);
```

**Constraints / expectations:**
- Timeout threshold
- Sticky fault

**Follow-ups:**
- Recovery action
- Missed kick budget

---

### C229 — Command queue + completion queue

**Interview prompt:**  
Submit commands on SQ; receive results on CQ (NVMe-lite / GPU-lite style).

**Implement:**
```c
int sq_submit(const cmd_t *c);
int cq_pull(cpl_t *c);
```

**Constraints / expectations:**
- Match cmd ids
- Full/empty

**Follow-ups:**
- Out-of-order completions
- Doorbell registers

---

### C230 — Mark cache ops in IPC path

**Interview prompt:**  
In code comments/API calls, show where cache clean/invalidate must occur for shared buffers.

**Implement:**
```c
void ipc_send_buf(void *p, size_t n);
void ipc_recv_buf(void *p, size_t n);
```

**Constraints / expectations:**
- Correct direction clean vs invalidate
- Explain why

**Follow-ups:**
- Uncached alias
- IOMMU

---


---

[← Back to category index](./README.md)
