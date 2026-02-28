# Topic 6 — Embedded Data Structures Interview Solutions (Q069-Q080)

## Q069: Hash table (open addressing)
### 1. Problem Statement
Implement fixed-size open-address map.
### 2. Assumptions
- Linear probing.
### 3. Full C Code
```c
int ht_find_slot(int *keys, uint8_t *used, int cap, int key) {
    int i = (key % cap + cap) % cap;
    for (int n = 0; n < cap; n++) {
        if (!used[i] || keys[i] == key) {
            return i;
        }
        i = (i + 1) % cap;
    }
    return -1;
}
```
### 4. Complexity
- Avg O(1), worst O(n)
### 5. Interview Follow-ups
1. Tombstone handling?
2. Load factor threshold?

## Q070: Hash table (separate chaining with static pool)
### 1. Problem Statement
Use bucket heads + node pool, no dynamic allocation.
### 2. Assumptions
- Node pool index free-list.
### 3. Full C Code
```c
typedef struct {
    int key;
    int val;
    int next;
} ChainNode;

int chain_alloc_node(int *free_head, ChainNode *pool) {
    int idx = *free_head;
    if (idx < 0) {
        return -1;
    }
    *free_head = pool[idx].next;
    return idx;
}
```
### 4. Complexity
- Avg O(1)
### 5. Interview Follow-ups
1. Pool exhaustion path?
2. Delete complexity?

## Q071: Fixed-capacity map (no dynamic allocation)
### 1. Problem Statement
Store key/value pairs in static arrays.
### 2. Assumptions
- Overwrite existing keys.
### 3. Full C Code
```c
int fixed_map_put(int *keys, int *vals, uint8_t *used, int cap, int k, int v) {
    int i = ht_find_slot(keys, used, cap, k);
    if (i < 0) {
        return -1;
    }
    keys[i] = k;
    vals[i] = v;
    used[i] = 1;
    return 0;
}
```
### 4. Complexity
- Avg O(1)
### 5. Interview Follow-ups
1. Eviction policy when full?
2. Determinism under collisions?

## Q072: Binary heap priority queue
### 1. Problem Statement
Implement min-heap push/pop.
### 2. Assumptions
- Array-backed heap.
### 3. Full C Code
```c
void heap_push_int(int *h, int *sz, int x) {
    int i = (*sz)++;
    h[i] = x;
    while (i > 0) {
        int p = (i - 1) / 2;
        if (h[p] <= h[i]) {
            break;
        }
        int t = h[p];
        h[p] = h[i];
        h[i] = t;
        i = p;
    }
}
```
### 4. Complexity
- O(log n)
### 5. Interview Follow-ups
1. Stable ordering support?
2. Fixed max capacity behavior?

## Q073: Indexed priority queue
### 1. Problem Statement
Support priority updates by item ID.
### 2. Assumptions
- `pos[id]` stores heap index.
### 3. Full C Code
```c
void ipq_swap(int *heap, int *pos, int i, int j) {
    int a = heap[i];
    int b = heap[j];
    heap[i] = b;
    heap[j] = a;
    pos[a] = j;
    pos[b] = i;
}
```
### 4. Complexity
- Update O(log n)
### 5. Interview Follow-ups
1. Decrease-key correctness?
2. Invalid ID handling?

## Q074: LRU cache (hash + doubly linked list)
### 1. Problem Statement
Support O(1) get/put with eviction.
### 2. Assumptions
- Hash maps key -> DLL node.
### 3. Full C Code
```c
#include <stdlib.h>

typedef struct LruNode {
    int key;
    int val;
    struct LruNode *prev;
    struct LruNode *next;
} LruNode;

typedef struct LruEnt {
    int key;
    LruNode *node;
    struct LruEnt *next;
} LruEnt;

typedef struct {
    int cap;
    int size;
    int buckets;
    LruEnt **tab;
    LruNode *head; /* MRU */
    LruNode *tail; /* LRU */
} LruCache;

static unsigned lru_hash(int key, int buckets) {
    return ((unsigned)key * 2654435761u) % (unsigned)buckets;
}

static LruEnt *lru_find(LruCache *c, int key) {
    unsigned idx = lru_hash(key, c->buckets);
    LruEnt *e = c->tab[idx];
    while (e) {
        if (e->key == key) return e;
        e = e->next;
    }
    return NULL;
}

static void lru_attach_front(LruCache *c, LruNode *n) {
    n->prev = NULL;
    n->next = c->head;
    if (c->head) c->head->prev = n;
    c->head = n;
    if (!c->tail) c->tail = n;
}

static void lru_detach(LruCache *c, LruNode *n) {
    if (n->prev) n->prev->next = n->next; else c->head = n->next;
    if (n->next) n->next->prev = n->prev; else c->tail = n->prev;
}

LruCache *lru_create(int cap) {
    if (cap <= 0) return NULL;
    LruCache *c = (LruCache *)calloc(1, sizeof(LruCache));
    if (!c) return NULL;
    c->cap = cap;
    c->buckets = cap * 2 + 1;
    c->tab = (LruEnt **)calloc((size_t)c->buckets, sizeof(LruEnt *));
    if (!c->tab) {
        free(c);
        return NULL;
    }
    return c;
}

int lru_get(LruCache *c, int key, int *found) {
    LruEnt *e = lru_find(c, key);
    if (!e) {
        if (found) *found = 0;
        return 0;
    }
    lru_detach(c, e->node);
    lru_attach_front(c, e->node);
    if (found) *found = 1;
    return e->node->val;
}

void lru_put(LruCache *c, int key, int val) {
    LruEnt *e = lru_find(c, key);
    if (e) {
        e->node->val = val;
        lru_detach(c, e->node);
        lru_attach_front(c, e->node);
        return;
    }

    if (c->size == c->cap && c->tail) {
        LruNode *victim = c->tail;
        lru_detach(c, victim);
        free(victim);
        c->size--;
    }

    LruNode *n = (LruNode *)calloc(1, sizeof(LruNode));
    if (!n) return;
    n->key = key;
    n->val = val;
    lru_attach_front(c, n);
    c->size++;
}
```
### 4. Complexity
- Avg O(1)
### 5. Interview Follow-ups
1. Thread-safe LRU design?
2. Memory fragmentation controls?

## Q075: Timer wheel data structure
### 1. Problem Statement
Bucket timers by tick modulo wheel size.
### 2. Assumptions
- Fixed tick granularity.
### 3. Full C Code
```c
typedef struct TwNode {
    uint32_t expiry;
    struct TwNode *next;
} TwNode;

void timer_wheel_add(TwNode **wheel, uint32_t wheel_size, TwNode *n) {
    uint32_t slot = n->expiry % wheel_size;
    n->next = wheel[slot];
    wheel[slot] = n;
}
```
### 4. Complexity
- Insert avg O(1)
### 5. Interview Follow-ups
1. Long timer overflow handling?
2. Precision tradeoff vs min-heap?

## Q076: Min-heap timer queue
### 1. Problem Statement
Keep earliest-expiry timer at root.
### 2. Assumptions
- Heap key is absolute expiry tick.
### 3. Full C Code
```c
typedef struct {
    uint32_t expiry;
    int id;
} TimerItem;

void timer_heap_push(TimerItem *h, int *sz, TimerItem x) {
    int i = (*sz)++;
    h[i] = x;
    while (i > 0) {
        int p = (i - 1) / 2;
        if (h[p].expiry <= h[i].expiry) {
            break;
        }
        TimerItem t = h[p];
        h[p] = h[i];
        h[i] = t;
        i = p;
    }
}
```
### 4. Complexity
- O(log n)
### 5. Interview Follow-ups
1. Tick wrap compare helper?
2. Cancel complexity?

## Q077: Bitmap-based free-slot allocator
### 1. Problem Statement
Allocate first free slot index from bitmap.
### 2. Assumptions
- `uint32_t` word granularity.
### 3. Full C Code
```c
int slot_alloc_bitmap(uint32_t *bm, int words) {
    for (int i = 0; i < words; i++) {
        if (~bm[i]) {
            uint32_t bit = (~bm[i]) & (bm[i] + 1u);
            bm[i] |= bit;
            return i * 32 + __builtin_ctz(bit);
        }
    }
    return -1;
}
```
### 4. Complexity
- O(words)
### 5. Interview Follow-ups
1. Atomic bit ops for multithread?
2. Fragmentation concerns?

## Q078: Intrusive linked list (Linux style)
### 1. Problem Statement
List node embedded in owner object.
### 2. Assumptions
- Circular doubly-linked head sentinel.
### 3. Full C Code
```c
struct list_head {
    struct list_head *next;
    struct list_head *prev;
};

static inline void INIT_LIST_HEAD(struct list_head *h) {
    h->next = h;
    h->prev = h;
}

static inline void list_add(struct list_head *n, struct list_head *h) {
    n->next = h->next;
    n->prev = h;
    h->next->prev = n;
    h->next = n;
}
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Safe iteration while delete?
2. Why intrusive lists in kernels?

## Q079: container_of() macro and usage
### 1. Problem Statement
Recover parent struct pointer from member pointer.
### 2. Assumptions
- Standard-layout struct and valid member pointer.
### 3. Full C Code
```c
#include <stddef.h>

#define container_of(ptr, type, member) \
    ((type *)((char *)(ptr) - offsetof(type, member)))
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. UB pitfalls?
2. Type-safety improvements?

## Q080: Task scheduler run queue (priority + FIFO tie-break)
### 1. Problem Statement
Order tasks by priority and then arrival sequence.
### 2. Assumptions
- Lower priority number runs first.
### 3. Full C Code
```c
typedef struct {
    int task_id;
    int prio;
    int seq;
} SchedTask;

int sched_compare(SchedTask a, SchedTask b) {
    if (a.prio != b.prio) {
        return (a.prio < b.prio) ? -1 : 1;
    }
    return (a.seq < b.seq) ? -1 : (a.seq > b.seq);
}
```
### 4. Complexity
- Depends on backing queue (heap/list)
### 5. Interview Follow-ups
1. Aging strategy to avoid starvation?
2. Real-time determinism guarantees?
