# Protocol Parsers & Framing

**IDs:** C186–C200 (15 questions)  
**Focus:** FSM parsers, COBS/SLIP, TLV, reassembly, ACK/retransmission.

[← Back to category index](./README.md)

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


---

[← Back to category index](./README.md)
