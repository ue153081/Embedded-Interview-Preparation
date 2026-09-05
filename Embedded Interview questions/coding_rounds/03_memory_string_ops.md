# Memory & String Operations

**IDs:** C041–C055 (15 questions)  
**Focus:** memcpy/memmove/memset, bounded strings, hex, secure wipe.

[← Back to category index](./README.md)

---

### C041 — Optimized memcpy

**Interview prompt:**  
Implement memcpy. Start simple, then optimize with alignment and word copies.

**Implement:**
```c
void *my_memcpy(void *dst, const void *src, size_t n);
```

**Constraints / expectations:**
- Handle small n
- Assume no overlap unless you also discuss memmove

**Follow-ups:**
- How Apple interview optimizes this
- Unaligned src/dst strategy

---

### C042 — memmove

**Interview prompt:**  
Implement memmove that is correct for overlapping regions.

**Implement:**
```c
void *my_memmove(void *dst, const void *src, size_t n);
```

**Constraints / expectations:**
- Copy backward or forward correctly
- NULL+n=0 policy

**Follow-ups:**
- Can it call memcpy when no overlap?
- Test cases you would write

---

### C043 — memset that won't be optimized away

**Interview prompt:**  
Implement memset and a secure zero that compilers shouldn't dead-strip.

**Implement:**
```c
void *my_memset(void *s, int c, size_t n);
void secure_zero(void *s, size_t n);
```

**Constraints / expectations:**
- secure_zero needs compiler barrier / volatile tricks
- Document intent

**Follow-ups:**
- memset_s
- Why memset on password buffer fails

---

### C044 — memcmp

**Interview prompt:**  
Implement memcmp returning <0/0/>0 with defined unsigned char ordering.

**Implement:**
```c
int my_memcmp(const void *a, const void *b, size_t n);
```

**Constraints / expectations:**
- Unsigned char compare
- n=0 returns 0

**Follow-ups:**
- Constant-time variant later
- SIMD

---

### C045 — strlen / strnlen

**Interview prompt:**  
Implement strlen and strnlen for bare-metal C-strings.

**Implement:**
```c
size_t my_strlen(const char *s);
size_t my_strnlen(const char *s, size_t maxlen);
```

**Constraints / expectations:**
- strnlen does not read past maxlen
- NULL policy

**Follow-ups:**
- Wide strings?
- Safety in untrusted buffers

---

### C046 — strlcpy semantics

**Interview prompt:**  
Implement a bounded string copy that always NUL-terminates when dst_size>0 and returns would-be length.

**Implement:**
```c
size_t my_strlcpy(char *dst, const char *src, size_t dst_size);
```

**Constraints / expectations:**
- Terminate when possible
- Return strlen(src) semantics

**Follow-ups:**
- vs strncpy hazards
- Truncation detection

---

### C047 — atoi with overflow detection

**Interview prompt:**  
Parse a signed integer from a string with overflow/invalid detection (no libc reliance required).

**Implement:**
```c
int my_atoi(const char *s, int *out); /* 0 ok, <0 error */
```

**Constraints / expectations:**
- Handle sign/spaces policy (document)
- Detect INT overflow

**Follow-ups:**
- strtol base
- Reject trailing junk?

---

### C048 — itoa for logging

**Interview prompt:**  
Convert integers to decimal strings without printf for a tiny log path.

**Implement:**
```c
int utoa_dec(uint32_t v, char *buf, size_t cap);
int itoa_dec(int32_t v, char *buf, size_t cap);
```

**Constraints / expectations:**
- NUL-terminate
- Return length or error if cap too small

**Follow-ups:**
- hex itoa
- zero-pad widths

---

### C049 — bytes_to_hex

**Interview prompt:**  
Format a byte buffer as hex text (no spaces or with separators—document).

**Implement:**
```c
int bytes_to_hex(const uint8_t *in, size_t n, char *out, size_t out_cap);
```

**Constraints / expectations:**
- Need 2n+1 output capacity for continuous hex
- Upper/lower defined

**Follow-ups:**
- Include ASCII sidebar?
- Streaming version

---

### C050 — Constant-time memcmp

**Interview prompt:**  
Implement a memcmp that does not short-circuit, for MAC/tag compare.

**Implement:**
```c
int ct_memcmp(const void *a, const void *b, size_t n); /* 0 equal, 1 differ */
```

**Constraints / expectations:**
- No early return on mismatch
- Discuss limits of 'constant time' in C

**Follow-ups:**
- Why needed for crypto
- Compiler reordering risks

---

### C051 — Split memcpy across ring wrap

**Interview prompt:**  
Write a helper that copies `n` bytes from a circular buffer starting at `idx` into linear memory.

**Implement:**
```c
void ring_read_memcpy(uint8_t *dst, const uint8_t *ring, size_t cap, size_t idx, size_t n);
```

**Constraints / expectations:**
- Handles wrap in at most two memcpy calls
- idx < cap, n <= cap typically

**Follow-ups:**
- Reserve/commit write side
- DMA contiguous helper link

---

### C052 — In-place buffer reverse

**Interview prompt:**  
Reverse a byte buffer in place.

**Implement:**
```c
void reverse_bytes(uint8_t *b, size_t n);
```

**Constraints / expectations:**
- In-place
- n=0/1 OK

**Follow-ups:**
- Reverse uint32_t array
- Endian swap relationship

---

### C053 — Rotate byte array

**Interview prompt:**  
Rotate a buffer left/right by `k` positions in place (or with O(n) extra if you justify).

**Implement:**
```c
void rotate_left(uint8_t *b, size_t n, size_t k);
```

**Constraints / expectations:**
- k may be > n (mod)
- Prefer reverse-based algorithm

**Follow-ups:**
- In-place vs scratch
- Bit rotate vs byte rotate

---

### C054 — Secure wipe + barrier

**Interview prompt:**  
Zero memory and prevent the compiler from removing it; add a memory barrier helper.

**Implement:**
```c
void secure_wipe(void *p, size_t n);
void compiler_barrier(void);
```

**Constraints / expectations:**
- volatile or similar technique
- Document CPU barrier separately

**Follow-ups:**
- DMA coherency barriers vs compiler barriers
- OPAQUE

---

### C055 — snprintf-lite integers only

**Interview prompt:**  
Implement a tiny formatter supporting %u %d %x into a bounded buffer.

**Implement:**
```c
int mini_snprintf(char *out, size_t cap, const char *fmt, ...);
```

**Constraints / expectations:**
- No float required
- Always terminate if cap>0
- Return would-be length or error—document

**Follow-ups:**
- How far toward real printf?
- Reentrant?

---


---

[← Back to category index](./README.md)
