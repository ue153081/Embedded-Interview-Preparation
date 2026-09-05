# Logging, Crash & Diagnostics

**IDs:** C231–C240 (10 questions)  
**Focus:** ISR-safe log, retained breadcrumbs, stack paint, health export.

[← Back to category index](./README.md)

---

### C231 — ISR-safe slog

**Interview prompt:**  
In ISR, only push a log record {id, a,b,c} into a ring—no printf.

**Implement:**
```c
typedef struct { uint16_t id; uint32_t a,b,c; } logrec_t;
int log_isr(uint16_t id, uint32_t a, uint32_t b, uint32_t c);
```

**Constraints / expectations:**
- Drop on full with counter
- No blocking

**Follow-ups:**
- Format strings in task
- Rate limit

---

### C232 — Task-side log drain

**Interview prompt:**  
Drain log ring and format human-readable lines to UART.

**Implement:**
```c
void log_task(void);
```

**Constraints / expectations:**
- Map id→fmt string table
- Don't block ISR long

**Follow-ups:**
- Binary log backend
- Timestamps

---

### C233 — Log levels compile-time strip

**Interview prompt:**  
Implement LOG_DEBUG/INFO/ERROR macros that compile out below a level.

**Implement:**
```c
#define LOG_LEVEL ...
#define LOG_DEBUG(...) ...
#define LOG_ERROR(...) ...
```

**Constraints / expectations:**
- Zero cost when disabled
- Variadic macros

**Follow-ups:**
- Runtime level filter
- Per-module levels

---

### C234 — Drop counters

**Interview prompt:**  
Track how many logs were dropped due to full buffer; expose getter.

**Implement:**
```c
uint32_t log_dropped(void);
```

**Constraints / expectations:**
- Atomic/IRQ safe
- Saturate or wrap—doc

**Follow-ups:**
- Alert on drops
- Water mark

---

### C235 — Retained-RAM crash breadcrumb

**Interview prompt:**  
On assert/fault, write magic+reason+PC into a .noinit structure surviving reboot.

**Implement:**
```c
typedef struct { uint32_t magic, reason, pc, lr; } crash_t;
void crash_write(uint32_t reason, uint32_t pc, uint32_t lr);
int crash_read(crash_t *out); /* after reboot */
```

**Constraints / expectations:**
- Magic validation
- Clear after read

**Follow-ups:**
- Stack dump
- coredump flash

---

### C236 — Stack paint / high-water

**Interview prompt:**  
Paint stack with a pattern at init; compute unused high-water mark.

**Implement:**
```c
void stack_paint(uint32_t *base, size_t words);
size_t stack_high_water(const uint32_t *base, size_t words);
```

**Constraints / expectations:**
- Pattern constant
- Called from safe context

**Follow-ups:**
- Per-task stacks
- Overflow canary

---

### C237 — Fault register dump

**Interview prompt:**  
Format CPU registers into a buffer on HardFault (fake reg struct).

**Implement:**
```c
size_t dump_regs(const regframe_t *r, char *out, size_t cap);
```

**Constraints / expectations:**
- Bounded
- Readable hex

**Follow-ups:**
- Fault status registers
- Nested fault

---

### C238 — Backtrace capture stub

**Interview prompt:**  
Walk a simple frame pointer chain (or simulated) to collect return addresses.

**Implement:**
```c
size_t backtrace(uint32_t *pcs, size_t max);
```

**Constraints / expectations:**
- Stop conditions
- No crash on corrupt FP

**Follow-ups:**
- Thumb bit
- DWARF unwind mention

---

### C239 — Health counters export

**Interview prompt:**  
Export key counters as `key=value\n` text for a diagnostics channel.

**Implement:**
```c
size_t health_export(char *out, size_t cap);
```

**Constraints / expectations:**
- Include drops, IRQs, uptime
- Truncation safe

**Follow-ups:**
- JSON
- Binary TLV

---

### C240 — Rate-limited assert log

**Interview prompt:**  
Don't spam: log an assert at most once per window.

**Implement:**
```c
void assert_ratelimited(const char *msg);
```

**Constraints / expectations:**
- Time window
- Still halt or not—doc

**Follow-ups:**
- Per-site tokens
- Token bucket

---


---

[← Back to category index](./README.md)
