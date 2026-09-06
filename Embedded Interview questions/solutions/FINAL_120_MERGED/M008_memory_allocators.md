# M008 — Memory allocators (pools → heap → special)

**Type:** Coding (C)  
**Merged from:** Q029, Q030, Q031, Q032, Q033, Q034, Q035, Q036  
**Companies:** Google · Apple · Tesla · NVIDIA · Qualcomm  
**Tier:** S (must-know)

**Question:** Fixed-size pool O(1), ISR-safe pool, guard/poison stats; variable freelist; buddy sketch; DMA-aligned and bump allocators.

---

## Sub-variant coverage

| Original Q | Sub-variant |
|---|---|
| Q029 | Fragmentation |
| Q030 | TLSF mention |
| Q031 | Handle indirection |
| Q032 | Double-free detection |
| Q033 | See merged solution |
| Q034 | See merged solution |
| Q035 | See merged solution |
| Q036 | See merged solution |

---

## Step 0 — Clarifying questions (say these out loud)

- **Candidate:** Alloc from ISR allowed?
- **Candidate:** Fixed block size or variable heap?

## Step 1 — Approach

Build Memory allocators (pools → heap → special) in layers: invariants first, happy path, then edge cases and concurrency.

- Restate API signatures and invariants aloud before coding.
- Implement core logic with straightforward loops; optimize after tests pass.
- Document ownership, error codes, and ISR vs task context.

## Step 2 — Data structures / invariants

1. Structs/enums matching API — invariants in comments.
2. Platform hooks (`irq_save`, `now_ms`) isolated for host test fakes.

## Step 3 — Complete solution (compilable C)

```c
#include <stdint.h>
#include <stddef.h>
typedef struct pool_node {
    struct pool_node *next;
}
pool_node_t;
typedef struct {
    unsigned char *arena;
    size_t block_size, block_count;
    pool_node_t *free_head;
}
pool_t;
int pool_init(pool_t *p,void *backing,size_t backing_size,size_t block_size) {
    if(!p||!backing||block_size<sizeof(pool_node_t))return -1;
    p->arena=backing;
    p->block_size=block_size;
    p->block_count=backing_size/block_size;
    p->free_head=0;
    for(size_t i=0;
    i<p->block_count;
    ++i) {
        pool_node_t *n=(pool_node_t*)(p->arena+i*block_size);
        n->next=p->free_head;
        p->free_head=n;
    }
    return 0;
}
void *pool_alloc(pool_t *p) {
    if(!p||!p->free_head)return 0;
    pool_node_t *n=p->free_head;
    p->free_head=n->next;
    return n;
}
void pool_free(pool_t *p,void *blk) {
    if(!p||!blk)return;
    pool_node_t *n=blk;
    n->next=p->free_head;
    p->free_head=n;
}
/* --- next section --- */
#include <stdint.h>
#include <stddef.h>
#include <stdatomic.h>
typedef struct {
    unsigned char *arena;
    size_t block_size, block_count;
    _Atomic(pool_node_t*) free_head;
}
pool_t;
typedef struct pool_node {
    struct pool_node *next;
}
pool_node_t;
void *pool_alloc_isrsafe(pool_t *p) {
    pool_node_t *n=atomic_load(&p->free_head);
    while(n) {
        pool_node_t *next=n->next;
        if(atomic_compare_exchange_weak(&p->free_head,&n,next))return n;
        n=atomic_load(&p->free_head);
    }
    return 0;
}
void pool_free_isrsafe(pool_t *p,void *blk) {
    pool_node_t *n=blk;
    pool_node_t *old=atomic_load(&p->free_head);
    do {
        n->next=old;
    }
    while(!atomic_compare_exchange_weak(&p->free_head,&old,n));
}
/* --- next section --- */
#include <stdint.h>
#include <stddef.h>
typedef struct {
    unsigned char *base;
    size_t size, offset;
}
bump_t;
void bump_init(bump_t *b,void *base,size_t sz) {
    b->base=base;
    b->size=sz;
    b->offset=0;
}
void *bump_alloc(bump_t *b,size_t n) {
    n=(n+7)&~7u;
    if(b->offset+n>b->size)return 0;
    void *p=b->base+b->offset;
    b->offset+=n;
    return p;
}
void bump_reset(bump_t *b) {
    b->offset=0;
}
/* --- next section --- */
#include <stdint.h>
#include <stddef.h>
typedef struct fb {
    size_t size;
    struct fb *next;
}
free_block_t;
void *arena_alloc(free_block_t **head,size_t n) {
    n=(n+7)&~7u;
    free_block_t *prev=0,*cur=*head;
    while(cur) {
        if(cur->size>=n) {
            if(cur->size>n+sizeof(free_block_t)+8) {
                free_block_t *split=(free_block_t*)((char*)cur+sizeof(free_block_t)+n);
                split->size=cur->size-n-sizeof(free_block_t);
                split->next=cur->next;
                cur->size=n;
                cur->next=split;
            }
            else {
                if(prev)prev->next=cur->next;
                else *head=cur->next;
            }
            return (char*)cur+sizeof(free_block_t);
        }
        prev=cur;
        cur=cur->next;
    }
    return 0;
}
```

## Step 4 — Complexity

| Operation | Time | Space |
|---|---:|---:|
| primary API | O(1) typical | O(1) or O(cap) |

## Step 5 — Edge cases

1. NULL / zero-length — defined error or no-op.
2. Boundary at max capacity — no overrun.
3. Repeated calls idempotent where API requires.

## Step 6 — Concurrency / ISR / context notes

ISR alloc only from ISR-safe pool; never malloc in ISR.

## Step 7 — Follow-up answers

**Q: Pool vs heap for RT?**  
**A:** Pool is O(1) deterministic; heap may fragment and invoke malloc latency spikes.


## Step 8 — Tests

1. Happy path — minimal valid input produces expected output.
2. Zero/null/empty — defined error, no crash.
3. Boundary — max capacity or timeout edge.
4. Stress — back-to-back calls or burst traffic.

## Further study

- [Memory Pool Allocation](https://github.com/theEmbeddedGeorge/theEmbeddedNewTestament.github.io/blob/master/Embedded_C/Memory_Pool_Allocation.md)
- [Memory Fragmentation](https://github.com/theEmbeddedGeorge/theEmbeddedNewTestament.github.io/blob/master/Embedded_C/Memory_Fragmentation.md)

---

*Generated by `tools/generate_merged_solutions.py` for M008.*