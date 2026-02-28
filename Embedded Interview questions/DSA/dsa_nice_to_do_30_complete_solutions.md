# DSA Nice-to-Do 30 — Complete C Solutions

Style: interview-ready C, clean indentation, edge cases included.

## N01) Merge Sorted Array
### Full C Code
```c
void merge_sorted_array(int *nums1, int m, const int *nums2, int n) {
    int i = m - 1;
    int j = n - 1;
    int w = m + n - 1;

    while (j >= 0) {
        if (i >= 0 && nums1[i] > nums2[j]) nums1[w--] = nums1[i--];
        else nums1[w--] = nums2[j--];
    }
}
```
### Complexity
- Time: O(m + n)
- Space: O(1)
### Interview Follow-ups
- Merging into new buffer vs in-place.

## N02) First Missing Positive
### Full C Code
```c
static void swap_int_n2(int *a, int *b) {
    int t = *a;
    *a = *b;
    *b = t;
}

int first_missing_positive(int *nums, int n) {
    for (int i = 0; i < n; ++i) {
        while (nums[i] >= 1 && nums[i] <= n && nums[nums[i] - 1] != nums[i]) {
            swap_int_n2(&nums[i], &nums[nums[i] - 1]);
        }
    }

    for (int i = 0; i < n; ++i) {
        if (nums[i] != i + 1) return i + 1;
    }
    return n + 1;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Why each number moves limited times.

## N03) Longest Consecutive Sequence
### Full C Code
```c
#include <stdlib.h>

static int cmp_int_n3(const void *a, const void *b) {
    int x = *(const int *)a;
    int y = *(const int *)b;
    return (x > y) - (x < y);
}

int longest_consecutive(int *nums, int n) {
    if (n == 0) return 0;
    qsort(nums, (size_t)n, sizeof(int), cmp_int_n3);

    int best = 1;
    int cur = 1;

    for (int i = 1; i < n; ++i) {
        if (nums[i] == nums[i - 1]) continue;
        if (nums[i] == nums[i - 1] + 1) cur++;
        else cur = 1;
        if (cur > best) best = cur;
    }
    return best;
}
```
### Complexity
- Time: O(n log n)
- Space: O(1) extra (in-place sort)
### Interview Follow-ups
- O(n) hash-set approach.

## N04) Set Matrix Zeroes
### Full C Code
```c
#include <stdbool.h>

void set_zeroes(int **mat, int rows, int cols) {
    bool row0 = false;
    bool col0 = false;

    for (int c = 0; c < cols; ++c) {
        if (mat[0][c] == 0) row0 = true;
    }
    for (int r = 0; r < rows; ++r) {
        if (mat[r][0] == 0) col0 = true;
    }

    for (int r = 1; r < rows; ++r) {
        for (int c = 1; c < cols; ++c) {
            if (mat[r][c] == 0) {
                mat[r][0] = 0;
                mat[0][c] = 0;
            }
        }
    }

    for (int r = 1; r < rows; ++r) {
        for (int c = 1; c < cols; ++c) {
            if (mat[r][0] == 0 || mat[0][c] == 0) mat[r][c] = 0;
        }
    }

    if (row0) {
        for (int c = 0; c < cols; ++c) mat[0][c] = 0;
    }
    if (col0) {
        for (int r = 0; r < rows; ++r) mat[r][0] = 0;
    }
}
```
### Complexity
- Time: O(rows * cols)
- Space: O(1)
### Interview Follow-ups
- If input matrix must stay immutable.

## N05) Trapping Rain Water
### Full C Code
```c
int trap_rain_water(const int *h, int n) {
    int l = 0;
    int r = n - 1;
    int lmax = 0;
    int rmax = 0;
    int ans = 0;

    while (l < r) {
        if (h[l] < h[r]) {
            if (h[l] >= lmax) lmax = h[l];
            else ans += lmax - h[l];
            l++;
        } else {
            if (h[r] >= rmax) rmax = h[r];
            else ans += rmax - h[r];
            r--;
        }
    }
    return ans;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Stack-based alternative.

## N06) Next Permutation
### Full C Code
```c
static void reverse_int_range(int *a, int l, int r) {
    while (l < r) {
        int t = a[l];
        a[l] = a[r];
        a[r] = t;
        l++;
        r--;
    }
}

void next_permutation(int *nums, int n) {
    int i = n - 2;
    while (i >= 0 && nums[i] >= nums[i + 1]) i--;

    if (i >= 0) {
        int j = n - 1;
        while (nums[j] <= nums[i]) j--;
        int t = nums[i];
        nums[i] = nums[j];
        nums[j] = t;
    }

    reverse_int_range(nums, i + 1, n - 1);
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Previous permutation variant.

## N07) Longest Common Prefix
### Full C Code
```c
int longest_common_prefix_len(char **strs, int n) {
    if (n == 0) return 0;

    int i = 0;
    while (strs[0][i] != '\0') {
        char c = strs[0][i];
        for (int j = 1; j < n; ++j) {
            if (strs[j][i] != c) return i;
        }
        i++;
    }
    return i;
}
```
### Complexity
- Time: O(n * m)
- Space: O(1)
### Interview Follow-ups
- Trie-based variant.

## N08) Compare Version Numbers
### Full C Code
```c
int compare_version(const char *v1, const char *v2) {
    int i = 0;
    int j = 0;

    while (v1[i] != '\0' || v2[j] != '\0') {
        long a = 0;
        long b = 0;

        while (v1[i] != '\0' && v1[i] != '.') {
            a = a * 10 + (v1[i] - '0');
            i++;
        }
        while (v2[j] != '\0' && v2[j] != '.') {
            b = b * 10 + (v2[j] - '0');
            j++;
        }

        if (a < b) return -1;
        if (a > b) return 1;

        if (v1[i] == '.') i++;
        if (v2[j] == '.') j++;
    }
    return 0;
}
```
### Complexity
- Time: O(n + m)
- Space: O(1)
### Interview Follow-ups
- Very long segments beyond 64-bit.

## N09) Add Strings
### Full C Code
```c
#include <stdlib.h>
#include <string.h>

char *add_strings(const char *a, const char *b) {
    int n = (int)strlen(a);
    int m = (int)strlen(b);
    int cap = (n > m ? n : m) + 2;

    char *tmp = (char *)malloc((size_t)cap);
    if (!tmp) return NULL;

    int i = n - 1;
    int j = m - 1;
    int k = 0;
    int carry = 0;

    while (i >= 0 || j >= 0 || carry) {
        int x = (i >= 0) ? a[i--] - '0' : 0;
        int y = (j >= 0) ? b[j--] - '0' : 0;
        int sum = x + y + carry;
        tmp[k++] = (char)('0' + (sum % 10));
        carry = sum / 10;
    }

    char *out = (char *)malloc((size_t)k + 1u);
    if (!out) {
        free(tmp);
        return NULL;
    }

    for (int t = 0; t < k; ++t) {
        out[t] = tmp[k - 1 - t];
    }
    out[k] = '\0';
    free(tmp);
    return out;
}
```
### Complexity
- Time: O(max(n, m))
- Space: O(max(n, m))
### Interview Follow-ups
- In-place if mutable buffers available.

## N10) Multiply Strings
### Full C Code
```c
#include <stdlib.h>
#include <string.h>

char *multiply_strings(const char *a, const char *b) {
    int n = (int)strlen(a);
    int m = (int)strlen(b);
    if ((n == 1 && a[0] == '0') || (m == 1 && b[0] == '0')) {
        char *z = (char *)malloc(2);
        if (!z) return NULL;
        z[0] = '0';
        z[1] = '\0';
        return z;
    }

    int len = n + m;
    int *acc = (int *)calloc((size_t)len, sizeof(int));
    if (!acc) return NULL;

    for (int i = n - 1; i >= 0; --i) {
        for (int j = m - 1; j >= 0; --j) {
            int p = (a[i] - '0') * (b[j] - '0');
            int pos2 = i + j + 1;
            int pos1 = i + j;

            int sum = p + acc[pos2];
            acc[pos2] = sum % 10;
            acc[pos1] += sum / 10;
        }
    }

    int start = 0;
    while (start < len && acc[start] == 0) start++;

    int out_len = len - start;
    char *out = (char *)malloc((size_t)out_len + 1u);
    if (!out) {
        free(acc);
        return NULL;
    }

    for (int i = 0; i < out_len; ++i) {
        out[i] = (char)('0' + acc[start + i]);
    }
    out[out_len] = '\0';

    free(acc);
    return out;
}
```
### Complexity
- Time: O(n * m)
- Space: O(n + m)
### Interview Follow-ups
- Base 10^k chunk optimization.

## N11) Permutation in String
### Full C Code
```c
#include <stdbool.h>
#include <string.h>

bool check_inclusion(const char *p, const char *s) {
    int m = (int)strlen(p);
    int n = (int)strlen(s);
    if (m > n) return false;

    int need[26] = {0};
    int win[26] = {0};

    for (int i = 0; i < m; ++i) {
        need[p[i] - 'a']++;
        win[s[i] - 'a']++;
    }

    if (memcmp(need, win, sizeof(need)) == 0) return true;

    for (int r = m; r < n; ++r) {
        win[s[r] - 'a']++;
        win[s[r - m] - 'a']--;
        if (memcmp(need, win, sizeof(need)) == 0) return true;
    }

    return false;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Arbitrary charset.

## N12) Isomorphic Strings
### Full C Code
```c
#include <stdbool.h>

bool is_isomorphic(const char *s, const char *t) {
    int m1[256];
    int m2[256];
    for (int i = 0; i < 256; ++i) {
        m1[i] = -1;
        m2[i] = -1;
    }

    for (int i = 0; s[i] != '\0' && t[i] != '\0'; ++i) {
        unsigned char a = (unsigned char)s[i];
        unsigned char b = (unsigned char)t[i];

        if (m1[a] == -1 && m2[b] == -1) {
            m1[a] = b;
            m2[b] = a;
        } else if (m1[a] != b || m2[b] != a) {
            return false;
        }
    }

    return true;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- UTF-8 code-point mapping.

## N13) Word Pattern
### Full C Code
```c
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    bool used;
    char key;
    char val[64];
} CharWordMap;

typedef struct {
    bool used;
    char key[64];
    char val;
} WordCharMap;

static int split_words(const char *s, char out[][64], int cap) {
    int n = 0;
    int i = 0;

    while (s[i] != '\0') {
        while (s[i] == ' ') i++;
        if (s[i] == '\0') break;

        int j = 0;
        while (s[i] != '\0' && s[i] != ' ' && j < 63) {
            out[n][j++] = s[i++];
        }
        out[n][j] = '\0';
        n++;
        if (n == cap) break;

        while (s[i] != '\0' && s[i] != ' ') i++;
    }

    return n;
}

bool word_pattern(const char *pattern, const char *s) {
    char words[256][64];
    int wc = split_words(s, words, 256);

    int pc = (int)strlen(pattern);
    if (pc != wc) return false;

    CharWordMap cw[256] = {0};
    WordCharMap wcmap[256] = {0};

    for (int i = 0; i < pc; ++i) {
        char p = pattern[i];
        const char *w = words[i];

        int idx1 = (unsigned char)p;
        if (!cw[idx1].used) {
            cw[idx1].used = true;
            cw[idx1].key = p;
            strcpy(cw[idx1].val, w);
        } else if (strcmp(cw[idx1].val, w) != 0) {
            return false;
        }

        int slot = -1;
        for (int j = 0; j < 256; ++j) {
            if (wcmap[j].used && strcmp(wcmap[j].key, w) == 0) {
                slot = j;
                break;
            }
        }
        if (slot == -1) {
            for (int j = 0; j < 256; ++j) {
                if (!wcmap[j].used) {
                    wcmap[j].used = true;
                    strcpy(wcmap[j].key, w);
                    wcmap[j].val = p;
                    slot = j;
                    break;
                }
            }
        }

        if (slot >= 0 && wcmap[slot].val != p) return false;
    }

    return true;
}
```
### Complexity
- Time: O(n * U) where U<=256 in this fixed implementation
- Space: O(U)
### Interview Follow-ups
- Dynamic hash-map implementation.

## N14) Contains Duplicate II
### Full C Code
```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int key;
    int last;
    bool used;
} LastSeenEntry;

static int hash_int_n14(int x, int mod) {
    int h = x % mod;
    return (h < 0) ? h + mod : h;
}

bool contains_nearby_duplicate(const int *nums, int n, int k) {
    int cap = 4 * n + 7;
    LastSeenEntry *map = (LastSeenEntry *)calloc((size_t)cap, sizeof(LastSeenEntry));
    if (!map) return false;

    for (int i = 0; i < n; ++i) {
        int p = hash_int_n14(nums[i], cap);

        while (map[p].used && map[p].key != nums[i]) {
            p = (p + 1) % cap;
        }

        if (map[p].used && i - map[p].last <= k) {
            free(map);
            return true;
        }

        map[p].used = true;
        map[p].key = nums[i];
        map[p].last = i;
    }

    free(map);
    return false;
}
```
### Complexity
- Time: O(n) average
- Space: O(n)
### Interview Follow-ups
- Sliding-window set alternative.

## N15) Happy Number
### Full C Code
```c
#include <stdbool.h>

static int next_happy(int x) {
    int sum = 0;
    while (x > 0) {
        int d = x % 10;
        sum += d * d;
        x /= 10;
    }
    return sum;
}

bool is_happy(int n) {
    int slow = n;
    int fast = n;

    do {
        slow = next_happy(slow);
        fast = next_happy(next_happy(fast));
    } while (slow != fast);

    return slow == 1;
}
```
### Complexity
- Time: O(log n) per transition, converges quickly
- Space: O(1)
### Interview Follow-ups
- Hash-set cycle detection version.

## N16) 4Sum
### Full C Code
```c
#include <stdlib.h>

typedef struct {
    int (*data)[4];
    int size;
    int cap;
} QuadList;

static int cmp_int_n16(const void *a, const void *b) {
    int x = *(const int *)a;
    int y = *(const int *)b;
    return (x > y) - (x < y);
}

QuadList four_sum(int *nums, int n, long target) {
    QuadList out = {0};
    qsort(nums, (size_t)n, sizeof(int), cmp_int_n16);

    for (int i = 0; i < n; ++i) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;

        for (int j = i + 1; j < n; ++j) {
            if (j > i + 1 && nums[j] == nums[j - 1]) continue;

            int l = j + 1;
            int r = n - 1;

            while (l < r) {
                long sum = (long)nums[i] + nums[j] + nums[l] + nums[r];
                if (sum < target) {
                    l++;
                } else if (sum > target) {
                    r--;
                } else {
                    if (out.size == out.cap) {
                        out.cap = (out.cap == 0) ? 8 : out.cap * 2;
                        out.data = (int (*)[4])realloc(out.data,
                                                       (size_t)out.cap * sizeof(*out.data));
                    }

                    out.data[out.size][0] = nums[i];
                    out.data[out.size][1] = nums[j];
                    out.data[out.size][2] = nums[l];
                    out.data[out.size][3] = nums[r];
                    out.size++;

                    l++;
                    r--;
                    while (l < r && nums[l] == nums[l - 1]) l++;
                    while (l < r && nums[r] == nums[r + 1]) r--;
                }
            }
        }
    }

    return out;
}
```
### Complexity
- Time: O(n^3)
- Space: O(1) extra (excluding output)
### Interview Follow-ups
- Generic k-sum recursion pattern.

## N17) Squares of a Sorted Array
### Full C Code
```c
#include <stdlib.h>

int *sorted_squares(const int *nums, int n) {
    int *out = (int *)malloc((size_t)n * sizeof(int));
    if (!out) return NULL;

    int l = 0;
    int r = n - 1;
    int w = n - 1;

    while (l <= r) {
        int lv = nums[l] * nums[l];
        int rv = nums[r] * nums[r];
        if (lv > rv) {
            out[w--] = lv;
            l++;
        } else {
            out[w--] = rv;
            r--;
        }
    }

    return out;
}
```
### Complexity
- Time: O(n)
- Space: O(n)
### Interview Follow-ups
- In-place variant if modification allowed.

## N18) Backspace String Compare
### Full C Code
```c
#include <stdbool.h>

bool backspace_compare(const char *s, const char *t) {
    int i = 0;
    int j = 0;
    while (s[i] != '\0') i++;
    while (t[j] != '\0') j++;
    i--; j--;

    int bs = 0;
    int bt = 0;

    while (i >= 0 || j >= 0) {
        while (i >= 0) {
            if (s[i] == '#') { bs++; i--; }
            else if (bs > 0) { bs--; i--; }
            else break;
        }
        while (j >= 0) {
            if (t[j] == '#') { bt++; j--; }
            else if (bt > 0) { bt--; j--; }
            else break;
        }

        char c1 = (i >= 0) ? s[i] : '\0';
        char c2 = (j >= 0) ? t[j] : '\0';
        if (c1 != c2) return false;

        i--;
        j--;
    }

    return true;
}
```
### Complexity
- Time: O(n + m)
- Space: O(1)
### Interview Follow-ups
- Stack-based variant.

## N19) Fruit Into Baskets
### Full C Code
```c
int total_fruit(const int *fruits, int n) {
    int type1 = -1, type2 = -1;
    int count1 = 0, count2 = 0;
    int l = 0;
    int best = 0;

    for (int r = 0; r < n; ++r) {
        int x = fruits[r];
        if (x == type1) {
            count1++;
        } else if (x == type2) {
            count2++;
        } else {
            while (count1 > 0 && count2 > 0) {
                int y = fruits[l++];
                if (y == type1) count1--;
                else count2--;
            }

            if (count1 == 0) {
                type1 = x;
                count1 = 1;
            } else {
                type2 = x;
                count2 = 1;
            }
        }

        int len = r - l + 1;
        if (len > best) best = len;
    }

    return best;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Generalize to at most K types.

## N20) Max Consecutive Ones III
### Full C Code
```c
int longest_ones(const int *nums, int n, int k) {
    int l = 0;
    int zero_count = 0;
    int best = 0;

    for (int r = 0; r < n; ++r) {
        if (nums[r] == 0) zero_count++;

        while (zero_count > k) {
            if (nums[l] == 0) zero_count--;
            l++;
        }

        int len = r - l + 1;
        if (len > best) best = len;
    }

    return best;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Streaming input adaptation.

## N21) Subarray Product Less Than K
### Full C Code
```c
int num_subarray_product_less_than_k(const int *nums, int n, int k) {
    if (k <= 1) return 0;

    int l = 0;
    long prod = 1;
    int ans = 0;

    for (int r = 0; r < n; ++r) {
        prod *= nums[r];

        while (prod >= k) {
            prod /= nums[l++];
        }

        ans += r - l + 1;
    }

    return ans;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- If zeros/negatives included.

## N22) Find Minimum in Rotated Sorted Array
### Full C Code
```c
int find_min_rotated(const int *nums, int n) {
    int l = 0;
    int r = n - 1;

    while (l < r) {
        int m = l + (r - l) / 2;
        if (nums[m] > nums[r]) l = m + 1;
        else r = m;
    }
    return nums[l];
}
```
### Complexity
- Time: O(log n)
- Space: O(1)
### Interview Follow-ups
- Duplicates degrade to O(n).

## N23) Koko Eating Bananas
### Full C Code
```c
static long hours_needed(const int *piles, int n, int k) {
    long h = 0;
    for (int i = 0; i < n; ++i) {
        h += (piles[i] + k - 1) / k;
    }
    return h;
}

int min_eating_speed(const int *piles, int n, int h) {
    int lo = 1;
    int hi = 1;

    for (int i = 0; i < n; ++i) {
        if (piles[i] > hi) hi = piles[i];
    }

    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (hours_needed(piles, n, mid) <= h) hi = mid;
        else lo = mid + 1;
    }

    return lo;
}
```
### Complexity
- Time: O(n log maxPile)
- Space: O(1)
### Interview Follow-ups
- Overflow-safe hours accumulation.

## N24) Capacity To Ship Packages Within D Days
### Full C Code
```c
static int days_needed(const int *w, int n, int cap) {
    int days = 1;
    int cur = 0;

    for (int i = 0; i < n; ++i) {
        if (cur + w[i] > cap) {
            days++;
            cur = 0;
        }
        cur += w[i];
    }
    return days;
}

int ship_within_days(const int *weights, int n, int days) {
    int lo = 0;
    int hi = 0;

    for (int i = 0; i < n; ++i) {
        if (weights[i] > lo) lo = weights[i];
        hi += weights[i];
    }

    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (days_needed(weights, n, mid) <= days) hi = mid;
        else lo = mid + 1;
    }

    return lo;
}
```
### Complexity
- Time: O(n log sumWeights)
- Space: O(1)
### Interview Follow-ups
- Prove monotonic predicate for binary search.

## N25) Min Stack
### Full C Code
```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int *val;
    int *mn;
    int top;
    int cap;
} MinStack;

bool minstack_init(MinStack *s, int cap) {
    s->val = (int *)malloc((size_t)cap * sizeof(int));
    s->mn = (int *)malloc((size_t)cap * sizeof(int));
    s->top = -1;
    s->cap = cap;
    return s->val && s->mn;
}

void minstack_free(MinStack *s) {
    free(s->val);
    free(s->mn);
}

bool minstack_push(MinStack *s, int x) {
    if (s->top + 1 >= s->cap) return false;
    s->top++;
    s->val[s->top] = x;
    if (s->top == 0) s->mn[s->top] = x;
    else s->mn[s->top] = (x < s->mn[s->top - 1]) ? x : s->mn[s->top - 1];
    return true;
}

bool minstack_pop(MinStack *s) {
    if (s->top < 0) return false;
    s->top--;
    return true;
}

int minstack_top(const MinStack *s) { return s->val[s->top]; }
int minstack_get_min(const MinStack *s) { return s->mn[s->top]; }
```
### Complexity
- Push/Pop/Top/GetMin: O(1)
### Interview Follow-ups
- Space-optimized encoded min stack.

## N26) Next Greater Element II
### Full C Code
```c
#include <stdlib.h>

int *next_greater_elements(const int *nums, int n) {
    int *ans = (int *)malloc((size_t)n * sizeof(int));
    int *st = (int *)malloc((size_t)n * sizeof(int));
    if (!ans || !st) {
        free(ans);
        free(st);
        return NULL;
    }

    for (int i = 0; i < n; ++i) ans[i] = -1;

    int top = -1;
    for (int i = 0; i < 2 * n; ++i) {
        int idx = i % n;

        while (top >= 0 && nums[idx] > nums[st[top]]) {
            ans[st[top--]] = nums[idx];
        }

        if (i < n) st[++top] = idx;
    }

    free(st);
    return ans;
}
```
### Complexity
- Time: O(n)
- Space: O(n)
### Interview Follow-ups
- Non-circular variant.

## N27) Largest Rectangle in Histogram
### Full C Code
```c
#include <stdlib.h>

int largest_rectangle_area(const int *h, int n) {
    int *st = (int *)malloc((size_t)(n + 1) * sizeof(int));
    if (!st) return 0;

    int top = -1;
    int best = 0;

    for (int i = 0; i <= n; ++i) {
        int cur = (i == n) ? 0 : h[i];

        while (top >= 0 && cur < h[st[top]]) {
            int ht = h[st[top--]];
            int left = (top >= 0) ? st[top] : -1;
            int width = i - left - 1;
            int area = ht * width;
            if (area > best) best = area;
        }

        st[++top] = i;
    }

    free(st);
    return best;
}
```
### Complexity
- Time: O(n)
- Space: O(n)
### Interview Follow-ups
- Maximal rectangle in binary matrix.

## N28) Sliding Window Maximum
### Full C Code
```c
#include <stdlib.h>

typedef struct {
    int *arr;
    int size;
} IntArray;

IntArray max_sliding_window(const int *nums, int n, int k) {
    IntArray out = {0};
    if (k <= 0 || k > n) return out;

    int *dq = (int *)malloc((size_t)n * sizeof(int));
    int *ans = (int *)malloc((size_t)(n - k + 1) * sizeof(int));
    if (!dq || !ans) {
        free(dq);
        free(ans);
        return out;
    }

    int head = 0;
    int tail = -1;
    int w = 0;

    for (int i = 0; i < n; ++i) {
        while (head <= tail && dq[head] <= i - k) head++;
        while (head <= tail && nums[dq[tail]] <= nums[i]) tail--;

        dq[++tail] = i;

        if (i >= k - 1) ans[w++] = nums[dq[head]];
    }

    free(dq);
    out.arr = ans;
    out.size = w;
    return out;
}
```
### Complexity
- Time: O(n)
- Space: O(n)
### Interview Follow-ups
- Streaming fixed-memory version.

## N29) Top K Frequent Elements
### Full C Code
```c
#include <stdlib.h>

typedef struct {
    int val;
    int freq;
} FreqPair;

static int cmp_int_n29(const void *a, const void *b) {
    int x = *(const int *)a;
    int y = *(const int *)b;
    return (x > y) - (x < y);
}

static int cmp_freq_desc(const void *a, const void *b) {
    const FreqPair *x = (const FreqPair *)a;
    const FreqPair *y = (const FreqPair *)b;
    return y->freq - x->freq;
}

int *top_k_frequent(int *nums, int n, int k) {
    qsort(nums, (size_t)n, sizeof(int), cmp_int_n29);

    FreqPair *pairs = (FreqPair *)malloc((size_t)n * sizeof(FreqPair));
    if (!pairs) return NULL;

    int m = 0;
    for (int i = 0; i < n; ) {
        int j = i;
        while (j < n && nums[j] == nums[i]) j++;
        pairs[m].val = nums[i];
        pairs[m].freq = j - i;
        m++;
        i = j;
    }

    qsort(pairs, (size_t)m, sizeof(FreqPair), cmp_freq_desc);

    int *ans = (int *)malloc((size_t)k * sizeof(int));
    if (!ans) {
        free(pairs);
        return NULL;
    }

    for (int i = 0; i < k; ++i) ans[i] = pairs[i].val;
    free(pairs);
    return ans;
}
```
### Complexity
- Time: O(n log n)
- Space: O(n)
### Interview Follow-ups
- O(n) bucket sort approach.

## N30) Meeting Rooms II
### Full C Code
```c
#include <stdlib.h>

typedef struct {
    int start;
    int end;
} Meeting;

static int cmp_int_n30(const void *a, const void *b) {
    int x = *(const int *)a;
    int y = *(const int *)b;
    return (x > y) - (x < y);
}

int min_meeting_rooms(const Meeting *meetings, int n) {
    if (n == 0) return 0;

    int *starts = (int *)malloc((size_t)n * sizeof(int));
    int *ends = (int *)malloc((size_t)n * sizeof(int));
    if (!starts || !ends) {
        free(starts);
        free(ends);
        return 0;
    }

    for (int i = 0; i < n; ++i) {
        starts[i] = meetings[i].start;
        ends[i] = meetings[i].end;
    }

    qsort(starts, (size_t)n, sizeof(int), cmp_int_n30);
    qsort(ends, (size_t)n, sizeof(int), cmp_int_n30);

    int s = 0;
    int e = 0;
    int rooms = 0;
    int best = 0;

    while (s < n) {
        if (starts[s] < ends[e]) {
            rooms++;
            if (rooms > best) best = rooms;
            s++;
        } else {
            rooms--;
            e++;
        }
    }

    free(starts);
    free(ends);
    return best;
}
```
### Complexity
- Time: O(n log n)
- Space: O(n)
### Interview Follow-ups
- Return room assignment schedule too.
