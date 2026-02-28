/*
 * linked_list_25_embedded_google.c
 *
 * Final prep document: 25 linked-list problems with full C code,
 * tailored for embedded/system interviews.
 *
 * Build:
 *   cc -std=c11 -Wall -Wextra -pedantic linked_list_25_embedded_google.c -o ll25
 */

#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>
#include <stdatomic.h>

/* =========================================================
 * Shared node types
 * ========================================================= */
typedef struct SNode {
    int data;
    struct SNode *next;
} SNode;

typedef struct DNode {
    int data;
    struct DNode *prev;
    struct DNode *next;
} DNode;

typedef struct RNode {
    int data;
    struct RNode *next;
    struct RNode *random;
} RNode;

typedef struct MNode {
    int data;
    struct MNode *next;
    struct MNode *child;
} MNode;

static SNode *snode_new(int v) {
    SNode *n = (SNode *)malloc(sizeof(SNode));
    if (!n) return NULL;
    n->data = v;
    n->next = NULL;
    return n;
}

static void slist_free(SNode *head) {
    while (head) {
        SNode *n = head->next;
        free(head);
        head = n;
    }
}

/* =========================================================
 * 1) Reverse Linked List (iterative, recursive, reverse every K)
 * ========================================================= */
SNode *reverse_iterative(SNode *head) {
    SNode *prev = NULL, *cur = head;
    while (cur) {
        SNode *nxt = cur->next;
        cur->next = prev;
        prev = cur;
        cur = nxt;
    }
    return prev;
}

SNode *reverse_recursive(SNode *head) {
    if (!head || !head->next) return head;
    SNode *nh = reverse_recursive(head->next);
    head->next->next = head;
    head->next = NULL;
    return nh;
}

SNode *reverse_k_nodes(SNode *head, int k) {
    if (!head || k <= 1) return head;
    SNode *cur = head, *prev = NULL;
    int c = 0;
    while (cur && c < k) {
        SNode *nxt = cur->next;
        cur->next = prev;
        prev = cur;
        cur = nxt;
        c++;
    }
    head->next = reverse_k_nodes(cur, k);
    return prev;
}

/* Interview note (1): O(n) time, O(1) iterative space; recursive uses call stack.
 * Edge tests: empty, single, two nodes, k=1, k>n, k multiple/non-multiple of n.
 */

/* =========================================================
 * 2) Detect Cycle + find loop start + remove loop
 * ========================================================= */
bool has_cycle(SNode *head) {
    SNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return true;
    }
    return false;
}

SNode *find_loop_start(SNode *head) {
    SNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) {
            slow = head;
            while (slow != fast) {
                slow = slow->next;
                fast = fast->next;
            }
            return slow;
        }
    }
    return NULL;
}

void remove_loop(SNode *head) {
    SNode *start = find_loop_start(head);
    if (!start) return;
    SNode *p = start;
    while (p->next != start) p = p->next;
    p->next = NULL;
}

/* Interview note (2): Floyd slow/fast is O(n), O(1) space.
 * Edge tests: no loop, self-loop, loop at head, loop in middle, full loop.
 */

/* =========================================================
 * 3) Merge two sorted lists + merge K sorted lists
 * ========================================================= */
SNode *merge_two_sorted(SNode *a, SNode *b) {
    SNode dummy = {0, NULL};
    SNode *tail = &dummy;
    while (a && b) {
        if (a->data <= b->data) {
            tail->next = a;
            a = a->next;
        } else {
            tail->next = b;
            b = b->next;
        }
        tail = tail->next;
    }
    tail->next = a ? a : b;
    return dummy.next;
}

SNode *merge_k_sorted(SNode **lists, int n) {
    if (!lists || n <= 0) return NULL;
    for (int step = 1; step < n; step *= 2) {
        for (int i = 0; i + step < n; i += 2 * step) {
            lists[i] = merge_two_sorted(lists[i], lists[i + step]);
        }
    }
    return lists[0];
}

/* Interview note (3): Merge-2 is O(n+m), in-place; merge-K pairwise is O(N log K).
 * Edge tests: one/both empty, duplicates, negative values, K=0, K=1.
 */

/* =========================================================
 * 4) Find middle of linked list
 * ========================================================= */
SNode *find_middle(SNode *head) {
    SNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    return slow;
}

/* Interview note (4): O(n) time, O(1) space via fast/slow pointer.
 * Edge tests: empty, one node, even length (define first/second middle), odd length.
 */

/* =========================================================
 * 5) Delete node without head pointer
 * ========================================================= */
bool delete_node_without_head(SNode *node) {
    if (!node || !node->next) return false;
    SNode *victim = node->next;
    node->data = victim->data;
    node->next = victim->next;
    free(victim);
    return true;
}

/* Interview note (5): O(1) by copying next node; cannot delete tail with this API.
 * Edge tests: middle node success, tail node failure, NULL input.
 */

/* =========================================================
 * 6) Check if linked list is palindrome (O(1) extra space)
 * ========================================================= */
bool is_palindrome(SNode *head) {
    if (!head || !head->next) return true;

    SNode *slow = head, *fast = head;
    while (fast->next && fast->next->next) {
        slow = slow->next;
        fast = fast->next->next;
    }

    SNode *second = reverse_iterative(slow->next);
    SNode *p1 = head, *p2 = second;
    bool ok = true;

    while (p2) {
        if (p1->data != p2->data) {
            ok = false;
            break;
        }
        p1 = p1->next;
        p2 = p2->next;
    }

    slow->next = reverse_iterative(second); /* restore */
    return ok;
}

/* Interview note (6): O(n) time, O(1) extra space; restore second half after check.
 * Edge tests: odd/even palindrome, non-palindrome, length 0/1/2.
 */

/* =========================================================
 * 7) Find intersection of two lists
 * ========================================================= */
SNode *get_intersection_node(SNode *a, SNode *b) {
    SNode *p = a, *q = b;
    while (p != q) {
        p = p ? p->next : b;
        q = q ? q->next : a;
    }
    return p;
}

/* Interview note (7): Pointer switching equalizes path lengths, O(n+m), O(1) space.
 * Edge tests: intersecting, non-intersecting, one list empty, same head.
 */

/* =========================================================
 * 8) Implement Singly Linked List from scratch
 * ========================================================= */
typedef struct {
    SNode *head;
} SinglyList;

void sll_init(SinglyList *l) {
    l->head = NULL;
}

bool sll_push_front(SinglyList *l, int v) {
    SNode *n = snode_new(v);
    if (!n) return false;
    n->next = l->head;
    l->head = n;
    return true;
}

bool sll_push_back(SinglyList *l, int v) {
    SNode *n = snode_new(v);
    if (!n) return false;
    if (!l->head) {
        l->head = n;
        return true;
    }
    SNode *p = l->head;
    while (p->next) p = p->next;
    p->next = n;
    return true;
}

bool sll_delete_key(SinglyList *l, int key) {
    SNode *cur = l->head, *prev = NULL;
    while (cur) {
        if (cur->data == key) {
            if (prev) prev->next = cur->next;
            else l->head = cur->next;
            free(cur);
            return true;
        }
        prev = cur;
        cur = cur->next;
    }
    return false;
}

SNode *sll_search(SinglyList *l, int key) {
    SNode *cur = l->head;
    while (cur) {
        if (cur->data == key) return cur;
        cur = cur->next;
    }
    return NULL;
}

void sll_clear(SinglyList *l) {
    slist_free(l->head);
    l->head = NULL;
}

/* Interview note (8): Ensure correct head updates and clear ownership rules.
 * Edge tests: operations on empty list, delete head/tail/missing key, search miss.
 */

/* =========================================================
 * 9) Implement Doubly Linked List
 * ========================================================= */
typedef struct {
    DNode *head;
    DNode *tail;
} DoublyList;

static DNode *dnode_new(int v) {
    DNode *n = (DNode *)malloc(sizeof(DNode));
    if (!n) return NULL;
    n->data = v;
    n->prev = n->next = NULL;
    return n;
}

void dll_init(DoublyList *l) {
    l->head = l->tail = NULL;
}

bool dll_push_front(DoublyList *l, int v) {
    DNode *n = dnode_new(v);
    if (!n) return false;
    n->next = l->head;
    if (l->head) l->head->prev = n;
    l->head = n;
    if (!l->tail) l->tail = n;
    return true;
}

bool dll_push_back(DoublyList *l, int v) {
    DNode *n = dnode_new(v);
    if (!n) return false;
    n->prev = l->tail;
    if (l->tail) l->tail->next = n;
    l->tail = n;
    if (!l->head) l->head = n;
    return true;
}

bool dll_remove(DoublyList *l, DNode *node) {
    if (!node) return false;
    if (node->prev) node->prev->next = node->next;
    else l->head = node->next;
    if (node->next) node->next->prev = node->prev;
    else l->tail = node->prev;
    free(node);
    return true;
}

void dll_clear(DoublyList *l) {
    DNode *cur = l->head;
    while (cur) {
        DNode *n = cur->next;
        free(cur);
        cur = n;
    }
    l->head = l->tail = NULL;
}

/* Interview note (9): O(1) insert/remove with node pointer, good for LRU/driver queues.
 * Edge tests: remove head/tail/middle, singleton transitions, empty clear.
 */

/* =========================================================
 * 10) Implement Circular Linked List
 * ========================================================= */
typedef struct {
    SNode *tail; /* tail->next is head */
} CircularList;

void cll_init(CircularList *c) {
    c->tail = NULL;
}

bool cll_push_back(CircularList *c, int v) {
    SNode *n = snode_new(v);
    if (!n) return false;
    if (!c->tail) {
        n->next = n;
        c->tail = n;
        return true;
    }
    n->next = c->tail->next;
    c->tail->next = n;
    c->tail = n;
    return true;
}

bool cll_pop_front(CircularList *c, int *out) {
    if (!c->tail) return false;
    SNode *head = c->tail->next;
    if (out) *out = head->data;

    if (head == c->tail) {
        c->tail = NULL;
    } else {
        c->tail->next = head->next;
    }
    free(head);
    return true;
}

void cll_clear(CircularList *c) {
    int tmp;
    while (cll_pop_front(c, &tmp)) {}
}

/* Interview note (10): Invariant tail->next == head when non-empty.
 * Edge tests: push/pop singleton, repeated wraparound, pop empty list.
 */

/* =========================================================
 * 11) Implement Free List Allocator (fixed buffer)
 * ========================================================= */
#define POOL_SIZE 1024

typedef struct FreeBlock {
    size_t size;              /* payload bytes in this block */
    struct FreeBlock *next;
} FreeBlock;

typedef struct {
    uint8_t buffer[POOL_SIZE];
    FreeBlock *free_list;
} FreeListAllocator;

static size_t align8(size_t n) {
    return (n + 7u) & ~((size_t)7u);
}

void fla_init(FreeListAllocator *a) {
    a->free_list = (FreeBlock *)a->buffer;
    a->free_list->size = POOL_SIZE - sizeof(FreeBlock);
    a->free_list->next = NULL;
}

void *fla_alloc(FreeListAllocator *a, size_t n) {
    n = align8(n);
    FreeBlock *prev = NULL, *cur = a->free_list;

    while (cur) {
        if (cur->size >= n) {
            size_t remaining = cur->size - n;
            if (remaining > sizeof(FreeBlock) + 8) {
                FreeBlock *split = (FreeBlock *)((uint8_t *)cur + sizeof(FreeBlock) + n);
                split->size = remaining - sizeof(FreeBlock);
                split->next = cur->next;
                if (prev) prev->next = split;
                else a->free_list = split;
                cur->size = n;
            } else {
                if (prev) prev->next = cur->next;
                else a->free_list = cur->next;
            }
            return (uint8_t *)cur + sizeof(FreeBlock);
        }
        prev = cur;
        cur = cur->next;
    }
    return NULL;
}

void fla_free(FreeListAllocator *a, void *ptr, size_t n) {
    if (!ptr || n == 0) return;
    n = align8(n);

    FreeBlock *block = (FreeBlock *)((uint8_t *)ptr - sizeof(FreeBlock));
    block->size = n;

    FreeBlock *prev = NULL, *cur = a->free_list;
    while (cur && cur < block) {
        prev = cur;
        cur = cur->next;
    }
    block->next = cur;
    if (prev) prev->next = block;
    else a->free_list = block;

    /* coalesce with next */
    if (block->next) {
        uint8_t *block_end = (uint8_t *)block + sizeof(FreeBlock) + block->size;
        if (block_end == (uint8_t *)block->next) {
            block->size += sizeof(FreeBlock) + block->next->size;
            block->next = block->next->next;
        }
    }
    /* coalesce with prev */
    if (prev) {
        uint8_t *prev_end = (uint8_t *)prev + sizeof(FreeBlock) + prev->size;
        if (prev_end == (uint8_t *)block) {
            prev->size += sizeof(FreeBlock) + block->size;
            prev->next = block->next;
        }
    }
}

/* Interview note (11): Sorted free list + coalescing, deterministic fixed-pool allocator.
 * Edge tests: split block, exact fit, alloc failure, coalesce left/right/both.
 */

/* =========================================================
 * 12) Flatten Multilevel Linked List
 * ========================================================= */
MNode *flatten_multilevel(MNode *head) {
    MNode *cur = head;
    while (cur) {
        if (cur->child) {
            MNode *next = cur->next;
            cur->next = cur->child;
            cur->child = NULL;

            MNode *tail = cur->next;
            while (tail->next) tail = tail->next;
            tail->next = next;
        }
        cur = cur->next;
    }
    return head;
}

/* Interview note (12): Splice child list in place and reconnect saved next pointer.
 * Edge tests: no child, nested child chains, child at tail.
 */

/* =========================================================
 * 13) Partition linked list around pivot x
 * ========================================================= */
SNode *partition_list(SNode *head, int x) {
    SNode less_dummy = {0, NULL}, ge_dummy = {0, NULL};
    SNode *lt = &less_dummy, *ge = &ge_dummy;

    while (head) {
        SNode *nxt = head->next;
        head->next = NULL;
        if (head->data < x) {
            lt->next = head;
            lt = head;
        } else {
            ge->next = head;
            ge = head;
        }
        head = nxt;
    }

    lt->next = ge_dummy.next;
    return less_dummy.next;
}

/* Interview note (13): Build <x and >=x chains then concatenate, O(n), O(1) extra.
 * Edge tests: all <x, all >=x, duplicates equal to pivot, empty list.
 */

/* =========================================================
 * 14) Rotate linked list right by k
 * ========================================================= */
SNode *rotate_right(SNode *head, int k) {
    if (!head || !head->next || k <= 0) return head;

    int n = 1;
    SNode *tail = head;
    while (tail->next) {
        tail = tail->next;
        n++;
    }

    k %= n;
    if (k == 0) return head;

    tail->next = head; /* make circular temporarily */
    int steps = n - k;
    while (steps--) tail = tail->next;

    SNode *new_head = tail->next;
    tail->next = NULL;
    return new_head;
}

/* Interview note (14): Convert to temporary cycle then cut at new tail.
 * Edge tests: k=0, k%n=0, k>n, one node, empty list.
 */

/* =========================================================
 * 15) Intrusive Linked List (Linux-kernel style)
 * ========================================================= */
struct list_head {
    struct list_head *next;
    struct list_head *prev;
};

static inline void INIT_LIST_HEAD(struct list_head *h) {
    h->next = h;
    h->prev = h;
}

static inline void __list_add(struct list_head *n,
                              struct list_head *prev,
                              struct list_head *next) {
    next->prev = n;
    n->next = next;
    n->prev = prev;
    prev->next = n;
}

static inline void list_add(struct list_head *n, struct list_head *head) {
    __list_add(n, head, head->next);
}

static inline void list_add_tail(struct list_head *n, struct list_head *head) {
    __list_add(n, head->prev, head);
}

static inline void __list_del(struct list_head *prev, struct list_head *next) {
    next->prev = prev;
    prev->next = next;
}

static inline void list_del(struct list_head *entry) {
    __list_del(entry->prev, entry->next);
    entry->next = entry->prev = NULL;
}

/* Interview note (15): Intrusive lists avoid extra allocations; node lives in owner struct.
 * Edge tests: add head/tail, delete only node, iterate-delete safety patterns.
 */

/* =========================================================
 * 16) container_of() macro
 * ========================================================= */
#define container_of(ptr, type, member) ((type *)((char *)(ptr) - offsetof(type, member)))

/* Example container */
struct task {
    int id;
    struct list_head node;
};

/* Interview note (16): container_of enables generic intrusive list traversal.
 * Edge tests: recovered outer pointer should equal original object pointer.
 */

/* =========================================================
 * 17) Remove Nth node from end
 * ========================================================= */
SNode *remove_nth_from_end(SNode *head, int n) {
    if (n <= 0) return head;

    SNode dummy = {0, head};
    SNode *fast = &dummy, *slow = &dummy;

    for (int i = 0; i < n; i++) {
        if (!fast->next) return head;
        fast = fast->next;
    }

    while (fast->next) {
        fast = fast->next;
        slow = slow->next;
    }

    SNode *victim = slow->next;
    if (victim) {
        slow->next = victim->next;
        free(victim);
    }
    return dummy.next;
}

/* Interview note (17): Maintain n-gap fast/slow pointers; dummy simplifies head deletion.
 * Edge tests: remove head, remove tail, n==len, n>len, n<=0.
 */

/* =========================================================
 * 18) Clone list with random pointer (O(1) extra memory)
 * ========================================================= */
RNode *clone_random_list(RNode *head) {
    if (!head) return NULL;

    /* 1) interleave clones */
    for (RNode *cur = head; cur;) {
        RNode *clone = (RNode *)malloc(sizeof(RNode));
        if (!clone) return NULL; /* simplified fail handling */
        clone->data = cur->data;
        clone->random = NULL;
        clone->next = cur->next;
        cur->next = clone;
        cur = clone->next;
    }

    /* 2) assign random pointers */
    for (RNode *cur = head; cur; cur = cur->next->next) {
        RNode *clone = cur->next;
        clone->random = cur->random ? cur->random->next : NULL;
    }

    /* 3) detach */
    RNode *clone_head = head->next;
    for (RNode *cur = head; cur;) {
        RNode *clone = cur->next;
        cur->next = clone->next;
        clone->next = clone->next ? clone->next->next : NULL;
        cur = cur->next;
    }

    return clone_head;
}

/* Interview note (18): Interleaving clones avoids hashmap; O(n) time, O(1) extra.
 * Edge tests: NULL randoms, self-random, shared random targets.
 */

/* =========================================================
 * 19) Reverse alternate K nodes
 * ========================================================= */
SNode *reverse_alternate_k(SNode *head, int k) {
    if (!head || k <= 1) return head;

    /* reverse first k */
    SNode *cur = head, *prev = NULL;
    int count = 0;
    while (cur && count < k) {
        SNode *nxt = cur->next;
        cur->next = prev;
        prev = cur;
        cur = nxt;
        count++;
    }

    /* skip next k */
    head->next = cur;
    count = 0;
    while (count < k - 1 && cur) {
        cur = cur->next;
        count++;
    }

    if (cur && cur->next) {
        cur->next = reverse_alternate_k(cur->next, k);
    }

    return prev;
}

/* Interview note (19): Reverse K, skip K pattern; recursion adds stack usage.
 * Edge tests: len<k, len in [k,2k), exact multiples, k<=1.
 */

/* =========================================================
 * 20) Detect and remove duplicate nodes (unsorted, no extra memory)
 * ========================================================= */
void remove_duplicates_no_extra(SNode *head) {
    for (SNode *cur = head; cur; cur = cur->next) {
        SNode *runner = cur;
        while (runner->next) {
            if (runner->next->data == cur->data) {
                SNode *dup = runner->next;
                runner->next = dup->next;
                free(dup);
            } else {
                runner = runner->next;
            }
        }
    }
}

/* Interview note (20): Runner method is O(n^2), O(1) space with no extra memory.
 * Edge tests: all unique, all duplicates, duplicates at head/tail/scattered.
 */

/* =========================================================
 * 21) LRU Cache (doubly list + hash map)
 * ========================================================= */
typedef struct LRUNode {
    int key;
    int value;
    struct LRUNode *prev;
    struct LRUNode *next;
} LRUNode;

typedef struct HEntry {
    int key;
    LRUNode *node;
    struct HEntry *next;
} HEntry;

typedef struct {
    int capacity;
    int size;
    int buckets;
    HEntry **table;
    LRUNode *head; /* MRU */
    LRUNode *tail; /* LRU */
} LRUCache;

static unsigned lru_hash(int key, int buckets) {
    return ((unsigned)key * 2654435761u) % (unsigned)buckets;
}

static HEntry *hentry_find(HEntry **table, int buckets, int key) {
    unsigned idx = lru_hash(key, buckets);
    HEntry *e = table[idx];
    while (e) {
        if (e->key == key) return e;
        e = e->next;
    }
    return NULL;
}

static void hentry_put(HEntry **table, int buckets, int key, LRUNode *node) {
    unsigned idx = lru_hash(key, buckets);
    HEntry *e = (HEntry *)malloc(sizeof(HEntry));
    if (!e) return;
    e->key = key;
    e->node = node;
    e->next = table[idx];
    table[idx] = e;
}

static void hentry_remove(HEntry **table, int buckets, int key) {
    unsigned idx = lru_hash(key, buckets);
    HEntry *cur = table[idx], *prev = NULL;
    while (cur) {
        if (cur->key == key) {
            if (prev) prev->next = cur->next;
            else table[idx] = cur->next;
            free(cur);
            return;
        }
        prev = cur;
        cur = cur->next;
    }
}

static void lru_attach_front(LRUCache *c, LRUNode *n) {
    n->prev = NULL;
    n->next = c->head;
    if (c->head) c->head->prev = n;
    c->head = n;
    if (!c->tail) c->tail = n;
}

static void lru_detach(LRUCache *c, LRUNode *n) {
    if (n->prev) n->prev->next = n->next;
    else c->head = n->next;
    if (n->next) n->next->prev = n->prev;
    else c->tail = n->prev;
    n->prev = n->next = NULL;
}

LRUCache *lru_create(int capacity) {
    if (capacity <= 0) return NULL;
    LRUCache *c = (LRUCache *)calloc(1, sizeof(LRUCache));
    if (!c) return NULL;
    c->capacity = capacity;
    c->buckets = capacity * 2 + 1;
    c->table = (HEntry **)calloc((size_t)c->buckets, sizeof(HEntry *));
    if (!c->table) {
        free(c);
        return NULL;
    }
    return c;
}

int lru_get(LRUCache *c, int key, bool *found) {
    HEntry *e = hentry_find(c->table, c->buckets, key);
    if (!e) {
        if (found) *found = false;
        return 0;
    }
    LRUNode *n = e->node;
    lru_detach(c, n);
    lru_attach_front(c, n);
    if (found) *found = true;
    return n->value;
}

void lru_put(LRUCache *c, int key, int value) {
    HEntry *e = hentry_find(c->table, c->buckets, key);
    if (e) {
        e->node->value = value;
        lru_detach(c, e->node);
        lru_attach_front(c, e->node);
        return;
    }

    if (c->size == c->capacity) {
        LRUNode *victim = c->tail;
        if (victim) {
            hentry_remove(c->table, c->buckets, victim->key);
            lru_detach(c, victim);
            free(victim);
            c->size--;
        }
    }

    LRUNode *n = (LRUNode *)calloc(1, sizeof(LRUNode));
    if (!n) return;
    n->key = key;
    n->value = value;
    lru_attach_front(c, n);
    hentry_put(c->table, c->buckets, key, n);
    c->size++;
}

void lru_destroy(LRUCache *c) {
    if (!c) return;
    LRUNode *n = c->head;
    while (n) {
        LRUNode *x = n->next;
        free(n);
        n = x;
    }
    for (int i = 0; i < c->buckets; i++) {
        HEntry *e = c->table[i];
        while (e) {
            HEntry *x = e->next;
            free(e);
            e = x;
        }
    }
    free(c->table);
    free(c);
}

/* Interview note (21): get/put O(1) average via hashmap + doubly list.
 * Edge tests: overwrite existing key, eviction order, repeated get reorder, capacity=1.
 */

/* =========================================================
 * 22) Timer Queue (sorted linked list by expiry tick)
 * ========================================================= */
typedef void (*timer_cb)(void *);

typedef struct TimerNode {
    uint32_t expiry;
    timer_cb cb;
    void *arg;
    struct TimerNode *next;
} TimerNode;

typedef struct {
    TimerNode *head;
} TimerQueue;

void timerq_init(TimerQueue *q) {
    q->head = NULL;
}

bool timerq_add(TimerQueue *q, uint32_t expiry, timer_cb cb, void *arg) {
    TimerNode *n = (TimerNode *)malloc(sizeof(TimerNode));
    if (!n) return false;
    n->expiry = expiry;
    n->cb = cb;
    n->arg = arg;
    n->next = NULL;

    if (!q->head || expiry < q->head->expiry) {
        n->next = q->head;
        q->head = n;
        return true;
    }

    TimerNode *cur = q->head;
    while (cur->next && cur->next->expiry <= expiry) cur = cur->next;
    n->next = cur->next;
    cur->next = n;
    return true;
}

void timerq_run_expired(TimerQueue *q, uint32_t now) {
    while (q->head && q->head->expiry <= now) {
        TimerNode *n = q->head;
        q->head = n->next;
        if (n->cb) n->cb(n->arg);
        free(n);
    }
}

void timerq_clear(TimerQueue *q) {
    while (q->head) {
        TimerNode *n = q->head->next;
        free(q->head);
        q->head = n;
    }
}

/* Interview note (22): Sorted insert O(n), pop expired from head in O(k).
 * Edge tests: equal expiries (tie policy), none expired, all expired.
 */

/* =========================================================
 * 23) Task Scheduler Queue (priority sorted)
 * ========================================================= */
typedef struct TaskNode {
    int task_id;
    int priority; /* lower is higher priority */
    struct TaskNode *next;
} TaskNode;

typedef struct {
    TaskNode *head;
} TaskQueue;

void taskq_init(TaskQueue *q) {
    q->head = NULL;
}

bool taskq_push(TaskQueue *q, int task_id, int priority) {
    TaskNode *n = (TaskNode *)malloc(sizeof(TaskNode));
    if (!n) return false;
    n->task_id = task_id;
    n->priority = priority;
    n->next = NULL;

    if (!q->head || priority < q->head->priority) {
        n->next = q->head;
        q->head = n;
        return true;
    }

    TaskNode *cur = q->head;
    while (cur->next && cur->next->priority <= priority) cur = cur->next;
    n->next = cur->next;
    cur->next = n;
    return true;
}

bool taskq_pop(TaskQueue *q, int *task_id) {
    if (!q->head) return false;
    TaskNode *n = q->head;
    q->head = n->next;
    if (task_id) *task_id = n->task_id;
    free(n);
    return true;
}

void taskq_clear(TaskQueue *q) {
    while (q->head) {
        TaskNode *n = q->head->next;
        free(q->head);
        q->head = n;
    }
}

/* Interview note (23): Priority-sorted queue is simple and predictable for small systems.
 * Edge tests: equal priorities, pop empty queue, mixed push/pop sequence.
 */

/* =========================================================
 * 24) Memory Block List (free blocks, split+merge)
 * ========================================================= */
typedef struct Block {
    size_t start;
    size_t size;
    struct Block *next;
} Block;

typedef struct {
    size_t total;
    Block *free_blocks;
} MemBlockList;

void mbl_init(MemBlockList *m, size_t total) {
    m->total = total;
    m->free_blocks = (Block *)malloc(sizeof(Block));
    if (!m->free_blocks) return;
    m->free_blocks->start = 0;
    m->free_blocks->size = total;
    m->free_blocks->next = NULL;
}

bool mbl_alloc(MemBlockList *m, size_t req, size_t *out_start) {
    Block *prev = NULL, *cur = m->free_blocks;
    while (cur) {
        if (cur->size >= req) {
            if (out_start) *out_start = cur->start;
            cur->start += req;
            cur->size -= req;
            if (cur->size == 0) {
                if (prev) prev->next = cur->next;
                else m->free_blocks = cur->next;
                free(cur);
            }
            return true;
        }
        prev = cur;
        cur = cur->next;
    }
    return false;
}

void mbl_free(MemBlockList *m, size_t start, size_t size) {
    Block *n = (Block *)malloc(sizeof(Block));
    if (!n) return;
    n->start = start;
    n->size = size;
    n->next = NULL;

    Block *prev = NULL, *cur = m->free_blocks;
    while (cur && cur->start < start) {
        prev = cur;
        cur = cur->next;
    }
    n->next = cur;
    if (prev) prev->next = n;
    else m->free_blocks = n;

    if (n->next && n->start + n->size == n->next->start) {
        Block *x = n->next;
        n->size += x->size;
        n->next = x->next;
        free(x);
    }
    if (prev && prev->start + prev->size == n->start) {
        prev->size += n->size;
        prev->next = n->next;
        free(n);
    }
}

void mbl_clear(MemBlockList *m) {
    Block *cur = m->free_blocks;
    while (cur) {
        Block *n = cur->next;
        free(cur);
        cur = n;
    }
    m->free_blocks = NULL;
}

/* Interview note (24): Keep free blocks sorted and coalesce adjacent regions.
 * Edge tests: fragmentation+merge, full alloc/free cycle, failed allocation.
 */

/* =========================================================
 * 25) Lock-Free SPSC Queue (linked-list based)
 * ========================================================= */
typedef struct SPSCNode {
    int value;
    _Atomic(struct SPSCNode *) next;
} SPSCNode;

typedef struct {
    _Atomic(SPSCNode *) head; /* consumer owns old head */
    _Atomic(SPSCNode *) tail; /* producer appends at tail */
} SPSCQueue;

bool spsc_init(SPSCQueue *q) {
    SPSCNode *stub = (SPSCNode *)calloc(1, sizeof(SPSCNode));
    if (!stub) return false;
    atomic_store_explicit(&stub->next, NULL, memory_order_relaxed);
    atomic_store_explicit(&q->head, stub, memory_order_relaxed);
    atomic_store_explicit(&q->tail, stub, memory_order_relaxed);
    return true;
}

bool spsc_enqueue(SPSCQueue *q, int value) {
    SPSCNode *n = (SPSCNode *)malloc(sizeof(SPSCNode));
    if (!n) return false;
    n->value = value;
    atomic_store_explicit(&n->next, NULL, memory_order_relaxed);

    SPSCNode *tail = atomic_load_explicit(&q->tail, memory_order_relaxed);
    atomic_store_explicit(&tail->next, n, memory_order_release);
    atomic_store_explicit(&q->tail, n, memory_order_release);
    return true;
}

bool spsc_dequeue(SPSCQueue *q, int *out) {
    SPSCNode *head = atomic_load_explicit(&q->head, memory_order_relaxed);
    SPSCNode *next = atomic_load_explicit(&head->next, memory_order_acquire);
    if (!next) return false;

    if (out) *out = next->value;
    atomic_store_explicit(&q->head, next, memory_order_release);
    free(head); /* old stub */
    return true;
}

void spsc_destroy(SPSCQueue *q) {
    int tmp;
    while (spsc_dequeue(q, &tmp)) {}
    SPSCNode *head = atomic_load_explicit(&q->head, memory_order_relaxed);
    free(head);
    atomic_store_explicit(&q->head, NULL, memory_order_relaxed);
    atomic_store_explicit(&q->tail, NULL, memory_order_relaxed);
}

/* Interview note (25): SPSC assumptions are mandatory; one producer, one consumer.
 * Edge tests: empty dequeue, producer burst, full drain, proper destroy lifecycle.
 */

/* =========================================================
 * Minimal helper print and smoke main
 * ========================================================= */
static void print_slist(const SNode *h) {
    while (h) {
        printf("%d", h->data);
        h = h->next;
        if (h) printf(" -> ");
    }
    printf("\n");
}

int main(void) {
    /* Tiny smoke check for core APIs */
    SinglyList l;
    sll_init(&l);
    sll_push_back(&l, 1);
    sll_push_back(&l, 2);
    sll_push_back(&l, 3);
    l.head = reverse_iterative(l.head);
    print_slist(l.head); /* 3 -> 2 -> 1 */
    sll_clear(&l);

    LRUCache *c = lru_create(2);
    if (c) {
        bool found = false;
        lru_put(c, 1, 100);
        lru_put(c, 2, 200);
        (void)lru_get(c, 1, &found);
        lru_put(c, 3, 300); /* evicts key 2 */
        printf("LRU get(2) found=%d\n", (int)(hentry_find(c->table, c->buckets, 2) != NULL));
        lru_destroy(c);
    }

    SPSCQueue q;
    if (spsc_init(&q)) {
        spsc_enqueue(&q, 10);
        spsc_enqueue(&q, 20);
        int x;
        if (spsc_dequeue(&q, &x)) printf("SPSC pop=%d\n", x);
        spsc_destroy(&q);
    }

    return 0;
}
