# Topic 1 — Memory Management Interview Solutions (Q001-Q018)

## Q001: Fixed-size memory pool allocator (init/alloc/free)
### 1. Problem Statement
Implement deterministic O(1) allocation/free from a preallocated arena.

### 2. Assumptions
- Fixed block size.
- Caller passes aligned arena.

### 3. Full C Code
```c
typedef struct PoolNode {
    struct PoolNode *next;
} PoolNode;

typedef struct {
    unsigned char *arena;
    size_t block_size;
    size_t block_count;
    PoolNode *free_head;
} FixedPool;

void fixed_pool_init(FixedPool *p, void *arena, size_t block_size, size_t block_count) {
    p->arena = (unsigned char *)arena;
    p->block_size = block_size;
    p->block_count = block_count;
    p->free_head = NULL;

    for (size_t i = 0; i < block_count; i++) {
        PoolNode *n = (PoolNode *)(p->arena + i * block_size);
        n->next = p->free_head;
        p->free_head = n;
    }
}

void *fixed_pool_alloc(FixedPool *p) {
    if (!p->free_head) {
        return NULL;
    }
    PoolNode *n = p->free_head;
    p->free_head = n->next;
    return n;
}

void fixed_pool_free(FixedPool *p, void *ptr) {
    if (!ptr) {
        return;
    }
    PoolNode *n = (PoolNode *)ptr;
    n->next = p->free_head;
    p->free_head = n;
}
```

### 4. Complexity
- Alloc: O(1)
- Free: O(1)
- Space overhead: one pointer per free block

### 5. Interview Follow-ups
1. How do you detect invalid pointer free?
2. How do you enforce alignment guarantees?

## Q002: Fixed pool with guard-byte corruption check
### 1. Problem Statement
Detect out-of-bounds writes around allocated payload.

### 2. Assumptions
- Debug mode instrumentation enabled.

### 3. Full C Code
```c
#include <stdint.h>
#include <stdbool.h>

#define PRE_GUARD  0xDEADBEEFu
#define POST_GUARD 0xBAADF00Du

typedef struct {
    uint32_t pre;
    uint8_t payload[32];
    uint32_t post;
} GuardedBlock;

void guarded_block_init(GuardedBlock *b) {
    b->pre = PRE_GUARD;
    b->post = POST_GUARD;
}

bool guarded_block_ok(const GuardedBlock *b) {
    return (b->pre == PRE_GUARD) && (b->post == POST_GUARD);
}
```

### 4. Complexity
- Check: O(1)

### 5. Interview Follow-ups
1. What is the runtime overhead in production?
2. How do you report corruption source quickly?

## Q003: Fixed pool with leak counter and stats API
### 1. Problem Statement
Track usage stats and allocation failures.

### 2. Assumptions
- Single-threaded updates or external synchronization.

### 3. Full C Code
```c
typedef struct {
    unsigned in_use;
    unsigned peak_in_use;
    unsigned alloc_failures;
} PoolStats;

void pool_stats_on_alloc(PoolStats *s, int success) {
    if (success) {
        s->in_use++;
        if (s->in_use > s->peak_in_use) {
            s->peak_in_use = s->in_use;
        }
    } else {
        s->alloc_failures++;
    }
}

void pool_stats_on_free(PoolStats *s) {
    if (s->in_use > 0) {
        s->in_use--;
    }
}
```

### 4. Complexity
- O(1) per event

### 5. Interview Follow-ups
1. How do you make counters thread-safe?
2. What extra metrics help for production telemetry?

## Q004: Variable-size free-list allocator (first-fit)
### 1. Problem Statement
Allocate variable-sized chunks from a static arena.

### 2. Assumptions
- Header precedes each free block.

### 3. Full C Code
```c
typedef struct FreeBlock {
    size_t size;
    struct FreeBlock *next;
} FreeBlock;

static size_t align8(size_t n) {
    return (n + 7u) & ~7u;
}

void *freelist_alloc(FreeBlock **head, size_t n) {
    n = align8(n);
    FreeBlock *prev = NULL;
    FreeBlock *cur = *head;

    while (cur) {
        if (cur->size >= n) {
            size_t rem = cur->size - n;
            if (rem > sizeof(FreeBlock) + 8u) {
                FreeBlock *split = (FreeBlock *)((unsigned char *)cur + sizeof(FreeBlock) + n);
                split->size = rem - sizeof(FreeBlock);
                split->next = cur->next;
                if (prev) {
                    prev->next = split;
                } else {
                    *head = split;
                }
                cur->size = n;
            } else {
                if (prev) {
                    prev->next = cur->next;
                } else {
                    *head = cur->next;
                }
            }
            return (unsigned char *)cur + sizeof(FreeBlock);
        }
        prev = cur;
        cur = cur->next;
    }

    return NULL;
}
```

### 4. Complexity
- Worst-case alloc scan: O(n)

### 5. Interview Follow-ups
1. Why first-fit vs best-fit?
2. How do you bound latency in RT paths?

## Q005: Free-list block split logic
### 1. Problem Statement
Split only when remainder can hold a valid free block.

### 2. Assumptions
- Minimum payload > 0.

### 3. Full C Code
```c
#include <stdbool.h>

bool can_split_block(size_t block_size, size_t requested, size_t header_size, size_t min_payload) {
    return block_size >= requested + header_size + min_payload;
}
```

### 4. Complexity
- O(1)

### 5. Interview Follow-ups
1. What min payload value should you pick?
2. How does split policy impact fragmentation?

## Q006: Free-list coalescing (prev/next/both sides)
### 1. Problem Statement
Merge adjacent free blocks during free.

### 2. Assumptions
- Free-list kept address-sorted.

### 3. Full C Code
```c
void freelist_free(FreeBlock **head, void *ptr, size_t n) {
    if (!ptr) {
        return;
    }

    n = align8(n);
    FreeBlock *block = (FreeBlock *)((unsigned char *)ptr - sizeof(FreeBlock));
    block->size = n;

    FreeBlock *prev = NULL;
    FreeBlock *cur = *head;

    while (cur && cur < block) {
        prev = cur;
        cur = cur->next;
    }

    block->next = cur;
    if (prev) {
        prev->next = block;
    } else {
        *head = block;
    }

    if (block->next &&
        (unsigned char *)block + sizeof(FreeBlock) + block->size == (unsigned char *)block->next) {
        block->size += sizeof(FreeBlock) + block->next->size;
        block->next = block->next->next;
    }

    if (prev &&
        (unsigned char *)prev + sizeof(FreeBlock) + prev->size == (unsigned char *)block) {
        prev->size += sizeof(FreeBlock) + block->size;
        prev->next = block->next;
    }
}
```

### 4. Complexity
- O(n) insertion + O(1) coalesce checks

### 5. Interview Follow-ups
1. What if list is unsorted?
2. How do you detect double-free?

## Q007: Buddy allocator (allocate by order)
### 1. Problem Statement
Allocate power-of-two chunk from per-order lists.

### 2. Assumptions
- Orders in `[MIN_ORDER, MAX_ORDER]`.

### 3. Full C Code
```c
#define MAX_ORDER 12

typedef struct BuddyNode {
    struct BuddyNode *next;
} BuddyNode;

typedef struct {
    unsigned char *base;
    BuddyNode *free_list[MAX_ORDER + 1];
} BuddyAlloc;

static size_t order_size(int order) {
    return (size_t)1u << order;
}

void *buddy_alloc(BuddyAlloc *a, int order) {
    int k = order;
    while (k <= MAX_ORDER && a->free_list[k] == NULL) {
        k++;
    }
    if (k > MAX_ORDER) {
        return NULL;
    }

    BuddyNode *node = a->free_list[k];
    a->free_list[k] = node->next;

    while (k > order) {
        k--;
        BuddyNode *buddy = (BuddyNode *)((unsigned char *)node + order_size(k));
        buddy->next = a->free_list[k];
        a->free_list[k] = buddy;
    }

    return node;
}
```

### 4. Complexity
- O(log N)

### 5. Interview Follow-ups
1. Where does internal fragmentation come from?
2. How do you verify order correctness on free?

## Q008: Buddy allocator (free + recursive merge)
### 1. Problem Statement
Free a block and recursively merge with free buddy.

### 2. Assumptions
- Caller provides correct order.

### 3. Full C Code
```c
static size_t buddy_offset(BuddyAlloc *a, void *ptr) {
    return (size_t)((unsigned char *)ptr - a->base);
}

static size_t buddy_of(size_t offset, int order) {
    return offset ^ ((size_t)1u << order);
}

void buddy_free(BuddyAlloc *a, void *ptr, int order) {
    size_t off = buddy_offset(a, ptr);

    while (order < MAX_ORDER) {
        size_t boff = buddy_of(off, order);
        BuddyNode *prev = NULL;
        BuddyNode *cur = a->free_list[order];

        while (cur) {
            size_t coff = buddy_offset(a, cur);
            if (coff == boff) {
                break;
            }
            prev = cur;
            cur = cur->next;
        }

        if (!cur) {
            break;
        }

        if (prev) {
            prev->next = cur->next;
        } else {
            a->free_list[order] = cur->next;
        }

        if (boff < off) {
            off = boff;
        }
        order++;
    }

    BuddyNode *n = (BuddyNode *)(a->base + off);
    n->next = a->free_list[order];
    a->free_list[order] = n;
}
```

### 4. Complexity
- O(log N)

### 5. Interview Follow-ups
1. How do you test merge correctness?
2. How do you store block order metadata safely?

## Q009: Slab allocator for fixed objects
### 1. Problem Statement
Fast allocator specialized for same-size objects.

### 2. Assumptions
- Object size fixed per cache.

### 3. Full C Code
```c
typedef struct SlabObj {
    struct SlabObj *next;
} SlabObj;

typedef struct {
    SlabObj *free_head;
    size_t obj_size;
} SlabCache;

void *slab_alloc(SlabCache *c) {
    if (!c->free_head) {
        return NULL;
    }
    SlabObj *o = c->free_head;
    c->free_head = o->next;
    return o;
}

void slab_free(SlabCache *c, void *ptr) {
    SlabObj *o = (SlabObj *)ptr;
    o->next = c->free_head;
    c->free_head = o;
}
```

### 4. Complexity
- O(1) alloc/free

### 5. Interview Follow-ups
1. Why slab is common in kernels/drivers?
2. How do you handle cache growth/shrink?

## Q010: Slab cache with constructor/destructor hooks
### 1. Problem Statement
Run object lifecycle hooks automatically.

### 2. Assumptions
- Hooks are optional.

### 3. Full C Code
```c
typedef void (*obj_ctor_t)(void *);
typedef void (*obj_dtor_t)(void *);

void *slab_alloc_with_ctor(SlabCache *c, obj_ctor_t ctor) {
    void *obj = slab_alloc(c);
    if (obj && ctor) {
        ctor(obj);
    }
    return obj;
}

void slab_free_with_dtor(SlabCache *c, void *obj, obj_dtor_t dtor) {
    if (!obj) {
        return;
    }
    if (dtor) {
        dtor(obj);
    }
    slab_free(c, obj);
}
```

### 4. Complexity
- O(1) + hook cost

### 5. Interview Follow-ups
1. What if constructor fails?
2. Should destructor run in interrupt context?

## Q011: Bitmap allocator for IDs/blocks
### 1. Problem Statement
Allocate small integer IDs efficiently.

### 2. Assumptions
- Bitmap words are `uint32_t`.

### 3. Full C Code
```c
int bitmap_alloc(uint32_t *bm, size_t words) {
    for (size_t i = 0; i < words; i++) {
        if (~bm[i]) {
            uint32_t free_bit = (~bm[i]) & (bm[i] + 1u);
            bm[i] |= free_bit;
            return (int)(i * 32u + __builtin_ctz(free_bit));
        }
    }
    return -1;
}

void bitmap_free(uint32_t *bm, int id) {
    bm[id / 32] &= ~(1u << (id % 32));
}
```

### 4. Complexity
- Alloc: O(words)
- Free: O(1)

### 5. Interview Follow-ups
1. How to make this lock-free?
2. How to avoid duplicate free?

## Q012: Bump/region allocator with reset checkpoint
### 1. Problem Statement
Fast linear allocator with bulk reset.

### 2. Assumptions
- No individual free.

### 3. Full C Code
```c
typedef struct {
    unsigned char *base;
    size_t cap;
    size_t off;
} Region;

void region_init(Region *r, void *base, size_t cap) {
    r->base = (unsigned char *)base;
    r->cap = cap;
    r->off = 0;
}

void *region_alloc(Region *r, size_t n) {
    n = (n + 7u) & ~7u;
    if (r->off + n > r->cap) {
        return NULL;
    }
    void *p = r->base + r->off;
    r->off += n;
    return p;
}

size_t region_mark(const Region *r) {
    return r->off;
}

void region_reset_to(Region *r, size_t mark) {
    if (mark <= r->cap) {
        r->off = mark;
    }
}
```

### 4. Complexity
- Alloc/reset: O(1)

### 5. Interview Follow-ups
1. Where is this allocator best used?
2. How do you prevent use-after-reset?

## Q013: Cache-aligned allocator (64-byte alignment)
### 1. Problem Statement
Return aligned pointers for cache/DMA friendliness.

### 2. Assumptions
- Alignment is power-of-two.

### 3. Full C Code
```c
static size_t align_up_pow2(size_t x, size_t a) {
    return (x + (a - 1u)) & ~(a - 1u);
}

void *aligned_arena_alloc(unsigned char *base, size_t *off, size_t cap, size_t n, size_t align) {
    size_t p = align_up_pow2(*off, align);
    if (p + n > cap) {
        return NULL;
    }
    *off = p + n;
    return base + p;
}
```

### 4. Complexity
- O(1)

### 5. Interview Follow-ups
1. Why alignment matters for DMA?
2. How does alignment help false-sharing avoidance?

## Q014: Zero-copy message buffer (reserve/commit/release)
### 1. Problem Statement
Expose producer/consumer pointers without memcpy.

### 2. Assumptions
- Circular buffer with one-slot-open policy.

### 3. Full C Code
```c
typedef struct {
    unsigned char *buf;
    uint32_t cap;
    uint32_t r;
    uint32_t w;
} ZcRing;

unsigned char *zc_reserve(ZcRing *z, uint32_t *len) {
    if (((z->w + 1u) % z->cap) == z->r) {
        *len = 0;
        return NULL;
    }

    if (z->w >= z->r) {
        *len = z->cap - z->w - (z->r == 0u ? 1u : 0u);
    } else {
        *len = z->r - z->w - 1u;
    }
    return z->buf + z->w;
}

void zc_commit(ZcRing *z, uint32_t n) {
    z->w = (z->w + n) % z->cap;
}

unsigned char *zc_peek(ZcRing *z, uint32_t *len) {
    if (z->r == z->w) {
        *len = 0;
        return NULL;
    }
    *len = (z->w > z->r) ? (z->w - z->r) : (z->cap - z->r);
    return z->buf + z->r;
}

void zc_release(ZcRing *z, uint32_t n) {
    z->r = (z->r + n) % z->cap;
}
```

### 4. Complexity
- O(1) per operation

### 5. Interview Follow-ups
1. How do you handle two-segment wrap reads?
2. What ownership guarantees are required?

## Q015: Circular DMA buffer read-side index logic
### 1. Problem Statement
Compute readable bytes when DMA updates write index.

### 2. Assumptions
- `hw_w` and `sw_r` are modulo-cap indices.

### 3. Full C Code
```c
uint32_t dma_readable(uint32_t hw_w, uint32_t sw_r, uint32_t cap) {
    return (hw_w + cap - sw_r) % cap;
}
```

### 4. Complexity
- O(1)

### 5. Interview Follow-ups
1. How do you detect DMA overrun?
2. How do you handle cache coherence on RX buffers?

## Q016: Double-buffer DMA manager (ping-pong)
### 1. Problem Statement
Use two buffers alternately for continuous DMA capture.

### 2. Assumptions
- ISR toggles active buffer on half/full callbacks.

### 3. Full C Code
```c
typedef struct {
    unsigned char *buf_a;
    unsigned char *buf_b;
    volatile int active; /* 0 -> DMA writing A, 1 -> DMA writing B */
} PingPongDma;

unsigned char *dma_current_write_buf(PingPongDma *p) {
    return (p->active == 0) ? p->buf_a : p->buf_b;
}

unsigned char *dma_ready_read_buf(PingPongDma *p) {
    return (p->active == 0) ? p->buf_b : p->buf_a;
}

void dma_flip_buffers(PingPongDma *p) {
    p->active ^= 1;
}
```

### 4. Complexity
- O(1)

### 5. Interview Follow-ups
1. What if consumer is slower than producer?
2. How do you signal backpressure?

## Q017: Memory pool for ISR-safe object allocation
### 1. Problem Statement
Provide bounded, non-blocking object allocation for ISR use.

### 2. Assumptions
- Either lock-free ownership or short critical section.

### 3. Full C Code
```c
typedef struct IsrPoolNode {
    struct IsrPoolNode *next;
} IsrPoolNode;

typedef struct {
    IsrPoolNode *free_head;
} IsrPool;

static inline void isr_enter_critical(void) {
    /* platform-specific: disable IRQ/preemption */
}

static inline void isr_exit_critical(void) {
    /* platform-specific: restore IRQ/preemption */
}

void isr_pool_init(IsrPool *p, void *arena, size_t block_size, size_t block_count) {
    p->free_head = NULL;
    unsigned char *base = (unsigned char *)arena;

    for (size_t i = 0; i < block_count; i++) {
        IsrPoolNode *n = (IsrPoolNode *)(base + i * block_size);
        n->next = p->free_head;
        p->free_head = n;
    }
}

void *isr_pool_alloc(IsrPool *p) {
    isr_enter_critical();
    IsrPoolNode *n = p->free_head;
    if (n) {
        p->free_head = n->next;
    }
    isr_exit_critical();
    return n;
}

void isr_pool_free(IsrPool *p, void *obj) {
    if (!obj) {
        return;
    }
    isr_enter_critical();
    IsrPoolNode *n = (IsrPoolNode *)obj;
    n->next = p->free_head;
    p->free_head = n;
    isr_exit_critical();
}
```

### 4. Complexity
- O(1)

### 5. Interview Follow-ups
1. Why avoid malloc/free in ISR?
2. How do you report pool exhaustion?

## Q018: Memory corruption detector using canaries/poison
### 1. Problem Statement
Add debug checks for use-after-free and overwrite bugs.

### 2. Assumptions
- Debug-only overhead accepted.

### 3. Full C Code
```c
#include <string.h>

#define POISON_BYTE 0xA5

void poison_fill(void *ptr, size_t n) {
    memset(ptr, POISON_BYTE, n);
}

int poison_verify(const void *ptr, size_t n) {
    const unsigned char *p = (const unsigned char *)ptr;
    for (size_t i = 0; i < n; i++) {
        if (p[i] != POISON_BYTE) {
            return 0;
        }
    }
    return 1;
}
```

### 4. Complexity
- Fill: O(n)
- Verify: O(n)

### 5. Interview Follow-ups
1. When should poison checks run?
2. How do you minimize runtime impact in release builds?
