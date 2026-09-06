# C Language, UB, Types & Macros

**IDs:** C001–C020 (20 questions)  
**Focus:** Core C for firmware: macros, UB, const, endian helpers, asserts.

[← Back to category index](./README.md)

---

### C001 — container_of / offsetof

**Interview prompt:**  
In Linux-style firmware, list nodes are embedded inside larger objects. Implement `offsetof` and `container_of`, then use them to recover `struct device*` from a `list_node*`.

**Implement:**
```c
#define offsetof(type, member) ...
#define container_of(ptr, type, member) ...
struct list_node { struct list_node *next; };
struct device { int id; struct list_node link; };
struct device *device_from_node(struct list_node *n);
```

**Constraints / expectations:**
- Correct for arbitrary member offset
- No UB when ptr is valid
- Works as macros in headers

**Follow-ups:**
- Why not just cast node to device?
- NULL handling?
- typeof-safe variant?

---

### C002 — Compile-time struct layout asserts

**Interview prompt:**  
You own a on-wire header. Add compile-time checks so size/offsets cannot regress unnoticed.

**Implement:**
```c
struct pkt_hdr { uint8_t type, flags; uint16_t len; uint32_t seq; };
/* static asserts for sizeof and key offsets */
```

**Constraints / expectations:**
- Use _Static_assert or portable macro
- Call out padding risks

**Follow-ups:**
- Packed attribute vs manual serialize?
- How to assert alignment?

---

### C003 — ARRAY_SIZE / MIN / MAX / BIT / GENMASK

**Interview prompt:**  
Write the standard embedded macros without classic footguns where possible.

**Implement:**
```c
#define ARRAY_SIZE(a) ...
#define MIN(a,b) ...
#define MAX(a,b) ...
#define BIT(n) ...
#define GENMASK(h,l) ...
```

**Constraints / expectations:**
- Discuss double-evaluation
- BIT/GENMASK width defined

**Follow-ups:**
- Unsafe MIN(i++, j) example
- typeof-based MIN

---

### C004 — likely / unlikely

**Interview prompt:**  
Implement branch hints and use them in a parser hot path.

**Implement:**
```c
#define likely(x) ...
#define unlikely(x) ...
int parse_frame(const uint8_t *buf, size_t n);
```

**Constraints / expectations:**
- __builtin_expect with fallback
- unlikely on errors

**Follow-ups:**
- Does it affect correctness?
- Mis-hinting cost?

---

### C005 — Fix undefined behavior snippets

**Interview prompt:**  
Identify UB in given snippets and rewrite them safely for firmware.

**Implement:**
```c
int shl(int x,int n);
int add(int a,int b);
uint32_t load_u32_alias(char *p);
int *ret_local(void);
```

**Constraints / expectations:**
- Explain each UB
- Prefer unsigned for shifts

**Follow-ups:**
- Sanitizers to catch these?
- -fwrapv?

---

### C006 — volatile flag vs atomics

**Interview prompt:**  
An ISR sets a flag consumed by the main loop. Implement with volatile, then a correct atomic/barrier version.

**Implement:**
```c
void isr(void);
void main_loop(void);
```

**Constraints / expectations:**
- Show volatile limits
- Correct handoff on weakly ordered CPUs

**Follow-ups:**
- When is volatile enough on M-profile?
- acquire/release?

---

### C007 — align_up / align_down

**Interview prompt:**  
Implement DMA-style alignment helpers with overflow detection.

**Implement:**
```c
size_t align_up(size_t x, size_t align);
size_t align_down(size_t x, size_t align);
int align_up_checked(size_t x, size_t align, size_t *out);
```

**Constraints / expectations:**
- align power-of-two
- overflow-safe

**Follow-ups:**
- Pointer alignment?
- Non-PoT align?

---

### C008 — Portable pack/unpack vs packed struct

**Interview prompt:**  
Don't cast wire buffers to structs. Implement explicit LE pack/unpack for a sensor report.

**Implement:**
```c
struct sensor_report { uint8_t id; uint16_t value; uint32_t ts; };
void pack_report(uint8_t out[7], const struct sensor_report *r);
int unpack_report(struct sensor_report *r, const uint8_t in[7]);
```

**Constraints / expectations:**
- Endian-safe
- Unaligned-safe

**Follow-ups:**
- When is packed OK?
- Add versioning

---

### C009 — Flexible array packet alloc

**Interview prompt:**  
Allocate header+payload in one block using a flexible array member.

**Implement:**
```c
struct packet { uint16_t len, type; uint8_t data[]; };
struct packet *packet_alloc(uint16_t type, const uint8_t *payload, uint16_t len);
void packet_free(struct packet *p);
```

**Constraints / expectations:**
- Overflow-safe size math
- Allocator injectable

**Follow-ups:**
- Pool version?
- Alignment of data[]?

---

### C010 — const-correct APIs

**Interview prompt:**  
Write buffer APIs with correct const usage; fix a buggy const-casting interface.

**Implement:**
```c
size_t checksum(const uint8_t *buf, size_t n);
int copy_cmd(uint8_t *dst, size_t dst_cap, const uint8_t *src, size_t n);
```

**Constraints / expectations:**
- Explain pointer const positions
- No cast away const

**Follow-ups:**
- restrict keyword?
- C++ overloads?

---

### C011 — Opcode handler table

**Interview prompt:**  
Implement a host-command dispatcher using function pointers.

**Implement:**
```c
typedef int (*cmd_fn)(const uint8_t *payload, size_t len, void *ctx);
int dispatch(uint8_t opcode, const uint8_t *payload, size_t len, void *ctx);
```

**Constraints / expectations:**
- Unknown opcode error
- NULL safety

**Follow-ups:**
- O(1) indexed table?
- ISR context?

---

### C012 — memcpy vs memmove with restrict

**Interview prompt:**  
Implement memcpy (no overlap) and memmove (overlap-safe). Document restrict.

**Implement:**
```c
void *my_memcpy(void *restrict dst, const void *restrict src, size_t n);
void *my_memmove(void *dst, const void *src, size_t n);
```

**Constraints / expectations:**
- Correct overlap direction
- Explain restrict UB

**Follow-ups:**
- Optimize with word copies?
- How to detect overlap?

---

### C013 — Endian helpers unaligned-safe

**Interview prompt:**  
Implement read/write LE/BE 16/32 helpers that work on unaligned addresses.

**Implement:**
```c
uint16_t read_le16(const uint8_t *p);
uint32_t read_le32(const uint8_t *p);
void write_be16(uint8_t *p, uint16_t v);
void write_be32(uint8_t *p, uint32_t v);
```

**Constraints / expectations:**
- Byte-wise assembly of values
- No host cast

**Follow-ups:**
- BE loads / LE stores too
- Cortex-M unaligned traps?

---

### C014 — uint8_t bit clear promotion bug

**Interview prompt:**  
Fix integer-promotion bugs when clearing bits on uint8_t.

**Implement:**
```c
uint8_t clear_bit(uint8_t x, unsigned bit);
uint8_t set_bit(uint8_t x, unsigned bit);
```

**Constraints / expectations:**
- Show why `x & ~(1<<bit)` fails
- Define out-of-range policy

**Follow-ups:**
- uint16_t similar issues?
- MISRA notes?

---

### C015 — Enum mode handler

**Interview prompt:**  
Implement mode name/enter with safe handling of invalid values.

**Implement:**
```c
typedef enum { MODE_OFF, MODE_RUN, MODE_FAULT, MODE_COUNT } mode_t;
const char *mode_name(mode_t m);
int mode_enter(mode_t m);
```

**Constraints / expectations:**
- Default/invalid path
- Optional MODE_COUNT asserts

**Follow-ups:**
- Wire-size packed enums?
- Table-driven approach?

---

### C016 — Status register pack/unpack

**Interview prompt:**  
Encode/decode a status byte with ready/err/code fields using shift/mask (not bitfields for the primary solution).

**Implement:**
```c
uint8_t status_pack(int ready, int err, unsigned code);
void status_unpack(uint8_t v, int *ready, int *err, unsigned *code);
```

**Constraints / expectations:**
- Validate field ranges
- Discuss bitfield pitfalls

**Follow-ups:**
- Atomic RMW updates?
- Linux FIELD_GET style macros?

---

### C017 — Driver status return codes

**Interview prompt:**  
Design drv_status_t and implement uart_read with timeout vs IO errors.

**Implement:**
```c
typedef enum { DRV_OK=0, DRV_ERR_PARAM=-1, DRV_ERR_TIMEOUT=-2, DRV_ERR_IO=-3, DRV_ERR_BUSY=-4 } drv_status_t;
drv_status_t uart_read(uint8_t *buf, size_t n, size_t *got, uint32_t timeout_ms);
```

**Constraints / expectations:**
- Validate pointers
- Document ISR vs thread context

**Follow-ups:**
- Return byte count instead?
- Map to Linux errno?

---

### C018 — FW_ASSERT / BUG_ON / WARN_ON

**Interview prompt:**  
Implement firmware assert macros with a defined failure policy.

**Implement:**
```c
void fw_assert_fail(const char *file, int line, const char *expr);
#define FW_ASSERT(x) ...
#define FW_BUG_ON(x) ...
#define FW_WARN_ON(x) ...
```

**Constraints / expectations:**
- Lightweight enough for FW
- Production vs debug behavior

**Follow-ups:**
- ISR-safe asserts?
- Retained-RAM breadcrumbs?

---

### C019 — static inline max vs macro

**Interview prompt:**  
Replace a MAX macro with static inline helpers and explain tradeoffs.

**Implement:**
```c
static inline int max_int(int a, int b);
static inline unsigned max_uint(unsigned a, unsigned b);
```

**Constraints / expectations:**
- Type safety
- Header definition rules

**Follow-ups:**
- always_inline?
- C++ overload set?

---

### C020 — Type-generic max

**Interview prompt:**  
Implement type-generic max using C11 _Generic (or explain C++ overloads).

**Implement:**
```c
#define max(a,b) /* _Generic ... */
```

**Constraints / expectations:**
- Works for int and long
- Document approach

**Follow-ups:**
- Linux min/max macros?
- float NaN?

---


---

[← Back to category index](./README.md)
