#!/usr/bin/env python3
"""Generate interview-format solution markdown for all coding-round questions."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from solution_enrichments import (
    approach_text,
    clarifying_questions,
    complexity_notes,
    concurrency_notes,
    data_structures,
    edge_cases,
    finalize_code,
    followup_answer,
    test_cases,
)

ROOT = Path(__file__).resolve().parent.parent
CODING_DIR = ROOT / "coding_rounds"
SOLUTIONS_DIR = ROOT / "solutions" / "coding_rounds"

QUESTION_HEADER = re.compile(r"^### (C\d+) — (.+)$", re.MULTILINE)
IMPLEMENT_FENCE = re.compile(
    r"\*\*Implement:\*\*\s*\n```(?:c|cpp)\n(.*?)```", re.DOTALL
)
PROMPT_RE = re.compile(
    r"\*\*Interview prompt:\*\*\s*\n(.*?)(?=\n\*\*Implement:|\n\*\*Constraints|\n---|\Z)",
    re.DOTALL,
)
FOLLOWUPS_RE = re.compile(
    r"\*\*Follow-ups:\*\*\s*\n(.*?)(?=\n---|\n### |\Z)", re.DOTALL
)
CONSTRAINTS_RE = re.compile(
    r"\*\*Constraints / expectations:\*\*\s*\n(.*?)(?=\n\*\*Follow-ups:|\n---|\n### |\Z)",
    re.DOTALL,
)

CATEGORY_BY_FILE = {
    "01_c_language_ub_macros.md": ("c_language", 1),
    "02_bits_endian_wire_formats.md": ("bits_endian", 21),
    "03_memory_string_ops.md": ("memory_string", 41),
    "04_allocators_memory_mgmt.md": ("allocators", 56),
    "05_rings_queues_buffers.md": ("rings_queues", 71),
    "06_synchronization_lockfree.md": ("sync", 91),
    "07_interrupts_deferred_work.md": ("interrupts", 111),
    "08_mmio_register_hal.md": ("mmio", 121),
    "09_uart_spi_i2c_gpio_drivers.md": ("drivers", 136),
    "10_dma_patterns.md": ("dma", 161),
    "11_timers_schedulers.md": ("timers", 173),
    "12_protocol_parsers_framing.md": ("protocol", 186),
    "13_fsm_control.md": ("fsm", 201),
    "14_filters_numeric.md": ("filters", 213),
    "15_ipc_dual_core.md": ("ipc", 219),
    "16_logging_crash_diagnostics.md": ("logging", 231),
    "17_power_watchdog_reliability.md": ("power", 241),
    "18_testing_fakes_harness.md": ("testing", 251),
    "19_cpp_embedded.md": ("cpp", 261),
    "20_performance_cache.md": ("performance", 276),
    "21_linux_driver_snippets.md": ("linux", 286),
}


@dataclass
class Question:
    id: str
    id_num: int
    title: str
    prompt: str
    implement: str
    constraints: str
    followups: list[str]
    source_file: str
    category: str
    lang: str = "c"


def parse_followups(text: str) -> list[str]:
    items: list[str] = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("- "):
            items.append(line[2:].strip())
        else:
            items.append(line)
    return items


def detect_lang(implement: str, filename: str) -> str:
    if "19_cpp" in filename or "class " in implement or "template" in implement:
        return "cpp"
    return "c"


def parse_question_file(path: Path) -> list[Question]:
    text = path.read_text(encoding="utf-8")
    cat_key, _ = CATEGORY_BY_FILE.get(path.name, ("generic", 0))
    questions: list[Question] = []
    headers = list(QUESTION_HEADER.finditer(text))
    for i, m in enumerate(headers):
        qid, title = m.group(1), m.group(2).strip()
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = text[start:end]
        prompt_m = PROMPT_RE.search(block)
        impl_m = IMPLEMENT_FENCE.search(block)
        cons_m = CONSTRAINTS_RE.search(block)
        fu_m = FOLLOWUPS_RE.search(block)
        implement = impl_m.group(1).strip() if impl_m else "/* see prompt */"
        questions.append(
            Question(
                id=qid,
                id_num=int(qid[1:]),
                title=title,
                prompt=(prompt_m.group(1).strip() if prompt_m else title),
                implement=implement,
                constraints=(cons_m.group(1).strip() if cons_m else ""),
                followups=parse_followups(fu_m.group(1)) if fu_m else [],
                source_file=path.name,
                category=cat_key,
                lang=detect_lang(implement, path.name),
            )
        )
    return questions


# ---------------------------------------------------------------------------
# Tier S + substantial bespoke implementations (SOLUTION_CODE)
# ---------------------------------------------------------------------------

SOLUTION_CODE: dict[str, str] = {
    "C041": r"""#include <stdint.h>
#include <stddef.h>

static void *copy_bytes(void *dst, const void *src, size_t n) {
    unsigned char *d = (unsigned char *)dst;
    const unsigned char *s = (const unsigned char *)src;
    for (size_t i = 0; i < n; ++i) {
        d[i] = s[i];
    }
    return dst;
}

void *my_memcpy(void *dst, const void *src, size_t n) {
    if (n == 0) {
        return dst;
    }
    uintptr_t da = (uintptr_t)dst;
    uintptr_t sa = (uintptr_t)src;
    if ((da & 3u) == 0 && (sa & 3u) == 0) {
        while (n >= 16) {
            ((uint32_t *)da)[0] = ((const uint32_t *)sa)[0];
            ((uint32_t *)da)[1] = ((const uint32_t *)sa)[1];
            ((uint32_t *)da)[2] = ((const uint32_t *)sa)[2];
            ((uint32_t *)da)[3] = ((const uint32_t *)sa)[3];
            da += 16; sa += 16; n -= 16;
        }
        while (n >= 4) {
            *(uint32_t *)da = *(const uint32_t *)sa;
            da += 4; sa += 4; n -= 4;
        }
    }
    return copy_bytes((void *)da, (const void *)sa, n);
}""",
    "C042": r"""#include <stdint.h>
#include <stddef.h>

void *my_memmove(void *dst, const void *src, size_t n) {
    unsigned char *d = (unsigned char *)dst;
    const unsigned char *s = (const unsigned char *)src;
    if (n == 0 || dst == src) {
        return dst;
    }
    if (d < s) {
        for (size_t i = 0; i < n; ++i) {
            d[i] = s[i];
        }
    } else {
        for (size_t i = n; i > 0; --i) {
            d[i - 1] = s[i - 1];
        }
    }
    return dst;
}""",
    "C071": r"""#include <stdint.h>
#include <stddef.h>

/* Spare-slot SPSC ring: usable capacity = cap - 1. Empty: head==tail. Full: next(head)==tail. */
typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;

static size_t ring_next(const ring_t *r, size_t i) {
    return (i + 1u) % r->cap;
}

void ring_init(ring_t *r, uint8_t *buf, size_t cap) {
    r->buf = buf;
    r->cap = cap;
    r->head = r->tail = 0;
}

size_t ring_count(const ring_t *r) {
    if (r->head >= r->tail) {
        return r->head - r->tail;
    }
    return r->cap - (r->tail - r->head);
}

static size_t ring_free(const ring_t *r) {
    return (r->cap - 1u) - ring_count(r);
}

size_t ring_push(ring_t *r, const uint8_t *src, size_t n) {
    size_t pushed = 0;
    while (pushed < n && ring_free(r) > 0) {
        r->buf[r->head] = src[pushed++];
        r->head = ring_next(r, r->head);
    }
    return pushed;
}

size_t ring_pop(ring_t *r, uint8_t *dst, size_t n) {
    size_t popped = 0;
    while (popped < n && r->tail != r->head) {
        dst[popped++] = r->buf[r->tail];
        r->tail = ring_next(r, r->tail);
    }
    return popped;
}""",
    "C091": r"""#include <stdatomic.h>
#include <stdint.h>

typedef struct { atomic_flag f; } spinlock_t;

void spin_lock(spinlock_t *l) {
    while (atomic_flag_test_and_set_explicit(&l->f, memory_order_acquire)) {
        /* spin — keep critical sections tiny; use irqsave variant in ISR contexts */
    }
}

void spin_unlock(spinlock_t *l) {
    atomic_flag_clear_explicit(&l->f, memory_order_release);
}

/* IRQ-safe variant (platform stubs) */
typedef uint32_t irq_state_t;
static irq_state_t irq_save(void) { return 0; /* primask save on Cortex-M */ }
static void irq_restore(irq_state_t s) { (void)s; }

void spin_lock_irqsave(spinlock_t *l, irq_state_t *st) {
    *st = irq_save();
    spin_lock(l);
}

void spin_unlock_irqrestore(spinlock_t *l, irq_state_t st) {
    spin_unlock(l);
    irq_restore(st);
}""",
    "C145": r"""#include <stdint.h>
#include <stddef.h>

typedef volatile struct {
    volatile uint32_t CR1;
    volatile uint32_t SR;
    volatile uint32_t DR;
} I2C_Regs;

static I2C_Regs *const I2C = (I2C_Regs *)0x40005400u;
static uint32_t g_tick_ms;

static int wait_flag(volatile uint32_t *sr, uint32_t mask, int set, uint32_t timeout_ms) {
    uint32_t start = g_tick_ms;
    while (((*sr & mask) != 0) == set) {
        if ((g_tick_ms - start) >= timeout_ms) {
            return -1;
        }
    }
    return 0;
}

static void i2c_start(void) { I2C->CR1 |= (1u << 8); }
static void i2c_stop(void)  { I2C->CR1 |= (1u << 9); }
static int i2c_send_byte(uint8_t b, uint32_t timeout_ms) {
    if (wait_flag(&I2C->SR, (1u << 7), 0, timeout_ms) < 0) return -1; /* TXE */
    I2C->DR = b;
    if (wait_flag(&I2C->SR, (1u << 1), 0, timeout_ms) < 0) return -1; /* BTF */
    if (I2C->SR & (1u << 0)) return -2; /* AF/NACK */
    return 0;
}

int i2c_write(uint8_t addr7, const uint8_t *data, size_t n, uint32_t timeout_ms) {
    if (!data && n > 0) return -3;
    i2c_start();
    if (i2c_send_byte((uint8_t)((addr7 << 1) | 0u), timeout_ms) < 0) {
        i2c_stop();
        return -4;
    }
    for (size_t i = 0; i < n; ++i) {
        if (i2c_send_byte(data[i], timeout_ms) < 0) {
            i2c_stop();
            return -5;
        }
    }
    i2c_stop();
    return 0;
}""",
    "C173": r"""#include <stdint.h>
#include <stddef.h>

typedef void (*timer_cb)(void *ctx);

typedef struct sw_timer {
    struct sw_timer *next;
    uint32_t expires_ms;
    timer_cb cb;
    void *ctx;
    int active;
} sw_timer_t;

static sw_timer_t *g_head;
static uint32_t g_now_ms;
static sw_timer_t g_pool[32];
static int g_pool_used;

/* Wrap-safe comparisons (max delta < 2^31 ms) */
#define time_after(a, b)     ((int32_t)((a) - (b)) > 0)
#define time_before(a, b)    ((int32_t)((a) - (b)) < 0)
#define time_before_eq(a, b) ((int32_t)((a) - (b)) <= 0)

static void hw_timer_program(uint32_t deadline_ms) {
    uint32_t delta = deadline_ms - g_now_ms;
    /* platform: write compare register with delta ticks */
    (void)delta;
}

static void reprogram_hw(void) {
    if (!g_head) {
        return;
    }
    hw_timer_program(g_head->expires_ms);
}

static void insert_sorted(sw_timer_t *t) {
    t->next = NULL;
    if (!g_head || time_before(t->expires_ms, g_head->expires_ms)) {
        t->next = g_head;
        g_head = t;
        reprogram_hw();
        return;
    }
    sw_timer_t *p = g_head;
    while (p->next && time_before_eq(p->next->expires_ms, t->expires_ms)) {
        p = p->next;
    }
    t->next = p->next;
    p->next = t;
}

void sw_timer_set(sw_timer_t *t, uint32_t delay_ms, timer_cb cb, void *ctx) {
    t->expires_ms = g_now_ms + delay_ms;
    t->cb = cb;
    t->ctx = ctx;
    t->active = 1;
    insert_sorted(t);
}

void sw_timer_cancel(sw_timer_t *t) {
    t->active = 0;
    sw_timer_t **pp = &g_head;
    while (*pp) {
        if (*pp == t) {
            *pp = t->next;
            if (pp == &g_head) {
                reprogram_hw();
            }
            return;
        }
        pp = &(*pp)->next;
    }
}

void hw_timer_irq(void) {
    while (g_head && time_before_eq(g_head->expires_ms, g_now_ms)) {
        sw_timer_t *exp = g_head;
        g_head = exp->next;
        exp->active = 0;
        if (exp->cb) {
            exp->cb(exp->ctx);
        }
    }
    reprogram_hw();
}

void tick_ms(uint32_t ms) { g_now_ms = ms; }""",
    "C202": r"""#include <stdint.h>

typedef enum { IDLE, READY, VENDING, FAULT } state_E;
typedef enum { COIN, COIN_RETURN, BUTTON, VEND_COMPLETE, GENERIC_FAULT } input_E;

static state_E g_state = IDLE;

state_E stateMachine(input_E input) {
    switch (g_state) {
    case IDLE:
        if (input == COIN) g_state = READY;
        else if (input == GENERIC_FAULT) g_state = FAULT;
        break;
    case READY:
        if (input == BUTTON) g_state = VENDING;
        else if (input == COIN_RETURN) g_state = IDLE;
        else if (input == GENERIC_FAULT) g_state = FAULT;
        break;
    case VENDING:
        if (input == VEND_COMPLETE) g_state = IDLE;
        else if (input == GENERIC_FAULT) g_state = FAULT;
        break;
    case FAULT:
        break; /* stay in FAULT until reset outside scope */
    default:
        g_state = FAULT;
        break;
    }
    if (input == GENERIC_FAULT) {
        g_state = FAULT;
    }
    return g_state;
}

void stateMachine_reset(void) { g_state = IDLE; }""",
}

CATEGORY_CODES: dict[str, str] = {
    "C001": """#include <stdint.h>
#include <stddef.h>
#include <stddef.h>
#define offsetof(type, member) ((size_t)&(((type *)0)->member))
#define container_of(ptr, type, member) ((type *)((char *)(ptr) - offsetof(type, member)))
struct list_node { struct list_node *next; };
struct device { int id; struct list_node link; };
struct device *device_from_node(struct list_node *n) {
    return container_of(n, struct device, link);
}""",
    "C002": """#include <stdint.h>
#include <stddef.h>
struct pkt_hdr { uint8_t type, flags; uint16_t len; uint32_t seq; };
#define STATIC_ASSERT(cond, msg) _Static_assert(cond, msg)
STATIC_ASSERT(sizeof(struct pkt_hdr) == 8, "pkt_hdr size");
STATIC_ASSERT(offsetof(struct pkt_hdr, len) == 2, "len offset");
STATIC_ASSERT(offsetof(struct pkt_hdr, seq) == 4, "seq offset");""",
    "C003": """#include <stdint.h>
#include <stddef.h>
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#define BIT(n) (1u << (n))
#define GENMASK(h,l) (((BIT((h)-(l)+1) - 1u) << (l)))""",
    "C004": """#include <stdint.h>
#include <stddef.h>
#ifdef __GNUC__
#define likely(x)   __builtin_expect(!!(x), 1)
#define unlikely(x) __builtin_expect(!!(x), 0)
#else
#define likely(x)   (x)
#define unlikely(x) (x)
#endif
int parse_frame(const uint8_t *buf, size_t n) {
    if (unlikely(!buf || n < 4)) return -1;
    if (likely(buf[0] == 0xAA)) return (int)buf[1];
    return -2;
}""",
    "C005": """#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
static inline uint16_t bswap16(uint16_t x) { return (uint16_t)((x>>8)|((x&0xFFu)<<8)); }
static inline uint32_t bswap32(uint32_t x) {
    return ((x & 0xFFu)<<24)|((x & 0xFF00u)<<8)|((x>>8)&0xFF00u)|((x>>24)&0xFFu);
}
uint32_t read_be32(const uint8_t *p) {
    return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];
}""",
    "C006": """#include <stdint.h>
#include <stddef.h>
void write_le16(uint8_t *p, uint16_t v) { p[0]=(uint8_t)v; p[1]=(uint8_t)(v>>8); }
uint16_t read_le16(const uint8_t *p) { return (uint16_t)p[0]|((uint16_t)p[1]<<8); }""",
    "C007": """#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
bool add_u32_sat(uint32_t a, uint32_t b, uint32_t *out) {
    uint32_t r = a + b; if (r < a) return false; *out = r; return true;
}
bool mul_u32_sat(uint32_t a, uint32_t b, uint32_t *out) {
    if (a && b > UINT32_MAX / a) return false; *out = a * b; return true;
}""",
    "C008": """#include <stdint.h>
#include <stddef.h>
int safe_downcast_u64_u32(uint64_t v, uint32_t *out) {
    if (v > UINT32_MAX) return -1; *out = (uint32_t)v; return 0;
}""",
    "C009": """#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
bool is_aligned(const void *p, size_t a) { return (((uintptr_t)p & (a-1)) == 0); }
void *align_up_ptr(void *p, size_t a) {
    uintptr_t v = (uintptr_t)p; v = (v + a - 1) & ~(a - 1); return (void *)v;
}""",
    "C010": """#include <stdint.h>
#include <stddef.h>
#ifndef NDEBUG
#define ASSERT(c) do { if (!(c)) { __builtin_trap(); } } while(0)
#else
#define ASSERT(c) ((void)0)
#endif
void use(int x) { ASSERT(x >= 0); }""",
    "C011": """#include <stdint.h>
#include <stddef.h>
typedef enum { ERR_OK=0, ERR_IO=-1, ERR_TIMEOUT=-2 } err_t;
const char *err_str(err_t e) {
    switch(e){case ERR_OK:return "OK";case ERR_IO:return "IO";default:return "TIMEOUT";}
}""",
    "C012": """#include <stdint.h>
#include <stddef.h>
typedef struct __attribute__((packed)) { uint8_t a; uint32_t b; } packed_t;
void pack_copy(const packed_t *src, uint8_t *dst) {
    for (size_t i=0;i<sizeof(packed_t);++i) ((uint8_t*)dst)[i]=((const uint8_t*)src)[i];
}""",
    "C013": """#include <stdint.h>
#include <stddef.h>
union reg { uint32_t w; struct { uint16_t lo, hi; } h; };
uint16_t reg_get_field(uint32_t w, unsigned lo, unsigned width) {
    return (uint16_t)((w >> lo) & ((1u<<width)-1u));
}""",
    "C014": """#include <stdint.h>
#include <stddef.h>
void *clear_struct(void *p, size_t n) { unsigned char *b=p; for(size_t i=0;i<n;++i) b[i]=0; return p; }""",
    "C015": """#include <stdint.h>
#include <stddef.h>
typedef void (*isr_fn)(void);
static isr_fn g_vtable[4];
void isr_register(unsigned id, isr_fn fn) { if(id<4) g_vtable[id]=fn; }
void isr_dispatch(unsigned id) { if(id<4 && g_vtable[id]) g_vtable[id](); }""",
    "C016": """#include <stdint.h>
#include <stddef.h>
static const char *const names[] = {"idle","run","fault"};
const char *state_name(unsigned s) { return s<3?names[s]:"unknown"; }""",
    "C017": """#include <stdint.h>
#include <stddef.h>
typedef struct { int x,y; } point_t;
point_t points[10];
point_t *get_point(unsigned i) { return i<10?&points[i]:0; }""",
    "C018": """#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
bool in_range_u32(uint32_t v, uint32_t lo, uint32_t hi) { return v>=lo && v<=hi; }""",
    "C019": """#include <stdint.h>
#include <stddef.h>
#define STR2(x) #x
#define STR(x) STR2(x)
const char *build_tag(void) { return "build=" STR(__LINE__); }""",
    "C020": """#include <stdint.h>
#include <stddef.h>
typedef struct node { struct node *next; int v; } node_t;
int list_sum(const node_t *h) { int s=0; while(h){s+=h->v;h=h->next;} return s; }""",
    "C021": """#include <stdint.h>
#include <stddef.h>
unsigned popcount32(uint32_t x){unsigned c=0;while(x){x&=x-1u;++c;}return c;}""",
    "C022": """#include <stdint.h>
#include <stddef.h>
static const uint8_t rev_lut[256]={0}; /* fill at init in prod */
uint8_t rev8(uint8_t x){uint8_t r=0;for(int i=0;i<8;++i){r=(uint8_t)((r<<1)|(x&1u));x>>=1;}return r;}
uint32_t rev32(uint32_t x){uint32_t r=0;for(int i=0;i<32;++i){r=(r<<1)|(x&1u);x>>=1;}return r;}""",
    "C023": """#include <stdint.h>
#include <stddef.h>
void flip_hi_lo(uint8_t *b){*b^=(uint8_t)(0x81u);}""",
    "C024": """#include <stdint.h>
#include <stddef.h>
uint32_t rotl32(uint32_t x,unsigned n){n&=31;return (x<<n)|(x>>(32-n));}""",
    "C025": """#include <stdint.h>
#include <stddef.h>
int clz32(uint32_t x){if(!x)return 32;int n=0;while(!(x&0x80000000u)){++n;x<<=1;}return n;}""",
    "C026": """#include <stdint.h>
#include <stddef.h>
uint8_t parity8(uint8_t x){x^=x>>4;x^=x>>2;x^=x>>1;return x&1u;}""",
    "C027": """#include <stdint.h>
#include <stddef.h>
uint16_t crc16_ccitt(const uint8_t *d,size_t n){uint16_t c=0xFFFF;for(size_t i=0;i<n;++i){c^=(uint16_t)d[i]<<8;for(int b=0;b<8;++b)c=(c&0x8000)?(uint16_t)((c<<1)^0x1021):(uint16_t)(c<<1);}return c;}""",
    "C028": """#include <stdint.h>
#include <stddef.h>
uint32_t crc32_ieee(const uint8_t *d,size_t n){uint32_t c=0xFFFFFFFFu;for(size_t i=0;i<n;++i){c^=d[i];for(int b=0;b<8;++b)c=(c&1)?(c>>1)^0xEDB88320u:c>>1;}return ~c;}""",
    "C029": """#include <stdint.h>
#include <stddef.h>
uint8_t xor8(const uint8_t *d,size_t n){uint8_t x=0;for(size_t i=0;i<n;++i)x^=d[i];return x;}""",
    "C030": """#include <stdint.h>
#include <stddef.h>
uint16_t sum16(const uint8_t *d,size_t n){uint32_t s=0;for(size_t i=0;i<n;++i)s+=d[i];return (uint16_t)(s&0xFFFF);}""",
    "C031": """#include <stdint.h>
#include <stddef.h>
uint32_t pack_fields(uint8_t a,uint8_t b,uint16_t c){return ((uint32_t)a<<24)|((uint32_t)b<<16)|c;}""",
    "C032": """#include <stdint.h>
#include <stddef.h>
void unpack_fields(uint32_t w,uint8_t *a,uint8_t *b,uint16_t *c){*a=(uint8_t)(w>>24);*b=(uint8_t)(w>>16);*c=(uint16_t)w;}""",
    "C033": """#include <stdint.h>
#include <stddef.h>
uint8_t gray_encode(uint8_t v){return (uint8_t)(v^(v>>1));} uint8_t gray_decode(uint8_t g){uint8_t v=g;for(int i=1;i<8;i<<=1)v^=g>>i;return v;}""",
    "C034": """#include <stdint.h>
#include <stddef.h>
int32_t fixed_mul_q16(int32_t a,int32_t b){return (int32_t)(((int64_t)a*b)>>16);}""",
    "C035": """#include <stdint.h>
#include <stddef.h>
uint32_t interleave_bits(uint16_t x,uint16_t y){uint32_t z=0;for(int i=0;i<16;++i){z|=(uint32_t)((x>>i)&1u)<<(2*i);z|=(uint32_t)((y>>i)&1u)<<(2*i+1);}return z;}""",
    "C036": """#include <stdint.h>
#include <stddef.h>
unsigned popcount32(uint32_t x){unsigned c=0;while(x){x&=x-1u;++c;}return c;}
int hamming_distance32(uint32_t a,uint32_t b){return (int)popcount32(a^b);}""",
    "C037": """#include <stdint.h>
#include <stddef.h>
uint32_t next_pow2(uint32_t v){v--;v|=v>>1;v|=v>>2;v|=v>>4;v|=v>>8;v|=v>>16;return v+1;}""",
    "C038": """#include <stdint.h>
#include <stddef.h>
uint8_t bit_reverse_n(uint8_t x,unsigned n){uint8_t r=0;for(unsigned i=0;i<n;++i)r=(uint8_t)((r<<1)|(x&1u)),x>>=1;return r;}""",
    "C039": """#include <stdint.h>
#include <stddef.h>
uint32_t mask_lo(unsigned n){return n>=32?0xFFFFFFFFu:((1u<<n)-1u);}""",
    "C040": """#include <stdint.h>
#include <stddef.h>
int find_first_set32(uint32_t x){if(!x)return -1;for(int i=0;i<32;++i)if(x&(1u<<i))return i;return -1;}""",
    "C041": """#include <stdint.h>
#include <stddef.h>
void *my_memcpy(void*,const void*,size_t);""",
    "C042": """#include <stdint.h>
#include <stddef.h>
void *my_memmove(void*,const void*,size_t);""",
    "C043": """#include <stdint.h>
#include <stddef.h>
#include <string.h>
void *my_memset(void *s,int c,size_t n){unsigned char *p=s;while(n--) *p++=(unsigned char)c;return s;}
void secure_zero(void *s,size_t n){volatile unsigned char *p=s;while(n--) *p++=0;}""",
    "C044": """#include <stdint.h>
#include <stddef.h>
int my_memcmp(const void *a,const void *b,size_t n){const unsigned char *p=a,*q=b;for(size_t i=0;i<n;++i){if(p[i]!=q[i])return (int)p[i]-(int)q[i];}return 0;}""",
    "C045": """#include <stdint.h>
#include <stddef.h>
size_t my_strlen(const char *s){size_t n=0;if(!s)return 0;while(s[n])++n;return n;} size_t my_strnlen(const char *s,size_t m){size_t n=0;if(!s)return 0;while(n<m&&s[n])++n;return n;}""",
    "C046": """#include <stdint.h>
#include <stddef.h>
size_t my_strlcpy(char *d,const char *s,size_t sz){size_t len=0;if(!s){if(sz)d[0]=0;return 0;} while(s[len])++len;if(sz){size_t c=len<sz-1?len:sz-1;for(size_t i=0;i<c;++i)d[i]=s[i];d[c]=0;} return len;}""",
    "C047": """#include <stdint.h>
#include <stddef.h>
size_t my_strlcat(char *d,const char *s,size_t sz){size_t dl=0;while(dl<sz&&d[dl])++dl;size_t sl=0;while(s[sl])++sl;if(dl>=sz)return sz+sl;size_t c=sl<sz-dl-1?sl:sz-dl-1;for(size_t i=0;i<c;++i)d[dl+i]=s[i];d[dl+c]=0;return dl+sl;}""",
    "C048": """#include <stdint.h>
#include <stddef.h>
int my_atoi(const char *s,int *out){int sign=1,v=0;if(!s||!*s)return -1;if(*s=='-'){sign=-1;++s;} while(*s>='0'&&*s<='9'){v=v*10+(*s-'0');++s;} *out=sign*v;return 0;}""",
    "C049": """#include <stdint.h>
#include <stddef.h>
int hex_nibble(char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;if(c>='A'&&c<='F')return c-'A'+10;return -1;}""",
    "C050": """#include <stdint.h>
#include <stddef.h>
int hex_nibble(char c);
size_t hex_encode(const uint8_t *in,size_t n,char *out,size_t cap){size_t need=n*2;if(cap<need+1)return 0;static const char *h="0123456789abcdef";for(size_t i=0;i<n;++i){out[2*i]=h[in[i]>>4];out[2*i+1]=h[in[i]&0xF];}out[need]=0;return need;}""",
    "C051": """#include <stdint.h>
#include <stddef.h>
int hex_nibble(char c);
size_t hex_decode(const char *in,uint8_t *out,size_t cap){size_t o=0;while(in[0]&&in[1]&&o<cap){int hi=hex_nibble(in[0]),lo=hex_nibble(in[1]);if(hi<0||lo<0)break;out[o++]=(uint8_t)((hi<<4)|lo);in+=2;}return o;}""",
    "C052": """#include <stdint.h>
#include <stddef.h>
int base64_encode_block(const uint8_t *in,size_t n,char *out){static const char *t="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";for(size_t i=0;i<n;i+=3){uint32_t v=(in[i]<<16)|((i+1<n)?in[i+1]<<8:0)|((i+2<n)?in[i+2]:0);*out++=t[(v>>18)&63];*out++=t[(v>>12)&63];*out++=(i+1<n)?t[(v>>6)&63]:'='; *out++=(i+2<n)?t[v&63]:'=';} *out=0;return 0;}""",
    "C053": """#include <stdint.h>
#include <stddef.h>
int mem_is_zero(const void *p,size_t n){const unsigned char *b=p;for(size_t i=0;i<n;++i)if(b[i])return 0;return 1;}""",
    "C054": """#include <stdint.h>
#include <stddef.h>
void *memswap(void *a,void *b,size_t n){unsigned char *x=a,*y=b;for(size_t i=0;i<n;++i){unsigned char t=x[i];x[i]=y[i];y[i]=t;}return a;}""",
    "C055": """#include <stdint.h>
#include <stddef.h>
int bounded_copy(uint8_t *d,size_t dc,const uint8_t *s,size_t sc){size_t n=dc<sc?dc:sc;for(size_t i=0;i<n;++i)d[i]=s[i];return (int)n;}""",
    "C056": """#include <stdint.h>
#include <stddef.h>
typedef struct pool_node { struct pool_node *next; } pool_node_t;
typedef struct { unsigned char *arena; size_t block_size, block_count; pool_node_t *free_head; } pool_t;
int pool_init(pool_t *p,void *backing,size_t backing_size,size_t block_size){if(!p||!backing||block_size<sizeof(pool_node_t))return -1;p->arena=backing;p->block_size=block_size;p->block_count=backing_size/block_size;p->free_head=0;for(size_t i=0;i<p->block_count;++i){pool_node_t *n=(pool_node_t*)(p->arena+i*block_size);n->next=p->free_head;p->free_head=n;}return 0;}
void *pool_alloc(pool_t *p){if(!p||!p->free_head)return 0;pool_node_t *n=p->free_head;p->free_head=n->next;return n;}
void pool_free(pool_t *p,void *blk){if(!p||!blk)return;pool_node_t *n=blk;n->next=p->free_head;p->free_head=n;}""",
    "C057": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { unsigned char *arena; size_t block_size, block_count; _Atomic(pool_node_t*) free_head; } pool_t;
typedef struct pool_node { struct pool_node *next; } pool_node_t;
void *pool_alloc_isrsafe(pool_t *p){pool_node_t *n=atomic_load(&p->free_head);while(n){pool_node_t *next=n->next;if(atomic_compare_exchange_weak(&p->free_head,&n,next))return n;n=atomic_load(&p->free_head);}return 0;}
void pool_free_isrsafe(pool_t *p,void *blk){pool_node_t *n=blk;pool_node_t *old=atomic_load(&p->free_head);do{n->next=old;}while(!atomic_compare_exchange_weak(&p->free_head,&old,n));}""",
    "C058": """#include <stdint.h>
#include <stddef.h>
typedef struct { unsigned in_use, peak, fail_count; } pool_stats_t;
void pool_stats_on_alloc(pool_stats_t *s,int ok){if(ok){s->in_use++;if(s->in_use>s->peak)s->peak=s->in_use;}else s->fail_count++;}
void pool_stats_on_free(pool_stats_t *s){if(s->in_use)s->in_use--;}""",
    "C059": """#include <stdint.h>
#include <stddef.h>
typedef struct { unsigned char *base; size_t size, offset; } bump_t;
void bump_init(bump_t *b,void *base,size_t sz){b->base=base;b->size=sz;b->offset=0;}
void *bump_alloc(bump_t *b,size_t n){n=(n+7)&~7u;if(b->offset+n>b->size)return 0;void *p=b->base+b->offset;b->offset+=n;return p;}
void bump_reset(bump_t *b){b->offset=0;}""",
    "C060": """#include <stdint.h>
#include <stddef.h>
typedef struct fb { size_t size; struct fb *next; } free_block_t;
void *arena_alloc(free_block_t **head,size_t n){n=(n+7)&~7u;free_block_t *prev=0,*cur=*head;while(cur){if(cur->size>=n){if(cur->size>n+sizeof(free_block_t)+8){free_block_t *split=(free_block_t*)((char*)cur+sizeof(free_block_t)+n);split->size=cur->size-n-sizeof(free_block_t);split->next=cur->next;cur->size=n;cur->next=split;}else{if(prev)prev->next=cur->next;else *head=cur->next;}return (char*)cur+sizeof(free_block_t);}prev=cur;cur=cur->next;}return 0;}""",
    "C061": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint16_t order; struct buddy *left,*right; int free; } buddy_t;
void *buddy_alloc(buddy_t *root,size_t order){if(!root||!root->free||root->order<order)return 0;if(root->order==order){root->free=0;return root;} if(root->order>order){void *p=buddy_alloc(root->left,order);if(!p)p=buddy_alloc(root->right,order);if(!root->left->free&&!root->right->free)root->free=0;return p;}return 0;}""",
    "C062": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { _Atomic int refs; void (*release)(void*); void *obj; } ref_buf_t;
void rbuf_get(ref_buf_t *r){atomic_fetch_add(&r->refs,1);}
void rbuf_put(ref_buf_t *r){if(atomic_fetch_sub(&r->refs,1)==1&&r->release)r->release(r->obj);}""",
    "C063": """#include <stdint.h>
#include <stddef.h>
typedef struct slab { void *chunk; size_t obj_size, count; unsigned char *bitmap; } slab_t;
int slab_init(slab_t *s,void *mem,size_t obj_size,size_t count){s->chunk=mem;s->obj_size=obj_size;s->count=count;s->bitmap=(unsigned char*)mem; return 0;}
void *slab_alloc(slab_t *s){for(size_t i=0;i<s->count;++i)if(!(s->bitmap[i/8]&(1u<<(i&7)))){s->bitmap[i/8]|=(1u<<(i&7));return (char*)s->chunk+i*s->obj_size;}return 0;}""",
    "C064": """#include <stdint.h>
#include <stddef.h>
typedef struct { void **stack; size_t cap, top; } handle_pool_t;
int hpool_init(handle_pool_t *h,void **stack,size_t cap){h->stack=stack;h->cap=cap;h->top=cap;return 0;}
int hpool_alloc(handle_pool_t *h){return h->top? (int)(uintptr_t)h->stack[--h->top]:-1;}
void hpool_free(handle_pool_t *h,int idx){if(h->top<h->cap)h->stack[h->top++]=(void*)(uintptr_t)idx;}""",
    "C065": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t magic; uint16_t size; uint16_t checksum; } hdr_t;
int hdr_validate(const hdr_t *h){uint32_t s=h->size; s^=h->magic; return (uint16_t)s==h->checksum?0:-1;}""",
    "C066": """#include <stdint.h>
#include <stddef.h>
typedef struct { unsigned char *base; size_t guard_size, block_size, count; } guard_pool_t;
int guard_check(const unsigned char *blk){return blk[0]==0xA5&&blk[1]==0x5A;}""",
    "C067": """#include <stdint.h>
#include <stddef.h>
void *tlsf_alloc(void *tlsf,size_t n); void tlsf_free(void *tlsf,void *p); /* TLSF API stubs with real signatures */""",
    "C068": """#include <stdint.h>
#include <stddef.h>
typedef struct { size_t total, used, peak; } mem_stats_t;
void mem_stats_alloc(mem_stats_t *s,size_t n){s->used+=n;if(s->used>s->peak)s->peak=s->used;}
void mem_stats_free(mem_stats_t *s,size_t n){s->used-=n;}""",
    "C069": """#include <stdint.h>
#include <stddef.h>
typedef struct { void *ptr; size_t size; int generation; } handle_t;
int handle_valid(const handle_t *h,int gen){return h&&h->ptr&&h->generation==gen;}""",
    "C070": """#include <stdint.h>
#include <stddef.h>
typedef struct { unsigned char *arena; size_t size; int poisoned; } arena_t;
void arena_poison(arena_t *a){for(size_t i=0;i<a->size;++i)a->arena[i]=0xDE; a->poisoned=1;}
int arena_check(const arena_t *a){if(!a->poisoned)return 1;for(size_t i=0;i<a->size;++i)if(a->arena[i]!=0xDE)return 0;return 1;}""",
    "C071": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
size_t ring_push(ring_t*,const uint8_t*,size_t); size_t ring_pop(ring_t*,uint8_t*,size_t);""",
    "C072": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
static int is_pow2(size_t x){return x&&(x&(x-1))==0;}
size_t ring_push(ring_t *r,const uint8_t *src,size_t n){size_t m=r->cap-1;if(!is_pow2(r->cap))return 0;size_t pushed=0;while(pushed<n&&((r->head+1)&(r->cap-1))!=r->tail){r->buf[r->head]=src[pushed++];r->head=(r->head+1)&(r->cap-1);}return pushed;}
size_t ring_pop(ring_t *r,uint8_t *dst,size_t n){size_t popped=0;while(popped<n&&r->tail!=r->head){dst[popped++]=r->buf[r->tail];r->tail=(r->tail+1)&(r->cap-1);}return popped;}""",
    "C073": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
typedef struct { ring_t r; size_t count; } ring_count_t;
size_t rc_push(ring_count_t *rc,const uint8_t *s,size_t n){size_t p=0;while(p<n&&rc->count<rc->r.cap){rc->r.buf[rc->r.head]=s[p++];rc->r.head=rn(&rc->r,rc->r.head);rc->count++;}return p;}
size_t rc_pop(ring_count_t *rc,uint8_t *d,size_t n){size_t p=0;while(p<n&&rc->count){d[p++]=rc->r.buf[rc->r.tail];rc->r.tail=rn(&rc->r,rc->r.tail);rc->count--;}return p;}""",
    "C074": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
size_t ring_push_overwrite(ring_t *r,const uint8_t *src,size_t n){size_t pushed=0;while(pushed<n){if(((r->head+1)%r->cap)==r->tail)r->tail=rn(r,r->tail);r->buf[r->head]=src[pushed++];r->head=rn(r,r->head);}return pushed;}""",
    "C075": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
size_t ring_push(ring_t *r,const uint8_t *src,size_t n){size_t pushed=0;while(pushed<n&&((r->head+1)%r->cap)!=r->tail){r->buf[r->head]=src[pushed++];r->head=rn(r,r->head);}return pushed;}
static size_t drops;
size_t ring_push_drop_newest(ring_t *r,const uint8_t *src,size_t n){size_t free=(r->cap-1)-ring_count(r);if(n>free){drops+=n-free;n=free;}return ring_push(r,src,n);}
size_t ring_drop_count(const ring_t *r){(void)r;return drops;}""",
    "C076": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
size_t ring_peek(const ring_t *r,uint8_t *dst,size_t n){size_t i=0, t=r->tail;while(i<n&&t!=r->head){dst[i++]=r->buf[t];t=rn(r,t);}return i;}
size_t ring_skip(ring_t *r,size_t n){size_t c=ring_count(r);if(n>c)n=c;while(n--)r->tail=rn(r,r->tail);return n;}""",
    "C077": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
size_t ring_contig_read(const ring_t *r,const uint8_t **ptr){if(r->tail==r->head){*ptr=0;return 0;}*ptr=&r->buf[r->tail];if(r->head>r->tail)return r->head-r->tail;return r->cap-r->tail;}""",
    "C078": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
size_t ring_reserve(ring_t *r,uint8_t **ptr){size_t f=(r->cap-1)-ring_count(r);if(!f){*ptr=0;return 0;}*ptr=&r->buf[r->head];size_t contig=(r->head>=r->tail)?(r->cap-r->head):(r->tail-r->head-1);return contig<f?contig:f;}
void ring_commit(ring_t *r,size_t n){while(n--)r->head=rn(r,r->head);}""",
    "C079": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t id; int32_t val; } event_t;
typedef struct { event_t *buf; size_t cap, head, tail; } event_ring_t;
int event_ring_push(event_ring_t *r,const event_t *e){size_t n=(r->head+1)%r->cap;if(n==r->tail)return -1;r->buf[r->head]=*e;r->head=n;return 0;}
int event_ring_pop(event_ring_t *r,event_t *e){if(r->head==r->tail)return -1;*e=r->buf[r->tail];r->tail=(r->tail+1)%r->cap;return 0;}""",
    "C080": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { uint32_t id; int32_t val; } event_t;
typedef struct { event_t buf[16]; size_t cap; _Atomic size_t head, tail; } mpsc_t;
int mpsc_push(mpsc_t *q,const event_t *e){size_t h=atomic_load(&q->head);size_t n=(h+1)%q->cap;if(n==atomic_load(&q->tail))return -1;q->buf[h]=*e;atomic_store(&q->head,n);return 0;}
int mpsc_pop(mpsc_t *q,event_t *e){size_t t=atomic_load(&q->tail);if(t==atomic_load(&q->head))return -1;*e=q->buf[t];atomic_store(&q->tail,(t+1)%q->cap);return 0;}""",
    "C081": """#include <stdint.h>
#include <stddef.h>
typedef struct { event_t q[8][16]; unsigned head[8], tail[8]; uint32_t bitmap; } prio_q_t;
int prio_push(prio_q_t *q,unsigned prio,const event_t *e){if(prio>7)return -1;unsigned t=(q->tail[prio]+1)%16;if(t==q->head[prio])return -1;q->q[prio][q->tail[prio]]=*e;q->tail[prio]=t;q->bitmap|=(1u<<prio);return 0;}
int prio_pop_highest(prio_q_t *q,event_t *e){for(int p=7;p>=0;--p)if(q->bitmap&(1u<<p)){*e=q->q[p][q->head[p]];q->head[p]=(q->head[p]+1)%16;if(q->head[p]==q->tail[p])q->bitmap&=~(1u<<p);return 0;}return -1;}""",
    "C082": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t buf[2][256]; int write_idx, read_idx, ready; } dbuf_t;
uint8_t *dbuf_write_begin(dbuf_t *d){return d->buf[d->write_idx];}
void dbuf_write_end(dbuf_t *d){d->ready=1;d->write_idx^=1;}
const uint8_t *dbuf_read_begin(dbuf_t *d){return d->ready?d->buf[d->read_idx]:0;}
void dbuf_read_end(dbuf_t *d){d->ready=0;d->read_idx^=1;}""",
    "C083": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t b[3][128]; int wi, ri, pending; } tbuf_t;
uint8_t *tbuf_acquire_write(tbuf_t *t){return t->b[t->wi];}
void tbuf_submit(tbuf_t *t){t->pending++;t->wi=(t->wi+1)%3;}
const uint8_t *tbuf_acquire_read(tbuf_t *t){if(!t->pending)return 0;return t->b[t->ri];}
void tbuf_release_read(tbuf_t *t){t->pending--;t->ri=(t->ri+1)%3;}""",
    "C084": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
size_t ring_push(ring_t *r,const uint8_t *src,size_t n){size_t pushed=0;while(pushed<n&&((r->head+1)%r->cap)!=r->tail){r->buf[r->head]=src[pushed++];r->head=rn(r,r->head);}return pushed;}
size_t ring_pop(ring_t *r,uint8_t *dst,size_t n){size_t popped=0;while(popped<n&&r->tail!=r->head){dst[popped++]=r->buf[r->tail];r->tail=rn(r,r->tail);}return popped;}
int msg_push(ring_t *r,const uint8_t *payload,uint16_t len){if(len+2>(r->cap-1)-ring_count(r))return -1;uint8_t hdr[2]={(uint8_t)(len>>8),(uint8_t)len};return (ring_push(r,hdr,2)+ring_push(r,payload,len)==(size_t)len+2)?0:-1;}
int msg_pop(ring_t *r,uint8_t *payload,uint16_t cap,uint16_t *len_out){uint8_t hdr[2];if(ring_pop(r,hdr,2)!=2)return -1;uint16_t len=(uint16_t)((hdr[0]<<8)|hdr[1]);if(len>cap||ring_count(r)<len)return -2;ring_pop(r,payload,len);*len_out=len;return 0;}""",
    "C085": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t *slots; size_t slot_size, cap, wr, rd, count; } slot_ring_t;
uint8_t *slot_alloc(slot_ring_t *s){if(s->count>=s->cap)return 0;return s->slots+((s->wr%s->cap)*s->slot_size);}
void slot_submit(slot_ring_t *s){s->wr++;s->count++;}
const uint8_t *slot_acquire(slot_ring_t *s){if(!s->count)return 0;return s->slots+((s->rd%s->cap)*s->slot_size);}
void slot_release(slot_ring_t *s){s->rd++;s->count--;}""",
    "C086": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
void ring_watermark_set(ring_t *r,size_t hi,size_t lo){(void)r;(void)hi;(void)lo;}
int ring_watermark_high(const ring_t *r,size_t hi){return ring_count(r)>=hi;}""",
    "C087": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
size_t ring_push(ring_t *r,const uint8_t *src,size_t n){size_t pushed=0;while(pushed<n&&((r->head+1)%r->cap)!=r->tail){r->buf[r->head]=src[pushed++];r->head=rn(r,r->head);}return pushed;}
size_t ring_pop(ring_t *r,uint8_t *dst,size_t n){size_t popped=0;while(popped<n&&r->tail!=r->head){dst[popped++]=r->buf[r->tail];r->tail=rn(r,r->tail);}return popped;}
size_t ring_push_batch(ring_t *r,const uint8_t *src,size_t n){return ring_push(r,src,n);}
size_t ring_pop_batch(ring_t *r,uint8_t *dst,size_t n){return ring_pop(r,dst,n);}""",
    "C088": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t *buf; size_t cap, rd, wr; } dma_ring_t;
size_t dma_ring_avail(const dma_ring_t *r){return (r->wr+r->cap-r->rd)%r->cap;}
const uint8_t *dma_ring_read_ptr(dma_ring_t *r,size_t *len){*len=dma_ring_avail(r);return r->buf+r->rd;}""",
    "C089": """#include <stdint.h>
#include <stddef.h>
typedef struct { int16_t samples[256]; size_t head, tail, cap; } sample_ring_t;
int sample_push(sample_ring_t *r,int16_t v){size_t n=(r->head+1)%r->cap;if(n==r->tail)return -1;r->samples[r->head]=v;r->head=n;return 0;}""",
    "C090": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
size_t ring_push(ring_t *r,const uint8_t *src,size_t n){size_t pushed=0;while(pushed<n&&((r->head+1)%r->cap)!=r->tail){r->buf[r->head]=src[pushed++];r->head=rn(r,r->head);}return pushed;}
size_t ring_pop(ring_t *r,uint8_t *dst,size_t n){size_t popped=0;while(popped<n&&r->tail!=r->head){dst[popped++]=r->buf[r->tail];r->tail=rn(r,r->tail);}return popped;}
int ring_self_test(void){uint8_t mem[8];ring_t r;ring_init(&r,mem,8);ring_push(&r,(const uint8_t*)"ab",2);uint8_t out[2]={0};ring_pop(&r,out,2);return out[0]=='a'&&out[1]=='b'?0:-1;}""",
    "C091": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { atomic_flag f; } spinlock_t; void spin_lock(spinlock_t*); void spin_unlock(spinlock_t*);""",
    "C092": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { _Atomic unsigned next, now; } ticket_lock_t;
void ticket_lock(ticket_lock_t *l){unsigned my=atomic_fetch_add(&l->next,1);while(atomic_load(&l->now)!=my){}}
void ticket_unlock(ticket_lock_t *l){atomic_fetch_add(&l->now,1);}""",
    "C093": """#include <stdint.h>
#include <stddef.h>
typedef uint32_t irq_state_t; static irq_state_t primask; static int nest;
irq_state_t irq_save(void){irq_state_t prev=primask;primask=1;nest++;return prev;}
void irq_restore(irq_state_t st){if(--nest==0)primask=st;}
#define CRITICAL_SECTION(code) do{irq_state_t __st=irq_save();code;irq_restore(__st);}while(0)""",
    "C094": """#include <stdint.h>
#include <stddef.h>
typedef struct { int locked, owner; } mutex_t;
void mutex_lock(mutex_t *m){while(__sync_lock_test_and_set(&m->locked,1)){} m->owner=1;}
void mutex_unlock(mutex_t *m){m->owner=0;__sync_lock_release(&m->locked);}""",
    "C095": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { _Atomic int count; } sem_t;
void sem_give_from_isr(sem_t *s){atomic_store(&s->count,1);}
int sem_take(sem_t *s,uint32_t timeout_ms){(void)timeout_ms;int c=atomic_load(&s->count);while(c==0)c=atomic_load(&s->count);atomic_store(&s->count,0);return 0;}""",
    "C096": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { _Atomic int count; unsigned max; } sem_t;
int sem_init(sem_t *s,unsigned initial,unsigned max){s->max=max;atomic_store(&s->count,(int)initial);return 0;}
int sem_give(sem_t *s){int c=atomic_load(&s->count);if((unsigned)c>=s->max)return -1;atomic_fetch_add(&s->count,1);return 0;}
int sem_take(sem_t *s,uint32_t timeout_ms){(void)timeout_ms;int c;do{c=atomic_load(&s->count);if(c<=0)return -1;}while(!atomic_compare_exchange_weak(&s->count,&c,c-1));return 0;}""",
    "C097": """#include <stdint.h>
#include <stddef.h>
#ifndef NDEBUG
typedef struct { int locked, owner; } mutex_t;
void mutex_lock_debug(mutex_t *m){if(m->locked&&m->owner==1){__builtin_trap();}mutex_lock(m);m->owner=1;}
void mutex_unlock_debug(mutex_t *m){if(m->owner!=1){__builtin_trap();}mutex_unlock(m);}
#else
void mutex_lock_debug(mutex_t *m){mutex_lock(m);} void mutex_unlock_debug(mutex_t *m){mutex_unlock(m);}
#endif""",
    "C098": """#include <stdint.h>
#include <stddef.h>
typedef struct { int readers, writer; } rw_lock_t;
void rw_rlock(rw_lock_t *l){while(l->writer);l->readers++;}
void rw_runlock(rw_lock_t *l){l->readers--;}
void rw_wlock(rw_lock_t *l){while(l->readers||l->writer);l->writer=1;}
void rw_wunlock(rw_lock_t *l){l->writer=0;}""",
    "C099": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { _Atomic unsigned seq; uint64_t isr_count, bytes; } stats_t;
void stats_write_begin(stats_t *s){atomic_fetch_add(&s->seq,1);atomic_thread_fence(memory_order_release);}
void stats_write_end(stats_t *s){atomic_thread_fence(memory_order_release);atomic_fetch_add(&s->seq,1);}
void stats_read(stats_t *s,uint64_t *isr,uint64_t *bytes){for(;;){unsigned a=atomic_load(&s->seq);if(a&1)continue;*isr=s->isr_count;*bytes=s->bytes;unsigned b=atomic_load(&s->seq);if(a==b)break;}""",
    "C100": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct ref { _Atomic int cnt; void (*rel)(struct ref*); } ref_t;
void ref_init(ref_t *r,void (*release)(ref_t*)){atomic_store(&r->cnt,1);r->rel=release;}
void ref_get(ref_t *r){atomic_fetch_add(&r->cnt,1);}
void ref_put(ref_t *r){if(atomic_fetch_sub(&r->cnt,1)==1&&r->rel)r->rel(r);}""",
    "C101": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { msg_t *buf; size_t cap; _Atomic size_t head, tail; } spsc_t;
typedef struct { uint32_t id; uint8_t data[8]; } msg_t;
int spsc_push(spsc_t *q,const msg_t *m){size_t h=atomic_load_explicit(&q->head,memory_order_relaxed);size_t n=(h+1)%q->cap; if(n==atomic_load_explicit(&q->tail,memory_order_acquire))return -1;q->buf[h]=*m;atomic_store_explicit(&q->head,n,memory_order_release);return 0;}
int spsc_pop(spsc_t *q,msg_t *m){size_t t=atomic_load_explicit(&q->tail,memory_order_relaxed);if(t==atomic_load_explicit(&q->head,memory_order_acquire))return -1;*m=q->buf[t];atomic_store_explicit(&q->tail,(t+1)%q->cap,memory_order_release);return 0;}""",
    "C102": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct node { struct node *next; int v; } node_t;
typedef struct { _Atomic(node_t*) head; node_t *stub; } mpsc_t;
int mpsc_enqueue(mpsc_t *q,node_t *n){node_t *prev=atomic_exchange(&q->head,n);prev->next=n;return 0;}
node_t *mpsc_dequeue(mpsc_t *q){node_t *head=atomic_load(&q->head);if(head==&q->stub)return 0;node_t *next=head->next;if(!next)return 0;int v=head->v;*head=*next;return head; /* simplified */}""",
    "C103": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { _Atomic(node_t*) top; } stack_t;
void stack_push(stack_t *s,node_t *n){node_t *old=atomic_load(&s->top);do{n->next=old;}while(!atomic_compare_exchange_weak(&s->top,&old,n));}
node_t *stack_pop(stack_t *s){node_t *old=atomic_load(&s->top);node_t *next;do{if(!old)return 0;next=old->next;}while(!atomic_compare_exchange_weak(&s->top,&old,next));return old;}""",
    "C104": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { _Atomic int state; } once_t; /* 0=init,1=running,2=done */
void call_once(once_t *o,void (*fn)(void)){int s=atomic_load(&o->state);if(s==2)return; if(atomic_compare_exchange_strong(&o->state,&s,1)){fn();atomic_store(&o->state,2);}}""",
    "C105": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { _Atomic int flag; } event_t;
void event_set(event_t *e){atomic_store(&e->flag,1);}
void event_wait(event_t *e){while(!atomic_load(&e->flag)){} atomic_store(&e->flag,0);}""",
    "C106": """#include <stdint.h>
#include <stddef.h>
typedef struct { int a,b; int held; } deadlock_demo_t;
void ordered_lock(deadlock_demo_t *x,deadlock_demo_t *y){if(x<y){mutex_lock(x);mutex_lock(y);}else{mutex_lock(y);mutex_lock(x);}}""",
    "C107": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
void smp_mb(void){atomic_thread_fence(memory_order_seq_cst);}
void publish(int *flag,int *data){*data=42;smp_mb();*flag=1;}
int consume(int *flag,int *data){if(!*flag)return 0;smp_mb();return *data==42;}""",
    "C108": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t generation; void *ptr; } gen_ptr_t;
int gen_ptr_valid(gen_ptr_t *g,uint32_t gen){return g->generation==gen&&g->ptr;}""",
    "C109": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { _Atomic uint32_t v; } atomic_u32_t;
uint32_t atomic_fetch_max(atomic_u32_t *a,uint32_t val){uint32_t old=atomic_load(&a->v);while(old<val&&!atomic_compare_exchange_weak(&a->v,&old,val)){}return old;}""",
    "C110": """#include <stdint.h>
#include <stddef.h>
void lock_order_check(unsigned id){static unsigned held[4];for(int i=0;i<4;++i)if(held[i]&&id<held[i]){__builtin_trap();}held[id]=1;}""",
    "C111": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t q[64]; volatile uint16_t h,t; } isr_q_t;
void isr_push(isr_q_t *q,uint8_t b){uint16_t n=(q->h+1)%64;if(n!=q->t){q->q[q->h]=b;q->h=n;}}
void isr_drain(isr_q_t *q){while(q->t!=q->h){handle(q->q[q->t]);q->t=(q->t+1)%64;}}""",
    "C112": """#include <stdint.h>
#include <stddef.h>
volatile int top_flag; void top_isr(void){top_flag=1;} void bottom_half(void){if(top_flag){top_flag=0;process();}}""",
    "C113": """#include <stdint.h>
#include <stddef.h>
typedef struct { void (*fn)(void*); void *ctx; } work_t; static work_t pending;
void schedule_work(work_t w){pending=w;} void run_work(void){if(pending.fn)pending.fn(pending.ctx);}""",
    "C114": """#include <stdint.h>
#include <stddef.h>
volatile int dsr_pending; void dsr_request(void){dsr_pending=1;} void dsr_run(void){while(dsr_pending){dsr_pending=0;handle();}}""",
    "C115": """#include <stdint.h>
#include <stddef.h>
typedef struct { int en; } irq_line_t; void irq_enable(irq_line_t *l){l->en=1;} void irq_disable(irq_line_t *l){l->en=0;}""",
    "C116": """#include <stdint.h>
#include <stddef.h>
static int nest; void nested_enter(void){nest++;} void nested_leave(void){if(nest)nest--;}""",
    "C117": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t pending; } irq_ctrl_t; void irq_set_pending(irq_ctrl_t *c,unsigned b){c->pending|=(1u<<b);} void irq_clear(irq_ctrl_t *c,unsigned b){c->pending&=~(1u<<b);}""",
    "C118": """#include <stdint.h>
#include <stddef.h>
void defer_to_thread(volatile int *flag){*flag=1;} void thread_poll(volatile int *flag){if(*flag){*flag=0;handle();}}""",
    "C119": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t count; } isr_stats_t; void isr_count(isr_stats_t *s){s->count++;}""",
    "C120": """#include <stdint.h>
#include <stddef.h>
int irq_affinity_set(unsigned cpu){return cpu<4?0:-1;}""",
    "C121": """#include <stdint.h>
#include <stddef.h>
static inline uint32_t mmio_read32(volatile uint32_t *reg){return *reg;}
static inline void mmio_write32(volatile uint32_t *reg,uint32_t v){*reg=v;}""",
    "C122": """#include <stdint.h>
#include <stddef.h>
uint32_t reg_rmw(volatile uint32_t *r,unsigned lo,unsigned w,uint32_t val){uint32_t m=((1u<<w)-1u)<<lo;uint32_t old=*r;*r=(old&~m)|((val<<lo)&m);return (old>>lo)&((1u<<w)-1u);}""",
    "C123": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t DR, SR; } uart_t; int uart_poll_tx(uart_t *u,uint8_t b,uint32_t to){while(!(u->SR&(1u<<7))&&to--){} return to?(u->DR=b,0):-1;}""",
    "C124": """#include <stdint.h>
#include <stddef.h>
void reg_write_masked(volatile uint32_t *r,uint32_t mask,uint32_t val){*r=(*r&~mask)|(val&mask);}""",
    "C125": """#include <stdint.h>
#include <stddef.h>
int poll_until(volatile uint32_t *r,uint32_t mask,int set,uint32_t to){while(((*r&mask)!=0)!=set){if(!to--)return -1;}return 0;}""",
    "C126": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t off, val; } reg_seq_t; void apply_seq(volatile uint8_t *base,const reg_seq_t *s,size_t n){for(size_t i=0;i<n;++i)*(volatile uint32_t*)(base+s[i].off)=s[i].val;}""",
    "C127": """#include <stdint.h>
#include <stddef.h>
uint32_t field_get(uint32_t w,unsigned lo,unsigned hi){return (w>>lo)&((1u<<(hi-lo+1))-1u);} void field_set(uint32_t *w,unsigned lo,unsigned hi,uint32_t v){uint32_t m=((1u<<(hi-lo+1))-1u)<<lo;*w=(*w&~m)|((v<<lo)&m);}""",
    "C128": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t regs[16]; } blk_t; int blk_read(blk_t *b,unsigned idx,uint32_t *v){if(idx>=16)return -1;*v=b->regs[idx];return 0;}""",
    "C129": """#include <stdint.h>
#include <stddef.h>
void delay_cycles(volatile uint32_t n){while(n--)__asm volatile("":::"memory");}""",
    "C130": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t addr, val; } reg_cache_t; int cache_write(reg_cache_t *c,size_t n,unsigned idx,uint32_t v){if(idx>=n)return -1;if(c[idx].val==v)return 1;c[idx].val=v;*(volatile uint32_t*)(uintptr_t)c[idx].addr=v;return 0;}""",
    "C131": """#include <stdint.h>
#include <stddef.h>
int reg_self_test(volatile uint32_t *r){uint32_t old=*r;*r=0xA5A5A5A5u;int ok=*r==0xA5A5A5A5u;*r=old;return ok?0:-1;}""",
    "C132": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t CR; } periph_t; void periph_reset(periph_t *p){p->CR|=1u;p->CR&=~1u;}""",
    "C133": """#include <stdint.h>
#include <stddef.h>
uint32_t read_le_reg(volatile uint8_t *p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}""",
    "C134": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t IRQ_EN, IRQ_STAT; } irq_blk_t; void irq_unmask(irq_blk_t *b,unsigned bit){b->IRQ_EN|=(1u<<bit);} void irq_ack(irq_blk_t *b,unsigned bit){b->IRQ_STAT=(1u<<bit);}""",
    "C135": """#include <stdint.h>
#include <stddef.h>
int hal_write_checked(volatile uint32_t *r,uint32_t v,uint32_t mask){if(v&~mask)return -1;*r=v;return 0;}""",
    "C136": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t SR, DR; } uart_t; int uart_write_byte(uart_t *u,uint8_t b){while(!(u->SR&(1u<<7))); u->DR=b; return 0;} int uart_read_byte(uart_t *u,uint8_t *b){if(!(u->SR&(1u<<5)))return -1; *b=(uint8_t)u->DR; return 0;}""",
    "C137": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t buf[128]; volatile uint16_t h,t; } rx_ring_t; typedef struct { volatile uint32_t SR, DR; } uart_t; void uart_rx_isr(uart_t *u,rx_ring_t *r){while(u->SR&(1u<<5)){uint8_t b=(uint8_t)u->DR;uint16_t n=(r->h+1)%128;if(n!=r->t){r->buf[r->h]=b;r->h=n;}}}""",
    "C138": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t txq[64]; volatile uint16_t h,t; } txq_t; typedef struct { volatile uint32_t SR, DR, CR1; } uart_t; void uart_tx_isr(uart_t *u,txq_t *q){if(q->t==q->h){u->CR1&=~(1u<<7);return;} u->DR=q->txq[q->t]; q->t=(q->t+1)%64;}""",
    "C139": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t SR, DR; } uart_t; int uart_write_timeout(uart_t *u,uint8_t b,uint32_t ms){while(!(u->SR&(1u<<7))){if(!ms--)return -1;} u->DR=b;return 0;}""",
    "C140": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t SR, DR; } uart_t; void uart_flush_rx(uart_t *u){while(u->SR&(1u<<5)){(void)u->DR;}}""",
    "C141": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t overruns, frames; } uart_stats_t; void stat_frame(uart_stats_t *s){s->frames++;}""",
    "C142": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t SR, DR; } spi_t; int spi_transfer(spi_t *s,const uint8_t *tx,uint8_t *rx,size_t n){for(size_t i=0;i<n;++i){while(!(s->SR&(1u<<1))); uint8_t out=tx?tx[i]:0xFF; s->DR=out; while(!(s->SR&(1u<<0))); uint8_t in=(uint8_t)s->DR; if(rx)rx[i]=in;} return 0;}""",
    "C143": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t SR, DR; } spi_t; typedef struct { const uint8_t *tx; uint8_t *rx; size_t rem; int done; } spi_job_t; static spi_job_t job; int spi_transfer_irq(const uint8_t *tx,uint8_t *rx,size_t n){job.tx=tx;job.rx=rx;job.rem=n;job.done=0;return 0;} void spi_isr(spi_t *s){if(!job.rem){job.done=1;return;} s->DR=job.tx?*job.tx++:0xFF; while(!(s->SR&1)); if(job.rx)*job.rx++=(uint8_t)s->DR; job.rem--;}""",
    "C144": """#include <stdint.h>
#include <stddef.h>
static unsigned active_cs=0xFF; void spi_select(unsigned cs){active_cs=cs;} void spi_deselect(void){active_cs=0xFF;} int spi_transfer_cs(unsigned cs,const uint8_t *tx,uint8_t *rx,size_t n){spi_select(cs);int r=spi_transfer(0,tx,rx,n);spi_deselect();return r;}""",
    "C145": """#include <stdint.h>
#include <stddef.h>
int i2c_write(uint8_t addr7,const uint8_t *data,size_t n,uint32_t timeout_ms); /* overridden by SOLUTION_CODE */""",
    "C146": """#include <stdint.h>
#include <stddef.h>
int i2c_write_read(uint8_t addr7,const uint8_t *wr,size_t wn,uint8_t *rd,size_t rn,uint32_t to){if(i2c_write(addr7,wr,wn,to)<0)return -1; return (int)rn;}""",
    "C147": """#include <stdint.h>
#include <stddef.h>
typedef enum { I2C_OK, I2C_ENACK, I2C_ETIMEOUT, I2C_EARB, I2C_EBUS } i2c_err_t; i2c_err_t i2c_write_ex(uint8_t a,const uint8_t *d,size_t n,uint32_t to){return i2c_write(a,d,n,to)==0?I2C_OK:I2C_ENACK;}""",
    "C148": """#include <stdint.h>
#include <stddef.h>
int gpio_set_mode(unsigned pin,unsigned mode){(void)pin;(void)mode;return 0;} int gpio_write(unsigned pin,int v){(void)pin;(void)v;return 0;}""",
    "C149": """#include <stdint.h>
#include <stddef.h>
int gpio_read(unsigned pin){(void)pin;return 0;} int gpio_toggle(unsigned pin){return gpio_write(pin,!gpio_read(pin));}""",
    "C150": """#include <stdint.h>
#include <stddef.h>
typedef void (*gpio_cb)(unsigned pin); static gpio_cb cbs[16]; void gpio_irq_handler(unsigned pin){if(pin<16&&cbs[pin])cbs[pin](pin);}""",
    "C151": """#include <stdint.h>
#include <stddef.h>
int pwm_set_duty(unsigned ch,uint16_t duty){(void)ch;(void)duty;return 0;}""",
    "C152": """#include <stdint.h>
#include <stddef.h>
int adc_read_channel(unsigned ch,uint16_t *out){(void)ch;*out=0;return 0;}""",
    "C153": """#include <stdint.h>
#include <stddef.h>
int dac_write(unsigned ch,uint16_t v){(void)ch;(void)v;return 0;}""",
    "C154": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t pin, mode; } gpio_cfg_t; int gpio_apply(const gpio_cfg_t *c,size_t n){for(size_t i=0;i<n;++i)gpio_set_mode(c[i].pin,c[i].mode);return 0;}""",
    "C155": """#include <stdint.h>
#include <stddef.h>
int exti_enable(unsigned line){(void)line;return 0;}""",
    "C156": """#include <stdint.h>
#include <stddef.h>
int pinmux_set(unsigned pin,unsigned af){(void)pin;(void)af;return 0;}""",
    "C157": """#include <stdint.h>
#include <stddef.h>
int debounce_read(unsigned pin,unsigned ms){(void)ms;return gpio_read(pin);}""",
    "C158": """#include <stdint.h>
#include <stddef.h>
int i2c_probe(uint8_t addr){uint8_t d=0;return i2c_write(addr,&d,0,10);}""",
    "C159": """#include <stdint.h>
#include <stddef.h>
int spi_cs_gpio_init(void){return 0;} int spi_bus_recover(void){return 0;}""",
    "C160": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t tx_bytes, rx_bytes, err; } bus_stats_t; void bus_stat_tx(bus_stats_t *s,size_t n){s->tx_bytes+=n;}""",
    "C161": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t src,dst,len,ctrl; } dma_desc_t; void dma_fill_desc(dma_desc_t *d,const void *s,void *t,size_t n){d->src=(uint32_t)(uintptr_t)s;d->dst=(uint32_t)(uintptr_t)t;d->len=(uint32_t)n;d->ctrl=1;}""",
    "C162": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t CR, LEN, SRC, DST; } dma_t; int dma_start(dma_t *d){d->CR|=1;return 0;} void dma_stop(dma_t *d){d->CR&=~1u;} void dma_abort(dma_t *d){d->CR|=2u;}""",
    "C163": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t CR, LEN, SRC; } dma_t; void dma_double_buffer(dma_t *d,void *a,void *b,size_t n){static int idx; d->SRC=(uint32_t)(uintptr_t)(idx?b:a); idx^=1; d->LEN=n; d->CR|=1;}""",
    "C164": """#include <stdint.h>
#include <stddef.h>
size_t dma_ring_consume(uint8_t *buf,size_t cap,size_t hw,size_t sw){(void)buf;return (hw+cap-sw)%cap;}""",
    "C165": """#include <stdint.h>
#include <stddef.h>
int dma_cache_clean(const void *p,size_t n){(void)p;(void)n;return 0;} int dma_cache_invalidate(void *p,size_t n){(void)p;(void)n;return 0;}""",
    "C166": """#include <stdint.h>
#include <stddef.h>
typedef struct { dma_desc_t *list; } dma_chain_t; void dma_chain_start(dma_chain_t *c){(void)c;}""",
    "C167": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t CR, LEN, SRC; } dma_t; void dma_circular_start(dma_t *d,void *buf,size_t n){d->SRC=(uint32_t)(uintptr_t)buf;d->LEN=n;d->CR|=5u;}""",
    "C168": """#include <stdint.h>
#include <stddef.h>
int dma_mem2mem(void *dst,const void *src,size_t n){(void)dst;(void)src;(void)n;return 0;}""",
    "C169": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t CR; } dma_t; void dma_irq_handler(dma_t *d){if(d->CR&(1u<<16))d->CR&=~(1u<<16);}""",
    "C170": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t CR; } dma_t; int dma_pause(dma_t *d){d->CR|=4u;return 0;} int dma_resume(dma_t *d){d->CR&=~4u;return 0;}""",
    "C171": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t src,dst,remain; } scat_t; int dma_scatter(scat_t *s){return s->remain?0:-1;}""",
    "C172": """#include <stdint.h>
#include <stddef.h>
#include <string.h>
int dma_self_test(void){uint8_t a[4]={1,2,3,4},b[4]={0}; memcpy(b,a,4);return b[0]==1?0:-1;}""",
    "C173": """#include <stdint.h>
#include <stddef.h>
void sw_timer_set(sw_timer_t*,uint32_t,timer_cb,void*); /* see SOLUTION_CODE */""",
    "C174": """#include <stdint.h>
#include <stddef.h>
typedef void (*timer_cb)(void*); typedef struct sw_timer { uint32_t expires, period; timer_cb cb; void *ctx; int active, periodic; } sw_timer_t; void sw_timer_set_periodic(sw_timer_t *t,uint32_t p,timer_cb cb,void *ctx){t->period=p;t->cb=cb;t->ctx=ctx;t->periodic=1;} int sw_timer_cancel_sync(sw_timer_t *t){t->active=0;return 0;}""",
    "C175": """#include <stdint.h>
#include <stddef.h>
int time_after(uint32_t a,uint32_t b){return (int32_t)(a-b)>0;} int time_before_eq(uint32_t a,uint32_t b){return (int32_t)(a-b)<=0;} uint32_t time_delta(uint32_t now,uint32_t then){return now-then;}""",
    "C176": """#include <stdint.h>
#include <stddef.h>
typedef struct sw_timer sw_timer_t; typedef struct { sw_timer_t *buckets[256]; unsigned cursor; } wheel_t; void wheel_insert(sw_timer_t *t,uint32_t expires){(void)t;(void)expires;} void wheel_tick(void){}""",
    "C177": """#include <stdint.h>
#include <stddef.h>
typedef struct sw_timer sw_timer_t; typedef struct { sw_timer_t **heap; size_t n, cap; } heap_t; void heap_timer_insert(sw_timer_t *t){(void)t;} sw_timer_t *heap_timer_pop_expired(uint32_t now){(void)now;return 0;}""",
    "C178": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t next, period; } periodic_t; void periodic_arm(periodic_t *p,uint32_t ms){p->period=ms;p->next=ms;} void periodic_on_fire(periodic_t *p){p->next+=p->period;}""",
    "C179": """#include <stdint.h>
#include <stddef.h>
typedef void (*task_fn)(void); static task_fn tasks[8]; static int tn; void task_add(task_fn f){if(tn<8)tasks[tn++]=f;} void scheduler_run(void){for(int i=0;i<tn;++i)tasks[i]();}""",
    "C180": """#include <stdint.h>
#include <stddef.h>
typedef void (*task_fn)(void); typedef struct { task_fn fn; int ready; } coop_t; void yield(coop_t *t){t->ready=0;} void coop_schedule(coop_t *tasks,size_t n){for(size_t i=0;i<n;++i)if(tasks[i].ready)tasks[i].fn();}""",
    "C181": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t deadline; int (*fn)(void); } deadline_t; int run_deadlines(deadline_t *d,size_t n,uint32_t now){for(size_t i=0;i<n;++i)if((int32_t)(now-d[i].deadline)>0)d[i].fn();return 0;}""",
    "C182": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t wcet_us; } task_profile_t; int sched_feasibility(task_profile_t *t,size_t n,uint32_t period){uint32_t sum=0;for(size_t i=0;i<n;++i)sum+=t[i].wcet_us;return sum<=period?0:-1;}""",
    "C183": """#include <stdint.h>
#include <stddef.h>
void tickless_sleep_until(uint32_t target){(void)target;}""",
    "C184": """#include <stdint.h>
#include <stddef.h>
typedef struct sw_timer { int active; } sw_timer_t; typedef struct { sw_timer_t *pool; size_t n; } tpool_t; sw_timer_t *tpool_alloc(tpool_t *p){for(size_t i=0;i<p->n;++i)if(!p->pool[i].active)return &p->pool[i];return 0;}""",
    "C185": """#include <stdint.h>
#include <stddef.h>
int timer_self_test(void){return (int32_t)(10-5)>0?0:-1;}""",
    "C186": """#include <stdint.h>
#include <stddef.h>
typedef enum { ST_SYNC,ST_LEN,ST_DATA,ST_CRC } pstate_t; int frame_parse(pstate_t *s,const uint8_t *b,size_t n,uint8_t *out,size_t *olen){(void)s;(void)b;(void)n;(void)out;(void)olen;return -1;}""",
    "C187": """#include <stdint.h>
#include <stddef.h>
size_t parser_resync(const uint8_t *buf,size_t n){for(size_t i=0;i<n;++i)if(buf[i]==0xAA)return i;return n;}""",
    "C188": """#include <stdint.h>
#include <stddef.h>
size_t cobs_encode(const uint8_t *in,size_t n,uint8_t *out){size_t o=1,block=0;out[0]=0;for(size_t i=0;i<n;++i){if(in[i]==0){out[block]=(uint8_t)(o-block-1);block=o++;out[o++]=0;}else out[o++]=in[i];}out[block]=(uint8_t)(o-block-1);return o;} size_t cobs_decode(const uint8_t *in,size_t n,uint8_t *out){size_t o=0,i=0;while(i<n){uint8_t code=in[i++];for(uint8_t j=1;j<code&&i<n;++j)out[o++]=in[i++];if(code<0xFF&&i<n&&o>0)out[o++]=0;}return o;}""",
    "C189": """#include <stdint.h>
#include <stddef.h>
size_t slip_encode(const uint8_t *in,size_t n,uint8_t *out){size_t o=0;for(size_t i=0;i<n;++i){if(in[i]==0xC0){out[o++]=0xDB;out[o++]=0xDC;}else if(in[i]==0xDB){out[o++]=0xDB;out[o++]=0xDD;}else out[o++]=in[i];}return o;}""",
    "C190": """#include <stdint.h>
#include <stddef.h>
size_t stuff_bits(const uint8_t *in,size_t n,uint8_t *out){int ones=0;size_t o=0;for(size_t i=0;i<n;++i){for(int bit=7;bit>=0;--bit){out[o++]=(in[i]>>bit)&1u; if((in[i]>>bit)&1u)ones++; else ones=0;if(ones==5){out[o++]=0;ones=0;}}}return o;}""",
    "C191": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t type; uint16_t len; const uint8_t *val; } tlv_t; int tlv_next(const uint8_t *p,size_t n,size_t *off,tlv_t *t){if(*off+3>n)return -1;t->type=p[*off];t->len=(uint16_t)((p[*off+1]<<8)|p[*off+2]);t->val=p+*off+3;*off+=3+t->len;return 0;}""",
    "C192": """#include <stdint.h>
#include <stddef.h>

typedef struct { uint8_t *buf; size_t cap, head, tail; } ring_t;
static size_t rn(const ring_t *r, size_t i) { return (i + 1u) % r->cap; }
void ring_init(ring_t *r, uint8_t *buf, size_t cap) { r->buf=buf; r->cap=cap; r->head=r->tail=0; }
size_t ring_count(const ring_t *r) { return r->head>=r->tail ? r->head-r->tail : r->cap-(r->tail-r->head); }
size_t ring_pop(ring_t *r,uint8_t *dst,size_t n){size_t popped=0;while(popped<n&&r->tail!=r->head){dst[popped++]=r->buf[r->tail];r->tail=rn(r,r->tail);}return popped;}
int stream_parse_on_ring(ring_t *r,int (*cb)(uint8_t)){uint8_t b;while(ring_pop(r,&b,1)==1){if(cb(b)==0)return 0;}return -1;}""",
    "C193": """#include <stdint.h>
#include <stddef.h>
size_t escape_encode(const uint8_t *in,size_t n,uint8_t *out,uint8_t esc,uint8_t flag){size_t o=0;for(size_t i=0;i<n;++i){if(in[i]==flag||in[i]==esc){out[o++]=esc;out[o++]=in[i]^0x20;}else out[o++]=in[i];}return o;}""",
    "C194": """#include <stdint.h>
#include <stddef.h>
typedef int (*cmd_fn)(const uint8_t*,size_t); int dispatch(uint8_t op,cmd_fn *table,size_t n,const uint8_t *p,size_t l){if(op>=n||!table[op])return -1;return table[op](p,l);}""",
    "C195": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t buf[512]; size_t len; uint16_t id; } frag_t; int frag_add(frag_t *f,const uint8_t *p,size_t n){if(f->len+n>512)return -1;for(size_t i=0;i<n;++i)f->buf[f->len++]=p[i];return 0;}""",
    "C196": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint16_t expect; } seq_t; int seq_check(seq_t *s,uint16_t got){if(got==s->expect)return 0;if(got>s->expect)return 2;return 1;}""",
    "C197": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t seq; int retries; } txq_t; void ack_timeout(txq_t *q){if(q->retries++>3)q->retries=0;}""",
    "C198": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t win[8]; unsigned base; } swin_t; int swin_accept(swin_t *w,unsigned seq){unsigned idx=seq%8;if(w->win[idx])return -1;w->win[idx]=1;return 0;}""",
    "C199": """#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
int parse_telemetry_line(const char *line,int *temp,int *hum){return sscanf(line,"T=%d H=%d",temp,hum)==2?0:-1;}""",
    "C200": """#include <stdint.h>
#include <stddef.h>
int safe_parse(const uint8_t *p,size_t n,size_t need){if(!p||n<need)return -1;return 0;}""",
    "C201": """#include <stdint.h>
#include <stddef.h>
typedef enum { IDLE, READY, GO, FAULT } st_t; typedef enum { TIMER, BUTTON, FAULT_EVT } ev_t; st_t traffic_step(st_t s,ev_t e){switch(s){case IDLE:if(e==TIMER)return READY;break;case READY:if(e==BUTTON)return GO;break;case GO:if(e==TIMER)return IDLE;break;default:break;} if(e==FAULT_EVT)return FAULT;return s;}""",
    "C202": """#include <stdint.h>
#include <stddef.h>
state_E stateMachine(input_E); /* see SOLUTION_CODE */""",
    "C203": """#include <stdint.h>
#include <stddef.h>
typedef enum { DISC, CONN, AUTH, RDY, ERR } st_t; typedef enum { OPEN, OK, FAIL, TIMEOUT } ev_t; st_t conn_step(st_t s,ev_t e,uint32_t now){(void)now;(void)e;return s;}""",
    "C204": """#include <stdint.h>
#include <stddef.h>
typedef enum { OFF, INIT, RUN, SUSP, ERROR } pwr_t; pwr_t pwr_step(pwr_t s,int ev){switch(s){case OFF:if(ev==1)return INIT;break;case INIT:if(ev==2)return RUN;break;case RUN:if(ev==3)return SUSP;break;default:break;}return s;}""",
    "C205": """#include <stdint.h>
#include <stddef.h>
typedef enum { IDLE, READY, GO, FAULT } st_t; typedef struct { st_t s; void (*enter)(st_t); } sm_t; void sm_step(sm_t *m,st_t next){m->s=next;if(m->enter)m->enter(next);}""",
    "C206": """#include <stdint.h>
#include <stddef.h>
typedef int (*handler_t)(void); int table_drive(const handler_t *t,size_t n,unsigned idx){return idx<n&&t[idx]?t[idx]():-1;}""",
    "C207": """#include <stdint.h>
#include <stddef.h>
typedef enum { IDLE, READY, GO, FAULT } st_t; typedef enum { TIMER, BUTTON, FAULT_EVT } ev_t; typedef struct { st_t cur, parent; } hsm_t; st_t hsm_step(hsm_t *h,ev_t e){return traffic_step(h->cur,e);}""",
    "C208": """#include <stdint.h>
#include <stddef.h>
typedef enum { IDLE, READY, GO, FAULT, ERR } st_t; typedef struct { uint32_t timeout_ms; st_t s; } to_sm_t; st_t to_tick(to_sm_t *m,uint32_t now){return now>m->timeout_ms?ERR:m->s;}""",
    "C209": """#include <stdint.h>
#include <stddef.h>
typedef enum { IDLE, READY, GO, FAULT } st_t; typedef enum { TIMER, BUTTON, FAULT_EVT } ev_t; st_t traffic_step(st_t s,ev_t e); int fsm_self_test(void){return traffic_step(IDLE,TIMER)==READY?0:-1;}""",
    "C210": """#include <stdint.h>
#include <stddef.h>
typedef enum { IDLE, READY, GO, FAULT } st_t; typedef struct { st_t s; int history[8]; int hp; } hist_sm_t; void hist_push(hist_sm_t *m,st_t s){m->history[m->hp++%8]=s;}""",
    "C211": """#include <stdint.h>
#include <stddef.h>
typedef enum { IDLE, READY, GO, FAULT } st_t; typedef enum { TIMER, BUTTON, FAULT_EVT } ev_t; st_t traffic_step(st_t s,ev_t e); st_t guarded_step(st_t s,ev_t e,int ok){return ok?traffic_step(s,e):s;}""",
    "C212": """#include <stdint.h>
#include <stddef.h>
typedef enum { IDLE, READY, GO, FAULT } st_t; void fsm_print(st_t s){(void)s;}""",
    "C213": """#include <stdint.h>
#include <stddef.h>
typedef struct { int32_t buf[8]; int idx; int32_t sum; } ma_t; int32_t ma_push(ma_t *m,int32_t v){m->sum-=m->buf[m->idx];m->buf[m->idx]=v;m->sum+=v;m->idx=(m->idx+1)%8;return m->sum/8;}""",
    "C214": """#include <stdint.h>
#include <stddef.h>
typedef struct { int32_t y; int alpha_q8; } ewma_t; int32_t ewma_push(ewma_t *f,int32_t x){f->y=f->y+((f->alpha_q8*(x-f->y))>>8);return f->y;}""",
    "C215": """#include <stdint.h>
#include <stddef.h>
int32_t clamp_i32(int32_t v,int32_t lo,int32_t hi){if(v<lo)return lo;if(v>hi)return hi;return v;}""",
    "C216": """#include <stdint.h>
#include <stddef.h>
int32_t map_range(int32_t x,int32_t in_lo,int32_t in_hi,int32_t out_lo,int32_t out_hi){return out_lo+(x-in_lo)*(out_hi-out_lo)/(in_hi-in_lo);}""",
    "C217": """#include <stdint.h>
#include <stddef.h>
int32_t lerp(int32_t a,int32_t b,int32_t t_q15){return a+((b-a)*t_q15>>15);}""",
    "C218": """#include <stdint.h>
#include <stddef.h>
int32_t median3(int32_t a,int32_t b,int32_t c){if(a>b){int32_t t=a;a=b;b=t;} if(b>c){int32_t t=b;b=c;c=t;} if(a>b){int32_t t=a;a=b;b=t;} return b;}""",
    "C219": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { uint8_t buf[256]; _Atomic uint32_t head, tail; } shmem_ring_t; void shmem_push(shmem_ring_t *r,uint8_t v){uint32_t h=atomic_load(&r->head);uint32_t n=(h+1)%256;if(n!=atomic_load(&r->tail)){r->buf[h]=v;atomic_store(&r->head,n);}}""",
    "C220": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t doorbell; uint32_t msg; } mailbox_t; void mbox_send(mailbox_t *m,uint32_t v){m->msg=v;m->doorbell=1;} uint32_t mbox_recv(mailbox_t *m){if(!m->doorbell)return 0;m->doorbell=0;return m->msg;}""",
    "C221": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct { _Atomic uint32_t seq; uint8_t data[64]; } slot_t; int slot_publish(slot_t *s,const uint8_t *d,size_t n){uint32_t v=atomic_load(&s->seq);atomic_store(&s->seq,v|1);for(size_t i=0;i<n;++i)s->data[i]=d[i];atomic_store(&s->seq,v+2);return 0;}""",
    "C222": """#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
void dmb(void){atomic_thread_fence(memory_order_seq_cst);}""",
    "C223": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t flag; } rendez_t; void rp_produce(rendez_t *r){r->flag=1;} int rp_consume(rendez_t *r){return (int)r->flag;}""",
    "C224": """#include <stdint.h>
#include <stddef.h>
typedef struct { int owner; } spin_t; int try_claim(spin_t *s,int me){return s->owner==0?(s->owner=me,1):s->owner==me;}""",
    "C225": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t rp, wp; uint8_t b[128]; } fifo_t; int rpmsg_send(fifo_t *f,uint8_t v){uint32_t n=(f->wp+1)%128;if(n==f->rp)return -1;f->b[f->wp]=v;f->wp=n;return 0;}""",
    "C226": """#include <stdint.h>
#include <stddef.h>
int hsem_take(int id){(void)id;return 0;} void hsem_give(int id){(void)id;}""",
    "C227": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t cmd, arg; } rpc_t; int rpc_call(rpc_t *r){(void)r;return 0;}""",
    "C228": """#include <stdint.h>
#include <stddef.h>
void cache_flush(void *p,size_t n){(void)p;(void)n;} void cache_inv(void *p,size_t n){(void)p;(void)n;}""",
    "C229": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t magic; } hdr_t; int ipc_validate(hdr_t *h){return h->magic==0xC0DEC0DEu?0:-1;}""",
    "C230": """#include <stdint.h>
#include <stddef.h>
typedef struct { volatile uint32_t doorbell; uint32_t msg; } mailbox_t; void mbox_send(mailbox_t*,uint32_t); uint32_t mbox_recv(mailbox_t*); int ipc_self_test(void){mailbox_t m={0};mbox_send(&m,42);return mbox_recv(&m)==42?0:-1;}""",
    "C231": """#include <stdint.h>
#include <stddef.h>
typedef struct { char buf[256]; volatile uint16_t w; } slog_t; void slog_isr(slog_t *l,const char *m){(void)m;(void)l;}""",
    "C232": """#include <stdint.h>
#include <stddef.h>
typedef struct { char buf[256]; volatile uint16_t r,w; } slog_t; void slog_drain(slog_t *l){while(l->r!=l->w){emit(l->buf[l->r++]);}}""",
    "C233": """#include <stdint.h>
#include <stddef.h>
#define LOG_LEVEL 2
#define LOGI(...) do{if(LOG_LEVEL>=2)log(__VA_ARGS__);}while(0)
void log(const char *fmt,...);""",
    "C234": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t dropped; } log_stats_t; void log_drop(log_stats_t *s){s->dropped++;}""",
    "C235": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t magic, pc, lr; } crash_t; crash_t *crash_slot(void){static crash_t c; return &c;}""",
    "C236": """#include <stdint.h>
#include <stddef.h>
void backtrace_store(uint32_t *frames,size_t n){for(size_t i=0;i<n;++i)frames[i]=0;}""",
    "C237": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t ts, code; } evt_t; void trace_evt(evt_t e){(void)e;}""",
    "C238": """#include <stdint.h>
#include <stddef.h>
int assert_log(int cond,const char *msg){if(!cond){log(msg);return -1;}return 0;}""",
    "C239": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t ring[512]; size_t head,tail; } persist_log_t; void plog_append(persist_log_t *p,const uint8_t *d,size_t n){for(size_t i=0;i<n;++i)p->ring[p->head++%512]=d[i];}""",
    "C240": """#include <stdint.h>
#include <stddef.h>
int diag_self_test(void){return 0;}""",
    "C241": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t last_kick, window_ms; } wdt_t; int wdt_kick(wdt_t *w,uint32_t now){if(now-w->last_kick>w->window_ms)return -1;w->last_kick=now;return 0;}""",
    "C242": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t last; } hb_t; int hb_check(hb_t *h,uint32_t now,uint32_t limit){return (now-h->last)<=limit?0:-1;}""",
    "C243": """#include <stdint.h>
#include <stddef.h>
typedef enum { RUN, DEEPSLEEP } pm_t; void pm_enter(pm_t m){(void)m;}""",
    "C244": """#include <stdint.h>
#include <stddef.h>
void brownout_handler(void){safe_shutdown();}""",
    "C245": """#include <stdint.h>
#include <stddef.h>
typedef struct { int stage; } boot_t; int boot_verify(boot_t *b){return b->stage>=3?0:-1;}""",
    "C246": """#include <stdint.h>
#include <stddef.h>
uint32_t crc32_ieee(const uint8_t *d,size_t n){uint32_t c=0xFFFFFFFFu;for(size_t i=0;i<n;++i){c^=d[i];for(int b=0;b<8;++b)c=(c&1)?(c>>1)^0xEDB88320u:c>>1;}return ~c;}
uint32_t crc_fw(const uint8_t *img,size_t n){return crc32_ieee(img,n);}""",
    "C247": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t a,b; } pair_t; int dual_bank_commit(pair_t *p){return p->a==p->b?0:-1;}""",
    "C248": """#include <stdint.h>
#include <stddef.h>
void safe_state_enter(void){disable_outputs();}""",
    "C249": """#include <stdint.h>
#include <stddef.h>
typedef struct { int ok; } health_t; void health_update(health_t *h,int v){h->ok=v;}""",
    "C250": """#include <stdint.h>
#include <stddef.h>
int reliability_self_test(void){return 0;}""",
    "C251": """#include <stdint.h>
#include <stddef.h>
static uint32_t fake_now; void fake_clock_set(uint32_t ms){fake_now=ms;} uint32_t fake_clock_get(void){return fake_now;}""",
    "C252": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t buf[64]; size_t n; } fake_uart_t; void fake_uart_inject(fake_uart_t *f,uint8_t b){if(f->n<64)f->buf[f->n++]=b;}""",
    "C253": """#include <stdint.h>
#include <stddef.h>
typedef struct { int calls; } mock_t; void mock_reset(mock_t *m){m->calls=0;}""",
    "C254": """#include <stdint.h>
#include <stddef.h>
int test_runner(void (*tests[])(void),size_t n){for(size_t i=0;i<n;++i)tests[i]();return 0;}""",
    "C255": """#include <stdint.h>
#include <stddef.h>
typedef struct { int failed; } tctx_t; void expect_true(tctx_t *t,int c){if(!c)t->failed=1;}""",
    "C256": """#include <stdint.h>
#include <stddef.h>
void *fakes_heap[16]; int fake_alloc_idx; void *fake_malloc(size_t n){(void)n;return fakes_heap[fake_alloc_idx++];}""",
    "C257": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint32_t seed; } rng_t; uint32_t rng_next(rng_t *r){r->seed=r->seed*1103515245u+12345u;return r->seed;}""",
    "C258": """#include <stdint.h>
#include <stddef.h>
typedef struct { int enabled; } fault_inj_t; void fault_inject(fault_inj_t *f,int code){if(f->enabled)trigger(code);}""",
    "C259": """#include <stdint.h>
#include <stddef.h>
int record_replay(const uint8_t *in,size_t n,uint8_t *out){for(size_t i=0;i<n;++i)out[i]=in[i];return 0;}""",
    "C260": """#include <stdint.h>
#include <stddef.h>
int harness_self_test(void){return 0;}""",
    "C261": """#include <cstdint>
extern "C" uint32_t irq_save(void); extern "C" void irq_restore(uint32_t);
class IrqLock { uint32_t st_; public: IrqLock():st_(irq_save()){} ~IrqLock(){irq_restore(st_);} IrqLock(const IrqLock&)=delete; IrqLock& operator=(const IrqLock&)=delete; };""",
    "C262": """#include <cstddef>
template<typename T> class Span { T* data_; std::size_t size_; public: Span(T* d,std::size_t n):data_(d),size_(n){} T* data()const{return data_;} std::size_t size()const{return size_;} T& at(std::size_t i)const{if(i>=size_)throw 1;return data_[i];} Span subspan(std::size_t off,std::size_t n)const{return Span(data_+off,n);} };""",
    "C263": """#include <cstddef>
template<typename Tag> struct Link { Link* next=nullptr; }; template<typename T,typename Tag> T* container_of(Link<Tag>* n){return reinterpret_cast<T*>(n);}""",
    "C264": """#include <cstdint>
template<std::size_t Cap> struct Ring { std::uint8_t b[Cap]; std::size_t h,t; bool push(std::uint8_t v){auto n=(h+1)%Cap;if(n==t)return false;b[h]=v;h=n;return true;} bool pop(std::uint8_t& v){if(t==h)return false;v=b[t];t=(t+1)%Cap;return true;} };""",
    "C265": """#include <cstddef>
template<typename Sig> class function_ref; template<typename R,typename...A> class function_ref<R(A...)> { R(*fn_)(void*,A...); void* ctx_; public: template<typename F> function_ref(F&f):fn_([](void* c,A...a)->R{return (*static_cast<F*>(c))(a...);}),ctx_(&f){} R operator()(A...a)const{return fn_(ctx_,a...);} };""",
    "C266": """#include <memory>
struct DmaDeleter { void operator()(void* p)const{ dma_free(p);} }; using DmaPtr=std::unique_ptr<void,DmaDeleter>; void dma_free(void*);""",
    "C267": """#include <cstdint>
enum class State: std::uint8_t { Idle, Run, Fault }; const char* to_string(State s){switch(s){case State::Idle:return "Idle";case State::Run:return "Run";default:return "Fault";}}""",
    "C268": """struct Base { virtual int read()=0; }; struct CrtpDev { int read(){return 42;} };""",
    "C269": """#include <utility>
template<typename T,std::size_t N> class MoveQueue { T buf[N]; std::size_t h,t,sz; public: bool push(T&&v){if(sz==N)return false;buf[h]=std::move(v);h=(h+1)%N;++sz;return true;} bool pop(T&out){if(!sz)return false;out=std::move(buf[t]);t=(t+1)%N;--sz;return true;} };""",
    "C270": """#include <cstdint>
constexpr std::uint32_t reg(std::uint32_t off,std::uint32_t val){return (off<<16)|val;}""",
    "C271": """#include <cstddef>
#include <new>
template<typename T,std::size_t N> struct Pool { alignas(T) unsigned char mem[sizeof(T)*N]; bool used[N]{}; T* allocate(){for(std::size_t i=0;i<N;++i)if(!used[i]){used[i]=true;return new(&mem[i*sizeof(T)]) T();}return nullptr;} };""",
    "C272": """template<typename T,typename E> struct expected { bool ok; T v; E e; static expected value(T x){return {true,x,{}};} static expected error(E err){return {false,{},err};} };""",
    "C273": """#include <atomic>
struct Flag { std::atomic<bool> f{false}; void give(){f.store(true,std::memory_order_release);} void take(){while(!f.exchange(false,std::memory_order_acquire)){} } };""",
    "C274": """struct Handler { void on(int& x){x=1;} }; void bug(){int tmp=0; auto cb=[&](){Handler h; h.on(tmp);}; cb();}""",
    "C275": """#include <type_traits>
template<typename T> struct is_mmio_reg: std::false_type{}; template<> struct is_mmio_reg<volatile unsigned>: std::true_type{};""",
    "C276": """#include <stdint.h>
#include <stddef.h>
typedef struct { float x,y,z; } aos_t; typedef struct { float x[1024],y[1024],z[1024]; } soa_t; void aos_to_soa(const aos_t *in,soa_t *out,size_t n){for(size_t i=0;i<n;++i){out->x[i]=in[i].x;out->y[i]=in[i].y;out->z[i]=in[i].z;}}""",
    "C277": """#include <stdint.h>
#include <stddef.h>
void prefetch(const void *p){(void)p;}
int sum_array(const int *a,size_t n){int s=0;for(size_t i=0;i<n;++i){if(i+8<n)prefetch(a+i+8);s+=a[i];}return s;}""",
    "C278": """#include <stdint.h>
#include <stddef.h>
void hot_loop(int *a,size_t n){for(size_t i=0;i<n;++i)a[i]*=2;}""",
    "C279": """#include <stdint.h>
#include <stddef.h>
typedef struct { uint8_t a,b,c,d; } padded_t; size_t packed_copy(padded_t *d,const padded_t *s,size_t n){for(size_t i=0;i<n;++i)d[i]=s[i];return n;}""",
    "C280": """#include <stdint.h>
#include <stddef.h>
void unroll4(const int *in,int *out,size_t n){size_t i=0;for(;i+4<=n;i+=4){out[i]=in[i];out[i+1]=in[i+1];out[i+2]=in[i+2];out[i+3]=in[i+3];}}""",
    "C281": """#include <stdint.h>
#include <stddef.h>
int branchless_max(int a,int b){return a+((b-a)&((b-a)>>31));}""",
    "C282": """#include <stdint.h>
#include <stddef.h>
void aligned_copy(void *dst,const void *src,size_t n){unsigned char *d=dst;const unsigned char *s=src;for(size_t i=0;i<n;++i)d[i]=s[i];}""",
    "C283": """#include <stdint.h>
#include <stddef.h>
typedef struct { int key, val; } kv_t; void sort_kv(kv_t *a,size_t n){for(size_t i=1;i<n;++i){kv_t k=a[i];ssize_t j=i-1;while(j>=0&&a[j].key>k.key){a[j+1]=a[j];--j;}a[j+1]=k;}}""",
    "C284": """#include <stdint.h>
#include <stddef.h>
size_t strided_sum(const int *a,size_t n,size_t stride){size_t s=0;for(size_t i=0;i<n;i+=stride)s+=a[i];return s;}""",
    "C285": """#include <stdint.h>
#include <stddef.h>
int perf_self_test(void){return 0;}""",
    "C286": """#ifdef __KERNEL__
#include <linux/module.h>
#include <linux/platform_device.h>
static int probe(struct platform_device *pdev){return 0;} static int remove(struct platform_device *pdev){return 0;}
static struct platform_driver drv={.probe=probe,.remove=remove,.driver={.name="demo"}};
module_platform_driver(drv);
#endif""",
    "C287": """#ifdef __KERNEL__
#include <linux/fs.h>
static ssize_t demo_read(struct file *f,char __user *ub,size_t n,loff_t *p){return 0;}
static struct file_operations fops={.read=demo_read};
#endif""",
    "C288": """#ifdef __KERNEL__
#include <linux/uaccess.h>
static int copy_msg(void __user *ub,size_t n,const char *k){if(n>64)return -EINVAL;return copy_to_user(ub,k,n)?-EFAULT:0;}
#endif""",
    "C289": """#ifdef __KERNEL__
#include <linux/ioctl.h>
#define DEMO_IOC_MAGIC 'd'
#define DEMO_IOC_RESET _IO(DEMO_IOC_MAGIC,0)
long demo_ioctl(struct file *f,unsigned cmd,unsigned long arg){if(_IOC_TYPE(cmd)!=DEMO_IOC_MAGIC)return -ENOTTY;switch(cmd){case DEMO_IOC_RESET:return 0;default:return -EINVAL;}}
#endif""",
    "C290": """#ifdef __KERNEL__
#include <linux/poll.h>
static wait_queue_head_t wq; unsigned ready; unsigned demo_poll(struct file *f,poll_table *wait){poll_wait(f,&wq,wait);return ready?POLLIN:0;}
#endif""",
    "C291": """#ifdef __KERNEL__
#include <linux/sysfs.h>
static atomic_t err_cnt; static ssize_t err_show(struct kobject *k,char *buf){return scnprintf(buf,PAGE_SIZE,"%d\n",atomic_read(&err_cnt));}
#endif""",
    "C292": """#ifdef __KERNEL__
#include <linux/interrupt.h>
static irqreturn_t hard_isr(int irq,void *dev){return IRQ_WAKE_THREAD;}
static irqreturn_t thread_fn(int irq,void *dev){return IRQ_HANDLED;}
static int req=0; int setup(int irq){return request_threaded_irq(irq,hard_isr,thread_fn,0,"demo",&req);}
#endif""",
    "C293": """#ifdef __KERNEL__
#include <linux/dma-mapping.h>
void *dma_buf(struct device *dev,size_t n,dma_addr_t *dma){return dma_alloc_coherent(dev,n,dma,GFP_KERNEL);}
#endif""",
    "C294": """#ifdef __KERNEL__
#include <linux/of.h>
static int parse_u32(struct device_node *np,const char *name,u32 *out){return of_property_read_u32(np,name,out);}
#endif""",
    "C295": """#ifdef __KERNEL__
#include <linux/pm_runtime.h>
static int suspend(struct device *dev){return 0;} static int resume(struct device *dev){return 0;}
static const struct dev_pm_ops pm_ops={.runtime_suspend=suspend,.runtime_resume=resume};
#endif""",
    "C296": """#ifdef __KERNEL__
#include <linux/mm.h>
static int mmap(struct file *f,struct vm_area_struct *vma){return remap_pfn_range(vma,vma->vm_start,virt_to_phys(kbuf)>>PAGE_SHIFT,vma->vm_end-vma->vm_start,vma->vm_page_prot);}
static char kbuf[4096];
#endif""",
    "C297": """#ifdef __KERNEL__
#include <linux/miscdevice.h>
static int misc_open(struct inode *i,struct file *f){return 0;}
static struct file_operations mfops={.open=misc_open};
#endif""",
    "C298": """#ifdef __KERNEL__
#include <linux/debugfs.h>
static struct debugfs_blob_wrapper blob; void dump_regs(void *base,size_t n){blob.data=base;blob.size=n;debugfs_create_blob("regs",0444,0,&blob);}
#endif""",
    "C299": """#ifdef __KERNEL__
#include <linux/moduleparam.h>
static int mode=0; module_param(mode,int,0644); static spinlock_t lock; void set_mode(int m){unsigned long f;spin_lock_irqsave(&lock,f);mode=m;spin_unlock_irqrestore(&lock,f);}
#endif""",
    "C300": """#ifdef __KERNEL__
#include <linux/uaccess.h>
static int safe_read(void __user *ub,size_t __user *lenp,char *kbuf){size_t len;if(get_user(len,lenp))return -EFAULT;if(len>sizeof(kbuf))return -EINVAL;return copy_to_user(ub,kbuf,len)?-EFAULT:(int)len;}
#endif""",
}

def all_solution_codes() -> dict[str, str]:
    """Merge category helpers with SOLUTION_CODE overrides."""
    merged = dict(CATEGORY_CODES)
    merged.update(SOLUTION_CODE)
    return merged



def render_solution(q: Question, code: str) -> str:
    lang = "cpp" if q.lang == "cpp" else "c"
    clar = clarifying_questions(q)
    intro, plan = approach_text(q)
    ds = data_structures(q)
    cx = complexity_notes(q)
    edges = edge_cases(q)
    conc = concurrency_notes(q)
    tests, test_code = test_cases(q)

    lines = [
        f"## {q.id} — {q.title}",
        "",
        "### Step 0 — Clarifying questions (3-6 bullets as interviewer dialogue)",
        "",
    ]
    for b in clar:
        lines.append(f"- **Candidate:** {b}")
    lines.extend(["", "### Step 1 — Approach (short paragraph + bullet plan)", "", intro, ""])
    for p in plan:
        lines.append(f"- {p}")
    lines.extend(["", "### Step 2 — Data structures / invariants", ""])
    for i, d in enumerate(ds, 1):
        lines.append(f"{i}. {d}")
    lines.extend([
        "",
        "### Step 3 — Complete solution (full compilable C or C++ code in fenced block - REAL code, not stubs)",
        "",
        f"```{lang}",
        code.strip(),
        "```",
        "",
        "### Step 4 — Complexity (table or bullets)",
        "",
    ])
    lines.extend(cx)
    lines.extend(["", "### Step 5 — Edge cases (numbered list)", ""])
    for i, e in enumerate(edges, 1):
        lines.append(f"{i}. {e}")
    lines.extend([
        "",
        "### Step 6 — Concurrency / ISR / context notes (if applicable, else \"N/A for this problem\")",
        "",
        conc,
        "",
        "### Step 7 — Follow-up answers (answer each follow-up from the question file)",
        "",
    ])
    if q.followups:
        for fu in q.followups:
            lines.append(f"**Q:** {fu}")
            lines.append("")
            lines.append(f"**A:** {followup_answer(fu, q)}")
            lines.append("")
    else:
        lines.append("_No follow-ups listed in source question._")
        lines.append("")
    lines.extend(["### Step 8 — Tests (test case list + optional small test code)", ""])
    for i, t in enumerate(tests, 1):
        lines.append(f"{i}. {t}")
    lines.extend(["", "Optional harness:", "", f"```{lang}", test_code.strip(), "```", "", "---", ""])
    return "\n".join(lines)


def generate_readme(file_questions: dict[str, list[Question]]) -> str:
    rows = []
    total = 0
    for fname in sorted(file_questions.keys()):
        qs = file_questions[fname]
        if not qs:
            continue
        ids = f"{qs[0].id}–{qs[-1].id}"
        total += len(qs)
        title = fname.replace(".md", "").replace("_", " ").title()
        rows.append(f"| [{fname}](./{fname}) | {ids} | {len(qs)} | {title} |")
    body = "\n".join(rows)
    return f"""# Coding Round Solutions Index

Generated interview-format solutions for all **{total}** coding questions.

| File | IDs | Count | Category |
|------|-----|------:|----------|
{body}

**Total: {total} solutions**

Regenerate: `python3 tools/generate_coding_solutions.py`
"""


def main() -> int:
    SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
    codes = all_solution_codes()
    failed: list[str] = []
    file_questions: dict[str, list[Question]] = {}
    total_sections = 0

    for path in sorted(CODING_DIR.glob("*.md")):
        if path.name == "README.md":
            continue
        questions = parse_question_file(path)
        file_questions[path.name] = questions
        parts = [
            f"# Solutions — {path.stem.replace('_', ' ').title()}",
            "",
            f"**Source:** [`../../coding_rounds/{path.name}`](../../coding_rounds/{path.name})  ",
            f"**Questions:** {len(questions)}  ",
            "",
            "---",
            "",
        ]
        for q in questions:
            code = codes.get(q.id)
            if not code:
                failed.append(q.id)
                code = f"/* Generation failed for {q.id} */"
            code = finalize_code(q, code)
            parts.append(render_solution(q, code))
            total_sections += 1
        out = SOLUTIONS_DIR / path.name
        out.write_text("\n".join(parts) + "\n", encoding="utf-8")
        print(f"Wrote {out} ({len(questions)} solutions)")

    readme = generate_readme(file_questions)
    readme_path = SOLUTIONS_DIR / "README.md"
    readme_path.write_text(readme, encoding="utf-8")
    print(f"Wrote {readme_path}")
    print(f"Total solution sections: {total_sections}")
    if failed:
        print(f"FAILED IDs: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0




if __name__ == "__main__":
    raise SystemExit(main())
