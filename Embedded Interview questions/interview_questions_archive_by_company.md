# Interview Questions Archive — Extracted by Company

Source: candidate/interviewer writeups archive (1point3acres-style PDF).  
Use as a **practice checklist**. Statements cleaned for clarity; original wording was noisy/OCR’d.

**Related files in this repo**
- Depth targeting: `top_mnc_embedded_interview_questions_indepth.md`
- Solved drills: `Embedded/*_solutions.md`, `google_l4_top50_full_solved_handbook.md`
- Design sheet: `Embedded/system_design_questions_only.md`

---

## How to use

1. Mark each item: `[ ]` not started · `[~]` partial · `[x]` can explain + code + 2 follow-ups  
2. Prioritize **Tier S** first (bottom of this file)  
3. Prefer implementing in C under timed conditions (45–90 min)

---

## Google — Embedded Software

### G01 — Flip monochrome bitmap in place (interviewer-authored)
**Prompt:** Given a monochrome bitmap as a flat array (1 bit/pixel), flip horizontally in place.

```c
void flip_bitmap(BYTE* bitmap, unsigned cx, unsigned cy);
```

**Probe for:** Is `cx` multiple of 8/16? Row stride? In-place constraints?  
**Skills:** nested loops, reverse bits in a byte, LUT optimization, lazy LUT init, clean helper functions (`inline reverse_bits`).  
**Follow-ups:** optimize with lookup table; trade memory for speed.

### G02 — Software timer queue on one hardware timer (interviewer-authored)
**APIs given:**
```c
void set_hw_timer(int relative_timeout_ms);   // only one HW timer pending; reset if called again
void handle_hw_timer(void);                  // ISR entry when HW timer fires
int64_t get_current_time(void);              // ms since boot
```

**Implement:**
```c
struct timer;  // caller allocates; you define fields
void set_timer(struct timer* t, int relative_timeout_ms, void (*cb)(void));
// also implement handle_hw_timer body
```

**Requirements:** many software timers; `cb` runs at interrupt level.  
**Hints:** store absolute expiry; update HW timer only when head changes.  
**Follow-ups:** protect list if IRQ fires during `set_timer`; multi-processor / spinlocks / which CPU gets IRQ.

### G03 — Non-blocking task scheduler (Pixel/home phone screen)
**Given:** `getTime()`, system calls `callNext()` each tick unit.  
**Implement:** structures + `regCall()` + `callNext()` so tasks run after timeout without blocking others.  
**Follow-ups:** complexity of reg/callNext; periodic tasks; priority tasks; interrupt-related questions.

### G04 — Integer log2 without math.h
Compute floor(log2(n)) with bit ops. Handle 0, negatives, overflow carefully.  
**Follow-up:** alternative implementations (shift left vs right); overflow checks.

### G05 — Touchscreen → SoC with clock mismatch
Touch @ ~200 MHz domain, LCD/controller slower; touch raises IRQ; API like `char read()`.  
**Design/code:** ring buffer, ISR flag, main loop consumer.  
**Follow-ups:** race conditions; mutex / critical section protection.

### G06 — memcpy with overlap
Implement `memcpy`; null checks; if ranges overlap, behave correctly (effectively `memmove`).

### G07 — BFS print by level
Standard level-order traversal / print.

### G08 — Unique + single-hill array
Array of ints: (1) all unique? (2) forms one hill (strictly increase then strictly decrease)? Many corner cases.

### G09 — R/L agents cannot cross
Two arrays same size with `_`, `R`, `L`. `R` may stay/move right; `L` stay/move left; cannot cross. Decide if input can become output.

### G10 — Device ↔ controller communication design ladder
Home-device (Echo-like) talking to controller:
1. Start with interrupts  
2. Too many IRQs / large payloads → shared memory  
3. No SHM → DMA  
4. Battery drain → sleep + wake on IRQ  
5. Cannot sleep → ASIC / companion controller offload  

### G11 — Unique paths in grid (DP)
Count paths start→end; enumerate small grids first; recursion vs memo vs DP; optimize to 1D DP (memory + register reuse).

### G12 — Two-thread lock polling concurrency
```text
Thread A: while true { print A; lock.poll(); print A; }
Thread B: while true { print B; lock.post(); }
```
Max consecutive `A`s possible? (Reason about scheduling.)

### G13 — Find rectangle in matrix
Detect whether a rectangle exists / find rectangle in a matrix (writeup incomplete; treat as classic “find rectangle formed by 1s” style).

### G14 — Virtual keyboard remote-control path
4-direction + OK (`u d l r x`). Keyboard 8 chars/row; start at `a`. Return button sequence for target string (e.g. `boy`).  
**Edge:** last row has only 2 keys — move column before row when entering last row.

### G15 — Sensor sampling system with callbacks (AR/VR onsite)
Design algorithm core + interface: sample sensors → compute state → adapt sampling frequency via callbacks.

### G16 — 5-bit RGB → 8-bit RGB
Expand each channel so 0→0 and max(31)→255; prefer bit-shift form (e.g. `(v<<3)|(v>>2)`), not naive multiply.

### G17 — Paint circle into byte framebuffer
Pointer + length + virtual width; circle center offset + radius; set bytes inside circle to 1, outside 0; handle bounds.  
**Follow-up:** if pointer is NULL, design API (e.g. allocate).

### G18 — Wheel direction from two samplers (quadrature-like)
Two sampler signals in a cyclic sequence; determine forward vs backward.  
**Follow-up:** missing/non-adjacent samples must not crash; recover / degrade gracefully.

### G19 — Mixed onsite topics (firmware track variance)
Expect mix: linked lists, HW design, Linux kernel, SW/HW testing, distributed — clarify role focus early.

---

## Apple — Embedded / Firmware

### A01 — Computer architecture + memcpy
Architecture questions, then implement `memcpy`.

### A02 — PWM-like driver
Write a PWM-similar driver from requirements/API sketch.

### A03 — Traffic lights FSM
Implement traffic-light finite state machine.

### A04 — Thermal sensor driver over I2C
Given I2C API; implement thermal sensor driver (init/read/convert/error paths).

### A05 — GPIO + debouncing
GPIO concepts + write a debounce routine.

### A06 — Hash table in C + Linux app↔driver IPC
Implement hash table in C; discuss efficient userspace↔driver communication.

### A07 — memcpy + optimize for speed
Implement then optimize (alignment, word copies, restrict, etc.).

### A08 — Same-sign ints (fastest check)
Fastest way to test whether two ints have same / opposite signs.

### A09 — Sliding window average
```c
double calculateWindowSizeAverage(int a);
```
Global window size; each call feeds one int; return average of last `WindowSize` values.  
**Follow-up:** multiple threads calling it (static/shared state).

### A10 — LC19-style linked list in full C
Not only the core function — write compilable `main`, list create, target fn, `free` (no leaks / no segfault).

### A11 — RTOS timer-based interruption
Explain/design timer-based interrupt handling under RTOS.

### A12 — C++ constructors deep dive
Types of constructors and what they actually do (not just names).

### A13 — Undefined behavior in C/C++
Concrete UB examples beyond null deref (signed overflow, strict aliasing, etc.).

### A14 — Endian size transformation
Endian conversion with size awareness.

### A15 — Pointer arithmetic pitfall
```c
char* ptr = &variable_a + n;
```
Offset scales by `sizeof(*&variable_a)` type, not always bytes — explain and avoid.

---

## Tesla — Firmware (timed C test style)

### T01 — Temperature macro
`C_TO_F` macro works for int or float: `degF = degC * (9/5) + 32` (avoid integer division bug).

### T02 — Flip MSB and LSB
```c
void flip_hi_lo(uint8_t* b);  // invert bit7 and bit0
```

### T03 — Debug broken ADC square helper
Explain bugs: wrong return width vs computation width; `volatile` ADC register read mid-expression; consistency.

### T04 — Struct from memory dump (endian)
32-bit LE system; unpack `packet_S { uint8_t count; uint16_t data[2]; uint32_t timestamp; }` at given address; also answer BE variant. Alignment/padding assumptions matter.

### T05 — Gumball vending FSM
States: `IDLE, READY, VENDING, FAULT`. Inputs: `COIN, COIN_RETURN, BUTTON, VEND_COMPLETE, GENERIC_FAULT`.  
Rules: start IDLE; invalid input no transition; `GENERIC_FAULT` → FAULT from any state; return current state.

### T06 — Unit test all branches
Write tests for validator: non-NULL, positive, non-zero, not sentinel `0x7FFFFFFF`.

### T07 — Exponential low-pass filter @ 10 Hz
EWMA: new = 0.1*sample + 0.9*prev; init to first sample; called every 100 ms.

### T08 — Circular FIFO (overwrite oldest)
Push char into length-20 circular buffer; if full, drop oldest.  
Print/empty oldest→newest.  

### T09 — ISR vs task sharing the FIFO
`bufferPush_ISR` vs `printAndEmptyBuffer` periodic task; decide where to disable/enable interrupts and why (`volatile` indices, nested IRQ).

---

## Amazon — Embedded / Lab126 / SDE-Firmware

### AM01 — Bus protocols deep dive (I2C)
Detailed I2C including timing/electrical behavior, not only API names. Be ready for SPI/UART compare.

### AM02 — Ring buffer without heap
Implement ring buffer for bytes: init/add/remove; **no dynamic allocation** (e.g. `template<size_t N>` / static array).

### AM03 — Interest / domain alignment
If asked preferred domain, answer what you can defend technically (FW vs general SDE).

---

## NVIDIA

### N01 — Fundamentals checklist (expect verbal + mini-code)
- `volatile`  
- mutex vs spinlock  
- bit manipulation  
- `memcpy` / `memmove`  
- queues  
- big vs little endian  
- stack vs heap  

---

## Qualcomm — WiFi Linux Device Driver

### Q01 — Paging / MMU / TLB
Benefits of paging; how paging supports protection; TLB / page cache concepts.

### Q02 — Spinlock vs mutex vs semaphore
Implementation differences; **which to use in interrupt handler** (typically spinlock).

### Q03 — Interrupt entry path
What CPU does on IRQ (save PC/state, stack, cache/memory considerations — discuss at sensible depth).

### Q04 — C keywords
`static`, `volatile` meanings in driver context.

---

## Microsemi — Firmware

### M01 — Recursively reverse-print a string (C)

### M02 — Arbitrary read via 32-bit-only MMIO API
API reads 32 bits at a time; implement read of any address + any size (span multiple words, alignment).

### M03 — Two devices exchanging via registers
Design/read-write protocol between two devices using registers.

---

## Autonomous Vehicle / Embedded (company unspecified)

### AV01 — State machine design
Clear states/transitions; C/C++ fluency; large-system operational flow awareness.

### AV02 — Binary / string / hex fluency
Coding emphasis on binary representation, strings, ASCII↔hex — not heavy exotic DS.

### AV03 — Culture fit
Embedded AV teams still weigh behavioral/culture.

---

## Unknown company — Embedded onsite (strong practice set)

### U01 — Multiple software timers on one HW timer
Single-thread system; tasks set alarms; implement software timers + callbacks; no lost tasks.

### U02 — Debug priority / lost high-rate timer data
Tasks: FLASH (prio 0), SPI (1), 36 kHz timer (2). Occasional data loss on 36 kHz path — debug methodology.

### U03 — Heisenbug after adding printf
Bug disappears when debug prints added — list plausible causes (timing, optimization, stack, IRQ latency, etc.).

### U04 — Count set bits in `uint8_t` + faster methods
Naive loop then Kernighan / LUT / SWAR.

---

## Tier S — practice first (from this archive)

| ID | Question | Company signal |
|----|----------|----------------|
| G02 | SW timer queue on 1 HW timer | Google |
| G05 | IRQ + ring buffer + races | Google |
| G18 | Quadrature-like direction decode | Google |
| A04 | I2C thermal sensor driver | Apple |
| A05 | GPIO debounce | Apple |
| A03 | Traffic light FSM | Apple |
| T04 | Endian struct memory dump | Tesla |
| T05 | Vending FSM | Tesla |
| T08/T09 | Circular FIFO + ISR sharing | Tesla |
| AM02 | Ring buffer no heap | Amazon |
| G06 | memcpy/memmove | Google/Apple/NVIDIA |
| G10 | IRQ→SHM→DMA→power ladder | Google |
| U01 | Multi SW timers | General FW |
| Q02 | Locks in IRQ context | Qualcomm/Linux |

---

## Suggested mapping to existing repo drills

| Archive ID | Practice with |
|------------|---------------|
| G02, U01, G03 | `Embedded/08_real_time_and_reliability_solutions.md` (timers) |
| G05, T08, T09, AM02 | `Embedded/03_circular_buffer_and_queue_solutions.md` |
| G06, A01, A07, N01 | `Embedded/09_system_mmio_ipc_and_low_level_solutions.md` + memmove drills |
| T02, G01, G16, U04 | `Embedded/02_bit_manipulation_solutions.md` |
| A03, T05, AV01 | FSM sections in driver/reliability notes |
| A04, A02 | `Embedded/07_driver_style_coding_solutions.md` |
| G10, S-design | `Embedded/system_design_questions_only.md` |
| Q01–Q04 | Linux verbal set in `top_mnc_embedded_interview_questions_indepth.md` §11 |

---

## Checkbox tracker

### Google
- [ ] G01 Bitmap flip  
- [ ] G02 Timer queue  
- [ ] G03 Scheduler regCall/callNext  
- [ ] G04 log2  
- [ ] G05 Touch IRQ ring  
- [ ] G06 memcpy/memmove  
- [ ] G07 BFS levels  
- [ ] G08 Hill array  
- [ ] G09 R/L transform  
- [ ] G10 Comm design ladder  
- [ ] G11 Unique paths DP  
- [ ] G12 Thread lock puzzle  
- [ ] G13 Rectangle  
- [ ] G14 Keyboard path  
- [ ] G15 Sensor callback system  
- [ ] G16 RGB expand  
- [ ] G17 Circle framebuffer  
- [ ] G18 Wheel/quadrature direction  

### Apple
- [ ] A01–A15 (mark individually as you go)

### Tesla
- [ ] T01–T09

### Amazon / NVIDIA / Qualcomm / Other
- [ ] AM01–AM03  
- [ ] N01  
- [ ] Q01–Q04  
- [ ] M01–M03  
- [ ] AV01–AV03  
- [ ] U01–U04  

---

**Note:** Some original writeups include incorrect candidate solutions. Treat this file as **prompts only**; verify your own implementations against your solved handbooks.
