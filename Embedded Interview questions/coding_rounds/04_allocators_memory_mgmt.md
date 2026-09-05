# Allocators & Memory Management

**IDs:** C056–C070 (15 questions)  
**Focus:** Pools, freelists, bump/arena, buddy, refcounted buffers.

[← Back to category index](./README.md)

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


---

[← Back to category index](./README.md)
