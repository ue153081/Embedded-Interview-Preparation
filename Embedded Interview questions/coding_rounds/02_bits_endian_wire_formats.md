# Bits, Endianness & Wire Formats

**IDs:** C021–C040 (20 questions)  
**Focus:** Bit ops, CRC/checksums, packing, Gray code, fixed-point.

[← Back to category index](./README.md)

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


---

[← Back to category index](./README.md)
