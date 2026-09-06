#!/usr/bin/env python3
"""Generate merged-topic interview solutions (M001-M044) for FINAL_120_MERGED."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from generate_coding_solutions import all_solution_codes
from solution_enrichments import EXPANDED_STUB_CODE, beautify_c_code

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "solutions" / "FINAL_120_MERGED"

ENT_BASE = (
    "https://github.com/theEmbeddedGeorge/theEmbeddedNewTestament.github.io/blob/master/"
)

COMPANY_NAMES = {
    "G": "Google",
    "A": "Apple",
    "N": "NVIDIA",
    "T": "Tesla",
    "Z": "Amazon",
    "R": "Qualcomm",
    "Q": "Meta",
    "I": "Intel",
    "M": "Microsoft",
}


def ent_link(title: str, path: str) -> str:
    return f"- [{title}]({ENT_BASE}{path})"


def format_companies(codes: str) -> str:
    parts = [COMPANY_NAMES.get(c, c) for c in codes.split()]
    return " · ".join(parts)


def fmt_qs(qs: list[str]) -> str:
    return ", ".join(qs)


# ---------------------------------------------------------------------------
# M006 — full ring buffer (Q016-Q021 merged)
# ---------------------------------------------------------------------------

M006_RING_CODE = r"""#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>

/* --- Spare-slot SPSC ring (Q016) --- */
typedef struct {
    uint8_t *buf;
    uint32_t cap;
    uint32_t head;
    uint32_t tail;
    uint32_t drops;
} ring_t;

static inline uint32_t ring_next_mod(const ring_t *r, uint32_t idx) {
    return (idx + 1u) % r->cap;
}

static inline uint32_t ring_next_mask(const ring_t *r, uint32_t idx) {
    return (idx + 1u) & (r->cap - 1u);
}

static inline int ring_is_pow2(uint32_t cap) {
    return cap >= 2u && (cap & (cap - 1u)) == 0u;
}

static inline uint32_t ring_next(const ring_t *r, uint32_t idx) {
    return ring_is_pow2(r->cap) ? ring_next_mask(r, idx) : ring_next_mod(r, idx);
}

int ring_init(ring_t *r, uint8_t *buf, uint32_t cap) {
    if (!r || !buf || cap < 2u) {
        return -1;
    }
    r->buf = buf;
    r->cap = cap;
    r->head = 0u;
    r->tail = 0u;
    r->drops = 0u;
    return 0;
}

int ring_is_empty(const ring_t *r) {
    return r->head == r->tail;
}

int ring_is_full(const ring_t *r) {
    return ring_next(r, r->head) == r->tail;
}

uint32_t ring_count(const ring_t *r) {
    if (r->head >= r->tail) {
        return r->head - r->tail;
    }
    return r->cap - r->tail + r->head;
}

uint32_t ring_free_space(const ring_t *r) {
    return (r->cap - 1u) - ring_count(r);
}

int ring_push(ring_t *r, uint8_t byte) {
    uint32_t next = ring_next(r, r->head);
    if (next == r->tail) {
        r->drops++;
        return -1;
    }
    r->buf[r->head] = byte;
    r->head = next;
    return 0;
}

size_t ring_push_n(ring_t *r, const uint8_t *src, size_t n) {
    size_t pushed = 0;
    while (pushed < n && ring_push(r, src[pushed]) == 0) {
        pushed++;
    }
    return pushed;
}

int ring_pop(ring_t *r, uint8_t *byte) {
    if (r->head == r->tail) {
        return -1;
    }
    *byte = r->buf[r->tail];
    r->tail = ring_next(r, r->tail);
    return 0;
}

size_t ring_pop_n(ring_t *r, uint8_t *dst, size_t n) {
    size_t popped = 0;
    while (popped < n && ring_pop(r, &dst[popped]) == 0) {
        popped++;
    }
    return popped;
}

size_t ring_peek_n(const ring_t *r, uint8_t *dst, size_t n) {
    size_t i = 0;
    uint32_t t = r->tail;
    while (i < n && t != r->head) {
        dst[i++] = r->buf[t];
        t = ring_next(r, t);
    }
    return i;
}

/* Q018 — overwrite-oldest on full */
int ring_push_overwrite(ring_t *r, uint8_t byte) {
    uint32_t next = ring_next(r, r->head);
    if (next == r->tail) {
        r->tail = ring_next(r, r->tail);
        r->drops++;
    }
    r->buf[r->head] = byte;
    r->head = next;
    return 0;
}

/* Q021 — DMA-friendly contiguous read span */
size_t ring_contig_read(const ring_t *r, const uint8_t **ptr) {
    if (r->tail == r->head) {
        *ptr = NULL;
        return 0;
    }
    *ptr = &r->buf[r->tail];
    if (r->head > r->tail) {
        return r->head - r->tail;
    }
    return r->cap - r->tail;
}

void ring_consume(ring_t *r, size_t n) {
    while (n-- > 0 && r->tail != r->head) {
        r->tail = ring_next(r, r->tail);
    }
}

/* Q020 — SMP SPSC with acquire/release atomics */
typedef struct {
    uint8_t *buf;
    uint32_t cap;
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
} ring_atomic_t;

int ring_atomic_init(ring_atomic_t *r, uint8_t *buf, uint32_t cap) {
    if (!r || !buf || cap < 2u) {
        return -1;
    }
    r->buf = buf;
    r->cap = cap;
    atomic_store_explicit(&r->head, 0u, memory_order_relaxed);
    atomic_store_explicit(&r->tail, 0u, memory_order_relaxed);
    return 0;
}

int ring_atomic_push(ring_atomic_t *r, uint8_t byte) {
    uint32_t h = atomic_load_explicit(&r->head, memory_order_relaxed);
    uint32_t next = ring_is_pow2(r->cap) ? ((h + 1u) & (r->cap - 1u))
                                         : ((h + 1u) % r->cap);
    uint32_t t = atomic_load_explicit(&r->tail, memory_order_acquire);
    if (next == t) {
        return -1;
    }
    r->buf[h] = byte;
    atomic_store_explicit(&r->head, next, memory_order_release);
    return 0;
}

int ring_atomic_pop(ring_atomic_t *r, uint8_t *byte) {
    uint32_t t = atomic_load_explicit(&r->tail, memory_order_relaxed);
    uint32_t h = atomic_load_explicit(&r->head, memory_order_acquire);
    if (t == h) {
        return -1;
    }
    *byte = r->buf[t];
    uint32_t next = ring_is_pow2(r->cap) ? ((t + 1u) & (r->cap - 1u))
                                         : ((t + 1u) % r->cap);
    atomic_store_explicit(&r->tail, next, memory_order_release);
    return 0;
}"""


def combine_codes(*parts: str) -> str:
    return "\n\n/* --- next section --- */\n\n".join(p.strip() for p in parts if p.strip())


def build_c_codes() -> dict[str, str]:
    codes = all_solution_codes()
    expanded = dict(EXPANDED_STUB_CODE)
    return {
        "M001": combine_codes(codes["C041"], codes["C042"], codes["C043"]),
        "M002": r"""#include <stdint.h>
#include <stddef.h>
#include <limits.h>
""" + codes["C048"] + "\n\n" + r"""
typedef enum { ATOI_OK = 0, ATOI_NULL = -1, ATOI_EMPTY = -2, ATOI_OVERFLOW = -3, ATOI_INVALID = -4 } atoi_err_t;

static int skip_ws(const char **s) {
    while (**s == ' ' || **s == '\t' || **s == '\n') {
        (*s)++;
    }
    return 0;
}

atoi_err_t safe_atoi(const char *s, int *out) {
    if (!s || !out) return ATOI_NULL;
    skip_ws(&s);
    if (!*s) return ATOI_EMPTY;
    int sign = 1;
    if (*s == '-') { sign = -1; s++; }
    else if (*s == '+') { s++; }
    if (*s < '0' || *s > '9') return ATOI_INVALID;
    long v = 0;
    while (*s >= '0' && *s <= '9') {
        v = v * 10 + (*s - '0');
        if ((sign == 1 && v > INT32_MAX) || (sign == -1 && v > (long)INT32_MAX + 1)) {
            return ATOI_OVERFLOW;
        }
        s++;
    }
    *out = (int)(sign * v);
    return ATOI_OK;
}""",
        "M003": combine_codes(codes["C005"], codes["C006"], codes["C012"], codes["C031"]),
        "M004": combine_codes(codes["C021"], codes["C022"], codes["C023"], codes["C037"], codes["C040"]),
        "M005": combine_codes(codes["C027"], codes["C028"]),
        "M006": M006_RING_CODE,
        "M007": combine_codes(codes["C075"], codes["C079"], codes["C081"], codes["C082"], codes["C099"]),
        "M008": combine_codes(codes["C056"], codes["C057"], codes["C059"], codes["C060"]),
        "M009": combine_codes(codes["C091"], codes["C092"], codes["C094"], codes["C096"], codes["C098"]),
        "M010": combine_codes(codes["C100"], codes["C101"], codes["C102"]),
        "M011": codes.get("C121", codes["C005"]) + "\n" + r"""
typedef volatile struct { volatile uint32_t SR; volatile uint32_t DR; } uart_regs_t;

static inline uint32_t read32(volatile uint32_t *reg) { return *reg; }
static inline void write32(volatile uint32_t *reg, uint32_t val) { *reg = val; }
static inline void rmw32(volatile uint32_t *reg, uint32_t mask, uint32_t val) {
    uint32_t v = read32(reg);
    v = (v & ~mask) | (val & mask);
    write32(reg, v);
}

int poll_flag(volatile uint32_t *sr, uint32_t mask, int want_set, uint32_t timeout_ms) {
    while (((read32(sr) & mask) != 0) != want_set) {
        if (timeout_ms-- == 0) return -1;
    }
    return 0;
}""",
        "M012": combine_codes(codes.get("C136", ""), codes.get("C137", ""), codes["C139"]),
        "M013": codes.get("C141", codes["C005"]) + codes.get("C142", ""),
        "M014": codes["C145"],
        "M015": combine_codes(expanded.get("C184", ""), codes.get("C155", "")),
        "M016": combine_codes(codes.get("C241", ""), expanded.get("C182", "")),
        "M017": codes.get("C186", codes["C004"]),
        "M018": combine_codes(
            expanded["C173"], expanded["C174"], expanded["C175"],
            expanded["C177"], expanded["C181"],
        ),
        "M019": codes.get("C242", "") + codes.get("C243", codes["C202"]),
        "M020": codes["C202"],
        "M021": codes.get("C213", r"""
#include <stdint.h>
typedef struct { int32_t alpha_q16; int32_t y_q16; uint8_t init; } ewma_t;
void ewma_init(ewma_t *f, int32_t alpha_q16) { f->alpha_q16 = alpha_q16; f->y_q16 = 0; f->init = 0; }
int32_t ewma_update(ewma_t *f, int32_t x_q16) {
    if (!f->init) { f->y_q16 = x_q16; f->init = 1; return f->y_q16; }
    int64_t diff = (int64_t)x_q16 - f->y_q16;
    f->y_q16 += (int32_t)((diff * f->alpha_q16) >> 16);
    return f->y_q16;
}"""),
        "M022": codes.get("C251", r"""
#include <stdint.h>
#include <stddef.h>
typedef struct { uintptr_t lo, hi; } range_t;
int range_valid(const range_t *r, uintptr_t p) {
    return r && p >= r->lo && p < r->hi;
}
int range_self_test(void) {
    range_t r = { .lo = 0x20000000u, .hi = 0x20001000u };
    return range_valid(&r, 0x20000500u) && !range_valid(&r, 0x30000000u);
}"""),
        "M023": codes["C001"],
    }


def _t(
    mid: str,
    title: str,
    slug: str,
    typ: str,
    companies: str,
    merged: list[str],
    prep: str,
    variants: list[str],
    study: list[tuple[str, str]],
    tier: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    d: dict[str, Any] = {
        "id": mid,
        "title": title,
        "slug": slug,
        "type": typ,
        "companies": companies,
        "merged_from": merged,
        "prep_question": prep,
        "sub_variants": variants,
        "further_study": study,
    }
    if tier:
        d["tier"] = tier
    d.update(extra)
    return d


TOPICS: dict[str, dict[str, Any]] = {
    "M001": _t(
        "M001", "Memory byte operations (memcpy / memmove / memset / secure wipe)",
        "memory_byte_ops", "C", "G A N T", ["Q001", "Q002"],
        "Implement overlap-safe memmove, optimized memcpy (alignment paths), and memset; explain secure zeroization.",
        ["NULL / zero-length semantics", "Overlapping regions (memmove direction)",
         "Word-aligned fast path vs byte tail", "volatile/memset_s for secrets"],
        [("Memory Management", "Embedded_C/Memory_Management.md"),
         ("Structure Alignment", "Embedded_C/Structure_Alignment.md")],
        tier="S",
        clarifying=[
            "May source and destination overlap? I'll implement memmove with direction choice.",
            "Alignment assumptions — I'll add word-aligned fast path when both pointers align.",
            "For secrets, should I use volatile wipe or memset_s-style API?",
        ],
        followups=[
            ("Why is memcpy UB on overlap?", "memcpy assumes non-overlapping regions; memmove handles forward/backward copy based on address order."),
            ("When does the compiler elide memset?", "When it proves the buffer is dead before any secret use; for crypto keys use explicit_bzero or volatile loop."),
        ],
    ),
    "M002": _t(
        "M002", "Safe string / integer parsing", "safe_atoi", "C", "G A", ["Q003"],
        "Implement safe atoi with overflow detection, invalid input handling, and clear return codes.",
        ["Leading whitespace", "Sign handling", "Partial parse", "INT_MAX boundary"],
        [("atoi implementation", "Data_Struct_Implementation/atoi/README.md")],
        clarifying=["Return code enum or negative errno style?", "Should I consume trailing non-digits or report invalid?"],
        followups=[("How handle INT_MIN?", "Special-case overflow when sign is negative and magnitude exceeds INT_MAX+1.")],
    ),
    "M003": _t(
        "M003", "Endianness, wire layout & struct unpacking", "endian_wire_struct", "C",
        "G A N T I", ["Q004", "Q010", "Q014"],
        "Endian helpers, bitfield unpack from wire frame, LE struct parse with padding awareness.",
        ["#pragma pack vs shift/mask", "Unaligned access", "Portable serialization"],
        [("Endianness", "Data_Struct_Implementation/endianess/README.md"),
         ("Protocol Implementation", "Communication_Protocols/Protocol_Implementation.md")],
        tier="S",
        clarifying=["Wire format big-endian or little-endian?", "May I cast packed struct pointers or use byte walks?"],
        followups=[("Why not cast buffer to struct?", "Alignment and padding differ across compilers; explicit unpack is portable.")],
    ),
    "M004": _t(
        "M004", "Bit manipulation toolkit", "bit_manipulation", "C", "G A T N", ["Q005", "Q006", "Q007", "Q008", "Q009", "Q013"],
        "Popcount, reverse bits, flip MSB/LSB, is_pow2/next_pow2, floor_log2, RGB expand.",
        ["SWAR popcount", "Lazy LUT init", "Edge cases n=0"],
        [("Bit Manipulation", "Embedded_C/Bit_Manipulation.md"),
         ("countBitsLookUpTable", "Data_Struct_Implementation/BitsManipulation/countBitsLookUpTable.md")],
        tier="S",
        clarifying=["32-bit or 64-bit width for log2?", "RGB 5-bit per channel expand to 8-bit?"],
        followups=[("Kernighan vs LUT popcount?", "Kernighan is O(set bits); LUT is O(1) with 256-byte table — trade cache for speed.")],
    ),
    "M005": _t(
        "M005", "CRC & checksums", "crc_checksums", "C", "G T I", ["Q011", "Q012"],
        "Implement CRC-8 and CRC-16 (bitwise + optional table); same API shape for both widths.",
        ["init/xorout/refin/refout", "Table-driven speedup", "Parser integration"],
        [("Error Detection", "Communication_Protocols/Error_Detection.md")],
        clarifying=["Polynomial and init value for CRC-16?", "Bitwise OK or table required?"],
        followups=[("When CRC vs checksum?", "CRC catches bursty bit errors; XOR sum only catches odd numbers of flipped bits in a byte.")],
    ),
    "M006": _t(
        "M006", "Ring buffers & SPSC queues (complete)", "ring_buffers_SPSC_complete", "C",
        "G A Z T N", ["Q016", "Q017", "Q018", "Q019", "Q020", "Q021"],
        "Byte ring with init/push/pop; spare-slot full/empty, pow2 mask, overwrite-oldest, ISR/task, lock-free SPSC, DMA contiguous read.",
        ["Q016: spare-slot ring init/push/pop", "Q017: power-of-2 mask indexing",
         "Q018: overwrite-oldest policy", "Q019: ISR producer / task consumer + drops",
         "Q020: lock-free SPSC acquire/release", "Q021: DMA contiguous read API"],
        [("Circular Ring Buffers", "Data_Struct_Implementation/circularRingBuffer/README.md"),
         ("UART Protocol", "Communication_Protocols/UART_Protocol.md")],
        tier="S",
        clarifying=[
            "Capacity cap — usable bytes with one spare slot?",
            "ISR producer / task consumer?",
            "On full: reject, block, or overwrite oldest?",
            "Need push_n/pop_n and DMA contiguous read API?",
        ],
        followups=[
            ("Why spare slot?", "Distinguish full vs empty with only head/tail — loses one byte of capacity."),
            ("Power-of-two size?", "Enables mask indexing instead of modulo — faster on CPUs without fast divide."),
            ("Overwrite-oldest?", "Advance tail then write — drops oldest telemetry; bad for command streams."),
            ("SMP variant?", "Acquire/release on opposite index before checking occupancy."),
            ("DMA read?", "Return pointer to contiguous span from tail to head or buffer end; wrap needs two segments."),
        ],
    ),
    "M007": _t(
        "M007", "IPC, mailboxes & lock-free handoff", "ipc_mailboxes", "C",
        "G A Z T N R", ["Q022", "Q023", "Q024", "Q025", "Q026", "Q027", "Q028"],
        "Logging ring, priority event queue, dual-core mailbox, zero-copy buffer transfer, sequence-lock stats, ISR flag, bounded producer-consumer.",
        ["Backpressure", "Generation counters", "Cache-line alignment", "irq_save vs atomics"],
        [("Shared Memory Programming", "Embedded_C/Shared_Memory_Programming.md"),
         ("Bounded Queue", "Data_Struct_Implementation/concurrency/BoundedQueue.md")],
        clarifying=["SPSC or MPSC logging?", "Shared SRAM cache-coherent or explicit flush?"],
        followups=[("Mailbox ordering?", "Payload visible before doorbell IRQ; use release store then trigger interrupt.")],
    ),
    "M008": _t(
        "M008", "Memory allocators (pools → heap → special)", "memory_allocators", "C",
        "G A T N R", ["Q029", "Q030", "Q031", "Q032", "Q033", "Q034", "Q035", "Q036"],
        "Fixed-size pool O(1), ISR-safe pool, guard/poison stats; variable freelist; buddy sketch; DMA-aligned and bump allocators.",
        ["Fragmentation", "TLSF mention", "Handle indirection", "Double-free detection"],
        [("Memory Pool Allocation", "Embedded_C/Memory_Pool_Allocation.md"),
         ("Memory Fragmentation", "Embedded_C/Memory_Fragmentation.md")],
        tier="S",
        clarifying=["Alloc from ISR allowed?", "Fixed block size or variable heap?"],
        followups=[("Pool vs heap for RT?", "Pool is O(1) deterministic; heap may fragment and invoke malloc latency spikes.")],
    ),
    "M009": _t(
        "M009", "Locks, semaphores & reader–writer", "locks_semaphores_rw", "C",
        "G A N Q Z T", ["Q037", "Q038", "Q039", "Q040", "Q041"],
        "Spinlock, ticket lock, mutex, counting/binary semaphore (ISR-safe give), reader-writer lock.",
        ["Starvation", "ISR vs task legality", "Priority inversion context"],
        [("Kernel Services", "Real_Time_Systems/Kernel_Services.md"),
         ("Reader Writer", "Data_Struct_Implementation/concurrency/ReaderWritter.md")],
        clarifying=["Single-core UP or SMP?", "Can this lock be taken from ISR?"],
        followups=[("Spinlock vs mutex?", "Spinlock for short ISR/task sections; mutex sleeps — never in ISR.")],
    ),
    "M010": _t(
        "M010", "Atomics, memory order & cache effects", "atomics_memory_order", "C",
        "G A N R", ["Q042", "Q043", "Q044", "Q045"],
        "Overflow-safe atomic counters; ABA on lock-free stack; acquire/release flag repair; false-sharing padding.",
        ["ABA tagged pointers", "memory_order_acquire/release", "Cache-line alignment"],
        [("Memory Ordering", "Computer_architecture/Memory_Ordering.md"),
         ("Multi-core Systems", "Computer_architecture/Multi_core_Systems.md")],
        tier="S",
        clarifying=["C11 atomics available?", "SMP or single-core with IRQ preemption?"],
        followups=[("ABA fix?", "Tagged pointers or epoch reclamation; Treiber stack unsafe without it.")],
    ),
    "M011": _t(
        "M011", "MMIO register HAL & timed polling", "mmio_hal_polling", "C",
        "G A N T R", ["Q046", "Q047"],
        "read32/write32/rmw with MMIO semantics; bitfield helpers; poll-with-timeout; volatile limits.",
        ["Posted writes", "Readback hazards", "Timeout units"],
        [("Memory-Mapped I/O", "Embedded_C/Memory-Mapped_I_O.md")],
        tier="S",
        clarifying=["Register base address provided?", "Timeout in cycles or milliseconds?"],
        followups=[("volatile enough for MMIO?", "volatile prevents CSE but not ordering; use barriers for publish sequences.")],
    ),
    "M012": _t(
        "M012", "UART driver (poll → IRQ → DMA)", "uart_driver_stack", "C",
        "G A Z T N", ["Q048", "Q049", "Q050"],
        "Polling TX/RX, IRQ-driven with rings and backpressure, optional circular DMA RX/TX; unified state machine.",
        ["Flush", "Error flags", "RTS/CTS", "Drop policy on full ring"],
        [("UART Protocol", "Communication_Protocols/UART_Protocol.md"),
         ("UART Configuration", "Communication_Protocols/UART_Configuration.md")],
        tier="S",
        clarifying=["FIFO depth and baud rate?", "Blocking API or callback on TX complete?"],
        followups=[("When DMA vs IRQ?", "DMA for high throughput bulk; IRQ fine for moderate byte rates and simpler bring-up.")],
    ),
    "M013": _t(
        "M013", "SPI driver (blocking → IRQ/DMA)", "spi_driver", "C", "A N", ["Q051", "Q052"],
        "Blocking full-duplex transfer; IRQ/DMA state machine with CS management.",
        ["CS per device", "Mode 0-3", "DMA scatter"],
        [("SPI Protocol", "Communication_Protocols/SPI_Protocol.md")],
        clarifying=["Single slave or multi-CS bus?", "Full-duplex always or TX-only phases?"],
        followups=[("CS timing?", "Assert CS before clocks; deassert after last bit shifted out.")],
    ),
    "M014": _t(
        "M014", "I2C master (transfer + recovery)", "i2c_master_recovery", "C",
        "A Z T", ["Q053", "Q054"],
        "Write, read, repeated-start write+read; NACK/timeout; stuck-bus recovery.",
        ["Clock stretch timeout", "9-pulse recovery", "STOP generation"],
        [("I2C Protocol", "Communication_Protocols/I2C_Protocol.md"),
         ("i2c bus", "Bus_Protocol/i2c.md")],
        tier="S",
        clarifying=["7-bit or 10-bit addressing?", "Clock stretch max before recovery?"],
        followups=[("Bus recovery?", "Toggle SCL up to 9 times while SDA high, then STOP.")],
    ),
    "M015": _t(
        "M015", "GPIO, debounce, PWM, ADC & sensor wrapper", "gpio_debounce_pwm_adc", "C",
        "A T", ["Q055", "Q056", "Q057", "Q058"],
        "GPIO read/write/toggle + interrupt debounce; PWM period/duty; ADC single-shot; thin sensor driver on I2C.",
        ["volatile ADC pitfalls", "Thermal read retry", "Symmetric debounce"],
        [("GPIO Configuration", "HW_Module/GPIO_Configuration.md"),
         ("Analog I/O", "HW_Module/Analog_I_O.md")],
        tier="S",
        clarifying=["Debounce in ISR or timer callback?", "ADC blocking with timeout?"],
        followups=[("Debounce approach?", "Restart timer on each edge; fire after quiet period — separate press/release if needed.")],
    ),
    "M016": _t(
        "M016", "Watchdog & deadline monitoring", "watchdog_deadline", "C",
        "A T Z N I", ["Q059", "Q065"],
        "Watchdog init/kick policy; windowed WDT sketch; deadline-miss counter; schedulability check.",
        ["Who kicks WDT", "WCET sum ≤ period", "Miss handling"],
        [("Watchdog Timers", "HW_Module/Watchdog_Timers.md"),
         ("Response Time Analysis", "Real_Time_Systems/Response_Time_Analysis.md")],
        clarifying=["Windowed or simple countdown WDT?", "Single supervisor task kicks?"],
        followups=[("Pet from ISR?", "No — pet only after all critical loops ran in supervised task.")],
    ),
    "M017": _t(
        "M017", "Protocol stream parser (framing + CRC + resync)", "protocol_parser", "C",
        "G T I", ["Q060"],
        "Byte-stream FSM: length field, CRC validate, resync on corruption; NEED_MORE / OK / RESYNC.",
        ["Magic sync byte", "Bounded resync scan", "Partial frames"],
        [("Protocol Implementation", "Communication_Protocols/Protocol_Implementation.md"),
         ("Error Detection", "Communication_Protocols/Error_Detection.md")],
        tier="S",
        clarifying=["Fixed or length-prefix frames?", "CRC width and polynomial?"],
        followups=[("Resync strategy?", "Hunt for magic byte; cap scan length to bound CPU in noise.")],
    ),
    "M018": _t(
        "M018", "Software timers & tick dispatch", "software_timers", "C",
        "G A T", ["Q061", "Q062", "Q063", "Q064"],
        "SW timers on one HW timer; periodic + wrap-safe compares; sorted list / min-heap / timer wheel; regCall/callNext dispatcher.",
        ["Drift-free periodic", "cancel_sync race", "Tickless sleep"],
        [("Timer Wheel", "Data_Struct_Implementation/timerWheel/README.md"),
         ("Timer/Counter Programming", "HW_Module/Timer_Counter_Programming.md")],
        tier="S",
        clarifying=["Callback in ISR or deferred worker?", "Max timer count N?"],
        followups=[("List vs heap vs wheel?", "List <16 timers; heap 16–500; wheel for many coarse timeouts.")],
    ),
    "M019": _t(
        "M019", "Reliability patterns (backoff, fault FSM)", "reliability_backoff_fsm", "C",
        "G A Z T I", ["Q066", "Q067"],
        "Exponential backoff for driver retries; fault-tolerant peripheral FSM idle/active/error/recover.",
        ["Jitter on backoff", "Max retry cap", "Explicit recover transitions"],
        [("Error Handling and Logging", "System_Integration/Error_Handling_and_Logging.md")],
        clarifying=["Backoff base and max delay?", "Auto-recover or manual reset?"],
        followups=[("Why jitter?", "Prevents thundering herd when many devices retry simultaneously.")],
    ),
    "M020": _t(
        "M020", "Classic FSM coding", "classic_fsm", "C", "A T", ["Q068"],
        "Traffic-light or vending-machine FSM; invalid inputs ignored or counted; table vs switch.",
        ["GENERIC_FAULT from every state", "Entry/exit actions", "Invalid event policy"],
        [("State Machines", "Data_Struct_Implementation/stateMachine/README.md")],
        tier="S",
        clarifying=["Table-driven or switch acceptable?", "Count invalid inputs for diagnostics?"],
        followups=[("Table vs switch?", "Table scales for many states; switch is fine for <6 states in interviews.")],
    ),
    "M021": _t(
        "M021", "Filters & signal-lite numeric", "filters_ewma", "C", "T", ["Q069"],
        "EWMA / first-order low-pass; init on first sample; fixed-point variant mention.",
        ["Q16.16 fixed point", "Saturate on overflow", "First-sample init"],
        [("Analog I/O", "HW_Module/Analog_I_O.md")],
        clarifying=["Float OK or fixed-point required?", "Alpha as Q16 fraction?"],
        followups=[("Why init on first sample?", "Avoids slow ramp from zero that biases early readings.")],
    ),
    "M022": _t(
        "M022", "Embedded unit-test harness", "unit_test_harness", "C", "T G", ["Q070"],
        "Branch-complete tests for pointer/range validator; fake HAL; fault injection hooks.",
        ["Table-driven tests", "Fake MMIO", "Fault inject timeouts"],
        [("Unit Testing for Embedded", "Debugging/Unit_Testing_for_Embedded.md")],
        clarifying=["Host compile with gcc OK?", "Need coverage of all branches?"],
        followups=[("Fake HAL pattern?", "Function pointers for register access; record call order in tests.")],
    ),
    "M023": _t(
        "M023", "C macros & intrusive structures", "macros_intrusive_list", "C",
        "G Q R", ["Q015"],
        "container_of, offsetof, intrusive doubly-linked list node usage.",
        ["Type-safe macros", "List insert/remove", "No hidden allocations"],
        [("C Language Fundamentals", "Embedded_C/C_Language_Fundamentals.md")],
        clarifying=["Linux kernel style container_of OK?", "Singly or doubly linked?"],
        followups=[("Why intrusive lists?", "Zero extra allocation; nodes embed in parent structs — cache-friendly for embedded.")],
    ),
}

# Verbal topics M026-M036
TOPICS.update({
    "M026": _t(
        "M026", "Memory model: volatile, atomics, barriers, MMIO, UB", "memory_model_verbal", "V",
        "G A N T R Q", ["Q071", "Q078", "Q083", "Q084"],
        "When is volatile required vs wrong? Atomics/barriers vs volatile; MMIO hazards; UB examples; pointer rules.",
        ["volatile for MMIO only", "atomics for cross-thread", "five UB examples"],
        [("Type Qualifiers", "Embedded_C/Type_Qualifiers.md"),
         ("Memory Ordering", "Computer_architecture/Memory_Ordering.md")],
        tier="S",
        interviewer_wants="Proof you won't ship heisenbugs from wrong memory semantics.",
        core=[
            "`volatile` — hardware register reads, ISR flag visibility; NOT a lock substitute.",
            "Atomics + memory_order — publish/consume between cores or ISR/task without mutex.",
            "Barriers (DMB/DSB/ISB) — ordering around DMA and self-modifying code.",
            "MMIO — every access is a side effect; posted writes may need readback.",
            "UB examples: null deref, signed overflow, strict-aliasing violation, use-after-free, data race.",
        ],
        traps=["Using volatile for thread synchronization", "Casting unrelated pointer types", "Assuming memset clears secrets"],
        followups_v=[
            ("When is volatile wrong?", "For mutex-protected data or when atomics already provide ordering."),
            ("MMIO readback?", "After critical config writes to ensure they reached the peripheral."),
            ("Strict aliasing?", "Reading float bits through uint32_t* without memcpy/union is UB in C."),
        ],
        script_60="Volatile is for hardware and signal-like memory — it stops the compiler from caching or eliding loads. For cross-context data sharing I use atomics with acquire and release, or a lock. MMIO needs volatile pointers plus barriers when ordering matters with DMA. UB I'd watch for: races, aliasing, overflow, lifetime bugs, and ISR/task sharing without protection.",
        ti_story="On PRU/R5F split we used volatile only for MMIO doorbells; cross-core counters used C11 atomics — volatile on shared stats caused lost updates under optimization.",
    ),
    "M027": _t(
        "M027", "Interrupt architecture (ISR rules, deferral, threaded IRQ)", "interrupt_architecture", "V",
        "G A T N Q Z", ["Q072", "Q073", "Q095"],
        "Illegal ISR operations; top-half vs bottom-half; threaded IRQ for GPIO encoder edges.",
        ["ISR latency budget", "Deferral mechanisms", "Hard vs threaded IRQ tradeoff"],
        [("External Interrupts", "HW_Module/External_Interrupts.md"),
         ("Interrupt Handling", "Real_Time_Systems/Interrupt_Handling.md")],
        tier="S",
        interviewer_wants="You keep ISRs short and know how to defer without losing events.",
        core=["ISR: no malloc, printf, blocking, long loops", "Defer via flag, ring buffer, or workqueue",
              "Threaded IRQ: top half acks hardware; bottom half can sleep (I2C/SPI)",
              "GPIO encoder: hard IRQ for timestamp; threaded for debounce/filter"],
        traps=["Heavy parsing in ISR", "Mutex in ISR", "Missing irq_save around shared list edits"],
        followups_v=[("GPIO encoder edges?", "Hard IRQ captures timestamp; threaded handler debounces and computes delta."),
                     ("Lost interrupts?", "Check NVIC priority, clear flags early, ring overflow policy.")],
        script_60="ISRs do the minimum: clear hardware, enqueue data, wake a task. Anything that blocks or takes milliseconds belongs in a bottom half — workqueue or threaded IRQ. For a fast encoder I capture edges in hard IRQ for jitter, then process position in a thread where I can use I2C if needed.",
        ti_story="EnDAT position ISR only latched timer and pushed to ring; frame parse ran on R5F — kept ISR under 2 µs.",
    ),
    "M028": _t(
        "M028", "Synchronization choice & failure modes", "sync_choice_failure", "V",
        "G A N Q Z T", ["Q074", "Q075", "Q076", "Q089"],
        "Mutex vs spinlock vs semaphore; priority inversion; deadlock; debug lost timer data.",
        ["Priority inheritance/ceiling", "Four deadlock conditions", "irq_save vs atomics"],
        [("Priority Inversion Prevention", "Real_Time_Systems/Priority_Inversion_Prevention.md"),
         ("Deadlock Avoidance", "Real_Time_Systems/Deadlock_Avoidance.md")],
        tier="S",
        interviewer_wants="You pick the right primitive and can debug real failures.",
        core=["Spinlock: ISR + short task sections", "Mutex: task-only, can sleep",
              "Semaphore: signaling + resource counting; ISR can give, not take blocking",
              "Priority inversion: high blocked on low holding mutex — fix with inheritance/ceiling",
              "Deadlock: mutual exclusion + hold-and-wait + no preemption + circular wait"],
        traps=["Mutex in ISR", "Spinlock across blocking call", "Unbounded priority inheritance chains"],
        followups_v=[("Debug lost timer data?", "Check ring overflow, priority inversion starving consumer, missing irq_save."),
                     ("When semaphore vs mutex?", "Semaphore for counting resources or ISR-to-task signal; mutex for exclusive ownership.")],
        script_60="In ISR I use spinlocks or lock-free rings — never mutex. In tasks, mutex for exclusive sections that may block. Priority inversion happens when a low task holds a mutex a high task needs — I use priority inheritance or ceiling. Deadlock needs all four conditions; I break hold-and-wait by lock ordering.",
        ti_story="Host poll starvation on UART ring looked like lost bytes — was priority inversion; raised parser priority above logger.",
    ),
    "M029": _t(
        "M029", "DMA, cache & ARM ordering instructions", "dma_cache_ordering", "V",
        "G A N R", ["Q077", "Q079"],
        "DMA cache coherency; DMB vs DSB vs ISB with driver examples.",
        ["Clean before TX DMA", "Invalidate after RX DMA", "Non-cacheable MPU region"],
        [("DMA Programming", "Advanced_Hardware/DMA_Programming.md"),
         ("Cache Management Coherency", "Advanced_Hardware/Cache_Management_Coherency.md")],
        tier="S",
        interviewer_wants="You won't corrupt buffers when CPU and DMA share RAM.",
        core=["CPU wrote buffer → clean cache before DMA TX", "DMA wrote buffer → invalidate before CPU read",
              "DMB: memory access ordering between observers", "DSB: wait for all memory ops to complete",
              "ISB: flush pipeline after MMU/MPU change"],
        traps=["DMA into stack", "Forgetting invalidate on RX", "Using cached buffer without alignment"],
        followups_v=[("Example DMB?", "Publish descriptor chain: write descriptors, DMB, then kick DMA engine."),
                     ("Coherent allocation?", "dma_alloc_coherent or MPU non-cacheable alias.")],
        script_60="DMA and CPU don't see the same bytes unless you manage cache. Before TX I clean the buffer so memory has fresh data. After RX I invalidate before the CPU reads. On ARM, DMB orders stores before kicking hardware; DSB completes everything; ISB after changing MPU regions.",
        ti_story="PRU shared buffer needed explicit cache clean/invalidate on AM335x — missing clean caused stale TX CRC failures.",
    ),
    "M030": _t(
        "M030", "Runtime environments & memory layout", "runtime_memory_layout", "V",
        "G A T N I", ["Q080", "Q082"],
        "Bare-metal vs RTOS vs Linux PREEMPT_RT; stack vs heap vs static; heap limits and fragmentation.",
        ["Stack sizing", "Heap avoidance in safety", "PREEMPT_RT scope"],
        [("Memory Management", "Embedded_C/Memory_Management.md"),
         ("Embedded Linux", "Operating_Systems_Linux/Embedded_Linux.md")],
        interviewer_wants="You understand where code lives and why FW limits dynamic allocation.",
        core=["Bare-metal: single stack, no OS overhead, you own all timing",
              "RTOS: tasks with isolated stacks, deterministic scheduler, IPC primitives",
              "Linux PREEMPT_RT: millisecond-ish RT with kernel patches; not hard RT",
              "Static allocation preferred for cert/safety; heap fragments over long uptime"],
        traps=["Undersized ISR stack", "malloc in ISR", "Assuming Linux is hard RT"],
        followups_v=[("Why limit heap?", "Fragmentation and nondeterministic latency; OOM in field is hard to recover."),
                     ("Stack vs heap?", "Stack for call frames — measure high-water; heap for variable lifetime objects.")],
        script_60="Bare-metal is simplest timing but you build everything. RTOS adds tasks and IPC with bounded context switch. Linux PREEMPT_RT helps soft RT but not microsecond guarantees. I prefer static pools; heap is last resort because fragmentation breaks long-running firmware.",
        ti_story="Industrial drive FW used static pools only — one malloc in init; field units ran years without heap fragmentation issues.",
    ),
    "M031": _t(
        "M031", "Boot, MMU, MPU & TrustZone", "boot_mmu_trustzone", "V",
        "A R G Q", ["Q081", "Q085", "Q099"],
        "Reset → vectors → .data/.bss → main; paging/MMU/TLB; MPU vs MMU vs TrustZone.",
        ["Vector table relocation", "BSS zero-init", "Exception levels"],
        [("Bootloader Development", "System_Integration/Bootloader_Development.md"),
         ("Memory Protection Units", "Advanced_Hardware/Memory_Protection_Units.md")],
        interviewer_wants="Boot-to-main mental model and protection at driver depth.",
        core=["Reset loads SP/PC from vector table; copy .data, zero .bss, call main",
              "MMU: virtual addresses, page tables, TLB caches translations",
              "MPU: simpler region-based protection on M-profile — no virtual memory",
              "TrustZone: secure/non-secure worlds, NSC gateways for crypto keys"],
        traps=["Assuming BSS is zero without CRT", "DMA to unmapped region", "Mixing secure/non-secure pointers"],
        followups_v=[("MPU for stacks?", "Guard regions below stacks catch overflow as MemManage fault."),
                     ("TrustZone driver impact?", "Sensitive keys only in secure world; NS calls via veneers.")],
        script_60="After reset the CPU jumps through the vector table, startup copies initialized data and clears BSS, then main. MMU gives virtual memory with TLB speedups; MPU on Cortex-M sets a few protect regions without OS. TrustZone splits secure and normal worlds for keys and attestation.",
        ti_story="AM64x bring-up: verified .data copy in startup — uninitialized global caused encoder calibration drift until BSS init fixed.",
    ),
    "M032": _t(
        "M032", "Measurement, debug & heisenbugs", "measurement_debug", "V",
        "T N I G A", ["Q086", "Q087", "Q088"],
        "Measure ISR latency/jitter; debug intermittent protocol/CRC/timing; why printf hides bugs.",
        ["GPIO pin profiling", "Logic analyzer", "Minimal intrusive logging"],
        [("JTAG/SWD Debugging", "Debugging/JTAG_SWD_Debugging.md"),
         ("Oscilloscope Measurements", "Debugging/Oscilloscope_Measurements.md")],
        tier="S",
        interviewer_wants="Systematic bench methodology, not guesswork.",
        core=["ISR latency: DWT cycle counter or GPIO toggle + scope",
              "Jitter: histogram many samples; look for priority blocking",
              "Intermittent CRC: capture raw bytes, compare against golden; check endian",
              "printf changes timing — use trace buffer or deferred log"],
        traps=["Optimizing away variables when debugging", "printf in ISR", "Single-sample latency claims"],
        followups_v=[("APEC methodology?", "Define measurement window, trigger, and statistical report — mean and max jitter."),
                     ("Heisenbug from debug?", "Debug build disables optimizations; use -O2 with guarded trace macros.")],
        script_60="I measure ISR latency with cycle counters or a scope on a GPIO strobe. For intermittent bugs I log raw frames to a ring and post-process — never printf in the hot path. printf adds mutex and UART time that masks races.",
        ti_story="EnDAT timing failures only appeared at full speed — scope on SCK vs DATA pin showed setup violation; printf had been masking it by slowing the loop.",
    ),
    "M033": _t(
        "M033", "Buses & protocols (I2C, CAN, endian)", "buses_protocols_verbal", "V",
        "Z A T N I", ["Q090", "Q091", "Q092"],
        "I2C timing; CAN arbitration and bus-off; endianness bugs in protocols.",
        ["START/STOP", "ACK/NACK", "CAN ID arbitration", "Wire vs host endian"],
        [("I2C Protocol", "Communication_Protocols/I2C_Protocol.md"),
         ("CAN Protocol", "Communication_Protocols/CAN_Protocol.md")],
        interviewer_wants="Protocol-level reasoning beyond register poking.",
        core=["I2C: open drain, START, addr+W/R, data bytes, ACK, STOP; clock stretch",
              "CAN: wired-AND arbitration — lowest ID wins; error frames escalate to bus-off",
              "Endian: define wire format explicitly; never assume struct layout matches wire"],
        traps=["Missing pull-ups on I2C", "Ignoring bus-off recovery", "Casting packet buffer to struct"],
        followups_v=[("CAN bus-off?", "Controller stops transmitting after error threshold — needs init recovery sequence."),
                     ("Prevent endian bugs?", "read_be16/write_le32 helpers; static_assert on wire struct sizes.")],
        script_60="I2C is open-drain with START, address, data, ACK, STOP — slaves can stretch SCL. CAN arbitrates by ID on the wire; too many errors trigger bus-off. I always use explicit endian helpers — ARM is little-endian, many protocols are big-endian.",
        ti_story="Host tool sent big-endian length field; firmware read as native LE — classic off-by-256 framing bug caught with hex dump.",
    ),
    "M034": _t(
        "M034", "Linux driver interface & platform model", "linux_driver_platform", "V",
        "A G Q Z M", ["Q093", "Q094", "Q096"],
        "ioctl/mmap/poll/netlink; platform probe/remove + DT; runtime PM suspend/resume.",
        ["copy_from_user", "devm_kzalloc", "of_property_read"],
        [("Linux Kernel Programming", "Operating_Systems_Linux/Linux_Kernel_Programming.md"),
         ("Device Drivers", "Operating_Systems_Linux/Device_Drivers.md")],
        tier="S",
        interviewer_wants="You can sketch a proper platform driver ABI.",
        core=["ioctl for structured commands; mmap for bulk zero-copy; poll for blocking read",
              "platform_driver probe: parse DT, devm_ioremap, register irq, devm_kzalloc",
              "pm_runtime_get/put; suspend saves state and gates clocks"],
        traps=["Dereferencing __user pointers", "Missing remove() cleanup", "IRQ without request_irq balance"],
        followups_v=[("ioctl vs sysfs?", "ioctl for complex ops; sysfs for simple config attributes."),
                     ("Device Tree role?", "Hardware description in kernel — driver reads properties at probe.")],
        script_60="Userspace talks to drivers via ioctl for commands, mmap for buffers, poll to sleep until data. Platform drivers match Device Tree compatible strings, use devm_* for auto cleanup, and implement suspend/resume with runtime PM refs balanced.",
        ti_story="Encoder platform driver: DT gave register base and IRQ; miscdevice + ioctl exposed position read — probe/remove symmetric for CI module load tests.",
    ),
    "M035": _t(
        "M035", "Security & safety concepts", "security_safety", "V",
        "A T Z R N I", ["Q097", "Q098"],
        "Secure boot and anti-rollback; ASIL/IEC diagnostics, watchdog hierarchy, degrade modes.",
        ["Chain of trust", "Version monotonic counter", "Safe state on fault"],
        [("Secure Boot and Chain of Trust", "Embedded_Security/Secure_Boot_and_Chain_of_Trust.md"),
         ("Watchdog Timers", "HW_Module/Watchdog_Timers.md")],
        interviewer_wants="High-level security/safety vocabulary for system design.",
        core=["Secure boot: ROM verifies next stage signature; anti-rollback via monotonic version fuse",
              "ASIL: hazard analysis drives diagnostic coverage and fail-safe reactions",
              "Watchdog hierarchy: outer WDT catches runaway supervisor; inner per-subsystem",
              "Degrade mode: limp-home with reduced features vs full shutdown"],
        traps=["Crypto in application without secure storage", "Single WDT pet from printf loop"],
        followups_v=[("Anti-rollback?", "Reject firmware older than eFuse version even if signature valid."),
                     ("Diagnostics for ASIL?", "Dual-channel compare, periodic self-test, documented safe state.")],
        script_60="Secure boot chains verified images from ROM through bootloader to app, with version fuses preventing downgrade. Safety systems map hazards to ASIL levels requiring diagnostics and defined safe states. Watchdogs are layered — not just one pet from main.",
        ti_story="Drive platform: outer WDT reset if motion supervisor missed deadline; inner WDT on comms task only — hierarchy prevented single bug from bricking recovery.",
    ),
    "M036": _t(
        "M036", "RT validation & system-level verbal", "rt_validation_system", "V",
        "I T N G", ["Q100"],
        "Validate hard real-time multi-channel protocol stack end-to-end.",
        ["WCET measurement", "Schedule feasibility", "HIL testing"],
        [("Response Time Analysis", "Real_Time_Systems/Response_Time_Analysis.md"),
         ("Hardware-in-the-Loop Testing", "Debugging/Hardware-in-the-Loop_Testing.md")],
        interviewer_wants="End-to-end validation story, not unit-test-only thinking.",
        core=["Define deadlines per channel; measure WCET with scope + CPU trace",
              "Schedule analysis: sum WCET ≤ frame or RTA with blocking",
              "Soak test under worst-case bus load; inject faults",
              "HIL replays captured field traces"],
        traps=["Average-case timing claims", "Testing only idle bus", "No backpressure scenario"],
        followups_v=[("Multi-channel interference?", "Shared CPU and bus — test all channels active simultaneously."),
                     ("Pass criteria?", "Zero missed deadlines over N hours at max load plus fault injection.")],
        script_60="I start from deadlines, measure WCET per task with tracing, run schedulability analysis, then soak test all channels at max load on HIL with fault injection. Pass means zero deadline misses over the test window.",
        ti_story="Validated EnDAT + HDSL + host comms concurrently on HIL — found host USB burst starved parser until ring high-water throttle added.",
    ),
})

# Design topics M039-M044
TOPICS.update({
    "M039": _t(
        "M039", "Driver stacks & bus frameworks", "driver_stacks_frameworks", "D",
        "G A N Z", ["Q101", "Q106", "Q107"],
        "Unified APIs for UART poll/IRQ/DMA, I2C transaction engine, SPI multi-device.",
        ["Retry/timeout/recovery", "CS management", "DMA hooks"],
        [("Hardware Abstraction Layer", "HW_Module/Hardware_Abstraction_Layer.md"),
         ("UART Protocol", "Communication_Protocols/UART_Protocol.md")],
        tier="S",
        clarifying_design=["Target bare-metal or Linux kernel framework?", "How many SPI devices on shared bus?"],
        requirements=["Common bus handle struct with ops vtable", "Timeout and error codes unified across UART/I2C/SPI",
                      "I2C: write, read, write_read, recovery", "SPI: per-device config + CS assert"],
        diagram="""```
  App / Middleware
        |
  +-----+-----+-----+
  | UART| I2C | SPI |  bus API (open, xfer, close)
  +--+--+--+--+--+--+
     |     |     |
  HAL ops vtable per instance (regs, irq, dma)
     |     |     |
  HW controllers
```""",
        components=["`bus_uart_t` with mode POLL|IRQ|DMA", "`i2c_engine_submit(txn)` queue + recovery FSM",
                    "`spi_device_t` with mode, speed, cs_gpio", "Shared `hal_time_ms()` for timeouts"],
        failure_modes=["Ring full on UART RX — drop policy + counter", "I2C NACK — STOP and return EIO",
                       "SPI CS glitch — enforce CS lead/trail times"],
        tradeoffs=["| Approach | Pros | Cons |", "|---|---|---|",
                   "| Poll | Simple bring-up | CPU bound |", "| IRQ + ring | Efficient moderate rate | IRQ load |",
                   "| DMA | High throughput | Cache coherency complexity |"],
        numbers=["UART 115200 → ~11.5 KB/s; IRQ budget <5% CPU at 1 Mbaud with DMA",
                 "I2C 400 kHz → ~40 KB/s theoretical; clock stretch eats margin"],
        followups_d=[("How unify errors?", "Common `bus_err_t` enum mapped from hardware flags."),
                     ("SPI multi-device?", "Per-device lock + CS gpio; bus lock around transfer.")],
        ti_story="TI motor SDK pattern: HAL vtable per SOC family — same UART API on AM243x and AM64x with different register backends.",
    ),
    "M040": _t(
        "M040", "Data path: ISR → task → DMA → pipeline", "data_path_pipeline", "D",
        "G A T N Z", ["Q102", "Q105", "Q116", "Q117"],
        "ISR→task event pipeline; DMA framework; sensor pipeline; device path IRQ→SHM→DMA→sleep.",
        ["Latency budget", "Backpressure", "Descriptor ownership"],
        [("DMA Programming", "Advanced_Hardware/DMA_Programming.md"),
         ("DMA Buffer Management", "Embedded_C/DMA_Buffer_Management.md")],
        tier="S",
        clarifying_design=["End-to-end latency target?", "Who owns buffer lifetime across DMA complete?"],
        requirements=["ISR enqueues events only; task parses", "DMA desc chain with completion callback",
                      "Pipeline stages: acquire → process → release", "Power: quiesce DMA before sleep"],
        diagram="""```
  Sensor -> IRQ -> ring -> task -> filter -> alert
                |
             DMA RX (ping-pong)
                |
            process half -> release desc
```""",
        components=["SPSC ring ISR→task", "`dma_chan_submit(desc, cb)`", "Pipeline stage function pointers",
                    "pm: wait TX drain + DMA idle before WFI"],
        failure_modes=["Ring overflow — throttle source", "DMA error bit — teardown and reinit channel",
                       "Sleep with active DMA — data corruption"],
        tradeoffs=["| Stage | Latency | CPU |", "|---|---:|---:|",
                   "| IRQ byte | low | high |", "| IRQ + ring | medium | medium |", "| DMA ping-pong | lowest bulk | low |"],
        numbers=["Example: 10 kHz sample → 100 µs period; ISR budget 5 µs; task WCET 30 µs"],
        followups_d=[("Backpressure?", "High-water callback throttles producer before drop."),
                     ("DMA ownership?", "CPU owns until submit; device owns until completion IRQ; then callback returns to pool.")],
        ti_story="EnDAT path: PRU DMA ping-pong into cache-aligned buffers, R5F parses in task — IRQ only flipped buffer index.",
    ),
    "M041": _t(
        "M041", "Platform services: timers, logging, watchdog, fault", "platform_services", "D",
        "G A T Z N I", ["Q103", "Q104", "Q108", "Q109"],
        "Logging levels/ring/crash persist; timer service; watchdog heartbeats; fault manager.",
        ["RT-safe logging", "Timer wheel vs heap", "Fault classify/retry/degrade"],
        [("Error Handling and Logging", "System_Integration/Error_Handling_and_Logging.md"),
         ("Timer Wheel", "Data_Struct_Implementation/timerWheel/README.md")],
        clarifying_design=["Log to UART, flash, or both?", "Max log rate in fault storm?"],
        requirements=["Async log ring; drop on full with counter", "SW timer service on HW tick",
                      "Per-task heartbeat slots; outer WDT", "Fault manager FSM: detect→classify→act"],
        diagram="""```
  Tasks --> log_ring --> drain task --> UART / flash
  Tasks --> heartbeat --> WDT supervisor
  Faults --> fault_mgr --> retry | degrade | reset
```""",
        components=["`log_printf(level, fmt)` macro → ring", "`timer_service_post(delay, cb)`",
                    "`wdt_supervisor_kick()` after all heartbeats", "`fault_report(code, severity)`"],
        failure_modes=["Log flood hides real fault — rate limit", "Missed heartbeat — safe state",
                       "Flash log wear — circular sector with metadata"],
        tradeoffs=["| Timer struct | Insert | Cancel |", "|---|---:|---:|",
                   "| Sorted list | O(n) | O(n) |", "| Min-heap | O(log n) | O(log n) |", "| Wheel | O(1) | O(1) coarse |"],
        numbers=["Log ring 4 KB → ~200 lines at 20 B avg; drain at 115200 ~44 ms worst case"],
        followups_d=[("Crash persistence?", "`.noinit` ram console or flash ring with magic header."),
                     ("Fault degrade?", "Retry N times with backoff, then limp mode or reset subsystem.")],
        ti_story="Field drive logs: ramconsole survived WDT reset; fault_mgr downgraded to speed-limited mode after repeated encoder faults.",
    ),
    "M042": _t(
        "M042", "Boot, OTA, security & power", "boot_ota_security_power", "D",
        "A G Z T R", ["Q110", "Q111", "Q118", "Q119"],
        "OTA A/B + auth + anti-brick; boot health checks; peripheral suspend/resume; secure firmware load.",
        ["Signature verify", "Rollback index", "Clock gating on suspend"],
        [("Firmware Update Mechanisms", "System_Integration/Firmware_Update_Mechanisms.md"),
         ("Secure Boot and Chain of Trust", "Embedded_Security/Secure_Boot_and_Chain_of_Trust.md")],
        tier="S",
        clarifying_design=["Dual-bank flash or external storage?", "Who holds signing keys?"],
        requirements=["A/B partitions with boot flag", "Verify signature + version before swap",
                      "Bootloader health GPIO/UART marker", "Driver suspend: save regs, gate clk, pin tri-state"],
        diagram="""```
  Boot ROM -> BL (verify A/B) -> App
                  |
            OTA download -> staging -> verify -> swap flag -> reboot
```""",
        components=["`ota_write_chunk()`", "`boot_select_slot()`", "`driver_suspend/resume` ops",
                    "Secure element or SW crypto verify"],
        failure_modes=["Power loss mid-OTA — keep old slot valid until atomic swap",
                       "Resume without restore — peripheral mismatch", "Downgrade attack — monotonic version"],
        tradeoffs=["| OTA | Pros | Cons |", "|---|---|---|",
                   "| Dual bank | Safe rollback | 2× flash |", "| Patch | Less space | Complex delta |"],
        numbers=["128 KB BL + 1 MB app typical; OTA chunk 4 KB aligned to flash page"],
        followups_d=[("Anti-brick?", "Never erase running slot until verify complete; keep boot pin recovery."),
                     ("Secure load factory vs field?", "Factory: JTAG lock after fuse; field: signed OTA only.")],
        ti_story="Drive OTA: verified image in inactive bank, atomic flag swap — bricked units recovered via UART BL after bad OTA taught us verify-before-erase.",
    ),
    "M043": _t(
        "M043", "Multi-core, encoder & gateway systems", "multicore_encoder_gateway", "D",
        "A N R G Z M I T N", ["Q112", "Q113", "Q114", "Q115"],
        "Dual-core RT+app IPC; Linux driver + userspace ABI; multi-channel encoder hard RT; Ethernet↔CAN gateway.",
        ["PRU/FPGA paths", "Host API", "QoS/backpressure"],
        [("Multi-Core Programming", "Advanced_Hardware/Multi_Core_Programming.md"),
         ("Cross-MCU Communication", "System_Design/Cross-MCU_Communication.md")],
        tier="S",
        clarifying_design=["Which core owns motion vs comms?", "Latency target for position sample to host?"],
        requirements=["Shared memory mailbox + doorbell between RT and Linux",
                      "Kernel driver mmap/ioctl for encoder ring", "Hard RT sample on PRU/R5F",
                      "Gateway: priority queues per egress port"],
        diagram="""```
  Encoder HW -> PRU/R5F (RT) -> SHM ring -> Linux driver -> userspace API
  Eth <-> gateway <-> CAN/UART (QoS queues)
```""",
        components=["`rpmsg` or custom mailbox", "`encoder_chrdev` with position read",
                    "Gateway routing table + rate limit per port"],
        failure_modes=["SHM cache coherency — explicit sync", "Host poll starvation — eventfd/epoll",
                       "Gateway flood — drop low-priority with ECN counter"],
        tradeoffs=["| IPC | Latency | Complexity |", "|---|---:|---:|",
                   "| Mailbox | µs | Low |", "| RPMsg | ms | Standard on TI SK |", "| PCIe | lowest bulk | High |"],
        numbers=["EnDAT position loop 16 kHz → 62.5 µs; host API <1 ms jitter target"],
        followups_d=[("Map HDSL/EnDAT?", "RT core handles SCK timing; app core exposes aggregated position over IOCTL."),
                     ("Gateway QoS?", "Separate rings per priority; WRR across egress ports.")],
        ti_story="Signature topic: HDSL on PRU, EnDAT3 parse on R5F, host ABI via mmap ring — same pattern as M043 gateway QoS for fieldbus bridges.",
    ),
    "M044": _t(
        "M044", "Test, bring-up & validation architecture", "test_bringup_validation", "D",
        "G A T N", ["Q120"],
        "Fake registers, fault injection, timing tests, CI for FW.",
        ["HAL fakes", "HIL", "Regression on host"],
        [("Unit Testing for Embedded", "Debugging/Unit_Testing_for_Embedded.md"),
         ("Hardware-in-the-Loop Testing", "Debugging/Hardware-in-the-Loop_Testing.md")],
        clarifying_design=["CI on host only or target in loop?", "Which faults to inject?"],
        requirements=["Register fake layer behind function pointers", "Fault inject: timeout, NACK, CRC bad",
                      "Timing tests with mock tick", "CI: build all + run host tests"],
        diagram="""```
  Tests -> fake HAL -> module under test
  CI: gcc host build + pytest/lit + cross-compile
  Nightly: HIL harness on target
```""",
        components=["`hal_fake_regs[]`", "`fault_inject_set(FAULT_I2C_NACK)`",
                    "`test_tick_advance(ms)`", "GitHub CI matrix arm-gcc"],
        failure_modes=["Fakes diverge from silicon — periodic HIL", "Flaky timing tests — deterministic tick",
                       "Missing cross-compile in CI — link errors in field"],
        tradeoffs=["| Test level | Speed | Fidelity |", "|---|---:|---:|",
                   "| Host unit | fast | low |", "| HIL | slow | high |", "| Field soak | slowest | real |"],
        numbers=["Aim >80% branch on safety modules; host suite <60 s in CI"],
        followups_d=[("Fake register fidelity?", "Mirror real flag timing — set TXE after DR write in fake."),
                     ("CI scope?", "Host tests every PR; HIL nightly; release soak 72 h.")],
        ti_story="Encoder driver: fake MMIO let us run 200 host tests per PR; HIL caught one flag ordering mismatch fakes missed.",
    ),
})


def further_study_section(topic: dict[str, Any]) -> str:
    lines = ["## Further study", ""]
    for title, path in topic["further_study"]:
        lines.append(ent_link(title, path))
    return "\n".join(lines)


def variant_table(topic: dict[str, Any]) -> str:
    rows = ["| Original Q | Sub-variant |", "|---|---|"]
    merged = topic["merged_from"]
    variants = topic["sub_variants"]
    for i, q in enumerate(merged):
        v = variants[i] if i < len(variants) else "See merged solution"
        rows.append(f"| {q} | {v} |")
    if len(variants) > len(merged):
        for v in variants[len(merged):]:
            rows.append(f"| — | {v} |")
    return "\n".join(rows)


def header_block(topic: dict[str, Any]) -> str:
    tier = topic.get("tier")
    tier_line = f"**Tier:** {tier} (must-know)\n" if tier else ""
    typ = {"C": "Coding (C)", "V": "Verbal", "D": "Design"}[topic["type"]]
    return f"""# {topic['id']} — {topic['title']}

**Type:** {typ}  
**Merged from:** {fmt_qs(topic['merged_from'])}  
**Companies:** {format_companies(topic['companies'])}  
{tier_line}
**Question:** {topic['prep_question']}

---

## Sub-variant coverage

{variant_table(topic)}

---"""


def default_coding_sections(topic: dict[str, Any]) -> dict[str, Any]:
    title = topic["title"].lower()
    clarifying = topic.get("clarifying", [
        f"Target bare-metal or host-compile OK for {topic['id']}?",
        "Return codes on error or silent drop with counter?",
    ])
    plan = [
        "Restate API signatures and invariants aloud before coding.",
        "Implement core logic with straightforward loops; optimize after tests pass.",
        "Document ownership, error codes, and ISR vs task context.",
    ]
    if "ring" in title:
        plan.insert(1, "Choose spare-slot vs count field; define drop policy on full.")
    ds = [
        "Structs/enums matching API — invariants in comments.",
        "Platform hooks (`irq_save`, `now_ms`) isolated for host test fakes.",
    ]
    edges = [
        "NULL / zero-length — defined error or no-op.",
        "Boundary at max capacity — no overrun.",
        "Repeated calls idempotent where API requires.",
    ]
    conc = "Label ISR-writable vs task-only fields. Keep ISR push O(1); defer parsing to task."
    if topic["type"] == "C" and "alloc" in title:
        conc = "ISR alloc only from ISR-safe pool; never malloc in ISR."
    cx = [
        "| Operation | Time | Space |",
        "|---|---:|---:|",
        "| primary API | O(1) typical | O(1) or O(cap) |",
    ]
    followups = topic.get("followups", [])
    tests = [
        "Happy path — minimal valid input produces expected output.",
        "Zero/null/empty — defined error, no crash.",
        "Boundary — max capacity or timeout edge.",
        "Stress — back-to-back calls or burst traffic.",
    ]
    return {
        "clarifying": clarifying,
        "plan": plan,
        "ds": ds,
        "edges": edges,
        "conc": conc,
        "cx": cx,
        "followups": followups,
        "tests": tests,
    }


def render_coding(topic: dict[str, Any], code: str) -> str:
    sec = default_coding_sections(topic)
    clarifying = topic.get("clarifying", sec["clarifying"])
    plan = topic.get("plan", sec["plan"])
    ds = topic.get("data_structures", sec["ds"])
    edges = topic.get("edge_cases", sec["edges"])
    conc = topic.get("concurrency", sec["conc"])
    cx = topic.get("complexity", sec["cx"])
    followups = topic.get("followups", sec["followups"])
    tests = topic.get("tests", sec["tests"])
    intro = topic.get("approach", f"Build {topic['title']} in layers: invariants first, happy path, then edge cases and concurrency.")

    lines = [
        header_block(topic),
        "",
        "## Step 0 — Clarifying questions (say these out loud)",
        "",
    ]
    for b in clarifying:
        lines.append(f"- **Candidate:** {b}")
    lines.extend([
        "",
        "## Step 1 — Approach",
        "",
        intro,
        "",
    ])
    for p in plan:
        lines.append(f"- {p}")
    lines.extend(["", "## Step 2 — Data structures / invariants", ""])
    for i, d in enumerate(ds, 1):
        lines.append(f"{i}. {d}")
    lines.extend([
        "",
        "## Step 3 — Complete solution (compilable C)",
        "",
        "```c",
        beautify_c_code(code).strip(),
        "```",
        "",
        "## Step 4 — Complexity",
        "",
    ])
    lines.extend(cx)
    lines.extend(["", "## Step 5 — Edge cases", ""])
    for i, e in enumerate(edges, 1):
        lines.append(f"{i}. {e}")
    lines.extend([
        "",
        "## Step 6 — Concurrency / ISR / context notes",
        "",
        conc,
        "",
        "## Step 7 — Follow-up answers",
        "",
    ])
    for item in followups:
        if isinstance(item, tuple):
            q, a = item
            lines.append(f"**Q: {q}**  ")
            lines.append(f"**A:** {a}")
            lines.append("")
    lines.extend(["", "## Step 8 — Tests", ""])
    for i, t in enumerate(tests, 1):
        lines.append(f"{i}. {t}")
    lines.extend([
        "",
        further_study_section(topic),
        "",
        "---",
        "",
        f"*Generated by `tools/generate_merged_solutions.py` for {topic['id']}.*",
    ])
    return "\n".join(lines)


def render_verbal(topic: dict[str, Any]) -> str:
    lines = [
        header_block(topic),
        "",
        "## Step 0 — What the interviewer wants",
        "",
        topic["interviewer_wants"],
        "",
        "## Step 1 — Core answer (bullets)",
        "",
    ]
    for b in topic["core"]:
        lines.append(f"- {b}")
    lines.extend(["", "## Step 2 — Traps / mistakes", ""])
    for t in topic["traps"]:
        lines.append(f"- {t}")
    lines.extend(["", "## Step 3 — Follow-ups with answers", ""])
    for q, a in topic["followups_v"]:
        lines.append(f"**Q: {q}**  ")
        lines.append(f"**A:** {a}")
        lines.append("")
    lines.extend([
        "## Step 4 — 60-second script",
        "",
        topic["script_60"],
        "",
        "## Step 5 — TI story hook",
        "",
        topic["ti_story"],
        "",
        further_study_section(topic),
        "",
        "---",
        "",
        f"*Generated by `tools/generate_merged_solutions.py` for {topic['id']}.*",
    ])
    return "\n".join(lines)


def render_design(topic: dict[str, Any]) -> str:
    lines = [
        header_block(topic),
        "",
        "## Step 0 — Clarifying questions",
        "",
    ]
    for q in topic["clarifying_design"]:
        lines.append(f"- {q}")
    lines.extend(["", "## Step 1 — Requirements", ""])
    for r in topic["requirements"]:
        lines.append(f"- {r}")
    lines.extend([
        "",
        "## Step 2 — ASCII block diagram",
        "",
        topic["diagram"],
        "",
        "## Step 3 — Components / APIs",
        "",
    ])
    for c in topic["components"]:
        lines.append(f"- {c}")
    lines.extend(["", "## Step 4 — Failure modes", ""])
    for f in topic["failure_modes"]:
        lines.append(f"- {f}")
    lines.extend(["", "## Step 5 — Tradeoffs table", ""])
    lines.extend(topic["tradeoffs"])
    lines.extend(["", "## Step 6 — Numbers / budgets", ""])
    for n in topic["numbers"]:
        lines.append(f"- {n}")
    lines.extend(["", "## Step 7 — Follow-ups", ""])
    for q, a in topic["followups_d"]:
        lines.append(f"**Q: {q}**  ")
        lines.append(f"**A:** {a}")
        lines.append("")
    lines.extend([
        "## Step 8 — TI story hook",
        "",
        topic["ti_story"],
        "",
        further_study_section(topic),
        "",
        "---",
        "",
        f"*Generated by `tools/generate_merged_solutions.py` for {topic['id']}.*",
    ])
    return "\n".join(lines)


def filename_for(topic: dict[str, Any]) -> str:
    return f"{topic['id']}_{topic['slug']}.md"


def generate_readme(written: list[tuple[str, dict[str, Any]]]) -> str:
    rows = [
        "# FINAL 120 — Merged Topic Solutions",
        "",
        "**Question list:** [`../../FINAL_120_MERGED_TOPICS.md`](../../FINAL_120_MERGED_TOPICS.md)  ",
        "**40 prep topics** (M001–M044) — one comprehensive solution per merged topic.  ",
        "*(M045 is mock checkpoint only — no solution file.)*",
        "",
        "Regenerate: `python3 tools/generate_merged_solutions.py`",
        "",
        "## All solutions",
        "",
        "| ID | Topic | Type | Original Qs | File |",
        "|----|-------|------|-------------|------|",
    ]
    type_label = {"C": "Coding", "V": "Verbal", "D": "Design"}
    for fname, topic in sorted(written, key=lambda x: x[1]["id"]):
        rows.append(
            f"| {topic['id']} | {topic['title'][:40]} | {type_label[topic['type']]} "
            f"| {fmt_qs(topic['merged_from'])} | [{fname}](./{fname}) |"
        )
    rows.append("")
    rows.append(f"**Total: {len(written)} solution files**")
    return "\n".join(rows) + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    c_codes = build_c_codes()
    written: list[tuple[str, dict[str, Any]]] = []
    missing_code: list[str] = []

    for mid in sorted(TOPICS.keys()):
        topic = TOPICS[mid]
        fname = filename_for(topic)
        if topic["type"] == "C":
            code = c_codes.get(mid, "")
            if not code.strip():
                missing_code.append(mid)
                code = f"/* missing code for {mid} */"
            body = render_coding(topic, code)
        elif topic["type"] == "V":
            body = render_verbal(topic)
        elif topic["type"] == "D":
            body = render_design(topic)
        else:
            print(f"Unknown type for {mid}", file=sys.stderr)
            return 1
        path = OUT_DIR / fname
        path.write_text(body, encoding="utf-8")
        written.append((fname, topic))
        print(f"Wrote {path}")

    readme = generate_readme(written)
    readme_path = OUT_DIR / "README.md"
    readme_path.write_text(readme, encoding="utf-8")
    print(f"Wrote {readme_path}")
    print(f"Total files: {len(written)} (+ README)")

    if missing_code:
        print(f"Missing C code: {', '.join(missing_code)}", file=sys.stderr)
        return 1
    if len(written) != 40:
        print(f"Expected 40 files, got {len(written)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
