# Embedded / Firmware Coding Rounds — All 300 Interview Questions (Elaborated)

**Purpose:** Full interview-style wording for every item in the coding bank.  
**Scope:** Embedded / firmware / driver **coding rounds only**  
**Excluded:** Pure DSA (trees/graphs/DP), system-design whiteboards  

**How to use**
1. Start with **Tier S** IDs listed at the bottom (timed 45–60 min each).
2. For each question: clarify constraints → write code → run mental tests → answer follow-ups.
3. Default language is **C11**; questions marked with `cpp` fences expect **C++**.

**Related files**
- Index/short titles: `EMBEDDED_FIRMWARE_CODING_ROUNDS_COMPLETE.md`
- DSA / system design: prepare separately

---

## Questions C001–C300

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

### C021 — Popcount

**Interview prompt:**  
Implement population count for uint32_t three ways: naive, Kernighan, SWAR (or LUT).

**Implement:**
```c
unsigned popcount32(uint32_t x);
```

**Constraints / expectations:**
- Compare complexity
- Optional LUT

**Follow-ups:**
- Hardware builtin?
- popcount64?

---

### C022 — Reverse bits

**Interview prompt:**  
Reverse bits in a byte and in a 32-bit word. Optimize with a 256-entry LUT for bytes.

**Implement:**
```c
uint8_t rev8(uint8_t x);
uint32_t rev32(uint32_t x);
```

**Constraints / expectations:**
- Correctness first
- LUT optional optimization

**Follow-ups:**
- Lazy LUT init?
- Use in bitmap flip interview?

---

### C023 — Flip MSB and LSB

**Interview prompt:**  
Invert only the most-significant and least-significant bits of a uint8_t in place.

**Implement:**
```c
void flip_hi_lo(uint8_t *b);
```

**Constraints / expectations:**
- NULL check
- Single XOR mask preferred

**Follow-ups:**
- Do the same for uint32_t MSB/LSB
- Endian confusion?

---

### C024 — get_bits / set_bits

**Interview prompt:**  
Extract and insert arbitrary bitfields from a register value.

**Implement:**
```c
uint32_t get_bits(uint32_t val, unsigned shift, unsigned width);
uint32_t set_bits(uint32_t val, unsigned shift, unsigned width, uint32_t field);
```

**Constraints / expectations:**
- Mask safely for width 1..32
- Define width=32 behavior

**Follow-ups:**
- Signed fields?
- Atomic RMW wrapper?

---

### C025 — Power-of-two helpers

**Interview prompt:**  
Detect power-of-two and round up to next power-of-two with overflow handling.

**Implement:**
```c
int is_pow2(size_t x);
int next_pow2(size_t x, size_t *out);
```

**Constraints / expectations:**
- 0 is not power of two
- Overflow returns error

**Follow-ups:**
- Bit-twiddle vs builtin clz
- Ring size use case

---

### C026 — floor_log2

**Interview prompt:**  
Compute floor(log2(n)) for uint32_t without libm. Define n=0 behavior.

**Implement:**
```c
int floor_log2_u32(uint32_t n); /* return -1 if n==0 */
```

**Constraints / expectations:**
- No floating point
- clz-based OK

**Follow-ups:**
- log2 of non-pow2
- 64-bit version

---

### C027 — Parity / nibble swap / odd-even swap

**Interview prompt:**  
Implement parity, swap high/low nibble, and swap odd/even bits of a byte.

**Implement:**
```c
int parity8(uint8_t x);
uint8_t swap_nibbles(uint8_t x);
uint8_t swap_odd_even_bits(uint8_t x);
```

**Constraints / expectations:**
- Clear definitions
- Branchless preferred

**Follow-ups:**
- Where used in protocols?
- LUT tradeoffs

---

### C028 — Gray code

**Interview prompt:**  
Implement binary↔Gray encode/decode for uint32_t.

**Implement:**
```c
uint32_t to_gray(uint32_t x);
uint32_t from_gray(uint32_t g);
```

**Constraints / expectations:**
- Correct inverse
- Explain use in encoders/rotary

**Follow-ups:**
- Incremental Gray counters
- Hardware rotary interview link

---

### C029 — Saturating add/sub

**Interview prompt:**  
Implement saturating arithmetic for uint8_t and uint16_t.

**Implement:**
```c
uint8_t sat_add_u8(uint8_t a, uint8_t b);
uint8_t sat_sub_u8(uint8_t a, uint8_t b);
uint16_t sat_add_u16(uint16_t a, uint16_t b);
```

**Constraints / expectations:**
- No UB
- Exact saturate to max/min

**Follow-ups:**
- Signed saturating add
- DSP builtins

---

### C030 — Q15 multiply

**Interview prompt:**  
Implement Q1.15 fixed-point multiply producing Q1.15 (with rounding optional).

**Implement:**
```c
int16_t q15_mul(int16_t a, int16_t b);
```

**Constraints / expectations:**
- Define format
- Avoid overflow in intermediate

**Follow-ups:**
- Q31 mul
- Saturation?

---

### C031 — Unpack LE struct from memory dump

**Interview prompt:**  
Given a little-endian memory dump and a struct with padding rules, extract fields correctly (classic Tesla-style).

**Implement:**
```c
typedef struct { uint8_t count; uint16_t data[2]; uint32_t timestamp; } packet_S;
void parse_packet_le(const uint8_t *mem, packet_S *out);
```

**Constraints / expectations:**
- Account for padding/alignment as specified
- Also answer big-endian variant if asked

**Follow-ups:**
- Natural alignment layout diagram
- Packed alternative

---

### C032 — Pack struct to BE wire image

**Interview prompt:**  
Serialize a struct to a big-endian wire buffer without relying on host layout.

**Implement:**
```c
struct msg { uint8_t type; uint16_t id; uint32_t val; };
void pack_msg_be(uint8_t out[7], const struct msg *m);
```

**Constraints / expectations:**
- Explicit offsets
- Tests with known vector

**Follow-ups:**
- Add CRC trailer
- Version field

---

### C033 — Expand 5-bit to 8-bit channel

**Interview prompt:**  
Map 0..31 to 0..255 so min→0 and max→255 using shifts (RGB565 style).

**Implement:**
```c
uint8_t expand5to8(uint8_t v5);
```

**Constraints / expectations:**
- v5 input 0..31
- Prefer bit replicate form

**Follow-ups:**
- expand6to8
- Why not v*255/31 only?

---

### C034 — RGB565 ↔ RGB888

**Interview prompt:**  
Convert between RGB565 and RGB888.

**Implement:**
```c
uint16_t rgb888_to_565(uint8_t r,uint8_t g,uint8_t b);
void rgb565_to_888(uint16_t c, uint8_t *r,uint8_t *g,uint8_t *b);
```

**Constraints / expectations:**
- Correct bit widths
- Document lossy conversion

**Follow-ups:**
- Endian of uint16 stored in memory?
- Premultiplied alpha?

---

### C035 — Simple checksums

**Interview prompt:**  
Implement additive checksum, XOR checksum, and Fletcher-16.

**Implement:**
```c
uint8_t sum8(const uint8_t *b,size_t n);
uint8_t xor8(const uint8_t *b,size_t n);
uint16_t fletcher16(const uint8_t *b,size_t n);
```

**Constraints / expectations:**
- Define empty input
- Document limitations vs CRC

**Follow-ups:**
- Ones complement checksum?
- When CRC is required?

---

### C036 — CRC-8

**Interview prompt:**  
Implement CRC-8 with a given polynomial (e.g. 0x07). Provide bit-wise and table-driven versions.

**Implement:**
```c
uint8_t crc8(const uint8_t *data, size_t len, uint8_t poly, uint8_t init);
```

**Constraints / expectations:**
- Match a known test vector you state
- Table optional

**Follow-ups:**
- Reflected CRC?
- Init/xorout variants

---

### C037 — CRC-16-CCITT

**Interview prompt:**  
Implement CRC-16-CCITT (poly 0x1021) commonly used in telecom/embed protocols.

**Implement:**
```c
uint16_t crc16_ccitt(const uint8_t *data, size_t len);
```

**Constraints / expectations:**
- Document init value (often 0xFFFF)
- Provide test vector

**Follow-ups:**
- Modbus CRC16 difference
- Incremental crc update

---

### C038 — CRC-32

**Interview prompt:**  
Implement CRC-32 (Ethernet poly). Table-driven is expected.

**Implement:**
```c
uint32_t crc32(const uint8_t *data, size_t len);
```

**Constraints / expectations:**
- Standard init/xorout
- Table in .rodata

**Follow-ups:**
- Slice-by-4 optimization
- Hardware CRC unit

---

### C039 — Bitstream reader

**Interview prompt:**  
Implement a reader that pulls arbitrary bit widths MSB-first from a byte stream.

**Implement:**
```c
typedef struct { const uint8_t *p; size_t nbytes; size_t bitpos; } bitreader_t;
int br_init(bitreader_t *br, const uint8_t *p, size_t nbytes);
int br_get(bitreader_t *br, unsigned width, uint32_t *out); /* width 1..32 */
```

**Constraints / expectations:**
- EOF error
- No overrun

**Follow-ups:**
- LSB-first mode
- Alignment helpers

---

### C040 — Hamming ECC (simplified)

**Interview prompt:**  
Implement (7,4) Hamming encode/decode with single-bit error correction.

**Implement:**
```c
uint8_t hamming74_encode(uint8_t nibble);
int hamming74_decode(uint8_t code, uint8_t *nibble_out); /* returns 0 ok, 1 corrected, <0 fail */
```

**Constraints / expectations:**
- Correct syndrome logic
- Define double-error behavior

**Follow-ups:**
- SECDED extended Hamming
- Why ECC memory uses this

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
### C056 — Fixed-size memory pool

**Interview prompt:**  
Implement a fixed-block allocator used in firmware instead of malloc.

**Implement:**
```c
typedef struct pool pool_t;
int pool_init(pool_t *p, void *backing, size_t backing_size, size_t block_size);
void *pool_alloc(pool_t *p);
void pool_free(pool_t *p, void *blk);
```

**Constraints / expectations:**
- O(1) alloc/free
- Handle exhaustion
- Alignment of blocks

**Follow-ups:**
- Fragmentation?
- Thread/ISR safety next?

---

### C057 — ISR-safe memory pool

**Interview prompt:**  
Make the pool safe to allocate from thread context and free from ISR (or vice versa as specified).

**Implement:**
```c
void *pool_alloc_isrsafe(pool_t *p);
void pool_free_isrsafe(pool_t *p, void *blk);
```

**Constraints / expectations:**
- Critical section or lock-free freelist
- Document context rules

**Follow-ups:**
- Can both ends be ISRs?
- Priority inversion?

---

### C058 — Pool statistics

**Interview prompt:**  
Extend the pool with high-watermark, current in-use, fail counts.

**Implement:**
```c
typedef struct { size_t used, hw, fails, capacity; } pool_stats_t;
void pool_get_stats(const pool_t *p, pool_stats_t *s);
```

**Constraints / expectations:**
- Update on alloc/free
- ISR-safe reads if claimed

**Follow-ups:**
- Reset watermark?
- Export via sysfs later?

---

### C059 — Pool guard magic / double-free detect

**Interview prompt:**  
Add canaries and detect double-free / corruption in a debug pool.

**Implement:**
```c
void *pool_alloc_debug(pool_t *p);
void pool_free_debug(pool_t *p, void *blk); /* abort/log on double-free */
```

**Constraints / expectations:**
- Magic before/after payload optional
- Clear on free

**Follow-ups:**
- Use-after-free poisoning?
- Overhead cost?

---

### C060 — Bitmap slot allocator

**Interview prompt:**  
Allocate/free indices 0..N-1 using a bitmap.

**Implement:**
```c
typedef struct { uint32_t *bits; unsigned n; } bitmap_alloc_t;
int bitmap_alloc_init(bitmap_alloc_t *a, uint32_t *bits, unsigned n);
int bitmap_alloc(bitmap_alloc_t *a); /* returns idx or -1 */
void bitmap_free(bitmap_alloc_t *a, unsigned idx);
```

**Constraints / expectations:**
- Correct bit indexing
- O(n) scan OK if noted

**Follow-ups:**
- Find-first-set optimize
- Hierarchical bitmap

---

### C061 — First-fit free-list allocator

**Interview prompt:**  
Implement a simple variable-size allocator over a memory region using an explicit free list.

**Implement:**
```c
int heap_init(void *mem, size_t size);
void *heap_malloc(size_t n);
void heap_free(void *ptr);
```

**Constraints / expectations:**
- Header per block
- Alignment
- First-fit

**Follow-ups:**
- Best-fit vs first-fit
- External fragmentation

---

### C062 — Heap block split

**Interview prompt:**  
When allocating from a free block larger than needed, split the remainder back onto the free list.

**Implement:**
```c
/* extend heap_malloc to split */
```

**Constraints / expectations:**
- Minimum remainder size
- Avoid tiny unusable fragments

**Follow-ups:**
- Coalesce interaction
- Header overhead

---

### C063 — Heap coalesce on free

**Interview prompt:**  
On free, merge with adjacent free blocks.

**Implement:**
```c
void heap_free(void *ptr); /* with coalesce */
```

**Constraints / expectations:**
- Boundary tags or prev pointer
- Correct adjacent detection

**Follow-ups:**
- Footers?
- Sorted free list?

---

### C064 — Bump / arena allocator

**Interview prompt:**  
Implement a resettable bump allocator for boot or frame allocations.

**Implement:**
```c
typedef struct { uint8_t *base,*cur,*end; } arena_t;
void arena_init(arena_t *a, void *mem, size_t n);
void *arena_alloc(arena_t *a, size_t n, size_t align);
void arena_reset(arena_t *a);
```

**Constraints / expectations:**
- Alignment support
- No individual free

**Follow-ups:**
- Scoped arenas
- Thread-local arena

---

### C065 — Aligned allocation API

**Interview prompt:**  
Allocate memory with a power-of-two alignment from your heap/pool.

**Implement:**
```c
void *aligned_alloc_pool(pool_t *p, size_t align); /* or heap */
void *heap_aligned_alloc(size_t size, size_t align);
```

**Constraints / expectations:**
- align PoT
- Store cookie to free correctly if needed

**Follow-ups:**
- posix_memalign semantics
- Over-aligned DMA

---

### C066 — DMA-capable buffer allocator

**Interview prompt:**  
Provide buffers suitable for DMA: alignment + note on cacheability flags.

**Implement:**
```c
void *dma_buffer_alloc(size_t size, size_t align);
void dma_buffer_free(void *p);
```

**Constraints / expectations:**
- Document cache clean/invalidate responsibility
- Alignment

**Follow-ups:**
- CMA / uncached regions
- Live pointer handoff

---

### C067 — Refcounted buffer object

**Interview prompt:**  
Implement get/put reference counting that frees at zero.

**Implement:**
```c
typedef struct buffer buffer_t;
buffer_t *buffer_create(size_t n);
buffer_t *buffer_get(buffer_t *b);
void buffer_put(buffer_t *b);
uint8_t *buffer_data(buffer_t *b);
size_t buffer_len(const buffer_t *b);
```

**Constraints / expectations:**
- Atomic or IRQ-safe if specified
- No use-after-free

**Follow-ups:**
- Weak refs?
- Sharing across cores

---

### C068 — Slab cache for one type

**Interview prompt:**  
Implement a slab for fixed-size objects with optional ctor/dtor.

**Implement:**
```c
typedef struct slab slab_t;
int slab_init(slab_t *s, size_t obj_size, size_t count, void *backing,
              void (*ctor)(void*), void (*dtor)(void*));
void *slab_alloc(slab_t *s);
void slab_free(slab_t *s, void *obj);
```

**Constraints / expectations:**
- ctor on alloc or at init—document
- O(1)

**Follow-ups:**
- Linux kmem_cache analogy
- Coloring?

---

### C069 — Buddy allocator (small)

**Interview prompt:**  
Implement a buddy allocator for orders 0..MAX_ORDER over a power-of-two region.

**Implement:**
```c
int buddy_init(void *mem, size_t size);
void *buddy_alloc(unsigned order);
void buddy_free(void *ptr, unsigned order);
```

**Constraints / expectations:**
- Correct buddy address math
- Free-list per order

**Follow-ups:**
- Why GPUs/OS use buddies
- Fragmentation behavior

---

### C070 — Fix ownership/UAF in callback queue

**Interview prompt:**  
A queue of callbacks frees objects incorrectly. Rewrite ownership so lifetimes are correct.

**Implement:**
```c
typedef void (*cb_t)(void *ctx);
int post_cb(cb_t cb, void *ctx);
void drain_cbs(void);
```

**Constraints / expectations:**
- Define who frees ctx
- No UAF if cancel happens

**Follow-ups:**
- refcounted ctx
- Cancellation races

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

### C121 — MMIO read/write

**Interview prompt:**  
Implement 32-bit MMIO accessors using volatile.

**Implement:**
```c
uint32_t reg_read32(volatile uint32_t *addr);
void reg_write32(volatile uint32_t *addr, uint32_t val);
```

**Constraints / expectations:**
- volatile correct
- Explain why pointers are volatile

**Follow-ups:**
- 8/16-bit accessors
- Memory barriers for posting

---

### C122 — Register RMW helper

**Interview prompt:**  
Implement read-modify-write with mask.

**Implement:**
```c
void reg_rmw32(volatile uint32_t *addr, uint32_t mask, uint32_t value);
```

**Constraints / expectations:**
- Only modify masked bits
- Document concurrency needs

**Follow-ups:**
- Atomic RMW if ISR shares
- Write-only regs

---

### C123 — Bit set/clear/toggle helpers

**Interview prompt:**  
Convenience wrappers around RMW.

**Implement:**
```c
void reg_set_bits(volatile uint32_t *a, uint32_t bits);
void reg_clr_bits(volatile uint32_t *a, uint32_t bits);
void reg_toggle_bits(volatile uint32_t *a, uint32_t bits);
```

**Constraints / expectations:**
- Correctness
- No accidental wider clears

**Follow-ups:**
- HW toggle registers that aren't RMW

---

### C124 — wait_for_bit with timeout

**Interview prompt:**  
Poll until a status bit becomes set/cleared or timeout.

**Implement:**
```c
int wait_for_bit(volatile uint32_t *addr, uint32_t mask, int set, uint32_t timeout_us);
```

**Constraints / expectations:**
- Use provided delay/timebase
- Return timeout error

**Follow-ups:**
- Busy wait vs sleep
- WFE/WFI

---

### C125 — Poll with deadline API

**Interview prompt:**  
Same as wait_for_bit but using absolute deadline ticks to avoid drift.

**Implement:**
```c
int wait_until(volatile uint32_t *addr, uint32_t mask, int set, uint32_t deadline_ticks);
```

**Constraints / expectations:**
- Wrap-safe time compare
- No extra drift

**Follow-ups:**
- Backoff delay
- Instrumentation

---

### C126 — Register map + static assert offsets

**Interview prompt:**  
Define a peripheral register map struct and assert offsets match the datasheet numbers given in the prompt.

**Implement:**
```c
struct uart_regs { uint32_t dr; uint32_t rsr; uint32_t reserved0[4]; uint32_t fr; /* ... */ };
/* static asserts */
```

**Constraints / expectations:**
- Match fictional datasheet offsets you state
- volatile uint32_t fields

**Follow-ups:**
- Reserved holes
- Array of instances

---

### C127 — Write posting barrier

**Interview prompt:**  
After writing a control register, ensure it is visible to device before continuing (readback barrier helper).

**Implement:**
```c
void reg_write32_posted(volatile uint32_t *addr, uint32_t val);
void mmio_barrier_after_write(volatile uint32_t *dummy_status);
```

**Constraints / expectations:**
- Explain posted writes
- Use readback pattern

**Follow-ups:**
- DMA coherency vs MMIO posting
- DMB on ARM

---

### C128 — Shadow registers for write-only HW

**Interview prompt:**  
Keep software shadows for write-only registers so you can RMW fields.

**Implement:**
```c
typedef struct { volatile uint32_t *hw; uint32_t shadow; } wo_reg_t;
void wo_set_bits(wo_reg_t *r, uint32_t bits);
void wo_clr_bits(wo_reg_t *r, uint32_t bits);
```

**Constraints / expectations:**
- Shadow and HW stay in sync
- Init shadow

**Follow-ups:**
- HW can change under you?
- Multi-thread shadows

---

### C129 — Fake MMIO for host tests

**Interview prompt:**  
Create a fake register block so driver logic can be unit-tested on host.

**Implement:**
```c
typedef struct { uint32_t storage[64]; } fake_mmio_t;
uint32_t fake_read32(fake_mmio_t *f, size_t off);
void fake_write32(fake_mmio_t *f, size_t off, uint32_t v);
```

**Constraints / expectations:**
- Hook side effects optional (e.g., writing CMD sets STATUS)
- Pointer map API like real driver

**Follow-ups:**
- How far to simulate HW
- CI usage

---

### C130 — Atomic RMW shared with ISR

**Interview prompt:**  
Thread and ISR both modify the same control register; make it safe.

**Implement:**
```c
void thread_enable_rx(void);
void isr_clear_error(void);
```

**Constraints / expectations:**
- Critical section or atomic HW bit set regs
- No lost bits

**Follow-ups:**
- HW bit-band / set-clear regs
- Compare-and-swap MMIO?

---

### C131 — Multi-register update sequence

**Interview prompt:**  
Some devices require writing REG_A then REG_B within constraints, or holding a latch. Implement a safe update function.

**Implement:**
```c
int device_set_config(uint32_t cfg_hi, uint32_t cfg_lo);
```

**Constraints / expectations:**
- Document required order
- Timeout if HW rejects

**Follow-ups:**
- Partial failure recovery
- IRQs during sequence

---

### C132 — Endian MMIO helpers

**Interview prompt:**  
Peripheral is big-endian; CPU is little-endian. Implement accessors that swap as needed.

**Implement:**
```c
uint32_t be_reg_read32(volatile uint32_t *addr);
void be_reg_write32(volatile uint32_t *addr, uint32_t cpu_val);
```

**Constraints / expectations:**
- Clear CPU vs wire endian
- Use byteswap

**Follow-ups:**
- 16-bit buses
- When HW does swapping

---

### C133 — FIELD_GET / FIELD_PREP macros

**Interview prompt:**  
Implement Linux-style field get/prep macros for a mask.

**Implement:**
```c
#define FIELD_GET(mask, reg) ...
#define FIELD_PREP(mask, val) ...
uint32_t encode_speed(uint32_t speed_code);
uint32_t decode_speed(uint32_t reg);
```

**Constraints / expectations:**
- mask contiguous bits
- No undefined shifts

**Follow-ups:**
- GENMASK combo
- Compile-time checks

---

### C134 — Soft reset with timeout

**Interview prompt:**  
Write a soft-reset sequence: set reset bit, wait for ack/clear, timeout and return error.

**Implement:**
```c
int device_soft_reset(uint32_t timeout_ms);
```

**Constraints / expectations:**
- Don't spin forever
- Leave device in known state on failure if possible

**Follow-ups:**
- Reset from ISR?
- Recovery retries

---

### C135 — Register dump logger

**Interview prompt:**  
Dump a range of registers into a caller buffer as text or binary words for debug.

**Implement:**
```c
size_t reg_dump(volatile uint32_t *base, size_t count, char *out, size_t out_cap);
```

**Constraints / expectations:**
- Bounded output
- Readable format

**Follow-ups:**
- debugfs analogy
- Sensitive registers redaction

---
### C136 — UART polling TX/RX

**Interview prompt:**  
Implement blocking UART transmit/receive by polling status registers (fake MMIO OK).

**Implement:**
```c
int uart_putc(char c);
int uart_getc(uint32_t timeout_ms);
int uart_write(const char *s, size_t n);
```

**Constraints / expectations:**
- Timeout on RX
- Check TX empty / RX ready bits

**Follow-ups:**
- Error flags framing/overrun
- Non-blocking API

---

### C137 — UART IRQ RX to ring

**Interview prompt:**  
IRQ on RX pushes bytes into a ring buffer consumed by a task.

**Implement:**
```c
void uart_rx_isr(void);
size_t uart_read(uint8_t *dst, size_t n);
```

**Constraints / expectations:**
- ISR short
- Drop policy on full

**Follow-ups:**
- High-water callback
- DMA later

---

### C138 — UART IRQ TX from ring

**Interview prompt:**  
Kickstart TX interrupt; ISR pulls from ring until empty then disables TX IRQ.

**Implement:**
```c
int uart_write_irq(const uint8_t *src, size_t n);
void uart_tx_isr(void);
```

**Constraints / expectations:**
- Enable TX IRQ only when needed
- No busy wait in write if async—document

**Follow-ups:**
- TX complete callback
- Half-duplex RS485 DE pin

---

### C139 — UART drain / flush

**Interview prompt:**  
Wait until TX ring+shift register drained.

**Implement:**
```c
int uart_flush(uint32_t timeout_ms);
```

**Constraints / expectations:**
- Timeout
- ISR interaction

**Follow-ups:**
- flush vs power-off
- Break signal

---

### C140 — Software RTS/CTS

**Interview prompt:**  
Implement SW flow control: stop accepting RX when local ring high; drive RTS; honor CTS before TX.

**Implement:**
```c
void uart_flow_on_rx_wm(void);
int uart_write_with_cts(const uint8_t *b, size_t n);
```

**Constraints / expectations:**
- Watermarks
- Document pin polarity

**Follow-ups:**
- HW flow control regs
- Deadlock if both sides stuck

---

### C141 — UART error recovery

**Interview prompt:**  
Count framing/overrun/parity errors in ISR and recover receiver.

**Implement:**
```c
void uart_err_isr(void);
typedef struct { uint32_t overrun, framing, parity; } uart_err_t;
```

**Constraints / expectations:**
- Read status correctly (order)
- Clear sticky errors

**Follow-ups:**
- When to reset RX FIFO
- User-visible stats

---

### C142 — SPI polling transfer

**Interview prompt:**  
Full-duplex SPI transfer of n bytes polling TX/RX flags.

**Implement:**
```c
int spi_transfer(const uint8_t *tx, uint8_t *rx, size_t n);
```

**Constraints / expectations:**
- Handle tx or rx NULL as discard/dummy
- CS control outside or inside—document

**Follow-ups:**
- Mode 0..3 timing
- Word size 16-bit

---

### C143 — SPI IRQ byte state machine

**Interview prompt:**  
Drive SPI transfer via interrupts with a state machine tracking remaining bytes.

**Implement:**
```c
int spi_transfer_irq(const uint8_t *tx, uint8_t *rx, size_t n);
void spi_isr(void);
```

**Constraints / expectations:**
- Completion signal
- Error path

**Follow-ups:**
- DMA upgrade
- Queue of transactions

---

### C144 — SPI multi-device CS

**Interview prompt:**  
Select among multiple CS lines; ensure only one device selected.

**Implement:**
```c
void spi_select(unsigned cs_id);
void spi_deselect(void);
int spi_transfer_cs(unsigned cs_id, const uint8_t *tx, uint8_t *rx, size_t n);
```

**Constraints / expectations:**
- Default idle CS level
- Mutex if multi-thread

**Follow-ups:**
- Shared bus with interrupts
- Timing delays after CS

---

### C145 — I2C write state machine

**Interview prompt:**  
Implement master write: START, addr, data bytes, STOP with ACK checks.

**Implement:**
```c
int i2c_write(uint8_t addr7, const uint8_t *data, size_t n, uint32_t timeout_ms);
```

**Constraints / expectations:**
- NACK handling
- Timeouts each phase

**Follow-ups:**
- 10-bit address
- Repeated start next

---

### C146 — I2C write-then-read (repeated start)

**Interview prompt:**  
Classic sensor transaction: write register address, repeated START, read N bytes.

**Implement:**
```c
int i2c_write_read(uint8_t addr7, const uint8_t *wr, size_t wn,
                   uint8_t *rd, size_t rn, uint32_t timeout_ms);
```

**Constraints / expectations:**
- No STOP between if repeated start
- ACK last byte rules

**Follow-ups:**
- SMBus differences
- Clock stretching wait

---

### C147 — I2C error taxonomy

**Interview prompt:**  
Map NACK/arbitration loss/timeout to distinct error codes and recover bus state.

**Implement:**
```c
typedef enum { I2C_OK, I2C_ENACK, I2C_ETIMEOUT, I2C_EARB, I2C_EBUS } i2c_err_t;
i2c_err_t i2c_write(...);
```

**Constraints / expectations:**
- Leave bus idle on error if possible
- Distinguish addr NACK vs data NACK if HW allows

**Follow-ups:**
- Retries
- Logging

---

### C148 — I2C bus recovery

**Interview prompt:**  
If SDA stuck low, toggle SCL up to 9 times and generate STOP to free the bus.

**Implement:**
```c
int i2c_bus_recover(void);
```

**Constraints / expectations:**
- GPIO bit-bang SCL/SDA
- Return success/fail

**Follow-ups:**
- When to auto-recover
- Device that holds SDA forever

---

### C149 — GPIO driver stubs

**Interview prompt:**  
Implement GPIO get/set/direction and edge IRQ configure against a fake register map.

**Implement:**
```c
void gpio_set_dir(unsigned pin, int output);
void gpio_write(unsigned pin, int level);
int gpio_read(unsigned pin);
void gpio_irq_config(unsigned pin, int rising, int falling, void (*cb)(void));
```

**Constraints / expectations:**
- Pin range checks
- Callback from ISR context

**Follow-ups:**
- Debounce link
- Open-drain

---

### C150 — GPIO debounce state machine

**Interview prompt:**  
Sample or use timers to produce a stable digital output from a bouncing input.

**Implement:**
```c
void debounce_on_edge(void);
int debounce_stable_level(void);
```

**Constraints / expectations:**
- Configurable debounce ms
- No false triggers

**Follow-ups:**
- Integrate with button events
- Analog comparator noise

---

### C151 — PWM period/duty

**Interview prompt:**  
Set PWM frequency and duty cycle given a timer clock.

**Implement:**
```c
int pwm_set(uint32_t clk_hz, uint32_t freq_hz, uint32_t duty_percent);
```

**Constraints / expectations:**
- Integer math careful
- Duty 0..100
- Error if impossible divisors

**Follow-ups:**
- High-res PWM
- Dead-time for H-bridge

---

### C152 — ADC read with averaging

**Interview prompt:**  
Read ADC with settling delay, timeout, optional N-sample average.

**Implement:**
```c
int adc_read_mv(unsigned channel, unsigned samples, uint32_t *mv_out);
```

**Constraints / expectations:**
- Timeout
- Reject invalid channel

**Follow-ups:**
- DMA continuous ADC
- Calibration offset/gain

---

### C153 — Bit-banged UART TX

**Interview prompt:**  
Transmit a byte on a GPIO UART TX line using delays for baud timing (timer mock OK).

**Implement:**
```c
void softuart_tx_byte(uint8_t b);
void softuart_write(const uint8_t *data, size_t n);
```

**Constraints / expectations:**
- Start/stop bits
- Disable IRQ during bit or compensate—discuss

**Follow-ups:**
- RX hard part
- Baud accuracy

---

### C154 — Button long-press / double-click

**Interview prompt:**  
From edge events + time, detect click, double-click, long-press.

**Implement:**
```c
typedef enum { BTN_NONE, BTN_CLICK, BTN_DOUBLE, BTN_LONG } btn_ev_t;
btn_ev_t button_task(uint32_t now_ms, int level);
```

**Constraints / expectations:**
- Configurable thresholds
- Clean state machine

**Follow-ups:**
- Triple click
- Repeat while hold

---

### C155 — Quadrature encoder decode

**Interview prompt:**  
Given two square waves A/B, decode direction and count (Gray-code state table).

**Implement:**
```c
void encoder_update(int a, int b); /* call on change or sample */
int32_t encoder_count(void);
```

**Constraints / expectations:**
- Correct 4x decoding table
- Illegal transitions handled

**Follow-ups:**
- Speed estimation
- Index Z channel

---

### C156 — Shift register bit-bang

**Interview prompt:**  
Drive a 74HC595-like output shift register: data/clock/latch.

**Implement:**
```c
void sr_write8(uint8_t value);
void sr_write_buf(const uint8_t *v, size_t n);
```

**Constraints / expectations:**
- Timing order correct
- Latch once per frame

**Follow-ups:**
- Daisy chain
- SPI HW instead

---

### C157 — 1-Wire reset + read byte

**Interview prompt:**  
Implement reset/presence pulse and read a byte with timing slots (delay stubs provided).

**Implement:**
```c
int ow_reset(void); /* 1 presence, 0 none, <0 error */
uint8_t ow_read_byte(void);
void ow_write_byte(uint8_t b);
```

**Constraints / expectations:**
- Document timing constants
- Bit order

**Follow-ups:**
- Search ROM
- CRC of ROM

---

### C158 — Multi-instance driver context

**Interview prompt:**  
Refactor a UART driver that used globals into `struct uart *` instance pointers.

**Implement:**
```c
typedef struct uart uart_t;
int uart_init(uart_t *u, uintptr_t mmio_base, ring_t *rx, ring_t *tx);
int uart_write(uart_t *u, const uint8_t *b, size_t n);
```

**Constraints / expectations:**
- No globals
- Reentrant across instances

**Follow-ups:**
- Container_of from ISR
- Probe/remove

---

### C159 — Idempotent init/deinit

**Interview prompt:**  
init() may be called twice; deinit() may be called without init. Make safe.

**Implement:**
```c
int uart_init(uart_t *u, ...);
void uart_deinit(uart_t *u);
```

**Constraints / expectations:**
- State flag
- Free resources once

**Follow-ups:**
- Partial init failure
- re-init after fault

---

### C160 — Non-blocking read/write EAGAIN

**Interview prompt:**  
Implement non-blocking APIs returning would-block when rings empty/full.

**Implement:**
```c
int uart_read_nb(uart_t *u, uint8_t *b, size_t n); /* return bytes or -EAGAIN */
int uart_write_nb(uart_t *u, const uint8_t *b, size_t n);
```

**Constraints / expectations:**
- Defined error codes
- No busy spin

**Follow-ups:**
- poll readiness
- POSIX analogy

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
### C186 — Length+CRC frame parser FSM

**Interview prompt:**  
Parse a stream into frames: magic, length, payload, CRC16. Use an explicit FSM.

**Implement:**
```c
typedef enum { ST_SYNC, ST_LEN, ST_PAYLOAD, ST_CRC } st_t;
int parser_feed(parser_t *p, uint8_t byte); /* returns 1 when frame ready */
```

**Constraints / expectations:**
- Reject oversize lengths
- CRC check

**Follow-ups:**
- Resync strategy
- Zero-copy payload

---

### C187 — Resync after corruption

**Interview prompt:**  
After CRC fail, recover by searching for next sync byte without wedging.

**Implement:**
```c
/* extend parser with resync */
```

**Constraints / expectations:**
- Don't infinite loop on garbage
- Count errors

**Follow-ups:**
- Sliding window sync
- Escape codes

---

### C188 — COBS encode/decode

**Interview prompt:**  
Implement Consistent Overhead Byte Stuffing encode and decode.

**Implement:**
```c
size_t cobs_encode(const uint8_t *in, size_t n, uint8_t *out, size_t out_cap);
size_t cobs_decode(const uint8_t *in, size_t n, uint8_t *out, size_t out_cap);
```

**Constraints / expectations:**
- Handle zeros
- Bounds checks
- Return error codes

**Follow-ups:**
- Why COBS vs HDLC
- Delimiter framing

---

### C189 — SLIP encode/decode

**Interview prompt:**  
Implement SLIP framing with END/ESC.

**Implement:**
```c
size_t slip_encode(const uint8_t *in,size_t n,uint8_t *out,size_t cap);
int slip_feed(slip_t *s, uint8_t b, uint8_t *frame, size_t cap, size_t *len);
```

**Constraints / expectations:**
- ESC mapping correct
- Overflow error

**Follow-ups:**
- IP over serial history
- CRC on top

---

### C190 — Bit stuffing (simplified HDLC)

**Interview prompt:**  
Stuff a bit so that five consecutive 1s get a 0 inserted; implement destuff.

**Implement:**
```c
size_t bit_stuff(const uint8_t *in, size_t nbits, uint8_t *out, size_t out_bits_cap);
size_t bit_destuff(...);
```

**Constraints / expectations:**
- Operate at bit level carefully
- Document API units

**Follow-ups:**
- Flag sequence 01111110
- Abort sequence

---

### C191 — TLV parser

**Interview prompt:**  
Parse Type-Length-Value records with strict bounds checking.

**Implement:**
```c
typedef struct { uint8_t type; uint16_t len; const uint8_t *val; } tlv_t;
int tlv_parse_all(const uint8_t *buf, size_t n, tlv_t *out, size_t max_out, size_t *count);
```

**Constraints / expectations:**
- Reject truncated TLVs
- Overflow-safe len

**Follow-ups:**
- Nested TLV
- Unknown type policy

---

### C192 — Incremental stream parser on ring

**Interview prompt:**  
Consume from a ring buffer into parser without requiring contiguous frame in memory (or gather first—justify).

**Implement:**
```c
int parser_consume_ring(parser_t *p, ring_t *r);
```

**Constraints / expectations:**
- Leave unconsumed bytes
- Handle wrap

**Follow-ups:**
- Contiguous gather helper
- Backpressure

---

### C193 — Escape-delimited binary protocol

**Interview prompt:**  
Frames start/end with 0x7E; 0x7D escapes next byte XOR 0x20. Implement unescape FSM.

**Implement:**
```c
int esc_feed(esc_t *e, uint8_t b, uint8_t *frame, size_t cap, size_t *len);
```

**Constraints / expectations:**
- Overflow
- Bad escape handling

**Follow-ups:**
- Compare to SLIP
- CRC placement

---

### C194 — Opcode command dispatcher

**Interview prompt:**  
After parsing a frame, dispatch opcode to handlers with payload slice.

**Implement:**
```c
int handle_frame(const uint8_t *frame, size_t len);
```

**Constraints / expectations:**
- Validate len per opcode
- Unknown opcode

**Follow-ups:**
- Versioning
- Async responses

---

### C195 — Fragment reassembly

**Interview prompt:**  
Messages arrive as fragments with id/offset/total; reassemble into a buffer.

**Implement:**
```c
int frag_submit(uint16_t id, uint16_t offset, uint16_t total, const uint8_t *data, uint16_t len);
int frag_ready(uint16_t id, uint8_t *out, size_t cap, size_t *out_len);
```

**Constraints / expectations:**
- Overlap/gap detection
- Timeout incomplete

**Follow-ups:**
- Multiple concurrent IDs
- Bitmap of received

---

### C196 — Seqno duplicate/gap detect

**Interview prompt:**  
Track sequence numbers; drop duplicates; detect gaps.

**Implement:**
```c
int seq_check(seq_t *s, uint16_t seq); /* 0 new, 1 dup, 2 gap */
```

**Constraints / expectations:**
- Wrap around
- Window optional

**Follow-ups:**
- Retransmit request
- Reorder buffer

---

### C197 — ACK timeout retransmit queue

**Interview prompt:**  
Keep unacked packets; retransmit on timeout; free on ACK.

**Implement:**
```c
int tx_submit(const uint8_t *frame, size_t n, uint16_t seq);
void on_ack(uint16_t seq);
void on_tick_1ms(void);
```

**Constraints / expectations:**
- Max retries
- Backoff optional

**Follow-ups:**
- Selective ACK
- Congestion

---

### C198 — Small sliding window

**Interview prompt:**  
Allow N outstanding unacked frames (N small, e.g. 4).

**Implement:**
```c
int window_send(...);
void window_on_ack(uint16_t seq);
```

**Constraints / expectations:**
- Advance base correctly
- Block when window full

**Follow-ups:**
- Go-Back-N vs selective
- Duplicate ACK

---

### C199 — ASCII telemetry line parser

**Interview prompt:**  
Parse lines like `T=25.5,H=40\n` into fields without malloc.

**Implement:**
```c
int parse_telemetry(const char *line, float *t, float *h);
```

**Constraints / expectations:**
- Robust to missing fields
- No buffer overflow

**Follow-ups:**
- Integer fixed-point instead of float
- Checksum field

---

### C200 — Defensive parser hardening

**Interview prompt:**  
Given a buggy parser, add checks: max length, integer overflow on size, reject partial.

**Implement:**
```c
/* fix and show attack inputs you block */
```

**Constraints / expectations:**
- Explicit tests for malice
- Clear errors

**Follow-ups:**
- Fuzzing strategy
- Integer overflow in len+hdr

---

### C201 — Traffic light FSM

**Interview prompt:**  
Implement a traffic light state machine; ignore invalid inputs; support FAULT from any state.

**Implement:**
```c
typedef enum { IDLE, READY, GO, FAULT } st_t;
typedef enum { TIMER, BUTTON, FAULT_EVT } ev_t;
st_t traffic_step(st_t s, ev_t e);
```

**Constraints / expectations:**
- No transition on invalid
- Pure function or with side effects—document

**Follow-ups:**
- Timing table
- Pedestrian phase

---

### C202 — Vending machine FSM (Tesla-style)

**Interview prompt:**  
States IDLE/READY/VENDING/FAULT; inputs COIN, COIN_RETURN, BUTTON, VEND_COMPLETE, GENERIC_FAULT. Invalid inputs do nothing. GENERIC_FAULT→FAULT from any state.

**Implement:**
```c
typedef enum { IDLE, READY, VENDING, FAULT } state_E;
typedef enum { COIN, COIN_RETURN, BUTTON, VEND_COMPLETE, GENERIC_FAULT } input_E;
state_E stateMachine(input_E input);
```

**Constraints / expectations:**
- Initial IDLE
- Return current state
- No crash on unexpected

**Follow-ups:**
- Add refund path
- Unit tests all edges

---

### C203 — Connection FSM

**Interview prompt:**  
DISCONNECTED→CONNECTING→AUTH→READY→ERROR with timeouts.

**Implement:**
```c
st_t conn_step(st_t s, ev_t e, uint32_t now);
```

**Constraints / expectations:**
- Timeout events
- Retry limits

**Follow-ups:**
- Backoff
- TLS analogy

---

### C204 — Driver power FSM

**Interview prompt:**  
OFF/INIT/RUN/SUSPEND/ERROR with legal transitions only.

**Implement:**
```c
int drv_event(drv_t *d, ev_t e);
```

**Constraints / expectations:**
- Illegal transition errors
- Entry/exit actions stubs

**Follow-ups:**
- Runtime PM mapping
- Wake sources

---

### C205 — Hierarchical FSM

**Interview prompt:**  
Parent mode ACTIVE has child states RUNNING/PAUSED. Implement hierarchy.

**Implement:**
```c
/* parent/child state handlers */
```

**Constraints / expectations:**
- Events bubble or consume—document
- Exit child before parent

**Follow-ups:**
- UML statechart features
- Concurrency regions skip

---

### C206 — Table-driven FSM

**Interview prompt:**  
Encode transitions in a table[state][event] = next/action.

**Implement:**
```c
typedef void (*action_t)(void);
typedef struct { int next; action_t act; } cell_t;
int fsm_step(int state, int event);
```

**Constraints / expectations:**
- Sparse table OK
- Bounds check

**Follow-ups:**
- Code gen from table
- Flash size

---

### C207 — Entry/exit actions + guards

**Interview prompt:**  
On transition, run exit(old), action, enter(new). Guards can cancel.

**Implement:**
```c
int fsm_try(fsm_t *f, int event);
```

**Constraints / expectations:**
- Order of actions
- Guard predicates

**Follow-ups:**
- Re-entrant events
- Logging transitions

---

### C208 — Quadrature direction FSM

**Interview prompt:**  
From two sampler bits in a cyclic Gray sequence, decide forward/backward (Google-style).

**Implement:**
```c
typedef enum { FWD, BACK, NONE, ERROR } dir_t;
dir_t direction(uint8_t prev, uint8_t now);
```

**Constraints / expectations:**
- Illegal jumps → ERROR not crash
- Document encoding of two bits

**Follow-ups:**
- Missing sample recovery
- Debounce

---

### C209 — Button UI FSM

**Interview prompt:**  
IDLE→DOWN→HOLD→REPEAT with timings.

**Implement:**
```c
ui_ev_t button_fsm(uint32_t now, int level);
```

**Constraints / expectations:**
- Configurable ms
- Clean edges

**Follow-ups:**
- Multi-button
- Gesture

---

### C210 — Session FSM with timeouts

**Interview prompt:**  
Protocol session with keepalive timeout and retransmit timer integration.

**Implement:**
```c
void session_on_rx(void);
void session_on_tick(uint32_t now);
```

**Constraints / expectations:**
- Armed timers
- State-specific timeout

**Follow-ups:**
- Backoff
- Max lifetime

---

### C211 — Retry then fault FSM

**Interview prompt:**  
On error retry up to N with delay; then FAULT; allow RESET event.

**Implement:**
```c
st_t recover_step(st_t s, ev_t e);
```

**Constraints / expectations:**
- Count retries
- Reset clears

**Follow-ups:**
- Jittered delay
- Circuit breaker link

---

### C212 — Exclusive mode manager

**Interview prompt:**  
Clients request modes; only one active; queue or reject second request.

**Implement:**
```c
int mode_request(mode_t m);
void mode_release(mode_t m);
```

**Constraints / expectations:**
- Priority optional
- Define conflict policy

**Follow-ups:**
- Preempt low mode
- Reference count shared mode

---

### C213 — Moving average

**Interview prompt:**  
Maintain average of last N samples in a ring.

**Implement:**
```c
void mav_init(mav_t *m, int *buf, size_t n);
void mav_push(mav_t *m, int sample);
int mav_get(const mav_t *m);
```

**Constraints / expectations:**
- Until filled define behavior
- Integer math

**Follow-ups:**
- Fixed-point
- Weighted

---

### C214 — EWMA / LPF (Tesla-style)

**Interview prompt:**  
Called at 10 Hz: y = 0.1*x + 0.9*y; initialize to first sample.

**Implement:**
```c
float lowPassSamples_10hz(float sample);
```

**Constraints / expectations:**
- First-call init
- No drift issues beyond float

**Follow-ups:**
- Fixed-point version
- α parameterization

---

### C215 — Binary debounce filter

**Interview prompt:**  
Require K consecutive equal samples before accepting new level.

**Implement:**
```c
int debounce_sample(int level);
```

**Constraints / expectations:**
- K configurable
- Return stable level

**Follow-ups:**
- Time-based vs count-based
- ISR usage

---

### C216 — Median of 3

**Interview prompt:**  
Return median of three readings to reject spikes.

**Implement:**
```c
int median3(int a, int b, int c);
```

**Constraints / expectations:**
- Branch-efficient OK
- Correct for duplicates

**Follow-ups:**
- Median of 5
- Sort network

---

### C217 — Slew / rate limit

**Interview prompt:**  
Limit how fast a setpoint can change per call.

**Implement:**
```c
int slew(int current, int target, int max_delta);
```

**Constraints / expectations:**
- Symmetric up/down or separate—doc
- Saturate

**Follow-ups:**
- Time-based slew
- Nonlinear

---

### C218 — PID step (fixed-point)

**Interview prompt:**  
Implement one PID iteration in Q-format without floats if possible.

**Implement:**
```c
int pid_step(pid_t *p, int setpoint, int measurement);
```

**Constraints / expectations:**
- Anti-windup basic
- Document gains format

**Follow-ups:**
- Derivative on measurement
- Feedforward

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

### C241 — Watchdog kick window

**Interview prompt:**  
Start watchdog; kick within open window; early/late kick is bad if windowed.

**Implement:**
```c
int wdt_init(uint32_t timeout_ms);
int wdt_kick(void);
```

**Constraints / expectations:**
- Document windowed vs simple
- Error if kicked wrong

**Follow-ups:**
- Task-based kicking
- External WDT pin

---

### C242 — Task heartbeat supervisor

**Interview prompt:**  
Tasks register and kick heartbeats; supervisor resets if one stalls.

**Implement:**
```c
int hb_register(unsigned id, uint32_t max_ms);
void hb_kick(unsigned id);
void hb_supervise(uint32_t now_ms);
```

**Constraints / expectations:**
- Detect stuck id
- Action: log+reset

**Follow-ups:**
- Suspend when task paused
- Priority of supervisor

---

### C243 — Stuck detection via progress counter

**Interview prompt:**  
Monitored code increments progress; checker ensures it changes.

**Implement:**
```c
void progress_tick(void);
int progress_check(uint32_t now);
```

**Constraints / expectations:**
- Timeout
- Sticky fault

**Follow-ups:**
- vs heartbeat API
- False positive when idle intentionally

---

### C244 — Brownout latch → safe mode

**Interview prompt:**  
On brownout IRQ, latch flag and enter safe outputs.

**Implement:**
```c
void brownout_isr(void);
void main_check_brownout(void);
```

**Constraints / expectations:**
- ISR minimal
- Safe GPIO state

**Follow-ups:**
- Hysteresis re-enable
- Capacitor time budget

---

### C245 — Exponential backoff retry

**Interview prompt:**  
Retry an operation with exponential backoff + optional jitter.

**Implement:**
```c
int retry_call(int (*fn)(void), unsigned max_tries);
```

**Constraints / expectations:**
- Cap max delay
- Jitter function stub

**Follow-ups:**
- Distinguish retryable errors
- Circuit breaker

---

### C246 — Circuit breaker

**Interview prompt:**  
After N consecutive failures, open circuit for cooldown; then half-open trial.

**Implement:**
```c
typedef enum { CB_CLOSED, CB_OPEN, CB_HALF } cb_st;
int cb_call(cb_t *cb, int (*fn)(void));
```

**Constraints / expectations:**
- State machine correct
- Configurable thresholds

**Follow-ups:**
- Metrics
- Per-endpoint breakers

---

### C247 — Suspend/resume peripheral context

**Interview prompt:**  
Save/restore device registers around suspend.

**Implement:**
```c
int dev_suspend(dev_t *d);
int dev_resume(dev_t *d);
```

**Constraints / expectations:**
- Idempotent
- Order of restore

**Follow-ups:**
- Runtime PM counts
- Wake IRQ

---

### C248 — Idempotent reinit after reset

**Interview prompt:**  
Device may be hard-reset; reinit must work whether first time or after crash.

**Implement:**
```c
int dev_reinit(dev_t *d);
```

**Constraints / expectations:**
- No leak of resources
- Detect already-inited

**Follow-ups:**
- Partial failure
- Soft vs hard reset

---

### C249 — Config CRC + default repair

**Interview prompt:**  
Stored config has CRC; on mismatch load defaults and flag error.

**Implement:**
```c
int config_load(cfg_t *c);
int config_save(const cfg_t *c);
```

**Constraints / expectations:**
- CRC function reuse
- Atomic save strategy simple

**Follow-ups:**
- A/B config slots
- Migration

---

### C250 — Safe-state outputs

**Interview prompt:**  
Central function forces outputs into safe mode (motors off, valves closed).

**Implement:**
```c
void enter_safe_state(void);
```

**Constraints / expectations:**
- Can call from fault path
- No alloc
- Document each pin

**Follow-ups:**
- Exit conditions
- Latched vs temporary

---

### C251 — Virtual time fake clock

**Interview prompt:**  
Provide a fake clock for unit tests that you can advance manually.

**Implement:**
```c
uint32_t fake_now_ms(void);
void fake_advance_ms(uint32_t dt);
```

**Constraints / expectations:**
- Deterministic
- Used by timers under test

**Follow-ups:**
- Simulating wrap
- Multi-thread tests

---

### C252 — Fake UART byte injector

**Interview prompt:**  
Test a parser by injecting bytes through a fake UART RX API.

**Implement:**
```c
void fake_uart_inject(const uint8_t *b, size_t n);
size_t uart_read(uint8_t *dst, size_t n); /* under test uses fake */
```

**Constraints / expectations:**
- Queue inside fake
- EOF/idle

**Follow-ups:**
- Inject errors
- Baud timing sim skip

---

### C253 — Fake MMIO with side effects

**Interview prompt:**  
Writing to CMD register sets BUSY then DONE in STATUS after advance.

**Implement:**
```c
void fake_write32(...);
void fake_tick(void); /* progress simulated HW */
```

**Constraints / expectations:**
- Enough to test driver wait_for_bit
- Deterministic

**Follow-ups:**
- Interrupt simulation
- DMA simulation

---

### C254 — Ring buffer unit tests

**Interview prompt:**  
Write tests covering empty/full/wrap/partial/overwrite policies.

**Implement:**
```c
void test_ring_wrap(void);
void test_ring_full(void);
/* run_all */
```

**Constraints / expectations:**
- Asserts clear
- No host leak

**Follow-ups:**
- Property tests
- ISR concurrency test

---

### C255 — Branch-complete validator tests (Tesla-style)

**Interview prompt:**  
Function validates pointer and data (>0, not sentinel). Write tests hitting every branch.

**Implement:**
```c
bool validatePointerAndData(int32_t *dataPtr);
bool test_validatePointerAndData(void);
```

**Constraints / expectations:**
- NULL, negative, zero, sentinel, happy
- Return false on first fail in harness OK

**Follow-ups:**
- More sentinels
- Parameterized tests

---

### C256 — Fault injection hooks

**Interview prompt:**  
Inject I2C NACK or DMA error via a test hook to exercise recovery paths.

**Implement:**
```c
void inject_i2c_nack(int enable);
void inject_dma_error(int enable);
```

**Constraints / expectations:**
- Compile-out in production
- Driver checks hooks

**Follow-ups:**
- Chaos testing
- Rate of injection

---

### C257 — Deterministic PRNG

**Interview prompt:**  
Implement a small deterministic PRNG for generating test vectors.

**Implement:**
```c
void prng_seed(uint32_t s);
uint32_t prng_u32(void);
```

**Constraints / expectations:**
- Reproducible sequence
- Document algorithm (xorshift OK)

**Follow-ups:**
- Range helper
- Shuffle

---

### C258 — CRC golden tests

**Interview prompt:**  
Assert CRC implementation against known vectors.

**Implement:**
```c
void test_crc16_vectors(void);
```

**Constraints / expectations:**
- At least 2-3 vectors
- Empty input

**Follow-ups:**
- Cross-check online tool
- Incremental update test

---

### C259 — Simulated ISR concurrency test

**Interview prompt:**  
From test code, call isr() between operations to catch races in ring/flags.

**Implement:**
```c
void test_race_flag(void);
```

**Constraints / expectations:**
- Show failing case without lock
- Passing with lock

**Follow-ups:**
- Thread sanitizer
- Model checking mention

---

### C260 — Bare-metal self-test main

**Interview prompt:**  
A main() that runs all self-tests and returns non-zero on failure (host or FW).

**Implement:**
```c
int main(void);
```

**Constraints / expectations:**
- Count pass/fail
- Print summary

**Follow-ups:**
- CI integration
- HW vs host builds

---

### C261 — RAII IRQ lock

**Interview prompt:**  
Implement a C++ RAII guard that disables IRQs in ctor and restores in dtor.

**Implement:**
```cpp
class IrqLock { public: IrqLock(); ~IrqLock(); IrqLock(const IrqLock&)=delete; /* ... */ };
```

**Constraints / expectations:**
- Nesting-safe restore
- No heap
- Rule of five lite

**Follow-ups:**
- Lock_guard mutex
- std::atomic signal

---

### C262 — Non-owning span

**Interview prompt:**  
Implement a simple Span<T> with data()/size()/subspan/bounds-checked at().

**Implement:**
```cpp
template<typename T> class Span { /* ... */ };
```

**Constraints / expectations:**
- No ownership
- Iterator optional

**Follow-ups:**
- vs std::span
- Lifetime safety

---

### C263 — Intrusive list template

**Interview prompt:**  
Intrusive doubly-linked list node mix-in and list operations.

**Implement:**
```cpp
template<typename T> struct IntrusiveNode { T* next; T* prev; };
template<typename T> class IntrusiveList { /* push/pop/erase */ };
```

**Constraints / expectations:**
- No alloc
- O(1) erase if node known

**Follow-ups:**
- Safe iteration while erase
- container_of style

---

### C264 — Static capacity ring (no heap)

**Interview prompt:**  
Template ring buffer with compile-time capacity, no dynamic allocation.

**Implement:**
```cpp
template<typename T, size_t N> class StaticRing {
 public:
  bool push(const T&); bool pop(T&);
};
```

**Constraints / expectations:**
- N power-of-two optional
- Trivial T first

**Follow-ups:**
- emplace
- ISR-safe policy

---

### C265 — function_ref without heap

**Interview prompt:**  
Non-owning callable reference for callbacks (store func ptr + obj).

**Implement:**
```cpp
template<typename Sig> class FunctionRef;
/* FunctionRef<void(int)> cb = ...; cb(3); */
```

**Constraints / expectations:**
- No alloc
- UB if referent dies—document

**Follow-ups:**
- vs std::function
- function_view

---

### C266 — unique_ptr custom deleter for DMA

**Interview prompt:**  
Manage DMA memory with unique_ptr and custom free.

**Implement:**
```cpp
struct DmaDeleter { void operator()(void* p) const; };
using DmaPtr = std::unique_ptr<uint8_t[], DmaDeleter>;
DmaPtr dma_make(size_t n);
```

**Constraints / expectations:**
- No leaks on exception if exceptions enabled—or document -fno-exceptions
- Alignment

**Follow-ups:**
- shared_ptr cache
- span from unique

---

### C267 — enum class + to_string

**Interview prompt:**  
Use enum class for modes; provide to_string and optional parse.

**Implement:**
```cpp
enum class Mode { Off, Run, Fault };
const char* to_string(Mode m);
```

**Constraints / expectations:**
- Exhaustive switch with warning
- Invalid handling

**Follow-ups:**
- std::optional parse
- Flag enums

---

### C268 — CRTP driver vs vtable

**Interview prompt:**  
Show a tiny driver interface with virtual calls and a CRTP version without vtable.

**Implement:**
```cpp
struct Uart { virtual int write(const uint8_t*, size_t)=0; virtual ~Uart()=default; };
template<typename Derived> struct UartCRTP { int write(...); };
```

**Constraints / expectations:**
- Discuss flash/RAM cost
- When vtable OK

**Follow-ups:**
- Concepts interface
- Fake for tests

---

### C269 — Move-only message queue

**Interview prompt:**  
Queue of move-only messages (e.g., unique_ptr payload).

**Implement:**
```cpp
template<typename T, size_t N> class MoveQueue {
 public:
  bool push(T&&); bool pop(T&);
};
```

**Constraints / expectations:**
- No copy of T
- Correct move on fail

**Follow-ups:**
- emplace
- ISR restrictions

---

### C270 — constexpr register encode

**Interview prompt:**  
Encode bitfields at compile time with constexpr functions.

**Implement:**
```cpp
constexpr uint32_t encode_ctrl(uint32_t div, bool en);
static_assert(encode_ctrl(3,true) == expected);
```

**Constraints / expectations:**
- No UB shifts
- Usable at compile time

**Follow-ups:**
- consteval
- Lookup tables

---

### C271 — Placement-new object pool

**Interview prompt:**  
Pool allocates objects via placement new; destroy explicitly.

**Implement:**
```cpp
template<typename T, size_t N> class ObjectPool {
 public:
  template<class...A> T* create(A&&...);
  void destroy(T*);
};
```

**Constraints / expectations:**
- Aligned storage
- No double destroy

**Follow-ups:**
- Exception safety
- Free list

---

### C272 — expected<T,E> lite

**Interview prompt:**  
Minimal success/error return without exceptions.

**Implement:**
```cpp
template<typename T, typename E> class Expected { /* ... */ };
Expected<int, Err> parse(const char*);
```

**Constraints / expectations:**
- bool conversion / has_value
- move semantics

**Follow-ups:**
- std::expected C++23
- Result monad

---

### C273 — Atomic flag handoff C++

**Interview prompt:**  
ISR sets atomic_bool with release; main loads acquire.

**Implement:**
```cpp
extern std::atomic_bool ready;
void isr();
void main_loop();
```

**Constraints / expectations:**
- Correct memory_order
- Data publication safety

**Follow-ups:**
- atomic<uint64_t>
- seq_cst tax

---

### C274 — Fix temporary lifetime callback bug

**Interview prompt:**  
Show a bug where a callback stores pointer to temporary; fix lifetimes.

**Implement:**
```cpp
void set_callback(std::function<void()> cb);
void buggy();
void fixed();
```

**Constraints / expectations:**
- Explain dangling
- Own or guarantee lifetime

**Follow-ups:**
- string_view pitfalls
- co_routines skip

---

### C275 — Header-only HAL traits

**Interview prompt:**  
Write a traits-based HAL selecting register access for real HW vs fake.

**Implement:**
```cpp
template<class Platform> struct UartHal { static void write(...); };
struct RealPlatform; struct FakePlatform;
```

**Constraints / expectations:**
- No virtual needed
- Test uses Fake

**Follow-ups:**
- Concepts constrain Platform
- Policy-based design

---

### C276 — AoS to SoA transform

**Interview prompt:**  
Convert array-of-structs samples to struct-of-arrays for processing speed.

**Implement:**
```c
typedef struct { int16_t x,y,z; } sample_t;
void aos_to_soa(const sample_t *in, size_t n, int16_t *x, int16_t *y, int16_t *z);
```

**Constraints / expectations:**
- Correctness
- Discuss cache why

**Follow-ups:**
- In-place?
- SIMD

---

### C277 — Prefetch-friendly loop

**Interview prompt:**  
Process a large buffer in a cache-friendly way; optional __builtin_prefetch.

**Implement:**
```c
uint32_t checksum(const uint8_t *b, size_t n);
```

**Constraints / expectations:**
- Sequential access
- Explain prefetch placement

**Follow-ups:**
- Blocking for L1
- Prefetch distance

---

### C278 — False sharing fix

**Interview prompt:**  
Two cores increment counters that falsely share a cache line; fix with padding/alignas.

**Implement:**
```c
struct Counters { atomic_uint a; atomic_uint b; }; /* buggy layout */
struct CountersFixed { /* padded */ };
```

**Constraints / expectations:**
- alignas(64) or pad
- Show before/after

**Follow-ups:**
- How to measure
- Destructive interference

---

### C279 — Branchless clamp

**Interview prompt:**  
Implement clamp/min/max branchlessly (or discuss when compiler does it).

**Implement:**
```c
int clamp(int x, int lo, int hi);
```

**Constraints / expectations:**
- Correct for all ints careful with overflow
- Document approach

**Follow-ups:**
- Conditional move
- SIMD select

---

### C280 — Word-wise checksum

**Interview prompt:**  
Checksum using 32-bit loads with byte tail handling.

**Implement:**
```c
uint32_t sum32(const uint8_t *b, size_t n);
```

**Constraints / expectations:**
- Alignment handling
- Endian defined

**Follow-ups:**
- Unaligned BE CPU
- IP checksum

---

### C281 — Alignment-aware copy

**Interview prompt:**  
Copy memory faster when both pointers aligned; fallback byte copy.

**Implement:**
```c
void *fast_memcpy(void *dst, const void *src, size_t n);
```

**Constraints / expectations:**
- Correct for all alignments
- Optional NEON mention

**Follow-ups:**
- memmove overlap
- Benchmark

---

### C282 — Hot/cold structure split

**Interview prompt:**  
Refactor a driver struct so rarely used fields don't pollute hot cache lines.

**Implement:**
```c
struct drv_hot { /* ... */ };
struct drv_cold { /* ... */ };
struct drv { struct drv_hot hot; struct drv_cold *cold; };
```

**Constraints / expectations:**
- Justify split
- Allocation strategy

**Follow-ups:**
- Profile-guided
- False sharing again

---

### C283 — Reduce copies in TX path

**Interview prompt:**  
Redesign API so TX can take ownership of a buffer instead of copying into driver.

**Implement:**
```c
/* old: write(const uint8_t*, n) copies */
/* new: write_buf(owned_buf_t*) zero-copy */
```

**Constraints / expectations:**
- Ownership clear
- Fallback copy API

**Follow-ups:**
- Lifetime scatterlist
- Lifetime lifetime

---

### C284 — Bit-reverse LUT vs compute

**Interview prompt:**  
Implement bit reverse with compute and LUT; discuss space/time.

**Implement:**
```c
uint8_t rev_compute(uint8_t x);
uint8_t rev_lut(uint8_t x);
```

**Constraints / expectations:**
- 256-byte table
- When LUT wins

**Follow-ups:**
- Generate LUT at compile time
- Cache pressure

---

### C285 — Ring indices cache-line placement

**Interview prompt:**  
Place producer/consumer indices on separate cache lines in shared ring.

**Implement:**
```c
struct spsc_shared { /* alignas pads */ };
```

**Constraints / expectations:**
- Explain false sharing
- Works with atomics

**Follow-ups:**
- Linux kernel ring examples
- Performance test

---

### C286 — platform_driver probe/remove

**Interview prompt:**  
Write a Linux platform_driver skeleton with probe/remove using managed resources.

**Implement:**
```c
static int my_probe(struct platform_device *pdev);
static void my_remove(struct platform_device *pdev);
/* module_platform_driver */
```

**Constraints / expectations:**
- devm_kzalloc
- Error unwind

**Follow-ups:**
- DT match table
- runtime PM stub

---

### C287 — Char device fops

**Interview prompt:**  
Implement open/read/write/release for a simple misc/char device backed by a kernel buffer.

**Implement:**
```c
static ssize_t my_read(struct file *f, char __user *buf, size_t n, loff_t *ppos);
static ssize_t my_write(struct file *f, const char __user *buf, size_t n, loff_t *ppos);
```

**Constraints / expectations:**
- copy_to_user/copy_from_user
- Bounds

**Follow-ups:**
- nonseekable
- concurrency

---

### C288 — Bounded copy_to_user path

**Interview prompt:**  
Read path must not overflow kernel buffer or userspace count.

**Implement:**
```c
ssize_t safe_read(...);
```

**Constraints / expectations:**
- min_t sizes
- return values POSIX-like

**Follow-ups:**
- partial reads
- EFAULT

---

### C289 — Versioned ioctl

**Interview prompt:**  
Define ioctl with struct that includes version; reject unsupported versions.

**Implement:**
```c
struct my_ioctl_arg { uint32_t ver; uint32_t val; };
#define MY_IOC _IOWR('m', 1, struct my_ioctl_arg)
long my_ioctl(struct file *f, unsigned cmd, unsigned long arg);
```

**Constraints / expectations:**
- copy_from_user first
- compat note optional

**Follow-ups:**
- extensible trailing data
- IOC macros

---

### C290 — poll / wait_queue data ready

**Interview prompt:**  
Implement poll that waits until data available; wake from IRQ.

**Implement:**
```c
static __poll_t my_poll(struct file *f, poll_table *wait);
void my_irq(void); /* wakes */
```

**Constraints / expectations:**
- poll_wait
- EPOLLIN when data

**Follow-ups:**
- EPOLLET edge
- fasync

---

### C291 — sysfs error counter

**Interview prompt:**  
Expose an error counter via sysfs show/store (store clears).

**Implement:**
```c
static ssize_t err_show(...);
static ssize_t err_store(...);
```

**Constraints / expectations:**
- DEVICE_ATTR
- Permissions

**Follow-ups:**
- debugfs vs sysfs
- atomic counter

---

### C292 — Threaded IRQ

**Interview prompt:**  
Request threaded IRQ: primary quick handler wakes thread handler.

**Implement:**
```c
static irqreturn_t primary(int irq, void *dev);
static irqreturn_t threaded(int irq, void *dev);
/* request_threaded_irq */
```

**Constraints / expectations:**
- IRQ_WAKE_THREAD
- No sleeping in primary

**Follow-ups:**
- oneshot
- affinity

---

### C293 — dma_alloc_coherent path

**Interview prompt:**  
Allocate coherent DMA buffer and handle failure; free on remove.

**Implement:**
```c
int alloc_dma(struct device *dev);
void free_dma(struct device *dev);
```

**Constraints / expectations:**
- dma_addr_t stored
- GFP flags

**Follow-ups:**
- streaming DMA map API
- attrs

---

### C294 — DT property parse

**Interview prompt:**  
Read a u32 frequency and optional GPIO from device tree in probe.

**Implement:**
```c
int parse_dt(struct device *dev, struct my_cfg *cfg);
```

**Constraints / expectations:**
- device_property_read_u32
- optional gpio_desc

**Follow-ups:**
- graph bindings skip
- endian in DT

---

### C295 — runtime PM suspend/resume

**Interview prompt:**  
Implement runtime suspend/resume callbacks and get/put usage in open/release.

**Implement:**
```c
static int my_runtime_suspend(struct device *dev);
static int my_runtime_resume(struct device *dev);
```

**Constraints / expectations:**
- pm_runtime_get_sync in open
- autosuspend optional

**Follow-ups:**
- system sleep vs runtime
- errors

---

### C296 — mmap kernel buffer

**Interview prompt:**  
Allow userspace to mmap a kernel buffer (vm_ops simplified / remap_pfn_range).

**Implement:**
```c
static int my_mmap(struct file *f, struct vm_area_struct *vma);
```

**Constraints / expectations:**
- Size checks
- VM_DONTEXPAND etc comments

**Follow-ups:**
- coherent DMA mmap
- cache attributes

---

### C297 — miscdevice event notify

**Interview prompt:**  
Register a miscdevice and support fasync or read-queue wakeups for events.

**Implement:**
```c
/* misc_register + fasync or wait queue */
```

**Constraints / expectations:**
- One of fasync/read OK
- Document API

**Follow-ups:**
- netlink alternative
- uevent

---

### C298 — debugfs register dump

**Interview prompt:**  
Create a debugfs file that dumps device registers when read.

**Implement:**
```c
static ssize_t regs_read(...);
/* debugfs_create_file */
```

**Constraints / expectations:**
- safe if device gone
- limit size

**Follow-ups:**
- seq_file
- access control

---

### C299 — Module param + locked state

**Interview prompt:**  
Module param sets mode; protect shared state with spinlock.

**Implement:**
```c
static int mode;
module_param(mode, int, 0644);
/* accessors with locking */
```

**Constraints / expectations:**
- sysfs param concurrency
- validate range

**Follow-ups:**
- rwlock
- percpu

---

### C300 — Fix TOCTOU on userspace length

**Interview prompt:**  
Userspace passes length then buffer; show TOCTOU bug and write the safe pattern (copy length once, clamp, then copy).

**Implement:**
```c
ssize_t buggy_write(...);
ssize_t safe_write(...);
```

**Constraints / expectations:**
- Single copy of metadata
- Clamp to kbuf

**Follow-ups:**
- get_user vs copy_from_user
- Speculative copy concerns

---

---

## Tier S — first 80 (highest MNC frequency)

C006 C013 C021 C022 C031 C036 C041 C042 C056 C057  
C071 C072 C074 C077 C087 C091 C093 C095 C101 C105  
C111 C115 C121 C122 C124 C137 C138 C145 C146 C148  
C150 C155 C164 C165 C166 C167 C173 C174 C175 C181  
C186 C187 C202 C208 C214 C219 C220 C231 C241 C245  
C251 C254 C255 C261 C264 C273 C278 C286 C288 C289  
C290 C292 C010 C014 C067 C082 C118 C134 C141 C160  
C196 C211 C226 C242 C249 C270 C283 C294  

Master these cold before grinding the rest.

---

## Progress

- Elaborated questions completed from blank: ___ / 300  
- Tier S completed: ___ / 80  
- Timed mocks: ___
